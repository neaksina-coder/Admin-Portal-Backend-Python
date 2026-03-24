# models/hr_budget_plan.py
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from db.base_class import Base


class HrBudgetPlan(Base):
    __tablename__ = "hr_budget_plans"
    __table_args__ = (
        UniqueConstraint("business_id", "year", name="uq_hr_budget_plan_business_year"),
    )

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    annual_budget = Column(Float, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    business_ref = relationship("Business")
