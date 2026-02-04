# crud/subscription_event.py
from typing import Any, Optional

from sqlalchemy.orm import Session

from models.subscription_event import SubscriptionEvent


def create_subscription_event(
    db: Session,
    *,
    subscription_id: int,
    business_id: int,
    event_type: str,
    payload: Optional[Any] = None,
    invoice_id: Optional[int] = None,
    actor_user_id: Optional[int] = None,
) -> SubscriptionEvent:
    event = SubscriptionEvent(
        subscription_id=subscription_id,
        business_id=business_id,
        invoice_id=invoice_id,
        actor_user_id=actor_user_id,
        event_type=event_type,
        payload=payload,
    )
    db.add(event)
    return event


def list_subscription_events(
    db: Session,
    *,
    subscription_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[SubscriptionEvent]:
    return (
        db.query(SubscriptionEvent)
        .filter(SubscriptionEvent.subscription_id == subscription_id)
        .order_by(SubscriptionEvent.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
