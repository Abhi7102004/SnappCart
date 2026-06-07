# backend/app/models/user.py

import uuid
import enum
from datetime import datetime

from sqlalchemy import (
    Column, String, Boolean,
    DateTime, Integer, Text,
    Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


# ─────────────────────────────────────────────────────────
# Enums — defined BEFORE the model that uses them
# ─────────────────────────────────────────────────────────

class UserRole(str, enum.Enum):
    customer = "customer"
    seller = "seller"
    admin = "admin"


class UserGender(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"
    prefer_not_to_say = "prefer_not_to_say"


class OAuthProvider(str, enum.Enum):
    local = "local"        # registered with email/password
    google = "google"      # logged in via Google
    github = "github"      # logged in via GitHub


# ─────────────────────────────────────────────────────────
# User Model
# ─────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    # ── Primary Key ──────────────────────────────────────
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Unique user identifier (UUID v4)"
    )

    # ── Identity ─────────────────────────────────────────
    email = Column(
        String(255),
        unique=True,
        nullable=True,
        index=True,
        comment="User email — nullable for OAuth users who don't share email"
    )
    phone = Column(
        String(20),
        unique=True,
        nullable=True,
        index=True,
        comment="Phone number with country code e.g. +919876543210"
    )
    username = Column(
        String(50),
        unique=True,
        nullable=True,
        index=True,
        comment="Unique username for seller profiles"
    )
    full_name = Column(
        String(255),
        nullable=True,
        comment="Full display name"
    )

    # ── Security ─────────────────────────────────────────
    hashed_password = Column(
        String(255),
        nullable=True,
        comment="bcrypt hashed password — NULL for OAuth users"
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="False = account deactivated by user"
    )
    is_banned = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="True = banned by admin"
    )
    banned_reason = Column(
        Text,
        nullable=True,
        comment="Admin note explaining why user was banned"
    )
    banned_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When the ban was applied"
    )
    failed_login_attempts = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Consecutive failed login attempts — reset on success"
    )
    last_failed_login_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When last failed login attempt occurred"
    )
    locked_until = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Account locked until this time after too many failures"
    )

    # ── Email Verification ────────────────────────────────
    is_email_verified = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="True after user clicks verification link in email"
    )
    email_verify_token = Column(
        String(255),
        nullable=True,
        index=True,
        comment="Random token sent in verification email"
    )
    email_verify_token_expires = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Token expires after 24 hours"
    )

    # ── Phone Verification ────────────────────────────────
    is_phone_verified = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="True after user verifies OTP sent to phone"
    )

    # ── Password Reset ────────────────────────────────────
    password_reset_token = Column(
        String(255),
        nullable=True,
        index=True,
        comment="Random token sent in password reset email"
    )
    password_reset_token_expires = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Token expires after 1 hour"
    )

    # ── OAuth ─────────────────────────────────────────────
    oauth_provider = Column(
        SQLEnum(OAuthProvider),
        default=OAuthProvider.local,
        nullable=False,
        comment="How user registered — local/google/github"
    )
    google_id = Column(
        String(255),
        unique=True,
        nullable=True,
        index=True,
        comment="Google's unique user ID from OAuth"
    )
    github_id = Column(
        String(255),
        unique=True,
        nullable=True,
        index=True,
        comment="GitHub's unique user ID from OAuth"
    )
    oauth_avatar_url = Column(
        String(500),
        nullable=True,
        comment="Profile picture URL from OAuth provider"
    )

    # ── Role ─────────────────────────────────────────────
    role = Column(
        SQLEnum(UserRole),
        default=UserRole.customer,
        nullable=False,
        index=True,
        comment="customer/seller/admin — controls permissions"
    )

    # ── Profile ───────────────────────────────────────────
    avatar_url = Column(
        String(500),
        nullable=True,
        comment="Custom profile picture uploaded to AWS S3"
    )
    date_of_birth = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Used for age verification and personalization"
    )
    gender = Column(
        SQLEnum(UserGender),
        nullable=True,
        comment="Optional — used for personalized recommendations"
    )

    # ── Timestamps ────────────────────────────────────────
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="When account was created"
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Auto-updates whenever any field changes"
    )
    last_login_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last successful login timestamp"
    )

    # ── Soft Delete ───────────────────────────────────────
    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="True = user deleted account (soft delete)"
    )
    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When user deleted their account"
    )

    def __repr__(self):
        return f"<User id={self.id} email={self.email} role={self.role}>"