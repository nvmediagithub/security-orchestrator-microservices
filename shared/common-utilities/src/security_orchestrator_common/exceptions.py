"""
Custom exception classes for SecurityOrchestrator microservices.

Provides standardized error handling with proper HTTP status codes and
structured error responses.
"""

from typing import Optional, Dict, Any


class SecurityOrchestratorError(Exception):
    """
    Base exception class for all SecurityOrchestrator errors.

    Attributes:
        message: Human-readable error message
        error_code: Machine-readable error code
        status_code: HTTP status code
        details: Additional error details
        correlation_id: Request correlation ID
    """

    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        self.correlation_id = correlation_id

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON response."""
        return {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "details": self.details
            },
            "correlation_id": self.correlation_id
        }


class ValidationError(SecurityOrchestratorError):
    """Exception raised for validation errors."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        correlation_id: Optional[str] = None
    ):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)

        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details=details,
            correlation_id=correlation_id
        )


class ConfigurationError(SecurityOrchestratorError):
    """Exception raised for configuration errors."""

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        correlation_id: Optional[str] = None
    ):
        details = {}
        if config_key:
            details["config_key"] = config_key

        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            status_code=500,
            details=details,
            correlation_id=correlation_id
        )


class ServiceUnavailableError(SecurityOrchestratorError):
    """Exception raised when a required service is unavailable."""

    def __init__(
        self,
        message: str,
        service_name: Optional[str] = None,
        retry_after: Optional[int] = None,
        correlation_id: Optional[str] = None
    ):
        details = {}
        if service_name:
            details["service_name"] = service_name
        if retry_after:
            details["retry_after_seconds"] = retry_after

        super().__init__(
            message=message,
            error_code="SERVICE_UNAVAILABLE",
            status_code=503,
            details=details,
            correlation_id=correlation_id
        )


class AuthenticationError(SecurityOrchestratorError):
    """Exception raised for authentication failures."""

    def __init__(
        self,
        message: str = "Authentication failed",
        auth_method: Optional[str] = None,
        correlation_id: Optional[str] = None
    ):
        details = {}
        if auth_method:
            details["auth_method"] = auth_method

        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=401,
            details=details,
            correlation_id=correlation_id
        )


class AuthorizationError(SecurityOrchestratorError):
    """Exception raised for authorization failures."""

    def __init__(
        self,
        message: str = "Insufficient permissions",
        required_role: Optional[str] = None,
        resource: Optional[str] = None,
        correlation_id: Optional[str] = None
    ):
        details = {}
        if required_role:
            details["required_role"] = required_role
        if resource:
            details["resource"] = resource

        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=403,
            details=details,
            correlation_id=correlation_id
        )


class ResourceNotFoundError(SecurityOrchestratorError):
    """Exception raised when a requested resource is not found."""

    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ):
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id

        super().__init__(
            message=message,
            error_code="RESOURCE_NOT_FOUND",
            status_code=404,
            details=details,
            correlation_id=correlation_id
        )


class ConflictError(SecurityOrchestratorError):
    """Exception raised for resource conflicts."""

    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ):
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id

        super().__init__(
            message=message,
            error_code="CONFLICT",
            status_code=409,
            details=details,
            correlation_id=correlation_id
        )


class RateLimitError(SecurityOrchestratorError):
    """Exception raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        correlation_id: Optional[str] = None
    ):
        details = {}
        if retry_after:
            details["retry_after_seconds"] = retry_after

        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details=details,
            correlation_id=correlation_id
        )


class ExternalServiceError(SecurityOrchestratorError):
    """Exception raised when external services fail."""

    def __init__(
        self,
        message: str,
        service_name: str,
        external_error_code: Optional[str] = None,
        correlation_id: Optional[str] = None
    ):
        details = {
            "service_name": service_name
        }
        if external_error_code:
            details["external_error_code"] = external_error_code

        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=502,
            details=details,
            correlation_id=correlation_id
        )


# Exception mapping for HTTP status codes
HTTP_EXCEPTION_MAPPING = {
    400: ValidationError,
    401: AuthenticationError,
    403: AuthorizationError,
    404: ResourceNotFoundError,
    409: ConflictError,
    429: RateLimitError,
    500: SecurityOrchestratorError,
    502: ExternalServiceError,
    503: ServiceUnavailableError,
}


def get_exception_for_status_code(status_code: int) -> type:
    """
    Get the appropriate exception class for an HTTP status code.

    Args:
        status_code: HTTP status code

    Returns:
        Exception class for the status code
    """
    return HTTP_EXCEPTION_MAPPING.get(status_code, SecurityOrchestratorError)