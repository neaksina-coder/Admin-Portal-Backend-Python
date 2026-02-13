# models/chat_conversation.py
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from db.base_class import Base


class ChatConversation(Base):
    __tablename__ = "chat_conversations"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    visitor_id = Column(Integer, ForeignKey("chat_visitors.id"), nullable=False, index=True)
    status = Column(String, default="Open", nullable=False, index=True)
    assigned_admin_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    ai_enabled = Column(Boolean, default=True, nullable=False)
    ai_paused = Column(Boolean, default=False, nullable=False)
    ai_handoff_at = Column(DateTime, nullable=True)
    last_message_at = Column(DateTime, nullable=True)
    last_read_at = Column(DateTime, nullable=True)
    unread_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)

    business_ref = relationship("Business", back_populates="chat_conversations")
    visitor_ref = relationship("ChatVisitor", back_populates="conversations")
    assigned_admin_ref = relationship("User")
    messages = relationship("ChatMessage", back_populates="conversation_ref")
