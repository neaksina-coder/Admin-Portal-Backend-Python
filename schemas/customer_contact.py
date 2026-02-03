# schemas/customer_contact.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CustomerContactBase(BaseModel):
    business_id: int = Field(..., alias="businessId")
    customer_id: int = Field(..., alias="customerId")
    channel: Optional[str] = None
    summary: str
    contacted_at: datetime = Field(..., alias="contactedAt")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class CustomerContactCreate(CustomerContactBase):
    pass


class CustomerContact(CustomerContactBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
        allow_population_by_field_name = True
        populate_by_name = True


class CustomerContactResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: CustomerContact


class CustomerContactListResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    total: int
    data: list[CustomerContact]
