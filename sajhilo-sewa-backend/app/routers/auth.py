from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.auth_utils import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    oauth2_scheme
)

router = APIRouter(prefix="/auth", tags=["auth"])

def _get_user_from_token(
    token: str,
    token_type: str,
    db: Session,
) -> models.User:
    """
    Shared logic: decode token, validate type, fetch User row.
    Raises 401 on any failure.
    """
    payload = decode_token(token)
    if not payload or payload.get("type") != token_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(models.User).filter(
        models.User.id == int(payload["sub"])
    ).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found.")
    return user
 
 
# ─────────────────────────────────────────────────────────────────────────────
#  POST /auth/register
# ─────────────────────────────────────────────────────────────────────────────
@router.post(
    "/register",
    response_model=schemas.MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user account",
)
def register(body: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Pipeline:
      1. Check if email is already registered.
      2. Check if username is already taken.
      3. Hash the password (never store plain text).
      4. Insert the new user row.
      5. Return a success message.
    """
    if db.query(models.User).filter(models.User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already registered.")
 
    # 2. Duplicate username check
    if db.query(models.User).filter(models.User.username == body.username).first():
        raise HTTPException(status_code=400, detail="Username already taken.")
 
    # 3 & 4. Hash password and save
    new_user = models.User(
        username=body.username,
        email=body.email,
        first_name=body.first_name,
        last_name=body.last_name,
        hashed_password=get_password_hash(body.password),
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
 
    # 5. Return message (don't expose user data on register)
    return {"message": "Account created successfully. Please log in."}
 
 
# ─────────────────────────────────────────────────────────────────────────────
#  POST /auth/login
#  Uses OAuth2PasswordRequestForm so it works with /docs Authorize button.
#  Form fields: username (we treat it as email) and password.
# ─────────────────────────────────────────────────────────────────────────────
@router.post(
    "/login",
    response_model=schemas.TokenResponse,
    summary="Login and receive JWT tokens",
)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db:   Session                   = Depends(get_db),
):
    # 1. Lookup by email OR username
    user = db.query(models.User).filter(
        (models.User.email == form.username) | (models.User.username == form.username)
    ).first()
 
    # 2. Verify existence first
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found",
        )

    # 3. Verify password
    if not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
 
    # 3. Active check
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled. Contact support.",
        )
 
    # 4 & 5. Issue tokens
    return schemas.TokenResponse(
        access_token=create_access_token(user.id, user.email),
        refresh_token=create_refresh_token(user.id),
        user=user,
    )
 
 
# ─────────────────────────────────────────────────────────────────────────────
#  POST /auth/refresh
# ─────────────────────────────────────────────────────────────────────────────
@router.post(
    "/refresh",
    response_model=schemas.TokenResponse,
    summary="Get a new token pair using a refresh token",
)
def refresh(body: schemas.RefreshRequest, db: Session = Depends(get_db)):
    """
    Pipeline:
      1. Decode and validate the refresh token.
      2. Confirm token type is 'refresh' (not 'access').
      3. Load the user.
      4. Issue a brand-new access + refresh token pair.
    """
    user = _get_user_from_token(body.refresh_token, "refresh", db)
 
    return schemas.TokenResponse(
        access_token=create_access_token(user.id, user.email),
        refresh_token=create_refresh_token(user.id),
        user=user,
    )
 
 
# ─────────────────────────────────────────────────────────────────────────────
#  GET /auth/me  —  protected route example
# ─────────────────────────────────────────────────────────────────────────────
@router.get(
    "/me",
    response_model=schemas.User,
    summary="Get the currently logged-in user",
)
def me(
    token: str     = Depends(oauth2_scheme),
    db:    Session = Depends(get_db),
):
    """Returns the user profile for whoever owns the access token."""
    user = _get_user_from_token(token, "access", db)
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled.")
    return user
 
 
# ─────────────────────────────────────────────────────────────────────────────
#  POST /auth/reset-password
# ─────────────────────────────────────────────────────────────────────────────
@router.post(
    "/reset-password",
    response_model=schemas.MessageResponse,
    summary="Reset user password",
)
def reset_password(body: schemas.PasswordReset, db: Session = Depends(get_db)):
    """
    Pipeline:
      1. Check if email exists.
      2. Check if username matches that email.
      3. Update the password.
    """
    user = db.query(models.User).filter(models.User.email == body.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="email do not exist"
        )
    
    if user.username != body.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="wrong username or email"
        )
    
    user.hashed_password = get_password_hash(body.new_password)
    db.commit()
    
    return {"message": "password changed"}


# ─────────────────────────────────────────────────────────────────────────────
#  POST /auth/logout
# ─────────────────────────────────────────────────────────────────────────────
@router.post(
    "/logout",
    response_model=schemas.MessageResponse,
    summary="Logout (client must discard both tokens)",
)
def logout(
    token: str     = Depends(oauth2_scheme),
    db:    Session = Depends(get_db),
):
    """
    JWTs are stateless — the server cannot invalidate them.
    This endpoint confirms the token is valid and tells the client
    to delete both tokens from storage.
    For true server-side revocation, add a Redis token blocklist.
    """
    _get_user_from_token(token, "access", db)
    return {"message": "Logged out successfully."}