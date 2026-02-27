# api/v1/notifications.py
import json
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from api import deps
from core.config import settings
from crud import notification as crud_notification
from crud import user as crud_user
from db.session import SessionLocal
from schemas.notification import (
    NotificationCreate,
    NotificationListResponse,
    NotificationResponse,
    NotificationUnreadCountResponse,
)
from schemas.user import TokenData


router = APIRouter()


class NotificationManager:
    def __init__(self) -> None:
        self.active: Dict[int, List[WebSocket]] = {}

    async def connect(self, business_id: int, ws: WebSocket) -> None:
        await ws.accept()
        self.active.setdefault(business_id, []).append(ws)

    def disconnect(self, business_id: int, ws: WebSocket) -> None:
        connections = self.active.get(business_id, [])
        if ws in connections:
            connections.remove(ws)
        if not connections and business_id in self.active:
            del self.active[business_id]

    async def broadcast(self, business_id: int, data: dict) -> None:
        for ws in list(self.active.get(business_id, [])):
            await ws.send_text(json.dumps(data))


manager = NotificationManager()


def _validate_ws_admin(token: str, db: Session):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = TokenData(email=payload.get("sub"))
    except (JWTError, ValidationError):
        return None
    user = crud_user.get_user_by_email(db, email=token_data.email)
    if not user:
        return None
    if not (user.is_superuser or (user.role or "").lower() == "admin"):
        return None
    return user


@router.websocket("/ws")
async def notifications_ws(websocket: WebSocket, businessId: int, token: str | None = None):
    db = SessionLocal()
    user = None
    if token:
        user = _validate_ws_admin(token, db)
    if not user:
        await websocket.close(code=1008)
        db.close()
        return

    await manager.connect(businessId, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(businessId, websocket)
    finally:
        db.close()


@router.get("", response_model=NotificationListResponse)
def list_notifications(
    businessId: int = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    unreadOnly: bool = Query(False),
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    notifications = crud_notification.list_notifications(
        db,
        business_id=businessId,
        skip=skip,
        limit=limit,
        unread_only=unreadOnly,
    )
    return {
        "success": True,
        "status_code": 200,
        "message": "Notifications retrieved successfully",
        "total": len(notifications),
        "data": notifications,
    }


@router.get("/unread-count", response_model=NotificationUnreadCountResponse)
def unread_count(
    businessId: int = Query(...),
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    count = crud_notification.unread_count(db, business_id=businessId)
    return {
        "success": True,
        "status_code": 200,
        "message": "Unread count retrieved successfully",
        "count": count,
    }


@router.post("", response_model=NotificationResponse, status_code=201)
async def create_notification(
    payload: NotificationCreate,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    notification = crud_notification.create_notification(db, payload)
    await manager.broadcast(
        notification.business_id,
        {
            "success": True,
            "status_code": 201,
            "message": "Notification created successfully",
            "data": {
                "id": notification.id,
                "businessId": notification.business_id,
                "type": notification.type,
                "title": notification.title,
                "body": notification.body,
                "iconUrl": notification.icon_url,
                "linkUrl": notification.link_url,
                "isRead": notification.is_read,
                "createdAt": notification.created_at.isoformat(),
            },
        },
    )
    return {
        "success": True,
        "status_code": 201,
        "message": "Notification created successfully",
        "data": notification,
    }


@router.post("/{notification_id}/read", response_model=NotificationResponse)
def mark_read(
    notification_id: int,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    notification = crud_notification.mark_read(db, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {
        "success": True,
        "status_code": 200,
        "message": "Notification marked as read",
        "data": notification,
    }


@router.post("/read-all")
def mark_all_read(
    businessId: int = Query(...),
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    updated = crud_notification.mark_all_read(db, business_id=businessId)
    return {
        "success": True,
        "message": "Notifications marked as read",
        "updated": updated,
    }


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    notification = crud_notification.delete_notification(db, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"success": True, "message": "Notification deleted successfully"}
