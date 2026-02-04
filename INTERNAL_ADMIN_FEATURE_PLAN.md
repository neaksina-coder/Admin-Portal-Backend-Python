# Internal Admin Roadmap — Detailed Implementation Plan

This document extends the current system with additional internal-admin features, aligned with AI_Business_Tools_Management_System.md. It is structured as phases, each with concrete build steps and manual tests. Use it to implement and validate one module at a time.

## Current Feature Baseline (Already Built)

- Auth + role checks (admin/superuser)
- Businesses + users.business_id
- Plans + features JSON
- Subscriptions (business?plan) with auto-plan update
- CRM (customers + contacts) + dashboard summary
- AI Insights (MVP)
- Sales/POS + Reports
- Marketing campaigns + email sending + email logs
- Promo codes

---

## Phase A — Billing & Admin Ops (High Priority)

### A1. Invoices / Billing History

Goal: Give internal admins a clear billing trail per business.

Build:
- Table: invoices
  - id, business_id, subscription_id, amount, currency
  - payment_status (pending/paid/failed/refunded)
  - payment_method, payment_date, due_date
  - metadata JSON
  - created_at
- Endpoints (admin-only):
  - POST /api/v1/invoices
  - GET /api/v1/invoices?businessId=
  - GET /api/v1/invoices/{id}
  - PUT /api/v1/invoices/{id}/status

Manual test:
1) Create invoice for a business
2) List invoices by businessId
3) Update status to paid
4) Verify invoice data returns correct status

### A2. Payment Monitoring

Goal: Admin visibility on failed/late payments.

Build:
- Report endpoint:
  - GET /api/v1/reports/payments?status=failed
  - GET /api/v1/reports/payments?status=overdue

Manual test:
1) Create invoice with status=failed
2) Fetch payment report (failed)
3) Create invoice with due_date < today and status=pending
4) Fetch payment report (overdue)

---

## Phase B — Admin Governance (Medium Priority)

### B1. Business Suspend / Unsuspend

Goal: Allow internal admin to pause access for problematic accounts.

Build:
- Add fields on businesses (if not already):
  - status (active/suspended)
  - suspended_at, suspended_reason
- Endpoints (admin-only):
  - PUT /api/v1/businesses/{id}/suspend
  - PUT /api/v1/businesses/{id}/unsuspend
- Enforce status at login or key endpoints

Manual test:
1) Suspend business
2) Try to access business endpoints (should fail)
3) Unsuspend business
4) Access restored

### B2. Audit Logs

Goal: track admin actions for accountability.

Build:
- Table: audit_logs
  - id, actor_user_id, action, target_type, target_id, metadata JSON, created_at
- Write logs when:
  - Business suspended/unsuspended
  - Plan changed
  - Subscription updated
  - Promo created

Manual test:
1) Perform an action (suspend or plan change)
2) Query audit log endpoint
3) Confirm log exists with correct metadata

---

## Phase C — AI Expansion (Optional Next)

### C1. AI Prediction Storage

Goal: store predictions separate from insights.

Build:
- Option A: reuse ai_insights with type = prediction
- Option B: create ai_predictions table

Endpoints (admin-only):
- POST /api/v1/ai-predictions
- GET /api/v1/ai-predictions?businessId=

Manual test:
1) Create prediction record
2) Fetch prediction by business

---

## Phase D — HR Module (Phase 2)

### D1. Employees CRUD

Build:
- Table: employees
  - id, business_id, name, role, attendance, performance_score
  - attrition_risk, performance_prediction

Endpoints (admin-only):
- POST /api/v1/employees
- GET /api/v1/employees?businessId=
- PUT /api/v1/employees/{id}
- DELETE /api/v1/employees/{id}

Manual test:
1) Create employee
2) List by business
3) Update employee
4) Delete employee

---

## Phase E — Reports Export

Goal: allow admin to export CSV/Excel from reports.

Build:
- Add export endpoints for sales/customers
  - GET /api/v1/reports/sales/export
  - GET /api/v1/reports/customers/export

Manual test:
1) Call export endpoint
2) Confirm file download and valid data

---

## Implementation Rules (Stay Consistent)

- All endpoints admin-only for now.
- Every new table must include business_id and created_at.
- Every module must have manual tests before moving on.
- Keep MVP logic simple; extend later.

---

## Recommended Next Step

Start with Phase A: Invoices/Billing. It connects directly to subscriptions and gives internal admin the most operational value.
