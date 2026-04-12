"""Database schema initialization script"""
import asyncio
from sqlalchemy import text, select, func

from src.database import engine, async_session_maker
from src.models.user import User
from src.models.product import Category, Product
from src.models.product_disease import ProductDisease


async def init_schema():
    """Initialize database schema by creating tables"""
    
    try:
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(lambda sync_conn: __import__('src.models.base', fromlist=['Base']).Base.metadata.create_all(sync_conn))
        print("✓ Database tables created/verified")
        
        # Verify tables by running queries
        async with async_session_maker() as session:
            # Verify users table
            users_count = await session.execute(select(func.count()).select_from(User))
            users_result = users_count.scalar()
            print(f"✓ Users table verified. Count: {users_result}")
            
            # Verify categories table
            categories_count = await session.execute(select(func.count()).select_from(Category))
            categories_result = categories_count.scalar()
            print(f"✓ Categories table verified. Count: {categories_result}")
            
            # Verify products table
            products_count = await session.execute(select(func.count()).select_from(Product))
            products_result = products_count.scalar()
            print(f"✓ Products table verified. Count: {products_result}")
            
            # Verify product diseases table
            diseases_count = await session.execute(select(func.count()).select_from(ProductDisease))
            diseases_result = diseases_count.scalar()
            print(f"✓ ProductDisease table verified. Count: {diseases_result}")
        
        print("\n✅ All database tables initialized successfully!")
        
    except Exception as e:
        print(f"❌ Schema initialization failed: {e}")
        print(f"   Please ensure the database is running and DATABASE_URL is correct.")
        raise


if __name__ == "__main__":
    asyncio.run(init_schema())
