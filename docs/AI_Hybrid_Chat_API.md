# AI Hybrid Chat — API Spec (FastAPI + Dify)

This document defines the API behavior for hybrid AI + admin chat. The AI auto-replies when the conversation mode is `AI`. When an admin takes over, mode becomes `ADMIN` and the AI stays silent. When the admin hands back, mode returns to `AI`.

---

## 1) Dify API (External)

### POST `https://api.dify.ai/v1/chat-messages`
Send a user message to Dify and receive an AI reply.

**Headers**
- `Authorization: Bearer <DIFY_API_KEY>`
- `Content-Type: application/json`

**Request Body (example)**
```json
{
  "inputs": {},
  "query": "Hi",
  "response_mode": "blocking",
  "conversation_id": "optional-existing-id",
  "user": "visitor-123"
}
```

**Response (example)**
```json
{
  "event": "message",
  "answer": "Hello! How can I help you today?",
  "conversation_id": "dify-conv-id",
  "message_id": "dify-msg-id",
  "created_at": 1700000000
}
```

**Notes**
- Use `response_mode: blocking` for synchronous replies.
- Persist `conversation_id` returned by Dify for follow-up messages.

---

## 2) Internal Chat API (FastAPI)

Base URL: `/api/v1`

### Conversation Mode

#### GET `/chat/mode/{conversation_id}`
Returns the current mode for a conversation.

**Response**
```json
{
  "conversationId": 123,
  "mode": "AI",
  "adminId": null
}
```

#### POST `/chat/mode/{conversation_id}/takeover`
Admin takes control of the conversation.

**Request**
```json
{
  "adminId": 45
}
```

**Response**
```json
{
  "conversationId": 123,
  "mode": "ADMIN",
  "adminId": 45
}
```

**Conflict (Admin already assigned)**
```json
{
  "error": "Another admin is already handling this"
}
```

#### POST `/chat/mode/{conversation_id}/handback`
Admin returns control to AI.

**Request**
```json
{
  "adminId": 45
}
```

**Response**
```json
{
  "conversationId": 123,
  "mode": "AI",
  "adminId": null
}
```

---

### Incoming Messages (Visitor)

#### POST `/chat/messages`
Creates a new visitor message. If mode is `AI`, the backend calls Dify and returns the AI reply. If mode is `ADMIN`, AI is silent.

**Request**
```json
{
  "conversationId": 123,
  "senderType": "visitor",
  "message": "Hi"
}
```

**Response (mode = AI)**
```json
{
  "conversationId": 123,
  "senderType": "ai",
  "message": "Hello! How can I help you today?"
}
```

**Response (mode = ADMIN)**
```json
{
  "conversationId": 123,
  "senderType": "system",
  "message": "Message delivered to admin."
}
```

**Errors**
```json
{
  "error": "Conversation not found"
}
```

---

### Admin Messages

#### POST `/chat/messages/admin`
Admin replies to a conversation.

**Request**
```json
{
  "conversationId": 123,
  "senderType": "admin",
  "adminId": 45,
  "message": "I can help you with that."
}
```

**Response**
```json
{
  "conversationId": 123,
  "senderType": "admin",
  "message": "I can help you with that."
}
```

**Behavior**
- Admin replies reset the inactivity timer.
- If admin is active, AI stays silent.

---

## 3) Mode Logic Summary

- Default for new conversations: `AI`.
- Admin takes over: `mode = ADMIN`, `adminId = <id>`.
- Admin hands back: `mode = AI`, `adminId = null`.
- If another admin already owns the conversation, block takeover.

---

## 4) Admin Inactivity Timer

- If no admin reply for 5 minutes, auto handback to AI.
- Timer resets on every admin reply.
- Only affects the conversation where admin is assigned.

---

## 5) Expected Behaviors (Tests)

- AI replies to new conversations by default.
- AI stays silent in `ADMIN` mode.
- Handback restores AI replies.
- AI uses knowledge base when available.
- Unknown questions return fallback:  
  `"I'm sorry, I don't have that information. Please contact our support team."`

