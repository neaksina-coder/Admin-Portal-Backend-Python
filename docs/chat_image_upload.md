# Chat Image Upload (Frontend Guide)

This backend now supports image messages for realtime chat. Use the REST upload endpoint for the binary file, then render the returned attachment fields in your UI. Optionally, broadcast via WebSocket if you want other clients to see the image immediately.

## Endpoint

`POST /api/v1/chat/conversations/{conversation_id}/messages/image`

### Form Data
- `file` (File, required): Image file.
- `senderType` (Text, required): `visitor` or `admin` (or `ai` if you use it).
- `senderId` (Text, optional)
- `content` (Text, optional): caption text.

### Response
Returns a normal chat message with attachment fields:
- `attachmentUrl`
- `attachmentType`
- `attachmentName`
- `attachmentSize`

## Minimal Frontend Flow

1. User drops an image in the chat input.
2. Upload the image via the endpoint above (multipart form).
3. Append the returned message to your UI.
4. If you want other clients to see it in realtime, send a WebSocket message with the returned attachment fields (see below).

## WebSocket Payload (Optional)

Send this after a successful upload if you want realtime broadcast:

```json
{
  "senderType": "visitor",
  "senderId": 123,
  "content": "Image caption",
  "attachmentUrl": "/uploads/chat_images/xxxxxxxx.jpg",
  "attachmentType": "image/jpeg",
  "attachmentName": "photo.jpg",
  "attachmentSize": 123456
}
```

## UI Rendering Rules

- If `attachmentUrl` exists and `attachmentType` starts with `image/`, render an `<img>` preview.
- Show `content` as caption if present.
- Fallback to a file icon + `attachmentName` if the UI cannot render the image.

## Example JavaScript (Fetch)

```js
const form = new FormData();
form.append("file", file);
form.append("senderType", "visitor");
form.append("senderId", String(visitorId));
form.append("content", caption || "");

const res = await fetch(
  `/api/v1/chat/conversations/${conversationId}/messages/image`,
  { method: "POST", body: form }
);
const json = await res.json();
// Append json.data to your messages list.
```

## Notes

- Backend accepts common image types: `jpg`, `jpeg`, `png`, `gif`, `webp`, `bmp`.
- Uploaded files are saved under `uploads/chat_images` and served at `/uploads/...`.
