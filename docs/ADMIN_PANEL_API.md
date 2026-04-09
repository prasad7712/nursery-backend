# Admin Panel API Documentation

## Overview

The admin panel APIs provide comprehensive management capabilities for administrators to manage users, orders, products, and inventory. All admin endpoints require authentication with admin role.

## Authentication

All admin endpoints require:
- Valid JWT token in `Authorization: Bearer <token>` header
- Admin role in user profile
- Some endpoints require "super_admin" role for sensitive operations

## Base URL

```
http://localhost:8000/api/v1/admin
```

## Admin Endpoints

### User Management (`/users`)

#### List Users
```http
GET /api/v1/admin/users?page=1&per_page=20&status=active&role=user&search=john
```

**Query Parameters:**
- `page` (int): Page number for pagination (default: 1)
- `per_page` (int): Items per page (default: 20, max: 100)
- `status` (string): Filter by status - "active" or "inactive"
- `role` (string): Filter by role - "admin" or "user"
- `search` (string): Search by email or name

**Response:**
```json
{
  "users": [
    {
      "id": "user-123",
      "email": "user@example.com",
      "name": "John Doe",
      "role": "user",
      "is_active": true,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-20T14:45:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "per_page": 20,
  "total_pages": 3
}
```

#### Get User Details
```http
GET /api/v1/admin/users/{user_id}
```

**Response:**
```json
{
  "id": "user-123",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T14:45:00Z"
}
```

#### Update User Status
```http
PUT /api/v1/admin/users/{user_id}/status
Content-Type: application/json

{
  "is_active": false,
  "reason": "Account suspension due to policy violation"
}
```

**Note:** Set `is_active: true` to activate a user, `is_active: false` to suspend/deactivate.

#### Change User Role
```http
PUT /api/v1/admin/users/{user_id}/role
Content-Type: application/json

{
  "new_role": "admin",
  "reason": "Promoted to admin"
}
```

**Required:** Super Admin role to perform this action.

**Valid Roles:**
- `user`: Regular user
- `admin`: Admin user
- `super_admin`: Super administrator (via database only)

#### Delete User
```http
DELETE /api/v1/admin/users/{user_id}?reason=Account%20terminated
```

**Note:** This performs a soft delete by deactivating the user.

**Required:** Super Admin role to perform this action.

---

### Order Management (`/orders`)

#### List Orders
```http
GET /api/v1/admin/orders?page=1&per_page=20&status=PENDING&payment_status=UNPAID&user_id=user-123
```

**Query Parameters:**
- `page` (int): Page number for pagination
- `per_page` (int): Items per page
- `status` (string): Filter by order status - PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED
- `payment_status` (string): Filter by payment status - PAID, UNPAID
- `user_id` (string): Filter by specific user

**Response:**
```json
{
  "orders": [
    {
      "id": "order-123",
      "user_id": "user-123",
      "user_email": "user@example.com",
      "status": "PENDING",
      "payment_status": "UNPAID",
      "total_amount": 99.99,
      "items_count": 3,
      "created_at": "2024-01-20T10:00:00Z",
      "updated_at": "2024-01-20T10:00:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "per_page": 20,
  "total_pages": 8
}
```

#### Get Order Details
```http
GET /api/v1/admin/orders/{order_id}
```

**Response:**
```json
{
  "id": "order-123",
  "user_id": "user-123",
  "user_email": "user@example.com",
  "status": "PENDING",
  "payment_status": "UNPAID",
  "total_amount": 99.99,
  "items_count": 3,
  "created_at": "2024-01-20T10:00:00Z",
  "updated_at": "2024-01-20T10:00:00Z"
}
```

#### Update Order Status
```http
PUT /api/v1/admin/orders/{order_id}/status
Content-Type: application/json

{
  "status": "CONFIRMED",
  "note": "Order confirmed and ready for shipment"
}
```

**Valid Statuses:**
- `PENDING`: Order placed, awaiting confirmation
- `CONFIRMED`: Order confirmed by admin
- `SHIPPED`: Order shipped to customer
- `DELIVERED`: Order delivered to customer
- `CANCELLED`: Order cancelled

#### Cancel Order
```http
POST /api/v1/admin/orders/{order_id}/cancel?reason=Customer%20requested
```

**Note:** Cannot cancel DELIVERED or already CANCELLED orders.

---

### Inventory Management (`/inventory`)

#### List Inventory
```http
GET /api/v1/admin/inventory?page=1&per_page=20&low_stock_only=false&product_id=prod-123
```

**Query Parameters:**
- `page` (int): Page number for pagination
- `per_page` (int): Items per page
- `low_stock_only` (boolean): Show only low stock items
- `product_id` (string): Filter by specific product

**Response:**
```json
{
  "inventories": [
    {
      "id": "inv-123",
      "product_id": "prod-123",
      "product_name": "Tomato Plant",
      "stock_level": 45,
      "low_stock_threshold": 20,
      "reorder_quantity": 50,
      "warehouse_location": "A-12-3",
      "last_restocked": "2024-01-18T15:30:00Z"
    }
  ],
  "total": 250,
  "page": 1,
  "per_page": 20,
  "total_pages": 13
}
```

#### Get Inventory Details
```http
GET /api/v1/admin/inventory/{product_id}
```

#### Adjust Stock Level
```http
POST /api/v1/admin/inventory/{inventory_id}/adjust
Content-Type: application/json

{
  "change_type": "ADD",
  "quantity": 100,
  "reason": "Restocking received from supplier",
  "note": "Supplier order #2024-001"
}
```

**Change Types:**
- `ADD`: Add quantity to existing stock
- `REMOVE`: Remove quantity from stock (fails if insufficient stock)
- `ADJUST`: Set stock to exact level (replace current stock)

#### Get Low Stock Products
```http
GET /api/v1/admin/inventory/low-stock/alert?page=1&per_page=20
```

Returns products where `stock_level <= low_stock_threshold`

---

### Dashboard (`/dashboard`)

#### Get Dashboard Statistics
```http
GET /api/v1/admin/dashboard/statistics
```

**Response:**
```json
{
  "users": {
    "total": 500,
    "active": 450,
    "inactive": 50
  },
  "orders": {
    "total": 1200,
    "by_status": {
      "pending": 150,
      "confirmed": 200,
      "shipped": 300,
      "delivered": 500,
      "cancelled": 50
    },
    "by_payment_status": {
      "paid": 1000,
      "unpaid": 200
    }
  },
  "products": {
    "total": 350,
    "active": 320,
    "inactive": 30
  },
  "low_stock_count": 12
}
```

#### Get Activity Logs
```http
GET /api/v1/admin/dashboard/activity-logs?page=1&per_page=20&admin_id=admin-123&action_type=STATUS_CHANGE
```

**Query Parameters:**
- `page` (int): Page number for pagination
- `per_page` (int): Items per page
- `admin_id` (string): Filter by specific admin
- `action_type` (string): Filter by action type (ACTIVATE, DEACTIVATE, STATUS_CHANGE, etc.)

**Response:**
```json
{
  "logs": [
    {
      "id": "log-123",
      "admin_id": "admin-123",
      "action_type": "STATUS_CHANGE",
      "entity_type": "Order",
      "entity_id": "order-456",
      "old_values": { "status": "PENDING" },
      "new_values": { "status": "CONFIRMED" },
      "reason": "Order verified and confirmed",
      "created_at": "2024-01-20T14:30:00Z"
    }
  ],
  "total": 1000,
  "page": 1,
  "per_page": 20
}
```

---

## Error Responses

All endpoints return standard error responses:

**400 Bad Request:**
```json
{
  "detail": "Invalid request parameters"
}
```

**403 Forbidden:**
```json
{
  "detail": "Only super admins can perform this action"
}
```

**404 Not Found:**
```json
{
  "detail": "Resource not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Error processing request"
}
```

---

## Common Use Cases

### 1. Suspend a User
```bash
curl -X PUT http://localhost:8000/api/v1/admin/users/user-123/status \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "is_active": false,
    "reason": "Violated terms of service"
  }'
```

### 2. Update Order Status
```bash
curl -X PUT http://localhost:8000/api/v1/admin/orders/order-123/status \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "SHIPPED",
    "note": "Shipment #SHP-001"
  }'
```

### 3. Adjust Product Inventory
```bash
curl -X POST http://localhost:8000/api/v1/admin/inventory/inv-123/adjust \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "change_type": "ADD",
    "quantity": 100,
    "reason": "Restocking",
    "note": "Received shipment from warehouse"
  }'
```

### 4. View Low Stock Products
```bash
curl -X GET "http://localhost:8000/api/v1/admin/inventory/low-stock/alert?page=1&per_page=20" \
  -H "Authorization: Bearer <token>"
```

### 5. Get Dashboard Overview
```bash
curl -X GET http://localhost:8000/api/v1/admin/dashboard/statistics \
  -H "Authorization: Bearer <token>"
```

---

## Rate Limiting & Pagination

- **Default page size:** 20 items
- **Maximum page size:** 100 items
- **Pagination:** All list endpoints support `page` and `per_page` parameters

---

## Best Practices

1. **Always provide reason/notes** for sensitive operations (suspend user, cancel order)
2. **Use filters** to narrow down results instead of fetching all items
3. **Monitor low stock alerts** for timely restocking
4. **Review activity logs** regularly for audit trails
5. **Restrict role changes** to super admins only
6. **Use appropriate status codes** for error handling

---

## Support

For issues or questions about the admin panel, contact the development team.
