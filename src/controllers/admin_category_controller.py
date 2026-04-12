"""Admin category management controller"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.middlewares.auth_middleware import security_scheme
from src.database import get_session
from src.services.admin_service import admin_service
from src.models.product import Category, Product
from src.data_contracts.admin_request_response import (
    AdminCategoryCreateRequest,
    AdminCategoryUpdateRequest,
    AdminCategoryResponse,
    AdminCategoryListResponse,
    SuccessResponse
)

router = APIRouter(prefix="/api/v1/admin/categories", tags=["admin:categories"])


@router.get("", response_model=AdminCategoryListResponse)
async def list_categories(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str = Query(None),
    credentials=Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
):
    """
    List all categories
    
    Auth Required: Admin
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        where_conditions = []
        if search:
            where_conditions.append(Category.name.contains(search))
        
        # Build query
        stmt = select(Category)
        if where_conditions:
            stmt = stmt.where(where_conditions[0])
        
        # Get total count
        count_stmt = select(func.count()).select_from(Category)
        if where_conditions:
            count_stmt = count_stmt.where(where_conditions[0])
        count_result = await session.execute(count_stmt)
        total = count_result.scalar() or 0
        
        # Get paginated results with relationships
        from sqlalchemy.orm import selectinload
        stmt = stmt.options(selectinload(Category.products)).order_by(
            Category.created_at.desc()
        ).offset((page - 1) * per_page).limit(per_page)
        result = await session.execute(stmt)
        categories = result.scalars().unique().all()
        
        # Sort by created_at descending
        categories = sorted(categories, key=lambda x: x.created_at, reverse=True) if categories else []
        
        result = []
        for cat in categories:
            cat_dict = AdminCategoryResponse.model_validate(cat).dict()
            cat_dict['product_count'] = len(cat.products) if hasattr(cat, 'products') else 0
            result.append(AdminCategoryResponse(**cat_dict))
        
        return AdminCategoryListResponse(
            categories=result,
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
            detail=f"Error fetching categories: {str(e)}"
        )


@router.get("/{category_id}", response_model=AdminCategoryResponse)
async def get_category(
    category_id: str,
    credentials=Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
):
    """Get category details
    
    Auth Required: Admin
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        from sqlalchemy.orm import selectinload
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        stmt = select(Category).where(Category.id == category_id).options(selectinload(Category.products))
        result = await session.execute(stmt)
        category = result.scalar_one_or_none()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        cat_dict = AdminCategoryResponse.model_validate(category).dict()
        cat_dict['product_count'] = len(category.products) if hasattr(category, 'products') else 0
        return AdminCategoryResponse(**cat_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("", response_model=AdminCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    request: AdminCategoryCreateRequest,
    credentials=Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
):
    """Create new category
    
    Auth Required: Admin
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        # Generate slug
        slug = request.name.lower().replace(' ', '-')
        
        # Check if slug exists
        stmt_existing = select(Category).where(Category.slug == slug)
        result_existing = await session.execute(stmt_existing)
        existing = result_existing.scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists"
            )
        
        category = Category(
            name=request.name,
            slug=slug,
            description=request.description,
            icon=request.icon
        )
        session.add(category)
        await session.commit()
        
        await admin_service.log_admin_action(
            session,
            admin_id=admin.id,
            action_type='CREATE',
            entity_type='Category',
            entity_id=category.id,
            new_values={'name': category.name}
        )
        
        cat_dict = AdminCategoryResponse.model_validate(category).dict()
        cat_dict['product_count'] = 0
        return AdminCategoryResponse(**cat_dict)
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating category: {str(e)}"
        )


@router.put("/{category_id}", response_model=AdminCategoryResponse)
async def update_category(
    category_id: str,
    request: AdminCategoryUpdateRequest,
    credentials=Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
):
    """Update category
    
    Auth Required: Admin
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        from sqlalchemy.orm import selectinload
        
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        stmt = select(Category).where(Category.id == category_id)
        result = await session.execute(stmt)
        category = result.scalar_one_or_none()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        update_data = {k: v for k, v in request.dict(exclude_unset=True).items() if v is not None}
        
        if update_data:
            old_values = {k: getattr(category, k) for k in update_data.keys()}
            for key, value in update_data.items():
                if hasattr(category, key):
                    setattr(category, key, value)
            
            await session.commit()
            
            await admin_service.log_admin_action(
                session,
                admin_id=admin.id,
                action_type='UPDATE',
                entity_type='Category',
                entity_id=category_id,
                old_values=old_values,
                new_values=update_data
            )
            
            # Refresh to get relationship data
            await session.refresh(category, ['products'])
            cat_dict = AdminCategoryResponse.model_validate(category).dict()
            cat_dict['product_count'] = len(category.products) if hasattr(category, 'products') else 0
            return AdminCategoryResponse(**cat_dict)
        
        cat_dict = AdminCategoryResponse.model_validate(category).dict()
        cat_dict['product_count'] = 0
        return AdminCategoryResponse(**cat_dict)
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating category: {str(e)}"
        )


@router.delete("/{category_id}", response_model=SuccessResponse)
async def delete_category(
    category_id: str,
    credentials=Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
):
    """Delete category
    
    Auth Required: Admin
    
    Note: Only categories with no products can be deleted
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        from sqlalchemy.orm import selectinload
        
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        stmt = select(Category).where(Category.id == category_id).options(selectinload(Category.products))
        result = await session.execute(stmt)
        category = result.scalar_one_or_none()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        if len(category.products) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete category with products. Delete products first."
            )
        
        await session.delete(category)
        await session.commit()
        
        await admin_service.log_admin_action(
            session,
            admin_id=admin.id,
            action_type='DELETE',
            entity_type='Category',
            entity_id=category_id
        )
        
        return SuccessResponse(message="Category deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting category: {str(e)}"
        )
