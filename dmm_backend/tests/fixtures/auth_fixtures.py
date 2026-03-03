"""
Authentication Fixtures for Testing
====================================
Mock JWT tokens and user authentication for pytest tests.

This module provides fixtures to bypass authentication in tests,
allowing integration tests to run without real auth setup.
"""

import pytest
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from jose import jwt
from documents import User

# Test configuration
TEST_SECRET_KEY = "test-secret-key-do-not-use-in-production"
TEST_ALGORITHM = "HS256"
TEST_ACCESS_TOKEN_EXPIRE_MINUTES = 30


class MockUser:
    """Mock user for testing"""
    def __init__(
        self,
        user_id: str = "test-user-123",
        username: str = "testuser",
        email: str = "test@example.com",
        is_active: bool = True,
        is_admin: bool = False
    ):
        self.id = user_id
        self.user_id = user_id
        self.username = username
        self.email = email
        self.is_active = is_active
        self.is_admin = is_admin
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def model_dump(self) -> Dict[str, Any]:
        """Convert to dict (Pydantic-like interface)"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "is_admin": self.is_admin,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


def create_test_token(
    user_id: str = "test-user-123",
    username: str = "testuser",
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a test JWT token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=TEST_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": user_id,
        "username": username,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    
    encoded_jwt = jwt.encode(to_encode, TEST_SECRET_KEY, algorithm=TEST_ALGORITHM)
    return encoded_jwt


@pytest.fixture
def mock_user():
    """Regular mock user fixture"""
    return MockUser()


@pytest.fixture
def mock_admin_user():
    """Admin mock user fixture"""
    return MockUser(
        user_id="admin-user-123",
        username="admin",
        email="admin@example.com",
        is_admin=True
    )


@pytest.fixture
def mock_auth_token(mock_user):
    """Mock JWT token for regular user"""
    return create_test_token(
        user_id=mock_user.user_id,
        username=mock_user.username
    )


@pytest.fixture
def mock_admin_token(mock_admin_user):
    """Mock JWT token for admin user"""
    return create_test_token(
        user_id=mock_admin_user.user_id,
        username=mock_admin_user.username
    )


@pytest.fixture
def auth_headers(mock_auth_token):
    """Headers with authentication token"""
    return {
        "Authorization": f"Bearer {mock_auth_token}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def admin_auth_headers(mock_admin_token):
    """Headers with admin authentication token"""
    return {
        "Authorization": f"Bearer {mock_admin_token}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def mock_get_current_user(mock_user, monkeypatch):
    """
    Mock the get_current_user dependency to return test user.
    
    Usage in tests:
        def test_something(client, mock_get_current_user):
            response = client.get("/api/endpoint")
            # Authentication is bypassed, returns mock_user
    """
    async def _mock_get_current_user():
        return mock_user
    
    # Patch the dependency function
    try:
        from dependencies.auth import get_current_user
        monkeypatch.setattr(
            "dependencies.auth.get_current_user",
            lambda: _mock_get_current_user()
        )
    except ImportError:
        pass  # Dependency module might not exist yet
    
    return mock_user


@pytest.fixture
def mock_get_admin_user(mock_admin_user, monkeypatch):
    """
    Mock the get_admin_user dependency to return admin user.
    
    Usage in tests:
        def test_admin_endpoint(client, mock_get_admin_user):
            response = client.delete("/api/admin/endpoint")
            # Admin authentication is bypassed
    """
    async def _mock_get_admin_user():
        return mock_admin_user
    
    try:
        from dependencies.auth import get_admin_user
        monkeypatch.setattr(
            "dependencies.auth.get_admin_user",
            lambda: _mock_get_admin_user()
        )
    except ImportError:
        pass
    
    return mock_admin_user


@pytest.fixture
def bypass_auth(monkeypatch):
    """
    Completely bypass authentication for all endpoints.
    
    Usage:
        def test_without_auth(client, bypass_auth):
            response = client.get("/api/protected")
            # No authentication needed
    """
    mock_user = MockUser()
    
    async def _return_mock_user():
        return mock_user
    
    # Patch all auth dependencies
    auth_functions = [
        "dependencies.auth.get_current_user",
        "dependencies.auth.get_optional_user",
        "dependencies.auth.get_admin_user",
    ]
    
    for func_path in auth_functions:
        try:
            monkeypatch.setattr(func_path, lambda: _return_mock_user())
        except (ImportError, AttributeError):
            pass  # Function doesn't exist yet
    
    return mock_user


# Usage Examples:
# ===============
#
# Example 1: Test with mock user
# -------------------------------
# def test_get_user_presets(client, mock_user, auth_headers):
#     response = client.get(
#         "/api/presets/user",
#         headers=auth_headers
#     )
#     assert response.status_code == 200
#
# Example 2: Test with bypassed auth
# -----------------------------------
# def test_create_preset(client, bypass_auth):
#     response = client.post(
#         "/api/presets/user",
#         json={"name": "Test Preset"}
#     )
#     assert response.status_code == 201
#
# Example 3: Test admin endpoint
# -------------------------------
# def test_delete_template(client, mock_admin_user, admin_auth_headers):
#     response = client.delete(
#         "/api/presets/templates/123",
#         headers=admin_auth_headers
#     )
#     assert response.status_code == 204
