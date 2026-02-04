# crud/audit_log.py
from datetime import datetime
from typing import Any, Optional

from sqlalchemy.orm import Session

from models.audit_log import AuditLog


def create_audit_log(
    db: Session,
    *,
    action: str,
    actor_user_id: Optional[int] = None,
    business_id: Optional[int] = None,
    target_type: Optional[str] = None,
    target_id: Optional[int] = None,
    metadata_json: Optional[Any] = None,
) -> AuditLog:
    log = AuditLog(
        action=action,
        actor_user_id=actor_user_id,
        business_id=business_id,
        target_type=target_type,
        target_id=target_id,
        metadata_json=metadata_json,
    )
    db.add(log)
    return log


def list_audit_logs(
    db: Session,
    *,
    business_id: Optional[int] = None,
    actor_user_id: Optional[int] = None,
    action: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[AuditLog]:
    query = db.query(AuditLog)
    if business_id is not None:
        query = query.filter(AuditLog.business_id == business_id)
    if actor_user_id is not None:
        query = query.filter(AuditLog.actor_user_id == actor_user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)
    if end_date:
        query = query.filter(AuditLog.created_at <= end_date)
    return (
        query.order_by(AuditLog.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
