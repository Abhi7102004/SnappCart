from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security.dependencies import require_admin
from app.models.user import User
from app.schemas.auth import MessageResponse
from app.schemas.category import (
    CategoryCreateRequest,
    CategoryResponse,
    CategoryUpdateRequest,
)
from app.services.category_service import CategoryService

router = APIRouter(prefix="/admin/categories", tags=["Admin: Categories"])

@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> CategoryResponse:
    return CategoryService.create(db, data)

@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    data: CategoryUpdateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> CategoryResponse:
    return CategoryService.update(db, category_id, data)

@router.delete("/{category_id}", response_model=MessageResponse)
async def delete_category(
    category_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> MessageResponse:
    return CategoryService.delete(db, category_id)

@router.get("", response_model=list[CategoryResponse])
async def list_categories(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[CategoryResponse]:
    return CategoryService.list(db)
