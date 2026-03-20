from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
#  CONFIG  —  loaded from your .env file
# ─────────────────────────────────────────────────────────────────────────────
SECRET_KEY                  = os.getenv("SECRET_KEY", "changeme")
ALGORITHM                   = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS   = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

# ─────────────────────────────────────────────────────────────────────────────
#  PASSWORD HASHING
# ─────────────────────────────────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a plain password against the stored bcrypt hash."""
    if hashed_password is None:
        return False
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a plain password with bcrypt before storing in the DB."""
    return pwd_context.hash(password)


# ─────────────────────────────────────────────────────────────────────────────
#  JWT — TOKEN CREATION
# ─────────────────────────────────────────────────────────────────────────────
def _create_token(data: dict, expires_delta: timedelta) -> str:
    """Internal helper: add expiry claim and sign the token."""
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + expires_delta
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(user_id: int, email: str) -> str:
    """
    Short-lived token (30 min by default).
    React attaches this to every request:
        Authorization: Bearer <access_token>
    """
    return _create_token(
        {"sub": str(user_id), "email": email, "type": "access"},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(user_id: int) -> str:
    """
    Long-lived token (7 days by default).
    Only used at POST /auth/refresh to get a new access token.
    """
    return _create_token(
        {"sub": str(user_id), "type": "refresh"},
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT. Returns payload dict or None if invalid/expired."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


# ─────────────────────────────────────────────────────────────────────────────
#  OAUTH2 SCHEME
#  Tells FastAPI to look for the token in the Authorization: Bearer header.
#  Also powers the Authorize button in /docs.
# ─────────────────────────────────────────────────────────────────────────────
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ─────────────────────────────────────────────────────────────────────────────
#  DEPENDENCIES  —  inject into any protected route via Depends()
# ─────────────────────────────────────────────────────────────────────────────
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db), 
):
    """
    Resolves a Bearer token → User row from the DB.
    Raises 401 if the token is missing, expired, or tampered with.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    # Require 'access' type specifically
    if payload.get("type") != "access":
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    from app import models
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(
    current_user=Depends(get_current_user),
):
    """Extends get_current_user — also blocks disabled accounts."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled.",
        )
    return current_user
