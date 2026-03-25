# models/product.py
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from db.base_class import Base


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("business_id", "sku", name="uq_products_business_sku"),
    )

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    sku = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    price = Column(Float, nullable=False)
    cost = Column(Float, nullable=True)
    stock = Column(Integer, nullable=False, default=0)
    unit = Column(String, nullable=True)
    status = Column(String, nullable=False, default="active")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)

    category = relationship("Category", back_populates="products")
    business_ref = relationship("Business", backref="products")
