# models/chat_message.py
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship

from db.base_class import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("chat_conversations.id"), nullable=False, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    sender_type = Column(String, nullable=False, index=True)
    sender_id = Column(Integer, nullable=True, index=True)
    content = Column(Text, nullable=False)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    conversation_ref = relationship("ChatConversation", back_populates="messages")
    business_ref = relationship("Business")
