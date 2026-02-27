# crud/notification.py
from typing import List, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from models.notification import Notification
from schemas.notification import NotificationCreate


def create_notification(db: Session, payload: NotificationCreate) -> Notification:
    notification = Notification(
        business_id=payload.business_id,
        type=payload.type,
        title=payload.title,
        body=payload.body,
        icon_url=payload.icon_url,
        link_url=payload.link_url,
        is_read=False,
        created_at=datetime.utcnow(),
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def list_notifications(
    db: Session,
    *,
    business_id: int,
    skip: int = 0,
    limit: int = 10,
    unread_only: bool = False,
) -> List[Notification]:
    query = db.query(Notification).filter(Notification.business_id == business_id)
    if unread_only:
        query = query.filter(Notification.is_read == False)
    return (
        query.order_by(Notification.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def unread_count(db: Session, *, business_id: int) -> int:
    return (
        db.query(Notification)
        .filter(Notification.business_id == business_id, Notification.is_read == False)
        .count()
    )


def get_notification(db: Session, notification_id: int) -> Optional[Notification]:
    return db.query(Notification).filter(Notification.id == notification_id).first()


def mark_read(db: Session, notification_id: int) -> Optional[Notification]:
    notification = get_notification(db, notification_id)
    if not notification:
        return None
    notification.is_read = True
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def mark_all_read(db: Session, *, business_id: int) -> int:
    updated = (
        db.query(Notification)
        .filter(Notification.business_id == business_id, Notification.is_read == False)
        .update({"is_read": True})
    )
    db.commit()
    return int(updated or 0)


def delete_notification(db: Session, notification_id: int) -> Optional[Notification]:
    notification = get_notification(db, notification_id)
    if not notification:
        return None
    db.delete(notification)
    db.commit()
    return notification
