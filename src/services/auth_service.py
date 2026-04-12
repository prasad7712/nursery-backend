"""Authentication service layer"""
from typing import Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth_core import auth_core
from src.data_contracts.api_request_response import (
    RegisterRequest,
    LoginRequest,
    UserResponse,
    LoginResponse,
    TokenResponse
)
from src.utilities.config_manager import config


class AuthService:
    """Authentication service handling business operations"""
    
    async def register_user(self, session: AsyncSession, request: RegisterRequest) -> Dict[str, Any]:
        """Register a new user"""
        user = await auth_core.create_user(
            session=session,
            email=request.email,
            password=request.password,
            phone=request.phone,
            first_name=request.first_name,
            last_name=request.last_name
        )
        
        # Create tokens for immediate login after registration
        access_token, refresh_token = await auth_core.create_tokens(session, user.id)
        
        return {
            "message": "User registered successfully",
            "user": UserResponse.model_validate(user),
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    
    async def login_user(self, session: AsyncSession, request: LoginRequest) -> LoginResponse:
        """Login user and return tokens"""
        # Authenticate user
        user = await auth_core.authenticate_user(session, request.email, request.password)
        
        # Create tokens
        access_token, refresh_token = await auth_core.create_tokens(session, user.id)
        
        # Return response
        return LoginResponse(
            user=UserResponse.model_validate(user),
            tokens=TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=config.jwt_access_token_expire_minutes * 60
            )
        )
    
    async def refresh_token(self, session: AsyncSession, refresh_token: str) -> TokenResponse:
        """Refresh access token"""
        access_token, new_refresh_token = await auth_core.refresh_access_token(session, refresh_token)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=config.jwt_access_token_expire_minutes * 60
        )
    
    async def change_user_password(self, session: AsyncSession, user_id: str, old_password: str, 
                                   new_password: str) -> Dict[str, str]:
        """Change password for authenticated user"""
        await auth_core.change_password(session, user_id, old_password, new_password)
        return {"message": "Password changed successfully"}
    
    async def logout_user(self, session: AsyncSession, refresh_token: str) -> Dict[str, str]:
        """Logout user"""
        await auth_core.logout(session, refresh_token)
        return {"message": "Logged out successfully"}


# Singleton instance
auth_service = AuthService()
