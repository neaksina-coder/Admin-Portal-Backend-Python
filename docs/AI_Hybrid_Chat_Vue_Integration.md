# AI Hybrid Chat — Vue Integration Guide

This guide shows how to integrate the hybrid AI + admin chat flow into your Vue frontend.

---

## 1) Environment

Example `.env` for Vue:
```ini
VITE_API_BASE=http://127.0.0.1:8000/api/v1
```

---

## 2) Create Conversation (Visitor)

Create once when the widget opens or on first message.

```ts
// POST /chat/conversations
const res = await fetch(`${API}/chat/conversations`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    businessId: 1,
    visitor: {
      name: "Test Visitor",
      email: "test@example.com",
      sourceUrl: window.location.href,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      language: navigator.language
    }
  })
});
const data = await res.json();
const conversationId = data.data.id;
```

---

## 3) Connect WebSocket

```ts
const ws = new WebSocket(`ws://127.0.0.1:8000/api/v1/chat/ws?conversationId=${conversationId}`);

ws.onmessage = (evt) => {
  const payload = JSON.parse(evt.data);
  const msg = payload.data;
  // append to chat UI
};
```

---

## 4) Send Visitor Message (AI auto‑reply)

```ts
ws.send(JSON.stringify({
  senderType: "visitor",
  content: "Hi"
}));
```

Expected:
- Visitor message is stored.
- AI replies automatically if conversation mode is AI.

---

## 5) Admin Takeover (Admin UI)

```ts
// POST /chat/mode/{conversationId}/takeover
await fetch(`${API}/chat/mode/${conversationId}/takeover`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${adminToken}`
  },
  body: JSON.stringify({ adminId })
});
```

Expected:
- Mode becomes ADMIN.
- AI stops replying.

---

## 6) Admin Send Reply (WS)

```ts
ws.send(JSON.stringify({
  senderType: "admin",
  senderId: adminId,
  content: "Hi, how can I help?"
}));
```

---

## 7) Handback to AI

```ts
// POST /chat/mode/{conversationId}/handback
await fetch(`${API}/chat/mode/${conversationId}/handback`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${adminToken}`
  },
  body: JSON.stringify({ adminId })
});
```

Expected:
- Mode becomes AI.
- AI resumes replying.

---

## 8) Check Mode (Admin UI)

```ts
// GET /chat/mode/{conversationId}
const res = await fetch(`${API}/chat/mode/${conversationId}`, {
  headers: { "Authorization": `Bearer ${adminToken}` }
});
const data = await res.json();
// data.data.mode = "AI" or "ADMIN"
```

---

## 9) Inactivity Auto‑Handback

If admin is inactive for 5 minutes, the next visitor message triggers auto‑handback to AI.
You do not need to call anything from the frontend.

---

## 10) Fallback Answer

If AI cannot answer, backend sends:
`I'm sorry, I don't have that information. Please contact our support team.`

---

## 11) UI Tips

- Show mode badge: `AI` vs `ADMIN`.
- Disable typing indicator for AI when in ADMIN mode.
- When admin takes over, display “Admin joined”.
- When handback, display “AI resumed”.

