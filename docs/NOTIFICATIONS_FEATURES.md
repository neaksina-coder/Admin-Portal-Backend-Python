# Notifications Feature — Actions and Endpoints

This document lists which actions generate notifications and the available API/WS endpoints.

---

## 1) Actions That Generate Notifications

### A) Visitor Chat Message (Auto)
Trigger: visitor sends a chat message.

Generated in: `api/v1/chat.py` via `_create_chat_notification(...)`

Notification fields:
- `type`: `chat`
- `title`: `New message received`
- `body`: message content or `Image message`
- `linkUrl`: `/apps/chat?conversationId=<id>`

---

### B) Manual Notification (Admin API)
Trigger: admin calls `POST /api/v1/notifications`

Purpose: create any custom notification (system alerts, billing warnings, etc.).

---

## 2) REST Endpoints (Base: `/api/v1/notifications`)

- `GET /notifications?businessId=...&skip=0&limit=10&unreadOnly=false`
  - List notifications for a business.
- `GET /notifications/unread-count?businessId=...`
  - Get unread count.
- `POST /notifications`
  - Create a notification (also broadcasts via WS).
- `POST /notifications/{notification_id}/read`
  - Mark one notification as read.
- `POST /notifications/read-all?businessId=...`
  - Mark all notifications as read for a business.
- `DELETE /notifications/{notification_id}`
  - Delete a notification.

---

## 3) WebSocket Endpoint

- `WS /api/v1/notifications/ws?businessId=...&token=...`
  - Admin/superuser only.
  - Receives real-time notifications when created.

