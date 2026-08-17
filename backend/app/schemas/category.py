from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

class CategoryCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    slug: str = Field(min_length=1, max_length=120)
    parent_id: Optional[UUID] = None
    spec_schema: Dict[str, Dict[str, object]] = Field(default_factory=dict)
    variant_attributes: List[str] = Field(default_factory=list)
    display_order: int = 0

class CategoryUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    parent_id: Optional[UUID] = None
    spec_schema: Optional[Dict[str, Dict[str, object]]] = None
    variant_attributes: Optional[List[str]] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None

class CategoryResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    parent_id: Optional[UUID]
    spec_schema: Dict[str, Dict[str, object]]
    variant_attributes: List[str]
    display_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}