# Dashboard Users Overview API

This endpoint powers the top user stats cards: Total Users, Paid Users, Active Users, Pending Users.

## Endpoint
`GET /api/v1/dashboard/users-overview`

Query params:
- `businessId` (optional): filter by business
- `range` (optional): `7d`, `30d`, `90d`, `365d` (default `7d`)

## Response
```json
{
  "success": true,
  "status_code": 200,
  "message": "Users overview",
  "data": {
    "totalUsers": 21459,
    "totalUsersGrowthPct": 29.0,
    "paidUsers": 4567,
    "paidUsersGrowthPct": 18.0,
    "activeUsers": 19860,
    "activeUsersGrowthPct": -14.0,
    "pendingUsers": 237,
    "pendingUsersGrowthPct": 42.0,
    "rangeDays": 7
  }
}
```

## Counting Rules
- **Total Users**: all users (optionally scoped by `businessId`)
- **Paid Users**: `plan_id` set **OR** `plan` set **OR** `billing` set
- **Active Users**: `status == "active"` **OR** `is_active == true`
- **Pending Users**: `status == "pending"`

## Growth Calculation
Growth percent compares current totals against totals **before** the start of the selected range.

## Notes
- Requires auth (`admin` role).
- Uses user timestamps (`created_at`, `updated_at`) for growth calculation.
