from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security.dependencies import require_seller, get_current_user
from app.models.user import User
from app.schemas.two_factor import (
    TwoFactorSetupResponse, TwoFactorConfirmRequest,
    TwoFactorConfirmResponse, TwoFactorVerifyRequest,
)
from fastapi import Response
from app.schemas.auth import LoginResponse, MessageResponse
from app.services.two_factor_service import TwoFactorService
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth/2fa", tags=["2FA"])

@router.post("/setup", response_model=TwoFactorSetupResponse)
async def setup_2fa(
    current_user: User = Depends(require_seller),
    db: Session = Depends(get_db),
) -> TwoFactorSetupResponse:
    return TwoFactorService.initiate_setup(current_user, db)

@router.post("/confirm", response_model=TwoFactorConfirmResponse)
async def confirm_2fa(
    data: TwoFactorConfirmRequest,
    current_user: User = Depends(require_seller),
    db: Session = Depends(get_db),
) -> TwoFactorConfirmResponse:
    return TwoFactorService.confirm_setup(current_user, data.code, db)

@router.post("/verify", response_model=LoginResponse)
async def verify_2fa(
    data: TwoFactorVerifyRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> LoginResponse:
    """
    Called after login() returns two_factor_required=True.
    No auth dependency here — user isn't fully authenticated yet.
    session_token (from Redis) ties this request to the pending login.
    """
    user = await TwoFactorService.verify_login_code(data.session_token, data.code, db)

    # Reuse existing token issuance — same as regular login success
    from app.core.security.jwt import create_access_token, create_refresh_token
    from app.schemas.user import UserResponse
    from app.core.config import settings
    from app.core.security.utils import utc_now

    access_token = create_access_token(str(user.id), user.role.value)
    refresh_token = create_refresh_token(str(user.id))
    await AuthService._store_refresh_token(str(user.id), refresh_token)
    AuthService._set_refresh_cookie(response, refresh_token)

    user.last_login_at = utc_now()
    db.commit()

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )
    
@router.post("/disable", response_model=MessageResponse)
async def disable_2fa(
    data: TwoFactorConfirmRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    result = TwoFactorService.disable(current_user, data.code, db)
    return MessageResponse(message=result["message"])