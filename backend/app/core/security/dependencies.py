# app/core/security/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from typing import Optional

from app.core.database import get_db
from app.core.security.jwt import decode_token
from app.core.security.utils import ensure_utc, utc_now
from app.models.user import User, UserRole
from app.core import messages as msg

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False
)


def validate_user_active(user: User) -> None:
    """
    Checks that apply on EVERY authenticated request:
    active + not banned + not currently locked.

    Used by: get_current_user (every request)
             AuthService.refresh_token

    Does NOT reset an expired lock — only login() does that,
    since only the login flow should "forgive" an expired lockout.
    """
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=msg.AUTH_ACCOUNT_DEACTIVATED
        )

    if user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=msg.AUTH_ACCOUNT_BANNED
        )

    if user.locked_until and ensure_utc(user.locked_until) > utc_now():
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=msg.AUTH_ACCOUNT_TEMPORARILY_LOCKED
        )

async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Extract + verify JWT access token. Returns authenticated User object."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=msg.AUTH_CREDENTIALS_INVALID,
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        if not user_id or token_type != "access":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False,
    ).first()

    if not user:
        raise credentials_exception

    validate_user_active(user)

    return user


async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Like get_current_user but returns None instead of raising.
    Used for routes that work for both guests and logged-in users.
    """
    if not token:
        return None
    try:
        return await get_current_user(token=token, db=db)
    except HTTPException:
        return None


# ── Role-based dependencies ──────────────────────────────────────

def require_roles(*roles: UserRole):
    """Factory that returns a dependency checking for specific roles"""
    async def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {[r.value for r in roles]}"
            )
        return current_user
    return role_checker

def verify_ownership(resource_owner_id, current_user: User) -> None:
    if current_user.role==UserRole.admin:
        return
    if str(resource_owner_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource"
        )

require_customer = require_roles(UserRole.customer, UserRole.seller, UserRole.admin)
require_seller = require_roles(UserRole.seller, UserRole.admin)
require_admin = require_roles(UserRole.admin)