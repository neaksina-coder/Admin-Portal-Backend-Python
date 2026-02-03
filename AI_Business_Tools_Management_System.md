# AI Business Tools Management System

## 1. System Overview (Technical View)

**System Type:**  
Cloud SaaS Business Management Platform with AI Analytics

**Main Capabilities:**  
- Multi-tenant (many companies use the same system)  
- Subscription-based access control  
- AI-powered analytics and prediction  
- Role-based system access  

---

## 2. Functional Requirement Analysis

### 2.1 Authentication & Access System

**Features:**  
- User Registration  
- User Login / Logout  
- Password Reset  
- JWT Token Authentication  
- Role-Based Access Control  

**Roles and Access:**  

| Role             | Access                  |
|-----------------|------------------------|
| Public          | Website only           |
| Customer Owner  | Full business access   |
| Customer Staff  | Limited business access|
| Admin           | Full system control    |
| Support         | Read + assist access   |

---

## 3. Customer Portal — Feature Analysis

### 3.1 Dashboard Module

**Purpose:** Show business overview + AI insights

**Features:**  
- Today sales summary  
- Revenue chart  
- Customer growth chart  
- AI insight card  
- Alert notifications  

**Data Source:**  
- Sales table  
- Customer table  
- AI insight table  

### 3.2 CRM Module

**Features:**  
- Customer CRUD  
- Customer segmentation  
- Contact history  
- Customer notes  

**AI Features:**  
- Churn risk score  
- Customer lifetime value estimate  
- Next best product suggestion  

### 3.3 Sales / POS Module

**Features:**  
- Sales transaction record  
- Product sales tracking  
- Invoice generation  
- Sales history  

**AI Features:**  
- Best selling product detection  
- Sales anomaly detection  
- Demand prediction  

### 3.4 Marketing Module

**Features:**  
- Campaign management  
- Customer targeting  
- Campaign performance tracking  

**AI Features:**  
- Best campaign time prediction  
- Audience segmentation  
- Content suggestion  

### 3.5 HR Module (Optional Phase 2)

**Features:**  
- Employee management  
- Attendance tracking  
- Performance tracking  

**AI Features:**  
- Performance prediction  
- Attrition risk detection  

### 3.6 Reports & Analytics Module

**Features:**  
- Sales reports  
- Customer reports  
- Marketing reports  
- Export reports  

**AI Features:**  
- Trend explanation  
- Forecast summary  
- Risk alerts  

### 3.7 Subscription Module

**Features:**  
- Current plan view  
- Upgrade / downgrade  
- Billing history  
- Payment method management  

---

## 4. AI Engine — Feature Analysis

**Level 1 — AI Insight (MVP)**  
- Input: Sales data, Customer data  
- Output: Text insight, Trend summary  

**Level 2 — AI Prediction**  
- Models: Sales Forecast, Churn Prediction, Demand Forecast  

**Level 3 — AI Automation (Future)**  
- Smart notification  
- Auto marketing trigger  
- Smart recommendation engine  

---

## 5. Admin Portal — Feature Analysis

**User Management:**  
- View users  
- Activate / deactivate  
- Reset password  
- Assign role  

**Business Management:**  
- View businesses  
- Suspend account  
- View subscription status  

**Pricing & Plan Management:**  
- Create plan  
- Edit plan features  
- Set usage limits  

**Payment Monitoring:**  
- Payment logs  
- Failed payments  
- Refund management  

**AI Monitoring:**  
- AI usage per company  
- AI cost tracking  
- AI performance logs  

**Revenue Dashboard:**  
- Monthly revenue  
- Active subscription count  
- Churn rate  

---

## 6. Pricing & Feature Access Logic

**Feature Access Rule:**  
`User → Subscription → Plan → Feature Access → System Module`

**Example:**  

| Plan       | CRM | AI Insight | AI Prediction |
|-----------|-----|-----------|---------------|
| Basic     | ✔   | ✔         | ❌            |
| Pro       | ✔   | ✔         | ✔             |

---

## 7. Data Architecture Analysis

**Core Entities:**  
- Users: Login + Role  
- Businesses: Company tenant  
- Plans: Pricing tiers  
- Subscriptions: Active user plan  
- Customers: CRM data  
- Sales: Transaction data  
- AI Insights: Generated results  

---

## 8. Security Architecture

**Authentication:** JWT Token  
**Authorization:** Role + Permission system  

**Data Security:**  
- HTTPS  
- Password hashing  
- Token expiration  

---

## 9. Technical Architecture

**Frontend:** Vue 3, Pinia, Tailwind  
**Backend:** Python FastAPI, PostgreSQL, Redis  

**AI Layer:**  
- Phase 1: AI API Integration  
- Phase 2: Custom ML Models  

---

## 10. Development Priority (Build Order)

**Phase 1 (MVP):**  
- Auth system  
- Subscription system  
- Dashboard  
- CRM basic  
- AI insight (API based)  

**Phase 2:**  
- Sales module  
- Reports  
- AI prediction  

**Phase 3:**  
- Marketing module  
- HR module  
- AI automation  

---

## 11. Risk & Complexity Analysis

| Complexity       | Modules / Features                       |
|-----------------|----------------------------------------|
| High            | AI prediction models, Subscription billing logic, Multi-tenant security |
| Medium          | Role permission system, Reporting system |
| Low             | Dashboard UI, CRUD modules              |

---

## 12. MVP Definition

**MVP Must Have:**  
- Login system  
- Business account  
- CRM basic  
- Dashboard  
- Subscription payment  
- AI insight summary  

---

# Implementation Plan (Build One-by-One, Test Each Step)

Use this checklist to implement features in order. Do not move to the next step until the current step is tested and confirmed.

## Phase 1 (MVP)

### Step 1 — Business / Tenant
Goal: create the business entity and link users to a business.

Build:
- Table: `businesses`
- Add `business_id` on `users`
- Role update: add `customer_owner` and `customer_staff` roles

Test (minimum):
1) Create business
2) Create owner user linked to business
3) Login as owner and verify business context

### Step 2 — Plans
Goal: define pricing tiers.

Build:
- Table: `plans` (plan_name, price, features)

Test (minimum):
1) Create a plan
2) List plans

### Step 3 — Subscriptions
Goal: connect a business to a plan.

Build:
- Table: `subscriptions` (business_id, plan_id, status, dates)

Test (minimum):
1) Create subscription for a business
2) Verify active plan for business

### Step 4 — CRM Basic (Customers)
Goal: manage customer data per business.

Build:
- Table: `customers` (business_id, name, email, phone, segment, notes)

Test (minimum):
1) Create customer for business
2) List customers by business
3) Update customer

### Step 5 — Dashboard Summary
Goal: show totals and basic analytics.

Build:
- Query: total customers, total sales (if sales exists)
- Placeholder: AI insight summary (static for MVP)

Test (minimum):
1) Fetch dashboard summary
2) Verify counts match current data

### Step 6 — AI Insight (MVP)
Goal: store and return AI insight text per business.

Build:
- Table: `ai_insights` (business_id, type, output_data, created_at)
- Simple endpoint to fetch latest insight

Test (minimum):
1) Insert insight record
2) Fetch latest insight for business

---

## Phase 2

### Step 7 — Sales Module
Goal: record sales and enable reporting.

Build:
- Table: `sales` (customer_id, business_id, product_id, quantity, total_price, transaction_date, invoice_number)

Test (minimum):
1) Create sale
2) List sales by business

### Step 8 — Reports
Goal: exportable summaries.

Build:
- Sales report endpoint
- Customer report endpoint

Test (minimum):
1) Fetch sales report
2) Fetch customer report

### Step 9 — AI Prediction
Goal: add predictive results (stored values).

Build:
- Add prediction fields to `sales` / `customers` or store in `ai_insights`

Test (minimum):
1) Store prediction result
2) Fetch prediction for business

---

## Phase 3

### Step 10 — Marketing Module
Goal: campaigns and targeting.

Build:
- Table: `marketing_campaigns`
- Basic CRUD

Test (minimum):
1) Create campaign
2) List campaigns

### Step 11 — HR Module (Optional)
Goal: employee management and basic HR data.

Build:
- Table: `employees`
- Basic CRUD

Test (minimum):
1) Create employee
2) List employees

### Step 12 — AI Automation (Future)
Goal: automated actions from AI signals.

Build:
- Notification trigger rules
- Event logs

Test (minimum):
1) Trigger a notification rule
2) Verify log entry

---

# AI Business Tools Management System - Database Analysis

## 1. Core DB Entities

### Users

* **Fields:** id, name, email, password_hash, role_id, business_id, created_at, updated_at
* **Notes:** role_id links to Roles table; supports multi-tenancy by business_id.

### Roles

* **Fields:** id, role_name, description
* **Access Levels:** Public, Customer Owner, Customer Staff, Admin, Support

### Businesses

* **Fields:** id, name, tenant_id, plan_id, status, created_at, updated_at
* **Notes:** Each business is a tenant; linked to Plans table.

### Plans

* **Fields:** id, plan_name, price, features (JSON or separate table), created_at, updated_at

### Subscriptions

* **Fields:** id, business_id, plan_id, start_date, end_date, status, billing_history (JSON)
* **Notes:** Tracks active/inactive subscription per business.

### Customers (CRM Data)

* **Fields:** id, business_id, name, email, phone, segment, notes, created_at, updated_at
* **AI Fields:** churn_risk_score, lifetime_value, next_best_product

### Sales

* **Fields:** id, customer_id, business_id, product_id, quantity, total_price, transaction_date, invoice_number
* **AI Fields:** demand_prediction, anomaly_flag

### Products

* **Fields:** id, business_id, name, price, stock, category, created_at, updated_at

### Marketing Campaigns

* **Fields:** id, business_id, name, target_segment, start_date, end_date, performance_metrics (JSON)
* **AI Fields:** best_time_to_send, content_suggestions

### HR (Optional Phase 2)

* **Employees:** id, business_id, name, role, attendance, performance_score
* **AI Fields:** attrition_risk, performance_prediction

### AI Insights

* **Fields:** id, business_id, type (insight/prediction), input_data (JSON), output_data (JSON), created_at
* **Notes:** Could store predictions for sales, customer churn, marketing, etc.

### Invoices / Billing

* **Fields:** id, business_id, subscription_id, amount, payment_status, payment_date, method

### Logs / Audit

* User actions, AI usage logs, system events

---

## 2. Relationships (ER Model)

* **Users ↔ Roles** → Many-to-One
* **Users ↔ Businesses** → Many-to-One
* **Businesses ↔ Plans** → Many-to-One
* **Businesses ↔ Customers** → One-to-Many
* **Businesses ↔ Sales** → One-to-Many
* **Customers ↔ Sales** → One-to-Many
* **Businesses ↔ Marketing Campaigns** → One-to-Many
* **Businesses ↔ AI Insights** → One-to-Many
* **Businesses ↔ Subscriptions** → One-to-Many
* **Subscriptions ↔ Plans** → Many-to-One
* **Businesses ↔ Products** → One-to-Many

---

## 3. Suggested Tables & Fields (Simplified)

### users

```
id | name | email | password_hash | role_id | business_id | created_at | updated_at
```

### roles

```
id | role_name | description
```

### businesses

```
id | name | tenant_id | plan_id | status | created_at | updated_at
```

### plans

```
id | plan_name | price | features (JSON) | created_at | updated_at
```

### subscriptions

```
id | business_id | plan_id | start_date | end_date | status | billing_history (JSON)
```

### customers

```
id | business_id | name | email | phone | segment | notes | churn_risk | lifetime_value | next_best_product | created_at | updated_at
```

### sales

```
id | customer_id | business_id | product_id | quantity | total_price | transaction_date | invoice_number | demand_prediction | anomaly_flag
```

### products

```
id | business_id | name | price | stock | category | created_at | updated_at
```

### marketing_campaigns

```
id | business_id | name | target_segment | start_date | end_date | performance_metrics (JSON) | best_time_to_send | content_suggestions
```

### employees

```
id | business_id | name | role | attendance | performance_score | attrition_risk | performance_prediction
```

### ai_insights

```
id | business_id | type | input_data (JSON) | output_data (JSON) | created_at
```

### invoices

```
id | business_id | subscription_id | amount | payment_status | payment_date | method
```

---

## 4. Notes / Recommendations

* **Multi-tenant Support:** Include business_id in almost every table to ensure proper tenant isolation.
* **JSON Fields:** AI predictions, features, campaign metrics, and billing history can use JSON to allow flexible storage.
* **Indexing:** Index business_id, customer_id, subscription_id for performance.
* **Audit Trail:** Maintain logs for actions, AI usage, and system events for monitoring.
* **Security:** Store passwords hashed, JWT for auth, and implement role-based access in DB queries.
