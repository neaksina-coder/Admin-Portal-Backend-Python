# Realtime Chat Integration (Vue)

This document explains how to integrate the new realtime chat feature with your existing Vue UI for both Website (visitor) and Admin.

## Overview
- REST is used to create a conversation and load history.
- WebSocket (WS) is used for realtime send/receive in that conversation.
- Both Visitor and Admin connect to the same WS URL with the same `conversationId`.

## Backend Endpoints

### REST
- `POST /api/v1/chat/conversations`
- `GET /api/v1/chat/conversations?businessId=...` (superuser + admin only)
- `GET /api/v1/chat/conversations/{id}` (superuser + admin only)
- `GET /api/v1/chat/conversations/{id}/messages`
- `POST /api/v1/chat/conversations/{id}/messages`

### WebSocket
- `ws://127.0.0.1:8000/api/v1/chat/ws?conversationId=ID`

## Data Model (Summary)
- `chat_conversations`
- `chat_messages`
- `chat_visitors`

## Visitor Flow (Website)

1. Create conversation (once, when widget opens or first message)
   - `POST /chat/conversations`

Request:
```json
{
  "businessId": 1,
  "visitor": {
    "name": "Sokha",
    "email": "sokha@gmail.com",
    "phone": "+85512345678",
    "sourceUrl": "https://your-site.com/pricing",
    "referrer": "https://google.com",
    "utmSource": "google",
    "utmMedium": "cpc",
    "utmCampaign": "pricing",
    "timezone": "Asia/Phnom_Penh",
    "language": "en-US",
    "browser": "Chrome",
    "os": "Windows",
    "device": "Desktop",
    "lastPage": "/pricing"
  }
}
```

Response:
- save `conversationId = data.id`

2. Load history (optional)
   - `GET /chat/conversations/{id}/messages`

3. Connect WebSocket
```js
const ws = new WebSocket(`ws://127.0.0.1:8000/api/v1/chat/ws?conversationId=${conversationId}`);
```

4. Send message via WS
```js
ws.send(JSON.stringify({
  senderType: "visitor",
  content: "Hello, I need help"
}));
```

5. Receive messages
```js
ws.onmessage = (evt) => {
  const payload = JSON.parse(evt.data);
  const msg = payload.data;
  // append to chat UI
};
```

## Admin Flow (Admin UI)

1. List conversations (admin token required)
   - `GET /chat/conversations?businessId=1`
   - Response items include `visitor` so the UI can show real names:
```json
{
  "id": 16,
  "visitorId": 1,
  "visitor": {
    "name": "Sina Neak",
    "email": "visitor@test.com",
    "sourceUrl": "https://your-site.com/landing"
  }
}
```
   - Response items also include unread state:
```json
{
  "id": 16,
  "unreadCount": 3,
  "lastReadAt": "2026-02-13T18:22:01.123456"
}
```

2. Open conversation
   - `GET /chat/conversations/{id}/messages`
   - Mark as read (when admin opens the chat)
   - `POST /chat/conversations/{id}/read`

3. Connect WebSocket (same as visitor)
```js
const ws = new WebSocket(`ws://127.0.0.1:8000/api/v1/chat/ws?conversationId=${conversationId}`);
```

4. Send reply via WS
```js
ws.send(JSON.stringify({
  senderType: "admin",
  senderId: adminId, // optional but recommended
  content: "Hi! I can help you."
}));
```

5. Receive realtime messages
Same as visitor.

## Profile Updates
- Update visitor profile (public, for widget):
  - `PATCH /chat/visitors/{visitorId}` (multipart form)
- Update visitor avatar (admin only):
  - `POST /chat/visitors/{visitorId}/avatar` (multipart form, field `avatar`)
- Update admin avatar (admin only):
  - `POST /chat/admins/me/avatar` (multipart form, field `avatar`)

## Message Payload (WS)
Send:
```json
{
  "senderType": "visitor | admin | ai",
  "senderId": 5,
  "content": "Message text",
  "confidence": 0.8
}
```

## Read/Unread (Short)
- Unread count is global (all admins share the same state).
- Use `unreadCount` from `GET /chat/conversations` to show the badge.
- When an admin opens a chat, call:
  - `POST /chat/conversations/{id}/read`
- After marking read, the conversation returns with:
  - `unreadCount: 0`
  - `lastReadAt: <timestamp>`

Receive:
```json
{
  "success": true,
  "status_code": 201,
  "message": "Message created successfully",
  "data": {
    "id": 123,
    "conversationId": 1,
    "businessId": 1,
    "senderType": "visitor",
    "senderId": null,
    "content": "Hello",
    "confidence": null,
    "createdAt": "2026-02-12T08:58:08.192972"
  }
}
```

## Vue Integration Notes
- Keep a single WS connection per active conversation.
- Use REST to create conversation and load initial history.
- Use WS only for realtime send/receive.
- On page refresh, re-connect to WS and re-load history.

## Admin Auth
- `GET /chat/conversations` and `GET /chat/conversations/{id}` require admin token.
- WebSocket endpoint is currently public; if you want admin-only WS replies, ask to add WS auth.

## Common Issues
- 404 on `/chat/*`: server not restarted after adding router.
- 401 on `GET /chat/conversations`: missing admin token.
- No WS response: wrong `conversationId` or conversation not created.
