"""Admin order management controller"""
from fastapi import APIRouter, Depends, HTTPException, status, Query

from src.middlewares.auth_middleware import security_scheme
from src.plugins.database import db
from src.services.admin_service import admin_service
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
    credentials=Depends(security_scheme)
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
        
        where = {}
        if status:
            where['status'] = status
        if payment_status:
            where['payment_status'] = payment_status
        if user_id:
            where['user_id'] = user_id
        
        total = await db.client.order.count(where=where)
        
        orders = await db.client.order.find_many(
            where=where,
            skip=(page - 1) * per_page,
            take=per_page,
            include={'user': True, 'items': True},
            order_by=[{'created_at': 'desc'}]
        )
        
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
async def get_order(order_id: str, credentials=Depends(security_scheme)):
    """
    Get order details
    
    Auth Required: Admin
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        order = await db.client.order.find_unique(
            where={'id': order_id},
            include={'user': True, 'items': True}
        )
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
    credentials=Depends(security_scheme)
):
    """
    Update order status
    
    Auth Required: Admin
    
    Valid statuses: PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        order = await db.client.order.find_unique(where={'id': order_id})
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        old_status = order.status
        
        await db.client.order.update(
            where={'id': order_id},
            data={'status': request.status}
        )
        
        await admin_service.log_admin_action(
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating order: {str(e)}"
        )


@router.post("/{order_id}/cancel", response_model=SuccessResponse)
async def cancel_order(
    order_id: str,
    reason: str = Query(...),
    credentials=Depends(security_scheme)
):
    """
    Cancel order
    
    Auth Required: Admin
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        order = await db.client.order.find_unique(where={'id': order_id})
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
        
        await db.client.order.update(
            where={'id': order_id},
            data={'status': 'CANCELLED'}
        )
        
        await admin_service.log_admin_action(
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cancelling order: {str(e)}"
        )
