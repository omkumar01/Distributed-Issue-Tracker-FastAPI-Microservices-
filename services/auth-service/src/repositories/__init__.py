"""User repository for data access."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
import uuid
import logging

from src.models import UserModel
from src.schemas import UserCreate

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for user data access."""
    
    def __init__(self, session: AsyncSession):
        """Initialize user repository.
        
        Args:
            session: AsyncSession for database operations
        """
        self.session = session
    
    async def create_user(self, user_create: UserCreate, password_hash: str) -> UserModel:
        """Create a new user.
        
        Args:
            user_create: User creation schema
            password_hash: Hashed password
            
        Returns:
            UserModel: Created user object
        """
        user = UserModel(
            id=str(uuid.uuid4()),
            email=user_create.email,
            username=user_create.username,
            password_hash=password_hash,
            first_name=user_create.first_name,
            last_name=user_create.last_name
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def get_user_by_id(self, user_id: str) -> UserModel | None:
        """Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            UserModel or None if not found
        """
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> UserModel | None:
        """Get user by email.
        
        Args:
            email: User email
            
        Returns:
            UserModel or None if not found
        """
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> UserModel | None:
        """Get user by username.
        
        Args:
            username: Username
            
        Returns:
            UserModel or None if not found
        """
        result = await self.session.execute(
            select(UserModel).where(UserModel.username == username)
        )
        return result.scalar_one_or_none()
    
    async def update_user(self, user_id: str, **kwargs) -> UserModel | None:
        """Update user.
        
        Args:
            user_id: User ID
            **kwargs: Fields to update
            
        Returns:
            Updated UserModel or None if not found
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        for key, value in kwargs.items():
            if hasattr(user, key) and key != "id":
                setattr(user, key, value)
        
        user.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def update_last_login(self, user_id: str) -> UserModel | None:
        """Update user last login timestamp.
        
        Args:
            user_id: User ID
            
        Returns:
            Updated UserModel or None
        """
        return await self.update_user(user_id, last_login=datetime.utcnow())
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user (soft delete by setting is_active to False).
        
        Args:
            user_id: User ID
            
        Returns:
            True if deleted, False if not found
        """
        user = await self.update_user(user_id, is_active=False)
        return user is not None
