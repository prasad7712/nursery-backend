"""Seed database with initial products and categories"""
import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from src.database import async_session_maker
from src.models.product import Category, Product
from src.models.admin import ProductInventory
from src.models.product_disease import ProductDisease


async def seed_database():
    """Seed database with categories and products"""
    
    async with async_session_maker() as session:
        try:
            print("✅ Connected to database")
        
        # Categories seed data
        categories_data = [
            {
                "name": "Flowering Plants",
                "slug": "flowering-plants",
                "description": "Beautiful flowering plants that add color and fragrance to your home",
                "icon": "🌸"
            },
            {
                "name": "Succulents",
                "slug": "succulents",
                "description": "Low-maintenance hardy plants with thick fleshy leaves",
                "icon": "🌵"
            },
            {
                "name": "Herbs",
                "slug": "herbs",
                "description": "Culinary and medicinal herbs for cooking and wellness",
                "icon": "🌿"
            },
            {
                "name": "Vegetables",
                "slug": "vegetables",
                "description": "Easy-to-grow vegetables for home gardening",
                "icon": "🥬"
            },
            {
                "name": "Indoor Plants",
                "slug": "indoor-plants",
                "description": "Perfect plants for indoor home decoration",
                "icon": "🏠"
            }
        ]
        
        # Create/update categories (idempotent)
        print("\n📌 Upserting categories...")
        created_categories: dict[str, str] = {}
        for cat_data in categories_data:
            stmt = select(Category).where(Category.slug == cat_data["slug"])
            result = await session.execute(stmt)
            category = result.scalar_one_or_none()
            
            if category:
                # Update existing category
                category.name = cat_data["name"]
                category.description = cat_data["description"]
                category.icon = cat_data.get("icon")
            else:
                # Create new category
                category = Category(
                    name=cat_data["name"],
                    slug=cat_data["slug"],
                    description=cat_data["description"],
                    icon=cat_data.get("icon")
                )
                session.add(category)
            
            await session.flush()
            created_categories[cat_data["slug"]] = category.id
            print(f"  ✅ Upserted category: {cat_data['name']}")
        
        await session.commit()
        
        # Products seed data
        products_data = [
            {
                "name": "Monstera Deliciosa",
                "scientific_name": "Monstera deliciosa",
                "slug": "monstera-deliciosa",
                "category_id": created_categories.get("indoor-plants"),
                "price": 35.99,
                "cost_price": 15.00,
                "image_url": "https://images.unsplash.com/photo-1562621976-a9b27aba3a26?w=500",
                "description": "Large-leaved tropical plant with iconic split leaves. Thrives in moderate light and indirect sunlight.",
                "care_instructions": "Water when soil is partly dry. Keep in indirect light. Provide trellis support.",
                "light_requirements": "Indirect bright light",
                "watering_frequency": "Weekly",
                "temperature_range": "65-75°F (18-24°C)",
                "is_active": True
            },
            {
                "name": "Snake Plant",
                "scientific_name": "Sansevieria trifasciata",
                "slug": "snake-plant",
                "category_id": created_categories.get("indoor-plants"),
                "price": 22.99,
                "cost_price": 8.00,
                "image_url": "https://images.unsplash.com/photo-1592771512295-35484d5bcaf5?w=500",
                "description": "Extremely hardy plant that tolerates neglect. Air-purifying qualities.",
                "care_instructions": "Water sparingly. Allow soil to dry between watering. Low light tolerant.",
                "light_requirements": "Low to moderate light",
                "watering_frequency": "Every 2-3 weeks",
                "temperature_range": "60-75°F (15-24°C)",
                "is_active": True
            },
            {
                "name": "Aloe Vera",
                "scientific_name": "Aloe barbadensis miller",
                "slug": "aloe-vera",
                "category_id": created_categories.get("succulents"),
                "price": 18.99,
                "cost_price": 6.00,
                "image_url": "https://images.unsplash.com/photo-1585470981016-4c9d24ce0310?w=500",
                "description": "Medicinal succulent with gel-filled leaves. Great for skin care and healing.",
                "care_instructions": "Water sparingly. Prefers dry conditions. Use cactus soil.",
                "light_requirements": "Bright light, direct sun preferred",
                "watering_frequency": "Monthly",
                "temperature_range": "55-85°F (13-29°C)",
                "is_active": True
            },
            {
                "name": "Basil",
                "scientific_name": "Ocimum basilicum",
                "slug": "basil",
                "category_id": created_categories.get("herbs"),
                "price": 12.99,
                "cost_price": 3.00,
                "image_url": "https://images.unsplash.com/photo-1571314121769-87d1273c36be?w=500",
                "description": "Aromatic culinary herb perfect for cooking. Fresh leaves year-round.",
                "care_instructions": "Pinch off flower buds to encourage leaf growth. Harvest regularly.",
                "light_requirements": "6-8 hours direct sunlight",
                "watering_frequency": "Daily, keep soil moist",
                "temperature_range": "70-85°F (21-29°C)",
                "is_active": True
            },
            {
                "name": "Cherry Tomato",
                "scientific_name": "Solanum lycopersicum var. cerasiforme",
                "slug": "cherry-tomato",
                "category_id": created_categories.get("vegetables"),
                "price": 24.99,
                "cost_price": 8.00,
                "image_url": "https://images.unsplash.com/photo-1589546814876-64a5d33db61e?w=500",
                "description": "Compact plant producing sweet cherry tomatoes. Ideal for container growing.",
                "care_instructions": "Support with stakes. Water consistently. Fertilize bi-weekly.",
                "light_requirements": "Full sun, 6-8 hours daily",
                "watering_frequency": "Daily during growing season",
                "temperature_range": "65-85°F (18-29°C)",
                "is_active": True
            },
            {
                "name": "Mint",
                "scientific_name": "Mentha spicata",
                "slug": "mint",
                "category_id": created_categories.get("herbs"),
                "price": 10.99,
                "cost_price": 2.50,
                "image_url": "https://images.unsplash.com/photo-1618841714828-54e23f5828fc?w=500",
                "description": "Refreshing herb perfect for teas and beverages. Spreads quickly.",
                "care_instructions": "Trim regularly to prevent woodiness. Prefers moist soil.",
                "light_requirements": "Partial to full sun",
                "watering_frequency": "Keep soil consistently moist",
                "temperature_range": "60-75°F (15-24°C)",
                "is_active": True
            },
            {
                "name": "Pothos",
                "scientific_name": "Epipremnum aureum",
                "slug": "pothos",
                "category_id": created_categories.get("indoor-plants"),
                "price": 19.99,
                "cost_price": 7.00,
                "image_url": "https://images.unsplash.com/photo-1530973802808-b01de566ed85?w=500",
                "description": "Trailing vine perfect for hanging baskets. Tolerates various light conditions.",
                "care_instructions": "Water when soil is dry. Can be trained on moss poles.",
                "light_requirements": "Indirect light, tolerates low light",
                "watering_frequency": "Every 1-2 weeks",
                "temperature_range": "65-80°F (18-26°C)",
                "is_active": True
            },
            {
                "name": "Spinach",
                "scientific_name": "Spinacia oleracea",
                "slug": "spinach",
                "category_id": created_categories.get("vegetables"),
                "price": 14.99,
                "cost_price": 4.00,
                "image_url": "https://images.unsplash.com/photo-1541519227354-08fa5d50c44d?w=500",
                "description": "Nutritious leafy green vegetable. Quick-growing and cold-hardy.",
                "care_instructions": "Harvest outer leaves as needed. Keep soil moist.",
                "light_requirements": "Full sun to partial shade",
                "watering_frequency": "Keep soil moist, don't overwater",
                "temperature_range": "50-70°F (10-21°C)",
                "is_active": True
            },
            {
                "name": "Roses",
                "scientific_name": "Rosa sp.",
                "slug": "roses",
                "category_id": created_categories.get("flowering-plants"),
                "price": 45.99,
                "cost_price": 18.00,
                "image_url": "https://images.unsplash.com/photo-1606187159385-f45f4b3faaa5?w=500",
                "description": "Elegant flowering plant with long-lasting blooms. Classic choice for gardens.",
                "care_instructions": "Prune regularly. Deadhead spent flowers. Fertilize monthly.",
                "light_requirements": "Full sun, 6+ hours daily",
                "watering_frequency": "3 times per week",
                "temperature_range": "50-75°F (10-24°C)",
                "is_active": True
            },
            {
                "name": "Jade Plant",
                "scientific_name": "Crassula ovata",
                "slug": "jade-plant",
                "category_id": created_categories.get("succulents"),
                "price": 28.99,
                "cost_price": 10.00,
                "image_url": "https://images.unsplash.com/photo-1586262841167-e27c4e97f85b?w=500",
                "description": "Slow-growing succulent with fleshy leaves. Symbol of luck and prosperity.",
                "care_instructions": "Water sparingly. Allow soil to dry between waterings. Bright light.",
                "light_requirements": "Bright light, direct sun",
                "watering_frequency": "Every 2-3 weeks",
                "temperature_range": "65-75°F (18-24°C)",
                "is_active": True
            }
        ]
        
        # Create/update products (idempotent)
        print("\n🌱 Upserting products...")
        for prod_data in products_data:
            try:
                # Skip if category doesn't exist
                if not prod_data.get("category_id"):
                    print(f"  ⚠️  Skipping {prod_data['name']} - category not found")
                    continue
                
                # Check if product exists
                stmt = select(Product).where(Product.slug == prod_data["slug"])
                result = await session.execute(stmt)
                product = result.scalar_one_or_none()
                
                if product:
                    # Update existing product
                    product.name = prod_data["name"]
                    product.scientific_name = prod_data.get("scientific_name")
                    product.category_id = prod_data["category_id"]
                    product.price = prod_data["price"]
                    product.cost_price = prod_data.get("cost_price")
                    product.image_url = prod_data["image_url"]
                    product.description = prod_data["description"]
                    product.care_instructions = prod_data["care_instructions"]
                    product.light_requirements = prod_data["light_requirements"]
                    product.watering_frequency = prod_data["watering_frequency"]
                    product.temperature_range = prod_data["temperature_range"]
                    product.is_active = prod_data.get("is_active", True)
                else:
                    # Create new product
                    product = Product(
                        name=prod_data["name"],
                        scientific_name=prod_data.get("scientific_name"),
                        slug=prod_data["slug"],
                        category_id=prod_data["category_id"],
                        price=prod_data["price"],
                        cost_price=prod_data.get("cost_price"),
                        image_url=prod_data["image_url"],
                        description=prod_data["description"],
                        care_instructions=prod_data["care_instructions"],
                        light_requirements=prod_data["light_requirements"],
                        watering_frequency=prod_data["watering_frequency"],
                        temperature_range=prod_data["temperature_range"],
                        is_active=prod_data.get("is_active", True)
                    )
                    session.add(product)
                
                await session.flush()
                print(f"  ✅ Upserted product: {prod_data['name']} (ID: {product.id})")
                
                # Ensure inventory exists for the product
                stmt_inv = select(ProductInventory).where(ProductInventory.product_id == product.id)
                result_inv = await session.execute(stmt_inv)
                inventory = result_inv.scalar_one_or_none()
                
                if inventory:
                    inventory.stock_level = 50
                    inventory.low_stock_threshold = 10
                else:
                    inventory = ProductInventory(
                        product_id=product.id,
                        stock_level=50,
                        low_stock_threshold=10
                    )
                    session.add(inventory)
                
                await session.flush()
                
                # Add some diseases for the product (skip if they exist)
                diseases = ["Leaf Spot", "Root Rot", "Pests"]
                for disease in diseases[:2]:  # Add 2 diseases per product
                    try:
                        stmt_disease = select(ProductDisease).where(
                            (ProductDisease.product_id == product.id) & 
                            (ProductDisease.disease_name == disease)
                        )
                        result_disease = await session.execute(stmt_disease)
                        existing = result_disease.scalar_one_or_none()
                        
                        if not existing:
                            product_disease = ProductDisease(
                                product_id=product.id,
                                disease_name=disease
                            )
                            session.add(product_disease)
                    except Exception:
                        # Disease might already exist, skip
                        pass
                        
            except Exception as e:
                print(f"  ⚠️  Product {prod_data['name']} error: {str(e)[:120]}")
        
        await session.commit()
        
        # Print summary
        print("\n" + "="*60)
        print("✅ DATABASE SEEDING COMPLETE!")
        print("="*60)
        
        # Get counts
        cat_count_result = await session.execute(select(func.count()).select_from(Category))
        cat_count = cat_count_result.scalar()
        
        prod_count_result = await session.execute(select(func.count()).select_from(Product))
        prod_count = prod_count_result.scalar()
        
        inv_count_result = await session.execute(select(func.count()).select_from(ProductInventory))
        inv_count = inv_count_result.scalar()
        
        print(f"📊 Summary:")
        print(f"   - Categories: {cat_count}")
        print(f"   - Products: {prod_count}")
        print(f"   - Inventories: {inv_count}")
        
    except Exception as e:
        await session.rollback()
        print(f"\n❌ Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(seed_database())
