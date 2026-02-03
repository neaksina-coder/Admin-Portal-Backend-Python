# schemas/plan.py
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class PlanBase(BaseModel):
    plan_name: str = Field(..., alias="planName")
    price: float = 0
    features: Optional[Any] = None

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class PlanCreate(PlanBase):
    pass


class Plan(PlanBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        allow_population_by_field_name = True
        populate_by_name = True


class PlanResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: Plan


class PlanListResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    total: int
    data: list[Plan]
