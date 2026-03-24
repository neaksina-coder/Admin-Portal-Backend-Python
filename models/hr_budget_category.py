# models/hr_budget_category.py
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db.base_class import Base


class HrBudgetCategory(Base):
    __tablename__ = "hr_budget_categories"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    allocated = Column(Float, nullable=False, default=0)
    spent = Column(Float, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    business_ref = relationship("Business")
