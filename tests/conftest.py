"""
Development testing configuration and fixtures.
"""

import pytest
import asyncio
from typing import Generator


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_client():
    """Async HTTP client for testing."""
    from httpx import AsyncClient
    from src.main import app
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_db_session():
    """Mock database session."""
    # Return mock session for testing
    pass


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    # Return mock Redis for testing
    pass
