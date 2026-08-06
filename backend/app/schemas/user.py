import re
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, field_validator, model_validator
from typing import Optional
from app.models.user import UserRole, UserGender, OAuthProvider
from app.core.validators import (
    validate_password_strength, validate_phone_e164, validate_full_name
)

class UserRegisterRequest(BaseModel):
    """Registration request — email OR phone required"""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str
    full_name: Optional[str] = None

    @field_validator("password")
    @classmethod
    def validate_password(cls,v:str) ->str:
        return validate_password_strength(v)
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        return validate_phone_e164(v)
    
    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        return validate_full_name(v)
    
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
        return validate_phone_e164(v)
    
    
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
    