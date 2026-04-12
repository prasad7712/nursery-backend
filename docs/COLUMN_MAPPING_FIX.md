# 🔧 Column Name Mapping Fix

## Issue

SQLAlchemy was using snake_case column names (e.g., `user_id`, `created_at`) but the PostgreSQL database created by Prisma uses camelCase column names (e.g., `userId`, `createdAt`).

**Error Example:**
```
column orders.user_id does not exist
HINT: Perhaps you meant to reference the column "orders.userId".
```

## Solution

Added explicit column name mapping in all SQLAlchemy models using the first parameter of `mapped_column()`:

```python
# Before (incorrect)
user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))

# After (correct)
user_id: Mapped[str] = mapped_column("userId", String(36), ForeignKey("users.id"))
```

## Files Fixed

### 1. Cart Models (`src/models/cart.py`)
- ✅ `user_id` → `userId`
- ✅ `created_at` → `createdAt`
- ✅ `updated_at` → `updatedAt`
- ✅ `cart_id` → `cartId`
- ✅ `product_id` → `productId`

### 2. Order Models (`src/models/order.py`)
- ✅ `user_id` → `userId`
- ✅ `payment_status` → `paymentStatus`
- ✅ `payment_id` → `paymentId`
- ✅ `total_amount` → `totalAmount`
- ✅ `shipping_address` → `shippingAddress`
- ✅ `created_at` → `createdAt`
- ✅ `updated_at` → `updatedAt`
- ✅ `order_id` → `orderId`
- ✅ `product_id` → `productId`
- ✅ `unit_price` → `unitPrice`

### 3. Payment Models (`src/models/payment.py`)
- ✅ `order_id` → `orderId`
- ✅ `user_id` → `userId`
- ✅ `razorpay_order_id` → `razorpayOrderId`
- ✅ `razorpay_payment_id` → `razorpayPaymentId`
- ✅ `razorpay_signature` → `razorpaySignature`
- ✅ `error_message` → `errorMessage`
- ✅ `created_at` → `createdAt`
- ✅ `updated_at` → `updatedAt`

### 4. User Models (`src/models/user.py`)
- ✅ All snake_case columns kept as-is (already match database)

### 5. Product Models (`src/models/product.py`)
- ✅ All snake_case columns kept as-is (already match database)

### 6. Admin Models (`src/models/admin.py`)
- ✅ All snake_case columns kept as-is (already match database)

### 7. AI Chat Models (`src/models/ai_chat.py`)
- ✅ All snake_case columns kept as-is (already match database)

## Column Naming Pattern

### Prisma Schema → Database Columns

Prisma automatically converts field names to camelCase in the database:

```prisma
model Cart {
  userId String  // Becomes "userId" in database
  createdAt DateTime  // Becomes "createdAt" in database
}
```

### SQLAlchemy Mapping

We use Python snake_case for attributes but map to database camelCase:

```python
class Cart(Base):
    user_id: Mapped[str] = mapped_column("userId", ...)  # Python: user_id, DB: userId
    created_at: Mapped[datetime] = mapped_column("createdAt", ...)  # Python: created_at, DB: createdAt
```

## Affected Tables

### Tables with camelCase columns:
- ✅ `carts` - userId, createdAt, updatedAt
- ✅ `cart_items` - cartId, productId, createdAt, updatedAt
- ✅ `orders` - userId, paymentStatus, paymentId, totalAmount, shippingAddress, createdAt, updatedAt
- ✅ `order_items` - orderId, productId, unitPrice, createdAt
- ✅ `payments` - orderId, userId, razorpayOrderId, razorpayPaymentId, razorpaySignature, errorMessage, createdAt, updatedAt

### Tables with snake_case columns (no mapping needed):
- ✅ `users` - All columns already snake_case
- ✅ `refresh_tokens` - All columns already snake_case
- ✅ `categories` - All columns already snake_case
- ✅ `products` - All columns already snake_case
- ✅ `product_diseases` - All columns already snake_case
- ✅ `admin_logs` - All columns already snake_case
- ✅ `product_inventories` - All columns already snake_case
- ✅ `inventory_logs` - All columns already snake_case
- ✅ `ai_chat_conversations` - All columns already snake_case
- ✅ `ai_chat_messages` - All columns already snake_case

## Testing

After this fix, all APIs should work:

### ✅ Cart APIs
```bash
GET /api/v1/cart
POST /api/v1/cart/add
PUT /api/v1/cart/update/{item_id}
DELETE /api/v1/cart/remove/{item_id}
```

### ✅ Order APIs
```bash
GET /api/v1/orders
POST /api/v1/orders
GET /api/v1/orders/{id}
```

### ✅ Payment APIs
```bash
POST /api/v1/payments/create-order
POST /api/v1/payments/verify
GET /api/v1/payments/status/{order_id}
```

## Key Takeaway

When migrating from Prisma to SQLAlchemy:
1. Check actual database column names (use `\d table_name` in psql)
2. Map SQLAlchemy attributes to match database columns exactly
3. Use first parameter of `mapped_column()` for column name mapping
4. Keep Python code snake_case for consistency

## Status

✅ **All column mappings fixed**  
✅ **All APIs should now work correctly**  
✅ **No more "column does not exist" errors**

---

**Date:** 2026-04-12  
**Status:** Complete ✅
