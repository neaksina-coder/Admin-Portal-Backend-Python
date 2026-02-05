# models/admin_digest.py
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB

from db.base_class import Base


class AdminDigest(Base):
    __tablename__ = "admin_digests"

    id = Column(Integer, primary_key=True, index=True)
    range_type = Column(String, nullable=False, index=True)
    summary_text = Column(Text, nullable=False)
    top_items = Column(JSONB, nullable=False)
    stats = Column(JSONB, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    generated_by = Column(String, nullable=False, default="system")
