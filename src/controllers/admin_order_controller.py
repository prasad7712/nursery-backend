"""Admin order management controller"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.middlewares.auth_middleware import security_scheme
from src.database import get_session
from src.services.admin_service import admin_service
from src.models.order import Order
from src.models.user import User
from src.data_contracts.admin_request_response import (
    AdminOrderStatusUpdateRequest,
    AdminOrderResponse,
    AdminOrderListResponse,
    SuccessResponse
)

router = APIRouter(prefix="/api/v1/admin/orders", tags=["admin:orders"])


@router.get("", response_model=AdminOrderListResponse)
async def list_orders(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    payment_status: str = Query(None),
    user_id: str = Query(None),
    credentials=Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
):
    """
    List all orders with filters
    
    Auth Required: Admin
    
    Query params:
        - status: Filter by order status (PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED)
        - payment_status: Filter by payment status
        - user_id: Filter by specific user
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        where_conditions = []
        if status:
            where_conditions.append(Order.status == status)
        if payment_status:
            where_conditions.append(Order.payment_status == payment_status)
        if user_id:
            where_conditions.append(Order.user_id == user_id)
        
        # Build query
        stmt = select(Order)
        if where_conditions:
            from sqlalchemy import and_
            stmt = stmt.where(and_(*where_conditions)) if len(where_conditions) > 1 else stmt.where(where_conditions[0])
        
        # Get total count
        count_stmt = select(func.count()).select_from(Order)
        if where_conditions:
            from sqlalchemy import and_
            count_stmt = count_stmt.where(and_(*where_conditions)) if len(where_conditions) > 1 else count_stmt.where(where_conditions[0])
        count_result = await session.execute(count_stmt)
        total = count_result.scalar() or 0
        
        # Get paginated results with relationships
        from sqlalchemy.orm import selectinload
        stmt = stmt.options(
            selectinload(Order.user),
            selectinload(Order.items)
        ).order_by(Order.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        result = await session.execute(stmt)
        orders = result.scalars().unique().all()
        
        result = []
        for order in orders:
            order_dict = AdminOrderResponse.model_validate(order).dict()
            order_dict['user_email'] = order.user.email if order.user else None
            order_dict['items_count'] = len(order.items) if hasattr(order, 'items') else 0
            result.append(AdminOrderResponse(**order_dict))
        
        return AdminOrderListResponse(
            orders=result,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=(total + per_page - 1) // per_page
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching orders: {str(e)}"
        )


@router.get("/{order_id}", response_model=AdminOrderResponse)
async def get_order(
    order_id: str,
    credentials=Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
):
    """Get order details
    
    Auth Required: Admin
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        from sqlalchemy.orm import selectinload
        
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        stmt = select(Order).where(Order.id == order_id).options(
            selectinload(Order.user),
            selectinload(Order.items)
        )
        result = await session.execute(stmt)
        order = result.scalar_one_or_none()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        order_dict = AdminOrderResponse.model_validate(order).dict()
        order_dict['user_email'] = order.user.email if order.user else None
        order_dict['items_count'] = len(order.items) if hasattr(order, 'items') else 0
        return AdminOrderResponse(**order_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{order_id}/status", response_model=SuccessResponse)
async def update_order_status(
    order_id: str,
    request: AdminOrderStatusUpdateRequest,
    credentials=Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
):
    """Update order status
    
    Auth Required: Admin
    
    Valid statuses: PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        stmt = select(Order).where(Order.id == order_id)
        result = await session.execute(stmt)
        order = result.scalar_one_or_none()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        old_status = order.status
        order.status = request.status
        await session.commit()
        
        await admin_service.log_admin_action(
            session,
            admin_id=admin.id,
            action_type='STATUS_CHANGE',
            entity_type='Order',
            entity_id=order_id,
            old_values={'status': old_status},
            new_values={'status': request.status},
            reason=request.note
        )
        
        return SuccessResponse(message=f"Order status updated to {request.status}")
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating order: {str(e)}"
        )


@router.post("/{order_id}/cancel", response_model=SuccessResponse)
async def cancel_order(
    order_id: str,
    reason: str = Query(...),
    credentials=Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
):
    """Cancel order
    
    Auth Required: Admin
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        stmt = select(Order).where(Order.id == order_id)
        result = await session.execute(stmt)
        order = result.scalar_one_or_none()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        if order.status in ['DELIVERED', 'CANCELLED']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel order with status {order.status}"
            )
        
        old_status = order.status
        order.status = 'CANCELLED'
        await session.commit()
        
        await admin_service.log_admin_action(
            session,
            admin_id=admin.id,
            action_type='STATUS_CHANGE',
            entity_type='Order',
            entity_id=order_id,
            old_values={'status': old_status},
            new_values={'status': 'CANCELLED'},
            reason=reason
        )
        
        return SuccessResponse(message="Order cancelled successfully")
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cancelling order: {str(e)}"
        )
