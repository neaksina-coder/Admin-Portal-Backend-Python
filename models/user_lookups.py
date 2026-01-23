# models/user_lookups.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from db.base_class import Base


class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(String, unique=True, nullable=False, index=True)
    label = Column(String, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    users = relationship("User", back_populates="role_ref")


class UserPlan(Base):
    __tablename__ = "user_plans"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(String, unique=True, nullable=False, index=True)
    label = Column(String, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    users = relationship("User", back_populates="plan_ref")


class UserStatus(Base):
    __tablename__ = "user_statuses"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(String, unique=True, nullable=False, index=True)
    label = Column(String, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    users = relationship("User", back_populates="status_ref")


class UserBilling(Base):
    __tablename__ = "user_billings"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(String, unique=True, nullable=False, index=True)
    label = Column(String, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    users = relationship("User", back_populates="billing_ref")
