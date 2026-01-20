# Authentication Features

This document outlines the authentication features, forms, and fields available in the application.

## Login Page (`login.vue`)

The login page allows users to sign in to their accounts.

### Form Fields

-   **Email:** The user's email address.
    -   Type: `email`
    -   Validation: `required`, `email`
-   **Password:** The user's password.
    -   Type: `password`
    -   Validation: `required`
-   **Remember Me:** A checkbox to keep the user logged in.
    -   Type: `checkbox`

### Actions

-   **Login:** A button to submit the login form.
-   **Forgot Password?:** A link to the "Forgot Password" page.
-   **Create an account:** A link to the "Registration" page.
-   **Social Logins:** The page includes a component for social media authentication (e.g., Google, Facebook).

## Registration Page (`register.vue`)

The registration page allows new users to create an account.

### Form Fields

-   **Username:** The user's desired username.
    -   Type: `text`
    -   Validation: `required`
-   **Email:** The user's email address.
    -   Type: `email`
    -   Validation: `required`, `email`
-   **Password:** The user's desired password.
    -   Type: `password`
    -   Validation: `required`
-   **Privacy Policy:** A checkbox to agree to the privacy policy and terms.
    -   Type: `checkbox`

### Actions

-   **Sign up:** A button to submit the registration form.
-   **Sign in instead:** A link to the "Login" page for users who already have an account.
-   **Social Logins:** The page includes a component for social media authentication.

## Forgot Password Page (`forgot-password.vue`)

This page allows users who have forgotten their password to request a password reset link.

### Form Fields

-   **Email:** The user's email address.
    -   Type: `email`
    -   Validation: `required`, `email`

### Actions

-   **Send Reset Link:** A button to submit the form and send a password reset link to the user's email.
-   **Back to login:** A link to return to the "Login" page.

## Other Authentication Pages

### `access-control.vue`

This page is not a form but a demonstration of role-based access control. It shows different content based on the user's role (e.g., 'admin' or 'user').

### `not-authorized.vue`

This is an informational page displayed to users who try to access a page or resource for which they do not have the necessary permissions. It displays a "401 - Not Authorized" error message.
