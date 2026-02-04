# schemas/subscription_event.py
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class SubscriptionEvent(BaseModel):
    id: int
    subscription_id: int = Field(..., alias="subscriptionId")
    business_id: int = Field(..., alias="businessId")
    invoice_id: Optional[int] = Field(None, alias="invoiceId")
    actor_user_id: Optional[int] = Field(None, alias="actorUserId")
    event_type: str = Field(..., alias="eventType")
    payload: Optional[Any] = None
    created_at: datetime

    class Config:
        from_attributes = True
        allow_population_by_field_name = True
        populate_by_name = True


class SubscriptionEventListResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    total: int
    data: list[SubscriptionEvent]
