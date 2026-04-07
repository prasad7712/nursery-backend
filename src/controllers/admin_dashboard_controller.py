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
        
        return AdminDashboardResponse(
            users=user_stats,
            orders=order_stats,
            products=product_stats,
            low_stock_count=product_stats.get('low_stock', 0),
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
        import json
        
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        logs_data = await admin_service.get_admin_logs(
            admin_id=admin_id,
            action_type=action_type,
            page=page,
            per_page=per_page
        )
        
        # Convert logs to AdminLogResponse format
        logs_list = []
        for log in logs_data.get('logs', []):
            log_dict = {
                'id': log.id,
                'admin_id': log.admin_id,
                'admin_email': log.admin.email if hasattr(log, 'admin') and log.admin else None,
                'action_type': log.action_type,
                'entity_type': log.entity_type,
                'entity_id': log.entity_id,
                'old_values': json.loads(log.old_values) if log.old_values else None,
                'new_values': json.loads(log.new_values) if log.new_values else None,
                'reason': log.reason,
                'ip_address': log.ip_address,
                'user_agent': log.user_agent if hasattr(log, 'user_agent') else None,
                'created_at': log.created_at
            }
            from src.data_contracts.admin_request_response import AdminLogResponse
            logs_list.append(AdminLogResponse(**log_dict))
        
        return AdminLogsResponse(
            logs=logs_list,
            total=logs_data.get('total', 0),
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
