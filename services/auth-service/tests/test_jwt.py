"""Auth Service - JWTHandler tests."""

import pytest
from datetime import timedelta
from unittest.mock import patch
from uuid import uuid4

from src.core.jwt import JWTHandler


@pytest.fixture
def jwt_handler():
    return JWTHandler()


class TestCreateAccessToken:
    """Test access token creation."""

    def test_returns_string(self, jwt_handler):
        token = jwt_handler.create_access_token(data={"sub": str(uuid4()), "email": "a@b.com"})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_custom_expiry(self, jwt_handler):
        token = jwt_handler.create_access_token(
            data={"sub": str(uuid4())},
            expires_delta=timedelta(hours=2),
        )
        assert isinstance(token, str)


class TestCreateRefreshToken:
    """Test refresh token creation."""

    def test_returns_string(self, jwt_handler):
        token = jwt_handler.create_refresh_token(data={"sub": str(uuid4()), "email": "a@b.com"})
        assert isinstance(token, str)


class TestVerifyAccessToken:
    """Test access token verification."""

    def test_valid_token(self, jwt_handler):
        user_id = str(uuid4())
        token = jwt_handler.create_access_token(data={"sub": user_id, "email": "a@b.com"})
        payload = jwt_handler.verify_access_token(token)
        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["type"] == "access"

    def test_expired_token(self, jwt_handler):
        token = jwt_handler.create_access_token(
            data={"sub": str(uuid4())},
            expires_delta=timedelta(seconds=-1),
        )
        payload = jwt_handler.verify_access_token(token)
        assert payload is None

    def test_invalid_token_string(self, jwt_handler):
        payload = jwt_handler.verify_access_token("not.a.valid.token")
        assert payload is None

    def test_refresh_token_rejected_as_access(self, jwt_handler):
        token = jwt_handler.create_refresh_token(data={"sub": str(uuid4())})
        payload = jwt_handler.verify_access_token(token)
        # Should reject because type != "access"
        assert payload is None


class TestVerifyRefreshToken:
    """Test refresh token verification."""

    def test_valid_refresh_token(self, jwt_handler):
        user_id = str(uuid4())
        token = jwt_handler.create_refresh_token(data={"sub": user_id, "email": "a@b.com"})
        payload = jwt_handler.verify_refresh_token(token)
        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["type"] == "refresh"

    def test_access_token_rejected_as_refresh(self, jwt_handler):
        token = jwt_handler.create_access_token(data={"sub": str(uuid4())})
        payload = jwt_handler.verify_refresh_token(token)
        # Should reject because type != "refresh"
        assert payload is None


class TestGetUserIdFromToken:
    """Test user ID extraction from token."""

    def test_extract_user_id(self, jwt_handler):
        user_id = str(uuid4())
        token = jwt_handler.create_access_token(data={"sub": user_id})
        extracted = jwt_handler.get_user_id_from_token(token)
        assert extracted == user_id

    def test_invalid_token_returns_none(self, jwt_handler):
        result = jwt_handler.get_user_id_from_token("garbage")
        assert result is None
