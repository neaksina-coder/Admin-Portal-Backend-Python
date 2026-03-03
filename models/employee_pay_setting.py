# models/employee_pay_setting.py
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db.base_class import Base


class EmployeePaySetting(Base):
    __tablename__ = "employee_pay_settings"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    pay_type = Column(String, nullable=False, default="monthly")
    monthly_salary = Column(Float, nullable=True)
    hourly_rate = Column(Float, nullable=True)
    overtime_rate = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    business_ref = relationship("Business")
    user_ref = relationship("User")
