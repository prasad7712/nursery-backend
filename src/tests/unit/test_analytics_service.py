"""Unit tests for the analytics service using SQLAlchemy"""
import pytest
from datetime import datetime, timedelta, timezone

from src.services.analytics_service import analytics_service
from src.models.user import User
from src.models.product import Product
from src.models.order import Order
from src.models.admin import ProductInventory


@pytest.mark.unit
class TestAnalyticsService:
    """Test suite for analytics service"""
    
    async def test_get_dashboard_metrics_empty(self, session):
        """Test dashboard metrics with empty database"""
        metrics = await analytics_service.get_dashboard_metrics(session)
        
        assert metrics['total_users'] == 0
        assert metrics['total_products'] == 0
        assert metrics['total_orders'] == 0
        assert metrics['total_revenue'] == 0.0
    
    async def test_get_dashboard_metrics_with_data(self, session, test_user, test_product, test_order):
        """Test dashboard metrics with sample data"""
        metrics = await analytics_service.get_dashboard_metrics(session)
        
        assert metrics['total_users'] >= 1
        assert metrics['total_products'] >= 1
        assert metrics['total_orders'] >= 1
    
    async def test_get_order_metrics(self, session, test_user, test_order):
        """Test order metrics calculation"""
        metrics = await analytics_service.get_order_metrics(session)
        
        assert 'total_orders' in metrics
        assert 'pending' in metrics
        assert 'confirmed' in metrics
        assert 'average_order_value' in metrics
        assert metrics['total_orders'] >= 1
        assert metrics['pending'] >= 1
    
    async def test_get_user_metrics(self, session, test_user, test_admin):
        """Test user metrics calculation"""
        metrics = await analytics_service.get_user_metrics(session)
        
        assert metrics['total_users'] >= 2  # test_user + test_admin
        assert metrics['total_admins'] >= 1
        assert metrics['active_users'] >= 2
    
    async def test_get_product_metrics(self, session, test_product):
        """Test product metrics calculation"""
        metrics = await analytics_service.get_product_metrics(session)
        
        assert metrics['total_products'] >= 1
        assert metrics['active_products'] >= 1
        assert 'total_inventory_value' in metrics
    
    async def test_get_revenue_by_date_range(self, session, test_user):
        """Test revenue calculation by date range"""
        # Create order with delivered status
        order = Order(
            id="test-order-delivered",
            user_id=test_user.id,
            status="DELIVERED",
            payment_status="SUCCESSFUL",
            total_amount=100.50
        )
        session.add(order)
        await session.commit()
        
        revenue_data = await analytics_service.get_revenue_by_date_range(session, days=30)
        
        assert isinstance(revenue_data, dict)
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        if today in revenue_data:
            assert revenue_data[today] == 100.50
    
    async def test_low_stock_products(self, session, test_product):
        """Test low stock product counting"""
        # Create inventory with low stock
        inventory = ProductInventory(
            id="test-inv-1",
            product_id=test_product.id,
            stock_level=5,
            low_stock_threshold=10
        )
        session.add(inventory)
        await session.commit()
        
        metrics = await analytics_service.get_product_metrics(session)
        assert metrics['low_stock_count'] >= 1
