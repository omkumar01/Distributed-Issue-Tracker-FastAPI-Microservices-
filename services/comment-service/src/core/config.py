"""Configuration settings for the Comment Service."""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Service configuration settings."""
    
    # Service Info
    SERVICE_NAME: str = "comment-service"
    SERVICE_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str
    
    # RabbitMQ
    RABBITMQ_URL: Optional[str] = "amqp://guest:guest@rabbitmq:5672/"
    
    # Redis (for WebSocket Pub/Sub if needed in the future)
    REDIS_URL: Optional[str] = "redis://redis:6379/2"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
