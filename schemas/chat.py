# schemas/chat.py
from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field, EmailStr


class ChatVisitorBase(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    source_url: Optional[str] = Field(None, alias="sourceUrl")
    referrer: Optional[str] = None
    utm_source: Optional[str] = Field(None, alias="utmSource")
    utm_medium: Optional[str] = Field(None, alias="utmMedium")
    utm_campaign: Optional[str] = Field(None, alias="utmCampaign")
    ip: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    device: Optional[str] = None
    last_page: Optional[str] = Field(None, alias="lastPage")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class ChatVisitor(ChatVisitorBase):
    id: int
    business_id: int = Field(..., alias="businessId")
    first_seen_at: datetime = Field(..., alias="firstSeenAt")
    last_seen_at: datetime = Field(..., alias="lastSeenAt")
    message_count: int = Field(..., alias="messageCount")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    class Config:
        from_attributes = True
        allow_population_by_field_name = True
        populate_by_name = True


class ChatConversationBase(BaseModel):
    business_id: int = Field(..., alias="businessId")
    visitor_id: int = Field(..., alias="visitorId")
    status: str
    assigned_admin_id: Optional[int] = Field(None, alias="assignedAdminId")
    ai_enabled: bool = Field(..., alias="aiEnabled")
    ai_paused: bool = Field(..., alias="aiPaused")
    ai_handoff_at: Optional[datetime] = Field(None, alias="aiHandoffAt")
    last_message_at: Optional[datetime] = Field(None, alias="lastMessageAt")
    last_read_at: Optional[datetime] = Field(None, alias="lastReadAt")
    unread_count: int = Field(..., alias="unreadCount")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class ChatConversationCreate(BaseModel):
    business_id: int = Field(..., alias="businessId")
    visitor_id: Optional[int] = Field(None, alias="visitorId")
    visitor: Optional[ChatVisitorBase] = None
    status: Optional[str] = None
    assigned_admin_id: Optional[int] = Field(None, alias="assignedAdminId")
    ai_enabled: Optional[bool] = Field(True, alias="aiEnabled")
    ai_paused: Optional[bool] = Field(False, alias="aiPaused")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class ChatConversationUpdate(BaseModel):
    status: Optional[str] = None
    assigned_admin_id: Optional[int] = Field(None, alias="assignedAdminId")
    ai_enabled: Optional[bool] = Field(None, alias="aiEnabled")
    ai_paused: Optional[bool] = Field(None, alias="aiPaused")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class ChatConversation(ChatConversationBase):
    id: int
    visitor_ref: Optional[ChatVisitorBase] = Field(None, alias="visitor")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    class Config:
        from_attributes = True
        allow_population_by_field_name = True
        populate_by_name = True


class ChatMessageBase(BaseModel):
    sender_type: Literal["visitor", "admin", "ai"] = Field(..., alias="senderType")
    sender_id: Optional[int] = Field(None, alias="senderId")
    content: str
    confidence: Optional[float] = None

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessage(ChatMessageBase):
    id: int
    conversation_id: int = Field(..., alias="conversationId")
    business_id: int = Field(..., alias="businessId")
    created_at: datetime = Field(..., alias="createdAt")

    class Config:
        from_attributes = True
        allow_population_by_field_name = True
        populate_by_name = True


class ChatConversationResponse(BaseModel):
    success: bool
    status_code: int = Field(..., alias="status_code")
    message: str
    data: ChatConversation

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class ChatConversationListResponse(BaseModel):
    success: bool
    status_code: int = Field(..., alias="status_code")
    message: str
    total: int
    data: list[ChatConversation]

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class ChatMessageResponse(BaseModel):
    success: bool
    status_code: int = Field(..., alias="status_code")
    message: str
    data: ChatMessage

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class ChatMessageListResponse(BaseModel):
    success: bool
    status_code: int = Field(..., alias="status_code")
    message: str
    total: int
    data: list[ChatMessage]

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
