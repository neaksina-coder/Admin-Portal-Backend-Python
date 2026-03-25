# schemas/sale.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SaleItemBase(BaseModel):
    product_id: int = Field(..., alias="productId")
    quantity: int = 1
    unit_price: float = Field(..., alias="unitPrice")
    total_price: float = Field(..., alias="totalPrice")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class SaleItemCreate(SaleItemBase):
    pass


class SaleItem(SaleItemBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
        allow_population_by_field_name = True
        populate_by_name = True


class SaleBase(BaseModel):
    business_id: int = Field(..., alias="businessId")
    customer_id: Optional[int] = Field(None, alias="customerId")
    quantity: int = 1
    total_price: float = Field(..., alias="totalPrice")
    original_amount: Optional[float] = Field(None, alias="originalAmount")
    discount_amount: Optional[float] = Field(None, alias="discountAmount")
    promo_code_id: Optional[int] = Field(None, alias="promoCodeId")
    transaction_date: datetime = Field(..., alias="transactionDate")
    invoice_number: Optional[str] = Field(None, alias="invoiceNumber")
    demand_prediction: Optional[float] = Field(None, alias="demandPrediction")
    anomaly_flag: Optional[bool] = Field(None, alias="anomalyFlag")
    items: Optional[List[SaleItemCreate]] = None

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class SaleCreate(SaleBase):
    pass


class Sale(SaleBase):
    id: int
    created_at: datetime
    items: Optional[List[SaleItem]] = None

    class Config:
        from_attributes = True
        allow_population_by_field_name = True
        populate_by_name = True


class SaleResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: Sale


class SaleListResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    total: int
    data: list[Sale]
