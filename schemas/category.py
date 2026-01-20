# schemas/category.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    status: str = 'active'

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class Category(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Response schemas
class CategoryResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: Category

class CategoryListResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    total: int
    data: list[Category]

class CategoryDeleteResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    id: int