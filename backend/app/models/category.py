import uuid

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from app.core.database import Base

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    slug = Column(String(120), unique=True, nullable=False, index=True)
    
    parent_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True, index=True,
        comment="NULL = top-level category",)
    
    spec_schema = Column(JSONB, nullable=False, default=dict,
        comment=(
            "Free-form spec keys → { label, filterable } metadata. "
            "Drives Meilisearch facets + filter UI."
        ),
    )
    variant_attributes = Column(JSONB, nullable=False, default=list,
        comment="Ordered list of attribute keys valid on variants (e.g. [\"color\", \"size\"])",
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Category id={self.id} name={self.name} parent={self.parent_id}>"