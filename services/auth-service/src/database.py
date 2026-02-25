"""Database configuration and session management."""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from src.core.config import settings
from src.models import Base
import logging

logger = logging.getLogger(__name__)


class Database:
    """Database connection handler."""
    
    def __init__(self):
        """Initialize database."""
        self.engine = None
        self.SessionLocal = None
    
    async def initialize(self):
        """Initialize database engine and session factory."""
        try:
            self.engine = create_async_engine(
                settings.DATABASE_URL,
                echo=settings.ENVIRONMENT == "development",
                poolclass=NullPool,
                connect_args={
                    "server_settings": {"application_name": settings.SERVICE_NAME}
                }
            )
            
            self.SessionLocal = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Create all tables
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            logger.info("Database initialized successfully and tables created")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def close(self):
        """Close database connection."""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connection closed")
    
    async def get_session(self) -> AsyncSession:
        """Get database session.
        
        Yields:
            AsyncSession: Database session
        """
        if not self.SessionLocal:
            raise RuntimeError("Database not initialized")
        
        async with self.SessionLocal() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                logger.error(f"Database session error: {e}")
                raise
            finally:
                await session.close()


# Global database instance
database = Database()
