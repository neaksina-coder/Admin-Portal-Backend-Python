# models/chat_visitor.py
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from db.base_class import Base


class ChatVisitor(Base):
    __tablename__ = "chat_visitors"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    name = Column(String, nullable=True, index=True)
    email = Column(String, nullable=True, index=True)
    phone = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    referrer = Column(String, nullable=True)
    utm_source = Column(String, nullable=True)
    utm_medium = Column(String, nullable=True)
    utm_campaign = Column(String, nullable=True)
    ip = Column(String, nullable=True)
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)
    timezone = Column(String, nullable=True)
    language = Column(String, nullable=True)
    browser = Column(String, nullable=True)
    os = Column(String, nullable=True)
    device = Column(String, nullable=True)
    last_page = Column(String, nullable=True)
    first_seen_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    message_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)

    business_ref = relationship("Business", back_populates="chat_visitors")
    conversations = relationship("ChatConversation", back_populates="visitor_ref")
