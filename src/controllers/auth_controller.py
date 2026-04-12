"""Authentication API Controller"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.data_contracts.api_request_response import (
    RegisterRequest,
    LoginRequest,
    RefreshTokenRequest,
    ChangePasswordRequest,
    RegisterApiResponse,
    LoginApiResponse,
    GetMeApiResponse,
    TokenResponse,
    MessageResponse,
    RateLimitResponse,
    UserResponse
)
from src.services.auth_service import auth_service
from src.middlewares.auth_middleware import AuthMiddleware, security_scheme
from src.utilities.rate_limiter import rate_limiter
from src.database import get_session


router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/register", response_model=RegisterApiResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, req: Request, session: AsyncSession = Depends(get_session)):
    """
    Register a new user
    
    - **email**: User email address (unique)
    - **password**: Strong password (min 8 chars, uppercase, lowercase, digit)
    - **firstName**: User's first name
    - **lastName**: User's last name
    """
    # Debug: Print received password length
    print(f"DEBUG: Password received: '{request.password}' (length: {len(request.password)} bytes)")
    
    # Rate limiting
    client_ip = req.client.host
    is_limited, limit_info = await rate_limiter.is_rate_limited(f"register:{client_ip}")
    if is_limited:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=RateLimitResponse(**limit_info).model_dump()
        )
    
    try:
        result = await auth_service.register_user(session, request)
        # Extract tokens from result
        access_token = result.get('access_token', '')
        refresh_token = result.get('refresh_token', '')
        return RegisterApiResponse(
            id=result['user'].id,
            email=result['user'].email,
            first_name=result['user'].first_name,
            last_name=result['user'].last_name,
            role=result['user'].role,
            token=access_token,
            refresh_token=refresh_token
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=LoginApiResponse)
async def login(request: LoginRequest, req: Request, session: AsyncSession = Depends(get_session)):
    """
    Login user and get access token
    
    - **email**: User email address
    - **password**: User password
    
    Returns JWT access token for authenticated requests
    """
    # Rate limiting
    is_limited, limit_info = await rate_limiter.is_rate_limited(
        f"login:{request.email}",
        max_requests=10,
        window_seconds=300  # 10 attempts per 5 minutes
    )
    if is_limited:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=RateLimitResponse(**limit_info).model_dump()
        )
    
    try:
        result = await auth_service.login_user(session, request)
        # result is LoginResponse with user and tokens
        return LoginApiResponse(
            id=result.user.id,
            email=result.user.email,
            first_name=result.user.first_name,
            last_name=result.user.last_name,
            role=result.user.role,
            token=result.tokens.access_token,
            refresh_token=result.tokens.refresh_token
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest, session: AsyncSession = Depends(get_session)):
    """
    Refresh access token using refresh token
    
    - **refresh_token**: Valid refresh token
    
    Returns new access token and refresh token
    """
    try:
        result = await auth_service.refresh_token(session, request.refresh_token)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    request: ChangePasswordRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
):
    """
    Change password for authenticated user
    
    - **old_password**: Current password
    - **new_password**: New password
    
    Requires authentication token
    """
    try:
        user = await AuthMiddleware.get_current_user(credentials)
        result = await auth_service.change_user_password(
            session,
            user.id,
            request.old_password,
            request.new_password
        )
        return MessageResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password change failed: {str(e)}"
        )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    request: RefreshTokenRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    session: AsyncSession = Depends(get_session)
):
    """
    Logout user and revoke refresh token
    
    - **refresh_token**: Refresh token to revoke
    
    Requires authentication token
    """
    try:
        user = await AuthMiddleware.get_current_user(credentials)
        result = await auth_service.logout_user(session, request.refresh_token)
        return MessageResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )


@router.get("/me", response_model=GetMeApiResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme)
):
    """
    Get current authenticated user information
    
    Requires authentication token in Authorization header
    """
    try:
        user = await AuthMiddleware.get_current_user(credentials)
        return GetMeApiResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
