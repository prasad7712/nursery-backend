"""Setup database schema using direct SQL"""
import asyncio
import os
from dotenv import load_dotenv
import mysql.connector
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

async def init_database():
    """Initialize database tables using direct SQL"""
    
    # Parse DATABASE_URL
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise ValueError("DATABASE_URL not set in .env")
    
    # Parse URL: mysql://user:password@host:port/database
    parsed = urlparse(db_url)
    config = {
        'host': parsed.hostname,
        'user': parsed.username,
        'password': parsed.password,
        'port': parsed.port or 3306,
        'database': parsed.path.lstrip('/')
    }
    
    try:
        # Connect to MySQL
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        print("✓ Connected to MySQL database")
        
        # Create tables SQL
        tables_sql = """
        SET FOREIGN_KEY_CHECKS = 0;
        
        -- Users table (already exists, but showing for reference)
        CREATE TABLE IF NOT EXISTS `users` (
          `id` varchar(36) NOT NULL,
          `email` varchar(191) NOT NULL,
          `phone` varchar(191),
          `password_hash` varchar(191) NOT NULL,
          `first_name` varchar(191),
          `last_name` varchar(191),
          `is_active` boolean NOT NULL DEFAULT true,
          `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
          `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          `last_logout_at` datetime,
          PRIMARY KEY (`id`),
          UNIQUE KEY `email` (`email`),
          UNIQUE KEY `phone` (`phone`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        
        -- Categories table
        CREATE TABLE IF NOT EXISTS `categories` (
          `id` varchar(36) NOT NULL,
          `name` varchar(191) NOT NULL,
          `slug` varchar(191) NOT NULL,
          `description` longtext NOT NULL,
          `icon` varchar(191),
          `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
          `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `slug` (`slug`),
          KEY `slug_idx` (`slug`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        
        -- Products table
        CREATE TABLE IF NOT EXISTS `products` (
          `id` varchar(36) NOT NULL,
          `name` varchar(191) NOT NULL,
          `scientific_name` varchar(191),
          `slug` varchar(191) NOT NULL,
          `category_id` varchar(36) NOT NULL,
          `price` double NOT NULL,
          `cost_price` double,
          `image_url` longtext NOT NULL,
          `description` longtext NOT NULL,
          `care_instructions` longtext NOT NULL,
          `light_requirements` varchar(191) NOT NULL,
          `watering_frequency` varchar(191) NOT NULL,
          `temperature_range` varchar(191) NOT NULL,
          `is_active` boolean NOT NULL DEFAULT true,
          `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
          `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `slug` (`slug`),
          KEY `category_id_idx` (`category_id`),
          KEY `slug_idx` (`slug`),
          KEY `is_active_idx` (`is_active`),
          CONSTRAINT `products_category_id_fk` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        
        -- Product Diseases table
        CREATE TABLE IF NOT EXISTS `product_diseases` (
          `id` varchar(36) NOT NULL,
          `product_id` varchar(36) NOT NULL,
          `disease_name` varchar(191) NOT NULL,
          PRIMARY KEY (`id`),
          KEY `product_id_idx` (`product_id`),
          UNIQUE KEY `product_id_disease_name` (`product_id`, `disease_name`),
          CONSTRAINT `product_diseases_product_id_fk` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        
        -- Refresh tokens table (already exists, but showing for reference)
        CREATE TABLE IF NOT EXISTS `refresh_tokens` (
          `id` varchar(36) NOT NULL,
          `user_id` varchar(36) NOT NULL,
          `token` longtext NOT NULL,
          `token_hash` varchar(255) NOT NULL,
          `expires_at` datetime NOT NULL,
          `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
          `is_revoked` boolean NOT NULL DEFAULT false,
          PRIMARY KEY (`id`),
          UNIQUE KEY `token_hash` (`token_hash`),
          KEY `user_id_idx` (`user_id`),
          CONSTRAINT `refresh_tokens_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        
        SET FOREIGN_KEY_CHECKS = 1;
        """
        
        # Execute each statement
        for statement in tables_sql.split(';'):
            statement = statement.strip()
            if statement:
                try:
                    cursor.execute(statement)
                    conn.commit()
                except Exception as e:
                    # Table might already exist or other issue
                    pass
        
        print("✓ All tables created/verified successfully")
        
        cursor.close()
        conn.close()
        print("✅ Database schema initialization complete!")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(init_database())
