"""Core authentication business logic"""
from datetime import datetime, timedelta, timezone
from typing import Tuple
import hashlib

from src.plugins.database import db
from src.utilities.security import security
from src.utilities.config_manager import config


class AuthCore:
    """Core authentication logic"""
    
    async def create_user(self, email: str, password: str, phone: str = None,
                         first_name: str = None, last_name: str = None):
        """Create a new user"""
        # Check if user already exists
        existing_user = await db.client.user.find_unique(where={'email': email})
        if existing_user:
            raise ValueError("User with this email already exists")
        
        if phone:
            existing_phone = await db.client.user.find_unique(where={'phone': phone})
            if existing_phone:
                raise ValueError("User with this phone number already exists")
        
        # Hash password
        password_hash = security.hash_password(password)
        
        # Create user
        user = await db.client.user.create(
            data={
                'email': email,
                'password_hash': password_hash,
                'phone': phone,
                'first_name': first_name,
                'last_name': last_name,
                'is_active': True
            }
        )
        
        return user
    
    async def authenticate_user(self, email: str, password: str):
        """Authenticate user with email and password"""
        user = await db.client.user.find_unique(where={'email': email})
        
        if not user:
            raise ValueError("Invalid credentials")
        
        if not security.verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")
        
        if not user.is_active:
            raise ValueError("User account is deactivated")
        
        return user
    
    async def create_tokens(self, user_id: str) -> Tuple[str, str]:
        """Create access and refresh tokens"""
        # Create access token
        access_token = security.create_access_token(
            data={"sub": user_id, "type": "access"}
        )
        
        # Create refresh token
        refresh_token_value = security.create_refresh_token(
            data={"sub": user_id, "type": "refresh"}
        )
        
        # Generate hash of refresh token for database storage
        token_hash = hashlib.sha256(refresh_token_value.encode()).hexdigest()
        
        # Store refresh token in database
        expires_at = datetime.now(timezone.utc) + timedelta(days=config.jwt_refresh_token_expire_days)
        await db.client.refreshtoken.create(
            data={
                'user_id': user_id,
                'token': refresh_token_value,
                'token_hash': token_hash,
                'expires_at': expires_at
            }
        )
        
        return access_token, refresh_token_value
    
    async def refresh_access_token(self, refresh_token: str) -> Tuple[str, str]:
        """Refresh access token using refresh token"""
        # Verify refresh token
        payload = security.decode_token(refresh_token)
        if not payload or payload.get('type') != 'refresh':
            raise ValueError("Invalid refresh token")
        
        # Generate hash of refresh token for lookup
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        
        # Check if refresh token exists and is valid
        token_record = await db.client.refreshtoken.find_unique(
            where={'token_hash': token_hash}
        )
        
        if not token_record:
            raise ValueError("Refresh token not found")
        
        if token_record.is_revoked:
            raise ValueError("Refresh token has been revoked")
        
        if token_record.expires_at < datetime.now(timezone.utc):
            raise ValueError("Refresh token has expired")
        
        # Get user
        user = await db.client.user.find_unique(where={'id': token_record.user_id})
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")
        
        # Revoke old refresh token
        await db.client.refreshtoken.update(
            where={'id': token_record.id},
            data={'is_revoked': True}
        )
        
        # Create new tokens
        return await self.create_tokens(user.id)
    
    async def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Change user password (authenticated)"""
        user = await db.client.user.find_unique(where={'id': user_id})
        if not user:
            raise ValueError("User not found")
        
        # Verify old password
        if not security.verify_password(old_password, user.password_hash):
            raise ValueError("Invalid old password")
        
        # Update password
        password_hash = security.hash_password(new_password)
        await db.client.user.update(
            where={'id': user_id},
            data={'password_hash': password_hash}
        )
        
        # Revoke all refresh tokens
        await db.client.refreshtoken.update_many(
            where={'user_id': user_id, 'is_revoked': False},
            data={'is_revoked': True}
        )
        
        return True
    
    async def logout(self, refresh_token: str) -> bool:
        """Logout user by revoking refresh token"""
        # Generate hash of refresh token for lookup
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        
        token_record = await db.client.refreshtoken.find_unique(
            where={'token_hash': token_hash}
        )
        
        if token_record:
            # Revoke the refresh token
            await db.client.refreshtoken.update(
                where={'id': token_record.id},
                data={'is_revoked': True}
            )
            
            # Set user's last logout time
            await db.client.user.update(
                where={'id': token_record.user_id},
                data={'last_logout_at': datetime.now(timezone.utc)}
            )
        
        return True


# Singleton instance
auth_core = AuthCore()
