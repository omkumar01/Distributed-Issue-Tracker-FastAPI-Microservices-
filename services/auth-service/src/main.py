"""Auth Service - Main application."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from src.routers import auth_router
from src.database import database
from src.core.config import settings
from src.middleware import exception_handler
from src.observability import init_tracing, init_fastapi_instrumentation, init_sqlalchemy_instrumentation
from shared.utils.exceptions import ApplicationException

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.ENVIRONMENT == "production" else logging.DEBUG
)
logger = logging.getLogger(__name__)


# Startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for app startup and shutdown.
    
    Args:
        app: FastAPI application
    """
    # Startup
    logger.info(f"Starting {settings.SERVICE_NAME} v{settings.SERVICE_VERSION}")
    
    # Initialize tracing and instrumentation
    init_tracing()
    init_sqlalchemy_instrumentation()
    
    # Initialize database
    await database.initialize()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.SERVICE_NAME}")
    await database.close()


# Create FastAPI app with lifespan
app = FastAPI(
    title="Auth Service",
    description="Centralized authentication and JWT token management",
    version=settings.SERVICE_VERSION,
    lifespan=lifespan
)

# Initialize FastAPI instrumentation
init_fastapi_instrumentation(app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add global exception handler
@app.exception_handler(ApplicationException)
async def application_exception_handler(request, exc: ApplicationException):
    """Handle application exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred"
        }
    )

# Include routers
app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["auth"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"{settings.SERVICE_NAME} API",
        "version": settings.SERVICE_VERSION,
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
