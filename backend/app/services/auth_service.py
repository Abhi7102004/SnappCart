import secrets
from datetime import datetime,timedelta,timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session
from fastapi import HTTPException,status

from app.models.user import User, UserRole, OAuthProvider
from app.schemas.user import UserRegisterRequest, UserResponse
from app.schemas.auth import RegisterResponse
from app.core.security.password import (
    hash_password, verify_password, DUMMY_HASH
)
from app.core.security.jwt import create_access_token, create_refresh_token
from app.core.config import settings
from loguru import logger

class AuthService:
    # ── REGISTRATION ─────────────────────────────────────────────────
    
    @staticmethod
    def register(
        data:UserRegisterRequest,
        db:Session
    ) -> RegisterResponse:
        """
        Register new user with email/phone + password.
        Handles:
          - Duplicate email/phone check (including soft-deleted)
          - Password hashing
          - Email verification token generation
        """
        
        if(data.email):
            existing = db.query(User).filter(User.email==data.email,User.is_deleted==False).first()
            if(existing):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="An account with this email already exists"
                )
        if data.phone:
            existing = db.query(User).filter(User.phone == data.phone,User.is_deleted == False).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="An account with this phone number already exists"
                )
                
        hashed = hash_password(data.password)
        
        verify_token = None
        verify_token_expires = None
        if(data.email):
            verify_token=secrets.token_urlsafe(32)
            verify_token_expires=datetime.now(timezone.utc)+timedelta(hours=24)

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
        
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
        except Exception:
            db.rollback()
            raise
        
        # TODO Day 27: send actual email via AWS SES
        # For now: log the token (dev mode only)
        
        if settings.debug and verify_token:
            logger.debug(f"Email verify token: {verify_token}")

        return RegisterResponse(
            message="Registration successful. Please verify your email.",
            user=UserResponse.model_validate(user),
            email_verification_sent=bool(data.email),
        )

    @staticmethod
    def verify_email(token:str,db:Session) ->dict:
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
        
        if user.email_verify_token_expires:
            expires=user.email_verify_token_expires
            # Make timezone aware if needed
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=timezone.utc)
            if expires < datetime.now(timezone.utc):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Verification token has expired. Request a new one."
                )
                
        # Already verified?
        if user.is_email_verified:
            return {"message": "Email already verified"}
        
        user.is_email_verified = True
        user.email_verify_token = None
        user.email_verify_token_expires = None
        
        try:
           db.commit()
        except Exception:
            db.rollback()
            raise
           
        logger.info(f"Email verified: {user.email}")
        return {"message": "Email verified successfully"}

    @staticmethod
    def validate_user_active(user:User)-> None:
        """Raise appropriate errors for inactive/banned users"""
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account has been deactivated"
            )

        if user.is_banned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account banned: {user.banned_reason or 'Policy violation'}"
            )
        
        # Check account lockout (failed login attempts)
        if user.locked_until:
            locked=user.locked_until
            if locked.tzinfo is None:
                locked=locked.replace(tzinfo=timezone.utc)
            if locked >datetime.now(timezone.utc):
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail="Account temporarily locked due to too many failed attempts"
                )
        
        