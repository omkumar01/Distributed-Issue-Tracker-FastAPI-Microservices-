"""Exception handler middleware."""

from fastapi import Request
from fastapi.responses import JSONResponse
from shared.utils.exceptions import ApplicationException
import logging

logger = logging.getLogger(__name__)


async def exception_handler(request: Request, exc: Exception):
    """Handle application exceptions.
    
    Args:
        request: HTTP request
        exc: Exception
        
    Returns:
        JSONResponse: Error response
    """
    if isinstance(exc, ApplicationException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": exc.error_code,
                "message": exc.message,
                "details": exc.details
            }
        )
    
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred"
        }
    )
