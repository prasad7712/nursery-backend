# Complete Admin Panel API Documentation

**Base URL:** `http://localhost:8000/api/v1/admin`

**Authentication:** All endpoints require `Authorization: Bearer <JWT_TOKEN>` header with Admin role

---

## Table of Contents
1. [Product Management](#product-management) ⭐ NEW
2. [Category Management](#category-management) ⭐ NEW
3. [Inventory Management](#inventory-management)
4. [Order Management](#order-management)
5. [User Management](#user-management)
6. [Dashboard](#dashboard)

---

## Product Management

**Base Path:** `/api/v1/admin/products`

### 1. List Products
```
GET /api/v1/admin/products?page=1&per_page=20&category_id=cat-123&is_active=true&search=tomato
```

**Query Parameters:**
- `page` (int, optional): Page number (default: 1)
- `per_page` (int, optional): Items per page (default: 20, max: 100)
- `category_id` (string, optional): Filter by category ID
- `is_active` (boolean, optional): Filter by active status (true/false)
- `search` (string, optional): Search by product name or scientific name

**Response:** (200 OK)
```json
{
  "products": [
    {
      "id": "prod-123",
      "name": "Tomato Plant",
      "scientific_name": "Solanum lycopersicum",
      "slug": "tomato-plant",
      "category_id": "cat-01",
      "price": 9.99,
      "cost_price": 4.50,
      "image_url": "https://example.com/images/tomato.jpg",
      "description": "Fresh organic tomato plant",
      "care_instructions": "Water daily, keep in sunlight",
      "light_requirements": "Full sun (6-8 hours)",
      "watering_frequency": "Daily",
      "temperature_range": "20-30°C",
      "is_active": true,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-20T14:45:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "per_page": 20,
  "total_pages": 8
}
```

---

### 2. Get Product Details
```
GET /api/v1/admin/products/{product_id}
```

**Path Parameters:**
- `product_id` (string, required): Product ID

**Response:** (200 OK)
```json
{
  "id": "prod-123",
  "name": "Tomato Plant",
  "scientific_name": "Solanum lycopersicum",
  "slug": "tomato-plant",
  "category_id": "cat-01",
  "price": 9.99,
  "cost_price": 4.50,
  "image_url": "https://example.com/images/tomato.jpg",
  "description": "Fresh organic tomato plant",
  "care_instructions": "Water daily, keep in sunlight",
  "light_requirements": "Full sun (6-8 hours)",
  "watering_frequency": "Daily",
  "temperature_range": "20-30°C",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T14:45:00Z"
}
```

**Error Responses:**
- 404 Not Found: `{"detail": "Product not found"}`

---

### 3. Create Product
```
POST /api/v1/admin/products
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Basil Plant",
  "scientific_name": "Ocimum basilicum",
  "category_id": "cat-02",
  "price": 5.99,
  "cost_price": 2.50,
  "image_url": "https://example.com/images/basil.jpg",
  "description": "Fresh organic basil plant",
  "care_instructions": "Water when soil is dry, pinch off flowers",
  "light_requirements": "Partial to full sun (4-6 hours)",
  "watering_frequency": "2-3 times per week",
  "temperature_range": "15-25°C",
  "is_active": true
}
```

**Response:** (201 Created)
```json
{
  "id": "prod-456",
  "name": "Basil Plant",
  "scientific_name": "Ocimum basilicum",
  "slug": "basil-plant",
  "category_id": "cat-02",
  "price": 5.99,
  "cost_price": 2.50,
  "image_url": "https://example.com/images/basil.jpg",
  "description": "Fresh organic basil plant",
  "care_instructions": "Water when soil is dry, pinch off flowers",
  "light_requirements": "Partial to full sun (4-6 hours)",
  "watering_frequency": "2-3 times per week",
  "temperature_range": "15-25°C",
  "is_active": true,
  "created_at": "2024-01-21T09:15:00Z",
  "updated_at": "2024-01-21T09:15:00Z"
}
```

**Validation:**
- `name`: Required, 1-200 characters
- `category_id`: Required, must exist in database
- `price`: Required, must be > 0
- `image_url`: Required
- `description`: Required
- `cost_price`: Optional, must be > 0 if provided

**Error Responses:**
- 400 Bad Request: `{"detail": "Category not found"}`
- 400 Bad Request: `{"detail": "Error creating product: ..."}`

---

### 4. Update Product
```
PUT /api/v1/admin/products/{product_id}
Content-Type: application/json
```

**Path Parameters:**
- `product_id` (string, required): Product ID

**Request Body:** (All fields optional - only include fields to update)
```json
{
  "name": "Premium Basil Plant",
  "price": 7.99,
  "description": "Updated description",
  "is_active": true
}
```

**Response:** (200 OK)
```json
{
  "id": "prod-456",
  "name": "Premium Basil Plant",
  "scientific_name": "Ocimum basilicum",
  "slug": "basil-plant",
  "category_id": "cat-02",
  "price": 7.99,
  "cost_price": 2.50,
  "image_url": "https://example.com/images/basil.jpg",
  "description": "Updated description",
  "care_instructions": "Water when soil is dry, pinch off flowers",
  "light_requirements": "Partial to full sun (4-6 hours)",
  "watering_frequency": "2-3 times per week",
  "temperature_range": "15-25°C",
  "is_active": true,
  "created_at": "2024-01-21T09:15:00Z",
  "updated_at": "2024-01-21T10:45:00Z"
}
```

**Error Responses:**
- 404 Not Found: `{"detail": "Product not found"}`
- 400 Bad Request: `{"detail": "Category not found"}`

---

### 5. Delete Product (Soft Delete)
```
DELETE /api/v1/admin/products/{product_id}
```

**Path Parameters:**
- `product_id` (string, required): Product ID

**Response:** (200 OK)
```json
{
  "success": true,
  "message": "Product deleted successfully"
}
```

**Note:** This is a soft delete - the product's `is_active` flag is set to `false`

**Error Responses:**
- 404 Not Found: `{"detail": "Product not found"}`

---

### 6. Activate Product
```
POST /api/v1/admin/products/{product_id}/activate
```

**Path Parameters:**
- `product_id` (string, required): Product ID

**Response:** (200 OK)
```json
{
  "success": true,
  "message": "Product activated successfully"
}
```

**Error Responses:**
- 404 Not Found: `{"detail": "Product not found"}`

---

## Category Management

**Base Path:** `/api/v1/admin/categories`

### 1. List Categories
```
GET /api/v1/admin/categories?page=1&per_page=20&search=vegetables
```

**Query Parameters:**
- `page` (int, optional): Page number (default: 1)
- `per_page` (int, optional): Items per page (default: 20, max: 100)
- `search` (string, optional): Search by category name

**Response:** (200 OK)
```json
{
  "categories": [
    {
      "id": "cat-01",
      "name": "Vegetables",
      "slug": "vegetables",
      "description": "Fresh vegetable plants",
      "icon": "🥬",
      "product_count": 25,
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T10:00:00Z"
    }
  ],
  "total": 8,
  "page": 1,
  "per_page": 20,
  "total_pages": 1
}
```

---

### 2. Get Category Details
```
GET /api/v1/admin/categories/{category_id}
```

**Path Parameters:**
- `category_id` (string, required): Category ID

**Response:** (200 OK)
```json
{
  "id": "cat-01",
  "name": "Vegetables",
  "slug": "vegetables",
  "description": "Fresh vegetable plants",
  "icon": "🥬",
  "product_count": 25,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

---

### 3. Create Category
```
POST /api/v1/admin/categories
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Herbs",
  "description": "Aromatic herb plants for cooking",
  "icon": "🌿"
}
```

**Response:** (201 Created)
```json
{
  "id": "cat-05",
  "name": "Herbs",
  "slug": "herbs",
  "description": "Aromatic herb plants for cooking",
  "icon": "🌿",
  "product_count": 0,
  "created_at": "2024-01-21T10:30:00Z",
  "updated_at": "2024-01-21T10:30:00Z"
}
```

**Validation:**
- `name`: Required, 1-100 characters
- `description`: Required
- `icon`: Optional

**Error Responses:**
- 400 Bad Request: `{"detail": "Category with this name already exists"}`

---

### 4. Update Category
```
PUT /api/v1/admin/categories/{category_id}
Content-Type: application/json
```

**Path Parameters:**
- `category_id` (string, required): Category ID

**Request Body:** (All fields optional)
```json
{
  "name": "Updated Herbs",
  "description": "Updated description",
  "icon": "🌱"
}
```

**Response:** (200 OK)
```json
{
  "id": "cat-05",
  "name": "Updated Herbs",
  "slug": "herbs",
  "description": "Updated description",
  "icon": "🌱",
  "product_count": 5,
  "created_at": "2024-01-21T10:30:00Z",
  "updated_at": "2024-01-21T11:00:00Z"
}
```

---

### 5. Delete Category
```
DELETE /api/v1/admin/categories/{category_id}
```

**Response:** (200 OK)
```json
{
  "success": true,
  "message": "Category deleted successfully"
}
```

---

## Inventory Management

**Base Path:** `/api/v1/admin/inventory`

### 1. List Inventory
```
GET /api/v1/admin/inventory?page=1&per_page=20&low_stock_only=false&product_id=prod-123
```

**Query Parameters:**
- `page` (int, optional): Page number (default: 1)
- `per_page` (int, optional): Items per page (default: 20, max: 100)
- `low_stock_only` (boolean, optional): Show only low stock items (default: false)
- `product_id` (string, optional): Filter by product ID

**Response:** (200 OK)
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
      "is_low_stock": false,
      "last_restocked": "2024-01-18T15:30:00Z",
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-18T15:30:00Z"
    }
  ],
  "total": 250,
  "page": 1,
  "per_page": 20,
  "total_pages": 13
}
```

---

### 2. Get Inventory Details
```
GET /api/v1/admin/inventory/{product_id}
```

**Path Parameters:**
- `product_id` (string, required): Product ID

**Response:** (200 OK)
```json
{
  "id": "inv-123",
  "product_id": "prod-123",
  "product_name": "Tomato Plant",
  "stock_level": 45,
  "low_stock_threshold": 20,
  "reorder_quantity": 50,
  "warehouse_location": "A-12-3",
  "is_low_stock": false,
  "last_restocked": "2024-01-18T15:30:00Z",
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-18T15:30:00Z"
}
```

---

### 3. Adjust Inventory Stock
```
POST /api/v1/admin/inventory/{inventory_id}/adjust
Content-Type: application/json
```

**Path Parameters:**
- `inventory_id` (string, required): Inventory ID

**Request Body:**
```json
{
  "change_type": "ADD",
  "quantity": 100,
  "reason": "Restocking received from supplier",
  "note": "Supplier order #2024-001"
}
```

**Change Types:**
- `ADD`: Add quantity to existing stock
- `REMOVE`: Remove quantity from stock (fails if insufficient)
- `ADJUST`: Set stock to exact level (replace current stock)

**Response:** (200 OK)
```json
{
  "success": true,
  "message": "Inventory adjusted successfully. Old stock: 45, New stock: 145"
}
```

**Validation:**
- `change_type`: Required, one of [ADD, REMOVE, ADJUST]
- `quantity`: Required, non-zero integer
- `reason`: Required, min 1 character

**Error Responses:**
- 400 Bad Request: `{"detail": "Error adjusting inventory: Insufficient stock"}`

---

### 4. Get Low Stock Products
```
GET /api/v1/admin/inventory/low-stock/alert?page=1&per_page=20
```

**Query Parameters:**
- `page` (int, optional): Page number (default: 1)
- `per_page` (int, optional): Items per page (default: 20, max: 100)

**Response:** (200 OK)
```json
{
  "inventories": [
    {
      "id": "inv-456",
      "product_id": "prod-456",
      "product_name": "Basil Plant",
      "stock_level": 8,
      "low_stock_threshold": 20,
      "reorder_quantity": 50,
      "warehouse_location": "B-5-1",
      "is_low_stock": true,
      "last_restocked": "2024-01-10T10:00:00Z",
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-10T10:00:00Z"
    }
  ],
  "total": 12,
  "page": 1,
  "per_page": 20,
  "total_pages": 1
}
```

---

## Order Management

**Base Path:** `/api/v1/admin/orders`

### 1. List Orders
```
GET /api/v1/admin/orders?page=1&per_page=20&status=PENDING&payment_status=UNPAID&user_id=user-123
```

**Query Parameters:**
- `page` (int, optional): Page number (default: 1)
- `per_page` (int, optional): Items per page (default: 20, max: 100)
- `status` (string, optional): PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED
- `payment_status` (string, optional): PAID, UNPAID
- `user_id` (string, optional): Filter by user ID

**Response:** (200 OK)
```json
{
  "orders": [
    {
      "id": "order-123",
      "user_id": "user-123",
      "user_email": "customer@example.com",
      "status": "PENDING",
      "payment_status": "UNPAID",
      "total_amount": 99.99,
      "shipping_address": "123 Main St, City, 12345",
      "notes": "Please deliver after 5 PM",
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

---

### 2. Get Order Details
```
GET /api/v1/admin/orders/{order_id}
```

**Path Parameters:**
- `order_id` (string, required): Order ID

**Response:** (200 OK)
```json
{
  "id": "order-123",
  "user_id": "user-123",
  "user_email": "customer@example.com",
  "status": "PENDING",
  "payment_status": "UNPAID",
  "total_amount": 99.99,
  "shipping_address": "123 Main St, City, 12345",
  "notes": "Please deliver after 5 PM",
  "items_count": 3,
  "created_at": "2024-01-20T10:00:00Z",
  "updated_at": "2024-01-20T10:00:00Z"
}
```

---

### 3. Update Order Status
```
PUT /api/v1/admin/orders/{order_id}/status
Content-Type: application/json
```

**Path Parameters:**
- `order_id` (string, required): Order ID

**Request Body:**
```json
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

**Response:** (200 OK)
```json
{
  "success": true,
  "message": "Order status updated successfully"
}
```

---

### 4. Cancel Order
```
POST /api/v1/admin/orders/{order_id}/cancel?reason=Customer%20requested
```

**Path Parameters:**
- `order_id` (string, required): Order ID

**Query Parameters:**
- `reason` (string, optional): Cancellation reason

**Response:** (200 OK)
```json
{
  "success": true,
  "message": "Order cancelled successfully"
}
```

**Note:** Cannot cancel DELIVERED or already CANCELLED orders.

---

## User Management

**Base Path:** `/api/v1/admin/users`

### 1. List Users
```
GET /api/v1/admin/users?page=1&per_page=20&status=active&role=user&search=john
```

**Query Parameters:**
- `page` (int, optional): Page number (default: 1)
- `per_page` (int, optional): Items per page (default: 20, max: 100)
- `status` (string, optional): active, inactive
- `role` (string, optional): admin, user
- `search` (string, optional): Search by email or name

**Response:** (200 OK)
```json
{
  "users": [
    {
      "id": "user-123",
      "email": "user@example.com",
      "phone": "+1234567890",
      "first_name": "John",
      "last_name": "Doe",
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

---

### 2. Get User Details
```
GET /api/v1/admin/users/{user_id}
```

**Path Parameters:**
- `user_id` (string, required): User ID

**Response:** (200 OK)
```json
{
  "id": "user-123",
  "email": "user@example.com",
  "phone": "+1234567890",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user",
  "is_active": true,
  "orders_count": 5,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T14:45:00Z"
}
```

---

### 3. Update User Status
```
PUT /api/v1/admin/users/{user_id}/status
Content-Type: application/json
```

**Path Parameters:**
- `user_id` (string, required): User ID

**Request Body:**
```json
{
  "is_active": false,
  "reason": "Account suspension due to policy violation"
}
```

**Response:** (200 OK)
```json
{
  "success": true,
  "message": "User status updated successfully"
}
```

---

### 4. Change User Role
```
PUT /api/v1/admin/users/{user_id}/role
Content-Type: application/json
```

**Path Parameters:**
- `user_id` (string, required): User ID

**Request Body:**
```json
{
  "new_role": "admin",
  "reason": "Promoted to admin"
}
```

**Valid Roles:**
- `user`: Regular user
- `admin`: Admin user
- `super_admin`: Super administrator (database only)

**Response:** (200 OK)
```json
{
  "success": true,
  "message": "User role updated successfully"
}
```

**Required:** Super Admin role to perform this action.

---

### 5. Delete User
```
DELETE /api/v1/admin/users/{user_id}?reason=Account%20terminated
```

**Path Parameters:**
- `user_id` (string, required): User ID

**Query Parameters:**
- `reason` (string, optional): Deletion reason

**Response:** (200 OK)
```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

**Required:** Super Admin role to perform this action.

---

## Dashboard

**Base Path:** `/api/v1/admin/dashboard`

### 1. Get Dashboard Statistics
```
GET /api/v1/admin/dashboard/statistics
```

**Response:** (200 OK)
```json
{
  "users": {
    "total": 500,
    "active": 450,
    "inactive": 50
  },
  "orders": {
    "total": 1200,
    "pending": 150,
    "confirmed": 200,
    "shipped": 300,
    "delivered": 500,
    "cancelled": 50
  },
  "products": {
    "total": 350,
    "active": 320,
    "inactive": 30
  },
  "low_stock_count": 12,
  "timestamp": "2024-01-21T12:00:00Z"
}
```

---

### 2. Get Activity Logs
```
GET /api/v1/admin/dashboard/activity-logs?page=1&per_page=20&admin_id=admin-123&action_type=STATUS_CHANGE
```

**Query Parameters:**
- `page` (int, optional): Page number (default: 1)
- `per_page` (int, optional): Items per page (default: 20, max: 100)
- `admin_id` (string, optional): Filter by admin ID
- `action_type` (string, optional): Filter by action type

**Response:** (200 OK)
```json
{
  "logs": [
    {
      "id": "log-123",
      "admin_id": "admin-123",
      "admin_email": "admin@example.com",
      "action_type": "STATUS_CHANGE",
      "entity_type": "Order",
      "entity_id": "order-456",
      "old_values": { "status": "PENDING" },
      "new_values": { "status": "CONFIRMED" },
      "reason": "Order verified and confirmed",
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0...",
      "created_at": "2024-01-20T14:30:00Z"
    }
  ],
  "total": 1000,
  "page": 1,
  "per_page": 20
}
```

---

## Error Handling

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Only super admins can perform this action"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Authentication Header Format

All endpoints require the authorization header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Common Response Fields

### Pagination (List Endpoints)
```json
{
  "total": 150,        // Total items in database
  "page": 1,           // Current page number
  "per_page": 20,      // Items per page
  "total_pages": 8     // Total number of pages
}
```

### Timestamps
All timestamps are in ISO 8601 format: `2024-01-21T12:00:00Z`

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully"
}
```

---

## Rate Limiting

- Default page size: 20 items
- Maximum page size: 100 items
- All list endpoints support pagination

---

## Frontend Development Tips

1. **Always include the JWT token** in the Authorization header
2. **Use pagination** for list endpoints to avoid loading too much data
3. **Monitor low stock alerts** - use the `/inventory/low-stock/alert` endpoint
4. **Admin role required** - ensure only authenticated admins can access these endpoints
5. **Soft deletes** - deleted items are marked as inactive, not permanently removed
6. **Validate inputs** - follow the field validation rules mentioned in each endpoint
7. **Activity logging** - all admin actions are logged for audit trails

---

## Quick Reference - API Summary

| Feature | Method | Endpoint | Status |
|---------|--------|----------|--------|
| **Products** | GET | `/products` | ✅ Ready |
| | POST | `/products` | ✅ Ready |
| | GET | `/products/{id}` | ✅ Ready |
| | PUT | `/products/{id}` | ✅ Ready |
| | DELETE | `/products/{id}` | ✅ Ready |
| | POST | `/products/{id}/activate` | ✅ Ready |
| **Categories** | GET | `/categories` | ✅ Ready |
| | POST | `/categories` | ✅ Ready |
| | GET | `/categories/{id}` | ✅ Ready |
| | PUT | `/categories/{id}` | ✅ Ready |
| | DELETE | `/categories/{id}` | ✅ Ready |
| **Inventory** | GET | `/inventory` | ✅ Ready |
| | GET | `/inventory/{product_id}` | ✅ Ready |
| | POST | `/inventory/{id}/adjust` | ✅ Ready |
| | GET | `/inventory/low-stock/alert` | ✅ Ready |
| **Orders** | GET | `/orders` | ✅ Ready |
| | GET | `/orders/{id}` | ✅ Ready |
| | PUT | `/orders/{id}/status` | ✅ Ready |
| | POST | `/orders/{id}/cancel` | ✅ Ready |
| **Users** | GET | `/users` | ✅ Ready |
| | GET | `/users/{id}` | ✅ Ready |
| | PUT | `/users/{id}/status` | ✅ Ready |
| | PUT | `/users/{id}/role` | ✅ Ready |
| | DELETE | `/users/{id}` | ✅ Ready |
| **Dashboard** | GET | `/dashboard/statistics` | ✅ Ready |
| | GET | `/dashboard/activity-logs` | ✅ Ready |

---

## Support

For any issues or questions, please check the test examples or contact the development team.
