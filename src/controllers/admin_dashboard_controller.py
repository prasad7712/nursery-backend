"""Admin dashboard controller for viewing statistics and metrics"""
from fastapi import APIRouter, Depends, HTTPException, status

from src.middlewares.auth_middleware import security_scheme
from src.plugins.database import db
from src.services.admin_service import admin_service
from src.data_contracts.admin_request_response import (
    AdminDashboardResponse,
    AdminLogsResponse
)

router = APIRouter(prefix="/api/v1/admin/dashboard", tags=["admin:dashboard"])


@router.get("/statistics", response_model=AdminDashboardResponse)
async def get_dashboard_statistics(credentials=Depends(security_scheme)):
    """
    Get admin dashboard statistics
    
    Auth Required: Admin
    
    Returns overview of:
    - User statistics (total, active, inactive)
    - Order statistics (by status and payment status)
    - Product statistics (total, active, inactive)
    - Low stock alerts
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        # Get user count
        user_stats = await admin_service.get_user_count()
        
        # Get order statistics
        order_stats = await admin_service.get_order_statistics()
        
        # Get product count
        product_stats = await admin_service.get_product_count()
        
        # Get low stock products
        low_stock = await admin_service.get_low_stock_products(page=1, per_page=5)
        
        return AdminDashboardResponse(
            users=user_stats,
            orders=order_stats,
            products=product_stats,
            low_stock_count=len(low_stock['inventories']) if low_stock['inventories'] else 0,
            timestamp=None
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching dashboard statistics: {str(e)}"
        )


@router.get("/activity-logs", response_model=AdminLogsResponse)
async def get_activity_logs(
    page: int = 1,
    per_page: int = 20,
    admin_id: str = None,
    action_type: str = None,
    credentials=Depends(security_scheme)
):
    """
    Get admin activity logs
    
    Auth Required: Admin
    
    Query params:
        - admin_id: Filter by specific admin
        - action_type: Filter by action type
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        logs = await admin_service.get_admin_logs(
            admin_id=admin_id,
            action_type=action_type,
            page=page,
            per_page=per_page
        )
        
        return AdminLogsResponse(
            logs=logs.get('logs', []),
            total=logs.get('total', 0),
            page=page,
            per_page=per_page
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching activity logs: {str(e)}"
        )
