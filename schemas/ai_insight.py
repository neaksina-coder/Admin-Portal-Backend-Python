# schemas/ai_insight.py
from pydantic import BaseModel, Field
from typing import Optional, Any, Literal
from datetime import datetime


class AIInsightBase(BaseModel):
    business_id: int = Field(..., alias="businessId")
    type: Literal["insight", "prediction"]
    input_data: Optional[Any] = Field(None, alias="inputData")
    output_data: Optional[Any] = Field(None, alias="outputData")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class AIInsightCreate(AIInsightBase):
    pass


class AIInsight(AIInsightBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
        allow_population_by_field_name = True
        populate_by_name = True


class AIInsightResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: AIInsight


class AIInsightListResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    total: int
    data: list[AIInsight]
