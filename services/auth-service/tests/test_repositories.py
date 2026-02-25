"""Auth Service - UserRepository tests with mocked AsyncSession."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime

from src.repositories import UserRepository
from shared.utils.exceptions import DatabaseException


# ─── Create User ───


@pytest.mark.asyncio
class TestUserRepositoryCreate:
    """Test UserRepository.create_user."""

    async def test_create_success(self, mock_session, sample_user):
        repo = UserRepository(mock_session)

        from src.schemas import UserCreate
        user_data = UserCreate(
            email="new@example.com", username="newuser",
            password="StrongP@ss1", first_name="New", last_name="User",
        )
        password_hash = "$2b$12$hashedvalue"

        result = await repo.create_user(user_data, password_hash)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once()

    async def test_create_rollback_on_error(self, mock_session):
        mock_session.commit.side_effect = Exception("Unique constraint")
        repo = UserRepository(mock_session)

        from src.schemas import UserCreate
        user_data = UserCreate(
            email="dup@example.com", username="dupuser",
            password="StrongP@ss1", first_name="D", last_name="U",
        )

        with pytest.raises(DatabaseException):
            await repo.create_user(user_data, "hash")
        mock_session.rollback.assert_awaited_once()


# ─── Get User ───


@pytest.mark.asyncio
class TestUserRepositoryGet:
    """Test UserRepository get methods."""

    async def test_get_by_id(self, mock_session, sample_user):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_session.execute.return_value = mock_result

        repo = UserRepository(mock_session)
        result = await repo.get_user_by_id(sample_user.id)

        assert result == sample_user

    async def test_get_by_id_not_found(self, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        repo = UserRepository(mock_session)
        result = await repo.get_user_by_id(str(uuid4()))

        assert result is None

    async def test_get_by_email(self, mock_session, sample_user):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_session.execute.return_value = mock_result

        repo = UserRepository(mock_session)
        result = await repo.get_user_by_email("test@example.com")

        assert result == sample_user

    async def test_get_by_email_not_found(self, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        repo = UserRepository(mock_session)
        result = await repo.get_user_by_email("nonexistent@example.com")

        assert result is None

    async def test_get_by_username(self, mock_session, sample_user):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_session.execute.return_value = mock_result

        repo = UserRepository(mock_session)
        result = await repo.get_user_by_username("testuser")

        assert result == sample_user


# ─── Update User ───


@pytest.mark.asyncio
class TestUserRepositoryUpdate:
    """Test UserRepository update methods."""

    async def test_update_last_login(self, mock_session, sample_user):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_session.execute.return_value = mock_result

        repo = UserRepository(mock_session)
        await repo.update_last_login(sample_user.id)

        mock_session.commit.assert_awaited_once()

    async def test_update_user(self, mock_session, sample_user):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_session.execute.return_value = mock_result

        repo = UserRepository(mock_session)
        result = await repo.update_user(sample_user.id, {"first_name": "Updated"})

        mock_session.commit.assert_awaited_once()

    async def test_update_nonexistent_user(self, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        repo = UserRepository(mock_session)
        result = await repo.update_user(str(uuid4()), {"first_name": "X"})

        assert result is None


# ─── Delete User ───


@pytest.mark.asyncio
class TestUserRepositoryDelete:
    """Test UserRepository.delete_user (soft delete)."""

    async def test_soft_delete(self, mock_session, sample_user):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_session.execute.return_value = mock_result

        repo = UserRepository(mock_session)
        result = await repo.delete_user(sample_user.id)

        mock_session.commit.assert_awaited_once()
        assert sample_user.is_active is False

    async def test_delete_not_found(self, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        repo = UserRepository(mock_session)
        result = await repo.delete_user(str(uuid4()))

        assert result is None
