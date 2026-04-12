"""Admin dashboard controller for viewing statistics and metrics"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.middlewares.auth_middleware import security_scheme
from src.database import get_session
from src.services.admin_service import admin_service
from src.services.analytics_service import analytics_service
from src.data_contracts.admin_request_response import (
    AdminDashboardResponse,
    AdminLogsResponse
)

router = APIRouter(prefix="/api/v1/admin/dashboard", tags=["admin:dashboard"])


@router.get("/statistics", response_model=AdminDashboardResponse)
async def get_dashboard_statistics(
    credentials=Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
):
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
        
        # Get dashboard metrics using analytics service
        metrics = await analytics_service.get_dashboard_metrics(session)
        
        # Get detailed metrics
        user_metrics = await analytics_service.get_user_metrics(session)
        order_metrics = await analytics_service.get_order_metrics(session)
        product_metrics = await analytics_service.get_product_metrics(session)
        
        return AdminDashboardResponse(
            users=user_metrics,
            orders=order_metrics,
            products=product_metrics,
            low_stock_count=metrics.get('low_stock_products', 0),
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
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    admin_id: str = Query(None),
    action_type: str = Query(None),
    credentials=Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
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
            session,
            admin_id=admin_id,
            action_type=action_type,
            page=page,
            per_page=per_page
        )
        
        # Convert logs to AdminLogResponse format
        logs_list = []
        for log in logs_data.get('logs', []):
            log_dict = {
                'id': log['id'],
                'admin_id': log['admin_id'],
                'admin_email': None,  # Not included in service response
                'action_type': log['action_type'],
                'entity_type': log['entity_type'],
                'entity_id': log['entity_id'],
                'old_values': log.get('old_values'),
                'new_values': log.get('new_values'),
                'reason': log.get('reason'),
                'ip_address': log.get('ip_address'),
                'user_agent': log.get('user_agent'),
                'created_at': log['created_at']
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
