"""Order business logic service layer"""
from typing import Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.order_core import OrderCore


class OrderService:
    """Order service with error handling"""
    
    def __init__(self):
        self.order_core = OrderCore()
    
    async def create_order(
        self,
        session: AsyncSession,
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
                session, user_id, shipping_address, notes
            )
            return result
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error creating order: {str(e)}")
    
    async def get_user_orders(
        self,
        session: AsyncSession,
        user_id: str,
        page: int = 1,
        per_page: int = 10
    ) -> Dict[str, Any]:
        """Get user's orders with pagination."""
        try:
            result = await self.order_core.get_user_orders(
                session, user_id, page, per_page
            )
            return result
        except Exception as e:
            raise Exception(f"Error fetching orders: {str(e)}")
    
    async def get_order_details(
        session: AsyncSession,
        user_id: str,
        order_id: str
    ) -> Dict[str, Any]:
        """Get order details."""
        try:
            result = await self.order_core.get_order_details(session, user_id, order_id)
            return result
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Error fetching order: {str(e)}")
