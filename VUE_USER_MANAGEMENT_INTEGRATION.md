# Vue.js User Management Integration Guide

This document shows how to integrate the User Management API into a Vue.js frontend.

## Base URL

Set your API base URL in an environment variable:

```
VITE_API_BASE_URL=http://localhost:8000
```

## Auth (token)

All endpoints below require a Bearer token:

```
Authorization: Bearer <token>
```

## Endpoints

### List users

`GET /users`

Query params:
- `q`
- `role` (`user` | `admin`)
- `plan`
- `status`
- `page`
- `itemsPerPage`
- `sortBy` (`user` | `email` | `role` | `plan` | `status` | `billing`)
- `orderBy` (`asc` | `desc`)

### Get user detail

`GET /users/{id}`

### Create user (admin or superuser)

`POST /users`

Body:
```
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

### Update user

`PUT /users/{id}`

Body:
```
{
  "fullName": "Jane A. Doe",
  "plan": "enterprise",
  "billing": "Manual-Credit Card",
  "status": "active",
  "company": "Acme",
  "country": "USA",
  "contact": "+1 234 567 890"
}
```

### Delete user

`DELETE /users/{id}`

### Role update (superuser only)

`PUT /users/{id}/role`

Body:
```
{ "role": "admin" }
```

## Vue.js Example (fetch)

Create a small API helper:

```
// src/api/userManagement.js
const API_BASE = import.meta.env.VITE_API_BASE_URL;

function authHeader(token) {
  return { Authorization: `Bearer ${token}` };
}

export async function listUsers(token, params = {}) {
  const url = new URL(`${API_BASE}/users`);
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== "") url.searchParams.set(k, v);
  });
  const res = await fetch(url.toString(), {
    headers: { ...authHeader(token) },
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getUser(token, id) {
  const res = await fetch(`${API_BASE}/users/${id}`, {
    headers: { ...authHeader(token) },
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function createUser(token, payload) {
  const res = await fetch(`${API_BASE}/users`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeader(token) },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function updateUser(token, id, payload) {
  const res = await fetch(`${API_BASE}/users/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", ...authHeader(token) },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function deleteUser(token, id) {
  const res = await fetch(`${API_BASE}/users/${id}`, {
    method: "DELETE",
    headers: { ...authHeader(token) },
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function updateUserRole(token, id, role) {
  const res = await fetch(`${API_BASE}/users/${id}/role`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", ...authHeader(token) },
    body: JSON.stringify({ role }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
```

## Vue.js Example (component usage)

```
<script setup>
import { ref, onMounted } from "vue";
import { listUsers, createUser } from "@/api/userManagement";

const token = ref("YOUR_JWT_TOKEN");
const users = ref([]);
const totalUsers = ref(0);

onMounted(async () => {
  const data = await listUsers(token.value, { page: 1, itemsPerPage: 10 });
  users.value = data.users;
  totalUsers.value = data.totalUsers;
});

async function onCreateUser() {
  await createUser(token.value, {
    fullName: "Jane Doe",
    email: "jane@example.com",
    password: "StrongPass123",
    role: "user",
    plan: "team",
    billing: "Manual-PayPal",
    status: "active",
  });
}
</script>
```

## Notes

- Admins can only manage `user` accounts. Superusers can manage all users.
- If you see 403, check role/permissions.
