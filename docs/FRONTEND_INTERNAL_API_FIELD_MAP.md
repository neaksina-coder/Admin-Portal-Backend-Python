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
