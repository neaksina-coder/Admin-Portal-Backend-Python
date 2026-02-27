# api/v1/chat.py
import json
import os
import shutil
import uuid
from datetime import datetime, timedelta
from typing import Dict, List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
    UploadFile,
    File,
    Form,
    Request,
)
from sqlalchemy.orm import Session

from api import deps
from crud import chat as crud_chat
from crud import notification as crud_notification
from models.chat_conversation import ChatConversation
from models.chat_message import ChatMessage
from core.config import settings
from db.session import SessionLocal
from schemas.chat import (
    ChatConversationCreate,
    ChatConversationUpdate,
    ChatConversationResponse,
    ChatConversationListResponse,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatMessageListResponse,
    ChatModeResponse,
    ChatModeAction,
)
from schemas.notification import NotificationCreate
from api.v1.notifications import manager as notification_manager
from utils.dify import call_dify_chat, call_dify_chat_async

router = APIRouter()


class ConnectionManager:
    def __init__(self) -> None:
        self.active: Dict[int, List[WebSocket]] = {}

    async def connect(self, conversation_id: int, ws: WebSocket) -> None:
        await ws.accept()
        self.active.setdefault(conversation_id, []).append(ws)

    def disconnect(self, conversation_id: int, ws: WebSocket) -> None:
        connections = self.active.get(conversation_id, [])
        if ws in connections:
            connections.remove(ws)
        if not connections and conversation_id in self.active:
            del self.active[conversation_id]

    async def broadcast(self, conversation_id: int, data: dict) -> None:
        for ws in list(self.active.get(conversation_id, [])):
            await ws.send_text(json.dumps(data))


manager = ConnectionManager()


def _save_chat_avatar(upload: UploadFile) -> str:
    upload_dir = os.path.join("uploads", "chat_avatars")
    os.makedirs(upload_dir, exist_ok=True)
    _, ext = os.path.splitext(upload.filename or "")
    filename = f"{uuid.uuid4().hex}{ext.lower()}"
    file_path = os.path.join(upload_dir, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload.file, buffer)
    return f"/uploads/chat_avatars/{filename}"


def _save_chat_image(upload: UploadFile) -> str:
    upload_dir = os.path.join("uploads", "chat_images")
    os.makedirs(upload_dir, exist_ok=True)
    _, ext = os.path.splitext(upload.filename or "")
    ext = ext.lower()
    allowed_exts = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}
    content_type = (upload.content_type or "").lower()
    if not content_type.startswith("image/") and ext not in allowed_exts:
        raise HTTPException(status_code=400, detail="Only image uploads are allowed")
    filename = f"{uuid.uuid4().hex}{ext or '.jpg'}"
    file_path = os.path.join(upload_dir, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload.file, buffer)
    return f"/uploads/chat_images/{filename}"


def _absolute_upload_url(request: Request, path: str | None) -> str | None:
    if path and path.startswith("/uploads/"):
        return f"{str(request.base_url).rstrip('/')}{path}"
    return path


def _create_chat_notification(db: Session, conversation: ChatConversation, message: ChatMessage):
    if message.sender_type != "visitor":
        return None
    body = message.content or "Image message"
    payload = NotificationCreate(
        business_id=conversation.business_id,
        type="chat",
        title="New message received",
        body=body,
        link_url=f"/apps/chat?conversationId={conversation.id}",
    )
    return crud_notification.create_notification(db, payload)


def _get_conversation_mode(conversation: ChatConversation) -> str:
    if conversation.ai_enabled and not conversation.ai_paused:
        return "AI"
    return "ADMIN"


def _is_admin_inactive(conversation: ChatConversation, now: datetime) -> bool:
    if conversation.ai_enabled:
        return False
    if not conversation.assigned_admin_id:
        return False
    last_reply = conversation.last_admin_reply_at or conversation.ai_handoff_at
    if not last_reply:
        return False
    timeout = timedelta(minutes=settings.ADMIN_INACTIVITY_MINUTES)
    return now - last_reply >= timeout


def _auto_handback(db: Session, conversation: ChatConversation) -> None:
    conversation.assigned_admin_id = None
    conversation.ai_enabled = True
    conversation.ai_paused = False
    conversation.last_admin_reply_at = None
    db.add(conversation)
    db.commit()
    db.refresh(conversation)


@router.post("/conversations", response_model=ChatConversationResponse, status_code=201)
def create_conversation(
    payload: ChatConversationCreate,
    db: Session = Depends(deps.get_db),
):
    try:
        conversation = crud_chat.create_conversation(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {
        "success": True,
        "status_code": 201,
        "message": "Conversation created successfully",
        "data": conversation,
    }


@router.patch("/visitors/{visitor_id}")
def update_visitor_profile(
    visitor_id: int,
    name: str | None = Form(None),
    email: str | None = Form(None),
    phone: str | None = Form(None),
    sourceUrl: str | None = Form(None),
    referrer: str | None = Form(None),
    utmSource: str | None = Form(None),
    utmMedium: str | None = Form(None),
    utmCampaign: str | None = Form(None),
    timezone: str | None = Form(None),
    language: str | None = Form(None),
    browser: str | None = Form(None),
    os: str | None = Form(None),
    device: str | None = Form(None),
    lastPage: str | None = Form(None),
    db: Session = Depends(deps.get_db),
):
    visitor = crud_chat.get_visitor(db, visitor_id)
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")
    update_data = {
        "name": name,
        "email": email,
        "phone": phone,
        "source_url": sourceUrl,
        "referrer": referrer,
        "utm_source": utmSource,
        "utm_medium": utmMedium,
        "utm_campaign": utmCampaign,
        "timezone": timezone,
        "language": language,
        "browser": browser,
        "os": os,
        "device": device,
        "last_page": lastPage,
    }
    for key, value in update_data.items():
        if value is not None:
            setattr(visitor, key, value)
    db.add(visitor)
    db.commit()
    db.refresh(visitor)
    return {"success": True, "message": "Visitor profile updated", "data": visitor}


@router.post("/visitors/{visitor_id}/avatar")
def update_visitor_avatar(
    visitor_id: int,
    request: Request,
    avatar: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    visitor = crud_chat.get_visitor(db, visitor_id)
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")
    avatar_path = _save_chat_avatar(avatar)
    visitor.avatar_url = avatar_path
    db.add(visitor)
    db.commit()
    db.refresh(visitor)
    avatar_url = avatar_path
    if avatar_url.startswith("/uploads/"):
        avatar_url = f"{str(request.base_url).rstrip('/')}{avatar_url}"
    return {
        "success": True,
        "message": "Visitor avatar updated",
        "data": {"avatarUrl": avatar_url},
    }


@router.post("/admins/me/avatar")
def update_admin_avatar(
    request: Request,
    avatar: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.require_roles(["admin"])),
):
    avatar_path = _save_chat_avatar(avatar)
    current_user.profile_image = avatar_path
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    avatar_url = avatar_path
    if avatar_url.startswith("/uploads/"):
        avatar_url = f"{str(request.base_url).rstrip('/')}{avatar_url}"
    return {
        "success": True,
        "message": "Admin avatar updated",
        "data": {"avatarUrl": avatar_url},
    }


@router.post(
    "/conversations/{conversation_id}/messages/image",
    response_model=ChatMessageResponse,
    status_code=201,
)
def create_image_message(
    conversation_id: int,
    request: Request,
    file: UploadFile = File(...),
    senderType: str = Form(...),
    senderId: int | None = Form(None),
    content: str | None = Form(None),
    db: Session = Depends(deps.get_db),
):
    conversation = crud_chat.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if senderType == "ai" and not conversation.ai_enabled:
        raise HTTPException(status_code=400, detail="AI is paused for this conversation")
    if senderType == "visitor" and _is_admin_inactive(conversation, datetime.utcnow()):
        _auto_handback(db, conversation)

    attachment_url = _save_chat_image(file)
    attachment_type = file.content_type or "image"
    attachment_name = file.filename or "image"
    attachment_size = None
    if attachment_url.startswith("/uploads/"):
        storage_path = os.path.join("uploads", attachment_url.replace("/uploads/", "").lstrip("/"))
        if os.path.exists(storage_path):
            attachment_size = os.path.getsize(storage_path)

    payload = ChatMessageCreate(
        sender_type=senderType,
        sender_id=senderId,
        content=content,
        attachment_url=attachment_url,
        attachment_type=attachment_type,
        attachment_name=attachment_name,
        attachment_size=attachment_size,
    )
    message = crud_chat.create_message(db, conversation=conversation, message_in=payload)
    _create_chat_notification(db, conversation, message)

    if message.content is None:
        message.content = ""
    message.attachment_url = _absolute_upload_url(request, message.attachment_url)

    return {
        "success": True,
        "status_code": 201,
        "message": "Message created successfully",
        "data": message,
    }


@router.get("/conversations", response_model=ChatConversationListResponse)
def list_conversations(
    businessId: int = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    status: str | None = Query(None),
    assignedAdminId: int | None = Query(None),
    aiEnabled: bool | None = Query(None),
    aiPaused: bool | None = Query(None),
    q: str | None = Query(None),
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    conversations = crud_chat.list_conversations(
        db,
        business_id=businessId,
        skip=skip,
        limit=limit,
        status=status,
        assigned_admin_id=assignedAdminId,
        ai_enabled=aiEnabled,
        ai_paused=aiPaused,
        q=q,
    )
    return {
        "success": True,
        "status_code": 200,
        "message": "Conversations retrieved successfully",
        "total": len(conversations),
        "data": conversations,
    }


@router.get("/mode/{conversation_id}", response_model=ChatModeResponse)
def get_conversation_mode(
    conversation_id: int,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    conversation = crud_chat.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {
        "success": True,
        "status_code": 200,
        "message": "Conversation mode retrieved successfully",
        "data": {
            "conversationId": conversation.id,
            "mode": _get_conversation_mode(conversation),
            "adminId": conversation.assigned_admin_id,
        },
    }


@router.post("/mode/{conversation_id}/takeover", response_model=ChatModeResponse)
def take_over_conversation(
    conversation_id: int,
    payload: ChatModeAction | None = None,
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.require_roles(["admin"])),
):
    conversation = crud_chat.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation.assigned_admin_id and conversation.assigned_admin_id != current_user.id:
        raise HTTPException(status_code=409, detail="Another admin is already handling this")
    if payload and payload.admin_id and payload.admin_id != current_user.id:
        raise HTTPException(status_code=403, detail="Admin ID mismatch")
    now = datetime.utcnow()
    conversation.assigned_admin_id = current_user.id
    conversation.ai_enabled = False
    conversation.ai_paused = True
    conversation.ai_handoff_at = conversation.ai_handoff_at or now
    conversation.last_admin_reply_at = now
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return {
        "success": True,
        "status_code": 200,
        "message": "Conversation taken over by admin",
        "data": {
            "conversationId": conversation.id,
            "mode": "ADMIN",
            "adminId": conversation.assigned_admin_id,
        },
    }


@router.post("/mode/{conversation_id}/handback", response_model=ChatModeResponse)
def hand_back_conversation(
    conversation_id: int,
    payload: ChatModeAction | None = None,
    db: Session = Depends(deps.get_db),
    current_user=Depends(deps.require_roles(["admin"])),
):
    conversation = crud_chat.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation.assigned_admin_id and conversation.assigned_admin_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the assigned admin can hand back this conversation")
    if payload and payload.admin_id and payload.admin_id != current_user.id:
        raise HTTPException(status_code=403, detail="Admin ID mismatch")
    _auto_handback(db, conversation)
    return {
        "success": True,
        "status_code": 200,
        "message": "Conversation handed back to AI",
        "data": {
            "conversationId": conversation.id,
            "mode": "AI",
            "adminId": None,
        },
    }


@router.websocket("/ws")
async def chat_ws(
    websocket: WebSocket,
    conversationId: int,
):
    db = SessionLocal()
    await manager.connect(conversationId, websocket)
    try:
        while True:
            payload = await websocket.receive_text()
            data = json.loads(payload)
            conversation = crud_chat.get_conversation(db, conversationId)
            if not conversation:
                await websocket.send_text(json.dumps({"error": "Conversation not found"}))
                continue
            if "senderType" not in data:
                await websocket.send_text(
                    json.dumps({"error": "senderType is required"})
                )
                continue
            if not data.get("content") and not data.get("attachmentUrl"):
                await websocket.send_text(
                    json.dumps({"error": "content or attachmentUrl is required"})
                )
                continue

            message_in = ChatMessageCreate(
                sender_type=data.get("senderType"),
                sender_id=data.get("senderId"),
                content=data.get("content"),
                confidence=data.get("confidence"),
                attachment_url=data.get("attachmentUrl"),
                attachment_type=data.get("attachmentType"),
                attachment_name=data.get("attachmentName"),
                attachment_size=data.get("attachmentSize"),
            )
            if message_in.sender_type == "visitor":
                if _is_admin_inactive(conversation, datetime.utcnow()):
                    _auto_handback(db, conversation)
            if message_in.sender_type == "ai" and not conversation.ai_enabled:
                await websocket.send_text(json.dumps({"error": "AI is paused"}))
                continue

            message = crud_chat.create_message(db, conversation=conversation, message_in=message_in)
            response = {
                "success": True,
                "status_code": 201,
                "message": "Message created successfully",
                "data": {
                    "id": message.id,
                    "conversationId": message.conversation_id,
                    "businessId": message.business_id,
                    "senderType": message.sender_type,
                    "senderId": message.sender_id,
                    "content": message.content,
                    "confidence": message.confidence,
                    "attachmentUrl": message.attachment_url,
                    "attachmentType": message.attachment_type,
                    "attachmentName": message.attachment_name,
                    "attachmentSize": message.attachment_size,
                    "createdAt": message.created_at.isoformat(),
                },
            }
            await manager.broadcast(conversationId, response)
            notification = _create_chat_notification(db, conversation, message)
            if notification:
                await notification_manager.broadcast(
                    conversation.business_id,
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
            if message_in.sender_type == "visitor" and conversation.ai_enabled and message_in.content:
                answer, dify_id = await call_dify_chat_async(
                    message_in.content,
                    user=f"visitor-{conversation.visitor_id}",
                    conversation_id=conversation.dify_conversation_id,
                )
                if dify_id and dify_id != conversation.dify_conversation_id:
                    conversation.dify_conversation_id = dify_id
                    db.add(conversation)
                    db.commit()
                    db.refresh(conversation)
                ai_message_in = ChatMessageCreate(
                    sender_type="ai",
                    content=answer,
                    confidence=0.8,
                )
                ai_message = crud_chat.create_message(db, conversation=conversation, message_in=ai_message_in)
                ai_response = {
                    "success": True,
                    "status_code": 201,
                    "message": "Message created successfully",
                    "data": {
                        "id": ai_message.id,
                        "conversationId": ai_message.conversation_id,
                        "businessId": ai_message.business_id,
                        "senderType": ai_message.sender_type,
                        "senderId": ai_message.sender_id,
                        "content": ai_message.content,
                        "confidence": ai_message.confidence,
                        "attachmentUrl": ai_message.attachment_url,
                        "attachmentType": ai_message.attachment_type,
                        "attachmentName": ai_message.attachment_name,
                        "attachmentSize": ai_message.attachment_size,
                        "createdAt": ai_message.created_at.isoformat(),
                    },
                }
                await manager.broadcast(conversationId, ai_response)
    except WebSocketDisconnect:
        manager.disconnect(conversationId, websocket)
    finally:
        db.close()


@router.get("/conversations/{conversation_id}", response_model=ChatConversationResponse)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    conversation = crud_chat.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {
        "success": True,
        "status_code": 200,
        "message": "Conversation retrieved successfully",
        "data": conversation,
    }


@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    conversation = crud_chat.delete_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"success": True, "message": "Conversation deleted successfully"}


@router.patch("/conversations/{conversation_id}", response_model=ChatConversationResponse)
def update_conversation(
    conversation_id: int,
    payload: ChatConversationUpdate,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    conversation = crud_chat.update_conversation(db, conversation_id, payload)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {
        "success": True,
        "status_code": 200,
        "message": "Conversation updated successfully",
        "data": conversation,
    }


@router.post("/conversations/{conversation_id}/read", response_model=ChatConversationResponse)
def mark_conversation_read(
    conversation_id: int,
    db: Session = Depends(deps.get_db),
    _: dict = Depends(deps.require_roles(["admin"])),
):
    conversation = crud_chat.mark_conversation_read(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {
        "success": True,
        "status_code": 200,
        "message": "Conversation marked as read",
        "data": conversation,
    }


@router.get("/conversations/{conversation_id}/messages", response_model=ChatMessageListResponse)
def list_messages(
    conversation_id: int,
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(deps.get_db),
):
    conversation = crud_chat.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    messages = crud_chat.list_messages(
        db,
        conversation_id=conversation_id,
        skip=skip,
        limit=limit,
    )
    if request:
        for message in messages:
            if message.content is None:
                message.content = ""
            message.attachment_url = _absolute_upload_url(request, message.attachment_url)
    return {
        "success": True,
        "status_code": 200,
        "message": "Messages retrieved successfully",
        "total": len(messages),
        "data": messages,
    }


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=ChatMessageResponse,
    status_code=201,
)
def create_message(
    conversation_id: int,
    payload: ChatMessageCreate,
    request: Request,
    db: Session = Depends(deps.get_db),
):
    conversation = crud_chat.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if not payload.content and not payload.attachment_url:
        raise HTTPException(status_code=400, detail="content or attachmentUrl is required")
    if payload.sender_type == "visitor":
        if _is_admin_inactive(conversation, datetime.utcnow()):
            _auto_handback(db, conversation)
    if payload.sender_type == "ai" and not conversation.ai_enabled:
        raise HTTPException(status_code=400, detail="AI is paused for this conversation")
    message = crud_chat.create_message(db, conversation=conversation, message_in=payload)
    _create_chat_notification(db, conversation, message)
    if message.content is None:
        message.content = ""
    message.attachment_url = _absolute_upload_url(request, message.attachment_url)
    if payload.sender_type == "visitor" and conversation.ai_enabled and payload.content:
        answer, dify_id = call_dify_chat(
            payload.content,
            user=f"visitor-{conversation.visitor_id}",
            conversation_id=conversation.dify_conversation_id,
        )
        if dify_id and dify_id != conversation.dify_conversation_id:
            conversation.dify_conversation_id = dify_id
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        ai_message_in = ChatMessageCreate(
            sender_type="ai",
            content=answer,
            confidence=0.8,
        )
        ai_message = crud_chat.create_message(db, conversation=conversation, message_in=ai_message_in)
        if ai_message.content is None:
            ai_message.content = ""
        ai_message.attachment_url = _absolute_upload_url(request, ai_message.attachment_url)
        return {
            "success": True,
            "status_code": 201,
            "message": "Message created successfully",
            "data": ai_message,
        }
    return {
        "success": True,
        "status_code": 201,
        "message": "Message created successfully",
        "data": message,
    }


@router.post("/conversations/{conversation_id}/ai-reply", response_model=ChatMessageResponse)
def ai_reply(
    conversation_id: int,
    db: Session = Depends(deps.get_db),
):
    conversation = crud_chat.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if not conversation.ai_enabled:
        raise HTTPException(status_code=400, detail="AI is paused for this conversation")

    last_visitor_message = crud_chat.get_last_visitor_message(db, conversation_id=conversation_id)
    if not last_visitor_message or not last_visitor_message.content:
        raise HTTPException(status_code=400, detail="No visitor message found to reply to")

    answer, dify_id = call_dify_chat(
        last_visitor_message.content,
        user=f"visitor-{conversation.visitor_id}",
        conversation_id=conversation.dify_conversation_id,
    )
    if dify_id and dify_id != conversation.dify_conversation_id:
        conversation.dify_conversation_id = dify_id
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    ai_message = ChatMessageCreate(
        sender_type="ai",
        content=answer,
        confidence=0.8,
    )
    message = crud_chat.create_message(db, conversation=conversation, message_in=ai_message)
    if message.confidence is not None and message.confidence < 0.4:
        crud_chat.update_conversation(
            db,
            conversation_id,
            ChatConversationUpdate(status="Pending"),
        )

    return {
        "success": True,
        "status_code": 200,
        "message": "AI reply generated",
        "data": message,
    }
