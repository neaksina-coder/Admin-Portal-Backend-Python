# Contact Inquiries (Public Website → Admin Inbox)

This feature lets any public website visitor submit a contact inquiry that appears in the internal admin inbox. Admins can review, assign, update status, and reply. This is **not** an email campaign feature.

## Goal
- Capture inbound inquiries from the public site.
- Route them to the internal admin team for reply and tracking.

## Flow
1. Visitor submits the public contact form.
2. Backend validates and stores the inquiry.
3. Inquiry appears in the admin inbox UI.
4. Admin assigns status and replies.
5. Customer receives reply from the business email.

## Public API

### Submit Inquiry (No Auth)
`POST /api/v1/public/contact-inquiries`

Body:
```json
{
  "businessId": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+123456789",
  "company": "Acme Co",
  "serviceInterest": "Website + SEO",
  "subject": "Need a quote",
  "message": "Please contact me about pricing."
}
```

## Admin API (Auth Required)

### List Inquiries
`GET /api/v1/contact-inquiries?businessId=1&status=new&q=acme&skip=0&limit=100`

### Inquiry Detail
`GET /api/v1/contact-inquiries/{inquiry_id}`

### Update Status/Assignee
`PUT /api/v1/contact-inquiries/{inquiry_id}`
```json
{
  "status": "in_progress",
  "assignedToUserId": 2
}
```

### Reply to Customer
`POST /api/v1/contact-inquiries/{inquiry_id}/reply`
```json
{
  "subject": "Thanks for contacting us",
  "body": "Hi John, thanks for reaching out. Here is our pricing..."
}
```

## Data Model
Stored in `contact_inquiries`:
- `business_id`
- `name`, `email`, `phone`, `company`
- `service_interest`, `subject`, `message`
- `status` (`new`, `in_progress`, `replied`, `closed`)
- `assigned_to_user_id`
- `source` (default `public_web`)
- `created_at`, `updated_at`, `replied_at`

## Email Configuration
Required for replies:
- `EMAIL_FROM`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASSWORD`
- `SMTP_USE_TLS`

Optional internal alert for new inquiries:
- `ADMIN_INBOX_EMAILS` (comma-separated)

## Not Included (Not a Campaign)
- Bulk sending
- Segmentation
- Automated sequences
