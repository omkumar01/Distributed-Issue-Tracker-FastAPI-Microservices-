"""Configuration module for issue service."""

from pydantic_settings import BaseSettings
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings."""
    
    # Service config
    SERVICE_NAME: str = "issue-service"
    SERVICE_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    # Database config
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres_password@postgres:5432/issue_tracker"
    
    # Redis config
    REDIS_URL: str = "redis://redis:6379/0"
    
    # RabbitMQ config
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672/"
    
    # Observability
    JAEGER_ENABLED: bool = False
    JAEGER_HOST: str = "jaeger"
    JAEGER_PORT: int = 6831
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
