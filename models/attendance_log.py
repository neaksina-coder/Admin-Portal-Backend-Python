# models/attendance_log.py
from datetime import datetime, date

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db.base_class import Base


class AttendanceLog(Base):
    __tablename__ = "attendance_logs"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    work_date = Column(Date, nullable=False, index=True)
    check_in_at = Column(DateTime, nullable=False)
    check_out_at = Column(DateTime, nullable=True)
    status = Column(String, nullable=False, default="present", index=True)
    note = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    business_ref = relationship("Business")
    user_ref = relationship("User")
