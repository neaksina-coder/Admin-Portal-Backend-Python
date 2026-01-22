# User Management API (Admin/Superuser)

This document defines the backend endpoints and rules for managing users.

## Roles

System roles:
- `user`
- `admin`

Notes:
- `superuser` is a flag/privilege (e.g. `is_superuser = true`), not a selectable role in the UI.
- When `is_superuser = true`, treat the user as full access.

## Access Rules

- Superuser can manage **all users** (both `admin` and `user`).
- Admin can manage **only `user` accounts**.
- Admin **cannot** manage superuser accounts.
- Admin **cannot** manage other admins (create/update/delete).

## List Users

`GET /users`

Returns a list of users with filters and pagination.

Query params:
- `q`: string (search by name/email)
- `role`: `user | admin`
- `plan`: string (e.g. basic/team/enterprise)
- `status`: string (e.g. active/inactive/pending)
- `page`: number
- `itemsPerPage`: number
- `sortBy`: string (e.g. user/email/role/plan/status/billing)
- `orderBy`: `asc | desc`

Rules:
- Superuser: can see all users.
- Admin: can see only `user` role accounts.

Response:
```json
{
  "users": [
    {
      "id": 1,
      "fullName": "Jane Doe",
      "email": "jane@example.com",
      "role": "user",
      "plan": "team",
      "billing": "Manual-PayPal",
      "status": "active"
    }
  ],
  "totalUsers": 50,
  "page": 1
}
```

## Get User Detail

`GET /users/{id}`

Rules:
- Superuser: can view any user.
- Admin: can view only `user` accounts.

Response (example):
```json
{
  "id": 1,
  "fullName": "Jane Doe",
  "email": "jane@example.com",
  "role": "user",
  "plan": "team",
  "billing": "Manual-PayPal",
  "status": "active",
  "profile": {
    "company": "Acme",
    "country": "USA",
    "contact": "+1 234 567 890"
  }
}
```

## Create User (Admin or Superuser)

`POST /users`

Rules:
- Superuser: can create `admin` or `user`.
- Admin: can create only `user`.

Body:
```json
{
  "fullName": "Jane Doe",
  "email": "jane@example.com",
  "password": "StrongPass123",
  "role": "user",
  "plan": "team",
  "billing": "Manual-PayPal",
  "status": "active"
}
```

Response:
```json
{
  "id": 1,
  "fullName": "Jane Doe",
  "email": "jane@example.com",
  "role": "user",
  "plan": "team",
  "billing": "Manual-PayPal",
  "status": "active",
  "profile": {
    "company": null,
    "country": null,
    "contact": null
  }
}
```

## Update User

`PUT /users/{id}`

Rules:
- Superuser: can update any user (role/plan/billing/status).
- Admin: can update only `user` accounts; must not set role to `admin` or touch superuser accounts.

Body (example):
```json
{
  "fullName": "Jane Doe",
  "plan": "enterprise",
  "billing": "Manual-Credit Card",
  "status": "active",
  "company": "Acme",
  "country": "USA",
  "contact": "+1 234 567 890"
}
```

Response:
```json
{
  "id": 1,
  "fullName": "Jane Doe",
  "email": "jane@example.com",
  "role": "user",
  "plan": "enterprise",
  "billing": "Manual-Credit Card",
  "status": "active",
  "profile": {
    "company": "Acme",
    "country": "USA",
    "contact": "+1 234 567 890"
  }
}
```

## Delete User

`DELETE /users/{id}`

Rules:
- Superuser: can delete any user.
- Admin: can delete only `user` accounts.

Response:
```json
{ "success": true }
```

## Create Admin (Superuser only)

`POST /users/admins`

Rules:
- Superuser only.

Body:
```json
{
  "fullName": "Admin User",
  "email": "admin@example.com",
  "password": "AdminPass123",
  "role": "admin",
  "plan": "team",
  "billing": "Manual-PayPal",
  "status": "active"
}
```

Response:
```json
{
  "id": 10,
  "fullName": "Admin User",
  "email": "admin@example.com",
  "role": "admin",
  "plan": "team",
  "billing": "Manual-PayPal",
  "status": "active",
  "profile": {
    "company": null,
    "country": null,
    "contact": null
  }
}
```

## Role Update (Superuser only)

`PUT /users/{id}/role`

Rules:
- Superuser only.
- Allowed roles: `user`, `admin`

Body:
```json
{ "role": "admin" }
```

Response:
```json
{
  "id": 1,
  "fullName": "Jane Doe",
  "email": "jane@example.com",
  "role": "admin",
  "plan": "team",
  "billing": "Manual-PayPal",
  "status": "active",
  "profile": {
    "company": "Acme",
    "country": "USA",
    "contact": "+1 234 567 890"
  }
}
```

## UI Notes

- Role dropdown should show only: `user`, `admin`.
- Keep `Plan` and `Billing` columns visible in the list header.
- Admin must not see or access role/permission management screens.
