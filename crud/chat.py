# crud/chat.py
from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from models.chat_visitor import ChatVisitor
from models.chat_conversation import ChatConversation
from models.chat_message import ChatMessage
from schemas.chat import ChatConversationCreate, ChatConversationUpdate, ChatMessageCreate, ChatVisitorBase


def get_conversation(db: Session, conversation_id: int) -> Optional[ChatConversation]:
    return (
        db.query(ChatConversation)
        .options(joinedload(ChatConversation.visitor_ref))
        .filter(ChatConversation.id == conversation_id)
        .first()
    )


def list_conversations(
    db: Session,
    *,
    business_id: int,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    assigned_admin_id: Optional[int] = None,
    ai_enabled: Optional[bool] = None,
    ai_paused: Optional[bool] = None,
    q: Optional[str] = None,
) -> List[ChatConversation]:
    query = (
        db.query(ChatConversation)
        .options(joinedload(ChatConversation.visitor_ref))
        .filter(ChatConversation.business_id == business_id)
    )
    if status:
        query = query.filter(ChatConversation.status == status)
    if assigned_admin_id is not None:
        query = query.filter(ChatConversation.assigned_admin_id == assigned_admin_id)
    if ai_enabled is not None:
        query = query.filter(ChatConversation.ai_enabled == ai_enabled)
    if ai_paused is not None:
        query = query.filter(ChatConversation.ai_paused == ai_paused)
    if q:
        like = f"%{q}%"
        query = query.join(ChatVisitor, ChatVisitor.id == ChatConversation.visitor_id).filter(
            or_(
                ChatVisitor.name.ilike(like),
                ChatVisitor.email.ilike(like),
            )
        )
    return (
        query.order_by(ChatConversation.updated_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_visitor(db: Session, visitor_id: int) -> Optional[ChatVisitor]:
    return db.query(ChatVisitor).filter(ChatVisitor.id == visitor_id).first()


def create_or_update_visitor(
    db: Session,
    *,
    business_id: int,
    visitor_in: ChatVisitorBase,
) -> ChatVisitor:
    visitor = None
    if visitor_in.email:
        visitor = (
            db.query(ChatVisitor)
            .filter(ChatVisitor.business_id == business_id, ChatVisitor.email == visitor_in.email)
            .first()
        )
    now = datetime.utcnow()
    if visitor:
        for field in (
            "name",
            "email",
            "phone",
            "avatar_url",
            "source_url",
            "referrer",
            "utm_source",
            "utm_medium",
            "utm_campaign",
            "ip",
            "country",
            "city",
            "timezone",
            "language",
            "browser",
            "os",
            "device",
            "last_page",
        ):
            value = getattr(visitor_in, field)
            if value is not None:
                setattr(visitor, field, value)
        visitor.last_seen_at = now
        db.commit()
        db.refresh(visitor)
        return visitor

    visitor = ChatVisitor(
        business_id=business_id,
        name=visitor_in.name,
        email=visitor_in.email,
        phone=visitor_in.phone,
        avatar_url=visitor_in.avatar_url,
        source_url=visitor_in.source_url,
        referrer=visitor_in.referrer,
        utm_source=visitor_in.utm_source,
        utm_medium=visitor_in.utm_medium,
        utm_campaign=visitor_in.utm_campaign,
        ip=visitor_in.ip,
        country=visitor_in.country,
        city=visitor_in.city,
        timezone=visitor_in.timezone,
        language=visitor_in.language,
        browser=visitor_in.browser,
        os=visitor_in.os,
        device=visitor_in.device,
        last_page=visitor_in.last_page,
        first_seen_at=now,
        last_seen_at=now,
        message_count=0,
    )
    db.add(visitor)
    db.commit()
    db.refresh(visitor)
    return visitor


def create_conversation(db: Session, conversation_in: ChatConversationCreate) -> ChatConversation:
    visitor_id = conversation_in.visitor_id
    if visitor_id:
        visitor = get_visitor(db, visitor_id)
        if not visitor:
            raise ValueError("Visitor not found")
        if visitor.business_id != conversation_in.business_id:
            raise ValueError("Visitor does not belong to this business")
    else:
        if not conversation_in.visitor:
            raise ValueError("Visitor details are required")
        visitor = create_or_update_visitor(
            db,
            business_id=conversation_in.business_id,
            visitor_in=conversation_in.visitor,
        )
        visitor_id = visitor.id

    conversation = ChatConversation(
        business_id=conversation_in.business_id,
        visitor_id=visitor_id,
        status=conversation_in.status or "Open",
        assigned_admin_id=conversation_in.assigned_admin_id,
        ai_enabled=True if conversation_in.ai_enabled is None else conversation_in.ai_enabled,
        ai_paused=False if conversation_in.ai_paused is None else conversation_in.ai_paused,
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def update_conversation(
    db: Session,
    conversation_id: int,
    conversation_in: ChatConversationUpdate,
) -> Optional[ChatConversation]:
    conversation = get_conversation(db, conversation_id)
    if not conversation:
        return None
    update_data = conversation_in.dict(exclude_unset=True, by_alias=False)
    for key, value in update_data.items():
        setattr(conversation, key, value)
    db.commit()
    db.refresh(conversation)
    return conversation


def list_messages(
    db: Session,
    *,
    conversation_id: int,
    skip: int = 0,
    limit: int = 100,
) -> List[ChatMessage]:
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_message(
    db: Session,
    *,
    conversation: ChatConversation,
    message_in: ChatMessageCreate,
) -> ChatMessage:
    message = ChatMessage(
        conversation_id=conversation.id,
        business_id=conversation.business_id,
        sender_type=message_in.sender_type,
        sender_id=message_in.sender_id,
        content=message_in.content,
        confidence=message_in.confidence,
    )
    db.add(message)

    now = datetime.utcnow()
    conversation.last_message_at = now
    if message_in.sender_type == "admin":
        if conversation.ai_enabled:
            conversation.ai_handoff_at = conversation.ai_handoff_at or now
        conversation.ai_enabled = False
        conversation.ai_paused = True
        conversation.status = conversation.status or "Open"
    elif message_in.sender_type == "visitor":
        conversation.status = "Open"
        visitor = get_visitor(db, conversation.visitor_id)
        if visitor:
            visitor.last_seen_at = now
            visitor.message_count = (visitor.message_count or 0) + 1
            db.add(visitor)
        conversation.unread_count = (conversation.unread_count or 0) + 1
    else:
        conversation.unread_count = 0
        conversation.last_read_at = now
    db.add(conversation)
    db.commit()
    db.refresh(message)
    return message


def mark_conversation_read(db: Session, conversation_id: int) -> Optional[ChatConversation]:
    conversation = get_conversation(db, conversation_id)
    if not conversation:
        return None
    conversation.unread_count = 0
    conversation.last_read_at = datetime.utcnow()
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def delete_conversation(db: Session, conversation_id: int) -> Optional[ChatConversation]:
    conversation = get_conversation(db, conversation_id)
    if not conversation:
        return None
    db.query(ChatMessage).filter(ChatMessage.conversation_id == conversation_id).delete()
    db.delete(conversation)
    db.commit()
    return conversation
