# models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from db.base_class import Base  # ← Change this from db.base to db.base_class

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    privacy_policy_accepted = Column(Boolean, default=False, nullable=False)
    role = Column(String, default='user', nullable=False)   