# models/sale.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from db.base_class import Base


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    total_price = Column(Float, nullable=False)
    original_amount = Column(Float, nullable=True)
    discount_amount = Column(Float, nullable=True)
    promo_code_id = Column(Integer, ForeignKey("promo_codes.id"), nullable=True, index=True)
    transaction_date = Column(DateTime, nullable=False)
    invoice_number = Column(String, nullable=True, index=True)
    demand_prediction = Column(Float, nullable=True)
    anomaly_flag = Column(Boolean, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    business_ref = relationship("Business", backref="sales")
