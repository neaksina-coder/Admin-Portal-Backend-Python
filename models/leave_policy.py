# models/leave_policy.py
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint, Float
from sqlalchemy.orm import relationship

from db.base_class import Base


class LeavePolicy(Base):
    __tablename__ = "leave_policies"
    __table_args__ = (
        UniqueConstraint("business_id", "leave_type_id", name="uq_leave_policies_business_type"),
    )

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    leave_type_id = Column(Integer, ForeignKey("leave_types.id"), nullable=False, index=True)
    annual_allowance = Column(Float, nullable=False, default=0)
    accrual_method = Column(String, nullable=False, default="monthly")
    carryover_days = Column(Float, nullable=True)
    max_balance = Column(Float, nullable=True)
    allow_negative = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    business_ref = relationship("Business")
    leave_type_ref = relationship("LeaveType")
