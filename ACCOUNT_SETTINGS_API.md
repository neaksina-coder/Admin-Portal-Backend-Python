# Account Settings API

This document defines the endpoints used for the Account Settings page (current user only).

## Access

- Auth required.
- Admin and Superuser only.
- Endpoint uses the **current logged-in user**; no user ID in path.

## Get Account Settings

`GET /users/me`

Response:
```json
{
  "id": 1,
  "fullName": "SuperAdmin",
  "email": "neaksina414@gmail.com",
  "role": "superuser",
  "isSuperuser": true,
  "profile": {
    "company": "PNC",
    "country": "Cambodia",
    "contact": "0969780938",
    "profileImage": "http://127.0.0.1:8000/uploads/profile_images/abcd1234.jpg"
  }
}
```

## Update Account Settings (with image upload)

`PUT /users/me`

Content-Type: `multipart/form-data`

Form fields:
- `fullName` (string, optional)
- `email` (string, optional)
- `company` (string, optional)
- `country` (string, optional)
- `contact` (string, optional)
- `profileImage` (file, optional)

Example form-data:
```
fullName=SuperAdmin
email=neaksina414@gmail.com
company=PNC
country=Cambodia
contact=0969780938
profileImage=@photo.jpg
```

Response:
```json
{
  "id": 1,
  "fullName": "SuperAdmin",
  "email": "neaksina414@gmail.com",
  "role": "superuser",
  "isSuperuser": true,
  "profile": {
    "company": "PNC",
    "country": "Cambodia",
    "contact": "0969780938",
    "profileImage": "http://127.0.0.1:8000/uploads/profile_images/abcd1234.jpg"
  }
}
```

## Update Password

`PUT /users/me/password`

Body (JSON):
```json
{
  "currentPassword": "OldPass123",
  "newPassword": "NewPass123",
  "confirmPassword": "NewPass123"
}
```

Password rules:
- Minimum 8 characters
- At least one lowercase letter
- At least one uppercase letter
- At least one number, symbol, or whitespace

Error messages (examples):
- Missing lowercase: `Password must include at least one lowercase letter`
- Missing uppercase: `Password must include at least one uppercase letter`
- Missing number/symbol/whitespace: `Password must include at least one number, symbol, or whitespace`
- Wrong current password: `Current password is incorrect`
- Mismatch: `Passwords do not match`

Response:
```json
{
  "success": true,
  "message": "Password updated successfully"
}
```

## Two-Factor Authentication (2FA)

### Get 2FA Status

`GET /users/me/2fa`

Response:
```json
{
  "enabled": false,
  "method": null,
  "smsPhone": null,
  "smsVerified": false
}
```

### Select 2FA Method

`POST /users/me/2fa/method`

Body:
```json
{ "method": "authenticator" }
```

Response: same as status.

### Authenticator App Setup

`POST /users/me/2fa/authenticator/setup`

Response:
```json
{
  "secret": "BASE32SECRET",
  "otpauthUrl": "otpauth://totp/Sina%20Neak:email@example.com?secret=BASE32SECRET&issuer=Sina%20Neak"
}
```

### Authenticator App Verify

`POST /users/me/2fa/authenticator/verify`

Body:
```json
{ "code": "123456" }
```

Response: same as status.

### SMS Start

`POST /users/me/2fa/sms/start`

Body:
```json
{ "phone": "+11234567890" }
```

Response: same as status.

### SMS Verify

`POST /users/me/2fa/sms/verify`

Body:
```json
{ "code": "123456" }
```

Response: same as status.

Notes:
- SMS sending is not integrated yet; only code validation is implemented.

## Notes

- `profileImage` in the response is a full URL you can open in the browser.
- Files are stored under `uploads/profile_images/` and served from `/uploads`.
*** End Patch}]} />
