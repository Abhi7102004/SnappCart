from pydantic import BaseModel
from typing import List
from app.schemas.user import UserResponse
from app.models.user import UserRole

class PaginatedUsersResponse(BaseModel):
    items:List[UserResponse]
    total:int
    page:int
    page_size:int
    total_pages: int
    
class BanUserRequest(BaseModel):
    reason: str

class UpdateUserRoleRequest(BaseModel):
    role: UserRole