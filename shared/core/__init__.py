"""
Core utilities and helpers for all services.
"""

import logging
from typing import Optional
import os
from functools import lru_cache


logger = logging.getLogger(__name__)


class Settings:
    """Application settings from environment variables."""

    def __init__(self):
        # Database
        self.DB_HOST = os.getenv("DB_HOST", "postgres")
        self.DB_PORT = int(os.getenv("DB_PORT", "5432"))
        self.DB_NAME = os.getenv("DB_NAME", "issue_tracker")
        self.DB_USER = os.getenv("DB_USER", "postgres")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres_password")

        # Redis
        self.REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
        self.REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
        self.REDIS_DB = int(os.getenv("REDIS_DB", "0"))

        # RabbitMQ
        self.RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
        self.RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
        self.RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
        self.RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")

        # Elasticsearch
        self.ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "localhost")
        self.ELASTICSEARCH_PORT = int(os.getenv("ELASTICSEARCH_PORT", "9200"))

        # JWT
        self.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
        self.JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
        self.JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
        self.JWT_REFRESH_EXPIRATION_DAYS = int(os.getenv("JWT_REFRESH_EXPIRATION_DAYS", "7"))

        # Service URLs
        self.AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
        self.USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8002")
        self.PROJECT_SERVICE_URL = os.getenv("PROJECT_SERVICE_URL", "http://localhost:8003")
        self.ISSUE_SERVICE_URL = os.getenv("ISSUE_SERVICE_URL", "http://localhost:8004")
        self.COMMENT_SERVICE_URL = os.getenv("COMMENT_SERVICE_URL", "http://localhost:8005")
        self.NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8006")
        self.SEARCH_SERVICE_URL = os.getenv("SEARCH_SERVICE_URL", "http://localhost:8007")
        self.AUDIT_SERVICE_URL = os.getenv("AUDIT_SERVICE_URL", "http://localhost:8008")

        # Environment
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        self.DEBUG = os.getenv("DEBUG", "true").lower() == "true"
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

        # Service name
        self.SERVICE_NAME = os.getenv("SERVICE_NAME", "unknown-service")

        # Database URL
        self.DATABASE_URL = os.getenv(
            "DATABASE_URL",
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def rabbitmq_url(self) -> str:
        """Get RabbitMQ connection URL."""
        return f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/"

    @property
    def redis_url(self) -> str:
        """Get Redis connection URL."""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def elasticsearch_url(self) -> str:
        """Get Elasticsearch connection URL."""
        return f"http://{self.ELASTICSEARCH_HOST}:{self.ELASTICSEARCH_PORT}"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


def setup_logging(service_name: str, log_level: str = "INFO") -> None:
    """Setup structured logging for a service."""
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logging.getLogger(service_name).setLevel(log_level)


class ServiceClient:
    """Base client for inter-service communication."""

    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout

    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint."""
        return f"{self.base_url}{endpoint}"
