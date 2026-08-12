from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from fastapi import HTTPException, status

from app.core import messages as msg
from app.core.mongo import products_collection
from app.schemas.product import ProductCreateRequest, ProductResponse

class ProductService:
    
    @staticmethod
    async def create_product(data:ProductCreateRequest) -> ProductResponse:
        """
        Create a new product in the database.
        """
        
        now = datetime.now(timezone.utc)
        stock = sum(v.stock for v in data.variants)
        
        doc = data.model_dump(mode="json")
        doc["stock"] = stock
        doc["is_published"] = False
        doc["is_deleted"] = False
        doc["created_at"] = now
        doc["updated_at"] = now
        
        result = await products_collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        
        return ProductResponse.model_validate(doc)

    @staticmethod
    async def get_product_by_id(product_id: str) -> ProductResponse:
        
        if not ObjectId.is_valid(product_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=msg.PRODUCT_INVALID_ID
            )
        
        doc = await products_collection.find_one({"_id": ObjectId(product_id), "is_deleted": False})
        
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=msg.PRODUCT_NOT_FOUND
            )
        
        return ProductResponse.model_validate(doc)
        
