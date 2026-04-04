"""Admin setup controller for creating initial admin account"""
from fastapi import APIRouter, HTTPException, status, Header
from typing import Optional

from src.data_contracts.api_request_response import (
    RegisterRequest,
    RegisterApiResponse
)
from src.services.auth_service import auth_service
from src.utilities.config_manager import config

router = APIRouter(prefix="/api/v1/admin", tags=["Admin Setup"])


@router.post("/setup", response_model=RegisterApiResponse, status_code=status.HTTP_201_CREATED)
async def setup_admin(
    request: RegisterRequest,
    setup_key: Optional[str] = Header(None)
):
    """
    Create initial admin account (requires ADMIN_SETUP_KEY)
    
    This endpoint is only available before any admin exists.
    
    Headers:
        - setup-key: Must match ADMIN_SETUP_KEY environment variable
    
    Body:
        - email: Admin email
        - password: Admin password
        - first_name: Admin first name
        - last_name: Admin last name
    """
    # Verify setup key
    admin_setup_key = config.get('admin_setup_key', None)
    if not admin_setup_key or setup_key != admin_setup_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing setup key"
        )
    
    try:
        # Create user
        user = await auth_service.register_user(request)
        
        # Update user role to ADMIN
        from src.plugins.database import db
        await db.client.user.update(
            where={'id': user['id']},
            data={'role': 'ADMIN'}
        )
        
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create admin: {str(e)}"
        )
