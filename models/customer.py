# models/customer.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from db.base_class import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    email = Column(String, nullable=True, index=True)
    phone = Column(String, nullable=True, index=True)
    segment = Column(String, nullable=True, index=True)
    notes = Column(Text, nullable=True)
    churn_risk_score = Column(Float, nullable=True)
    lifetime_value = Column(Float, nullable=True)
    next_best_product = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)

    business_ref = relationship("Business", back_populates="customers")
    contacts = relationship("CustomerContact", back_populates="customer_ref")
