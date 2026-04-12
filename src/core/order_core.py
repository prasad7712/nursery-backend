"""Order business logic core"""
from typing import Optional, Dict, Any, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.cart import Cart, CartItem
from src.models.order import Order, OrderItem
from src.models.product import Product


class OrderCore:
    """Order domain logic using SQLAlchemy ORM"""
    
    async def create_order(
        self,
        session: AsyncSession,
        user_id: str,
        shipping_address: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create order from user's cart"""
        # Fetch user's cart
        result = await session.execute(select(Cart).where(Cart.user_id == user_id))
        cart = result.scalar_one_or_none()
        
        if not cart:
            raise ValueError("Cannot create order: cart is empty")
        
        # Fetch cart items
        result = await session.execute(select(CartItem).where(CartItem.cart_id == cart.id))
        cart_items = result.scalars().all()
        
        if not cart_items:
            raise ValueError("Cannot create order: cart is empty")
        
        # Calculate total amount
        total_amount = 0.0
        for cart_item in cart_items:
            result = await session.execute(select(Product).where(Product.id == cart_item.product_id))
            product = result.scalar_one_or_none()
            if product:
                total_amount += product.price * cart_item.quantity
        
        # Create Order
        order = Order(
            id=str(__import__('uuid').uuid4()),
            user_id=user_id,
            status="PENDING",
            total_amount=round(total_amount, 2),
            shipping_address=shipping_address,
            notes=notes
        )
        
        session.add(order)
        await session.commit()
        await session.refresh(order)
        
        # Create OrderItems (snapshot pricing)
        for cart_item in cart_items:
            result = await session.execute(select(Product).where(Product.id == cart_item.product_id))
            product = result.scalar_one_or_none()
            
            if product:
                unit_price = product.price
                subtotal = unit_price * cart_item.quantity
                
                order_item = OrderItem(
                    id=str(__import__('uuid').uuid4()),
                    order_id=order.id,
                    product_id=product.id,
                    quantity=cart_item.quantity,
                    unit_price=unit_price,
                    subtotal=round(subtotal, 2)
                )
                session.add(order_item)
        
        await session.commit()
        
        # Clear cart
        result = await session.execute(select(CartItem).where(CartItem.cart_id == cart.id))
        cart_items_to_delete = result.scalars().all()
        
        for item in cart_items_to_delete:
            await session.delete(item)
        
        await session.commit()
        
        # Return order data
        return await self._fetch_order_data(session, order.id)
    
    async def get_user_orders(
        self,
        session: AsyncSession,
        user_id: str,
        page: int = 1,
        per_page: int = 10
    ) -> Dict[str, Any]:
        """Get user's orders with pagination"""
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 10
        
        # Count total orders
        result = await session.execute(
            select(__import__('sqlalchemy').func.count(Order.id)).where(Order.user_id == user_id)
        )
        total = result.scalar() or 0
        
        # Fetch all orders for user
        result = await session.execute(
            select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
        )
        all_orders = result.scalars().all()
        
        # Apply pagination
        paginated_orders = all_orders[(page - 1) * per_page : page * per_page]
        
        # Format orders
        orders_data = []
        for order in paginated_orders:
            orders_data.append(await self._format_order(session, order))
        
        return {
            'orders': orders_data,
            'total': total,
            'page': page,
            'per_page': per_page
        }
    
    async def get_order_details(self, session: AsyncSession, user_id: str, order_id: str) -> Dict[str, Any]:
        """Get order details with items"""
        result = await session.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        
        if not order:
            raise ValueError(f"Order not found: {order_id}")
        
        # Verify user owns order
        if order.user_id != user_id:
            raise ValueError("Unauthorized: Order does not belong to user")
        
        return await self._format_order(session, order)
    
    async def _format_order(self, session: AsyncSession, order: Order) -> Dict[str, Any]:
        """Format order record into API response format"""
        # Fetch order items
        result = await session.execute(select(OrderItem).where(OrderItem.order_id == order.id))
        order_items = result.scalars().all()
        
        items_data = []
        for item in order_items:
            result = await session.execute(select(Product).where(Product.id == item.product_id))
            product = result.scalar_one_or_none()
            
            if product:
                items_data.append({
                    'id': item.id,
                    'product_id': product.id,
                    'product_name': product.name,
                    'product_image': product.image_url,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'subtotal': item.subtotal
                })
        
        return {
            'id': order.id,
            'user_id': order.user_id,
            'status': order.status.value if order.status else "PENDING",
            'items': items_data,
            'total_amount': order.total_amount,
            'shipping_address': order.shipping_address,
            'notes': order.notes,
            'created_at': order.created_at,
            'updated_at': order.updated_at
        }
    
    async def _fetch_order_data(self, session: AsyncSession, order_id: str) -> Dict[str, Any]:
        """Helper: Fetch order with items"""
        result = await session.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        
        if not order:
            raise ValueError(f"Order not found: {order_id}")
        
        return await self._format_order(session, order)
    
    async def update_order_status(self, session: AsyncSession, order_id: str, new_status: str) -> Dict[str, Any]:
        """Update order status (admin only)"""
        valid_statuses = ["PENDING", "CONFIRMED", "SHIPPED", "DELIVERED", "CANCELLED"]
        
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        result = await session.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        
        if not order:
            raise ValueError(f"Order not found: {order_id}")
        
        order.status = new_status
        session.add(order)
        await session.commit()
        
        return await self._fetch_order_data(session, order.id)


# Singleton instance
order_core = OrderCore()
