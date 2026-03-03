# models/payslip.py
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db.base_class import Base


class Payslip(Base):
    __tablename__ = "payslips"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    pay_period_id = Column(Integer, ForeignKey("pay_periods.id"), nullable=False, index=True)
    gross_pay = Column(Float, nullable=False, default=0)
    overtime_pay = Column(Float, nullable=False, default=0)
    deductions = Column(Float, nullable=False, default=0)
    net_pay = Column(Float, nullable=False, default=0)
    status = Column(String, nullable=False, default="generated", index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    business_ref = relationship("Business")
    user_ref = relationship("User")
    pay_period_ref = relationship("PayPeriod")
