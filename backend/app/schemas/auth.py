from pydantic import BaseModel, EmailStr
from typing import Optional
from app.schemas.user import UserResponse

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