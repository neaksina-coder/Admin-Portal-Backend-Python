# Business Customer Account API

This document describes the endpoints used by the customer-facing Account & Security pages.

## Base URL

`/api/v1`

## Authentication

All endpoints require a valid `Authorization: Bearer <token>` header.

If the user’s business is suspended, the API returns:

`403` with `{"detail":"Business account is suspended"}`

## Account Profile

### Get current user profile

`GET /users/me`

Response:
```json
{
  "id": 1,
  "fullName": "John Doe",
  "email": "john@demo.com",
  "role": "customer_owner",
  "isSuperuser": false,
  "businessId": 3,
  "profile": {
    "company": "PNC",
    "country": "Cambodia",
    "contact": "0969780938",
    "profileImage": "http://localhost:8000/uploads/profile_images/abc.png"
  }
}
```

### Update current user profile

`PUT /users/me`

Content type: `multipart/form-data`

Fields:
- `fullName` (string, optional)
- `email` (string, optional)
- `company` (string, optional)
- `country` (string, optional)
- `contact` (string, optional)
- `profileImage` (file, optional)

Response: same shape as `GET /users/me`

Notes:
- If `email` is already taken by another user, returns `409`.

## Security

### Update password

`PUT /users/me/password`

Body (JSON):
```json
{
  "currentPassword": "OldPass123!",
  "newPassword": "NewPass123!",
  "confirmPassword": "NewPass123!"
}
```

Response:
```json
{ "success": true, "message": "Password updated successfully" }
```

## Business Account

### Get current business

`GET /business-account/me`

Response:
```json
{
  "success": true,
  "status_code": 200,
  "message": "Business account retrieved successfully",
  "data": {
    "id": 3,
    "name": "HR-Management",
    "tenantId": "hr-team",
    "planId": 2,
    "plan": { "id": 2, "name": "Pro" },
    "status": "active",
    "suspendedAt": null,
    "suspendedReason": null,
    "timestamps": {
      "created": "2026-02-05T12:00:00",
      "updated": "2026-02-05T12:00:00"
    }
  }
}
```

### Update current business

`PUT /business-account/me`

Body (JSON):
```json
{
  "name": "New Business Name",
  "tenantId": "new-tenant-code"
}
```

Response: same shape as `GET /business-account/me`

Notes:
- `tenantId` must be unique and not empty.
- `name` must be not empty.
