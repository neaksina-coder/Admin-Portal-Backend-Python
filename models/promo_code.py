# models/promo_code.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float
from datetime import datetime
from db.base_class import Base


class PromoCode(Base):
    __tablename__ = "promo_codes"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    code = Column(String, nullable=False, index=True)
    discount_type = Column(String, nullable=False)  # percent | fixed
    discount_value = Column(Float, nullable=False)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    usage_limit = Column(Integer, nullable=True)
    used_count = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
