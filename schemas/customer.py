# schemas/customer.py
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class CustomerBase(BaseModel):
    business_id: int = Field(..., alias="businessId")
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    segment: Optional[str] = None
    notes: Optional[str] = None
    churn_risk_score: Optional[float] = Field(None, alias="churnRiskScore")
    lifetime_value: Optional[float] = Field(None, alias="lifetimeValue")
    next_best_product: Optional[str] = Field(None, alias="nextBestProduct")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    segment: Optional[str] = None
    notes: Optional[str] = None
    churn_risk_score: Optional[float] = Field(None, alias="churnRiskScore")
    lifetime_value: Optional[float] = Field(None, alias="lifetimeValue")
    next_best_product: Optional[str] = Field(None, alias="nextBestProduct")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class Customer(CustomerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        allow_population_by_field_name = True
        populate_by_name = True


class CustomerResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: Customer


class CustomerListResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    total: int
    data: list[Customer]
