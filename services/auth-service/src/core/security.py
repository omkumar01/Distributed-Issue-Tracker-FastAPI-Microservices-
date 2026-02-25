"""Security utilities for hashing and encryption."""

from passlib.context import CryptContext
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class SecurityHandler:
    """Handles password hashing and security operations."""
    
    def __init__(self):
        """Initialize the security handler with bcrypt context."""
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__rounds=12
        )
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
            
        Raises:
            ValueError: If password cannot be hashed
            
        Note:
            Bcrypt has a 72-byte limit. Passwords longer than this will cause an error.
        """
        try:
            # Safely truncate password to 72 bytes if necessary (bcrypt limitation)
            password_bytes = password.encode('utf-8')
            
            if len(password_bytes) > 72:
                # Truncate at byte boundary and decode, removing incomplete characters
                truncated_bytes = password_bytes[:72]
                password = truncated_bytes.decode('utf-8', errors='ignore')
                
                # Double-check we're at or under the limit
                password_bytes = password.encode('utf-8')
                if len(password_bytes) > 72:
                    # Emergency fallback: use Latin-1 encoding which is 1 byte per character
                    password = password[:72]
            
            return self.pwd_context.hash(password)
        except ValueError as e:
            logger.error(f"Password hashing error: {e}")
            raise ValueError("Password is too long or contains invalid characters")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash.
        
        Args:
            plain_password: Plain text password from user
            hashed_password: Hashed password from database
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            # Safely handle password length for bcrypt verification
            password_bytes = plain_password.encode('utf-8')
            if len(password_bytes) > 72:
                # Truncate at byte boundary
                truncated_bytes = password_bytes[:72]
                plain_password = truncated_bytes.decode('utf-8', errors='ignore')
            
            return self.pwd_context.verify(plain_password, hashed_password)
        except ValueError as e:
            logger.error(f"Password verification error: {e}")
            return False
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def validate_password_strength(self, password: str, min_length: int = 8) -> tuple[bool, Optional[str]]:
        """Validate password strength.
        
        Args:
            password: Password to validate
            min_length: Minimum password length
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check bcrypt 72-byte limit (for UTF-8 encoded strings)
        if len(password.encode('utf-8')) > 72:
            return False, "Password must not exceed 72 bytes when encoded in UTF-8 (consider a shorter password or fewer special characters)"
        
        if len(password) < min_length:
            return False, f"Password must be at least {min_length} characters long"
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        if not (has_upper and has_lower and has_digit):
            return False, "Password must contain uppercase, lowercase, and digit"
        
        return True, None


# Global instance
security_handler = SecurityHandler()
