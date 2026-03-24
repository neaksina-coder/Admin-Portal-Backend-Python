# models/hr_performance_review.py
from datetime import datetime, date

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db.base_class import Base


class HrPerformanceReview(Base):
    __tablename__ = "hr_performance_reviews"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    review_period = Column(Date, nullable=False, index=True)
    score = Column(Float, nullable=False, default=0)
    goals_achieved = Column(Integer, nullable=False, default=0)
    rating = Column(Integer, nullable=False, default=0)
    trend = Column(String, nullable=False, default="flat")
    metric_quality = Column(Float, nullable=False, default=0)
    metric_speed = Column(Float, nullable=False, default=0)
    metric_collaboration = Column(Float, nullable=False, default=0)
    metric_initiative = Column(Float, nullable=False, default=0)
    metric_reliability = Column(Float, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    business_ref = relationship("Business")
    user_ref = relationship("User")
