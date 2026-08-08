# app/services/auth_service.py

import secrets
from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Response, Request
from jose import JWTError
from loguru import logger

from app.models.user import User, UserRole, OAuthProvider
from app.schemas.user import UserRegisterRequest, UserResponse
from app.schemas.auth import RegisterResponse, LoginResponse, RefreshResponse

from app.core.config import settings
from app.core.constants import (
    MAX_FAILED_LOGIN_ATTEMPTS,ACCOUNT_LOCKOUT_MINUTES,EMAIL_VERIFY_TOKEN_EXPIRE_HOURS,
    REFRESH_COOKIE_NAME,REFRESH_COOKIE_PATH,RESEND_VERIFICATION_COOLDOWN_SECONDS,
    RESEND_VERIFY_PREFIX,FORGOT_PASSWORD_PREFIX,PASSWORD_RESET_TOKEN_EXPIRE_HOURS,
    FORGOT_PASSWORD_COOLDOWN_SECONDS,
)
from app.core import messages as msg
from app.core.security.password import hash_password, verify_password, DUMMY_HASH
from app.core.security.jwt import (
    create_access_token, create_refresh_token,
    decode_token, get_refresh_token_key,
)
from app.services.two_factor_service import TwoFactorService
from app.schemas.two_factor import TwoFactorLoginResponse

from app.services.email_service import EmailService
from app.core.security.utils import ensure_utc, is_expired, utc_now
from app.core.security.dependencies import validate_user_active
from app.core.redis import redis_client


class AuthService:

    # ── Internal helpers ─────────────────────────────────────────────

    @staticmethod
    def _set_refresh_cookie(response: Response, token: str) -> None:
        """Single source of truth for refresh cookie settings — no duplication"""
        response.set_cookie(
            key=REFRESH_COOKIE_NAME,
            value=token,
            httponly=True,
            secure=settings.environment == "production",
            samesite="lax",
            max_age=settings.refresh_token_expire_days * 24 * 3600,
            path=REFRESH_COOKIE_PATH,
        )

    @staticmethod
    async def _store_refresh_token(user_id: str, token: str) -> None:
        """Single source of truth for storing refresh token in Redis"""
        redis_key = get_refresh_token_key(user_id)
        await redis_client.setex(
            redis_key,
            settings.refresh_token_expire_days * 24 * 3600,
            token
        )

    # ── REGISTRATION ────────────────────────────────────────────────

    @staticmethod
    def register(data: UserRegisterRequest, db: Session) -> RegisterResponse:
        """
        Register new user with email/phone + password.
        Handles duplicate check, password hashing, email verification token.
        """
        if data.email:
            existing = db.query(User).filter(
                User.email == data.email,
                User.is_deleted == False
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=msg.AUTH_EMAIL_EXISTS
                )

        if data.phone:
            existing = db.query(User).filter(
                User.phone == data.phone,
                User.is_deleted == False
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=msg.AUTH_PHONE_EXISTS
                )

        hashed = hash_password(data.password)

        verify_token = None
        verify_token_expires = None
        if data.email:
            verify_token = secrets.token_urlsafe(32)
            verify_token_expires = utc_now() + timedelta(hours=EMAIL_VERIFY_TOKEN_EXPIRE_HOURS)

        user = User(
            email=data.email,
            phone=data.phone,
            full_name=data.full_name,
            hashed_password=hashed,
            role=UserRole.customer,
            oauth_provider=OAuthProvider.local,
            is_email_verified=False,
            is_phone_verified=False,
            email_verify_token=verify_token,
            email_verify_token_expires=verify_token_expires,
            is_active=True,
            is_deleted=False,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        logger.info(f"New user registered: {user.email or user.phone}")

        # TODO Day 27: send actual email via AWS SES
        if verify_token:
            EmailService.send_verification_email(user.email,user.full_name,user.email_verify_token)

        return RegisterResponse(
            message=msg.AUTH_REGISTER_SUCCESS,
            user=UserResponse.model_validate(user),
            email_verification_sent=bool(data.email),
        )

    # ── EMAIL VERIFICATION ──────────────────────────────────────────

    @staticmethod
    def verify_email(token: str, db: Session) -> dict:
        """Verify email using token sent to user's email"""
        user = db.query(User).filter(
            User.email_verify_token == token,
            User.is_deleted == False
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=msg.AUTH_VERIFY_TOKEN_INVALID
            )

        if is_expired(user.email_verify_token_expires):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=msg.AUTH_VERIFY_TOKEN_EXPIRED
            )

        if user.is_email_verified:
            return {"message": msg.AUTH_EMAIL_ALREADY_VERIFIED}

        user.is_email_verified = True
        user.email_verify_token = None
        user.email_verify_token_expires = None
        db.commit()

        logger.info(f"Email verified: {user.email}")
        return {"message": msg.AUTH_EMAIL_VERIFIED_SUCCESS}

    # ── LOGIN ────────────────────────────────────────────────────────

    @staticmethod
    async def login(
        email_or_phone: str,
        password: str,
        response: Response,
        db: Session,
    ) -> LoginResponse:
        """
        Login with email or phone + password.

        Security:
          - Generic error message (never reveal if email exists)
          - Always runs bcrypt (timing attack prevention)
          - Account lockout after MAX_FAILED_LOGIN_ATTEMPTS
          - Refresh token stored in Redis + httpOnly cookie
        """
        filter_field = User.email if "@" in email_or_phone else User.phone
        user = db.query(User).filter(
            filter_field == email_or_phone,
            User.is_deleted == False
        ).first()

        # ALWAYS run bcrypt even if user not found — timing attack prevention
        stored_hash = user.hashed_password if user else DUMMY_HASH
        password_correct = verify_password(password, stored_hash)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=msg.AUTH_INVALID_CREDENTIALS
            )

        # Active/banned check (no lock check here — handled below,
        # since login uniquely needs to RESET an expired lock)
        if not user.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, msg.AUTH_ACCOUNT_DEACTIVATED)
        if user.is_banned:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                msg.AUTH_ACCOUNT_BANNED.format(reason=user.banned_reason or "Policy violation")
            )

        # Lock check WITH reset-if-expired (only login does this)
        if user.locked_until:
            if ensure_utc(user.locked_until) > utc_now():
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail=msg.AUTH_ACCOUNT_LOCKED.format(until=user.locked_until.strftime('%H:%M UTC'))
                )
            # Lock expired → forgive it
            user.locked_until = None
            user.failed_login_attempts = 0

        # Wrong password
        if not password_correct:
            user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
            user.last_failed_login_at = utc_now()

            if user.failed_login_attempts >= MAX_FAILED_LOGIN_ATTEMPTS:
                user.locked_until = utc_now() + timedelta(minutes=ACCOUNT_LOCKOUT_MINUTES)
                db.commit()
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail=msg.AUTH_ACCOUNT_LOCKED_DURATION.format(minutes=ACCOUNT_LOCKOUT_MINUTES)
                )

            db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=msg.AUTH_INVALID_CREDENTIALS
            )

        # ── Successful login ─────────────────────────────────────
        user.failed_login_attempts = 0
        user.last_failed_login_at = None
        user.locked_until = None
        user.last_login_at = utc_now()
        db.commit()

        if user.two_factor_enabled:
            session_token = await TwoFactorService.create_pending_session(str(user.id))
            return TwoFactorLoginResponse(session_token=session_token)
        
        access_token = create_access_token(user_id=str(user.id), role=user.role.value)
        refresh_token = create_refresh_token(user_id=str(user.id))

        await AuthService._store_refresh_token(str(user.id), refresh_token)
        AuthService._set_refresh_cookie(response, refresh_token)

        logger.info(f"User logged in: {user.email or user.phone}")

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )

    # ── REFRESH ──────────────────────────────────────────────────────

    @staticmethod
    async def refresh_token(request: Request, response: Response, db: Session) -> RefreshResponse:
        """Issue new access token using refresh token from cookie. Rotates refresh token."""
        invalid_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=msg.AUTH_INVALID_REFRESH_TOKEN
        )

        refresh_token = request.cookies.get(REFRESH_COOKIE_NAME)
        if not refresh_token:
            raise invalid_exception

        try:
            payload = decode_token(refresh_token)
            user_id = payload.get("sub")
            if not user_id or payload.get("type") != "refresh":
                raise invalid_exception
        except JWTError:
            raise invalid_exception

        redis_key = get_refresh_token_key(user_id)
        stored_token = await redis_client.get(redis_key)
        if not stored_token or stored_token != refresh_token:
            raise invalid_exception

        user = db.query(User).filter(
            User.id == user_id,
            User.is_deleted == False
        ).first()
        if not user:
            raise invalid_exception

        validate_user_active(user)

        new_access_token = create_access_token(user_id=str(user.id), role=user.role.value)
        new_refresh_token = create_refresh_token(user_id=str(user.id))

        await AuthService._store_refresh_token(str(user.id), new_refresh_token)
        AuthService._set_refresh_cookie(response, new_refresh_token)

        return RefreshResponse(access_token=new_access_token, token_type="bearer")

    # ── LOGOUT ───────────────────────────────────────────────────────

    @staticmethod
    async def logout(request: Request, response: Response, current_user: User) -> dict:
        """Delete refresh token from Redis (revoke) + clear httpOnly cookie"""
        redis_key = get_refresh_token_key(str(current_user.id))
        await redis_client.delete(redis_key)

        response.delete_cookie(key=REFRESH_COOKIE_NAME, path=REFRESH_COOKIE_PATH)

        logger.info(f"User logged out: {current_user.email or current_user.phone}")
        return {"message": msg.AUTH_LOGOUT_SUCCESS}
    
    @staticmethod
    async def resend_verification_mail(email:str,db:Session) -> dict:
        """
        Resend verification email.
        Rate limited via Redis (1 request per RESEND_VERIFICATION_COOLDOWN_SECONDS)
        to prevent spam-clicking the resend button.

        Generic response regardless of whether email exists — prevents
        email enumeration (same principle as login's generic error).
        """

        cooldown_key = f"{RESEND_VERIFY_PREFIX}{email}"
        
        if await redis_client.get(cooldown_key):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=msg.RATE_LIMIT_COOLDOWN.format(action="verification email")
            )
        
        user = db.query(User).filter(
            User.email == email,
            User.is_deleted == False
        ).first()

        generic_response = {
            "message": msg.AUTH_VERIFICATION_SENT_GENERIC
        }
        
        if not user or user.is_email_verified:
            # Set cooldown anyway — prevents attacker from probing
            # which emails exist by noticing missing cooldown behavior
            await redis_client.setex(cooldown_key, RESEND_VERIFICATION_COOLDOWN_SECONDS, "1")
            return generic_response

        verify_token=secrets.token_urlsafe(32)
        user.email_verify_token = verify_token
        user.email_verify_token_expires = utc_now() + timedelta(
            hours=EMAIL_VERIFY_TOKEN_EXPIRE_HOURS
        )
        db.commit()
        
        if verify_token:
            EmailService.send_verification_email(email,user.full_name,verify_token)

        await redis_client.setex(cooldown_key,RESEND_VERIFICATION_COOLDOWN_SECONDS,"1")
        
        logger.info(f"Verification email resent: {user.email}")
        return generic_response

    @staticmethod
    async def forgot_password(email:str,db:Session) -> dict:
        """
        Request password reset link.
        Generic response always — never reveals whether the email exists.
        Rate limited via Redis cooldown (same pattern as resend-verification).
        """
        
        cooldown_key=f"{FORGOT_PASSWORD_PREFIX}{email}"
        
        if await redis_client.get(cooldown_key):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=msg.RATE_LIMIT_COOLDOWN.format(action="password reset")
            )
        
        user = db.query(User).filter(
            User.email == email,
            User.is_deleted == False
        ).first()
        
        generic_response = {
            "message": msg.AUTH_RESET_SENT_GENERIC
        }
        
        if not user or user.hashed_password is None:
            await redis_client.setex(cooldown_key, FORGOT_PASSWORD_COOLDOWN_SECONDS, "1")
            return generic_response
        
        reset_token=secrets.token_urlsafe(32)
        user.password_reset_token=reset_token
        user.password_reset_token_expires=utc_now()+timedelta(hours=PASSWORD_RESET_TOKEN_EXPIRE_HOURS)
        db.commit()
        
        EmailService.send_password_reset_email(email,user.full_name,reset_token)
        
        logger.info(f"Password reset requested: {user.email}")
        return generic_response

    @staticmethod
    async def reset_password(token:str,new_password:str,db:Session) -> dict:
        """
        Reset password using token from email.
        Invalidates the token (single-use) AND the user's active session —
        if the password was compromised, this logs out whoever had access.
        """
        
        user = db.query(User).filter(
            User.password_reset_token == token,
            User.is_deleted == False
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=msg.AUTH_RESET_TOKEN_INVALID
            )
        
        if is_expired(user.password_reset_token_expires):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=msg.AUTH_RESET_TOKEN_EXPIRED
            )
        
        user.hashed_password=hash_password(new_password)
        user.password_reset_token=None
        user.password_reset_token_expires=None
        user.failed_login_attempts = 0
        user.locked_until = None
        
        db.commit()
        
        redis_key=get_refresh_token_key(str(user.id))
        await redis_client.delete(redis_key)
        
        logger.info(f"Password reset completed: {user.email}")
        return {"message": msg.AUTH_RESET_SUCCESS}


        