# Roles and Permissions

This document summarizes what each role can do based on the current FastAPI routes.

## Roles

### user

- Auth: register, login, logout, forgot password, verify OTP, reset password.
- Products: list products, get product by ID, get product by SKU.
- Categories: list categories, get category by ID.

### admin

Includes everything a `user` can do, plus:

- Products: create, update, delete.
- Categories: create, update, delete.
- Users: list users.

### superuser

Includes everything an `admin` can do, plus:

- Admin management: create admins.
- Role management: update any user's role (user/admin/superuser).

## Notes

- `superuser` access is enforced via `is_superuser` and bypasses role checks in `require_roles`.
- Login returns `role = "superuser"` when `is_superuser` is true.
- Protected routes require `Authorization: Bearer <token>`.

## Endpoint Map (by role)

### Public or any authenticated user (no role check)

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/forgot-password`
- `POST /auth/otp/verify`
- `POST /auth/reset-password`
- `POST /auth/logout` (requires auth, no role check)
- `GET /products`
- `GET /products/{product_id}`
- `GET /products/sku/{sku}`
- `GET /categories`
- `GET /categories/{category_id}`

### admin (or superuser)

- `POST /products`
- `PUT /products/{product_id}`
- `DELETE /products/{product_id}`
- `POST /categories`
- `PUT /categories/{category_id}`
- `DELETE /categories/{category_id}`
- `GET /users`

### superuser only

- `POST /users/admins`
- `PUT /users/{user_id}/role`
