"""Auth Service - SecurityHandler tests."""

import pytest
from src.core.security import SecurityHandler


@pytest.fixture
def security():
    return SecurityHandler()


class TestHashPassword:
    """Test password hashing."""

    def test_hash_returns_string(self, security):
        hashed = security.hash_password("StrongPass1!")
        assert isinstance(hashed, str)
        assert hashed != "StrongPass1!"

    def test_hash_different_for_same_input(self, security):
        h1 = security.hash_password("StrongPass1!")
        h2 = security.hash_password("StrongPass1!")
        # bcrypt salts generate different hashes each time
        assert h1 != h2

    def test_hash_long_password_truncated(self, security):
        # bcrypt has 72-byte limit; this should not raise
        long_pw = "A" * 200
        hashed = security.hash_password(long_pw)
        assert isinstance(hashed, str)


class TestVerifyPassword:
    """Test password verification."""

    def test_correct_password(self, security):
        password = "MySecureP@ss1"
        hashed = security.hash_password(password)
        assert security.verify_password(password, hashed) is True

    def test_wrong_password(self, security):
        hashed = security.hash_password("CorrectPass1!")
        assert security.verify_password("WrongPass1!", hashed) is False

    def test_invalid_hash(self, security):
        assert security.verify_password("password", "not-a-valid-hash") is False

    def test_empty_password(self, security):
        hashed = security.hash_password("ValidPass1!")
        assert security.verify_password("", hashed) is False


class TestValidatePasswordStrength:
    """Test password strength validation."""

    def test_strong_password(self, security):
        is_valid, msg = security.validate_password_strength("MyStr0ng!")
        assert is_valid is True
        assert msg is None

    def test_too_short(self, security):
        is_valid, msg = security.validate_password_strength("Ab1!")
        assert is_valid is False
        assert "at least" in msg

    def test_no_uppercase(self, security):
        is_valid, msg = security.validate_password_strength("lowercase1!")
        assert is_valid is False

    def test_no_lowercase(self, security):
        is_valid, msg = security.validate_password_strength("UPPERCASE1!")
        assert is_valid is False

    def test_no_digit(self, security):
        is_valid, msg = security.validate_password_strength("NoDigitHere!")
        assert is_valid is False

    def test_custom_min_length(self, security):
        is_valid, msg = security.validate_password_strength("Ab1!", min_length=3)
        assert is_valid is True

    def test_exceeds_72_bytes(self, security):
        long_pw = "Aa1!" + "x" * 100  # Over 72 bytes
        is_valid, msg = security.validate_password_strength(long_pw)
        assert is_valid is False
        assert "72 bytes" in msg
