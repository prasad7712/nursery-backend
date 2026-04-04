"""Analytics service for calculating dashboard metrics"""
from datetime import datetime, timedelta, timezone
from typing import Dict, Any

from src.plugins.database import db


class AnalyticsService:
    """Service for calculating dashboard analytics"""
    
    async def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get overall dashboard metrics"""
        try:
            # Get counts
            total_users = await db.client.user.count()
            total_customers = await db.client.user.count(
                where={'role': 'CUSTOMER'}
            )
            total_admins = await db.client.user.count(
                where={'role': 'ADMIN'}
            )
            total_products = await db.client.product.count(where={'is_active': True})
            total_orders = await db.client.order.count()
            pending_orders = await db.client.order.count(
                where={'status': 'PENDING'}
            )
            
            # Get revenue
            total_revenue = await self._calculate_total_revenue()
            
            # Get low stock products
            low_stock_products = await db.client.productinventory.count(
                where={'stock_level': {'lte': 'low_stock_threshold'}}
            )
            
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
    
    async def get_order_metrics(self) -> Dict[str, Any]:
        """Get order-related metrics"""
        try:
            total_orders = await db.client.order.count()
            pending = await db.client.order.count(where={'status': 'PENDING'})
            confirmed = await db.client.order.count(where={'status': 'CONFIRMED'})
            shipped = await db.client.order.count(where={'status': 'SHIPPED'})
            delivered = await db.client.order.count(where={'status': 'DELIVERED'})
            cancelled = await db.client.order.count(where={'status': 'CANCELLED'})
            
            total_revenue = await self._calculate_total_revenue()
            
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
    
    async def get_user_metrics(self) -> Dict[str, Any]:
        """Get user-related metrics"""
        try:
            total_users = await db.client.user.count()
            active_users = await db.client.user.count(where={'is_active': True})
            inactive_users = await db.client.user.count(where={'is_active': False})
            total_admins = await db.client.user.count(where={'role': 'ADMIN'})
            
            # New users this month
            month_ago = datetime.now(timezone.utc) - timedelta(days=30)
            new_users_this_month = await db.client.user.count(
                where={'created_at': {'gte': month_ago}}
            )
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'inactive_users': inactive_users,
                'total_admins': total_admins,
                'new_users_this_month': new_users_this_month
            }
        except Exception as e:
            raise Exception(f"Error calculating user metrics: {str(e)}")
    
    async def get_product_metrics(self) -> Dict[str, Any]:
        """Get product-related metrics"""
        try:
            total_products = await db.client.product.count()
            active_products = await db.client.product.count(where={'is_active': True})
            inactive_products = await db.client.product.count(where={'is_active': False})
            
            # Get low stock count
            low_stock_count = await self._count_low_stock_products()
            
            # Calculate total inventory value
            total_inventory_value = await self._calculate_inventory_value()
            
            return {
                'total_products': total_products,
                'active_products': active_products,
                'inactive_products': inactive_products,
                'low_stock_count': low_stock_count,
                'total_inventory_value': round(total_inventory_value, 2)
            }
        except Exception as e:
            raise Exception(f"Error calculating product metrics: {str(e)}")
    
    async def get_revenue_by_date_range(self, days: int = 30) -> Dict[str, float]:
        """Get revenue grouped by date"""
        try:
            orders = await db.client.order.find_many(
                where={
                    'status': 'DELIVERED',
                    'created_at': {
                        'gte': datetime.now(timezone.utc) - timedelta(days=days)
                    }
                },
                order_by=[{'created_at': 'desc'}]
            )
            
            revenue_by_date = {}
            for order in orders:
                date_key = order.created_at.strftime('%Y-%m-%d')
                revenue_by_date[date_key] = revenue_by_date.get(date_key, 0) + order.total_amount
            
            return revenue_by_date
        except Exception as e:
            raise Exception(f"Error calculating revenue by date: {str(e)}")
    
    # Private helper methods
    
    async def _calculate_total_revenue(self) -> float:
        """Calculate total revenue from delivered orders"""
        try:
            orders = await db.client.order.find_many(
                where={'status': 'DELIVERED'}
            )
            
            total = sum(order.total_amount for order in orders)
            return round(total, 2)
        except Exception:
            return 0.0
    
    async def _count_low_stock_products(self) -> int:
        """Count products with low stock"""
        try:
            inventories = await db.client.productinventory.find_many()
            
            count = 0
            for inv in inventories:
                if inv.stock_level <= inv.low_stock_threshold:
                    count += 1
            
            return count
        except Exception:
            return 0
    
    async def _calculate_inventory_value(self) -> float:
        """Calculate total inventory value"""
        try:
            inventories = await db.client.productinventory.find_many(
                include={'product': True}
            )
            
            total_value = 0.0
            for inv in inventories:
                if inv.product and inv.product.cost_price:
                    total_value += inv.stock_level * inv.product.cost_price
            
            return round(total_value, 2)
        except Exception:
            return 0.0


# Singleton instance
analytics_service = AnalyticsService()
