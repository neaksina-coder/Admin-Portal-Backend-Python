# schemas/audit_log.py
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class AuditLog(BaseModel):
    id: int
    business_id: Optional[int] = Field(None, alias="businessId")
    actor_user_id: Optional[int] = Field(None, alias="actorUserId")
    action: str
    target_type: Optional[str] = Field(None, alias="targetType")
    target_id: Optional[int] = Field(None, alias="targetId")
    metadata_json: Optional[Any] = Field(
        None,
        validation_alias="metadata",
        serialization_alias="metadata",
    )
    created_at: datetime

    class Config:
        from_attributes = True
        allow_population_by_field_name = True
        populate_by_name = True


class AuditLogListResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    total: int
    data: list[AuditLog]
