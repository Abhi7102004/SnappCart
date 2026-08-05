import math
from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from loguru import logger

from app.models.user import User,UserRole
from app.schemas.admin import PaginatedUsersResponse
from app.schemas.user import UserResponse
from app.core.constants import DEFAULT_PAGE_SIZE,MAX_PAGE_SIZE
from app.core.security.jwt import get_refresh_token_key
from app.core.security.utils import utc_now
from app.core.redis import redis_client

class AdminService:
    
    @staticmethod
    def list_users(db:Session,page:int=1,page_size:int=DEFAULT_PAGE_SIZE) ->PaginatedUsersResponse:
        page_size = min(page_size, MAX_PAGE_SIZE)
        page = max(page, 1)

        query = db.query(User).filter(User.is_deleted == False)
        total=query.count()
        
        users = (
            query.order_by(User.created_at.desc())
            .offset((page-1)*page_size)
            .limit(page_size)
            .all()
        )
        
        return PaginatedUsersResponse(
            items=[UserResponse.model_validate(u) for u in users],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=math.ceil(total/page_size) if total else 0
        )

    @staticmethod
    async def ban_user(user_id:str,reason:str,admin:User,db:Session) ->dict:
        if str(user_id) == str(admin.id):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "You cannot ban your own account")
        
        user = db.query(User).filter(User.id==user_id,User.is_deleted==False).first()
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

        if user.role==admin.role:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Cannot ban another admin")
        
        user.is_banned = True
        user.banned_reason = reason
        user.banned_at = utc_now()
        db.commit()

        redis_key = get_refresh_token_key(str(user.id))
        await redis_client.delete(redis_key)

        logger.info(f"User banned by {admin.email}: {user.email or user.phone} — {reason}")
        return {"message": "User banned successfully"}
    
    @staticmethod
    def unban_user(user_id: str, db: Session) -> dict:
        user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

        user.is_banned = False
        user.banned_reason = None
        user.banned_at = None
        db.commit()

        logger.info(f"User unbanned: {user.email or user.phone}")
        return {"message": "User unbanned successfully"}
    
    @staticmethod
    def update_role(user_id: str, new_role: UserRole, admin: User, db: Session) -> dict:
        if str(user_id) == str(admin.id):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "You cannot change your own role")

        user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

        old_role = user.role
        user.role = new_role
        db.commit()

        logger.info(f"Role changed by {admin.email}: {user.email} {old_role.value} → {new_role.value}")
        return {"message": f"User role updated to {new_role.value}"}