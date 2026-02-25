"""Exceptions and error handling."""

from typing import Optional, Any, Dict


class ApplicationException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(ApplicationException):
    """Raised for validation errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=422, error_code="VALIDATION_ERROR", details=details)


class AuthenticationException(ApplicationException):
    """Raised for authentication errors."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401, error_code="AUTH_FAILED")


class AuthorizationException(ApplicationException):
    """Raised for authorization errors."""

    def __init__(self, message: str = "Access denied"):
        super().__init__(message, status_code=403, error_code="ACCESS_DENIED")


class ResourceNotFoundException(ApplicationException):
    """Raised when a resource is not found."""

    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} {resource_id} not found"
        super().__init__(message, status_code=404, error_code="RESOURCE_NOT_FOUND")


class ServiceException(ApplicationException):
    """Raised for service-level errors."""

    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message, status_code=status_code, error_code="SERVICE_ERROR")


class ExternalServiceException(ApplicationException):
    """Raised when external service call fails."""

    def __init__(self, service_name: str, message: str):
        error_message = f"External service error from {service_name}: {message}"
        super().__init__(error_message, status_code=502, error_code="EXTERNAL_SERVICE_ERROR")


class DatabaseException(ApplicationException):
    """Raised for database errors."""

    def __init__(self, message: str):
        super().__init__(message, status_code=500, error_code="DATABASE_ERROR")


class ConflictException(ApplicationException):
    """Raised for conflict errors (e.g., duplicate resource)."""

    def __init__(self, message: str):
        super().__init__(message, status_code=409, error_code="CONFLICT")
