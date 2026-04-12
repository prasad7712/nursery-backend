"""Dashboard controller for admin panel"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.middlewares.auth_middleware import security_scheme
from src.services.analytics_service import analytics_service
from src.data_contracts.admin_request_response import (
    DashboardMetrics,
    OrderMetrics,
    UserMetrics,
    ProductMetrics
)
from src.database import get_session

router = APIRouter(prefix="/api/v1/admin/dashboard", tags=["admin:dashboard"])


@router.get("/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(credentials=Depends(security_scheme), session: AsyncSession = Depends(get_session)):
    """
    Get overall dashboard metrics
    
    Auth Required: Admin
    
    Returns:
        - Total users, products, orders
        - Total revenue and pending orders
        - Low stock products count
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        metrics = await analytics_service.get_dashboard_metrics(session)
        return DashboardMetrics(**metrics)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching metrics: {str(e)}"
        )


@router.get("/orders", response_model=OrderMetrics)
async def get_order_metrics(credentials=Depends(security_scheme), session: AsyncSession = Depends(get_session)):
    """
    Get order-related metrics
    
    Auth Required: Admin
    
    Returns:
        - Order counts by status
        - Total revenue and average order value
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        metrics = await analytics_service.get_order_metrics(session)
        return OrderMetrics(**metrics)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching order metrics: {str(e)}"
        )


@router.get("/users", response_model=UserMetrics)
async def get_user_metrics(credentials=Depends(security_scheme), session: AsyncSession = Depends(get_session)):
    """
    Get user-related metrics
    
    Auth Required: Admin
    
    Returns:
        - User counts by status and role
        - New users this month
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        metrics = await analytics_service.get_user_metrics(session)
        return UserMetrics(**metrics)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user metrics: {str(e)}"
        )


@router.get("/products", response_model=ProductMetrics)
async def get_product_metrics(credentials=Depends(security_scheme), session: AsyncSession = Depends(get_session)):
    """
    Get product-related metrics
    
    Auth Required: Admin
    
    Returns:
        - Product counts and low stock count
        - Total inventory value
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        metrics = await analytics_service.get_product_metrics(session)
        return ProductMetrics(**metrics)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching product metrics: {str(e)}"
        )


@router.get("/revenue")
async def get_revenue_by_date(
    days: int = 30,
    credentials=Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
):
    """
    Get revenue grouped by date
    
    Auth Required: Admin
    
    Query params:
        - days: Number of days to look back (default 30)
    
    Returns:
        - Revenue for each date
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        if days < 1 or days > 365:
            raise ValueError("Days must be between 1 and 365")
        
        revenue_data = await analytics_service.get_revenue_by_date_range(session, days)
        return {
            'period_days': days,
            'revenue_by_date': revenue_data,
            'total_revenue': sum(revenue_data.values())
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching revenue: {str(e)}"
        )
