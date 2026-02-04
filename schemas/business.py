# schemas/business.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class BusinessTimestamps(BaseModel):
    created: datetime
    updated: datetime


class BusinessBase(BaseModel):
    name: str
    tenant_id: Optional[str] = Field(None, alias="tenantId")
    plan_id: Optional[int] = Field(None, alias="planId")
    plan: Optional[dict] = None
    status: str = "active"
    suspended_at: Optional[datetime] = Field(None, alias="suspendedAt")
    suspended_reason: Optional[str] = Field(None, alias="suspendedReason")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class BusinessCreate(BusinessBase):
    pass


class BusinessSuspendRequest(BaseModel):
    reason: Optional[str] = None


class Business(BusinessBase):
    id: int
    timestamps: BusinessTimestamps

    class Config:
        from_attributes = True
        allow_population_by_field_name = True
        populate_by_name = True


class BusinessResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: Business


class BusinessListResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    total: int
    data: list[Business]
