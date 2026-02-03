# schemas/marketing_campaign.py
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class MarketingCampaignBase(BaseModel):
    business_id: int = Field(..., alias="businessId")
    name: str
    target_segment: Optional[str] = Field(None, alias="targetSegment")
    channel: Optional[str] = None
    start_date: datetime = Field(..., alias="startDate")
    end_date: Optional[datetime] = Field(None, alias="endDate")
    performance_metrics: Optional[Any] = Field(None, alias="performanceMetrics")
    best_time_to_send: Optional[str] = Field(None, alias="bestTimeToSend")
    content_suggestions: Optional[Any] = Field(None, alias="contentSuggestions")
    ab_variants: Optional[Any] = Field(None, alias="abVariants")
    ab_metrics: Optional[Any] = Field(None, alias="abMetrics")
    ab_winner: Optional[str] = Field(None, alias="abWinner")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class MarketingCampaignCreate(MarketingCampaignBase):
    pass


class MarketingCampaignUpdate(BaseModel):
    name: Optional[str] = None
    target_segment: Optional[str] = Field(None, alias="targetSegment")
    channel: Optional[str] = None
    start_date: Optional[datetime] = Field(None, alias="startDate")
    end_date: Optional[datetime] = Field(None, alias="endDate")
    performance_metrics: Optional[Any] = Field(None, alias="performanceMetrics")
    best_time_to_send: Optional[str] = Field(None, alias="bestTimeToSend")
    content_suggestions: Optional[Any] = Field(None, alias="contentSuggestions")
    ab_variants: Optional[Any] = Field(None, alias="abVariants")
    ab_metrics: Optional[Any] = Field(None, alias="abMetrics")
    ab_winner: Optional[str] = Field(None, alias="abWinner")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class MarketingCampaign(MarketingCampaignBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
        allow_population_by_field_name = True
        populate_by_name = True


class MarketingCampaignResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: MarketingCampaign


class MarketingCampaignListResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    total: int
    data: list[MarketingCampaign]


class MarketingCampaignSendRequest(BaseModel):
    subject: str
    body: str
    html: Optional[str] = None
    segment: Optional[str] = None
    dry_run: bool = Field(False, alias="dryRun")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
