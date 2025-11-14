"""
Custom error classes and error handling utilities
"""

from typing import Dict, Any, Optional
from fastapi import HTTPException
from pydantic import BaseModel
from enum import Enum


class ErrorCode(str, Enum):
    """Standard error codes for the application."""
    # General errors
    INTERNAL_ERROR = "INTERNAL_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    DUPLICATE_RESOURCE = "DUPLICATE_RESOURCE"
    INSUFFICIENT_FUNDS = "INSUFFICIENT_FUNDS"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"

    # Benchmark errors
    BENCHMARK_INSUFFICIENT_DATA = "BENCHMARK_INSUFFICIENT_DATA"
    BENCHMARK_INVALID_DOMAIN = "BENCHMARK_INVALID_DOMAIN"
    BENCHMARK_LANGUAGE_MISMATCH = "BENCHMARK_LANGUAGE_MISMATCH"
    BENCHMARK_QUALITY_TOO_HIGH = "BENCHMARK_QUALITY_TOO_HIGH"
    BENCHMARK_RATE_LIMITED = "BENCHMARK_RATE_LIMITED"
    BENCHMARK_NETWORK_ERROR = "BENCHMARK_NETWORK_ERROR"
    BENCHMARK_SERVER_OVERLOAD = "BENCHMARK_SERVER_OVERLOAD"

    # Order errors
    ORDER_PROCESSING_FAILED = "ORDER_PROCESSING_FAILED"
    ORDER_PAYMENT_FAILED = "ORDER_PAYMENT_FAILED"
    ORDER_DELIVERY_FAILED = "ORDER_DELIVERY_FAILED"

    # Production errors
    PRODUCTION_CLUSTER_FAILED = "PRODUCTION_CLUSTER_FAILED"
    PRODUCTION_JOB_FAILED = "PRODUCTION_JOB_FAILED"
    PRODUCTION_UPLOAD_FAILED = "PRODUCTION_UPLOAD_FAILED"

    # Email errors
    EMAIL_SEND_FAILED = "EMAIL_SEND_FAILED"
    EMAIL_VERIFICATION_FAILED = "EMAIL_VERIFICATION_FAILED"
    EMAIL_DELIVERY_FAILED = "EMAIL_DELIVERY_FAILED"


class AppError(Exception):
    """Base class for application errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class BusinessError(AppError):
    """Base class for business logic errors."""

    def __init__(
        self,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 400
    ):
        self.code = code
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(BusinessError):
    """Validation related errors."""
    pass


class ResourceNotFoundError(BusinessError):
    """Resource not found errors."""

    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            code="RESOURCE_NOT_FOUND",
            message=f"{resource} with ID '{resource_id}' not found",
            details={"resource": resource, "resource_id": resource_id},
            status_code=404
        )


class DuplicateResourceError(BusinessError):
    """Duplicate resource errors."""

    def __init__(self, resource: str, details: Dict[str, Any]):
        super().__init__(
            code="DUPLICATE_RESOURCE",
            message=f"{resource} already exists",
            details=details,
            status_code=409
        )


class InsufficientFundsError(BusinessError):
    """Payment related errors."""

    def __init__(self, required: float, available: float):
        super().__init__(
            code="INSUFFICIENT_FUNDS",
            message="Insufficient funds for this transaction",
            details={"required": required, "available": available},
            status_code=402
        )


class ExternalServiceError(BusinessError):
    """External service errors (Stripe, HuggingFace, etc.)."""

    def __init__(self, service: str, error: str):
        super().__init__(
            code="EXTERNAL_SERVICE_ERROR",
            message=f"Error from {service}: {error}",
            details={"service": service, "error": error},
            status_code=502
        )


class BenchmarkError(BusinessError):
    """Benchmark processing errors with user-friendly suggestions."""

    ERROR_SUGGESTIONS = {
        "INSUFFICIENT_DATA": "Try expanding your time range or reducing keyword specificity",
        "INVALID_DOMAIN": "Check your domain name spelling and try using more specific terms",
        "LANGUAGE_MISMATCH": "Verify that your selected languages match your content",
        "QUALITY_TOO_HIGH": "Try reducing quality requirements or expanding your search scope",
        "RATE_LIMITED": "Please wait a few minutes before retrying",
        "NETWORK_ERROR": "Check your internet connection and try again",
        "SERVER_OVERLOAD": "The system is busy. Please try again in a few minutes",
    }

    def __init__(self, error_code: str, details: Optional[Dict[str, Any]] = None):
        suggestion = self.ERROR_SUGGESTIONS.get(error_code, "Please contact support for assistance")

        super().__init__(
            code=f"BENCHMARK_{error_code}",
            message=f"Benchmark failed: {error_code.replace('_', ' ').lower()}",
            details={
                "error_code": error_code,
                "suggestion": suggestion,
                **(details or {})
            },
            status_code=422
        )


class OrderError(BusinessError):
    """Order processing errors."""

    def __init__(self, error_type: str, order_id: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code=f"ORDER_{error_type}",
            message=f"Order processing failed: {error_type.replace('_', ' ').lower()}",
            details={"order_id": order_id, **(details or {})},
            status_code=422
        )


class ProductionError(BusinessError):
    """Production processing errors."""

    def __init__(self, error_type: str, order_id: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code=f"PRODUCTION_{error_type}",
            message=f"Production failed: {error_type.replace('_', ' ').lower()}",
            details={"order_id": order_id, **(details or {})},
            status_code=422
        )


# Error response models
class ErrorDetail(BaseModel):
    """Detailed error information."""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    suggestion: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response format."""
    error: ErrorDetail
    timestamp: str
    request_id: Optional[str] = None


# Error handling utilities
def create_error_response(
    code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    suggestion: Optional[str] = None,
    status_code: int = 400
) -> Dict[str, Any]:
    """Create a standardized error response."""
    from datetime import datetime

    return {
        "error": {
            "code": code,
            "message": message,
            "details": details,
            "suggestion": suggestion,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


def handle_business_error(error: BusinessError) -> HTTPException:
    """Convert business error to FastAPI HTTPException."""
    response_data = create_error_response(
        code=error.code,
        message=error.message,
        details=error.details,
        suggestion=error.details.get("suggestion"),
    )

    return HTTPException(
        status_code=error.status_code,
        detail=response_data
    )


def get_retry_after_header(error: BusinessError) -> Optional[str]:
    """Get retry-after header value for rate limited errors."""
    if error.code in ["RATE_LIMITED", "SERVER_OVERLOAD"]:
        return "300"  # 5 minutes
    return None