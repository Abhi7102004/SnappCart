# app/services/product_service.py — REPLACE the existing file

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from bson import ObjectId
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from pymongo.errors import DuplicateKeyError
from app.core import messages as msg
from app.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from app.core.mongo import products_collection
from app.models.user import User, UserRole
from app.schemas.product import (
    ProductCreateRequest,
    ProductListResponse,
    ProductResponse,
    ProductUpdateRequest,
)
from app.services.category_service import CategoryService


class ProductService:

    # ── Helpers ─────────────────────────────────────────

    @staticmethod
    def _validate_id(product_id: str) -> ObjectId:
        if not ObjectId.is_valid(product_id):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, msg.PRODUCT_INVALID_ID)
        return ObjectId(product_id)

    @staticmethod
    async def _get_doc_or_404(oid: ObjectId) -> dict:
        doc = await products_collection.find_one({"_id": oid, "is_deleted": False})
        if not doc:
            raise HTTPException(status.HTTP_404_NOT_FOUND, msg.PRODUCT_NOT_FOUND)
        return doc

    @staticmethod
    def _verify_product_ownership(doc: dict, current_user: User) -> None:
        """
        verify_ownership (Day 29) pattern applied to product docs.
        Admins bypass; sellers can only touch their own products.
        """
        if current_user.role == UserRole.admin:
            return
        if doc.get("seller_id") != str(current_user.id):
            raise HTTPException(status.HTTP_403_FORBIDDEN, msg.PRODUCT_UPDATE_FORBIDDEN)

    # ── CREATE ──────────────────────────────────────────

    @staticmethod
    async def create_product(
        db: Session,
        data: ProductCreateRequest,
        current_user: User,
    ) -> ProductResponse:
        seller_id_str = str(current_user.id)

        CategoryService.get_or_404(db, data.category_id)

        # Per-seller slug uniqueness
        clash = await products_collection.find_one({
            "seller_id": seller_id_str,
            "slug": data.slug,
            "is_deleted": False,
        })
        if clash:
            raise HTTPException(status.HTTP_409_CONFLICT, msg.PRODUCT_SLUG_EXISTS)

        now = datetime.now(timezone.utc)
        stock = sum(v.stock for v in data.variants)

        doc = data.model_dump(mode="json")
        doc["seller_id"] = seller_id_str
        doc["category_id"] = str(data.category_id)
        doc["stock"] = stock
        doc["is_published"] = False
        doc["is_deleted"] = False
        doc["created_at"] = now
        doc["updated_at"] = now

        try:
            result = await products_collection.insert_one(doc)
        except DuplicateKeyError:
            raise HTTPException(status.HTTP_409_CONFLICT, msg.PRODUCT_SLUG_EXISTS)
        
        doc["_id"] = result.inserted_id

        return ProductResponse.model_validate(doc)

    # ── READ ────────────────────────────────────────────

    @staticmethod
    async def get_product_by_id(
        product_id: str,
        include_drafts: bool = False,
        current_user: Optional[User] = None,
    ) -> ProductResponse:
        oid = ProductService._validate_id(product_id)

        query: dict = {"_id": oid, "is_deleted": False}
        if not include_drafts:
            query["is_published"] = True

        doc = await products_collection.find_one(query)
        if not doc:
            raise HTTPException(status.HTTP_404_NOT_FOUND, msg.PRODUCT_NOT_FOUND)

        # If a draft is being fetched, only owner or admin allowed
        if not doc.get("is_published", False):
            if current_user is None:
                raise HTTPException(status.HTTP_404_NOT_FOUND, msg.PRODUCT_NOT_FOUND)
            ProductService._verify_product_ownership(doc, current_user)

        return ProductResponse.model_validate(doc)

    @staticmethod
    async def list_products(
        page: int = 1,
        page_size: int = DEFAULT_PAGE_SIZE,
        category_id: Optional[str] = None,
        seller_id: Optional[str] = None,
        include_drafts: bool = False,
    ) -> ProductListResponse:
        page_size = min(page_size, MAX_PAGE_SIZE)
        page = max(page, 1)

        query: dict = {"is_deleted": False}
        if not include_drafts:
            query["is_published"] = True
        if category_id:
            query["category_id"] = category_id
        if seller_id:
            query["seller_id"] = seller_id

        total = await products_collection.count_documents(query)

        cursor = (
            products_collection
            .find(query)
            .sort("_id", -1)                    # recent-first (Day 39)
            .skip((page - 1) * page_size)
            .limit(page_size)
        )
        items = [ProductResponse.model_validate(doc) async for doc in cursor]

        return ProductListResponse(
            total=total, page=page, page_size=page_size, items=items,
        )

    # ── UPDATE ──────────────────────────────────────────

    @staticmethod
    async def update_product(
        product_id: str,
        data: ProductUpdateRequest,
        current_user: User,
    ) -> ProductResponse:
        oid = ProductService._validate_id(product_id)
        doc = await ProductService._get_doc_or_404(oid)
        ProductService._verify_product_ownership(doc, current_user)

        update_fields = data.model_dump(exclude_unset=True, mode="json")
        if not update_fields:
            return ProductResponse.model_validate(doc)

        if "variants" in update_fields:
            update_fields["stock"] = sum(v["stock"] for v in update_fields["variants"])

        update_fields["updated_at"] = datetime.now(timezone.utc)

        try:
            await products_collection.update_one({"_id": oid}, {"$set": update_fields})
        except DuplicateKeyError:
            raise HTTPException(status.HTTP_409_CONFLICT, msg.PRODUCT_SLUG_EXISTS)
        updated = await products_collection.find_one({"_id": oid})
        return ProductResponse.model_validate(updated)

    # ── DELETE (soft) ───────────────────────────────────

    @staticmethod
    async def soft_delete_product(product_id: str, current_user: User) -> dict:
        oid = ProductService._validate_id(product_id)
        doc = await ProductService._get_doc_or_404(oid)
        ProductService._verify_product_ownership(doc, current_user)

        await products_collection.update_one(
            {"_id": oid},
            {"$set": {
                "is_deleted": True,
                "is_published": False,
                "updated_at": datetime.now(timezone.utc),
            }},
        )
        return {"message": "Product deleted successfully."}