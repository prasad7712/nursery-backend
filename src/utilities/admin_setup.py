"""Admin account setup on application startup"""
import logging
from sqlalchemy import select

from src.database import async_session_maker
from src.models.user import User
from src.utilities.security import security
from src.utilities.config_manager import config

logger = logging.getLogger(__name__)


async def setup_admin_account():
    """Create admin account from environment variables if it doesn't exist"""
    async with async_session_maker() as session:
        try:
            # Get admin credentials from config
            admin_email = config.get('admin_email')
            admin_password = config.get('admin_password')
            admin_first_name = config.get('admin_first_name')
            admin_last_name = config.get('admin_last_name')
            
            # Check if admin credentials are configured
            if not admin_email or not admin_password:
                logger.warning("Admin credentials not configured in environment variables")
                return
            
            # Check if admin already exists
            stmt = select(User).where(User.email == admin_email)
            result = await session.execute(stmt)
            existing_admin = result.scalar_one_or_none()
            
            if existing_admin:
                # Check if role is already ADMIN
                if existing_admin.role == 'ADMIN':
                    logger.info(f"✅ Admin account already exists: {admin_email}")
                else:
                    # Update existing user to ADMIN role
                    existing_admin.role = 'ADMIN'
                    await session.commit()
                    logger.info(f"✅ Existing user {admin_email} upgraded to ADMIN role")
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
            
            logger.info(f"✅ Admin account created successfully")
            logger.info(f"   Email: {admin_email}")
            logger.info(f"   Name: {admin_first_name} {admin_last_name}")
            logger.info(f"   Role: ADMIN")
            
        except Exception as e:
            await session.rollback()
            logger.error(f"❌ Failed to setup admin account: {str(e)}")
            raise
