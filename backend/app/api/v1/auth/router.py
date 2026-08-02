from fastapi import APIRouter, Depends, Response, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security.dependencies import get_current_user
from app.schemas.user import UserRegisterRequest, UserResponse
from app.schemas.auth import (
    RegisterResponse, LoginRequest, LoginResponse,
    RefreshResponse, MessageResponse, EmailVerifyRequest,ResendVerificationRequest
)
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: UserRegisterRequest,
    db: Session = Depends(get_db),
) -> RegisterResponse:
    return AuthService.register(data, db)


@router.post(
    "/login",
    response_model=LoginResponse,
)
async def login(
    data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> LoginResponse:
    return await AuthService.login(
        email_or_phone=data.email_or_phone,
        password=data.password,
        response=response,
        db=db,
    )


@router.post(
    "/refresh",
    response_model=RefreshResponse,
)
async def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> RefreshResponse:
    return await AuthService.refresh_token(request, response, db)


@router.post(
    "/logout",
    response_model=MessageResponse,
)
async def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    result = await AuthService.logout(request, response, current_user)
    return MessageResponse(message=result["message"])


@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Get currently authenticated user's profile"""
    return UserResponse.model_validate(current_user)


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    data: EmailVerifyRequest,
    db: Session = Depends(get_db),
) -> MessageResponse:
    result = AuthService.verify_email(data.token, db)
    return MessageResponse(message=result["message"])


@router.get("/verify-email", response_model=MessageResponse)
async def verify_email_link(
    token: str,
    db: Session = Depends(get_db),
) -> MessageResponse:
    result = AuthService.verify_email(token, db)
    return MessageResponse(message=result["message"])

@router.post("/resend-verification",response_model=MessageResponse)
async def resend_verification_mail(
    data:ResendVerificationRequest,
    db:Session=Depends(get_db)
)-> MessageResponse:
    result = await AuthService.resend_verification_mail(data.email, db)
    return MessageResponse(message=result["message"])