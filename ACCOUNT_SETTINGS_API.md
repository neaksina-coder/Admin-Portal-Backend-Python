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

## Notes

- `profileImage` in the response is a full URL you can open in the browser.
- Files are stored under `uploads/profile_images/` and served from `/uploads`.
*** End Patch}]} />
