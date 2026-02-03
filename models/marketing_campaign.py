# models/marketing_campaign.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from db.base_class import Base


class MarketingCampaign(Base):
    __tablename__ = "marketing_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    target_segment = Column(String, nullable=True)
    channel = Column(String, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    performance_metrics = Column(JSONB, nullable=True)
    best_time_to_send = Column(String, nullable=True)
    content_suggestions = Column(JSONB, nullable=True)
    ab_variants = Column(JSONB, nullable=True)
    ab_metrics = Column(JSONB, nullable=True)
    ab_winner = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
