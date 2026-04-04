"""Admin inventory management controller"""
from fastapi import APIRouter, Depends, HTTPException, status, Query

from src.middlewares.auth_middleware import security_scheme
from src.plugins.database import db
from src.services.admin_service import admin_service
from src.data_contracts.admin_request_response import (
    AdminInventoryAdjustmentRequest,
    AdminInventoryResponse,
    AdminInventoryListResponse,
    SuccessResponse
)

router = APIRouter(prefix="/api/v1/admin/inventory", tags=["admin:inventory"])


@router.get("", response_model=AdminInventoryListResponse)
async def list_inventory(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    low_stock_only: bool = Query(False),
    product_id: str = Query(None),
    credentials=Depends(security_scheme)
):
    """
    List product inventory
    
    Auth Required: Admin
    
    Query params:
        - low_stock_only: Show only low stock items
        - product_id: Filter by specific product
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        if low_stock_only:
            inventory_list = await admin_service.get_low_stock_products(
                page=page,
                per_page=per_page
            )
            return AdminInventoryListResponse(
                inventories=[
                    AdminInventoryResponse.model_validate(inv).dict() 
                    for inv in inventory_list['inventories']
                ],
                total=inventory_list['total'],
                page=page,
                per_page=per_page,
                total_pages=inventory_list['total_pages']
            )
        
        where = {}
        if product_id:
            where['product_id'] = product_id
        
        total = await db.client.productinventory.count(where=where)
        
        inventories = await db.client.productinventory.find_many(
            where=where,
            skip=(page - 1) * per_page,
            take=per_page,
            include={'product': True}
        )
        
        inventory_list = []
        for inv in inventories:
            inv_dict = AdminInventoryResponse.model_validate(inv).dict()
            inv_dict['product_name'] = inv.product.name if inv.product else None
            inventory_list.append(AdminInventoryResponse(**inv_dict))
        
        return AdminInventoryListResponse(
            inventories=inventory_list,
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
            detail=f"Error fetching inventory: {str(e)}"
        )


@router.get("/{product_id}", response_model=AdminInventoryResponse)
async def get_inventory(product_id: str, credentials=Depends(security_scheme)):
    """
    Get product inventory details
    
    Auth Required: Admin
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        inventory = await db.client.productinventory.find_unique(
            where={'product_id': product_id},
            include={'product': True}
        )
        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventory not found"
            )
        
        inv_dict = AdminInventoryResponse.model_validate(inventory).dict()
        inv_dict['product_name'] = inventory.product.name if inventory.product else None
        return AdminInventoryResponse(**inv_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{inventory_id}/adjust", response_model=SuccessResponse)
async def adjust_inventory(
    inventory_id: str,
    request: AdminInventoryAdjustmentRequest,
    credentials=Depends(security_scheme)
):
    """
    Adjust product inventory
    
    Auth Required: Admin
    
    Change types:
        - ADD: Add quantity to stock
        - REMOVE: Remove quantity from stock
        - ADJUST: Set stock to specific level
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        result = await admin_service.adjust_inventory(
            admin_id=admin.id,
            inventory_id=inventory_id,
            change_type=request.change_type,
            quantity=request.quantity,
            reason=request.reason,
            note=request.note
        )
        
        return SuccessResponse(
            message=f"Inventory adjusted successfully. "
                    f"Old stock: {result['old_stock']}, New stock: {result['new_stock']}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error adjusting inventory: {str(e)}"
        )


@router.get("/low-stock/alert", response_model=AdminInventoryListResponse)
async def get_low_stock_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    credentials=Depends(security_scheme)
):
    """
    Get list of low stock products
    
    Auth Required: Admin
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        inventory_data = await admin_service.get_low_stock_products(
            page=page,
            per_page=per_page
        )
        
        return AdminInventoryListResponse(
            inventories=[
                AdminInventoryResponse.model_validate(inv).dict() 
                for inv in inventory_data['inventories']
            ],
            total=inventory_data['total'],
            page=page,
            per_page=per_page,
            total_pages=inventory_data['total_pages']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching low stock products: {str(e)}"
        )
