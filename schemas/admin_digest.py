# schemas/admin_digest.py
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AdminDigestOut(BaseModel):
    range_type: str = Field(..., alias="range")
    summary_text: str = Field(..., alias="summaryText")
    top_items: list[dict[str, Any]] = Field(..., alias="topItems")
    stats: dict[str, Any]
    generated_at: datetime = Field(..., alias="generatedAt")

    class Config:
        from_attributes = True
        allow_population_by_field_name = True
        populate_by_name = True


class AdminDigestResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: AdminDigestOut | None
