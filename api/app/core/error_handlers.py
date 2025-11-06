"""
Global error handlers for FastAPI application
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import structlog

from app.core.errors import AppError, create_error_response

logger = structlog.get_logger(__name__)


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Handle custom application errors"""
    from app.core.errors import create_error_response

    # Handle BusinessError specifically
    if hasattr(exc, 'code'):
        content = create_error_response(
            code=exc.code,
            message=exc.message,
            details=exc.details
        )
    else:
        # Handle general AppError
        content = create_error_response(
            code="INTERNAL_ERROR",
            message=exc.message,
            details=exc.details
        )

    return JSONResponse(status_code=exc.status_code, content=content)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle standard HTTP exceptions"""
    logger.warning(
        "HTTP exception",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path,
        method=request.method
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "HTTP_ERROR",
                "message": exc.detail,
                "details": {},
                "retryable": False
            }
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions"""
    logger.error(
        "Unhandled exception",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
        method=request.method,
        exc_info=True
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
                "details": {"error_type": type(exc).__name__},
                "retryable": True
            }
        }
    )


async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle Pydantic validation errors"""
    from pydantic import ValidationError

    if isinstance(exc, ValidationError):
        logger.warning(
            "Validation error",
            errors=exc.errors(),
            path=request.url.path,
            method=request.method
        )

        # Extract field errors
        field_errors = {}
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            field_errors[field] = error["msg"]

        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid request data",
                    "details": {"fields": field_errors},
                    "retryable": False
                }
            }
        )

    # Re-raise if not a validation error
    raise exc


def setup_error_handlers(app):
    """Setup all error handlers for the FastAPI app"""

    # Import here to avoid circular imports
    from fastapi.exceptions import RequestValidationError

    # Custom application errors
    app.add_exception_handler(AppError, app_error_handler)

    # HTTP exceptions
    app.add_exception_handler(HTTPException, http_exception_handler)

    # Pydantic validation errors
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # General exceptions (must be last)
    app.add_exception_handler(Exception, general_exception_handler)

    logger.info("Error handlers configured")
