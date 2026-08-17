# app/api/v1/products/router.py

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.constants import DEFAULT_PAGE_SIZE
from app.core.database import get_db
from app.core.security.dependencies import (
    get_current_user,
    get_current_user_optional,
    require_seller,
)
from app.models.user import User
from app.schemas.auth import MessageResponse
from app.schemas.product import (
    ProductCreateRequest,
    ProductListResponse,
    ProductResponse,
    ProductUpdateRequest,
)
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_seller),
) -> ProductResponse:
    return await ProductService.create_product(db, data, current_user)


@router.get("", response_model=ProductListResponse)
async def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1),
    category_id: Optional[str] = None,
    seller_id: Optional[str] = None,
) -> ProductListResponse:
    """
    Public listing — only published + non-deleted products.
    Sellers browsing their own drafts should use GET /products/mine
    """
    return await ProductService.list_products(
        page=page,
        page_size=page_size,
        category_id=category_id,
        seller_id=seller_id,
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> ProductResponse:

    include_drafts = current_user is not None
    return await ProductService.get_product_by_id(
        product_id,
        include_drafts=include_drafts,
        current_user=current_user,
    )


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    data: ProductUpdateRequest,
    current_user: User = Depends(require_seller),
) -> ProductResponse:
    return await ProductService.update_product(product_id, data, current_user)


@router.delete("/{product_id}", response_model=MessageResponse)
async def delete_product(
    product_id: str,
    current_user: User = Depends(require_seller),
) -> MessageResponse:
    result = await ProductService.soft_delete_product(product_id, current_user)
    return MessageResponse(message=result["message"])