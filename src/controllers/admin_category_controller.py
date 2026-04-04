"""Admin category management controller"""
from fastapi import APIRouter, Depends, HTTPException, status, Query

from src.middlewares.auth_middleware import security_scheme
from src.plugins.database import db
from src.services.admin_service import admin_service
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
    credentials=Depends(security_scheme)
):
    """
    List all categories
    
    Auth Required: Admin
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        where = {}
        if search:
            where['name'] = {'contains': search}
        
        total = await db.client.category.count(where=where)
        
        categories = await db.client.category.find_many(
            where=where,
            skip=(page - 1) * per_page,
            take=per_page,
            include={'products': True},
            order_by=[{'created_at': 'desc'}]
        )
        
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
async def get_category(category_id: str, credentials=Depends(security_scheme)):
    """
    Get category details
    
    Auth Required: Admin
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        category = await db.client.category.find_unique(
            where={'id': category_id},
            include={'products': True}
        )
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
    credentials=Depends(security_scheme)
):
    """
    Create new category
    
    Auth Required: Admin
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        # Generate slug
        slug = request.name.lower().replace(' ', '-')
        
        # Check if slug exists
        existing = await db.client.category.find_unique(where={'slug': slug})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists"
            )
        
        category = await db.client.category.create(
            data={
                'name': request.name,
                'slug': slug,
                'description': request.description,
                'icon': request.icon
            }
        )
        
        await admin_service.log_admin_action(
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating category: {str(e)}"
        )


@router.put("/{category_id}", response_model=AdminCategoryResponse)
async def update_category(
    category_id: str,
    request: AdminCategoryUpdateRequest,
    credentials=Depends(security_scheme)
):
    """
    Update category
    
    Auth Required: Admin
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        category = await db.client.category.find_unique(where={'id': category_id})
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        update_data = {k: v for k, v in request.dict(exclude_unset=True).items() if v is not None}
        
        if update_data:
            updated_category = await db.client.category.update(
                where={'id': category_id},
                data=update_data,
                include={'products': True}
            )
            
            await admin_service.log_admin_action(
                admin_id=admin.id,
                action_type='UPDATE',
                entity_type='Category',
                entity_id=category_id,
                old_values={k: getattr(category, k) for k in update_data.keys()},
                new_values=update_data
            )
            
            cat_dict = AdminCategoryResponse.model_validate(updated_category).dict()
            cat_dict['product_count'] = len(updated_category.products)
            return AdminCategoryResponse(**cat_dict)
        
        cat_dict = AdminCategoryResponse.model_validate(category).dict()
        cat_dict['product_count'] = 0
        return AdminCategoryResponse(**cat_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating category: {str(e)}"
        )


@router.delete("/{category_id}", response_model=SuccessResponse)
async def delete_category(category_id: str, credentials=Depends(security_scheme)):
    """
    Delete category
    
    Auth Required: Admin
    
    Note: Only categories with no products can be deleted
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        category = await db.client.category.find_unique(
            where={'id': category_id},
            include={'products': True}
        )
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
        
        await db.client.category.delete(where={'id': category_id})
        
        await admin_service.log_admin_action(
            admin_id=admin.id,
            action_type='DELETE',
            entity_type='Category',
            entity_id=category_id
        )
        
        return SuccessResponse(message="Category deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting category: {str(e)}"
        )
