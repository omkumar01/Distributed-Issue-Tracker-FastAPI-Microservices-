"""Auth Service - Pydantic schema validation tests."""

import pytest
from uuid import uuid4
from pydantic import ValidationError

from src.schemas import (
    UserCreate, UserLogin, UserResponse, TokenResponse,
    PasswordChangeRequest, RefreshTokenRequest, EmailVerificationRequest,
    ErrorResponse,
)


class TestUserCreate:
    """Test UserCreate schema."""

    def test_valid(self):
        u = UserCreate(
            email="test@example.com",
            username="testuser",
            password="StrongP@ss1",
            first_name="Test",
            last_name="User",
        )
        assert u.email == "test@example.com"
        assert u.username == "testuser"

    def test_missing_email(self):
        with pytest.raises(ValidationError):
            UserCreate(username="user", password="Pass1!", first_name="A", last_name="B")

    def test_invalid_email_format(self):
        with pytest.raises(ValidationError):
            UserCreate(email="not-email", username="user", password="Pass1!", first_name="A", last_name="B")

    def test_short_username(self):
        with pytest.raises(ValidationError):
            UserCreate(email="a@b.com", username="ab", password="Pass1!", first_name="A", last_name="B")

    def test_short_password(self):
        with pytest.raises(ValidationError):
            UserCreate(email="a@b.com", username="user", password="Ab1!", first_name="A", last_name="B")

    def test_minimal_valid(self):
        u = UserCreate(
            email="a@b.com",
            username="usr",
            password="StrongP@ss1",
            first_name="A",
            last_name="B",
        )
        assert u.first_name == "A"


class TestUserLogin:
    """Test UserLogin schema."""

    def test_valid(self):
        login = UserLogin(email="test@example.com", password="password123")
        assert login.email == "test@example.com"

    def test_missing_password(self):
        with pytest.raises(ValidationError):
            UserLogin(email="test@example.com")


class TestTokenResponse:
    """Test TokenResponse schema."""

    def test_valid(self):
        resp = TokenResponse(
            access_token="eyJ...",
            refresh_token="eyJ...",
            token_type="bearer",
            expires_in=1800,
        )
        assert resp.token_type == "bearer"
        assert resp.expires_in == 1800

    def test_default_token_type(self):
        resp = TokenResponse(
            access_token="eyJ...",
            refresh_token="eyJ...",
            expires_in=1800,
        )
        assert resp.token_type == "bearer"


class TestPasswordChangeRequest:
    """Test PasswordChangeRequest schema."""

    def test_valid(self):
        req = PasswordChangeRequest(
            current_password="OldPass1!",
            new_password="NewPass1!",
        )
        assert req.current_password == "OldPass1!"
        assert req.new_password == "NewPass1!"

    def test_missing_new_password(self):
        with pytest.raises(ValidationError):
            PasswordChangeRequest(current_password="OldPass1!")


class TestRefreshTokenRequest:
    """Test RefreshTokenRequest schema."""

    def test_valid(self):
        req = RefreshTokenRequest(refresh_token="some-token-value")
        assert req.refresh_token == "some-token-value"


class TestUserResponse:
    """Test UserResponse schema."""

    def test_from_dict(self):
        user_id = str(uuid4())
        resp = UserResponse(
            id=user_id,
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            is_active=True,
            is_verified=False,
        )
        assert resp.id == user_id
        assert resp.is_active is True


class TestErrorResponse:
    """Test ErrorResponse schema."""

    def test_valid(self):
        err = ErrorResponse(
            error_code="VALIDATION_ERROR",
            message="Invalid input",
        )
        assert err.error_code == "VALIDATION_ERROR"
