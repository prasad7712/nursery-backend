"""Admin user management controller"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from src.middlewares.auth_middleware import security_scheme
from src.database import get_session
from src.services.admin_service import admin_service
from src.models.user import User
from src.data_contracts.admin_request_response import (
    AdminUserListResponse,
    AdminUserResponse,
    SuccessResponse,
    AdminUserStatusUpdateRequest,
    AdminUserRoleChangeRequest
)

router = APIRouter(prefix="/api/v1/admin/users", tags=["admin:users"])


@router.get("", response_model=AdminUserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    role: str = Query(None),
    search: str = Query(None),
    credentials=Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
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
        
        where_conditions = []
        if status:
            where_conditions.append(User.is_active == (status == 'active'))
        if role:
            where_conditions.append(User.role == role)
        if search:
            where_conditions.append(or_(
                User.email.contains(search),
                User.first_name.contains(search)
            ))
        
        # Build query
        stmt = select(User)
        if where_conditions:
            from sqlalchemy import and_
            stmt = stmt.where(and_(*where_conditions)) if len(where_conditions) > 1 else stmt.where(where_conditions[0])
        
        # Get total count
        count_stmt = select(func.count()).select_from(User)
        if where_conditions:
            from sqlalchemy import and_
            count_stmt = count_stmt.where(and_(*where_conditions)) if len(where_conditions) > 1 else count_stmt.where(where_conditions[0])
        count_result = await session.execute(count_stmt)
        total = count_result.scalar() or 0
        
        # Get paginated results
        stmt = stmt.order_by(User.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        result = await session.execute(stmt)
        users = result.scalars().all()
        
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
async def get_user(
    user_id: str,
    credentials=Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
):
    """
    Get user details
    
    Auth Required: Admin
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
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
    credentials=Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
):
    """
    Update user status (activate/suspend)
    
    Auth Required: Admin
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if request.is_active:
            await admin_service.activate_user(session, admin.id, user_id, request.reason)
            message = "User activated successfully"
        else:
            await admin_service.deactivate_user(session, admin.id, user_id, request.reason)
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
    credentials=Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
):
    """Change user role
    
    Auth Required: Admin (Super Admin only)
    
    Valid roles: admin, user
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        # Check if admin is super admin
        if admin.role != 'ADMIN':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can change user roles"
            )
        
        result = await admin_service.change_user_role(
            session,
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
    credentials=Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
):
    """
    Delete user (soft delete - just deactivate)
    
    Auth Required: Super Admin
    """
    try:
        from src.middlewares.auth_middleware import AuthMiddleware
        admin = await AuthMiddleware.get_current_admin(credentials)
        
        # Check if admin is super admin
        if admin.role != 'ADMIN':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can delete users"
            )
        
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Soft delete by deactivating
        await admin_service.deactivate_user(session, admin.id, user_id, reason)
        
        return SuccessResponse(message="User deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}"
        )
