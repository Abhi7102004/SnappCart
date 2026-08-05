from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security.dependencies import require_admin
from app.core.constants import DEFAULT_PAGE_SIZE
from app.models.user import User
from app.schemas.admin import PaginatedUsersResponse,BanUserRequest,UpdateUserRoleRequest
from app.schemas.auth import MessageResponse
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin",tags=["Admin"])

@router.get("/users",response_model=PaginatedUsersResponse)
async def list_users(
    page: int = Query(1,ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE,ge=1,le=100),
    db:Session = Depends(get_db),
    admin: User = Depends(require_admin)
) -> PaginatedUsersResponse:
    return AdminService.list_users(db,page,page_size)

@router.patch("/users/{user_id}/ban",response_model=MessageResponse)
async def ban_user(
    user_id:str,
    data:BanUserRequest,
    db:Session = Depends(get_db),
    admin: User = Depends(require_admin)
) -> MessageResponse:
    result = await AdminService.ban_user(user_id,data.reason,admin,db)
    return MessageResponse(message=result["message"])

@router.patch("/users/{user_id}/unban", response_model=MessageResponse)
async def unban_user(
    user_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> MessageResponse:
    result = AdminService.unban_user(user_id, db)
    return MessageResponse(message=result["message"])

@router.patch("/users/{user_id}/role", response_model=MessageResponse)
async def update_user_role(
    user_id: str,
    data: UpdateUserRoleRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> MessageResponse:
    result = AdminService.update_role(user_id, data.role, admin, db)
    return MessageResponse(message=result["message"])
