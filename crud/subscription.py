# crud/subscription.py
from datetime import date, timedelta
from typing import Optional, List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from crud.subscription_event import create_subscription_event
from models.subscription import Subscription
from models.business import Business
from models.plan import Plan
from models.invoice import Invoice
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

    # Professional billing flow: subscription is always pending until invoice is paid.
    db_sub = Subscription(
        business_id=sub_in.business_id,
        plan_id=sub_in.plan_id,
        start_date=sub_in.start_date,
        end_date=sub_in.end_date,
        status="pending",
        billing_history=sub_in.billing_history,
    )

    db.add(db_sub)
    db.flush()  # Get subscription id before creating linked invoice.

    create_subscription_event(
        db,
        subscription_id=db_sub.id,
        business_id=db_sub.business_id,
        event_type="subscription_created",
        payload={
            "requestedStatus": sub_in.status,
            "effectiveStatus": "pending",
            "planId": db_sub.plan_id,
        },
    )

    db_invoice = Invoice(
        business_id=sub_in.business_id,
        subscription_id=db_sub.id,
        amount=float(plan.price or 0),
        currency="USD",
        payment_status="pending",
        due_date=date.today() + timedelta(days=7),
        metadata_json={
            "source": "subscription_create",
            "planId": sub_in.plan_id,
            "subscriptionId": db_sub.id,
        },
    )
    db.add(db_invoice)
    db.flush()

    create_subscription_event(
        db,
        subscription_id=db_sub.id,
        business_id=db_sub.business_id,
        invoice_id=db_invoice.id,
        event_type="invoice_created",
        payload={
            "amount": db_invoice.amount,
            "currency": db_invoice.currency,
            "paymentStatus": db_invoice.payment_status,
            "dueDate": db_invoice.due_date.isoformat() if db_invoice.due_date else None,
        },
    )

    db.commit()
    db.refresh(db_sub)
    return db_sub
