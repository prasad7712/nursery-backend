"""Order business logic core"""
from typing import Optional, Dict, Any, List

from src.plugins.database import db


class OrderCore:
    """Order domain logic using Prisma ORM"""
    
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
            Order dictionary with items
        
        Raises:
            ValueError: If cart is empty
        """
        # Fetch user's cart
        cart = await db.client.cart.find_unique(
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
        order = await db.client.order.create(
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
            
            await db.client.orderitem.create(
                data={
                    "orderId": order.id,
                    "productId": cart_item.product.id,
                    "quantity": cart_item.quantity,
                    "unitPrice": unit_price,
                    "subtotal": round(subtotal, 2)
                }
            )
        
        # Clear cart
        await db.client.cartitem.delete_many(where={"cartId": cart.id})
        
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
        
        # Count total orders
        total = await db.client.order.count(where={"userId": user_id})
        
        # Fetch all orders for user (will sort in Python)
        all_orders = await db.client.order.find_many(
            where={"userId": user_id},
            include={"items": {"include": {"product": True}}}
        )
        
        # Sort by createdAt descending (newest first)
        all_orders.sort(key=lambda o: o.createdAt, reverse=True)
        
        # Apply pagination
        paginated_orders = all_orders[(page - 1) * per_page : page * per_page]
        
        # Format orders
        orders_data = []
        for order in paginated_orders:
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
            Order dictionary with all details
        
        Raises:
            ValueError: If order not found or doesn't belong to user
        """
        order = await db.client.order.find_unique(
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
    
    async def _fetch_order_data(self, order_id: str) -> Dict[str, Any]:
        """
        Helper: Fetch order with items.
        """
        order = await db.client.order.find_unique(
            where={"id": order_id},
            include={"items": {"include": {"product": True}}}
        )
        
        if not order:
            raise ValueError(f"Order not found: {order_id}")
        
        return await self._format_order(order)
    
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
        
        order = await db.client.order.update(
            where={"id": order_id},
            data={"status": new_status},
            include={"items": {"include": {"product": True}}}
        )
        
        return await self._format_order(order)
