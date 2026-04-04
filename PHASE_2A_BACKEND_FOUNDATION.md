# Phase 2A: Backend Foundation - Cart & Orders Implementation

**Document Purpose:** Complete backend implementation guide for Phase 2 (cart and order management)  
**Target Timeline:** 4-5 hours  
**Frontend Parallel:** Phase 2B runs simultaneously to save time  
**Prerequisites:** Phase 1 backend complete (auth + products working)

---

## Overview

Phase 2A builds the shopping cart and order management infrastructure:
- **Cart System:** Add items, remove items, update quantities, clear cart
- **Order System:** Create orders from cart, retrieve order history, manage order status
- **Database:** Expand Prisma schema with Order, OrderItem, Cart, CartItem models
- **API Endpoints:** 7 new endpoints (4 cart + 3 order)
- **Service Architecture:** Follow established Controllers → Services → Core pattern

---

## STEP 1: Update Prisma Schema (15 mins)

**File:** `D:\My Projects\nursery-backend\prisma\schema.prisma`

### Goal
Add Cart, CartItem, Order, OrderItem models with proper relationships and status enums.

### Implementation

Find the existing schema and add these models before `@@db.index` indexes at the bottom:

#### A. Add Enums

```prisma
enum OrderStatus {
  PENDING
  CONFIRMED
  SHIPPED
  DELIVERED
  CANCELLED
}
```

Insert this after your existing enums (if any) or at the top of the model definitions.

#### B. Add Cart and CartItem Models

```prisma
model Cart {
  id        String     @id @default(cuid())
  userId    String     @unique  // One cart per user
  user      User       @relation(fields: [userId], references: [id], onDelete: Cascade)
  
  items     CartItem[]
  
  createdAt DateTime   @default(now())
  updatedAt DateTime   @updatedAt
  
  @@index([userId])
}

model CartItem {
  id        String     @id @default(cuid())
  cartId    String
  cart      Cart       @relation(fields: [cartId], references: [id], onDelete: Cascade)
  
  productId String
  product   Product    @relation(fields: [productId], references: [id])
  
  quantity  Int        @default(1)
  
  createdAt DateTime   @default(now())
  updatedAt DateTime   @updatedAt
  
  @@unique([cartId, productId])  // Prevent duplicate items in cart
  @@index([cartId])
  @@index([productId])
}
```

#### C. Add Order and OrderItem Models

```prisma
model Order {
  id        String     @id @default(cuid())
  userId    String
  user      User       @relation(fields: [userId], references: [id])
  
  items     OrderItem[]
  
  status    OrderStatus @default(PENDING)
  
  totalAmount      Float
  shippingAddress  String?
  notes            String?
  
  createdAt DateTime   @default(now())
  updatedAt DateTime   @updatedAt
  
  @@index([userId])
  @@index([status])
}

model OrderItem {
  id        String     @id @default(cuid())
  orderId   String
  order     Order      @relation(fields: [orderId], references: [id], onDelete: Cascade)
  
  productId String
  product   Product    @relation(fields: [productId], references: [id])
  
  quantity  Int
  unitPrice Float      // Snapshot of product price at purchase time
  subtotal  Float      // quantity * unitPrice
  
  createdAt DateTime   @default(now())
  
  @@index([orderId])
  @@index([productId])
}
```

#### D. Update User Model

Add these relations to the existing `User` model:

```prisma
model User {
  // ... existing fields ...
  
  // Add these new relations
  cart      Cart?      // One-to-one (nullable - created on first cart action)
  orders    Order[]    // One-to-many
  
  // ... rest of existing User fields ...
}
```

#### E. Update Product Model

Add Cart and Order relations to the existing `Product` model:

```prisma
model Product {
  // ... existing fields ...
  
  // Add these new relations
  cartItems CartItem[]   // Many-to-many through CartItem
  orderItems OrderItem[] // Many-to-many through OrderItem
  
  // ... rest of existing Product fields ...
}
```

### Verify Schema Structure

Your schema should have this structure:
```
models:
  ├─ User (updated with cart, orders relations)
  ├─ Product (updated with cartItems, orderItems relations)
  ├─ Category (unchanged)
  ├─ ProductDisease (unchanged)
  ├─ RefreshToken (unchanged)
  ├─ Cart (NEW)
  ├─ CartItem (NEW)
  ├─ Order (NEW)
  ├─ OrderItem (NEW)

enums:
  ├─ OrderStatus (NEW)
  └─ (any existing enums)
```

### Run Migration

```bash
cd D:\My Projects\nursery-backend
prisma migrate dev --name add_cart_and_orders
```

Expected output:
```
✓ Created migration: ./prisma/migrations/xxx_add_cart_and_orders/migration.sql
Your database has been successfully migrated to `xxx_add_cart_and_orders`.
```

### Verify in Prisma Studio (Optional)

```bash
prisma studio
```

Visit `http://localhost:5555` and verify all new tables exist: Cart, CartItem, Order, OrderItem.

---

## STEP 2: Create Data Contracts (20 mins)

**File:** `D:\My Projects\nursery-backend\src\data_contracts\api_request_response.py`

### Goal
Define request/response models for cart and order endpoints with proper camelCase aliases for API responses.

### Implementation

Add these models to the existing data_contracts file:

```python
# ==================== CART MODELS ====================

class CartItemAddRequest(BaseModel):
    product_id: str = Field(..., description="Product ID to add to cart")
    quantity: int = Field(default=1, ge=1, le=100, description="Quantity (1-100)")

class CartItemUpdateRequest(BaseModel):
    quantity: int = Field(..., ge=1, le=100, description="New quantity (1-100)")

class CartItemResponse(BaseModel):
    id: str = Field(alias="id")
    product_id: str = Field(alias="productId")
    product_name: str = Field(alias="productName")
    product_image: Optional[str] = Field(None, alias="productImage")
    price: float = Field(alias="price")
    quantity: int = Field(alias="quantity")
    subtotal: float = Field(alias="subtotal")  # price * quantity
    
    class Config:
        from_attributes = True
        populate_by_name = True

class CartResponse(BaseModel):
    id: str = Field(alias="id")
    user_id: str = Field(alias="userId")
    items: List[CartItemResponse] = Field(alias="items")
    total_amount: float = Field(alias="totalAmount")
    total_items: int = Field(alias="totalItems")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    
    class Config:
        from_attributes = True
        populate_by_name = True

# ==================== ORDER MODELS ====================

class OrderItemResponse(BaseModel):
    id: str = Field(alias="id")
    product_id: str = Field(alias="productId")
    product_name: str = Field(alias="productName")
    product_image: Optional[str] = Field(None, alias="productImage")
    quantity: int = Field(alias="quantity")
    unit_price: float = Field(alias="unitPrice")
    subtotal: float = Field(alias="subtotal")
    
    class Config:
        from_attributes = True
        populate_by_name = True

class CreateOrderRequest(BaseModel):
    shipping_address: str = Field(..., min_length=10, max_length=500, description="Delivery address")
    notes: Optional[str] = Field(None, max_length=500, description="Special instructions")
    
    @validator('shipping_address')
    def validate_address(cls, v):
        if len(v.strip()) < 10:
            raise ValueError("Address must be at least 10 characters")
        return v

class OrderResponse(BaseModel):
    id: str = Field(alias="id")
    user_id: str = Field(alias="userId")
    status: str = Field(alias="status")  # "PENDING", "CONFIRMED", "SHIPPED", "DELIVERED"
    items: List[OrderItemResponse] = Field(alias="items")
    total_amount: float = Field(alias="totalAmount")
    shipping_address: str = Field(alias="shippingAddress")
    notes: Optional[str] = Field(None, alias="notes")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    
    class Config:
        from_attributes = True
        populate_by_name = True

class OrderListResponse(BaseModel):
    orders: List[OrderResponse]
    total: int
    page: int
    per_page: int
    
    class Config:
        from_attributes = True
        populate_by_name = True
```

---

## STEP 3: Build Cart Core Logic (45 mins)

**File:** `D:\My Projects\nursery-backend\src\core\cart_core.py` (NEW FILE)

### Goal
Implement cart business logic: add items, remove items, update quantities, fetch cart.

### Implementation

Create new file with this content:

```python
from typing import Optional, Dict, Any
from sqlalchemy.exc import IntegrityError
from prisma import Prisma
from prisma.models import Cart, CartItem, Product

class CartCore:
    def __init__(self, db: Prisma):
        self.db = db
    
    async def get_or_create_cart(self, user_id: str) -> Cart:
        """Get user's cart or create if doesn't exist."""
        cart = await self.db.cart.find_unique(where={"userId": user_id})
        
        if not cart:
            cart = await self.db.cart.create(data={"userId": user_id})
        
        return cart
    
    async def add_to_cart(
        self, 
        user_id: str, 
        product_id: str, 
        quantity: int
    ) -> Dict[str, Any]:
        """
        Add item to cart or increment quantity if exists.
        
        Args:
            user_id: User ID
            product_id: Product ID
            quantity: Quantity to add
        
        Returns:
            Updated cart data
        
        Raises:
            ValueError: If product not found or invalid quantity
        """
        # Validate product exists
        product = await self.db.product.find_unique(where={"id": product_id})
        if not product:
            raise ValueError(f"Product not found: {product_id}")
        
        if quantity < 1:
            raise ValueError("Quantity must be at least 1")
        
        # Get or create cart
        cart = await self.get_or_create_cart(user_id)
        
        # Check if item already in cart
        existing_item = await self.db.cartitem.find_unique(
            where={"cartId_productId": {"cartId": cart.id, "productId": product_id}}
        )
        
        if existing_item:
            # Update quantity
            await self.db.cartitem.update(
                where={"id": existing_item.id},
                data={"quantity": existing_item.quantity + quantity}
            )
        else:
            # Add new item
            await self.db.cartitem.create(
                data={
                    "cartId": cart.id,
                    "productId": product_id,
                    "quantity": quantity
                }
            )
        
        # Return updated cart
        return await self._fetch_cart_data(cart.id)
    
    async def get_cart(self, user_id: str) -> Dict[str, Any]:
        """
        Fetch user's cart with all items and calculations.
        
        Returns:
            {
                'id': 'cart_id',
                'user_id': 'user_id',
                'items': [
                    {
                        'id': 'item_id',
                        'product_id': 'prod_id',
                        'product_name': 'name',
                        'price': 29.99,
                        'quantity': 2,
                        'subtotal': 59.98
                    }
                ],
                'total_amount': 59.98,
                'total_items': 2
            }
        
        Raises:
            ValueError: If user not found or cart doesn't exist
        """
        cart = await self.db.cart.find_unique(where={"userId": user_id})
        
        if not cart:
            # Return empty cart structure
            return {
                'id': None,
                'user_id': user_id,
                'items': [],
                'total_amount': 0.0,
                'total_items': 0
            }
        
        return await self._fetch_cart_data(cart.id)
    
    async def remove_from_cart(self, user_id: str, cart_item_id: str) -> Dict[str, Any]:
        """
        Remove item from cart.
        
        Args:
            user_id: User ID (for authorization)
            cart_item_id: CartItem ID to remove
        
        Returns:
            Updated cart data
        
        Raises:
            ValueError: If item not found or doesn't belong to user
        """
        # Verify item exists and belongs to user's cart
        item = await self.db.cartitem.find_unique(where={"id": cart_item_id})
        if not item:
            raise ValueError(f"Cart item not found: {cart_item_id}")
        
        # Verify cart belongs to user
        cart = await self.db.cart.find_unique(where={"id": item.cartId})
        if not cart or cart.userId != user_id:
            raise ValueError("Unauthorized: Item does not belong to user's cart")
        
        # Delete item
        await self.db.cartitem.delete(where={"id": cart_item_id})
        
        # Return updated cart
        return await self._fetch_cart_data(cart.id)
    
    async def update_cart_item(
        self, 
        user_id: str, 
        cart_item_id: str, 
        quantity: int
    ) -> Dict[str, Any]:
        """
        Update item quantity or remove if quantity is 0.
        
        Args:
            user_id: User ID (for authorization)
            cart_item_id: CartItem ID
            quantity: New quantity (0 = remove item)
        
        Returns:
            Updated cart data
        
        Raises:
            ValueError: If invalid quantity or item not found
        """
        if quantity < 0:
            raise ValueError("Quantity cannot be negative")
        
        # Verify item exists
        item = await self.db.cartitem.find_unique(where={"id": cart_item_id})
        if not item:
            raise ValueError(f"Cart item not found: {cart_item_id}")
        
        # Verify cart belongs to user
        cart = await self.db.cart.find_unique(where={"id": item.cartId})
        if not cart or cart.userId != user_id:
            raise ValueError("Unauthorized: Item does not belong to user's cart")
        
        if quantity == 0:
            # Remove item
            await self.db.cartitem.delete(where={"id": cart_item_id})
        else:
            # Update quantity
            await self.db.cartitem.update(
                where={"id": cart_item_id},
                data={"quantity": quantity}
            )
        
        # Return updated cart
        return await self._fetch_cart_data(cart.id)
    
    async def clear_cart(self, user_id: str) -> None:
        """
        Clear all items from user's cart.
        
        Used during checkout.
        """
        cart = await self.db.cart.find_unique(where={"userId": user_id})
        if cart:
            await self.db.cartitem.delete_many(where={"cartId": cart.id})
    
    async def _fetch_cart_data(self, cart_id: str) -> Dict[str, Any]:
        """
        Helper: Fetch cart with items and calculate totals.
        
        Returns complete cart object with calculations.
        """
        cart = await self.db.cart.find_unique(
            where={"id": cart_id},
            include={"items": {"include": {"product": True}}}
        )
        
        if not cart:
            raise ValueError(f"Cart not found: {cart_id}")
        
        # Calculate totals
        total_amount = 0.0
        total_items = 0
        items_data = []
        
        for item in cart.items:
            subtotal = item.product.price * item.quantity
            total_amount += subtotal
            total_items += item.quantity
            
            items_data.append({
                'id': item.id,
                'product_id': item.product.id,
                'product_name': item.product.name,
                'product_image': item.product.image_url,
                'price': item.product.price,
                'quantity': item.quantity,
                'subtotal': subtotal
            })
        
        return {
            'id': cart.id,
            'user_id': cart.userId,
            'items': items_data,
            'total_amount': round(total_amount, 2),
            'total_items': total_items,
            'created_at': cart.createdAt,
            'updated_at': cart.updatedAt
        }
```

---

## STEP 4: Build Cart Service (20 mins)

**File:** `D:\My Projects\nursery-backend\src\services\cart_service.py` (NEW FILE)

### Goal
Wire CartCore into service layer with error handling and auth checks.

### Implementation

```python
from typing import Dict, Any
from src.core.cart_core import CartCore
from src.plugins.database import get_db

class CartService:
    def __init__(self):
        self.cart_core = CartCore(get_db())
    
    async def add_to_cart(
        self, 
        user_id: str, 
        product_id: str, 
        quantity: int
    ) -> Dict[str, Any]:
        """
        Add item to cart with error handling.
        
        Raises:
            ValueError: If product not found, invalid quantity
        """
        try:
            result = await self.cart_core.add_to_cart(user_id, product_id, quantity)
            return result
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error adding to cart: {str(e)}")
    
    async def get_cart(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's cart.
        
        Returns empty cart if no items.
        """
        try:
            result = await self.cart_core.get_cart(user_id)
            return result
        except Exception as e:
            raise Exception(f"Error fetching cart: {str(e)}")
    
    async def remove_from_cart(self, user_id: str, cart_item_id: str) -> Dict[str, Any]:
        """
        Remove item from cart.
        
        Raises:
            ValueError: If item not found or unauthorized
        """
        try:
            result = await self.cart_core.remove_from_cart(user_id, cart_item_id)
            return result
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error removing from cart: {str(e)}")
    
    async def update_cart_item(
        self, 
        user_id: str, 
        cart_item_id: str, 
        quantity: int
    ) -> Dict[str, Any]:
        """
        Update item quantity.
        
        Set quantity=0 to remove item.
        """
        try:
            result = await self.cart_core.update_cart_item(user_id, cart_item_id, quantity)
            return result
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error updating cart item: {str(e)}")
    
    async def clear_cart(self, user_id: str) -> None:
        """Clear all items from user's cart."""
        try:
            await self.cart_core.clear_cart(user_id)
        except Exception as e:
            raise Exception(f"Error clearing cart: {str(e)}")
```

---

## STEP 5: Build Cart Controller (30 mins)

**File:** `D:\My Projects\nursery-backend\src\controllers\cart_controller.py` (NEW FILE)

### Goal
Create 4 HTTP endpoints for cart operations with auth middleware and error handling.

### Implementation

```python
from fastapi import APIRouter, Depends, HTTPException, status
from src.middlewares.auth_middleware import verify_token
from src.services.cart_service import CartService
from src.data_contracts.api_request_response import (
    CartItemAddRequest,
    CartItemUpdateRequest,
    CartResponse
)

router = APIRouter(prefix="/api/v1", tags=["Cart"])
cart_service = CartService()

# ============== CART ENDPOINTS ==============

@router.post("/cart/add", response_model=CartResponse, status_code=200)
async def add_to_cart(
    request: CartItemAddRequest,
    user_id: str = Depends(verify_token)
):
    """
    Add item to cart or increment quantity if exists.
    
    Auth Required: Yes
    
    Request:
    {
        "product_id": "prod_123",
        "quantity": 2
    }
    
    Response: Updated cart object
    """
    try:
        result = await cart_service.add_to_cart(
            user_id=user_id,
            product_id=request.product_id,
            quantity=request.quantity
        )
        return CartResponse(**result)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/cart", response_model=CartResponse, status_code=200)
async def get_cart(user_id: str = Depends(verify_token)):
    """
    Get user's cart with all items and totals.
    
    Auth Required: Yes
    
    Response: Cart object (empty if no items)
    """
    try:
        result = await cart_service.get_cart(user_id)
        return CartResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.delete("/cart/items/{item_id}", response_model=CartResponse, status_code=200)
async def remove_from_cart(
    item_id: str,
    user_id: str = Depends(verify_token)
):
    """
    Remove item from cart.
    
    Auth Required: Yes
    
    Path Params:
    - item_id: CartItem ID to remove
    
    Response: Updated cart object
    """
    try:
        result = await cart_service.remove_from_cart(user_id, item_id)
        return CartResponse(**result)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.put("/cart/items/{item_id}", response_model=CartResponse, status_code=200)
async def update_cart_item(
    item_id: str,
    request: CartItemUpdateRequest,
    user_id: str = Depends(verify_token)
):
    """
    Update item quantity (set to 0 to remove).
    
    Auth Required: Yes
    
    Path Params:
    - item_id: CartItem ID
    
    Request:
    {
        "quantity": 5
    }
    
    Response: Updated cart object
    """
    try:
        result = await cart_service.update_cart_item(
            user_id=user_id,
            cart_item_id=item_id,
            quantity=request.quantity
        )
        return CartResponse(**result)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
```

---

## STEP 6: Build Order Core Logic (60 mins)

**File:** `D:\My Projects\nursery-backend\src\core\order_core.py` (NEW FILE)

### Goal
Implement order business logic: create order from cart, retrieve orders, get order details.

### Implementation

```python
from typing import Optional, Dict, Any, List
from datetime import datetime
from prisma import Prisma
from prisma.models import Order, OrderStatus

class OrderCore:
    def __init__(self, db: Prisma):
        self.db = db
    
    async def create_order(
        self,
        user_id: str,
        shipping_address: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create order from user's cart.
        
        Steps:
        1. Fetch user's cart
        2. Verify cart is not empty
        3. Create Order record
        4. Create OrderItems (copy from CartItems with price snapshot)
        5. Clear cart
        6. Return order data
        
        Args:
            user_id: User ID
            shipping_address: Shipping address
            notes: Optional notes
        
        Returns:
            Order data with items
        
        Raises:
            ValueError: If cart is empty, user not found
        """
        # Fetch user's cart
        cart = await self.db.cart.find_unique(
            where={"userId": user_id},
            include={"items": {"include": {"product": True}}}
        )
        
        if not cart or len(cart.items) == 0:
            raise ValueError("Cannot create order: cart is empty")
        
        # Calculate total amount
        total_amount = 0.0
        for item in cart.items:
            total_amount += item.product.price * item.quantity
        
        # Create Order
        order = await self.db.order.create(
            data={
                "userId": user_id,
                "status": "PENDING",
                "totalAmount": round(total_amount, 2),
                "shippingAddress": shipping_address,
                "notes": notes
            }
        )
        
        # Create OrderItems (snapshot pricing)
        for cart_item in cart.items:
            unit_price = cart_item.product.price
            subtotal = unit_price * cart_item.quantity
            
            await self.db.orderitem.create(
                data={
                    "orderId": order.id,
                    "productId": cart_item.product.id,
                    "quantity": cart_item.quantity,
                    "unitPrice": unit_price,
                    "subtotal": round(subtotal, 2)
                }
            )
        
        # Clear cart
        await self.db.cartitem.delete_many(where={"cartId": cart.id})
        
        # Return order data
        return await self._fetch_order_data(order.id)
    
    async def get_user_orders(
        self,
        user_id: str,
        page: int = 1,
        per_page: int = 10
    ) -> Dict[str, Any]:
        """
        Get user's orders with pagination.
        
        Args:
            user_id: User ID
            page: Page number (1-indexed)
            per_page: Items per page
        
        Returns:
            {
                'orders': [...],
                'total': 25,
                'page': 1,
                'per_page': 10
            }
        """
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 10
        
        skip = (page - 1) * per_page
        
        # Count total orders
        total = await self.db.order.count(where={"userId": user_id})
        
        # Fetch orders
        orders = await self.db.order.find_many(
            where={"userId": user_id},
            include={"items": {"include": {"product": True}}},
            order_by={"createdAt": "desc"},
            skip=skip,
            take=per_page
        )
        
        # Format orders
        orders_data = []
        for order in orders:
            orders_data.append(await self._format_order(order))
        
        return {
            'orders': orders_data,
            'total': total,
            'page': page,
            'per_page': per_page
        }
    
    async def get_order_details(self, user_id: str, order_id: str) -> Dict[str, Any]:
        """
        Get order details with items.
        
        Args:
            user_id: User ID (for authorization)
            order_id: Order ID
        
        Returns:
            Order data with all details
        
        Raises:
            ValueError: If order not found or doesn't belong to user
        """
        order = await self.db.order.find_unique(
            where={"id": order_id},
            include={"items": {"include": {"product": True}}}
        )
        
        if not order:
            raise ValueError(f"Order not found: {order_id}")
        
        # Verify user owns order
        if order.userId != user_id:
            raise ValueError("Unauthorized: Order does not belong to user")
        
        return await self._format_order(order)
    
    async def _format_order(self, order) -> Dict[str, Any]:
        """
        Format order record into API response format.
        
        Helper method.
        """
        items_data = []
        for item in order.items:
            items_data.append({
                'id': item.id,
                'product_id': item.product.id,
                'product_name': item.product.name,
                'product_image': item.product.image_url,
                'quantity': item.quantity,
                'unit_price': item.unitPrice,
                'subtotal': item.subtotal
            })
        
        return {
            'id': order.id,
            'user_id': order.userId,
            'status': order.status,
            'items': items_data,
            'total_amount': order.totalAmount,
            'shipping_address': order.shippingAddress,
            'notes': order.notes,
            'created_at': order.createdAt,
            'updated_at': order.updatedAt
        }
    
    async def update_order_status(self, order_id: str, new_status: str) -> Dict[str, Any]:
        """
        Update order status (admin only).
        
        Valid statuses: PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED
        
        Raises:
            ValueError: If invalid status or order not found
        """
        valid_statuses = ["PENDING", "CONFIRMED", "SHIPPED", "DELIVERED", "CANCELLED"]
        
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        order = await self.db.order.update(
            where={"id": order_id},
            data={"status": new_status},
            include={"items": {"include": {"product": True}}}
        )
        
        return await self._format_order(order)
```

---

## STEP 7: Build Order Service & Controller (50 mins)

**File Part 1:** `D:\My Projects\nursery-backend\src\services\order_service.py` (NEW FILE)

```python
from typing import Dict, Any
from src.core.order_core import OrderCore
from src.plugins.database import get_db

class OrderService:
    def __init__(self):
        self.order_core = OrderCore(get_db())
    
    async def create_order(
        self,
        user_id: str,
        shipping_address: str,
        notes: str = None
    ) -> Dict[str, Any]:
        """
        Create order from cart.
        
        Raises:
            ValueError: If cart empty or invalid address
        """
        try:
            result = await self.order_core.create_order(
                user_id, shipping_address, notes
            )
            return result
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error creating order: {str(e)}")
    
    async def get_user_orders(
        self,
        user_id: str,
        page: int = 1,
        per_page: int = 10
    ) -> Dict[str, Any]:
        """Get user's orders with pagination."""
        try:
            result = await self.order_core.get_user_orders(
                user_id, page, per_page
            )
            return result
        except Exception as e:
            raise Exception(f"Error fetching orders: {str(e)}")
    
    async def get_order_details(
        self,
        user_id: str,
        order_id: str
    ) -> Dict[str, Any]:
        """Get order details."""
        try:
            result = await self.order_core.get_order_details(user_id, order_id)
            return result
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error fetching order: {str(e)}")
```

**File Part 2:** `D:\My Projects\nursery-backend\src\controllers\order_controller.py` (NEW FILE)

```python
from fastapi import APIRouter, Depends, HTTPException, status, Query
from src.middlewares.auth_middleware import verify_token
from src.services.order_service import OrderService
from src.data_contracts.api_request_response import (
    CreateOrderRequest,
    OrderResponse,
    OrderListResponse
)

router = APIRouter(prefix="/api/v1", tags=["Orders"])
order_service = OrderService()

# ============== ORDER ENDPOINTS ==============

@router.post("/orders", response_model=OrderResponse, status_code=201)
async def create_order(
    request: CreateOrderRequest,
    user_id: str = Depends(verify_token)
):
    """
    Create order from user's cart.
    
    Auth Required: Yes
    
    Request:
    {
        "shipping_address": "123 Main St, City, State 12345",
        "notes": "Please deliver after 6 PM"
    }
    
    Response: Created order (status 201)
    """
    try:
        result = await order_service.create_order(
            user_id=user_id,
            shipping_address=request.shipping_address,
            notes=request.notes
        )
        return OrderResponse(**result)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/orders", response_model=OrderListResponse, status_code=200)
async def get_user_orders(
    user_id: str = Depends(verify_token),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100)
):
    """
    Get user's orders with pagination.
    
    Auth Required: Yes
    
    Query Params:
    - page: Page number (default 1)
    - per_page: Items per page (default 10, max 100)
    
    Response: List of orders + pagination info
    """
    try:
        result = await order_service.get_user_orders(
            user_id=user_id,
            page=page,
            per_page=per_page
        )
        return OrderListResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/orders/{order_id}", response_model=OrderResponse, status_code=200)
async def get_order_details(
    order_id: str,
    user_id: str = Depends(verify_token)
):
    """
    Get order details.
    
    Auth Required: Yes
    
    Path Params:
    - order_id: Order ID
    
    Response: Order data with items
    """
    try:
        result = await order_service.get_order_details(
            user_id=user_id,
            order_id=order_id
        )
        return OrderResponse(**result)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
```

---

## STEP 8: Update main.py (5 mins)

**File:** `D:\My Projects\nursery-backend\src\main.py`

### Goal
Register cart and order routers so endpoints are available.

### Implementation

Find the section where routers are registered in `main.py` and add these imports and registrations:

```python
# Add these imports at the top (with other controller imports)
from src.controllers.cart_controller import router as cart_router
from src.controllers.order_controller import router as order_router

# In the app creation section (in the startup/lifespan context), add these lines:
# Usually after other router includes, around line 50-80

app.include_router(cart_router)
app.include_router(order_router)
```

**Example of how it should look:**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.controllers.auth_controller import router as auth_router
from src.controllers.product_controller import router as product_router
from src.controllers.cart_controller import router as cart_router  # NEW
from src.controllers.order_controller import router as order_router  # NEW

app = FastAPI(...)

# ... CORS setup ...

# Include routers
app.include_router(auth_router)
app.include_router(product_router)
app.include_router(cart_router)   # NEW
app.include_router(order_router)  # NEW

# ... rest of code ...
```

---

## Testing Checklist

After implementing all steps, verify:

### Database
- [ ] Run `prisma studio` and confirm Cart, CartItem, Order, OrderItem tables exist
- [ ] Verify relationships: User→Cart, User→Orders, Cart→CartItems, Order→OrderItems

### API Endpoints

**Cart Endpoints:**
- [ ] POST /api/v1/cart/add - Add item to cart
- [ ] GET /api/v1/cart - Fetch user's cart
- [ ] DELETE /api/v1/cart/items/{item_id} - Remove item
- [ ] PUT /api/v1/cart/items/{item_id} - Update quantity

**Order Endpoints:**
- [ ] POST /api/v1/orders - Create order from cart
- [ ] GET /api/v1/orders - List user's orders
- [ ] GET /api/v1/orders/{id} - Get order details

### Functionality Tests

```bash
# Using Postman or curl:

# 1. Get auth token (use existing login endpoint)
# POST /api/v1/auth/login

# 2. Create cart with auth token
# POST /api/v1/cart/add
# Header: Authorization: Bearer <token>
# Body: {"product_id": "<valid_product_id>", "quantity": 2}

# 3. Verify response has cart structure (id, items[], total_amount)

# 4. Get cart
# GET /api/v1/cart
# Header: Authorization: Bearer <token>

# 5. Update item quantity
# PUT /api/v1/cart/items/<item_id>
# Body: {"quantity": 5}

# 6. Create order
# POST /api/v1/orders
# Header: Authorization: Bearer <token>
# Body: {"shipping_address": "123 Main St, City 12345", "notes": "..."}

# 7. Get orders
# GET /api/v1/orders?page=1&per_page=10

# 8. Get order details
# GET /api/v1/orders/<order_id>
```

---

## Error Handling Summary

| Scenario | Error Code | Message |
|----------|-----------|---------|
| Product not found | 400 | "Product not found: {id}" |
| Empty cart checkout | 400 | "Cannot create order: cart is empty" |
| Item not found | 400 | "Cart item not found: {id}" |
| Unauthorized access | 400 | "Unauthorized: Item/Order does not belong to user" |
| Invalid quantity | 400 | "Quantity must be at least 1" |
| Invalid address | 400 | "Address must be at least 10 characters" |
| Server error | 500 | "Error: {exception message}" |

---

## Summary

| Step | File(s) | Time | Status |
|------|---------|------|--------|
| 1 | prisma/schema.prisma | 15 min | Setup database |
| 2 | api_request_response.py | 20 min | Define request/response models |
| 3 | cart_core.py | 45 min | Implement cart logic |
| 4 | cart_service.py | 20 min | Wire service layer |
| 5 | cart_controller.py | 30 min | Create 4 cart endpoints |
| 6 | order_core.py | 60 min | Implement order logic |
| 7 | order_service.py, order_controller.py | 50 min | Create 3 order endpoints |
| 8 | main.py | 5 min | Register routers |
| **TOTAL** | **8 files** | **4-5 hours** | **Complete Phase 2A** |

---

## Next: Phase 2B

After Phase 2A is complete, frontend (Phase 2B) will:
- Create useCart hook for cart state management
- Build cart page (/cart)
- Build checkout page (/checkout)
- Build order history (/orders)
- Build order details (/orders/{id})
- Integrate with these new backend endpoints

Phase 2B can run **in parallel** to save time—frontend can start while you're implementing backend steps 6-8.
