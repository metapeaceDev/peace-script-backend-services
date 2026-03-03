"""
Core utilities and shared components for DMM Backend.

This package contains core functionality including:
- Error handling and exception management
- Security utilities
- Configuration management
- Shared validators
"""

from .error_handlers import (
    ErrorResponse,
    ErrorCode,
    DatabaseException,
    ExternalServiceException,
    global_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    database_exception_handler,
    external_service_exception_handler,
    setup_error_handlers,
)

__all__ = [
    "ErrorResponse",
    "ErrorCode",
    "DatabaseException",
    "ExternalServiceException",
    "global_exception_handler",
    "validation_exception_handler",
    "http_exception_handler",
    "database_exception_handler",
    "external_service_exception_handler",
    "setup_error_handlers",
]
