# schemas/invoice.py
from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class InvoiceBase(BaseModel):
    business_id: int = Field(..., alias="businessId")
    subscription_id: Optional[int] = Field(None, alias="subscriptionId")
    amount: float
    currency: str = "USD"
    payment_status: str = Field("pending", alias="paymentStatus")
    payment_method: Optional[str] = Field(None, alias="paymentMethod")
    due_date: Optional[date] = Field(None, alias="dueDate")
    payment_date: Optional[date] = Field(None, alias="paymentDate")
    metadata_json: Optional[Any] = Field(
        None,
        validation_alias="metadata",
        serialization_alias="metadata",
    )

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceStatusUpdate(BaseModel):
    payment_status: str = Field(..., alias="paymentStatus")
    payment_method: Optional[str] = Field(None, alias="paymentMethod")
    payment_date: Optional[date] = Field(None, alias="paymentDate")
    metadata_json: Optional[Any] = Field(
        None,
        validation_alias="metadata",
        serialization_alias="metadata",
    )

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class Invoice(InvoiceBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
        allow_population_by_field_name = True
        populate_by_name = True


class InvoiceResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: Invoice


class InvoiceListResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    total: int
    data: list[Invoice]
