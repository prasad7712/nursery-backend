"""Cart business logic core"""
from typing import Optional, Dict, Any

from src.plugins.database import db


class CartCore:
    """Cart domain logic using Prisma ORM"""
    
    async def get_or_create_cart(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's cart or create if doesn't exist.
        
        Args:
            user_id: User ID
        
        Returns:
            Cart dictionary
        """
        cart = await db.client.cart.find_unique(where={"userId": user_id})
        
        if not cart:
            cart = await db.client.cart.create(data={"userId": user_id})
        
        return await self._fetch_cart_data(cart.id)
    
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
            Updated cart dictionary
        
        Raises:
            ValueError: If product not found or invalid quantity
        """
        # Validate product exists
        product = await db.client.product.find_unique(where={"id": product_id})
        if not product:
            raise ValueError(f"Product not found: {product_id}")
        
        if quantity < 1 or quantity > 100:
            raise ValueError("Quantity must be between 1 and 100")
        
        # Get or create cart
        cart = await db.client.cart.find_unique(where={"userId": user_id})
        if not cart:
            cart = await db.client.cart.create(data={"userId": user_id})
        
        # Check if item already in cart
        existing_item = await db.client.cartitem.find_unique(
            where={"cartId_productId": {"cartId": cart.id, "productId": product_id}}
        )
        
        if existing_item:
            # Update quantity
            await db.client.cartitem.update(
                where={"id": existing_item.id},
                data={"quantity": existing_item.quantity + quantity}
            )
        else:
            # Add new item
            await db.client.cartitem.create(
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
        
        Returns empty cart if doesn't exist.
        """
        cart = await db.client.cart.find_unique(where={"userId": user_id})
        
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
        
        return await self._fetch_cart_data(cart.id)
    
    async def remove_from_cart(self, user_id: str, cart_item_id: str) -> Dict[str, Any]:
        """
        Remove item from cart.
        
        Args:
            user_id: User ID (for authorization)
            cart_item_id: CartItem ID to remove
        
        Returns:
            Updated cart dictionary
        
        Raises:
            ValueError: If item not found or unauthorized
        """
        # Verify item exists and belongs to user's cart
        item = await db.client.cartitem.find_unique(where={"id": cart_item_id})
        if not item:
            raise ValueError(f"Cart item not found: {cart_item_id}")
        
        # Verify cart belongs to user
        cart = await db.client.cart.find_unique(where={"id": item.cartId})
        if not cart or cart.userId != user_id:
            raise ValueError("Unauthorized: Item does not belong to user's cart")
        
        # Delete item
        await db.client.cartitem.delete(where={"id": cart_item_id})
        
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
            Updated cart dictionary
        
        Raises:
            ValueError: If invalid quantity or item not found
        """
        if quantity < 0 or quantity > 100:
            raise ValueError("Quantity must be between 0 and 100")
        
        # Verify item exists
        item = await db.client.cartitem.find_unique(where={"id": cart_item_id})
        if not item:
            raise ValueError(f"Cart item not found: {cart_item_id}")
        
        # Verify cart belongs to user
        cart = await db.client.cart.find_unique(where={"id": item.cartId})
        if not cart or cart.userId != user_id:
            raise ValueError("Unauthorized: Item does not belong to user's cart")
        
        if quantity == 0:
            # Remove item
            await db.client.cartitem.delete(where={"id": cart_item_id})
        else:
            # Update quantity
            await db.client.cartitem.update(
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
        cart = await db.client.cart.find_unique(where={"userId": user_id})
        if cart:
            await db.client.cartitem.delete_many(where={"cartId": cart.id})
    
    async def _fetch_cart_data(self, cart_id: str) -> Dict[str, Any]:
        """
        Helper: Fetch cart with items and calculate totals.
        
        Returns complete cart object with calculations.
        """
        cart = await db.client.cart.find_unique(
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
                'subtotal': round(subtotal, 2)
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
