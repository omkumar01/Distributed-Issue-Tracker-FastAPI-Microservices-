"""Configuration module for auth service."""

from pydantic_settings import BaseSettings
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings."""
    
    # Service config
    SERVICE_NAME: str = "auth-service"
    SERVICE_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    # Database config
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres_password@postgres:5432/issue_tracker"
    
    # Redis config
    REDIS_URL: str = "redis://redis:6379/0"
    
    # JWT config
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Security config
    PASSWORD_MIN_LENGTH: int = 8
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15
    
    # OAuth config
    OAUTH_PROVIDERS: dict = {
        "google": {
            "client_id": "",
            "client_secret": "",
            "redirect_uri": "http://localhost:8001/api/v1/auth/oauth/google/callback"
        },
        "github": {
            "client_id": "",
            "client_secret": "",
            "redirect_uri": "http://localhost:8001/api/v1/auth/oauth/github/callback"
        }
    }
    
    # Observability
    JAEGER_ENABLED: bool = False
    JAEGER_HOST: str = "jaeger"
    JAEGER_PORT: int = 6831
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
