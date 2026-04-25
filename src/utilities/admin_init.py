"""Initialize admin account on startup"""
import os
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import async_session_maker
from src.models.user import User
from src.utilities.security import security


async def initialize_admin():
    """Create admin account if it doesn't exist"""
    async with async_session_maker() as session:
        try:
            # Read directly from environment variables
            admin_email = os.getenv('ADMIN_EMAIL', None)
            admin_password = os.getenv('ADMIN_PASSWORD', None)
            admin_first_name = os.getenv('ADMIN_FIRST_NAME', 'Admin')
            admin_last_name = os.getenv('ADMIN_LAST_NAME', 'User')
            
            if not admin_email or not admin_password:
                print("⚠️  Admin credentials not configured in .env")
                return
            
            # Strip whitespace and truncate to 72 bytes (bcrypt limit)
            if isinstance(admin_password, str):
                admin_password = admin_password.strip()
                password_bytes = admin_password.encode('utf-8')
                if len(password_bytes) > 72:
                    print(f"⚠️  Admin password exceeds 72 bytes ({len(password_bytes)} bytes), truncating...")
                    # Safely truncate at byte boundary
                    admin_password = password_bytes[:72].decode('utf-8', errors='ignore').strip()
            
            # Check if admin already exists
            stmt = select(User).where(User.email == admin_email)
            result = await session.execute(stmt)
            existing_admin = result.scalar_one_or_none()
            
            if existing_admin:
                print(f"✅ Admin user already exists: {admin_email}")
                return
            
            # Hash password
            password_hash = security.hash_password(admin_password)
            
            # Create admin user
            admin_user = User(
                email=admin_email,
                password_hash=password_hash,
                first_name=admin_first_name,
                last_name=admin_last_name,
                role='ADMIN',
                is_active=True
            )
            session.add(admin_user)
            await session.commit()
            
            print(f"✅ Admin user created successfully!")
            print(f"   Email: {admin_email}")
            print(f"   ID: {admin_user.id}")
            print(f"   Role: {admin_user.role}")
            
        except Exception as e:
            await session.rollback()
            print(f"⚠️  Could not initialize admin: {str(e)}")
