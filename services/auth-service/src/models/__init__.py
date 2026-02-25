"""SQLAlchemy models for auth service."""

from sqlalchemy import Column, String, DateTime, Boolean, Integer, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class UserModel(Base):
    """User model for database."""
    
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<UserModel(id={self.id}, email={self.email}, username={self.username})>"


class RefreshTokenModel(Base):
    """Refresh token model for tracking issued tokens."""
    
    __tablename__ = "refresh_tokens"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), index=True, nullable=False)
    token_hash = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<RefreshTokenModel(id={self.id}, user_id={self.user_id})>"


class LoginAttemptModel(Base):
    """Login attempt model for tracking failed attempts."""
    
    __tablename__ = "login_attempts"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), index=True, nullable=True)
    email = Column(String(255), index=True, nullable=False)
    ip_address = Column(String(45), nullable=False)
    success = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<LoginAttemptModel(id={self.id}, email={self.email}, success={self.success})>"


class OAuthProviderModel(Base):
    """OAuth provider credentials model."""
    
    __tablename__ = "oauth_providers"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), index=True, nullable=False)
    provider = Column(String(50), nullable=False)  # google, github, etc.
    provider_user_id = Column(String(255), nullable=False)
    access_token = Column(String(500), nullable=True)
    refresh_token = Column(String(500), nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<OAuthProviderModel(id={self.id}, user_id={self.user_id}, provider={self.provider})>"
