from pydantic import BaseModel, EmailStr
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
#  USER SCHEMAS  (your original code — unchanged)
# ─────────────────────────────────────────────────────────────────────────────
class UserBase(BaseModel):
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email:    Optional[EmailStr] = None
    password: Optional[str] = None

class User(UserBase):
    id:        int
    is_active: bool

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────────────────────────────────────
#  AUTH SCHEMAS  (new — needed for login / register responses)
# ─────────────────────────────────────────────────────────────────────────────
class TokenResponse(BaseModel):
    """Returned by /auth/login and /auth/refresh."""
    access_token:  str
    refresh_token: str
    token_type:    str = "bearer"
    user:          User


class RefreshRequest(BaseModel):
    """Body sent to /auth/refresh."""
    refresh_token: str


class MessageResponse(BaseModel):
    """Generic success message — used by /auth/register and /auth/logout."""
    message: str