# models/hr_hiring_position.py
from datetime import datetime, date

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db.base_class import Base


class HrHiringPosition(Base):
    __tablename__ = "hr_hiring_positions"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    department = Column(String, nullable=True, index=True)
    status = Column(String, nullable=False, default="open", index=True)
    priority = Column(String, nullable=True)
    opened_at = Column(Date, nullable=False)
    closed_at = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    business_ref = relationship("Business")
