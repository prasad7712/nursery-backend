"""Admin product management controller"""
from fastapi import APIRouter, Depends, HTTPException, status, Query

from src.middlewares.auth_middleware import security_scheme
from src.plugins.database import db
from src.services.admin_service import admin_service
from src.data_contracts.admin_request_response import (
    AdminProductCreateRequest,
    AdminProductUpdateRequest,
    AdminProductResponse,
    AdminProductListResponse,
    SuccessResponse
)

router = APIRouter(prefix="/api/v1/admin/products", tags=["admin:products"])


@router.get("", response_model=AdminProductListResponse)
async def list_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category_id: str = Query(None),
    is_active: bool = Query(None),
    search: str = Query(None),
    credentials=Depends(security_scheme)
):
    """
    List all products with filters
    
    Auth Required: Admin
    
    Query params:
        - page: Page number (default 1)
        - per_page: Items per page (default 20)
        - category_id: Filter by category
        - is_active: Filter by active status
        - search: Search by name or scientific name
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        where = {}
        if category_id:
            where['category_id'] = category_id
        if is_active is not None:
            where['is_active'] = is_active
        if search:
            where['OR'] = [
                {'name': {'contains': search}},
                {'scientific_name': {'contains': search}}
            ]
        
        total = await db.client.product.count(where=where)
        
        products = await db.client.product.find_many(
            where=where,
            skip=(page - 1) * per_page,
            take=per_page
        )
        
        # Sort by created_at descending
        products = sorted(products, key=lambda x: x.created_at, reverse=True) if products else []
        
        return AdminProductListResponse(
            products=[AdminProductResponse.model_validate(p) for p in products],
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
            detail=f"Error fetching products: {str(e)}"
        )


@router.get("/{product_id}", response_model=AdminProductResponse)
async def get_product(product_id: str, credentials=Depends(security_scheme)):
    """
    Get product details
    
    Auth Required: Admin
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        product = await db.client.product.find_unique(where={'id': product_id})
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        return AdminProductResponse.model_validate(product)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("", response_model=AdminProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    request: AdminProductCreateRequest,
    credentials=Depends(security_scheme)
):
    """
    Create new product
    
    Auth Required: Admin
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        # Check if category exists
        category = await db.client.category.find_unique(where={'id': request.category_id})
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found"
            )
        
        # Generate slug from name
        slug = request.name.lower().replace(' ', '-').replace('_', '-')
        
        # Check if slug already exists
        existing = await db.client.product.find_unique(where={'slug': slug})
        if existing:
            slug = f"{slug}-{len(await db.client.product.find_many(where={'slug': {'contains': slug}}))+1}"
        
        # Create product
        product = await db.client.product.create(
            data={
                'name': request.name,
                'scientific_name': request.scientific_name,
                'slug': slug,
                'category_id': request.category_id,
                'price': request.price,
                'cost_price': request.cost_price,
                'image_url': request.image_url,
                'description': request.description,
                'care_instructions': request.care_instructions,
                'light_requirements': request.light_requirements,
                'watering_frequency': request.watering_frequency,
                'temperature_range': request.temperature_range,
                'is_active': request.is_active
            }
        )
        
        # Create inventory record
        await db.client.productinventory.create(
            data={
                'product_id': product.id,
                'stock_level': 0,
                'low_stock_threshold': 10
            }
        )
        
        # Log admin action
        await admin_service.log_admin_action(
            admin_id=admin.id,
            action_type='CREATE',
            entity_type='Product',
            entity_id=product.id,
            new_values={
                'name': product.name,
                'price': product.price,
                'category_id': product.category_id
            }
        )
        
        return AdminProductResponse.model_validate(product)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating product: {str(e)}"
        )


@router.put("/{product_id}", response_model=AdminProductResponse)
async def update_product(
    product_id: str,
    request: AdminProductUpdateRequest,
    credentials=Depends(security_scheme)
):
    """
    Update product
    
    Auth Required: Admin
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        product = await db.client.product.find_unique(where={'id': product_id})
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # If category_id is provided, check if it exists
        if request.category_id:
            category = await db.client.category.find_unique(where={'id': request.category_id})
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category not found"
                )
        
        # Build update data
        update_data = {k: v for k, v in request.dict(exclude_unset=True).items() if v is not None}
        
        if update_data:
            updated_product = await db.client.product.update(
                where={'id': product_id},
                data=update_data
            )
            
            # Log admin action
            await admin_service.log_admin_action(
                admin_id=admin.id,
                action_type='UPDATE',
                entity_type='Product',
                entity_id=product_id,
                old_values={k: getattr(product, k) for k in update_data.keys()},
                new_values=update_data
            )
            
            return AdminProductResponse.model_validate(updated_product)
        
        return AdminProductResponse.model_validate(product)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating product: {str(e)}"
        )


@router.delete("/{product_id}", response_model=SuccessResponse)
async def delete_product(product_id: str, credentials=Depends(security_scheme)):
    """
    Delete product (soft delete via is_active=false)
    
    Auth Required: Admin
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        product = await db.client.product.find_unique(where={'id': product_id})
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Soft delete
        await db.client.product.update(
            where={'id': product_id},
            data={'is_active': False}
        )
        
        # Log admin action
        await admin_service.log_admin_action(
            admin_id=admin.id,
            action_type='DELETE',
            entity_type='Product',
            entity_id=product_id,
            old_values={'is_active': True},
            new_values={'is_active': False}
        )
        
        return SuccessResponse(message="Product deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting product: {str(e)}"
        )


@router.post("/{product_id}/activate", response_model=SuccessResponse)
async def activate_product(product_id: str, credentials=Depends(security_scheme)):
    """
    Activate product
    
    Auth Required: Admin
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        product = await db.client.product.find_unique(where={'id': product_id})
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        await db.client.product.update(
            where={'id': product_id},
            data={'is_active': True}
        )
        
        await admin_service.log_admin_action(
            admin_id=admin.id,
            action_type='ACTIVATE',
            entity_type='Product',
            entity_id=product_id
        )
        
        return SuccessResponse(message="Product activated successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
