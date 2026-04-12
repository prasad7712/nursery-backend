"""Admin product management controller"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from src.middlewares.auth_middleware import security_scheme
from src.database import get_session
from src.services.admin_service import admin_service
from src.models.product import Product, Category
from src.models.admin import ProductInventory
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
    credentials=Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
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
        
        where_conditions = []
        if category_id:
            where_conditions.append(Product.category_id == category_id)
        if is_active is not None:
            where_conditions.append(Product.is_active == is_active)
        if search:
            where_conditions.append(or_(
                Product.name.contains(search),
                Product.scientific_name.contains(search)
            ))
        
        # Build query
        stmt = select(Product)
        if where_conditions:
            from sqlalchemy import and_
            stmt = stmt.where(and_(*where_conditions)) if len(where_conditions) > 1 else stmt.where(where_conditions[0])
        
        # Get total count
        count_stmt = select(func.count()).select_from(Product)
        if where_conditions:
            from sqlalchemy import and_
            count_stmt = count_stmt.where(and_(*where_conditions)) if len(where_conditions) > 1 else count_stmt.where(where_conditions[0])
        count_result = await session.execute(count_stmt)
        total = count_result.scalar() or 0
        
        # Get paginated results
        stmt = stmt.order_by(Product.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        result = await session.execute(stmt)
        products = result.scalars().all()
        
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
async def get_product(
    product_id: str,
    credentials=Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
):
    """
    Get product details
    
    Auth Required: Admin
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        stmt = select(Product).where(Product.id == product_id)
        result = await session.execute(stmt)
        product = result.scalar_one_or_none()
        
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
    credentials=Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
):
    """
    Create new product
    
    Auth Required: Admin
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        # Check if category exists
        stmt_cat = select(Category).where(Category.id == request.category_id)
        result_cat = await session.execute(stmt_cat)
        category = result_cat.scalar_one_or_none()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found"
            )
        
        # Generate slug from name
        slug = request.name.lower().replace(' ', '-').replace('_', '-')
        
        # Check if slug already exists
        stmt_existing = select(Product).where(Product.slug == slug)
        result_existing = await session.execute(stmt_existing)
        existing = result_existing.scalar_one_or_none()
        
        if existing:
            # Get count of products with similar slug
            stmt_count = select(func.count()).select_from(Product).where(Product.slug.contains(slug))
            result_count = await session.execute(stmt_count)
            count = result_count.scalar() or 0
            slug = f"{slug}-{count + 1}"
        
        # Create product
        product = Product(
            name=request.name,
            scientific_name=request.scientific_name,
            slug=slug,
            category_id=request.category_id,
            price=request.price,
            cost_price=request.cost_price,
            image_url=request.image_url,
            description=request.description,
            care_instructions=request.care_instructions,
            light_requirements=request.light_requirements,
            watering_frequency=request.watering_frequency,
            temperature_range=request.temperature_range,
            is_active=request.is_active
        )
        session.add(product)
        await session.flush()
        
        # Create inventory record
        inventory = ProductInventory(
            product_id=product.id,
            stock_level=0,
            low_stock_threshold=10
        )
        session.add(inventory)
        await session.commit()
        
        # Log admin action
        await admin_service.log_admin_action(
            session,
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
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating product: {str(e)}"
        )


@router.put("/{product_id}", response_model=AdminProductResponse)
async def update_product(
    product_id: str,
    request: AdminProductUpdateRequest,
    credentials=Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
):
    """
    Update product
    
    Auth Required: Admin
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        stmt = select(Product).where(Product.id == product_id)
        result = await session.execute(stmt)
        product = result.scalar_one_or_none()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # If category_id is provided, check if it exists
        if request.category_id:
            stmt_cat = select(Category).where(Category.id == request.category_id)
            result_cat = await session.execute(stmt_cat)
            category = result_cat.scalar_one_or_none()
            
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category not found"
                )
        
        # Get old values for logging
        old_values = {k: getattr(product, k) for k in request.dict(exclude_unset=True).keys() if hasattr(product, k)}
        
        # Update product with provided values
        update_data = request.dict(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None and hasattr(product, key):
                setattr(product, key, value)
        
        await session.commit()
        
        # Log admin action
        await admin_service.log_admin_action(
            session,
            admin_id=admin.id,
            action_type='UPDATE',
            entity_type='Product',
            entity_id=product_id,
            old_values=old_values,
            new_values=update_data
        )
        
        return AdminProductResponse.model_validate(product)
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating product: {str(e)}"
        )


@router.delete("/{product_id}", response_model=SuccessResponse)
async def delete_product(
    product_id: str,
    credentials=Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
):
    """
    Delete product (soft delete via is_active=false)
    
    Auth Required: Admin
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        stmt = select(Product).where(Product.id == product_id)
        result = await session.execute(stmt)
        product = result.scalar_one_or_none()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Soft delete
        product.is_active = False
        await session.commit()
        
        # Log admin action
        await admin_service.log_admin_action(
            session,
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
async def activate_product(
    product_id: str,
    credentials=Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
):
    """
    Activate product
    
    Auth Required: Admin
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        stmt = select(Product).where(Product.id == product_id)
        result = await session.execute(stmt)
        product = result.scalar_one_or_none()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        product.is_active = True
        await session.commit()
        
        await admin_service.log_admin_action(
            session,
            admin_id=admin.id,
            action_type='ACTIVATE',
            entity_type='Product',
            entity_id=product_id
        )
        
        return SuccessResponse(message="Product activated successfully")
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
