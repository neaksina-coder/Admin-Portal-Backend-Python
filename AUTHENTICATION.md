# Authentication API Guide

Base URL: `http://127.0.0.1:8000/api/v1`

This document describes the current authentication flow and required payloads/headers.

## Quick Start

- Run the backend: `python main.py` (starts on `http://127.0.0.1:8000`)
- Ensure your frontend origin is allowed by CORS in `main.py` (example: `http://localhost:5173`)

## Auth Endpoints

### Register

`POST /auth/register`

Body (JSON):
```json
{
  "email": "user@example.com",
  "username": "user1",
  "password": "StrongPass123",
  "privacy_policy_accepted": true
}
```

Success response:
```json
{
  "success": true,
  "status_code": 201,
  "message": "User created successfully",
  "user": { "id": 1, "email": "user@example.com", "username": "user1", "role": "user" }
}
```

### Login

`POST /auth/login`

Body (JSON):
```json
{
  "email": "user@example.com",
  "password": "StrongPass123"
}
```

Success response:
```json
{
  "success": true,
  "status_code": 200,
  "message": "Login successful",
  "token": "jwt_access_token",
  "user": { "id": 1, "email": "user@example.com", "username": "user1", "role": "user" }
}
```

Use the token for protected endpoints:
```
Authorization: Bearer <token>
```

### Logout

`POST /auth/logout`

Headers:
```
Authorization: Bearer <token>
```

Success response:
```json
{
  "success": true,
  "status_code": 200,
  "message": "Logged out successfully."
}
```

## Password Reset Flow (OTP + Reset Token)

### Step 1: Request OTP

`POST /auth/forgot-password`

Body (JSON):
```json
{
  "email": "user@example.com"
}
```

Response (always success):
```json
{
  "success": true,
  "status_code": 200,
  "message": "If the email exists, an OTP has been sent."
}
```

### Step 2: Verify OTP

`POST /auth/otp/verify`

Body (JSON):
```json
{
  "email": "user@example.com",
  "otp": "123456"
}
```

Success response:
```json
{
  "success": true,
  "status_code": 200,
  "message": "OTP verified successfully.",
  "reset_token": "temporary_reset_token"
}
```

### Step 3: Reset Password

`POST /auth/reset-password`

Headers:
```
X-Reset-Token: <reset_token>
```

Body (JSON):
```json
{
  "new_password": "NewStrongPass123",
  "confirm_password": "NewStrongPass123"
}
```

Success response:
```json
{
  "success": true,
  "status_code": 200,
  "message": "Password has been reset successfully."
}
```

## Roles and Access

Roles:
- `user`: default role for normal accounts
- `admin`: operational role
- `superuser`: full access

Notes:
- `admin` can access admin-only routes (products/categories CRUD, list users).
- `superuser` can create admins and update roles.

## Admin Management

### Create Admin (superuser only)

`POST /users/admins`

Headers:
```
Authorization: Bearer <superuser_token>
```

Body (JSON):
```json
{
  "email": "admin@example.com",
  "username": "admin1",
  "password": "AdminPass123",
  "privacy_policy_accepted": true
}
```

### Update User Role (superuser only)

`PUT /users/{user_id}/role`

Headers:
```
Authorization: Bearer <superuser_token>
```

Body (JSON):
```json
{
  "role": "admin"
}
```

## Environment (SMTP for OTP Email)

Required env vars:
```
EMAIL_FROM
SMTP_HOST
SMTP_PORT
SMTP_USER
SMTP_PASSWORD
SMTP_USE_TLS
```

Gmail example:
```
EMAIL_FROM=your_gmail@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_gmail@gmail.com
SMTP_PASSWORD=YOUR_APP_PASSWORD
SMTP_USE_TLS=true
```
