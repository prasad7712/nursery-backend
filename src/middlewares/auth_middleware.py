"""Authentication middleware for JWT token verification"""
from datetime import datetime, timezone
from functools import wraps
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.utilities.security import security
from src.plugins.database import db


security_scheme = HTTPBearer()


class AuthMiddleware:
    """Authentication middleware for protecting routes"""
    
    @staticmethod
    async def get_current_user(credentials: HTTPAuthorizationCredentials):
        """Get current authenticated user from JWT token"""
        token = credentials.credentials
        
        # Decode token
        payload = security.decode_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify token type
        if payload.get('type') != 'access':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user ID from token
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        user = await db.client.user.find_unique(where={'id': user_id})
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated"
            )
        
        # Check if token was issued before user's last logout
        if user.last_logout_at:
            token_issued_at = payload.get('iat')
            if token_issued_at:
                # Convert token_issued_at from Unix timestamp to datetime
                token_issued_dt = datetime.fromtimestamp(token_issued_at, tz=timezone.utc)
                
                if token_issued_dt < user.last_logout_at:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token has been invalidated after logout",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
        
        return user
    
    @staticmethod
    async def get_current_active_user(credentials: HTTPAuthorizationCredentials):
        """Get current active user"""
        user = await AuthMiddleware.get_current_user(credentials)
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )
        
        return user
    
    @staticmethod
    async def get_current_admin(credentials: HTTPAuthorizationCredentials):
        """Get current admin user"""
        user = await AuthMiddleware.get_current_user(credentials)
        
        if user.role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        return user
    
    @staticmethod
    def require_role(*allowed_roles):
        """Decorator to require specific roles"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, credentials: HTTPAuthorizationCredentials = None, **kwargs):
                if not credentials:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication credentials missing"
                    )
                
                user = await AuthMiddleware.get_current_user(credentials)
                
                if user.role not in allowed_roles:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Required roles: {', '.join(allowed_roles)}"
                    )
                
                # Pass user to the endpoint
                kwargs['current_user'] = user
                return await func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    @staticmethod
    def extract_user_from_token(token: str) -> dict:
        """Extract user data from JWT token"""
        payload = security.decode_token(token)
        if not payload:
            return None
        
        return {
            'user_id': payload.get('sub'),
            'role': payload.get('role', 'CUSTOMER'),
            'type': payload.get('type')
        }

