# models/category.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from db.base_class import Base

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    slug = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String, default='active')  # active, inactive
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to products
    products = relationship("Product", back_populates="category")