# 🔧 Index Definition Fix - FINAL

## Issue Resolved

**Error:** `Can't create Index on table 'carts': no column named 'user_id' is present.`

**Root Cause:** Index definitions were using Python attribute names (snake_case) instead of actual database column names (camelCase).

## Solution Applied

Updated all index definitions to use the actual database column names.

### Files Fixed

#### 1. `src/models/cart.py` ✅
```python
# Before
Index("idx_cart_user_id", "user_id")

# After  
Index("idx_cart_user_id", "userId")
```

**All indexes fixed:**
- `idx_cart_user_id` → uses `userId`
- `idx_cart_item_cart_id` → uses `cartId`
- `idx_cart_item_product_id` → uses `productId`

#### 2. `src/models/order.py` ✅
```python
# Before
Index("idx_order_user_id", "user_id")
Index("idx_order_payment_status", "payment_status")

# After
Index("idx_order_user_id", "userId")
Index("idx_order_payment_status", "paymentStatus")
```

**All indexes fixed:**
- `idx_order_user_id` → uses `userId`
- `idx_order_payment_status` → uses `paymentStatus`
- `idx_order_item_order_id` → uses `orderId`
- `idx_order_item_product_id` → uses `productId`

#### 3. `src/models/payment.py` ✅
```python
# Before
Index("idx_payment_order_id", "order_id")
Index("idx_payment_razorpay_order_id", "razorpay_order_id")

# After
Index("idx_payment_order_id", "orderId")
Index("idx_payment_razorpay_order_id", "razorpayOrderId")
```

**All indexes fixed:**
- `idx_payment_order_id` → uses `orderId`
- `idx_payment_user_id` → uses `userId`
- `idx_payment_razorpay_order_id` → uses `razorpayOrderId`
- `idx_payment_razorpay_payment_id` → uses `razorpayPaymentId`

#### 4. Other Models ✅
- `src/models/user.py` - Already correct (snake_case columns)
- `src/models/product.py` - Already correct (snake_case columns)
- `src/models/admin.py` - Already correct (snake_case columns)
- `src/models/ai_chat.py` - Already correct (snake_case columns)

## Complete Column & Index Mapping

### Tables with camelCase columns (Prisma-created):

| Table | Python Attribute | DB Column | Index Name |
|-------|-----------------|-----------|------------|
| **carts** | user_id | userId | idx_cart_user_id |
| **cart_items** | cart_id | cartId | idx_cart_item_cart_id |
| **cart_items** | product_id | productId | idx_cart_item_product_id |
| **orders** | user_id | userId | idx_order_user_id |
| **orders** | payment_status | paymentStatus | idx_order_payment_status |
| **order_items** | order_id | orderId | idx_order_item_order_id |
| **order_items** | product_id | productId | idx_order_item_product_id |
| **payments** | order_id | orderId | idx_payment_order_id |
| **payments** | user_id | userId | idx_payment_user_id |
| **payments** | razorpay_order_id | razorpayOrderId | idx_payment_razorpay_order_id |
| **payments** | razorpay_payment_id | razorpayPaymentId | idx_payment_razorpay_payment_id |

### Tables with snake_case columns (no mapping needed):
- users
- refresh_tokens
- categories
- products
- product_diseases
- admin_logs
- product_inventories
- inventory_logs
- ai_chat_conversations
- ai_chat_messages

## Key Learnings

1. **Column Mapping:** Use first parameter in `mapped_column()`
   ```python
   user_id: Mapped[str] = mapped_column("userId", String(36), ...)
   ```

2. **Index Mapping:** Use actual database column name in `Index()`
   ```python
   Index("idx_cart_user_id", "userId")
   ```

3. **Foreign Key Mapping:** Use actual database column name
   ```python
   ForeignKey("users.id")  # Table name is always correct
   ```

## Testing

Run the application:
```bash
python run_app.py
```

Expected output:
```
🚀 Starting FastAPI Auth Service...
📂 Initializing database schema...
✅ Database schema initialized
✅ Database connection successful
✅ FastAPI service started successfully
INFO: Uvicorn running on http://0.0.0.0:8000
```

## Status

✅ **All column mappings complete**  
✅ **All index definitions fixed**  
✅ **Application should start without errors**  
✅ **All APIs ready to test**

---

**Date:** 2026-04-12  
**Status:** COMPLETE ✅  
**Next:** Test all API endpoints
