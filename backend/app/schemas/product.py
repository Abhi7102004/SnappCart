
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_serializer, field_validator

from app.core.config import settings
from app.schemas.common import PyObjectId

class VariantSchema(BaseModel):
    variant_id: UUID = Field(default_factory=uuid4)
    sku: str = Field(min_length=1, max_length=100)
    attributes: Dict[str, str]
    price: int = Field(ge=0)
    stock: int = Field(ge=0)
    image: Optional[str] = None
    
class ProductCreateRequest(BaseModel):
    seller_id: UUID
    category_id:UUID
    name: str = Field(min_length=1, max_length=200)
    slug: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=10)
    brand: str = Field(min_length=1, max_length=100)
    price: int = Field(ge=0)
    mrp: int = Field(ge=0)
    specs: Dict[str, str] = Field(default_factory=dict)
    images: List[str] = Field(min_length=1)
    variants: List[VariantSchema] = Field(min_length=1)
    tags: List[str] = Field(default_factory=list)

    @field_validator("mrp")
    @classmethod
    def mrp_not_below_price(cls, v: int, info):
        price = info.data.get("price")
        if price is not None and v < price:
            raise ValueError("MRP cannot be less than the selling price.")
        return v
    
class ProductResponse(BaseModel):
    id: PyObjectId = Field(alias="_id")
    seller_id: UUID
    category_id: UUID
    name: str
    slug: str
    description: str
    brand: str
    price: int
    mrp: int
    specs: Dict[str, str]
    images: List[str]
    variants: List[VariantSchema]
    stock: int
    tags: List[str]
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    @field_serializer("images")
    def build_image_urls(self, images: List[str]) -> List[str]:
        """
        Convert image filenames to full URLs using the CloudFront domain.
        """
        domain = settings.cloudfront_domain
        if not domain:
            return images
        return [f"https://{domain}/{key}" for key in images]

class ProductUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    slug: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, min_length=10)
    brand: Optional[str] = Field(default=None, min_length=1, max_length=100)
    price: Optional[int] = Field(default=None, ge=0)
    mrp: Optional[int] = Field(default=None, ge=0)
    specs: Optional[Dict[str, str]] = None
    images: Optional[List[str]] = Field(default=None, min_length=1)
    variants: Optional[List[VariantSchema]] = Field(default=None, min_length=1)
    tags: Optional[List[str]] = None
    is_published: Optional[bool] = None

class ProductListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[ProductResponse]
    