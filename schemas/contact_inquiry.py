# schemas/contact_inquiry.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class ContactInquiryBase(BaseModel):
    business_id: int = Field(..., alias="businessId")
    name: str
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    service_interest: Optional[str] = Field(None, alias="serviceInterest")
    subject: Optional[str] = None
    message: str
    source: Optional[str] = "public_web"

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class ContactInquiryPublicCreate(ContactInquiryBase):
    pass


class ContactInquiryUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to_user_id: Optional[int] = Field(None, alias="assignedToUserId")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class ContactInquiryReplyRequest(BaseModel):
    subject: Optional[str] = None
    body: str


class ContactInquiry(ContactInquiryBase):
    id: int
    status: str
    assigned_to_user_id: Optional[int] = Field(None, alias="assignedToUserId")
    created_at: datetime
    updated_at: datetime
    replied_at: Optional[datetime] = Field(None, alias="repliedAt")

    class Config:
        from_attributes = True
        allow_population_by_field_name = True
        populate_by_name = True


class ContactInquiryResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: ContactInquiry


class ContactInquiryListResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    total: int
    data: list[ContactInquiry]
