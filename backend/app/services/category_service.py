# app/services/category_service.py

from uuid import UUID

from fastapi import HTTPException, status
from loguru import logger
from sqlalchemy.orm import Session

from app.core import messages as msg
from app.core.mongo import products_collection
from app.models.category import Category
from app.schemas.category import (
    CategoryCreateRequest,
    CategoryResponse,
    CategoryUpdateRequest,
)


class CategoryService:

    @staticmethod
    def _get_or_404(db: Session, category_id: UUID) -> Category:
        cat = db.query(Category).filter(Category.id == category_id).first()
        if not cat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=msg.CATEGORY_NOT_FOUND,
            )
        return cat

    @staticmethod
    def _would_be_circular(db: Session, category_id: UUID, new_parent_id: UUID) -> bool:
        """
        Walk UP the parent chain from new_parent_id — if we ever hit
        category_id itself, setting new_parent_id would create a cycle.
        """
        current = new_parent_id
        while current is not None:
            if current == category_id:
                return True
            parent = db.query(Category.parent_id).filter(Category.id == current).first()
            current = parent[0] if parent else None
        return False

    @staticmethod
    def create(db: Session, data: CategoryCreateRequest) -> CategoryResponse:
        existing = db.query(Category).filter(Category.slug == data.slug).first()
        if existing:
            raise HTTPException(status.HTTP_409_CONFLICT, msg.CATEGORY_SLUG_EXISTS)

        if data.parent_id:
            parent = db.query(Category).filter(Category.id == data.parent_id).first()
            if not parent:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, msg.CATEGORY_PARENT_NOT_FOUND)

        cat = Category(
            name=data.name,
            slug=data.slug,
            parent_id=data.parent_id,
            spec_schema=data.spec_schema,
            variant_attributes=data.variant_attributes,
            display_order=data.display_order,
        )
        db.add(cat)
        db.commit()
        db.refresh(cat)
        logger.info(f"Category created: {cat.slug}")
        return CategoryResponse.model_validate(cat)

    @staticmethod
    def update(db: Session, category_id: UUID, data: CategoryUpdateRequest) -> CategoryResponse:
        cat = CategoryService._get_or_404(db, category_id)

        if data.parent_id is not None and data.parent_id != cat.parent_id:
            if data.parent_id == category_id:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, msg.CATEGORY_CIRCULAR_PARENT)
            new_parent = db.query(Category).filter(Category.id == data.parent_id).first()
            if not new_parent:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, msg.CATEGORY_PARENT_NOT_FOUND)
            if CategoryService._would_be_circular(db, category_id, data.parent_id):
                raise HTTPException(status.HTTP_400_BAD_REQUEST, msg.CATEGORY_CIRCULAR_PARENT)

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(cat, field, value)

        db.commit()
        db.refresh(cat)
        return CategoryResponse.model_validate(cat)

    @staticmethod
    async def delete(db: Session, category_id: UUID) -> dict:
        cat = CategoryService._get_or_404(db, category_id)

        product_count = await products_collection.count_documents({
            "category_id": str(category_id),
            "is_deleted": False,
        })
        if product_count > 0:
            raise HTTPException(status.HTTP_409_CONFLICT, msg.CATEGORY_HAS_PRODUCTS)

        cat.is_active = False
        db.commit()
        logger.info(f"Category deactivated: {cat.slug}")
        return {"message": "Category deleted"}

    @staticmethod
    def list_all(db: Session) -> list[CategoryResponse]:
        cats = (
            db.query(Category)
            .filter(Category.is_active == True)
            .order_by(Category.display_order, Category.name)
            .all()
        )
        return [CategoryResponse.model_validate(c) for c in cats]

    @staticmethod
    def get_or_404(db: Session, category_id: UUID) -> Category:
        """Public entrypoint — reused by ProductService for cross-DB validation."""
        return CategoryService._get_or_404(db, category_id)