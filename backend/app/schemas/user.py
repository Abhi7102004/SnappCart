import re
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, field_validator, model_validator
from typing import Optional
from app.models.user import UserRole, UserGender, OAuthProvider

class UserRegisterRequest(BaseModel):
    """Registration request — email OR phone required"""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str
    full_name: Optional[str] = None

    @field_validator("password")
    @classmethod
    def validate_password(cls,v:str) ->str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if len(v) > 128:
            raise ValueError("Password must be at most 128 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one number")
        return v
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # E.164 format: +[country code][number]
        pattern = r"^\+[1-9]\d{6,14}$"
        if not re.match(pattern, v):
            raise ValueError("Phone must be in E.164 format (+919838388338)")
        return v
    
    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Full name must be at least 2 characters")
        if len(v) > 100:
            raise ValueError("Full name must be at most 100 characters")
        return v
    
    @model_validator(mode="after")
    def email_or_phone_required(self) -> "UserRegisterRequest":
        if not self.email and not self.phone:
            raise ValueError("Either email or phone is required")
        return self
    
    
class UserUpdateRequest(BaseModel):
    """Update profile request"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[UserGender] = None
    date_of_birth: Optional[datetime] = None
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not re.match(r"^\+[1-9]\d{6,14}$", v):
            raise ValueError("Phone must be in E.164 format")
        return v
    
    
class UserResponse(BaseModel):
    """User data safe to return — NEVER includes hashed_password"""
    id: UUID
    email: Optional[str] = None
    phone: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: UserRole
    avatar_url: Optional[str] = None
    oauth_avatar_url: Optional[str] = None
    is_email_verified: bool
    is_phone_verified: bool
    oauth_provider: OAuthProvider
    created_at: datetime
    last_login_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

class UserProfileResponse(UserResponse):
    """Extended profile — includes more fields"""
    gender: Optional[UserGender] = None
    date_of_birth: Optional[datetime] = None
    updated_at: datetime

    model_config = {"from_attributes": True}
    