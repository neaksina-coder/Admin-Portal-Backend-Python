# crud/subscription.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional, List

from models.subscription import Subscription
from models.business import Business
from models.plan import Plan
from models.ai_insight import AIInsight
from schemas.subscription import SubscriptionCreate


def get_subscription(db: Session, subscription_id: int) -> Optional[Subscription]:
    return db.query(Subscription).filter(Subscription.id == subscription_id).first()


def list_subscriptions(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    business_id: Optional[int] = None,
) -> List[Subscription]:
    query = db.query(Subscription)
    if business_id:
        query = query.filter(Subscription.business_id == business_id)
    return query.offset(skip).limit(limit).all()


def create_subscription(db: Session, sub_in: SubscriptionCreate) -> Subscription:
    business = db.query(Business).filter(Business.id == sub_in.business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    plan = db.query(Plan).filter(Plan.id == sub_in.plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    db_sub = Subscription(
        business_id=sub_in.business_id,
        plan_id=sub_in.plan_id,
        start_date=sub_in.start_date,
        end_date=sub_in.end_date,
        status=sub_in.status,
        billing_history=sub_in.billing_history,
    )
    if sub_in.status == "active":
        # Ensure only one active subscription per business.
        db.query(Subscription).filter(
            Subscription.business_id == sub_in.business_id,
            Subscription.status == "active",
        ).update({"status": "inactive"})
        db.query(Business).filter(Business.id == sub_in.business_id).update(
            {"plan_id": sub_in.plan_id}
        )
        if isinstance(plan.features, dict) and plan.features.get("aiInsight"):
            db.add(
                AIInsight(
                    business_id=sub_in.business_id,
                    type="insight",
                    input_data={"source": "subscription", "planId": sub_in.plan_id},
                    output_data={"summary": "AI insights enabled for this plan."},
                )
            )
    db.add(db_sub)
    db.commit()
    db.refresh(db_sub)
    return db_sub
