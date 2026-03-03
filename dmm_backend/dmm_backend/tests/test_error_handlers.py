"""
Tests for Core Error Handling System.

Tests:
1. ErrorResponse model validation
2. Global exception handler
3. HTTP exception handler
4. Validation exception handler
5. Database exception handler
6. External service exception handler
"""

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ValidationError
from datetime import datetime

from core.error_handlers import (
    ErrorResponse,
    ErrorCode,
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    database_exception_handler,
    external_service_exception_handler,
    DatabaseException,
    ExternalServiceException,
    setup_error_handlers,
)
from fastapi import HTTPException


class TestErrorResponse:
    """Test ErrorResponse model."""
    
    def test_error_response_model_valid(self):
        """Test ErrorResponse with valid data."""
        error = ErrorResponse(
            error="TestError",
            message="Test message",
            timestamp=datetime.utcnow().isoformat() + "Z",
            path="/api/test"
        )
        
        assert error.error == "TestError"
        assert error.message == "Test message"
        assert error.path == "/api/test"
        assert error.detail is None
        assert error.request_id is None
    
    def test_error_response_model_with_details(self):
        """Test ErrorResponse with optional fields."""
        error = ErrorResponse(
            error="ValidationError",
            message="Invalid input",
            detail="Email is required",
            timestamp=datetime.utcnow().isoformat() + "Z",
            path="/api/register",
            request_id="req_123",
            errors=[{"field": "email", "message": "Required"}]
        )
        
        assert error.error == "ValidationError"
        assert error.detail == "Email is required"
        assert error.request_id == "req_123"
        assert len(error.errors) == 1
        assert error.errors[0]["field"] == "email"


class TestErrorHandlers:
    """Test error handler functions."""
    
    @pytest.fixture
    def app(self):
        """Create test FastAPI app."""
        app = FastAPI()
        setup_error_handlers(app)
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)
    
    def test_http_exception_handler_404(self, app, client):
        """Test HTTPException handler for 404."""
        @app.get("/test-404")
        async def test_404():
            raise HTTPException(status_code=404, detail="Resource not found")
        
        response = client.get("/test-404")
        
        assert response.status_code == 404
        data = response.json()
        assert data["error"] == ErrorCode.NOT_FOUND
        assert "not found" in data["message"].lower()
        assert data["path"] == "/test-404"
        assert "timestamp" in data
    
    def test_http_exception_handler_401(self, app, client):
        """Test HTTPException handler for 401."""
        @app.get("/test-401")
        async def test_401():
            raise HTTPException(status_code=401, detail="Unauthorized access")
        
        response = client.get("/test-401")
        
        assert response.status_code == 401
        data = response.json()
        assert data["error"] == ErrorCode.UNAUTHORIZED
        assert "Unauthorized" in data["message"]
    
    def test_http_exception_handler_403(self, app, client):
        """Test HTTPException handler for 403."""
        @app.get("/test-403")
        async def test_403():
            raise HTTPException(status_code=403, detail="Forbidden")
        
        response = client.get("/test-403")
        
        assert response.status_code == 403
        data = response.json()
        assert data["error"] == ErrorCode.FORBIDDEN
    
    def test_validation_exception_handler(self, app, client):
        """Test validation exception handler."""
        class TestModel(BaseModel):
            email: str
            age: int
        
        @app.post("/test-validation")
        async def test_validation(data: TestModel):
            return {"ok": True}
        
        # Send invalid data
        response = client.post("/test-validation", json={"email": "not-an-email"})
        
        assert response.status_code == 422
        data = response.json()
        assert data["error"] == ErrorCode.VALIDATION_ERROR
        assert "invalid input" in data["message"].lower()
        assert "errors" in data
        assert len(data["errors"]) > 0
    
    def test_global_exception_handler(self, app, client):
        """Test global exception handler for unhandled exceptions."""
        @app.get("/test-exception")
        async def test_exception():
            raise ValueError("Unexpected error occurred")
        
        # Use TestClient with raise_server_exceptions=False to test error handlers
        test_client = TestClient(app, raise_server_exceptions=False)
        response = test_client.get("/test-exception")
        
        assert response.status_code == 500
        data = response.json()
        assert data["error"] == ErrorCode.INTERNAL_SERVER_ERROR
        assert "unexpected error" in data["message"].lower()
        assert "timestamp" in data
    
    def test_database_exception_handler(self, app, client):
        """Test database exception handler."""
        @app.get("/test-db-error")
        async def test_db_error():
            raise DatabaseException("Database connection failed")
        
        response = client.get("/test-db-error")
        
        assert response.status_code == 500
        data = response.json()
        assert data["error"] == ErrorCode.DATABASE_ERROR
        assert "database" in data["message"].lower()
    
    def test_external_service_exception_handler(self, app, client):
        """Test external service exception handler."""
        @app.get("/test-external-error")
        async def test_external_error():
            raise ExternalServiceException("ComfyUI unavailable")
        
        response = client.get("/test-external-error")
        
        assert response.status_code == 503
        data = response.json()
        assert data["error"] == ErrorCode.EXTERNAL_SERVICE_ERROR
        assert "unavailable" in data["message"].lower()


class TestErrorCodes:
    """Test ErrorCode constants."""
    
    def test_error_codes_exist(self):
        """Test that all expected error codes exist."""
        assert hasattr(ErrorCode, "BAD_REQUEST")
        assert hasattr(ErrorCode, "UNAUTHORIZED")
        assert hasattr(ErrorCode, "FORBIDDEN")
        assert hasattr(ErrorCode, "NOT_FOUND")
        assert hasattr(ErrorCode, "CONFLICT")
        assert hasattr(ErrorCode, "VALIDATION_ERROR")
        assert hasattr(ErrorCode, "INTERNAL_SERVER_ERROR")
        assert hasattr(ErrorCode, "DATABASE_ERROR")
        assert hasattr(ErrorCode, "EXTERNAL_SERVICE_ERROR")
    
    def test_error_code_values(self):
        """Test error code string values."""
        assert ErrorCode.BAD_REQUEST == "BadRequest"
        assert ErrorCode.NOT_FOUND == "NotFound"
        assert ErrorCode.INTERNAL_SERVER_ERROR == "InternalServerError"


class TestCustomExceptions:
    """Test custom exception classes."""
    
    def test_database_exception(self):
        """Test DatabaseException."""
        exc = DatabaseException("Connection failed")
        assert str(exc) == "Connection failed"
        assert isinstance(exc, Exception)
    
    def test_external_service_exception(self):
        """Test ExternalServiceException."""
        exc = ExternalServiceException("Service timeout")
        assert str(exc) == "Service timeout"
        assert isinstance(exc, Exception)


class TestErrorHandlerIntegration:
    """Integration tests for complete error handling flow."""
    
    def test_multiple_validation_errors(self):
        """Test handling of multiple validation errors."""
        app = FastAPI()
        setup_error_handlers(app)
        
        class UserCreate(BaseModel):
            email: str
            username: str
            age: int
        
        @app.post("/users")
        async def create_user(user: UserCreate):
            return {"ok": True}
        
        client = TestClient(app)
        
        # Send data with multiple validation errors (missing required fields)
        response = client.post("/users", json={"email": "invalid"})
        
        assert response.status_code == 422
        data = response.json()
        assert data["error"] == ErrorCode.VALIDATION_ERROR
        assert "errors" in data
        # Should have at least 1 error (missing age at minimum)
        assert len(data["errors"]) >= 1
    
    def test_error_response_consistency(self):
        """Test that all error responses follow the same format."""
        app = FastAPI()
        setup_error_handlers(app)
        
        @app.get("/404")
        async def test_404():
            raise HTTPException(status_code=404, detail="Not found")
        
        @app.get("/500")
        async def test_500():
            raise ValueError("Internal error")
        
        # Use TestClient with raise_server_exceptions=False to test error handlers
        client = TestClient(app, raise_server_exceptions=False)
        
        # Test 404
        response_404 = client.get("/404")
        data_404 = response_404.json()
        
        # Test 500
        response_500 = client.get("/500")
        data_500 = response_500.json()
        
        # Both should have same structure
        required_fields = ["error", "message", "timestamp", "path"]
        for field in required_fields:
            assert field in data_404
            assert field in data_500
        
        # Timestamps should be ISO format
        assert "T" in data_404["timestamp"]
        assert "T" in data_500["timestamp"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
