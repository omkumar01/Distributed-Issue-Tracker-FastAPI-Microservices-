"""JWT token creation and validation."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
from jose import JWTError, jwt
from .config import settings

logger = logging.getLogger(__name__)


class JWTHandler:
    """Handles JWT token creation and validation."""
    
    def __init__(self):
        """Initialize JWT handler with settings."""
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire = settings.REFRESH_TOKEN_EXPIRE_DAYS
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create an access token.
        
        Args:
            data: Data to encode in the token
            expires_delta: Custom expiration time
            
        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire)
        
        to_encode.update({"exp": expire, "type": "access"})
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            raise
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create a refresh token.
        
        Args:
            data: Data to encode in the token
            
        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire)
        to_encode.update({"exp": expire, "type": "refresh"})
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating refresh token: {e}")
            raise
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token.
        
        Args:
            token: JWT token to verify
            
        Returns:
            Decoded token data
            
        Raises:
            JWTError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            logger.error(f"Invalid token: {e}")
            raise
    
    def verify_access_token(self, token: str) -> Dict[str, Any]:
        """Verify an access token.
        
        Args:
            token: JWT token to verify
            
        Returns:
            Decoded token data
            
        Raises:
            JWTError: If token is invalid or not an access token
        """
        payload = self.verify_token(token)
        if payload.get("type") != "access":
            raise JWTError("Invalid token type")
        return payload
    
    def verify_refresh_token(self, token: str) -> Dict[str, Any]:
        """Verify a refresh token.
        
        Args:
            token: JWT token to verify
            
        Returns:
            Decoded token data
            
        Raises:
            JWTError: If token is invalid or not a refresh token
        """
        payload = self.verify_token(token)
        if payload.get("type") != "refresh":
            raise JWTError("Invalid token type")
        return payload
    
    def get_user_id_from_token(self, token: str) -> str:
        """Extract user ID from token.
        
        Args:
            token: JWT token
            
        Returns:
            User ID
            
        Raises:
            JWTError: If token is invalid
        """
        payload = self.verify_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise JWTError("User ID not found in token")
        return user_id


# Global instance
jwt_handler = JWTHandler()
