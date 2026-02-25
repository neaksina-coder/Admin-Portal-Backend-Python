# Chat Image Admin Fix (Short)

If admin can’t see image messages, update the backend to:

1. Return absolute URLs for `attachmentUrl`.
2. Ensure `content` is not null (use empty string).

These changes are already applied in `api/v1/chat.py`.
