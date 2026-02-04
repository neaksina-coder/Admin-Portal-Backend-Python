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

## 15) Telegram Internal Alerts (Cross-Cutting)

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
