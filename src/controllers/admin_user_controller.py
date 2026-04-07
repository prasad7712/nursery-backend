"""Admin user management controller"""
from fastapi import APIRouter, Depends, HTTPException, status, Query

from src.middlewares.auth_middleware import security_scheme
from src.plugins.database import db
from src.services.admin_service import admin_service
from src.data_contracts.admin_request_response import (
    AdminUserStatusUpdateRequest,
    AdminUserRoleChangeRequest,
    AdminUserResponse,
    AdminUserListResponse,
    SuccessResponse
)

router = APIRouter(prefix="/api/v1/admin/users", tags=["admin:users"])


@router.get("", response_model=AdminUserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    role: str = Query(None),
    search: str = Query(None),
    credentials=Depends(security_scheme)
):
    """
    List all users with filters
    
    Auth Required: Admin
    
    Query params:
        - status: Filter by user status (active, inactive)
        - role: Filter by role (admin, user)
        - search: Search by email or name
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        where = {}
        if status:
            where['is_active'] = status == 'active'
        if role:
            where['role'] = role
        if search:
            where['OR'] = [
                {'email': {'contains': search}},
                {'name': {'contains': search}}
            ]
        
        total = await db.client.user.count(where=where)
        
        users = await db.client.user.find_many(
            where=where,
            skip=(page - 1) * per_page,
            take=per_page
        )
        
        # Sort by created_at descending
        users = sorted(users, key=lambda x: x.created_at, reverse=True) if users else []
        
        user_list = [AdminUserResponse.model_validate(u).dict() for u in users]
        
        return AdminUserListResponse(
            users=user_list,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=(total + per_page - 1) // per_page
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching users: {str(e)}"
        )


@router.get("/{user_id}", response_model=AdminUserResponse)
async def get_user(user_id: str, credentials=Depends(security_scheme)):
    """
    Get user details
    
    Auth Required: Admin
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        user = await db.client.user.find_unique(where={'id': user_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return AdminUserResponse.model_validate(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{user_id}/status", response_model=SuccessResponse)
async def update_user_status(
    user_id: str,
    request: AdminUserStatusUpdateRequest,
    credentials=Depends(security_scheme)
):
    """
    Update user status (activate/suspend)
    
    Auth Required: Admin
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        user = await db.client.user.find_unique(where={'id': user_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if request.is_active:
            await admin_service.activate_user(admin.id, user_id, request.reason)
            message = "User activated successfully"
        else:
            await admin_service.deactivate_user(admin.id, user_id, request.reason)
            message = "User deactivated successfully"
        
        return SuccessResponse(message=message)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating user status: {str(e)}"
        )


@router.put("/{user_id}/role", response_model=SuccessResponse)
async def change_user_role(
    user_id: str,
    request: AdminUserRoleChangeRequest,
    credentials=Depends(security_scheme)
):
    """
    Change user role
    
    Auth Required: Admin (Super Admin only)
    
    Valid roles: admin, user
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        # Check if admin is super admin
        if admin.role != 'super_admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only super admins can change user roles"
            )
        
        result = await admin_service.change_user_role(
            admin.id,
            user_id,
            request.new_role,
            request.reason
        )
        
        return SuccessResponse(message=f"User role changed to {request.new_role}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error changing user role: {str(e)}"
        )


@router.delete("/{user_id}", response_model=SuccessResponse)
async def delete_user(
    user_id: str,
    reason: str = Query(...),
    credentials=Depends(security_scheme)
):
    """
    Delete user (soft delete - just deactivate)
    
    Auth Required: Super Admin
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        # Check if admin is super admin
        if admin.role != 'super_admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only super admins can delete users"
            )
        
        user = await db.client.user.find_unique(where={'id': user_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Soft delete by deactivating
        await admin_service.deactivate_user(admin.id, user_id, reason)
        
        return SuccessResponse(message="User deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}"
        )
