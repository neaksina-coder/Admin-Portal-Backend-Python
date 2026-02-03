# schemas/business.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class BusinessTimestamps(BaseModel):
    created: datetime
    updated: datetime


class BusinessBase(BaseModel):
    name: str
    tenant_id: Optional[str] = Field(None, alias="tenantId")
    plan: Optional[dict] = None
    status: str = "active"

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class BusinessCreate(BusinessBase):
    pass


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
