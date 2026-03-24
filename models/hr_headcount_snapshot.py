# models/hr_headcount_snapshot.py
from datetime import datetime, date

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from db.base_class import Base


class HrHeadcountSnapshot(Base):
    __tablename__ = "hr_headcount_snapshots"
    __table_args__ = (
        UniqueConstraint("business_id", "snapshot_month", name="uq_hr_headcount_business_month"),
    )

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    snapshot_month = Column(Date, nullable=False, index=True)
    headcount = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    business_ref = relationship("Business")
