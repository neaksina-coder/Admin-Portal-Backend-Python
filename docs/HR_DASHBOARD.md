# HR Dashboard (Short)

## Endpoint
- **GET** `/api/v1/hr/dashboard/?businessId=<BUSINESS_ID>`

## Access
- `customer_owner`, `hr_admin`, `superuser`

## Response (example)
```json
{
  "success": true,
  "status_code": 200,
  "message": "HR dashboard summary",
  "data": {
    "employees": { "total": 10, "active": 8, "pending": 1, "inactive": 1 },
    "attendance": { "todayCheckedIn": 5, "todayCheckedOut": 3, "missingCheckout": 2 },
    "leave": { "pending": 2, "approvedThisMonth": 4, "rejectedThisMonth": 1 },
    "payroll": { "lastPeriodNetPay": 3200, "payslipsGenerated": 8, "openPeriods": 1 }
  }
}
```
