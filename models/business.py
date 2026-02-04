# models/business.py
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from db.base_class import Base


class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    tenant_id = Column(String, unique=True, nullable=False, index=True)
    plan_id = Column(Integer, nullable=True, index=True)
    status = Column(String, default="active", nullable=False)
    suspended_at = Column(DateTime, nullable=True)
    suspended_reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)

    users = relationship("User", back_populates="business_ref")
    subscriptions = relationship("Subscription", back_populates="business_ref")
    customers = relationship("Customer", back_populates="business_ref")
    ai_insights = relationship("AIInsight", back_populates="business_ref")
