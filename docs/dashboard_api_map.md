# Dashboard API Map (CRM UI)

Use these endpoints to make the CRM dashboard fully dynamic.

## 1) Top KPI Cards

`GET /api/v1/dashboard/overview?businessId=1&range=30d`

Response fields:
- `ordersCount`
- `salesTotal`
- `profitTotal`
- `customersNew`
- `growthPct`

Map to UI:
- Orders card → `ordersCount`
- Sales card → `salesTotal`
- Profit card → `profitTotal`
- Revenue Growth % → `growthPct`
- New Customers → `customersNew`

## 2) Revenue Growth (Mini Chart + Line Chart)

`GET /api/v1/dashboard/revenue-series?businessId=1&range=30d&interval=day`

Use `interval=month` for the large line chart.

Each item:
- `period` (ISO string)
- `value` (number)

## 3) Earning Reports (Bar Chart)

`GET /api/v1/dashboard/segments?businessId=1`

Each item:
- `segment`
- `count`

## 4) Latest Statistics (Bar Chart)

Option A (customers):
`GET /api/v1/dashboard/customers-series?businessId=1&range=30d&interval=day`

Option B (churn risk):
`GET /api/v1/dashboard/churn-risk?businessId=1`

Each item:
- `period` + `value` (series) OR
- `bucket` + `count` (churn)

## 5) Orders Trend (if you need it)

`GET /api/v1/dashboard/orders-series?businessId=1&range=30d&interval=day`

Each item:
- `period`
- `value`
