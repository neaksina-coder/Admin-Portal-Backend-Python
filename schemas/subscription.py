# schemas/subscription.py
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import date, datetime


class SubscriptionBase(BaseModel):
    business_id: int = Field(..., alias="businessId")
    plan_id: int = Field(..., alias="planId")
    start_date: date = Field(..., alias="startDate")
    end_date: Optional[date] = Field(None, alias="endDate")
    status: str = "active"
    billing_history: Optional[Any] = Field(None, alias="billingHistory")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class SubscriptionCreate(SubscriptionBase):
    pass


class Subscription(SubscriptionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
        allow_population_by_field_name = True
        populate_by_name = True


class SubscriptionResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: Subscription


class SubscriptionListResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    total: int
    data: list[Subscription]
