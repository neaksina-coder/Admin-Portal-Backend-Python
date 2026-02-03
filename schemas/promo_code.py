# schemas/promo_code.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PromoCodeBase(BaseModel):
    business_id: int = Field(..., alias="businessId")
    code: str
    discount_type: str = Field(..., alias="discountType")  # percent | fixed
    discount_value: float = Field(..., alias="discountValue")
    start_date: Optional[datetime] = Field(None, alias="startDate")
    end_date: Optional[datetime] = Field(None, alias="endDate")
    usage_limit: Optional[int] = Field(None, alias="usageLimit")
    is_active: bool = Field(True, alias="isActive")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class PromoCodeCreate(PromoCodeBase):
    pass


class PromoCodeUpdate(BaseModel):
    code: Optional[str] = None
    discount_type: Optional[str] = Field(None, alias="discountType")
    discount_value: Optional[float] = Field(None, alias="discountValue")
    start_date: Optional[datetime] = Field(None, alias="startDate")
    end_date: Optional[datetime] = Field(None, alias="endDate")
    usage_limit: Optional[int] = Field(None, alias="usageLimit")
    is_active: Optional[bool] = Field(None, alias="isActive")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class PromoCode(PromoCodeBase):
    id: int
    used_count: int = Field(..., alias="usedCount")
    created_at: datetime

    class Config:
        from_attributes = True
        allow_population_by_field_name = True
        populate_by_name = True


class PromoCodeResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: PromoCode


class PromoCodeListResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    total: int
    data: list[PromoCode]


class PromoApplyRequest(BaseModel):
    business_id: int = Field(..., alias="businessId")
    code: str
    amount: float

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class PromoApplyResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: dict
