# models/hr_hiring_pipeline.py
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from db.base_class import Base


class HrHiringPipeline(Base):
    __tablename__ = "hr_hiring_pipeline"
    __table_args__ = (
        UniqueConstraint("business_id", "stage", name="uq_hr_hiring_pipeline_business_stage"),
    )

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    stage = Column(String, nullable=False, index=True)
    applicants = Column(Integer, nullable=False, default=0)
    priority = Column(String, nullable=True)
    sort_order = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    business_ref = relationship("Business")
