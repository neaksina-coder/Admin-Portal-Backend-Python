# crud/invoice.py
from typing import List, Optional

from sqlalchemy.orm import Session

from crud.subscription_event import create_subscription_event
from models.ai_insight import AIInsight
from models.business import Business
from models.invoice import Invoice
from models.plan import Plan
from models.subscription import Subscription
from schemas.invoice import InvoiceCreate, InvoiceStatusUpdate


def get_invoice(db: Session, invoice_id: int) -> Optional[Invoice]:
    return db.query(Invoice).filter(Invoice.id == invoice_id).first()


def list_invoices(
    db: Session,
    *,
    business_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Invoice]:
    query = db.query(Invoice)
    if business_id is not None:
        query = query.filter(Invoice.business_id == business_id)
    return query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()


def create_invoice(db: Session, invoice_in: InvoiceCreate) -> Invoice:
    db_invoice = Invoice(**invoice_in.dict(by_alias=False))
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice


def _activate_subscription_for_paid_invoice(db: Session, db_invoice: Invoice) -> None:
    if not db_invoice.subscription_id:
        return

    sub = (
        db.query(Subscription)
        .filter(Subscription.id == db_invoice.subscription_id)
        .first()
    )
    if not sub:
        return

    # Keep only one active subscription per business.
    db.query(Subscription).filter(
        Subscription.business_id == sub.business_id,
        Subscription.id != sub.id,
        Subscription.status == "active",
    ).update({"status": "inactive"})

    sub.status = "active"

    business = db.query(Business).filter(Business.id == sub.business_id).first()
    previous_plan_id = business.plan_id if business else None
    if business:
        business.plan_id = sub.plan_id

    create_subscription_event(
        db,
        subscription_id=sub.id,
        business_id=sub.business_id,
        invoice_id=db_invoice.id,
        event_type="subscription_activated",
        payload={
            "reason": "invoice_paid",
            "planId": sub.plan_id,
            "previousPlanId": previous_plan_id,
        },
    )

    plan = db.query(Plan).filter(Plan.id == sub.plan_id).first()
    if plan and isinstance(plan.features, dict) and plan.features.get("aiInsight"):
        db.add(
            AIInsight(
                business_id=sub.business_id,
                type="insight",
                input_data={"source": "invoice_paid", "planId": sub.plan_id},
                output_data={"summary": "AI insights enabled for this plan."},
            )
        )


def update_invoice_status(
    db: Session,
    invoice_id: int,
    payload: InvoiceStatusUpdate,
) -> Optional[Invoice]:
    db_invoice = get_invoice(db, invoice_id)
    if not db_invoice:
        return None

    previous_status = (db_invoice.payment_status or "").lower()

    update_data = payload.dict(exclude_unset=True, by_alias=False)
    for key, value in update_data.items():
        setattr(db_invoice, key, value)

    new_status = (db_invoice.payment_status or "").lower()

    if db_invoice.subscription_id:
        create_subscription_event(
            db,
            subscription_id=db_invoice.subscription_id,
            business_id=db_invoice.business_id,
            invoice_id=db_invoice.id,
            event_type="invoice_status_changed",
            payload={
                "previousStatus": previous_status,
                "newStatus": new_status,
                "paymentDate": db_invoice.payment_date.isoformat() if db_invoice.payment_date else None,
                "paymentMethod": db_invoice.payment_method,
            },
        )

    if previous_status != "paid" and new_status == "paid":
        _activate_subscription_for_paid_invoice(db, db_invoice)

    db.commit()
    db.refresh(db_invoice)
    return db_invoice
