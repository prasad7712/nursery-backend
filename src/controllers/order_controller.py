"""Order API Controller"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPAuthorizationCredentials

from src.middlewares.auth_middleware import AuthMiddleware, security_scheme
from src.services.order_service import OrderService
from src.data_contracts.api_request_response import (
    CreateOrderRequest,
    OrderResponse,
    OrderListResponse
)

router = APIRouter(prefix="/api/v1", tags=["Orders"])
order_service = OrderService()


@router.post("/orders", response_model=OrderResponse, status_code=201)
async def create_order(
    request: CreateOrderRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme)
):
    """
    Create order from user's cart.
    
    Auth Required: Yes
    
    Request:
    ```json
    {
        "shipping_address": "123 Main St, City, State 12345",
        "notes": "Please deliver after 6 PM"
    }
    ```
    
    Response: Created order (status 201)
    """
    try:
        user = await AuthMiddleware.get_current_user(credentials)
        result = await order_service.create_order(
            user_id=user.id,
            shipping_address=request.shipping_address,
            notes=request.notes
        )
        return OrderResponse(**result)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/orders", response_model=OrderListResponse, status_code=200)
async def get_user_orders(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100)
):
    """
    Get user's orders with pagination.
    
    Auth Required: Yes
    
    Query Params:
    - page: Page number (default 1)
    - per_page: Items per page (default 10, max 100)
    
    Response: List of orders + pagination info
    """
    try:
        user = await AuthMiddleware.get_current_user(credentials)
        result = await order_service.get_user_orders(
            user_id=user.id,
            page=page,
            per_page=per_page
        )
        return OrderListResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/orders/{order_id}", response_model=OrderResponse, status_code=200)
async def get_order_details(
    order_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme)
):
    """
    Get order details.
    
    Auth Required: Yes
    
    Path Params:
    - order_id: Order ID
    
    Response: Order data with items
    """
    try:
        user = await AuthMiddleware.get_current_user(credentials)
        result = await order_service.get_order_details(
            user_id=user.id,
            order_id=order_id
        )
        return OrderResponse(**result)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
