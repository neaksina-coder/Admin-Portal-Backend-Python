# schemas/category.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    business_id: int = Field(..., alias="businessId")
    name: str
    slug: str
    description: Optional[str] = None
    status: str = "active"

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class Category(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        allow_population_by_field_name = True
        populate_by_name = True


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
