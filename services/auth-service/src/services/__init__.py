"""Authentication service with business logic."""

from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import logging
from typing import Optional

from src.repositories import UserRepository
from src.schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from src.core.security import security_handler
from src.core.jwt import jwt_handler
from shared.utils.exceptions import AuthenticationException, ValidationException, ResourceNotFoundException

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize auth service.
        
        Args:
            session: AsyncSession for database operations
        """
        self.session = session
        self.user_repo = UserRepository(session)
    
    async def register(self, user_create: UserCreate) -> UserResponse:
        """Register a new user.
        
        Args:
            user_create: User creation data
            
        Returns:
            UserResponse: Created user
            
        Raises:
            ValidationException: If user already exists or password is weak
        """
        # Validate password strength
        is_valid, error_msg = security_handler.validate_password_strength(user_create.password)
        if not is_valid:
            raise ValidationException(error_msg)
        
        # Check if email already exists
        existing_email = await self.user_repo.get_user_by_email(user_create.email)
        if existing_email:
            raise ValidationException("Email already registered")
        
        # Check if username already exists
        existing_username = await self.user_repo.get_user_by_username(user_create.username)
        if existing_username:
            raise ValidationException("Username already taken")
        
        # Hash password and create user
        password_hash = security_handler.hash_password(user_create.password)
        user = await self.user_repo.create_user(user_create, password_hash)
        
        logger.info(f"User registered: {user.id}")
        return UserResponse.from_orm(user)
    
    async def login(self, user_login: UserLogin) -> TokenResponse:
        """Login user and return tokens.
        
        Args:
            user_login: Login credentials
            
        Returns:
            TokenResponse: Access and refresh tokens
            
        Raises:
            AuthenticationException: If credentials are invalid
        """
        # Find user by email
        user = await self.user_repo.get_user_by_email(user_login.email)
        if not user:
            raise AuthenticationException("Invalid email or password")
        
        # Check if user is active
        if not user.is_active:
            raise AuthenticationException("User account is disabled")
        
        # Verify password
        if not security_handler.verify_password(user_login.password, user.password_hash):
            raise AuthenticationException("Invalid email or password")
        
        # Update last login
        await self.user_repo.update_last_login(user.id)
        
        # Create tokens
        access_token = jwt_handler.create_access_token(
            data={"sub": user.id, "email": user.email}
        )
        refresh_token = jwt_handler.create_refresh_token(
            data={"sub": user.id, "email": user.email}
        )
        
        logger.info(f"User logged in: {user.id}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=1800  # 30 minutes in seconds
        )
    
    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            TokenResponse: New access and refresh tokens
            
        Raises:
            AuthenticationException: If refresh token is invalid
        """
        try:
            payload = jwt_handler.verify_refresh_token(refresh_token)
            user_id = payload.get("sub")
            
            # Get user to verify they still exist and are active
            user = await self.user_repo.get_user_by_id(user_id)
            if not user or not user.is_active:
                raise AuthenticationException("User not found or inactive")
            
            # Create new tokens
            access_token = jwt_handler.create_access_token(
                data={"sub": user.id, "email": user.email}
            )
            new_refresh_token = jwt_handler.create_refresh_token(
                data={"sub": user.id, "email": user.email}
            )
            
            logger.info(f"Token refreshed for user: {user.id}")
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=new_refresh_token,
                expires_in=1800
            )
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise AuthenticationException("Invalid or expired refresh token")
    
    async def get_current_user(self, token: str) -> UserResponse:
        """Get current user from access token.
        
        Args:
            token: Access token
            
        Returns:
            UserResponse: Current user
            
        Raises:
            AuthenticationException: If token is invalid
        """
        try:
            payload = jwt_handler.verify_access_token(token)
            user_id = payload.get("sub")
            
            user = await self.user_repo.get_user_by_id(user_id)
            if not user:
                raise ResourceNotFoundException("User", user_id)
            
            return UserResponse.from_orm(user)
        except Exception as e:
            logger.error(f"Failed to get current user: {e}")
            raise AuthenticationException("Invalid or expired token")
    
    async def change_password(self, user_id: str, old_password: str, new_password: str):
        """Change user password.
        
        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password
            
        Raises:
            AuthenticationException: If old password is wrong
            ValidationException: If new password is weak
        """
        # Validate new password
        is_valid, error_msg = security_handler.validate_password_strength(new_password)
        if not is_valid:
            raise ValidationException(error_msg)
        
        # Get user
        user = await self.user_repo.get_user_by_id(user_id)
        if not user:
            raise ResourceNotFoundException("User", user_id)
        
        # Verify old password
        if not security_handler.verify_password(old_password, user.password_hash):
            raise AuthenticationException("Invalid current password")
        
        # Hash and update new password
        new_password_hash = security_handler.hash_password(new_password)
        await self.user_repo.update_user(user_id, password_hash=new_password_hash)
        
        logger.info(f"Password changed for user: {user_id}")
    
    async def verify_email(self, user_id: str):
        """Mark user email as verified.
        
        Args:
            user_id: User ID
        """
        user = await self.user_repo.get_user_by_id(user_id)
        if not user:
            raise ResourceNotFoundException("User", user_id)
        
        await self.user_repo.update_user(user_id, is_verified=True)
        logger.info(f"Email verified for user: {user_id}")
