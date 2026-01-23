# Users Filters API

Endpoint:
- `GET /api/v1/users/filters`

Auth:
- Bearer token required (admin role)

Purpose:
- Provide complete filter options for Users list (role, plan, status).
- Values are loaded from lookup tables when available; if none exist, defaults are returned.

Response (200):
```json
{
  "roles": [
    { "label": "User", "value": "user" },
    { "label": "Admin", "value": "admin" },
    { "label": "Superuser", "value": "superuser" }
  ],
  "plans": [
    { "label": "Basic", "value": "basic" },
    { "label": "Company", "value": "company" },
    { "label": "Enterprise", "value": "enterprise" },
    { "label": "Team", "value": "team" }
  ],
  "statuses": [
    { "label": "Active", "value": "active" },
    { "label": "Inactive", "value": "inactive" },
    { "label": "Pending", "value": "pending" }
  ]
}
```

Rules:
- Return all possible values, not just those on the current page.
- Sort by `sort_order` then label (user-friendly order).
- Superuser accounts still receive all roles; frontend can hide options by permissions.

Errors:
- 401 Unauthorized (no valid token)
- 403 Forbidden (no access to Users list)
- 500 Server error
