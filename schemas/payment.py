# schemas/payment.py
from pydantic import BaseModel, Field
from typing import Optional


class PayPalOrderCreate(BaseModel):
    plan_name: str = Field(..., alias="planName")
    billing_cycle: str = Field("monthly", alias="billingCycle")  # monthly | yearly
    business_name: str = Field(..., alias="businessName")
    email: str
    password: str

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class PayPalOrderResponse(BaseModel):
    order_id: str = Field(..., alias="orderId")


class PayPalCaptureRequest(BaseModel):
    order_id: str = Field(..., alias="orderId")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class PayPalCaptureResponse(BaseModel):
    success: bool
    message: str
    business_id: Optional[int] = Field(None, alias="businessId")
    subscription_id: Optional[int] = Field(None, alias="subscriptionId")
