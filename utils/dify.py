# utils/dify.py
from __future__ import annotations

from typing import Optional, Tuple

import httpx

from core.config import settings


def _build_headers() -> dict:
    if not settings.DIFY_API_KEY:
        raise RuntimeError("DIFY_API_KEY is not configured")
    return {
        "Authorization": f"Bearer {settings.DIFY_API_KEY}",
        "Content-Type": "application/json",
    }


def _build_payload(query: str, user: str, conversation_id: Optional[str]) -> dict:
    payload = {
        "inputs": {},
        "query": query,
        "response_mode": settings.DIFY_RESPONSE_MODE or "blocking",
        "user": user,
    }
    if conversation_id:
        payload["conversation_id"] = conversation_id
    return payload


def _parse_response(data: dict) -> Tuple[str, Optional[str]]:
    answer = (data.get("answer") or "").strip()
    conversation_id = data.get("conversation_id")
    if not answer:
        answer = settings.DIFY_FALLBACK_MESSAGE
    return answer, conversation_id


def call_dify_chat(query: str, *, user: str, conversation_id: Optional[str] = None) -> Tuple[str, Optional[str]]:
    if not settings.DIFY_API_KEY:
        return settings.DIFY_FALLBACK_MESSAGE, conversation_id
    url = f"{settings.DIFY_BASE_URL.rstrip('/')}/chat-messages"
    payload = _build_payload(query, user, conversation_id)
    try:
        with httpx.Client(timeout=20) as client:
            response = client.post(url, headers=_build_headers(), json=payload)
        if response.status_code >= 400:
            return settings.DIFY_FALLBACK_MESSAGE, conversation_id
        data = response.json()
        return _parse_response(data)
    except Exception:
        return settings.DIFY_FALLBACK_MESSAGE, conversation_id


async def call_dify_chat_async(
    query: str,
    *,
    user: str,
    conversation_id: Optional[str] = None,
) -> Tuple[str, Optional[str]]:
    if not settings.DIFY_API_KEY:
        return settings.DIFY_FALLBACK_MESSAGE, conversation_id
    url = f"{settings.DIFY_BASE_URL.rstrip('/')}/chat-messages"
    payload = _build_payload(query, user, conversation_id)
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(url, headers=_build_headers(), json=payload)
        if response.status_code >= 400:
            return settings.DIFY_FALLBACK_MESSAGE, conversation_id
        data = response.json()
        return _parse_response(data)
    except Exception:
        return settings.DIFY_FALLBACK_MESSAGE, conversation_id
