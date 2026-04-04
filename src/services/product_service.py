"""Product business logic orchestration"""
from typing import Optional, Dict, Any

from src.core.product_core import ProductCore


class ProductService:
    """Product service layer"""
    
    def __init__(self):
        self.product_core = ProductCore()
    
    async def get_all_products(
        self,
        category_id: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 10
    ) -> Dict[str, Any]:
        """Get all products with filtering and pagination"""
        try:
            return await self.product_core.get_all_products(
                category_id=category_id,
                search=search,
                page=page,
                per_page=per_page
            )
        except ValueError as e:
            raise ValueError(str(e))
    
    async def get_product_detail(self, product_id: str) -> Dict[str, Any]:
        """Get product details"""
        try:
            return await self.product_core.get_product_detail(product_id)
        except ValueError as e:
            raise ValueError(str(e))
    
    async def get_all_categories(self) -> Dict[str, Any]:
        """Get all categories"""
        try:
            categories = await self.product_core.get_all_categories()
            return {
                'categories': categories,
                'total': len(categories)
            }
        except ValueError as e:
            raise ValueError(str(e))
