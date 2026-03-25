# models/category.py
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from db.base_class import Base


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint("business_id", "slug", name="uq_categories_business_slug"),
    )

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    slug = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="active")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)

    products = relationship("Product", back_populates="category")
    business_ref = relationship("Business", backref="categories")
