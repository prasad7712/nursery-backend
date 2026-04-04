"""Admin account setup on application startup"""
import logging
from src.plugins.database import db
from src.utilities.security import security
from src.utilities.config_manager import config

logger = logging.getLogger(__name__)


async def setup_admin_account():
    """Create admin account from environment variables if it doesn't exist"""
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
        existing_admin = await db.client.user.find_unique(
            where={'email': admin_email}
        )
        
        if existing_admin:
            # Check if role is already ADMIN
            if hasattr(existing_admin, 'role') and existing_admin.role == 'ADMIN':
                logger.info(f"✅ Admin account already exists: {admin_email}")
            else:
                # Update existing user to ADMIN role
                await db.client.user.update(
                    where={'id': existing_admin.id},
                    data={'role': 'ADMIN'}
                )
                logger.info(f"✅ Existing user {admin_email} upgraded to ADMIN role")
            return
        
        # Hash password
        password_hash = security.hash_password(admin_password)
        
        # Create admin user
        admin_user = await db.client.user.create(
            data={
                'email': admin_email,
                'password_hash': password_hash,
                'first_name': admin_first_name,
                'last_name': admin_last_name,
                'role': 'ADMIN',
                'is_active': True
            }
        )
        
        logger.info(f"✅ Admin account created successfully")
        logger.info(f"   Email: {admin_email}")
        logger.info(f"   Name: {admin_first_name} {admin_last_name}")
        logger.info(f"   Role: ADMIN")
        
    except Exception as e:
        logger.error(f"❌ Failed to setup admin account: {str(e)}")
        raise
