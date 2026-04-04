"""Core product business logic"""
from typing import Optional, List, Dict, Any

from src.plugins.database import db


class ProductCore:
    """Core product logic"""
    
    async def get_all_products(
        self,
        category_id: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 10
    ) -> Dict[str, Any]:
        """Get all active products with optional filtering and pagination"""
        
        # Build where conditions
        where_conditions = {'is_active': True}
        
        if category_id:
            where_conditions['category_id'] = category_id
        
        if search:
            # Search in name or description
            where_conditions['OR'] = [
                {'name': {'contains': search}},
                {'description': {'contains': search}}
            ]
        
        # Get total count
        total = await db.client.product.count(where=where_conditions)
        
        # Calculate skip for pagination
        skip = (page - 1) * per_page
        
        # Get paginated products
        products = await db.client.product.find_many(
            where=where_conditions,
            skip=skip,
            take=per_page,
            include={'diseases': True}
        )
        
        # Convert to dictionaries with common_diseases
        products_list = []
        for product in products:
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
                'common_diseases': [d.disease_name for d in product.diseases] if hasattr(product, 'diseases') else [],
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
    
    async def get_product_detail(self, product_id: str) -> Dict[str, Any]:
        """Get product detail by ID"""
        
        product = await db.client.product.find_unique(
            where={'id': product_id},
            include={'diseases': True}
        )
        
        if not product:
            raise ValueError("Product not found")
        
        if not product.is_active:
            raise ValueError("Product not found")
        
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
            'common_diseases': [d.disease_name for d in product.diseases] if hasattr(product, 'diseases') else [],
            'is_active': product.is_active,
            'created_at': product.created_at,
            'updated_at': product.updated_at
        }
        
        return product_dict
    
    async def get_all_categories(self) -> List[Dict[str, Any]]:
        """Get all categories"""
        
        categories = await db.client.category.find_many()
        
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
