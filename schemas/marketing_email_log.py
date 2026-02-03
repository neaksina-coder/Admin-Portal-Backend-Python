# schemas/marketing_email_log.py
from pydantic import BaseModel, Field
from datetime import datetime


class MarketingEmailLog(BaseModel):
    id: int
    campaign_id: int = Field(..., alias="campaignId")
    business_id: int = Field(..., alias="businessId")
    recipient_email: str = Field(..., alias="recipientEmail")
    subject: str
    status: str
    error_message: str | None = Field(None, alias="errorMessage")
    sent_at: datetime = Field(..., alias="sentAt")

    class Config:
        from_attributes = True
        allow_population_by_field_name = True
        populate_by_name = True


class MarketingEmailLogListResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    total: int
    data: list[MarketingEmailLog]
