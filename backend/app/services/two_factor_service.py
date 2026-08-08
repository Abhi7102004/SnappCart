import pyotp
import secrets
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from loguru import logger

from app.models.user import User
from app.core.encryption import encrypt, decrypt
from app.core.security.password import hash_password, verify_password
from app.core.constants import (
    BACKUP_CODE_COUNT, TWO_FA_ISSUER,
    TWO_FA_TOTP_PREFIX, TWO_FA_TOTP_TTL_SECONDS,
)
from app.core.redis import redis_client
from app.schemas.two_factor import (
    TwoFactorSetupResponse, TwoFactorConfirmResponse, TwoFactorVerifyRequest
)

class TwoFactorService:

    # ── SETUP ────────────────────────────────────────────────────────
    
    @staticmethod
    def initiate_setup(user: User, db: Session) -> TwoFactorSetupResponse:
        """
        Generate a new TOTP secret for the user.
        Stores it encrypted BUT keeps two_factor_enabled=False —
        must be confirmed with a live code before activating.
        """
        
        if user.two_factor_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA is already enabled on this account"
            )
        
        raw_secret = pyotp.random_base32()
        user.two_factor_secret = encrypt(raw_secret)
        db.commit()
        
        label = user.email or user.phone or str(user.id)
        totp = pyotp.TOTP(raw_secret)
        uri = totp.provisioning_uri(name=label, issuer_name=TWO_FA_ISSUER)
        
        return TwoFactorSetupResponse(otpauth_uri=uri,secret=raw_secret)
    
    @staticmethod
    def confirm_setup(user: User, code: str, db: Session) -> TwoFactorConfirmResponse:
        """
        Verify the user actually scanned the QR code correctly,
        THEN activate 2FA and generate backup codes.
        """
        if user.two_factor_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA is already enabled"
            )

        if not user.two_factor_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No 2FA setup in progress. Start setup first."
            )
            
        TwoFactorService._verify_totp_code(user, code)
        
        plain_backup_codes = [
            secrets.token_hex(5).upper()
            for _ in range(BACKUP_CODE_COUNT)
        ]
        
        user.two_factor_backup_codes = [hash_password(c) for c in plain_backup_codes]
        user.two_factor_enabled = True
        db.commit()

        logger.info(f"2FA enabled: {user.email or user.phone}")
        
        return TwoFactorConfirmResponse(
            message="2FA enabled successfully. Save your backup codes — they won't be shown again.",
            backup_codes=plain_backup_codes,
        )
    
    # ── VERIFY (during login) ────────────────────────────────────────

    @staticmethod
    async def create_pending_session(user_id: str) -> str:
        """
        Called by login() when 2FA is required — BEFORE issuing tokens.
        Stores user_id in Redis under a random session token.
        Frontend sends this token back alongside the TOTP code.
        """
        session_token = secrets.token_urlsafe(32)
        await redis_client.setex(
            f"{TWO_FA_TOTP_PREFIX}{session_token}",
            TWO_FA_TOTP_TTL_SECONDS,
            user_id
        )
        return session_token
    
    @staticmethod
    async def verify_login_code(
        session_token: str, code: str, db: Session
    ) -> User:
        """
        Verify the TOTP/backup code during login.
        Returns the authenticated User if valid.
        """
        redis_key = f"{TWO_FA_TOTP_PREFIX}{session_token}"
        user_id = await redis_client.get(redis_key)

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="2FA session expired or invalid. Please log in again."
            )
        
        user = db.query(User).filter(
            User.id == user_id,
            User.is_deleted == False
        ).first()
        
        if not user or not user.two_factor_enabled:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid session")

        is_valid = TwoFactorService._try_totp(user, code)
        if not is_valid:
            is_valid = TwoFactorService._try_backup_code(user, code, db)
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired 2FA code"
            )
            
        await redis_client.delete(redis_key)
        return user

    # ── DISABLE ──────────────────────────────────────────────────────

    @staticmethod
    def disable(user: User, code: str, db: Session) -> dict:
        """Disable 2FA. Requires a valid code to prevent accidental/malicious disable."""
        if not user.two_factor_enabled:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "2FA is not enabled")

        TwoFactorService._verify_totp_code(user, code)

        user.two_factor_enabled = False
        user.two_factor_secret = None
        user.two_factor_backup_codes = None
        db.commit()

        logger.info(f"2FA disabled: {user.email or user.phone}")
        return {"message": "2FA disabled successfully"}

    # ── Internal helpers ─────────────────────────────────────────────
    
    @staticmethod
    def _verify_totp_code(user:User,code:str) -> None:
        """Verify a 6-digit TOTP code. Raises on invalid."""
        if not TwoFactorService._try_totp(user, code):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired 2FA code"
            )

    @staticmethod
    def _try_totp(user: User, code: str) -> bool:
        """Returns True if code is a valid current TOTP code."""
        try:
            raw_secret = decrypt(user.two_factor_secret)
            totp = pyotp.TOTP(raw_secret)
            # valid_window=1 → accepts codes from ±30s window (clock drift)
            return totp.verify(code, valid_window=1)
        except Exception:
            return False
    
    @staticmethod
    def _try_backup_code(user: User, code: str, db: Session) -> bool:
        """
        Check if code matches any stored backup code hash.
        If match found → delete that hash (single-use).
        """
        if not user.two_factor_backup_codes:
            return False
        
        for i,hashed in enumerate(user.two_factor_backup_codes):
            if verify_password(code,hashed):
                remaining = list(user.two_factor_backup_codes)
                remaining.pop(i)
                user.two_factor_backup_codes = remaining if remaining else None
                db.commit()
                logger.info(f"Backup code used: {user.email or user.phone}")
                return True

        return False