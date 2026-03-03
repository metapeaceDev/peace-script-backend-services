"""
Test Configuration for Presets Router
======================================
Fixtures and helpers specific to preset testing.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, Mock
from datetime import datetime
from typing import Optional, AsyncGenerator
from httpx import AsyncClient, ASGITransport

from dmm_backend.documents import User
from dmm_backend.documents_presets import UserPreset, PresetTemplate, PresetTag


@pytest_asyncio.fixture
async def client_with_auth(test_user, prepare_db) -> AsyncGenerator[AsyncClient, None]:
    """
    Create an async HTTP client with mocked authentication.
    This overrides the get_current_user dependency to return test_user.
    """
    from dmm_backend.main import app
    from dmm_backend.dependencies.auth import get_current_user, get_optional_user
    
    async def mock_get_current_user():
        return test_user
    
    async def mock_get_optional_user():
        return test_user
    
    # Override dependencies
    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[get_optional_user] = mock_get_optional_user
    
    # Create client
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    
    # Cleanup
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def mock_auth_dependency(client_with_auth, test_user):
    """
    Simplified fixture that ensures client_with_auth is set up.
    Returns the test user for convenience in test assertions.
    """
    return test_user


@pytest_asyncio.fixture
async def mock_admin_auth(test_admin_user):
    """Mock authentication for admin user."""
    from dmm_backend.main import app
    from dmm_backend.dependencies.auth import get_current_user, get_admin_user
    
    async def mock_get_current_user():
        return test_admin_user
    
    async def mock_get_admin_user():
        return test_admin_user
    
    # Override dependencies in the FastAPI app
    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[get_admin_user] = mock_get_admin_user
    
    yield test_admin_user
    
    # Cleanup
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(prepare_db):
    """Create a test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password="$2b$12$hashed_password",
        is_active=True,
        is_admin=False,
        created_at=datetime.now()
    )
    await user.insert()
    return user


@pytest_asyncio.fixture
async def test_admin_user(prepare_db):
    """Create a test admin user."""
    admin = User(
        email="admin@example.com",
        username="adminuser",
        full_name="Admin User",
        hashed_password="$2b$12$hashed_admin_password",
        is_active=True,
        is_admin=True,
        created_at=datetime.now()
    )
    await admin.insert()
    return admin


@pytest_asyncio.fixture
async def preset_template(prepare_db):
    """Create a test preset template."""
    template = PresetTemplate(
        template_id="test_template_001",
        name="Test Template",
        description="Test template description",
        category="shot_composition",
        visibility="system",
        config={
            "parameters": [
                {
                    "name": "brightness",
                    "type": "range",
                    "value": 50,
                    "min_value": 0,
                    "max_value": 100
                },
                {
                    "name": "shot_type",
                    "type": "select",
                    "value": "wide",
                    "options": ["wide", "medium", "close"]
                }
            ]
        },
        tags=[
            PresetTag(name="test", color="#FF0000"),
            PresetTag(name="template", color="#00FF00")
        ],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    await template.insert()
    return template


@pytest_asyncio.fixture
async def user_preset(prepare_db, test_user):
    """Create a test user preset."""
    preset = UserPreset(
        name="My Test Preset",
        description="User preset description",
        category="lighting",
        visibility="private",
        user_id=str(test_user.id),
        config={
            "parameters": [
                {
                    "name": "exposure",
                    "type": "range",
                    "value": 75,
                    "min_value": 0,
                    "max_value": 100
                }
            ]
        },
        is_favorite=False,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    await preset.insert()
    return preset


@pytest_asyncio.fixture
async def multiple_presets(prepare_db, test_user):
    """Create multiple test presets for pagination testing."""
    presets = []
    for i in range(15):
        preset = UserPreset(
            name=f"Test Preset {i+1}",
            description=f"Description for preset {i+1}",
            category="lighting" if i % 2 == 0 else "camera_movement",
            visibility="private",
            user_id=str(test_user.id),
            config={
                "parameters": [
                    {
                        "name": "param",
                        "type": "range",
                        "value": i * 10,
                        "min_value": 0,
                        "max_value": 100
                    }
                ]
            },
            is_favorite=(i % 3 == 0),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        await preset.insert()
        presets.append(preset)
    return presets
