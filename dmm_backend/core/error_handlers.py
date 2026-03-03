"""
Standardized Error Handling System for DMM Backend.

This module provides:
- Standardized error response format
- Global exception handlers
- HTTP exception handlers
- Validation error handlers
- Comprehensive error logging

Usage:
    from core.error_handlers import ErrorResponse, HTTPException
    
    # In FastAPI app initialization:
    from core.error_handlers import (
        global_exception_handler,
        validation_exception_handler,
        http_exception_handler
    )
    
    app.add_exception_handler(Exception, global_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
import logging
import traceback
import sys

# Configure logging
logger = logging.getLogger(__name__)


class ErrorResponse(BaseModel):
    """
    Standardized error response format.
    
    All API errors should return this format for consistency.
    """
    error: str = Field(..., description="Error type/code (e.g., 'ValidationError', 'NotFoundError')")
    message: str = Field(..., description="User-friendly error message")
    detail: Optional[str] = Field(None, description="Technical details (optional, for debugging)")
    timestamp: str = Field(..., description="ISO 8601 timestamp when error occurred")
    path: str = Field(..., description="Request path that caused the error")
    request_id: Optional[str] = Field(None, description="Request tracking ID (if available)")
    errors: Optional[List[Dict[str, Any]]] = Field(None, description="Detailed validation errors")
    
    class Config:
        schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Invalid input data",
                "detail": "Email format is invalid",
                "timestamp": "2024-11-04T16:30:00Z",
                "path": "/api/auth/register",
                "request_id": "req_abc123xyz",
                "errors": [
                    {
                        "field": "email",
                        "message": "Invalid email format",
                        "type": "value_error.email"
                    }
                ]
            }
        }


class ErrorCode:
    """Standard error codes for the application."""
    
    # Client errors (4xx)
    BAD_REQUEST = "BadRequest"
    UNAUTHORIZED = "Unauthorized"
    FORBIDDEN = "Forbidden"
    NOT_FOUND = "NotFound"
    CONFLICT = "Conflict"
    VALIDATION_ERROR = "ValidationError"
    UNPROCESSABLE_ENTITY = "UnprocessableEntity"
    
    # Server errors (5xx)
    INTERNAL_SERVER_ERROR = "InternalServerError"
    SERVICE_UNAVAILABLE = "ServiceUnavailable"
    DATABASE_ERROR = "DatabaseError"
    EXTERNAL_SERVICE_ERROR = "ExternalServiceError"


def get_request_id(request: Request) -> Optional[str]:
    """
    Extract request ID from headers or generate one.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Request ID string or None
    """
    return request.headers.get("X-Request-ID") or request.headers.get("X-Correlation-ID")


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for unhandled exceptions.
    
    This catches all exceptions that aren't explicitly handled
    and returns a standardized error response.
    
    Args:
        request: FastAPI request object
        exc: The exception that was raised
        
    Returns:
        JSONResponse with standardized error format
    """
    request_id = get_request_id(request)
    
    # Log the exception with full context
    logger.error(
        f"Unhandled exception: {type(exc).__name__}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "request_id": request_id,
            "error_type": type(exc).__name__,
            "error_message": str(exc),
        },
        exc_info=True
    )
    
    # In development, include stack trace
    detail = None
    if sys.platform != "win32":  # Simple dev check
        try:
            detail = traceback.format_exc()
        except:
            pass
    
    error_response = ErrorResponse(
        error=ErrorCode.INTERNAL_SERVER_ERROR,
        message="An unexpected error occurred. Please try again later.",
        detail=detail if detail else str(exc),
        timestamp=datetime.utcnow().isoformat() + "Z",
        path=str(request.url.path),
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.dict(exclude_none=True)
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handler for FastAPI HTTPException.
    
    Converts HTTPException to standardized error response format.
    
    Args:
        request: FastAPI request object
        exc: HTTPException instance
        
    Returns:
        JSONResponse with standardized error format
    """
    request_id = get_request_id(request)
    
    # Map status codes to error types
    error_type_map = {
        400: ErrorCode.BAD_REQUEST,
        401: ErrorCode.UNAUTHORIZED,
        403: ErrorCode.FORBIDDEN,
        404: ErrorCode.NOT_FOUND,
        409: ErrorCode.CONFLICT,
        422: ErrorCode.UNPROCESSABLE_ENTITY,
        500: ErrorCode.INTERNAL_SERVER_ERROR,
        503: ErrorCode.SERVICE_UNAVAILABLE,
    }
    
    error_type = error_type_map.get(exc.status_code, ErrorCode.INTERNAL_SERVER_ERROR)
    
    # Log the exception
    log_level = logging.WARNING if exc.status_code < 500 else logging.ERROR
    logger.log(
        log_level,
        f"HTTP {exc.status_code}: {exc.detail}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "request_id": request_id,
            "status_code": exc.status_code,
        }
    )
    
    error_response = ErrorResponse(
        error=error_type,
        message=str(exc.detail),
        timestamp=datetime.utcnow().isoformat() + "Z",
        path=str(request.url.path),
        request_id=request_id
    )
    
    # Add 'detail' field for FastAPI compatibility (tests expect this)
    response_dict = error_response.dict(exclude_none=True)
    response_dict["detail"] = str(exc.detail)
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response_dict
    )


async def validation_exception_handler(
    request: Request, 
    exc: RequestValidationError
) -> JSONResponse:
    """
    Handler for Pydantic validation errors.
    
    Converts validation errors to standardized error response format
    with detailed field-level error information.
    
    Args:
        request: FastAPI request object
        exc: RequestValidationError instance
        
    Returns:
        JSONResponse with standardized error format including field errors
    """
    request_id = get_request_id(request)
    
    # Extract detailed validation errors
    errors = []
    for error in exc.errors():
        field_path = " -> ".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field_path,
            "message": error["msg"],
            "type": error["type"],
            "input": error.get("input")
        })
    
    # Log validation errors
    logger.warning(
        f"Validation error on {request.url.path}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "request_id": request_id,
            "errors": errors,
        }
    )
    
    error_response = ErrorResponse(
        error=ErrorCode.VALIDATION_ERROR,
        message="Invalid input data. Please check the errors and try again.",
        detail=f"{len(errors)} validation error(s) found",
        timestamp=datetime.utcnow().isoformat() + "Z",
        path=str(request.url.path),
        request_id=request_id,
        errors=errors
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.dict(exclude_none=True)
    )


class DatabaseException(Exception):
    """Exception raised for database-related errors."""
    pass


class ExternalServiceException(Exception):
    """Exception raised for external service errors."""
    pass


async def database_exception_handler(request: Request, exc: DatabaseException) -> JSONResponse:
    """
    Handler for database-related exceptions.
    
    Args:
        request: FastAPI request object
        exc: DatabaseException instance
        
    Returns:
        JSONResponse with standardized error format
    """
    request_id = get_request_id(request)
    
    logger.error(
        f"Database error: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "request_id": request_id,
        },
        exc_info=True
    )
    
    error_response = ErrorResponse(
        error=ErrorCode.DATABASE_ERROR,
        message="A database error occurred. Please try again later.",
        timestamp=datetime.utcnow().isoformat() + "Z",
        path=str(request.url.path),
        request_id=request_id,
        detail=str(exc)
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.dict(exclude_none=True)
    )


async def external_service_exception_handler(
    request: Request, 
    exc: ExternalServiceException
) -> JSONResponse:
    """
    Handler for external service exceptions.
    
    Args:
        request: FastAPI request object
        exc: ExternalServiceException instance
        
    Returns:
        JSONResponse with standardized error format
    """
    request_id = get_request_id(request)
    
    logger.error(
        f"External service error: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "request_id": request_id,
        },
        exc_info=True
    )
    
    error_response = ErrorResponse(
        error=ErrorCode.EXTERNAL_SERVICE_ERROR,
        message="An external service is temporarily unavailable. Please try again later.",
        timestamp=datetime.utcnow().isoformat() + "Z",
        path=str(request.url.path),
        request_id=request_id,
        detail=str(exc)
    )
    
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=error_response.dict(exclude_none=True)
    )


def setup_error_handlers(app) -> None:
    """
    Register all error handlers with the FastAPI application.
    
    Usage:
        from core.error_handlers import setup_error_handlers
        
        app = FastAPI()
        setup_error_handlers(app)
    
    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(Exception, global_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(DatabaseException, database_exception_handler)
    app.add_exception_handler(ExternalServiceException, external_service_exception_handler)
    
    logger.info("Error handlers registered successfully")
