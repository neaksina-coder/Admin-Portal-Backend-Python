# models/product.py
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from db.base_class import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    sku = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True, index=True)  # Foreign Key
    price = Column(Float, nullable=False)
    cost = Column(Float, nullable=True)
    stock = Column(Integer, default=0)
    unit = Column(String, nullable=True)
    status = Column(String, default='active')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to category
    category = relationship("Category", back_populates="products")