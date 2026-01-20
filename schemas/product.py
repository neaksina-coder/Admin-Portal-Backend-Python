# schemas/product.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Import Category schema
from schemas.category import Category

class ProductBase(BaseModel):
    name: str
    sku: str
    description: Optional[str] = None
    category_id: Optional[int] = None  # Changed from category string to category_id
    price: float = Field(..., gt=0)
    cost: Optional[float] = Field(None, ge=0)
    stock: int = Field(default=0, ge=0)
    unit: Optional[str] = None
    status: str = 'active'

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None  # Changed
    price: Optional[float] = Field(None, gt=0)
    cost: Optional[float] = Field(None, ge=0)
    stock: Optional[int] = Field(None, ge=0)
    unit: Optional[str] = None
    status: Optional[str] = None

class Product(ProductBase):
    id: int
    created_at: datetime
    category: Optional[Category] = None  # Include category data in response

    class Config:
        from_attributes = True

# Response schemas
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

class ProductDeleteResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    id: int