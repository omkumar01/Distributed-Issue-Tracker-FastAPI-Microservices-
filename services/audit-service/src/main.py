"""Audit Service - Main application."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import asyncio
from contextlib import asynccontextmanager

from src.routers import audit_router
from src.database import initialize_db_manager, get_database_manager, DatabaseManager
from src.repositories.audit_repository import AuditLogRepository
from src.services.event_consumer import AuditEventConsumer
from shared.core import setup_logging, get_settings

# Configure logging
settings = get_settings()
setup_logging("audit-service", settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Global variables
event_consumer = None
consumer_task = None


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup
    logger.info("Initializing Audit Service...")
    try:
        global event_consumer, consumer_task
        
        # Initialize database
        db_manager = initialize_db_manager(settings.DATABASE_URL)
        await db_manager.initialize()
        await db_manager.create_all_tables()
        logger.info("Database initialized successfully")
        
        # Initialize event consumer
        try:
            async_session = db_manager.get_session()
            repo = AuditLogRepository(async_session)
            event_consumer = AuditEventConsumer(repo, settings)
            await event_consumer.connect()
            
            # Start consumer in background
            consumer_task = asyncio.create_task(consumer_loop())
            logger.info("Event consumer started")
        except Exception as e:
            logger.warning(f"Event consumer not available, continuing without it: {e}")
            event_consumer = None
            
    except Exception as e:
        logger.error(f"Failed to initialize Audit Service: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Audit Service...")
    
    if consumer_task:
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            pass
    
    if event_consumer:
        await event_consumer.close()
    
    db_manager = get_database_manager()
    if db_manager:
        await db_manager.close()
    
    logger.info("Audit Service shut down complete")


async def consumer_loop():
    """Run event consumer loop."""
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        logger.info("Consumer loop cancelled")


# Create FastAPI app
app = FastAPI(
    title="Audit Service",
    description="Activity logs, compliance events, and data access tracking",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "audit-service",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Audit Service API",
        "version": "1.0.0",
        "description": "Manage audit logs, compliance events, and data access",
        "endpoints": {
            "audit_logs": "/api/v1",
            "compliance": "/api/v1/compliance",
            "data_access": "/api/v1/data-access",
            "health": "/health",
            "docs": "/docs",
            "openapi": "/openapi.json"
        }
    }


# Include routers
app.include_router(audit_router.router, prefix="/api/v1")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level=settings.LOG_LEVEL.lower()
    )
