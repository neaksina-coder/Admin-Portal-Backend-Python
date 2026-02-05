# utils/admin_digest.py
from __future__ import annotations

from datetime import datetime, timedelta
import json
import urllib.request

from sqlalchemy.orm import Session

from core.config import settings
from crud import admin_digest as crud_admin_digest
from db.session import SessionLocal
from models.audit_log import AuditLog
from models.business import Business
from models.invoice import Invoice
from models.subscription import Subscription


def _post_json(url: str, payload: dict, timeout: int = 30) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
    return json.loads(body)


def _build_payload(db: Session, start: datetime, end: datetime) -> dict:
    businesses = (
        db.query(Business)
        .filter(Business.created_at >= start, Business.created_at <= end)
        .order_by(Business.created_at.desc())
        .all()
    )

    overdue_invoices = (
        db.query(Invoice)
        .filter(
            Invoice.due_date.isnot(None),
            Invoice.due_date < end.date(),
            Invoice.payment_status != "paid",
        )
        .order_by(Invoice.due_date.asc())
        .all()
    )

    failed_invoices_count = (
        db.query(Invoice)
        .filter(Invoice.payment_status == "failed", Invoice.created_at >= start)
        .count()
    )

    pending_subscriptions = (
        db.query(Subscription)
        .filter(
            Subscription.status == "pending",
            Subscription.created_at <= end - timedelta(hours=48),
        )
        .order_by(Subscription.created_at.asc())
        .all()
    )

    audit_logs = (
        db.query(AuditLog)
        .filter(AuditLog.created_at >= start, AuditLog.created_at <= end)
        .order_by(AuditLog.created_at.desc())
        .all()
    )

    suspensions = sum(
        1 for log in audit_logs if "suspend" in (log.action or "").lower()
    )
    role_changes = sum(1 for log in audit_logs if "role" in (log.action or "").lower())

    payload = {
        "range": "daily",
        "windowStart": start.isoformat(),
        "windowEnd": end.isoformat(),
        "stats": {
            "newBusinesses": len(businesses),
            "overdueInvoices": len(overdue_invoices),
            "failedInvoices": failed_invoices_count,
            "subscriptionsPending": len(pending_subscriptions),
            "suspensions": suspensions,
            "roleChanges": role_changes,
        },
        "items": {
            "businesses": [
                {"id": b.id, "name": b.name, "createdAt": b.created_at.isoformat()}
                for b in businesses
            ],
            "invoices": [
                {
                    "id": i.id,
                    "businessId": i.business_id,
                    "amount": i.amount,
                    "status": i.payment_status,
                    "dueDate": i.due_date.isoformat() if i.due_date else None,
                }
                for i in overdue_invoices
            ],
            "subscriptions": [
                {
                    "id": s.id,
                    "businessId": s.business_id,
                    "status": s.status,
                    "createdAt": s.created_at.isoformat(),
                }
                for s in pending_subscriptions
            ],
            "auditLogs": [
                {
                    "id": a.id,
                    "action": a.action,
                    "actorUserId": a.actor_user_id,
                    "createdAt": a.created_at.isoformat(),
                }
                for a in audit_logs
            ],
        },
    }
    return payload


def generate_and_store_daily_digest() -> None:
    db = SessionLocal()
    try:
        end = datetime.utcnow()
        start = end - timedelta(days=1)

        payload = _build_payload(db, start, end)
        response = _post_json(settings.N8N_ADMIN_DIGEST_WEBHOOK_URL, payload)

        summary_text = response.get("summaryText", "")
        top_items = response.get("topItems", [])
        stats = payload.get("stats", {})

        crud_admin_digest.create_admin_digest(
            db,
            range_type="daily",
            summary_text=summary_text,
            top_items=top_items,
            stats=stats,
            generated_by="system",
        )
    except Exception as exc:
        print(f"[admin-digest] Failed to generate digest: {exc}")
    finally:
        db.close()
