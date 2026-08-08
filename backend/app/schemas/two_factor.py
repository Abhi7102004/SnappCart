# app/schemas/two_factor.py

from pydantic import BaseModel
from typing import List


class TwoFactorSetupResponse(BaseModel):
    """Returned when user initiates 2FA setup — frontend renders QR from uri"""
    otpauth_uri: str
    secret: str           # shown as manual fallback (masked in UI)


class TwoFactorConfirmRequest(BaseModel):
    code: str             # 6-digit code from authenticator app


class TwoFactorConfirmResponse(BaseModel):
    message: str
    backup_codes: List[str]  # shown ONCE — user must save these


class TwoFactorVerifyRequest(BaseModel):
    """Sent during login when 2FA is required"""
    session_token: str    # ties this request to the pending login
    code: str             # 6-digit TOTP or 10-digit backup code


class TwoFactorLoginResponse(BaseModel):
    """Returned by login() when 2FA is enabled — not yet fully authenticated"""
    two_factor_required: bool = True
    session_token: str    # opaque token, stored in Redis, ties to user_id