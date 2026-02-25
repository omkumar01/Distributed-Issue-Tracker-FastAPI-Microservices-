"""Token refresh endpoint module."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from src.database import database
from src.services import AuthService
from src.schemas import RefreshTokenRequest, TokenResponse
from shared.utils.exceptions import ApplicationException

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_db() -> AsyncSession:
    """Get database session."""
    async for session in database.get_session():
        yield session


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token endpoint.
    
    Exchanges a valid refresh token for a new access token.
    
    Args:
        request: Refresh token request with refresh_token
        db: Database session
        
    Returns:
        TokenResponse: New access and refresh tokens
        
    Raises:
        HTTPException: If refresh token is invalid or expired
    """
    try:
        auth_service = AuthService(db)
        return await auth_service.refresh_access_token(request.refresh_token)
    except ApplicationException as e:
        logger.warning(f"Token refresh failed: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(status_code=401, detail="Invalid refresh token")
