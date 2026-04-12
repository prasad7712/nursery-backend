"""Admin inventory management controller"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.middlewares.auth_middleware import security_scheme
from src.database import get_session
from src.services.admin_service import admin_service
from src.models.admin import ProductInventory
from src.models.product import Product
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
    credentials=Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
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
        
        where_conditions = []
        if low_stock_only:
            where_conditions.append(ProductInventory.stock_level <= ProductInventory.low_stock_threshold)
        if product_id:
            where_conditions.append(ProductInventory.product_id == product_id)
        
        # Build query
        stmt = select(ProductInventory)
        if where_conditions:
            from sqlalchemy import and_
            stmt = stmt.where(and_(*where_conditions)) if len(where_conditions) > 1 else stmt.where(where_conditions[0])
        
        # Get total count
        count_stmt = select(func.count()).select_from(ProductInventory)
        if where_conditions:
            from sqlalchemy import and_
            count_stmt = count_stmt.where(and_(*where_conditions)) if len(where_conditions) > 1 else count_stmt.where(where_conditions[0])
        count_result = await session.execute(count_stmt)
        total = count_result.scalar() or 0
        
        # Get paginated results with relationships
        from sqlalchemy.orm import selectinload
        stmt = stmt.options(selectinload(ProductInventory.product)).offset(
            (page - 1) * per_page
        ).limit(per_page)
        result = await session.execute(stmt)
        inventories = result.scalars().unique().all()
        
        inventory_list = []
        for inv in inventories:
            inv_response = AdminInventoryResponse.model_validate(inv)
            inventory_list.append(inv_response)
        
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
async def get_inventory(
    product_id: str,
    credentials=Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
):
    """Get product inventory details
    
    Auth Required: Admin
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        from sqlalchemy.orm import selectinload
        
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        stmt = select(ProductInventory).where(
            ProductInventory.product_id == product_id
        ).options(selectinload(ProductInventory.product))
        result = await session.execute(stmt)
        inventory = result.scalar_one_or_none()
        
        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventory not found"
            )
        
        return AdminInventoryResponse.model_validate(inventory)
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
    credentials=Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
):
    """Adjust product inventory
    
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
            session,
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
    credentials=Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
):
    """Get list of low stock products
    
    Auth Required: Admin
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        inventory_data = await admin_service.get_low_stock_products(
            session,
            page=page,
            per_page=per_page
        )
        
        return AdminInventoryListResponse(
            inventories=[
                AdminInventoryResponse.model_validate(inv) 
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
