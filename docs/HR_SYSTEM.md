# HR System Overview

This document describes the HR system features, APIs, and role permissions implemented in this project.

## Roles

### Internal

- `superuser`: Full access to all HR features across all businesses.

### Customer

- `customer_owner`: Full HR access within their business.
- `hr_admin`: Full HR access within their business.
- `employee`: Self-only access (own profile, own attendance, own leaves, own payslips).

## Feature Summary

1. Employee Registration + Approval
2. Employee Directory
3. Leave Management
4. Attendance
5. Payroll Basics

## 1) Employee Registration + Approval

### Public Registration

- **POST** `/api/v1/public/hr/register`
  - Purpose: Employee self-registers with company code.
  - Status: Created as `role=employee`, `is_active=false`, `status=pending`.
  - Company code maps to `business.tenant_id`.

#### Request Body

```json
{
  "companyCode": "acme-hr",
  "name": "Sokha Dara",
  "email": "sokha@acme.com",
  "phone": "+85512345678",
  "employeeId": "EMP-1042",
  "department": "HR",
  "password": "Secret123!",
  "confirmPassword": "Secret123!"
}
```

### HR Approval

- **GET** `/api/v1/hr/employees/pending?businessId=1`
  - Roles: `customer_owner`, `hr_admin`, `superuser`
- **POST** `/api/v1/hr/employees/{user_id}/approve`
  - Roles: `customer_owner`, `hr_admin`, `superuser`

## 2) Employee Directory

### List Employees

- **GET** `/api/v1/hr/employees/?businessId=1`
  - Roles: `customer_owner`, `hr_admin`, `superuser`

### Create Employee

- **POST** `/api/v1/hr/employees/`
  - Roles: `customer_owner`, `hr_admin`, `superuser`

```json
{
  "businessId": 1,
  "fullName": "Sokha Dara",
  "email": "sokha@acme.com",
  "phone": "+85512345678",
  "employeeId": "EMP-1042",
  "department": "HR",
  "password": "Secret123!"
}
```

### View Employee

- **GET** `/api/v1/hr/employees/{user_id}`
  - Roles: `customer_owner`, `hr_admin`, `superuser`
  - Employees may view only their own record.

### Update Employee

- **PUT** `/api/v1/hr/employees/{user_id}`
  - Roles: `customer_owner`, `hr_admin`, `superuser`

### Deactivate Employee

- **POST** `/api/v1/hr/employees/{user_id}/deactivate`
  - Roles: `customer_owner`, `hr_admin`, `superuser`

## 3) Leave Management

### Create Leave

- **POST** `/api/v1/hr/leaves/`
  - Roles: `employee` (self-only), `customer_owner`, `hr_admin`, `superuser`

```json
{
  "leaveType": "Annual",
  "startDate": "2026-03-10",
  "endDate": "2026-03-12",
  "reason": "Family trip"
}
```

### List Leaves

- **GET** `/api/v1/hr/leaves/?businessId=1&status=pending`
  - Roles: `customer_owner`, `hr_admin`, `superuser`
  - Employees only see their own records.

### Approve / Reject

- **POST** `/api/v1/hr/leaves/{id}/approve`
- **POST** `/api/v1/hr/leaves/{id}/reject`
  - Roles: `customer_owner`, `hr_admin`, `superuser`

```json
{ "note": "Please update the dates and resubmit." }
```

## 4) Attendance

### Check In

- **POST** `/api/v1/hr/attendance/check-in`
  - Roles: `employee`, `superuser`

```json
{ "note": "Arrived on time" }
```

### Check Out

- **POST** `/api/v1/hr/attendance/check-out`
  - Roles: `employee`, `superuser`

```json
{ "note": "Leaving now" }
```

### List Attendance

- **GET** `/api/v1/hr/attendance/?businessId=1&startDate=2026-03-01&endDate=2026-03-31`
  - Roles: `customer_owner`, `hr_admin`, `superuser`
  - Employees only see their own records.

### Update Attendance

- **PUT** `/api/v1/hr/attendance/{log_id}`
  - Roles: `customer_owner`, `hr_admin`, `superuser`

```json
{
  "checkInAt": "2026-03-03T01:00:00Z",
  "checkOutAt": "2026-03-03T09:00:00Z",
  "status": "present",
  "note": "Adjusted"
}
```

## 5) Payroll Basics

### Create Pay Period

- **POST** `/api/v1/hr/payroll/periods`
  - Roles: `customer_owner`, `hr_admin`, `superuser`

```json
{ "businessId": 1, "periodStart": "2026-03-01", "periodEnd": "2026-03-31" }
```

### List Pay Periods

- **GET** `/api/v1/hr/payroll/periods?businessId=1`
  - Roles: `customer_owner`, `hr_admin`, `superuser`

### Set Employee Pay

- **POST** `/api/v1/hr/payroll/settings`
  - Roles: `customer_owner`, `hr_admin`, `superuser`

```json
{
  "businessId": 1,
  "userId": 123,
  "payType": "monthly",
  "monthlySalary": 800,
  "hourlyRate": null,
  "overtimeRate": 10
}
```

### Run Payroll

- **POST** `/api/v1/hr/payroll/run`
  - Roles: `customer_owner`, `hr_admin`, `superuser`

```json
{ "businessId": 1, "payPeriodId": 5 }
```

### List Payslips

- **GET** `/api/v1/hr/payroll/payslips?businessId=1`
  - Roles: `customer_owner`, `hr_admin`, `superuser`
  - Employees only see their own payslips.

## Notes

- All HR endpoints require authentication.
- `superuser` bypasses role restrictions and can access all businesses.
- Most HR actions are scoped by `business_id`.
