# schemas/product.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from schemas.category import Category


class ProductBase(BaseModel):
    business_id: int = Field(..., alias="businessId")
    name: str
    sku: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    price: float
    cost: Optional[float] = None
    stock: int = 0
    unit: Optional[str] = None
    status: str = "active"

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    price: Optional[float] = None
    cost: Optional[float] = None
    stock: Optional[int] = None
    unit: Optional[str] = None
    status: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    category: Optional[Category] = None

    class Config:
        from_attributes = True
        allow_population_by_field_name = True
        populate_by_name = True


class ProductResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: Product


class ProductListResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    total: int
    data: list[Product]
