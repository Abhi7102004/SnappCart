from pydantic import BaseModel, EmailStr,field_validator
from typing import Optional
from app.schemas.user import UserResponse
from app.core.validators import validate_password_strength

class RegisterResponse(BaseModel):
    """Response after successful registration"""
    message: str
    user: UserResponse
    email_verification_sent: bool
    
class LoginRequest(BaseModel):
    """Login with email or phone + password"""
    email_or_phone: str
    password: str

class LoginResponse(BaseModel):
    """Response after successful login"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    
class RefreshResponse(BaseModel):
    """Response after token refresh"""
    access_token: str
    token_type: str = "bearer"

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    
class EmailVerifyRequest(BaseModel):
    token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class ResendVerificationRequest(BaseModel):
    email: EmailStr
    
class ResetPasswordRequest(BaseModel):
    token:str
    new_password:str
    
    @field_validator("new_password")
    @classmethod
    def validate_password(cls,v:str) ->str:
        return validate_password_strength(v)

class ChangePasswordRequest(BaseModel):
    old_password:str
    new_password:str
    
    @field_validator("new_password")
    @classmethod
    def _validate_new_password(cls, v: str) -> str:
        return validate_password_strength(v)