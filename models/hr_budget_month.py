# models/hr_budget_month.py
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from db.base_class import Base


class HrBudgetMonth(Base):
    __tablename__ = "hr_budget_months"
    __table_args__ = (
        UniqueConstraint("business_id", "year", "month", name="uq_hr_budget_month_business_year_month"),
    )

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    month = Column(Integer, nullable=False, index=True)
    budget = Column(Float, nullable=False, default=0)
    actual = Column(Float, nullable=False, default=0)
    forecast = Column(Float, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    business_ref = relationship("Business")
