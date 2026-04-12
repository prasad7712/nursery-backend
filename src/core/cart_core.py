"""Cart business logic core"""
from typing import Optional, Dict, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.cart import Cart, CartItem
from src.models.product import Product


class CartCore:
    """Cart domain logic using SQLAlchemy ORM"""
    
    async def get_or_create_cart(self, session: AsyncSession, user_id: str) -> Dict[str, Any]:
        """Get user's cart or create if doesn't exist"""
        result = await session.execute(select(Cart).where(Cart.user_id == user_id))
        cart = result.scalar_one_or_none()
        
        if not cart:
            cart = Cart(id=str(__import__('uuid').uuid4()), user_id=user_id)
            session.add(cart)
            await session.commit()
            await session.refresh(cart)
        
        return await self._fetch_cart_data(session, cart.id)
    
    async def add_to_cart(
        self, 
        session: AsyncSession,
        user_id: str, 
        product_id: str, 
        quantity: int
    ) -> Dict[str, Any]:
        """Add item to cart or increment quantity if exists"""
        # Validate product exists
        result = await session.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()
        
        if not product:
            raise ValueError(f"Product not found: {product_id}")
        
        if quantity < 1 or quantity > 100:
            raise ValueError("Quantity must be between 1 and 100")
        
        # Get or create cart
        result = await session.execute(select(Cart).where(Cart.user_id == user_id))
        cart = result.scalar_one_or_none()
        
        if not cart:
            cart = Cart(id=str(__import__('uuid').uuid4()), user_id=user_id)
            session.add(cart)
            await session.commit()
            await session.refresh(cart)
        
        # Check if item already in cart
        result = await session.execute(
            select(CartItem).where(
                (CartItem.cart_id == cart.id) & (CartItem.product_id == product_id)
            )
        )
        existing_item = result.scalar_one_or_none()
        
        if existing_item:
            # Update quantity
            existing_item.quantity += quantity
            session.add(existing_item)
        else:
            # Add new item
            new_item = CartItem(
                id=str(__import__('uuid').uuid4()),
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity
            )
            session.add(new_item)
        
        await session.commit()
        
        # Return updated cart
        return await self._fetch_cart_data(session, cart.id)
    
    async def get_cart(self, session: AsyncSession, user_id: str) -> Dict[str, Any]:
        """Fetch user's cart with all items and calculations"""
        result = await session.execute(select(Cart).where(Cart.user_id == user_id))
        cart = result.scalar_one_or_none()
        
        if not cart:
            # Return empty cart structure
            return {
                'id': None,
                'user_id': user_id,
                'items': [],
                'total_amount': 0.0,
                'total_items': 0,
                'created_at': None,
                'updated_at': None
            }
        
        return await self._fetch_cart_data(session, cart.id)
    
    async def remove_from_cart(self, session: AsyncSession, user_id: str, cart_item_id: str) -> Dict[str, Any]:
        """Remove item from cart"""
        # Verify item exists
        result = await session.execute(select(CartItem).where(CartItem.id == cart_item_id))
        item = result.scalar_one_or_none()
        
        if not item:
            raise ValueError(f"Cart item not found: {cart_item_id}")
        
        # Verify cart belongs to user
        result = await session.execute(select(Cart).where(Cart.id == item.cart_id))
        cart = result.scalar_one_or_none()
        
        if not cart or cart.user_id != user_id:
            raise ValueError("Unauthorized: Item does not belong to user's cart")
        
        # Delete item
        await session.delete(item)
        await session.commit()
        
        # Return updated cart
        return await self._fetch_cart_data(session, cart.id)
    
    async def update_cart_item(
        self, 
        session: AsyncSession,
        user_id: str, 
        cart_item_id: str, 
        quantity: int
    ) -> Dict[str, Any]:
        """Update item quantity or remove if quantity is 0"""
        if quantity < 0 or quantity > 100:
            raise ValueError("Quantity must be between 0 and 100")
        
        # Verify item exists
        result = await session.execute(select(CartItem).where(CartItem.id == cart_item_id))
        item = result.scalar_one_or_none()
        
        if not item:
            raise ValueError(f"Cart item not found: {cart_item_id}")
        
        # Verify cart belongs to user
        result = await session.execute(select(Cart).where(Cart.id == item.cart_id))
        cart = result.scalar_one_or_none()
        
        if not cart or cart.user_id != user_id:
            raise ValueError("Unauthorized: Item does not belong to user's cart")
        
        if quantity == 0:
            # Remove item
            await session.delete(item)
        else:
            # Update quantity
            item.quantity = quantity
            session.add(item)
        
        await session.commit()
        
        # Return updated cart
        return await self._fetch_cart_data(session, cart.id)
    
    async def clear_cart(self, session: AsyncSession, user_id: str) -> None:
        """Clear all items from user's cart"""
        result = await session.execute(select(Cart).where(Cart.user_id == user_id))
        cart = result.scalar_one_or_none()
        
        if cart:
            result = await session.execute(select(CartItem).where(CartItem.cart_id == cart.id))
            items = result.scalars().all()
            
            for item in items:
                await session.delete(item)
            
            await session.commit()
    
    async def _fetch_cart_data(self, session: AsyncSession, cart_id: str) -> Dict[str, Any]:
        """Helper: Fetch cart with items and calculate totals"""
        result = await session.execute(select(Cart).where(Cart.id == cart_id))
        cart = result.scalar_one_or_none()
        
        if not cart:
            raise ValueError(f"Cart not found: {cart_id}")
        
        # Fetch cart items with products
        result = await session.execute(
            select(CartItem).where(CartItem.cart_id == cart_id)
        )
        cart_items = result.scalars().all()
        
        # Calculate totals
        total_amount = 0.0
        total_items = 0
        items_data = []
        
        for item in cart_items:
            # Fetch product for pricing
            result = await session.execute(select(Product).where(Product.id == item.product_id))
            product = result.scalar_one_or_none()
            
            if product:
                subtotal = product.price * item.quantity
                total_amount += subtotal
                total_items += item.quantity
                
                items_data.append({
                    'id': item.id,
                    'product_id': product.id,
                    'product_name': product.name,
                    'product_image': product.image_url,
                    'price': product.price,
                    'quantity': item.quantity,
                    'subtotal': round(subtotal, 2)
                })
        
        return {
            'id': cart.id,
            'user_id': cart.user_id,
            'items': items_data,
            'total_amount': round(total_amount, 2),
            'total_items': total_items,
            'created_at': cart.created_at,
            'updated_at': cart.updated_at
        }


# Singleton instance
cart_core = CartCore()
