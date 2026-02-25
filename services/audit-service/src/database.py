"""Audit Service - Database connection and session management."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
import logging
import asyncio

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manage database connections."""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = None
        self.async_session_maker = None
        logger.info(f"DatabaseManager initialized with URL: {database_url[:50]}...")
    
    async def initialize(self):
        """Initialize database engine and session factory."""
        logger.info(f"Initializing database with URL: {self.database_url}")
        self.engine = create_async_engine(
            self.database_url,
            echo=False,
            poolclass=NullPool,
            future=True,
            connect_args={
                "timeout": 30,
                "ssl": "allow",
                "server_settings": {
                    "application_name": "audit-service"
                }
            }
        )
        
        self.async_session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            future=True
        )
        
        logger.info("Database engine and session maker initialized")
    
    async def close(self):
        """Close database connections."""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connections closed")
    
    async def get_session(self) -> AsyncSession:
        """Get a database session."""
        if not self.async_session_maker:
            raise RuntimeError("Database not initialized")
        return self.async_session_maker()
    
    async def create_all_tables(self, max_retries: int = 5, retry_delay: int = 2):
        """Create all tables with retry logic."""
        from src.models.audit_log import Base
        
        if not self.engine:
            raise RuntimeError("Database not initialized")
        
        logger.info(f"Attempting to create tables (max retries: {max_retries})...")
        
        for attempt in range(max_retries):
            try:
                async with self.engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
                logger.info("Database tables created successfully")
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Failed to create tables (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {retry_delay}s...")
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error(f"Failed to create tables after {max_retries} attempts: {e}")
                    raise


# Global database manager instance
db_manager: DatabaseManager = None


def initialize_db_manager(database_url: str) -> DatabaseManager:
    """Initialize the global database manager instance."""
    global db_manager
    db_manager = DatabaseManager(database_url)
    return db_manager


def get_database_manager() -> DatabaseManager:
    """Get the database manager instance."""
    if not db_manager:
        raise RuntimeError("Database manager not initialized")
    return db_manager


async def get_session() -> AsyncSession:
    """Dependency for getting database session in FastAPI routes."""
    session = await get_database_manager().get_session()
    try:
        yield session
    finally:
        await session.close()
