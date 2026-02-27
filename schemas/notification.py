# schemas/notification.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class NotificationBase(BaseModel):
    business_id: int = Field(..., alias="businessId")
    type: str
    title: str
    body: Optional[str] = None
    icon_url: Optional[str] = Field(None, alias="iconUrl")
    link_url: Optional[str] = Field(None, alias="linkUrl")
    is_read: bool = Field(False, alias="isRead")
    created_at: Optional[datetime] = Field(None, alias="createdAt")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class NotificationCreate(BaseModel):
    business_id: int = Field(..., alias="businessId")
    type: str
    title: str
    body: Optional[str] = None
    icon_url: Optional[str] = Field(None, alias="iconUrl")
    link_url: Optional[str] = Field(None, alias="linkUrl")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class Notification(NotificationBase):
    id: int

    class Config:
        from_attributes = True
        allow_population_by_field_name = True
        populate_by_name = True


class NotificationListResponse(BaseModel):
    success: bool
    status_code: int = Field(..., alias="status_code")
    message: str
    total: int
    data: list[Notification]

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class NotificationResponse(BaseModel):
    success: bool
    status_code: int = Field(..., alias="status_code")
    message: str
    data: Notification

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class NotificationUnreadCountResponse(BaseModel):
    success: bool
    status_code: int = Field(..., alias="status_code")
    message: str
    count: int

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
