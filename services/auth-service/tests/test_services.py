"""Auth Service - AuthService tests with mocked dependencies."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime

from src.services import AuthService
from src.schemas import UserCreate, UserLogin, PasswordChangeRequest
from shared.utils.exceptions import (
    ValidationException, AuthenticationException, ResourceNotFoundException,
)


@pytest.fixture
def auth_service(mock_user_repo):
    """Create AuthService with mocked repository."""
    return AuthService(mock_user_repo)


# ─── Registration ───


@pytest.mark.asyncio
class TestAuthServiceRegister:
    """Test AuthService.register."""

    @patch("src.services.security_handler")
    async def test_register_success(self, mock_security, auth_service, mock_user_repo, sample_user):
        mock_security.validate_password_strength.return_value = (True, None)
        mock_security.hash_password.return_value = "$2b$12$hashed"
        mock_user_repo.get_user_by_email.return_value = None
        mock_user_repo.get_user_by_username.return_value = None
        mock_user_repo.create_user.return_value = sample_user

        user_data = UserCreate(
            email="new@example.com", username="newuser",
            password="StrongP@ss1", first_name="N", last_name="U",
        )
        result = await auth_service.register(user_data)

        assert result is not None
        mock_user_repo.create_user.assert_awaited_once()

    @patch("src.services.security_handler")
    async def test_register_weak_password(self, mock_security, auth_service):
        mock_security.validate_password_strength.return_value = (False, "Too weak")

        with pytest.raises(ValidationException):
            await auth_service.register(UserCreate(
                email="a@b.com", username="usr",
                password="weak", first_name="A", last_name="B",
            ))

    @patch("src.services.security_handler")
    async def test_register_duplicate_email(self, mock_security, auth_service, mock_user_repo, sample_user):
        mock_security.validate_password_strength.return_value = (True, None)
        mock_user_repo.get_user_by_email.return_value = sample_user  # Already exists

        with pytest.raises(ValidationException, match="[Ee]mail"):
            await auth_service.register(UserCreate(
                email="test@example.com", username="newuser",
                password="StrongP@ss1", first_name="A", last_name="B",
            ))

    @patch("src.services.security_handler")
    async def test_register_duplicate_username(self, mock_security, auth_service, mock_user_repo, sample_user):
        mock_security.validate_password_strength.return_value = (True, None)
        mock_user_repo.get_user_by_email.return_value = None
        mock_user_repo.get_user_by_username.return_value = sample_user  # Already exists

        with pytest.raises(ValidationException, match="[Uu]sername"):
            await auth_service.register(UserCreate(
                email="unique@example.com", username="testuser",
                password="StrongP@ss1", first_name="A", last_name="B",
            ))


# ─── Login ───


@pytest.mark.asyncio
class TestAuthServiceLogin:
    """Test AuthService.login."""

    @patch("src.services.jwt_handler")
    @patch("src.services.security_handler")
    async def test_login_success(self, mock_security, mock_jwt, auth_service, mock_user_repo, sample_user):
        mock_user_repo.get_user_by_email.return_value = sample_user
        mock_security.verify_password.return_value = True
        mock_jwt.create_access_token.return_value = "access-token"
        mock_jwt.create_refresh_token.return_value = "refresh-token"

        login_data = UserLogin(email="test@example.com", password="password")
        result = await auth_service.login(login_data)

        assert result.access_token == "access-token"
        assert result.refresh_token == "refresh-token"
        mock_user_repo.update_last_login.assert_awaited_once()

    @patch("src.services.security_handler")
    async def test_login_user_not_found(self, mock_security, auth_service, mock_user_repo):
        mock_user_repo.get_user_by_email.return_value = None

        with pytest.raises(AuthenticationException):
            await auth_service.login(UserLogin(email="no@exist.com", password="pass"))

    @patch("src.services.security_handler")
    async def test_login_wrong_password(self, mock_security, auth_service, mock_user_repo, sample_user):
        mock_user_repo.get_user_by_email.return_value = sample_user
        mock_security.verify_password.return_value = False

        with pytest.raises(AuthenticationException):
            await auth_service.login(UserLogin(email="test@example.com", password="wrong"))

    @patch("src.services.security_handler")
    async def test_login_inactive_user(self, mock_security, auth_service, mock_user_repo, sample_user):
        sample_user.is_active = False
        mock_user_repo.get_user_by_email.return_value = sample_user

        with pytest.raises(AuthenticationException):
            await auth_service.login(UserLogin(email="test@example.com", password="pass"))


# ─── Token Refresh ───


@pytest.mark.asyncio
class TestAuthServiceRefresh:
    """Test AuthService.refresh_token."""

    @patch("src.services.jwt_handler")
    async def test_refresh_success(self, mock_jwt, auth_service, mock_user_repo, sample_user):
        mock_jwt.verify_refresh_token.return_value = {"sub": sample_user.id, "email": "a@b.com"}
        mock_user_repo.get_user_by_id.return_value = sample_user
        mock_jwt.create_access_token.return_value = "new-access"
        mock_jwt.create_refresh_token.return_value = "new-refresh"

        result = await auth_service.refresh_token("old-refresh-token")

        assert result.access_token == "new-access"

    @patch("src.services.jwt_handler")
    async def test_refresh_invalid_token(self, mock_jwt, auth_service):
        mock_jwt.verify_refresh_token.return_value = None

        with pytest.raises(AuthenticationException):
            await auth_service.refresh_token("bad-token")

    @patch("src.services.jwt_handler")
    async def test_refresh_user_not_found(self, mock_jwt, auth_service, mock_user_repo):
        mock_jwt.verify_refresh_token.return_value = {"sub": str(uuid4())}
        mock_user_repo.get_user_by_id.return_value = None

        with pytest.raises(AuthenticationException):
            await auth_service.refresh_token("token")


# ─── Get Current User ───


@pytest.mark.asyncio
class TestAuthServiceCurrentUser:
    """Test AuthService.get_current_user."""

    async def test_get_current_user(self, auth_service, mock_user_repo, sample_user):
        mock_user_repo.get_user_by_id.return_value = sample_user

        result = await auth_service.get_current_user(sample_user.id)
        assert result is not None

    async def test_get_current_user_not_found(self, auth_service, mock_user_repo):
        mock_user_repo.get_user_by_id.return_value = None

        with pytest.raises(ResourceNotFoundException):
            await auth_service.get_current_user(str(uuid4()))


# ─── Change Password ───


@pytest.mark.asyncio
class TestAuthServiceChangePassword:
    """Test AuthService.change_password."""

    @patch("src.services.security_handler")
    async def test_change_password_success(self, mock_security, auth_service, mock_user_repo, sample_user):
        mock_user_repo.get_user_by_id.return_value = sample_user
        mock_security.verify_password.return_value = True
        mock_security.validate_password_strength.return_value = (True, None)
        mock_security.hash_password.return_value = "$2b$12$newhash"
        mock_user_repo.update_user.return_value = sample_user

        req = PasswordChangeRequest(current_password="OldPass1!", new_password="NewPass1!")
        result = await auth_service.change_password(sample_user.id, req)

        mock_user_repo.update_user.assert_awaited_once()

    @patch("src.services.security_handler")
    async def test_change_password_wrong_current(self, mock_security, auth_service, mock_user_repo, sample_user):
        mock_user_repo.get_user_by_id.return_value = sample_user
        mock_security.verify_password.return_value = False

        with pytest.raises(AuthenticationException):
            await auth_service.change_password(
                sample_user.id,
                PasswordChangeRequest(current_password="wrong", new_password="NewPass1!"),
            )

    @patch("src.services.security_handler")
    async def test_change_password_weak_new(self, mock_security, auth_service, mock_user_repo, sample_user):
        mock_user_repo.get_user_by_id.return_value = sample_user
        mock_security.verify_password.return_value = True
        mock_security.validate_password_strength.return_value = (False, "Too weak")

        with pytest.raises(ValidationException):
            await auth_service.change_password(
                sample_user.id,
                PasswordChangeRequest(current_password="OldPass1!", new_password="weak"),
            )


# ─── Verify Email ───


@pytest.mark.asyncio
class TestAuthServiceVerifyEmail:
    """Test AuthService.verify_email."""

    async def test_verify_email_success(self, auth_service, mock_user_repo, sample_user):
        sample_user.is_verified = False
        mock_user_repo.get_user_by_id.return_value = sample_user
        mock_user_repo.update_user.return_value = sample_user

        result = await auth_service.verify_email(sample_user.id)
        mock_user_repo.update_user.assert_awaited_once()

    async def test_verify_email_user_not_found(self, auth_service, mock_user_repo):
        mock_user_repo.get_user_by_id.return_value = None

        with pytest.raises(ResourceNotFoundException):
            await auth_service.verify_email(str(uuid4()))
