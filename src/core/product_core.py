"""Core product business logic"""
from typing import Optional, List, Dict, Any

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.product import Product, Category, ProductDisease


class ProductCore:
    """Core product logic"""
    
    async def get_all_products(
        self,
        session: AsyncSession,
        category_id: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 10
    ) -> Dict[str, Any]:
        """Get all active products with optional filtering and pagination"""
        
        # Build where conditions
        conditions = [Product.is_active == True]
        
        if category_id:
            conditions.append(Product.category_id == category_id)
        
        if search:
            # Search in name or description
            conditions.append(
                or_(
                    Product.name.contains(search),
                    Product.description.contains(search)
                )
            )
        
        # Get total count
        result = await session.execute(
            select(func.count(Product.id)).where(*conditions)
        )
        total = result.scalar() or 0
        
        # Calculate skip for pagination
        skip = (page - 1) * per_page
        
        # Get paginated products
        result = await session.execute(
            select(Product).where(*conditions).offset(skip).limit(per_page)
        )
        products = result.scalars().all()
        
        # Convert to dictionaries with common_diseases
        products_list = []
        for product in products:
            # Fetch diseases for this product
            result = await session.execute(
                select(ProductDisease).where(ProductDisease.product_id == product.id)
            )
            diseases = result.scalars().all()
            
            product_dict = {
                'id': product.id,
                'name': product.name,
                'scientific_name': product.scientific_name,
                'slug': product.slug,
                'category_id': product.category_id,
                'price': product.price,
                'image_url': product.image_url,
                'description': product.description,
                'care_instructions': product.care_instructions,
                'light_requirements': product.light_requirements,
                'watering_frequency': product.watering_frequency,
                'temperature_range': product.temperature_range,
                'common_diseases': [d.disease_name for d in diseases],
                'is_active': product.is_active,
                'created_at': product.created_at
            }
            products_list.append(product_dict)
        
        return {
            'products': products_list,
            'total': total,
            'page': page,
            'per_page': per_page
        }
    
    async def get_product_detail(self, session: AsyncSession, product_id: str) -> Dict[str, Any]:
        """Get product detail by ID"""
        
        result = await session.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()
        
        if not product or not product.is_active:
            raise ValueError("Product not found")
        
        # Fetch diseases for this product
        result = await session.execute(
            select(ProductDisease).where(ProductDisease.product_id == product.id)
        )
        diseases = result.scalars().all()
        
        # Convert to dictionary with common_diseases
        product_dict = {
            'id': product.id,
            'name': product.name,
            'scientific_name': product.scientific_name,
            'slug': product.slug,
            'category_id': product.category_id,
            'price': product.price,
            'cost_price': product.cost_price,
            'image_url': product.image_url,
            'description': product.description,
            'care_instructions': product.care_instructions,
            'light_requirements': product.light_requirements,
            'watering_frequency': product.watering_frequency,
            'temperature_range': product.temperature_range,
            'common_diseases': [d.disease_name for d in diseases],
            'is_active': product.is_active,
            'created_at': product.created_at,
            'updated_at': product.updated_at
        }
        
        return product_dict
    
    async def get_all_categories(self, session: AsyncSession) -> List[Dict[str, Any]]:
        """Get all categories"""
        
        result = await session.execute(select(Category))
        categories = result.scalars().all()
        
        # Convert to dictionaries
        categories_list = []
        for category in categories:
            category_dict = {
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
                'description': category.description,
                'icon': category.icon
            }
            categories_list.append(category_dict)
        
        return categories_list


# Singleton instance
product_core = ProductCore()
