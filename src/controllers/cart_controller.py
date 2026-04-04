"""Cart API Controller"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from src.middlewares.auth_middleware import AuthMiddleware, security_scheme
from src.services.cart_service import CartService
from src.data_contracts.api_request_response import (
    CartItemAddRequest,
    CartItemUpdateRequest,
    CartResponse
)

router = APIRouter(prefix="/api/v1", tags=["Cart"])
cart_service = CartService()


@router.post("/cart/add", response_model=CartResponse, status_code=200)
async def add_to_cart(
    request: CartItemAddRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme)
):
    """
    Add item to cart or increment quantity if exists.
    
    Auth Required: Yes
    
    Request:
    ```json
    {
        "product_id": "prod_123",
        "quantity": 2
    }
    ```
    
    Response: Updated cart object
    """
    try:
        user = await AuthMiddleware.get_current_user(credentials)
        result = await cart_service.add_to_cart(
            user_id=user.id,
            product_id=request.product_id,
            quantity=request.quantity
        )
        return CartResponse(**result)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/cart", response_model=CartResponse, status_code=200)
async def get_cart(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    """
    Get user's cart with all items and totals.
    
    Auth Required: Yes
    
    Response: Cart object (empty if no items)
    """
    try:
        user = await AuthMiddleware.get_current_user(credentials)
        result = await cart_service.get_cart(user.id)
        return CartResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.delete("/cart/items/{item_id}", response_model=CartResponse, status_code=200)
async def remove_from_cart(
    item_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme)
):
    """
    Remove item from cart.
    
    Auth Required: Yes
    
    Path Params:
    - item_id: CartItem ID to remove
    
    Response: Updated cart object
    """
    try:
        user = await AuthMiddleware.get_current_user(credentials)
        result = await cart_service.remove_from_cart(user.id, item_id)
        return CartResponse(**result)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.put("/cart/items/{item_id}", response_model=CartResponse, status_code=200)
async def update_cart_item(
    item_id: str,
    request: CartItemUpdateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme)
):
    """
    Update item quantity (set to 0 to remove).
    
    Auth Required: Yes
    
    Path Params:
    - item_id: CartItem ID
    
    Request:
    ```json
    {
        "quantity": 5
    }
    ```
    
    Response: Updated cart object
    """
    try:
        user = await AuthMiddleware.get_current_user(credentials)
        result = await cart_service.update_cart_item(
            user_id=user.id,
            cart_item_id=item_id,
            quantity=request.quantity
        )
        return CartResponse(**result)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
