# models/marketing_email_log.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from db.base_class import Base


class MarketingEmailLog(Base):
    __tablename__ = "marketing_email_logs"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("marketing_campaigns.id"), nullable=False, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    recipient_email = Column(String, nullable=False, index=True)
    subject = Column(String, nullable=False)
    status = Column(String, nullable=False)  # sent / failed
    error_message = Column(String, nullable=True)
    sent_at = Column(DateTime, default=datetime.utcnow, nullable=False)
