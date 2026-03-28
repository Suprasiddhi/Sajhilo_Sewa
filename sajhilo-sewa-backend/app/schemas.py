from pydantic import BaseModel, EmailStr
from typing import Optional, List


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


# ─────────────────────────────────────────────────────────────────────────────
#  GESTURE SCHEMAS 
# ─────────────────────────────────────────────────────────────────────────────

class MediaBase(BaseModel):
    media_type: str
    url: str

class MediaCreate(MediaBase):
    pass

class Media(MediaBase):
    id: int
    section_id: int

    class Config:
        from_attributes = True

class GestureSectionBase(BaseModel):
    title: str
    description: Optional[str] = None

class GestureSectionCreate(GestureSectionBase):
    media: List[MediaCreate]

class GestureSection(GestureSectionBase):
    id: int
    gesture_id: int
    media: List[Media]

    class Config:
        from_attributes = True

class GestureBase(BaseModel):
    name: str
    category: str

class GestureCreate(GestureBase):
    sections: List[GestureSectionCreate]

class Gesture(GestureBase):
    id: int
    sections: List[GestureSection]

    class Config:
        from_attributes = True

class AdminStatsResponse(BaseModel):
    total_users: int
    all_usernames: List[str]
    total_gestures: int
    latest_gestures: List[Gesture]