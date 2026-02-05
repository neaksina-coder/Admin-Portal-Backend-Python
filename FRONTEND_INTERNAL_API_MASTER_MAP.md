# Frontend Internal API Master Map

This document combines:
1) Feature/Endpoint map
2) Field-level DB and JSON mapping

---

## Part A - Feature and Endpoint Map

# Frontend API Feature Map (Internal Admin Portal)

Base URL: `/api/v1`

Scope now: internal team (`admin`, `superuser`).

## 1) Auth

Feature: Authentication and account recovery.

- `POST /auth/register` - Register user
- `POST /auth/login` - Login
- `POST /auth/logout` - Logout
- `POST /auth/forgot-password` - Request reset/OTP
- `POST /auth/otp/verify` - Verify OTP
- `POST /auth/reset-password` - Reset password

---

## 2) Users / Roles

Feature: Internal user management.

- `GET /users/` - List users (search/filter/pagination)
- `GET /users/filters` - Role/plan/status filter options
- `GET /users/me` - Current admin profile
- `PUT /users/me` - Update current admin profile
- `PUT /users/me/password` - Change current admin password
- `GET /users/{user_id}` - User detail
- `POST /users/` - Create user
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user
- `POST /users/admins` - Create admin (superuser only)
- `POST /users/superusers` - Create superuser (superuser only)
- `PUT /users/{user_id}/role` - Change role (superuser only)

---

## 3) Businesses

Feature: Tenant/business management.

- `POST /businesses/` - Create business
- `GET /businesses/` - List businesses
- `GET /businesses/{business_id}` - Business detail
- `PUT /businesses/{business_id}/suspend` - Suspend business
- `PUT /businesses/{business_id}/unsuspend` - Unsuspend business

Sub-feature output fields for frontend state:
- `status`
- `suspendedAt`
- `suspendedReason`
- `plan` object (`id`, `name`)

---

## 4) Plans

Feature: Pricing/feature packages.

- `POST /plans/` - Create plan
- `GET /plans/` - List plans (supports filters, e.g. name)
- `GET /plans/{plan_id}` - Plan detail

---

## 5) Subscriptions

Feature: Business subscription lifecycle.

- `POST /subscriptions/` - Create subscription (stored as `pending` in current flow)
- `GET /subscriptions/` - List subscriptions
- `GET /subscriptions/{subscription_id}` - Subscription detail

Sub-feature endpoint:
- `GET /subscriptions/{subscription_id}/events` - Subscription history timeline

Current lifecycle:
1. Create subscription -> `pending`
2. Auto-create invoice -> `pending`
3. Invoice marked paid -> subscription auto `active`, business `plan_id` updated

---

## 6) Invoices / Billing

Feature: Billing history + manual payment status operations.

- `POST /invoices/` - Create invoice
- `GET /invoices/` - List invoices (supports `businessId`, pagination)
- `GET /invoices/{invoice_id}` - Invoice detail
- `PUT /invoices/{invoice_id}/status` - Update payment status

Sub-feature behavior:
- When status changes to `paid`, system auto-activates linked subscription and updates business plan.

---

## 7) CRM Customers

Feature: Customer management per business.

- `POST /customers/` - Create customer
- `GET /customers/` - List customers (by business, filters)
- `GET /customers/{customer_id}` - Customer detail
- `PUT /customers/{customer_id}` - Update customer
- `DELETE /customers/{customer_id}` - Delete customer

Sub-feature endpoints (contact history):
- `POST /customers/{customer_id}/contacts` - Add contact history record
- `GET /customers/{customer_id}/contacts` - List contact history records

---

## 8) Dashboard

Feature: CRM dashboard summary.

- `GET /dashboard/crm` - CRM summary KPIs by business

---

## 9) AI Insights

Feature: Store/retrieve AI insight records.

- `POST /ai-insights/` - Create insight
- `GET /ai-insights/` - List insights by business
- `GET /ai-insights/{insight_id}` - Insight detail

---

## 10) Sales / POS

Feature: Sales transaction records.

- `POST /sales/` - Create sale
- `GET /sales/` - List sales by business/date
- `GET /sales/{sale_id}` - Sale detail

---

## 11) Marketing Campaigns

Feature: Campaign CRUD + send + logs.

- `POST /marketing/` - Create campaign
- `GET /marketing/` - List campaigns
- `GET /marketing/{campaign_id}` - Campaign detail
- `PUT /marketing/{campaign_id}` - Update campaign
- `DELETE /marketing/{campaign_id}` - Delete campaign

Sub-feature endpoints:
- `POST /marketing/{campaign_id}/send` - Send campaign (email)
- `GET /marketing/{campaign_id}/logs` - Delivery logs

---

## 12) Promo Codes

Feature: Discount code management and validation.

- `POST /promos/` - Create promo code
- `GET /promos/` - List promo codes by business
- `GET /promos/{promo_id}` - Promo detail
- `PUT /promos/{promo_id}` - Update promo
- `DELETE /promos/{promo_id}` - Delete promo

Sub-feature endpoint:
- `POST /promos/apply` - Validate/apply promo to amount

---

## 13) Reports

Feature: Operational reporting.

- `GET /reports/sales/summary` - Sales summary
- `GET /reports/customers/summary` - Customer summary
- `GET /reports/payments` - Payment monitoring report

Sub-feature filters on payments report:
- `status=pending|paid|failed|refunded|overdue`
- `businessId`
- `skip`, `limit`

---

## 14) Audit Logs

Feature: Internal accountability trail.

- `GET /audit-logs/` - List audit logs

Sub-feature filters:
- `businessId`
- `actorUserId`
- `action`
- `startDate`, `endDate`
- `skip`, `limit`

---

## 15) Admin Digest (AI Summary)

Feature: Daily AI summary for internal admins.

- `GET /admin-digest/latest` - Latest daily summary (stored snapshot)

Notes:
- Generated daily at 6:00 AM (Asia/Phnom_Penh).
- Uses internal data: businesses, invoices, subscriptions, audit logs.
- Frontend should display `summaryText` and the top 5 `topItems`.

---

## 16) Telegram Internal Alerts (Cross-Cutting)

Feature: Internal real-time event alerts.

Triggered from current modules:
- business created/suspended/unsuspended
- subscription created
- invoice created/status updated

Config used by backend:
- `TELEGRAM_ALERTS_ENABLED`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_IDS`

---

## Frontend Implementation Notes

- All admin endpoints require Bearer token.
- Keep a shared API client with automatic token injection.
- Use module-based navigation in Vue:
  - Users, Businesses, Plans, Subscriptions, Invoices, CRM, Sales, Marketing, Reports, Audit Logs.
- For subscription/invoice UI, model lifecycle explicitly:
  - `pending subscription` -> `pending invoice` -> `paid invoice` -> `active subscription`.


---

## Part B - Field-Level Integration Map

# Frontend Integration Field Map (DB + JSON)

Base URL: `/api/v1`

This file focuses on field-level integration: DB columns and API JSON keys.

---

## 1) Businesses

### DB Table: `businesses`
- `id`
- `name`
- `tenant_id`
- `plan_id`
- `status`
- `suspended_at`
- `suspended_reason`
- `created_at`
- `updated_at`

### API Response Shape
```json
{
  "id": 2,
  "name": "ERP-ORG",
  "tenantId": "ero-org",
  "planId": 3,
  "plan": { "id": 3, "name": "Enterprise" },
  "status": "active",
  "suspendedAt": null,
  "suspendedReason": null,
  "timestamps": {
    "created": "2026-02-04T07:58:23.316084",
    "updated": "2026-02-04T08:10:10.000000"
  }
}
```

---

## 2) Plans

### DB Table: `plans`
- `id`
- `plan_name`
- `price`
- `features` (JSONB)
- `created_at`
- `updated_at`

### API Response Shape
```json
{
  "id": 3,
  "planName": "Enterprise",
  "price": 99.99,
  "features": {
    "crm": true,
    "aiInsight": true,
    "aiPrediction": true,
    "maxUsers": "unlimited"
  },
  "created_at": "2026-02-02T09:22:57.758060",
  "updated_at": "2026-02-02T09:22:57.758062"
}
```

---

## 3) Subscriptions

### DB Table: `subscriptions`
- `id`
- `business_id`
- `plan_id`
- `start_date`
- `end_date`
- `status` (`pending|active|inactive`)
- `billing_history` (legacy JSONB)
- `created_at`

### API Request (Create)
```json
{
  "businessId": 2,
  "planId": 3,
  "startDate": "2026-02-04",
  "endDate": null
}
```

### API Response Shape
```json
{
  "id": 12,
  "businessId": 2,
  "planId": 3,
  "startDate": "2026-02-04",
  "endDate": null,
  "status": "pending",
  "billingHistory": null,
  "created_at": "2026-02-04T08:30:00.000000"
}
```

---

## 4) Subscription Events (History)

### DB Table: `subscription_events`
- `id`
- `subscription_id`
- `business_id`
- `invoice_id`
- `actor_user_id`
- `event_type`
- `payload` (JSONB)
- `created_at`

### API Response Shape
```json
{
  "id": 18,
  "subscriptionId": 12,
  "businessId": 2,
  "invoiceId": 9,
  "actorUserId": 1,
  "eventType": "subscription_activated",
  "payload": {
    "reason": "invoice_paid",
    "planId": 3,
    "previousPlanId": 2
  },
  "created_at": "2026-02-04T08:40:12.000000"
}
```

---

## 5) Invoices

### DB Table: `invoices`
- `id`
- `business_id`
- `subscription_id`
- `amount`
- `currency`
- `payment_status` (`pending|paid|failed|refunded`)
- `payment_method`
- `due_date`
- `payment_date`
- `metadata` (JSONB)
- `created_at`

### API Request (Update Status)
```json
{
  "paymentStatus": "paid",
  "paymentMethod": "bank_transfer",
  "paymentDate": "2026-02-04"
}
```

### API Response Shape
```json
{
  "id": 9,
  "businessId": 2,
  "subscriptionId": 12,
  "amount": 99.99,
  "currency": "USD",
  "paymentStatus": "paid",
  "paymentMethod": "bank_transfer",
  "dueDate": "2026-02-11",
  "paymentDate": "2026-02-04",
  "metadata": {
    "source": "subscription_create",
    "planId": 3,
    "subscriptionId": 12
  },
  "created_at": "2026-02-04T08:30:00.000000"
}
```

---

## 6) Customers (CRM)

### DB Table: `customers`
- `id`
- `business_id`
- `name`
- `email`
- `phone`
- `segment`
- `notes`
- `churn_risk_score`
- `lifetime_value`
- `next_best_product`
- `created_at`
- `updated_at`

### API Response Shape
```json
{
  "id": 1,
  "businessId": 2,
  "name": "Jane Doe",
  "email": "jane@example.com",
  "phone": "+1 222 333 4444",
  "segment": "vip",
  "notes": "First client",
  "churnRiskScore": 0.2,
  "lifetimeValue": 1200.5,
  "nextBestProduct": "Analytics Pro",
  "created_at": "2026-02-03T02:12:14.111576",
  "updated_at": "2026-02-03T02:12:14.111580"
}
```

---

## 7) Customer Contacts

### DB Table: `customer_contacts`
- `id`
- `business_id`
- `customer_id`
- `channel`
- `summary`
- `contacted_at`
- `created_at`

### API Response Shape
```json
{
  "id": 4,
  "businessId": 2,
  "customerId": 1,
  "channel": "email",
  "summary": "Follow-up sent",
  "contactedAt": "2026-02-04T09:00:00",
  "created_at": "2026-02-04T09:00:01"
}
```

---

## 8) Sales

### DB Table: `sales`
- `id`
- `customer_id`
- `business_id`
- `quantity`
- `total_price`
- `original_amount`
- `discount_amount`
- `promo_code_id`
- `transaction_date`
- `invoice_number`
- `demand_prediction`
- `anomaly_flag`
- `created_at`

### API Response Shape
```json
{
  "id": 11,
  "customerId": 1,
  "businessId": 2,
  "quantity": 1,
  "originalAmount": 100,
  "discountAmount": 20,
  "totalPrice": 80,
  "promoCodeId": 2,
  "transactionDate": "2026-02-04T12:00:00",
  "invoiceNumber": "INV-1770089932",
  "created_at": "2026-02-04T12:00:01"
}
```

---

## 9) Promo Codes

### DB Table: `promo_codes`
- `id`
- `business_id`
- `code`
- `discount_type`
- `discount_value`
- `start_date`
- `end_date`
- `usage_limit`
- `used_count`
- `is_active`
- `created_at`

### API Response Shape
```json
{
  "id": 7,
  "businessId": 2,
  "code": "CNY-100",
  "discountType": "percent",
  "discountValue": 20,
  "startDate": "2026-02-04T00:00:00",
  "endDate": "2026-02-20T23:59:59",
  "usageLimit": 100,
  "usedCount": 0,
  "isActive": true,
  "created_at": "2026-02-04T03:48:39.333752"
}
```

### Promo Apply Response
```json
{
  "originalAmount": 100,
  "discountAmount": 20,
  "finalAmount": 80,
  "promoCodeId": 7
}
```

---

## 10) Marketing Campaigns

### DB Table: `marketing_campaigns`
- `id`
- `business_id`
- `name`
- `target_segment`
- `start_date`
- `end_date`
- `performance_metrics` (JSONB)
- `best_time_to_send`
- `content_suggestions` (JSONB)
- `channel`
- `ab_variant` (JSONB)
- `created_at`

### API Response Shape
```json
{
  "id": 3,
  "businessId": 2,
  "name": "Test Email Campaign",
  "targetSegment": "vip",
  "startDate": "2026-02-03T00:00:00",
  "endDate": "2026-02-04T00:00:00",
  "channel": "email",
  "performanceMetrics": { "sent": 1 },
  "created_at": "2026-02-03T09:22:55.117362"
}
```

---

## 11) Marketing Email Logs

### DB Table: `marketing_email_logs`
- `id`
- `campaign_id`
- `business_id`
- `recipient_email`
- `subject`
- `status`
- `error_message`
- `created_at`

### API Response Shape
```json
{
  "id": 14,
  "campaignId": 3,
  "businessId": 2,
  "recipientEmail": "client@example.com",
  "subject": "CNY Promotion",
  "status": "sent",
  "errorMessage": null,
  "created_at": "2026-02-04T10:20:00"
}
```

---

## 12) AI Insights

### DB Table: `ai_insights`
- `id`
- `business_id`
- `type`
- `input_data` (JSONB)
- `output_data` (JSONB)
- `created_at`

### API Response Shape
```json
{
  "id": 5,
  "businessId": 2,
  "type": "insight",
  "inputData": { "source": "subscription", "planId": 3 },
  "outputData": { "summary": "AI insights enabled for this plan." },
  "created_at": "2026-02-04T07:30:00"
}
```

---

## 13) Reports

### Sales Summary Response
```json
{
  "totalRevenue": 1200.5,
  "totalSales": 18
}
```

### Customers Summary Response
```json
{
  "totalCustomers": 42
}
```

### Payments Report Item
```json
{
  "id": 9,
  "businessId": 2,
  "subscriptionId": 12,
  "amount": 99.99,
  "currency": "USD",
  "paymentStatus": "pending",
  "paymentMethod": null,
  "dueDate": "2026-02-11",
  "paymentDate": null,
  "metadata": {
    "source": "subscription_create"
  },
  "created_at": "2026-02-04T08:30:00"
}
```

---

## 14) Audit Logs

### DB Table: `audit_logs`
- `id`
- `business_id`
- `actor_user_id`
- `action`
- `target_type`
- `target_id`
- `metadata` (JSONB)
- `created_at`

### API Response Shape
```json
{
  "id": 21,
  "businessId": 2,
  "actorUserId": 1,
  "action": "invoice_status_updated",
  "targetType": "invoice",
  "targetId": 9,
  "metadata": {
    "previousStatus": "pending",
    "newStatus": "paid"
  },
  "created_at": "2026-02-04T08:45:00"
}
```

---

## 15) Admin Digest (AI Summary)

### DB Table: `admin_digests`
- `id`
- `range_type` (`daily`)
- `summary_text`
- `top_items` (JSONB)
- `stats` (JSONB)
- `generated_at`
- `generated_by` (`system|user`)

### API Response Shape (`GET /admin-digest/latest`)
```json
{
  "range": "daily",
  "summaryText": "Daily operations are stable with no overdue invoices or failed payments. One new business was registered today.",
  "topItems": [
    {
      "type": "business",
      "id": "newBusinesses",
      "label": "New Businesses",
      "reason": "One new business was registered today.",
      "priority": "low"
    }
  ],
  "stats": {
    "newBusinesses": 1,
    "overdueInvoices": 0,
    "failedInvoices": 0,
    "subscriptionsPending": 0,
    "suspensions": 0,
    "roleChanges": 0
  },
  "generatedAt": "2026-02-05T06:00:00"
}
```

---

## Field Naming Convention for Frontend

- DB uses snake_case.
- API payloads use camelCase aliases for frontend (`businessId`, `paymentStatus`, etc.).
- Keep frontend types aligned to API JSON, not DB column names.

