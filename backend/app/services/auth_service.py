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
    MAX_FAILED_LOGIN_ATTEMPTS,
    ACCOUNT_LOCKOUT_MINUTES,
    EMAIL_VERIFY_TOKEN_EXPIRE_HOURS,
    REFRESH_COOKIE_NAME,
    REFRESH_COOKIE_PATH,
)
from app.core.security.password import hash_password, verify_password, DUMMY_HASH
from app.core.security.jwt import (
    create_access_token, create_refresh_token,
    decode_token, get_refresh_token_key,
)
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
                    detail="An account with this email already exists"
                )

        if data.phone:
            existing = db.query(User).filter(
                User.phone == data.phone,
                User.is_deleted == False
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="An account with this phone number already exists"
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
        if settings.debug and verify_token:
            logger.debug(f"Email verify token: {verify_token}")

        return RegisterResponse(
            message="Registration successful. Please verify your email.",
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
                detail="Invalid or expired verification token"
            )

        if is_expired(user.email_verify_token_expires):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification token has expired. Request a new one."
            )

        if user.is_email_verified:
            return {"message": "Email already verified"}

        user.is_email_verified = True
        user.email_verify_token = None
        user.email_verify_token_expires = None
        db.commit()

        logger.info(f"Email verified: {user.email}")
        return {"message": "Email verified successfully"}

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
                detail="Invalid email/phone or password"
            )

        # Active/banned check (no lock check here — handled below,
        # since login uniquely needs to RESET an expired lock)
        if not user.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Account has been deactivated")
        if user.is_banned:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                f"Account banned: {user.banned_reason or 'Policy violation'}"
            )

        # Lock check WITH reset-if-expired (only login does this)
        if user.locked_until:
            if ensure_utc(user.locked_until) > utc_now():
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail=f"Account locked until {user.locked_until.strftime('%H:%M UTC')}. "
                           f"Too many failed login attempts."
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
                    detail=f"Account locked for {ACCOUNT_LOCKOUT_MINUTES} minutes "
                           f"due to too many failed attempts"
                )

            db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email/phone or password"
            )

        # ── Successful login ─────────────────────────────────────
        user.failed_login_attempts = 0
        user.last_failed_login_at = None
        user.locked_until = None
        user.last_login_at = utc_now()
        db.commit()

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
            detail="Invalid or expired refresh token. Please login again."
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
        return {"message": "Logged out successfully"}