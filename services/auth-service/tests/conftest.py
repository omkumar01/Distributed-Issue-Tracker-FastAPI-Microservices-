"""Pytest configuration and fixtures for auth-service tests."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_session():
    """Create a mock async database session."""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()
    session.close = AsyncMock()
    session.add = MagicMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def sample_user():
    """Return a mock user model object."""
    user = MagicMock()
    user.id = str(uuid4())
    user.email = "test@example.com"
    user.username = "testuser"
    user.password_hash = "$2b$12$fakehashfortest"
    user.first_name = "Test"
    user.last_name = "User"
    user.is_active = True
    user.is_verified = False
    user.created_at = datetime.utcnow()
    user.updated_at = datetime.utcnow()
    user.last_login = None
    return user


@pytest.fixture
def mock_user_repo():
    """Create a mock UserRepository."""
    repo = AsyncMock()
    repo.create_user = AsyncMock()
    repo.get_user_by_id = AsyncMock()
    repo.get_user_by_email = AsyncMock()
    repo.get_user_by_username = AsyncMock()
    repo.update_user = AsyncMock()
    repo.update_last_login = AsyncMock()
    repo.delete_user = AsyncMock()
    return repo
