# api/v1/chat.py
import json
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from api import deps
from crud import chat as crud_chat
from db.session import SessionLocal
from schemas.chat import (
    ChatConversationCreate,
    ChatConversationUpdate,
    ChatConversationResponse,
    ChatConversationListResponse,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatMessageListResponse,
)

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


@router.websocket("/ws")
async def chat_ws(
    websocket: WebSocket,
    conversationId: int,
):
    db = SessionLocal()
    await manager.connect(conversationId, websocket)
    try:
        conversation = crud_chat.get_conversation(db, conversationId)
        if not conversation:
            await websocket.send_text(json.dumps({"error": "Conversation not found"}))
            return

        while True:
            payload = await websocket.receive_text()
            data = json.loads(payload)
            if "senderType" not in data or "content" not in data:
                await websocket.send_text(
                    json.dumps({"error": "senderType and content are required"})
                )
                continue

            message_in = ChatMessageCreate(
                sender_type=data.get("senderType"),
                sender_id=data.get("senderId"),
                content=data.get("content"),
                confidence=data.get("confidence"),
            )
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
                    "createdAt": message.created_at.isoformat(),
                },
            }
            await manager.broadcast(conversationId, response)
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
    db: Session = Depends(deps.get_db),
):
    conversation = crud_chat.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if payload.sender_type == "ai" and not conversation.ai_enabled:
        raise HTTPException(status_code=400, detail="AI is paused for this conversation")
    message = crud_chat.create_message(db, conversation=conversation, message_in=payload)
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

    placeholder_message = ChatMessageCreate(
        sender_type="ai",
        content="Thanks for your message. An admin will reply if needed.",
        confidence=0.2,
    )
    message = crud_chat.create_message(db, conversation=conversation, message_in=placeholder_message)
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
