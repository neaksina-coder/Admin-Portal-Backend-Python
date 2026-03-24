# models/employee_leave_balance.py
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Float, UniqueConstraint
from sqlalchemy.orm import relationship

from db.base_class import Base


class EmployeeLeaveBalance(Base):
    __tablename__ = "employee_leave_balances"
    __table_args__ = (
        UniqueConstraint("user_id", "leave_type_id", name="uq_employee_leave_balance_user_type"),
    )

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    leave_type_id = Column(Integer, ForeignKey("leave_types.id"), nullable=False, index=True)
    balance = Column(Float, nullable=False, default=0)
    used = Column(Float, nullable=False, default=0)
    pending = Column(Float, nullable=False, default=0)
    last_accrual_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    business_ref = relationship("Business")
    user_ref = relationship("User")
    leave_type_ref = relationship("LeaveType")
