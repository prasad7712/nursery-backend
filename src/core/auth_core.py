"""Core authentication business logic"""
from datetime import datetime, timedelta, timezone
from typing import Tuple
import hashlib
import uuid

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User, RefreshToken
from src.utilities.security import security
from src.utilities.config_manager import config


class AuthCore:
    """Core authentication logic"""
    
    async def create_user(self, session: AsyncSession, email: str, password: str, phone: str = None,
                         first_name: str = None, last_name: str = None):
        """Create a new user"""
        # Check if user already exists by email
        result = await session.execute(select(User).where(User.email == email))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise ValueError("User with this email already exists")
        
        if phone:
            result = await session.execute(select(User).where(User.phone == phone))
            existing_phone = result.scalar_one_or_none()
            if existing_phone:
                raise ValueError("User with this phone number already exists")
        
        # Hash password
        password_hash = security.hash_password(password)
        
        # Create user (SQLAlchemy will auto-generate UUID and set defaults)
        user = User(
            email=email,
            password_hash=password_hash,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            is_active=True
        )
        
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
    
    async def authenticate_user(self, session: AsyncSession, email: str, password: str):
        """Authenticate user with email and password"""
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError("Invalid credentials")
        
        if not security.verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")
        
        if not user.is_active:
            raise ValueError("User account is deactivated")
        
        return user
    
    async def create_tokens(self, session: AsyncSession, user_id: str) -> Tuple[str, str]:
        """Create access and refresh tokens with user role"""
        # Get user to include role in token
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError("User not found")
        
        # Get user role (default to CUSTOMER if not set)
        # user.role is stored as string in DB, so check if it has .value attr (enum) or use directly (string)
        user_role = user.role.value if hasattr(user.role, 'value') else (user.role or "CUSTOMER")
        
        # Create access token with role
        access_token = security.create_access_token(
            data={
                "sub": user_id,
                "type": "access",
                "role": user_role
            }
        )
        
        # Create refresh token
        refresh_token_value = security.create_refresh_token(
            data={"sub": user_id, "type": "refresh"}
        )
        
        # Generate hash of refresh token for database storage
        token_hash = hashlib.sha256(refresh_token_value.encode()).hexdigest()
        
        # Store refresh token in database
        expires_at = datetime.now(timezone.utc) + timedelta(days=config.jwt_refresh_token_expire_days)
        refresh_token = RefreshToken(
            user_id=user_id,
            token=refresh_token_value,
            token_hash=token_hash,
            expires_at=expires_at
        )
        
        session.add(refresh_token)
        await session.commit()
        
        return access_token, refresh_token_value
    
    async def refresh_access_token(self, session: AsyncSession, refresh_token: str) -> Tuple[str, str]:
        """Refresh access token using refresh token"""
        # Verify refresh token
        payload = security.decode_token(refresh_token)
        if not payload or payload.get('type') != 'refresh':
            raise ValueError("Invalid refresh token")
        
        # Generate hash of refresh token for lookup
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        
        # Check if refresh token exists and is valid
        result = await session.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
        token_record = result.scalar_one_or_none()
        
        if not token_record:
            raise ValueError("Refresh token not found")
        
        if token_record.is_revoked:
            raise ValueError("Refresh token has been revoked")
        
        if token_record.expires_at < datetime.now(timezone.utc):
            raise ValueError("Refresh token has expired")
        
        # Get user
        result = await session.execute(select(User).where(User.id == token_record.user_id))
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")
        
        # Revoke old refresh token
        token_record.is_revoked = True
        session.add(token_record)
        await session.commit()
        
        # Create new tokens
        return await self.create_tokens(session, user.id)
    
    async def change_password(self, session: AsyncSession, user_id: str, old_password: str, new_password: str) -> bool:
        """Change user password (authenticated)"""
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError("User not found")
        
        # Verify old password
        if not security.verify_password(old_password, user.password_hash):
            raise ValueError("Invalid old password")
        
        # Update password
        password_hash = security.hash_password(new_password)
        user.password_hash = password_hash
        
        session.add(user)
        await session.commit()
        
        # Revoke all refresh tokens
        result = await session.execute(
            select(RefreshToken).where(
                and_(
                    RefreshToken.user_id == user_id,
                    RefreshToken.is_revoked == False
                )
            )
        )
        tokens = result.scalars().all()
        
        for token in tokens:
            token.is_revoked = True
            session.add(token)
        
        await session.commit()
        return True
    
    async def logout(self, session: AsyncSession, refresh_token: str) -> bool:
        """Logout user by revoking refresh token"""
        # Generate hash of refresh token for lookup
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        
        result = await session.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
        token_record = result.scalar_one_or_none()
        
        if token_record:
            # Revoke the refresh token
            token_record.is_revoked = True
            session.add(token_record)
            
            # Set user's last logout time
            result = await session.execute(select(User).where(User.id == token_record.user_id))
            user = result.scalar_one_or_none()
            
            if user:
                user.last_logout_at = datetime.now(timezone.utc)
                session.add(user)
            
            await session.commit()
        
        return True


# Singleton instance
auth_core = AuthCore()
