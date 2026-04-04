"""Cart business logic service layer"""
from typing import Dict, Any

from src.core.cart_core import CartCore


class CartService:
    """Cart service with error handling"""
    
    def __init__(self):
        self.cart_core = CartCore()
    
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
