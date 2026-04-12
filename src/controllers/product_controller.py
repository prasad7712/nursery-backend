"""Product API Controller"""
from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.data_contracts.api_request_response import (
    ProductsListResponse,
    ProductDetailResponse,
    CategoriesListResponse,
    ProductResponse,
    CategoryResponse
)
from src.services.product_service import ProductService
from src.database import get_session


router = APIRouter(prefix="/api/v1", tags=["Products"])
product_service = ProductService()


@router.get("/products", response_model=ProductsListResponse)
async def list_products(
    category_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    session: AsyncSession = Depends(get_session)
):
    """
    Get all active products with optional filtering and pagination
    
    - **category_id**: Optional category ID to filter by
    - **search**: Optional search term to filter by name or description
    - **page**: Page number (default: 1)
    - **per_page**: Items per page (default: 10, max: 100)
    
    Returns paginated list of products with common_diseases array
    """
    try:
        result = await product_service.get_all_products(
            session,
            category_id=category_id,
            search=search,
            page=page,
            per_page=per_page
        )
        
        # Convert to ProductResponse objects
        products = [ProductResponse(**p) for p in result['products']]
        
        return ProductsListResponse(
            products=products,
            total=result['total'],
            page=result['page'],
            per_page=result['per_page']
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve products: {str(e)}"
        )


@router.get("/products/{product_id}", response_model=ProductDetailResponse)
async def get_product_detail(
    product_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Get product details by ID
    
    - **product_id**: Product ID
    
    Returns full product information including care instructions and common diseases
    """
    try:
        product = await product_service.get_product_detail(session, product_id)
        return ProductDetailResponse(**product)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve product: {str(e)}"
        )


@router.get("/categories", response_model=CategoriesListResponse)
async def list_categories(session: AsyncSession = Depends(get_session)):
    """
    Get all product categories
    
    Returns list of categories with names, slugs, descriptions, and icons
    """
    try:
        result = await product_service.get_all_categories(session)
        
        # Convert to CategoryResponse objects
        categories = [CategoryResponse(**c) for c in result['categories']]
        
        return CategoriesListResponse(
            categories=categories,
            total=result['total']
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve categories: {str(e)}"
        )
