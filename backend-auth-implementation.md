
# Backend Authentication Implementation (Python)

This document outlines the backend implementation details for the authentication features, based on the frontend requirements documented in `auth-features.md`.

## 1. Login Endpoint

### Endpoint Details

-   **URL:** `/auth/login`
-   **Method:** `POST`
-   **Description:** Authenticates a user and returns a token.

### Request Body

```json
{
    "email": "user@example.com",
    "password": "user_password"
}
```

### Success Response (200 OK)

```json
{
    "token": "your_jwt_token",
    "user": {
        "id": 1,
        "username": "example_user",
        "email": "user@example.com",
        "role": "user"
    }
}
```

### Error Responses

-   **401 Unauthorized:** Invalid credentials.
-   **422 Unprocessable Entity:** Missing or invalid fields.

### Implementation Notes

1.  **Receive Request:** Get the `email` and `password` from the request body.
2.  **Validate Input:** Ensure both fields are present and the email is in a valid format.
3.  **Find User:** Query the database for a user with the given email.
4.  **Verify Password:** If the user exists, compare the provided password with the hashed password in the database.
5.  **Generate Token:** If the password is correct, generate a JSON Web Token (JWT) with the user's ID and role.
6.  **Return Response:** Send the token and user data in the response.

## 2. Registration Endpoint

### Endpoint Details

-   **URL:** `/auth/register`
-   **Method:** `POST`
-   **Description:** Creates a new user account.

### Request Body

```json
{
    "username": "new_user",
    "email": "new_user@example.com",
    "password": "strong_password"
}
```

### Success Response (201 Created)

```json
{
    "message": "User created successfully",
    "user": {
        "id": 2,
        "username": "new_user",
        "email": "new_user@example.com"
    }
}
```

### Error Responses

-   **409 Conflict:** An account with the same email or username already exists.
-   **422 Unprocessable Entity:** Missing or invalid fields (e.g., weak password).

### Implementation Notes

1.  **Receive Request:** Get `username`, `email`, and `password` from the request body.
2.  **Validate Input:** Ensure all fields are present, the email is valid, and the password meets security requirements.
3.  **Check for Existing User:** Query the database to ensure no user with the same email or username exists.
4.  **Hash Password:** Hash the password using a strong algorithm like bcrypt.
5.  **Create User:** Save the new user to the database with the hashed password.
6.  **Return Response:** Confirm that the user was created.

## 3. Forgot Password Endpoint

### Endpoint Details

-   **URL:** `/auth/forgot-password`
-   **Method:** `POST`
-   **Description:** Sends a password reset link to the user's email.

### Request Body

```json
{
    "email": "user@example.com"
}
```

### Success Response (200 OK)

```json
{
    "message": "Password reset link sent successfully."
}
```

### Error Responses

-   **404 Not Found:** No user with the given email address was found.
-   **422 Unprocessable Entity:** Missing or invalid email field.

### Implementation Notes

1.  **Receive Request:** Get the `email` from the request body.
2.  **Validate Input:** Ensure the email field is present and valid.
3.  **Find User:** Query the database for a user with the given email.
4.  **Generate Reset Token:** Create a temporary, secure token for password reset (e.g., a short-lived JWT).
5.  **Send Email:** Email a link containing the reset token to the user. The link should point to a frontend page that can handle the token.
6.  **Return Response:** Confirm that the email has been sent.

## 4. Reset Password Endpoint

### Endpoint Details

-   **URL:** `/auth/reset-password`
-   **Method:** `POST`
-   **Description:** Resets the user's password using a reset token.

### Request Body

```json
{
    "token": "reset_token_from_email",
    "new_password": "new_strong_password"
}
```

### Success Response (200 OK)

```json
{
    "message": "Password has been reset successfully."
}
```

### Error Responses

-   **401 Unauthorized:** Invalid or expired token.
-   **422 Unprocessable Entity:** Missing fields or weak new password.

### Implementation Notes

1.  **Receive Request:** Get the `token` and `new_password` from the request body.
2.  **Validate Token:** Decode and verify the reset token. Check for expiration.
3.  **Find User:** Identify the user from the token's payload.
4.  **Hash New Password:** Hash the `new_password`.
5.  **Update Password:** Update the user's password in the database.
6.  **Invalidate Token:** Ensure the reset token cannot be used again.
7.  **Return Response:** Confirm the password has been reset.
