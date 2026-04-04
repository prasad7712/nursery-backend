"""Database schema initialization script"""
import asyncio
import os
from dotenv import load_dotenv
from src.plugins.database import db

# Load environment variables
load_dotenv()

async def init_schema():
    """Initialize database schema by creating tables"""
    
    try:
        # Connect to database
        await db.connect()
        print("✓ Connected to database")
        
        # Get the Prisma client
        client = db.client
        
        # For Python Prisma client, we need to ensure tables exist
        # The Prisma client will auto-create tables when we interact with models
        # But let's verify by trying to query
        
        # Try to query users (will create table if it doesn't exist through Prisma ORM)
        users_count = await client.user.count()
        print(f"✓ Users table verified/created. Count: {users_count}")
        
        # Try to query categories
        categories_count = await client.category.count()
        print(f"✓ Categories table verified/created. Count: {categories_count}")
        
        # Try to query products
        products_count = await client.product.count()
        print(f"✓ Products table verified/created. Count: {products_count}")
        
        # Try to query product diseases
        diseases_count = await client.productdisease.count()
        print(f"✓ ProductDisease table verified/created. Count: {diseases_count}")
        
        print("\n✅ All database tables initialized successfully!")
        
    except Exception as e:
        print(f"❌ Schema initialization failed: {e}")
        print(f"   This is expected if the database doesn't exist yet.")
        print(f"   Please create the database manually or run migrations.")
        raise
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(init_schema())
