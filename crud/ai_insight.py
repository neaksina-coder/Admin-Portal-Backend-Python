# crud/ai_insight.py
from sqlalchemy.orm import Session
from typing import Optional, List

from models.ai_insight import AIInsight
from schemas.ai_insight import AIInsightCreate


def get_ai_insight(db: Session, insight_id: int) -> Optional[AIInsight]:
    return db.query(AIInsight).filter(AIInsight.id == insight_id).first()


def list_ai_insights(
    db: Session,
    *,
    business_id: int,
    limit: int = 20,
    type: Optional[str] = None,
) -> List[AIInsight]:
    query = db.query(AIInsight).filter(AIInsight.business_id == business_id)
    if type:
        query = query.filter(AIInsight.type == type)
    return query.order_by(AIInsight.created_at.desc()).limit(limit).all()


def create_ai_insight(db: Session, insight_in: AIInsightCreate) -> AIInsight:
    db_insight = AIInsight(
        business_id=insight_in.business_id,
        type=insight_in.type,
        input_data=insight_in.input_data,
        output_data=insight_in.output_data,
    )
    db.add(db_insight)
    db.commit()
    db.refresh(db_insight)
    return db_insight
