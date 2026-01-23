# Superuser Management (Roles & Permissions UI)

This document describes how to implement **create superuser** and **update role to superuser** from the Roles & Permissions page.

## Access

- Only authenticated **superusers** can create or promote superusers.
- Admins and regular users must not see or access these actions.

## API Endpoints

### Create Superuser (superuser only)

`POST /users/superusers`

Body:
```json
{
  "fullName": "Super User",
  "email": "super@example.com",
  "password": "SuperPass123",
  "role": "superuser",
  "plan": "team",
  "billing": "Manual-PayPal",
  "status": "active"
}
```

Response:
```json
{
  "id": 11,
  "fullName": "Super User",
  "email": "super@example.com",
  "role": "superuser",
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

### Update Role (superuser only)

`PUT /users/{id}/role`

Body:
```json
{ "role": "superuser" }
```

Response:
```json
{
  "id": 2,
  "fullName": "Jane Doe",
  "email": "jane@example.com",
  "role": "superuser",
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

## UI Behavior (Roles & Permissions page)

- Show a **"Create Superuser"** action only if the logged-in user is a superuser.
- Allow role change to **superuser** only for superusers.
- Keep existing role options for admins: `user`, `admin` (no `superuser`).

### Recommended UI flow

1. User opens **Roles & Permissions**.
2. If `currentUser.role === "superuser"`:
   - Show "Create Superuser" button.
   - Show `superuser` option in role update controls.
3. Submit form -> call API -> show success toast and refresh list.

## Validation and Error Handling

Common error responses:

- `400` invalid role (role must be `superuser` for `/users/superusers`).
- `403` not enough permissions (non-superuser).
- `409` email already exists.

## Notes

- The backend sets `is_superuser = true` when role is `superuser`.
- Login returns `role = "superuser"` for superusers, so the UI can rely on `currentUser.role` to gate access.
