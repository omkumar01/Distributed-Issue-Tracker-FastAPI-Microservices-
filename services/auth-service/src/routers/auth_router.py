"""Auth API routers."""

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging

from src.database import database
from src.services import AuthService
from src.schemas import (
    UserCreate, UserLogin, UserResponse, TokenResponse,
    RefreshTokenRequest, PasswordChangeRequest, ErrorResponse
)
from shared.utils.exceptions import ApplicationException, AuthenticationException

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_db() -> AsyncSession:
    """Get database session dependency.
    
    Yields:
        AsyncSession: Database session
    """
    async for session in database.get_session():
        yield session


async def get_current_user(
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Get current user from authorization header.
    
    Args:
        authorization: Authorization header
        db: Database session
        
    Returns:
        UserResponse: Current user
        
    Raises:
        HTTPException: If token is missing or invalid
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    try:
        # Extract token from "Bearer <token>" format
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authorization header format")
        
        token = parts[1]
        auth_service = AuthService(db)
        return await auth_service.get_current_user(token)
    except ApplicationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Failed to get current user: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/register", response_model=UserResponse)
async def register(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user.
    
    Args:
        user_create: User registration data
        db: Database session
        
    Returns:
        UserResponse: Created user
    """
    try:
        auth_service = AuthService(db)
        return await auth_service.register(user_create)
    except ApplicationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/login", response_model=TokenResponse)
async def login(
    user_login: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Login user and return tokens.
    
    Args:
        user_login: Login credentials
        db: Database session
        
    Returns:
        TokenResponse: Access and refresh tokens
    """
    try:
        auth_service = AuthService(db)
        return await auth_service.login(user_login)
    except ApplicationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token.
    
    Args:
        request: Refresh token request
        db: Database session
        
    Returns:
        TokenResponse: New tokens
    """
    try:
        auth_service = AuthService(db)
        return await auth_service.refresh_access_token(request.refresh_token)
    except ApplicationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/logout")
async def logout(
    current_user: UserResponse = Depends(get_current_user)
):
    """Logout user (token invalidation done on client side).
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        dict: Logout confirmation
    """
    logger.info(f"User logged out: {current_user.id}")
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: UserResponse = Depends(get_current_user)
):
    """Get current user profile.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserResponse: Current user
    """
    return current_user


@router.post("/change-password")
async def change_password(
    request: PasswordChangeRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Change user password.
    
    Args:
        request: Password change request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: Success message
    """
    try:
        if request.new_password != request.confirm_password:
            raise HTTPException(status_code=422, detail="Passwords do not match")
        
        auth_service = AuthService(db)
        await auth_service.change_password(
            current_user.id,
            request.old_password,
            request.new_password
        )
        return {"message": "Password changed successfully"}
    except ApplicationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/verify-email")
async def verify_email(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Verify user email.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: Success message
    """
    try:
        auth_service = AuthService(db)
        await auth_service.verify_email(current_user.id)
        return {"message": "Email verified successfully"}
    except ApplicationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
