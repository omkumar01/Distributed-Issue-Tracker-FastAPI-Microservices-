"""Login endpoint module."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from src.database import database
from src.services import AuthService
from src.schemas import UserLogin, TokenResponse
from shared.utils.exceptions import ApplicationException

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_db() -> AsyncSession:
    """Get database session."""
    async for session in database.get_session():
        yield session


@router.post("/login", response_model=TokenResponse)
async def login(
    user_login: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """User login endpoint.
    
    Handles credential-based login and returns JWT tokens.
    
    Args:
        user_login: Email and password credentials
        db: Database session
        
    Returns:
        TokenResponse: Access and refresh tokens
        
    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        auth_service = AuthService(db)
        return await auth_service.login(user_login)
    except ApplicationException as e:
        logger.warning(f"Login failed: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")
