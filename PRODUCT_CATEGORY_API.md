# Products & Categories API (for Vue.js integration)

Base URL: `http://127.0.0.1:8000/api/v1`

Auth: create/update/delete require role `admin` via `deps.require_roles(["admin"])`.

---
## Categories

### Data model (Category)
Fields:
- `id` (int)
- `name` (string, unique, required)
- `slug` (string, unique, required)
- `description` (string, nullable)
- `status` (string, default `active`)
- `created_at` (datetime)

### Create category
POST `/categories/`
Auth: admin
Body (CategoryCreate):
```json
{
  "name": "Beverages",
  "slug": "beverages",
  "description": "Drinks and refreshments",
    
}
```
Response (CategoryResponse):
```json
{
  "success": true,
  "status_code": 201,
  "message": "Category created successfully",
  "data": {
    "id": 1,
    "name": "Beverages",
    "slug": "beverages",
    "description": "Drinks and refreshments",
    "status": "active",
    "created_at": "2026-01-23T10:30:00"
  }
}
```
Errors:
- 400: `Category with this slug already exists`

### List categories
GET `/categories/`
Query params:
- `skip` (int, default 0, min 0)
- `limit` (int, default 100, min 1, max 100)
- `status` (string, optional)

Response (CategoryListResponse):
```json
{
  "success": true,
  "status_code": 200,
  "message": "Categories retrieved successfully",
  "total": 2,
  "data": [
    {
      "id": 1,
      "name": "Beverages",
      "slug": "beverages",
      "description": "Drinks and refreshments",
      "status": "active",
      "created_at": "2026-01-23T10:30:00"
    }
  ]
}
```

### Get category by id
GET `/categories/{category_id}`
Response (CategoryResponse) same shape as create.
Errors:
- 404: `Category not found`

### Update category
PUT `/categories/{category_id}`
Auth: admin
Body (CategoryUpdate, all fields optional):
```json
{
  "name": "Soft Drinks",
  "slug": "soft-drinks",
  "description": "Sodas and sparkling drinks",
  "status": "active"
}
```
Response (CategoryResponse) same shape as create.
Errors:
- 404: `Category not found`

### Delete category
DELETE `/categories/{category_id}`
Auth: admin
Response (CategoryDeleteResponse):
```json
{
  "success": true,
  "status_code": 200,
  "message": "Category deleted successfully",
  "id": 1
}
```
Errors:
- 404: `Category not found`

---
## Products

### Data model (Product)
Fields:
- `id` (int)
- `name` (string, required)
- `sku` (string, unique, required)
- `description` (string, nullable)
- `category_id` (int, nullable)
- `price` (float, required, gt 0)
- `cost` (float, nullable, ge 0)
- `stock` (int, default 0, ge 0)
- `unit` (string, nullable)
- `status` (string, default `active`)
- `created_at` (datetime)
- `category` (Category object, nullable)

### Create product
POST `/products/`
Auth: admin
Body (ProductCreate):
```json
{
  "name": "Coca Cola",
  "sku": "SKU-COC-001",
  "description": "330ml can",
  "category_id": 1,
  "price": 1.5,
  "cost": 1.0,
  "stock": 100,
  "unit": "can",
  "status": "active"
}
```
Response (ProductResponse):
```json
{
  "success": true,
  "status_code": 201,
  "message": "Product created successfully",
  "data": {
    "id": 1,
    "name": "Coca Cola",
    "sku": "SKU-COC-001",
    "description": "330ml can",
    "category_id": 1,
    "price": 1.5,
    "cost": 1.0,
    "stock": 100,
    "unit": "can",
    "status": "active",
    "created_at": "2026-01-23T10:40:00",
    "category": {
      "id": 1,
      "name": "Beverages",
      "slug": "beverages",
      "description": "Drinks and refreshments",
      "status": "active",
      "created_at": "2026-01-23T10:30:00"
    }
  }
}
```
Errors:
- 400: `Product with this SKU already exists`

### List products
GET `/products/`
Query params:
- `skip` (int, default 0, min 0)
- `limit` (int, default 100, min 1, max 100)
- `category_id` (int, optional)
- `status` (string, optional)

Response (ProductListResponse):
```json
{
  "success": true,
  "status_code": 200,
  "message": "Products retrieved successfully",
  "total": 1,
  "data": [
    {
      "id": 1,
      "name": "Coca Cola",
      "sku": "SKU-COC-001",
      "description": "330ml can",
      "category_id": 1,
      "price": 1.5,
      "cost": 1.0,
      "stock": 100,
      "unit": "can",
      "status": "active",
      "created_at": "2026-01-23T10:40:00",
      "category": {
        "id": 1,
        "name": "Beverages",
        "slug": "beverages",
        "description": "Drinks and refreshments",
        "status": "active",
        "created_at": "2026-01-23T10:30:00"
      }
    }
  ]
}
```

### Get product by id
GET `/products/{product_id}`
Response (ProductResponse) same shape as create.
Errors:
- 404: `Product not found`

### Get product by SKU
GET `/products/sku/{sku}`
Response (ProductResponse) same shape as create.
Errors:
- 404: `Product not found`

### Update product
PUT `/products/{product_id}`
Auth: admin
Body (ProductUpdate, all fields optional):
```json
{
  "name": "Coca Cola Zero",
  "sku": "SKU-COC-001",
  "description": "330ml can - zero sugar",
  "category_id": 1,
  "price": 1.6,
  "cost": 1.05,
  "stock": 120,
  "unit": "can",
  "status": "active"
}
```
Response (ProductResponse) same shape as create.
Errors:
- 400: `Product with this SKU already exists` (if SKU conflicts)
- 404: `Product not found`

### Delete product
DELETE `/products/{product_id}`
Auth: admin
Response (ProductDeleteResponse):
```json
{
  "success": true,
  "status_code": 200,
  "message": "Product deleted successfully",
  "id": 1
}
```
Errors:
- 404: `Product not found`

---
## Notes for frontend
- The API returns `success`, `status_code`, `message`, and `data` for single resources; list responses include `total`.
- `category_id` on products is optional; if set, the response includes a nested `category` object.
- Validation: `price > 0`, `cost >= 0`, `stock >= 0`.
- Status is a string, defaults to `active`.
