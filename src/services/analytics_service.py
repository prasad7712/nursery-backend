"""Analytics service for calculating dashboard metrics"""
from datetime import datetime, timedelta, timezone
from typing import Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.models.product import Product
from src.models.order import Order
from src.models.admin import ProductInventory


class AnalyticsService:
    """Service for calculating dashboard analytics"""
    
    async def get_dashboard_metrics(self, session: AsyncSession) -> Dict[str, Any]:
        """Get overall dashboard metrics"""
        try:
            # Get counts
            total_users_result = await session.execute(select(func.count()).select_from(User))
            total_users = total_users_result.scalar() or 0
            
            total_customers_result = await session.execute(
                select(func.count()).select_from(User).where(User.role == 'CUSTOMER')
            )
            total_customers = total_customers_result.scalar() or 0
            
            total_admins_result = await session.execute(
                select(func.count()).select_from(User).where(User.role == 'ADMIN')
            )
            total_admins = total_admins_result.scalar() or 0
            
            total_products_result = await session.execute(
                select(func.count()).select_from(Product).where(Product.is_active == True)
            )
            total_products = total_products_result.scalar() or 0
            
            total_orders_result = await session.execute(select(func.count()).select_from(Order))
            total_orders = total_orders_result.scalar() or 0
            
            pending_orders_result = await session.execute(
                select(func.count()).select_from(Order).where(Order.status == 'PENDING')
            )
            pending_orders = pending_orders_result.scalar() or 0
            
            # Get revenue
            total_revenue = await self._calculate_total_revenue(session)
            
            # Get low stock products
            low_stock_products = await self._count_low_stock_products(session)
            
            return {
                'total_users': total_users,
                'total_customers': total_customers,
                'total_admins': total_admins,
                'total_products': total_products,
                'total_orders': total_orders,
                'total_revenue': total_revenue,
                'pending_orders': pending_orders,
                'low_stock_products': low_stock_products
            }
        except Exception as e:
            raise Exception(f"Error calculating dashboard metrics: {str(e)}")
    
    async def get_order_metrics(self, session: AsyncSession) -> Dict[str, Any]:
        """Get order-related metrics"""
        try:
            total_orders_result = await session.execute(select(func.count()).select_from(Order))
            total_orders = total_orders_result.scalar() or 0
            
            pending_result = await session.execute(
                select(func.count()).select_from(Order).where(Order.status == 'PENDING')
            )
            pending = pending_result.scalar() or 0
            
            confirmed_result = await session.execute(
                select(func.count()).select_from(Order).where(Order.status == 'CONFIRMED')
            )
            confirmed = confirmed_result.scalar() or 0
            
            shipped_result = await session.execute(
                select(func.count()).select_from(Order).where(Order.status == 'SHIPPED')
            )
            shipped = shipped_result.scalar() or 0
            
            delivered_result = await session.execute(
                select(func.count()).select_from(Order).where(Order.status == 'DELIVERED')
            )
            delivered = delivered_result.scalar() or 0
            
            cancelled_result = await session.execute(
                select(func.count()).select_from(Order).where(Order.status == 'CANCELLED')
            )
            cancelled = cancelled_result.scalar() or 0
            
            total_revenue = await self._calculate_total_revenue(session)
            
            # Calculate average order value
            aov = total_revenue / total_orders if total_orders > 0 else 0
            
            return {
                'total_orders': total_orders,
                'pending': pending,
                'confirmed': confirmed,
                'shipped': shipped,
                'delivered': delivered,
                'cancelled': cancelled,
                'average_order_value': round(aov, 2),
                'total_revenue': round(total_revenue, 2)
            }
        except Exception as e:
            raise Exception(f"Error calculating order metrics: {str(e)}")
    
    async def get_user_metrics(self, session: AsyncSession) -> Dict[str, Any]:
        """Get user-related metrics"""
        try:
            total_users_result = await session.execute(select(func.count()).select_from(User))
            total_users = total_users_result.scalar() or 0
            
            active_users_result = await session.execute(
                select(func.count()).select_from(User).where(User.is_active == True)
            )
            active_users = active_users_result.scalar() or 0
            
            inactive_users_result = await session.execute(
                select(func.count()).select_from(User).where(User.is_active == False)
            )
            inactive_users = inactive_users_result.scalar() or 0
            
            total_admins_result = await session.execute(
                select(func.count()).select_from(User).where(User.role == 'ADMIN')
            )
            total_admins = total_admins_result.scalar() or 0
            
            # New users this month
            month_ago = datetime.now(timezone.utc) - timedelta(days=30)
            new_users_result = await session.execute(
                select(func.count()).select_from(User).where(User.created_at >= month_ago)
            )
            new_users_this_month = new_users_result.scalar() or 0
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'inactive_users': inactive_users,
                'total_admins': total_admins,
                'new_users_this_month': new_users_this_month
            }
        except Exception as e:
            raise Exception(f"Error calculating user metrics: {str(e)}")
    
    async def get_product_metrics(self, session: AsyncSession) -> Dict[str, Any]:
        """Get product-related metrics"""
        try:
            total_products_result = await session.execute(select(func.count()).select_from(Product))
            total_products = total_products_result.scalar() or 0
            
            active_products_result = await session.execute(
                select(func.count()).select_from(Product).where(Product.is_active == True)
            )
            active_products = active_products_result.scalar() or 0
            
            inactive_products_result = await session.execute(
                select(func.count()).select_from(Product).where(Product.is_active == False)
            )
            inactive_products = inactive_products_result.scalar() or 0
            
            # Get low stock count
            low_stock_count = await self._count_low_stock_products(session)
            
            # Calculate total inventory value
            total_inventory_value = await self._calculate_inventory_value(session)
            
            return {
                'total_products': total_products,
                'active_products': active_products,
                'inactive_products': inactive_products,
                'low_stock_count': low_stock_count,
                'total_inventory_value': round(total_inventory_value, 2)
            }
        except Exception as e:
            raise Exception(f"Error calculating product metrics: {str(e)}")
    
    async def get_revenue_by_date_range(self, session: AsyncSession, days: int = 30) -> Dict[str, float]:
        """Get revenue grouped by date"""
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            stmt = select(Order).where(
                (Order.status == 'DELIVERED') &
                (Order.created_at >= cutoff_date)
            ).order_by(Order.created_at.desc())
            
            result = await session.execute(stmt)
            orders = result.scalars().all()
            
            revenue_by_date = {}
            for order in orders:
                date_key = order.created_at.strftime('%Y-%m-%d')
                revenue_by_date[date_key] = revenue_by_date.get(date_key, 0) + (order.total_amount or 0)
            
            return revenue_by_date
        except Exception as e:
            raise Exception(f"Error calculating revenue by date: {str(e)}")
    
    # Private helper methods
    
    async def _calculate_total_revenue(self, session: AsyncSession) -> float:
        """Calculate total revenue from delivered orders"""
        try:
            stmt = select(func.sum(Order.total_amount)).where(Order.status == 'DELIVERED')
            result = await session.execute(stmt)
            total = result.scalar() or 0.0
            return round(total, 2)
        except Exception:
            return 0.0
    
    async def _count_low_stock_products(self, session: AsyncSession) -> int:
        """Count products with low stock"""
        try:
            # Count where stock_level <= low_stock_threshold
            stmt = select(func.count()).select_from(ProductInventory).where(
                ProductInventory.stock_level <= ProductInventory.low_stock_threshold
            )
            result = await session.execute(stmt)
            count = result.scalar() or 0
            return count
        except Exception:
            return 0
    
    async def _calculate_inventory_value(self, session: AsyncSession) -> float:
        """Calculate total inventory value"""
        try:
            from sqlalchemy.orm import selectinload
            stmt = select(ProductInventory).options(selectinload(ProductInventory.product))
            result = await session.execute(stmt)
            inventories = result.scalars().all()
            
            total_value = 0.0
            for inv in inventories:
                if inv.product and inv.product.cost_price:
                    total_value += inv.stock_level * inv.product.cost_price
            
            return round(total_value, 2)
        except Exception:
            return 0.0


# Singleton instance
analytics_service = AnalyticsService()
