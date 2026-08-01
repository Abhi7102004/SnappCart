from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.user import UserRegisterRequest
from app.schemas.auth import (
    RegisterResponse,
    MessageResponse,
    EmailVerifyRequest,
)
from app.services.auth_service import AuthService

router=APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="""
    Register with email or phone number + password.
    - Either email OR phone is required (or both)
    - Password must be 8-128 chars, include uppercase, lowercase, number
    - Phone must be E.164 format (+919838388338)
    - Email verification link sent automatically
    """,
)
async def register(
    data:UserRegisterRequest,
    db:Session=Depends(get_db)
)-> RegisterResponse:
    return AuthService.register(data,db)

@router.post(
    "/verify-email",
    response_model=MessageResponse,
    summary="Verify email address",
)
async def verify_email(
    data:EmailVerifyRequest,
    db: Session=Depends(get_db)
)-> MessageResponse:
    result = AuthService.verify_email(data.token, db)
    return MessageResponse(message=result["message"])

@router.get(
    "/verify-email",
    response_model=MessageResponse,
    summary="Verify email via link (GET)",
)
async def verify_email_link(
    token: str,
    db: Session = Depends(get_db),
) -> MessageResponse:
    """Handles clicking link from email: /verify-email?token=xxx"""
    result = AuthService.verify_email(token, db)
    return MessageResponse(message=result["message"])