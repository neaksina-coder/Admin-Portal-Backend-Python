# models/leave_transaction.py
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Float, String
from sqlalchemy.orm import relationship

from db.base_class import Base


class LeaveTransaction(Base):
    __tablename__ = "leave_transactions"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    leave_type_id = Column(Integer, ForeignKey("leave_types.id"), nullable=False, index=True)
    change = Column(Float, nullable=False, default=0)
    reason = Column(String, nullable=False)
    ref_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    business_ref = relationship("Business")
    user_ref = relationship("User")
    leave_type_ref = relationship("LeaveType")
