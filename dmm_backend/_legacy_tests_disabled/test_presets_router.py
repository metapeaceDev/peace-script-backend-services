"""
Comprehensive Test Suite for Presets Router
===========================================
Tests all endpoints in the Presets API including templates, user presets, favorites, and duplication.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from datetime import datetime
from beanie import PydanticObjectId

# Import local fixtures
from tests.conftest_presets import (
    client_with_auth,
    mock_auth_dependency,
    mock_admin_auth,
    test_user,
    test_admin_user,
    preset_template,
    user_preset,
    multiple_presets
)

from dmm_backend.documents import User
from dmm_backend.utils.preset_validators import PresetValidator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from datetime import datetime
from beanie import PydanticObjectId

from dmm_backend.documents import User

# Import from conftest_presets
from conftest_presets import (
    test_user,
    test_admin_user,
    preset_template,
    user_preset,
    multiple_presets,
    mock_auth_dependency,
    mock_admin_auth
)


# ============================================================================
# Template Endpoints Tests
# ============================================================================

class TestPresetTemplates:
    """Test suite for preset template endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_templates_success(self, client_with_auth: AsyncClient, preset_template):
        """Test GET /api/presets/templates - Success."""
        response = await client_with_auth.get("/api/presets/templates")
        
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        assert len(data["templates"]) >= 1
        assert data["templates"][0]["name"] == "Test Template"
    
    @pytest.mark.asyncio
    async def test_get_templates_with_filters(self, client_with_auth: AsyncClient, preset_template):
        """Test GET /api/presets/templates with filters."""
        response = await client_with_auth.get(
            "/api/presets/templates",
            params={"category": "shot_composition"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["templates"]) >= 1
    
    @pytest.mark.asyncio
    async def test_get_templates_empty(self, client_with_auth: AsyncClient):
        """Test GET /api/presets/templates with no templates."""
        response = await client_with_auth.get("/api/presets/templates")
        
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        assert len(data["templates"]) == 0
    
    @pytest.mark.asyncio
    async def test_get_template_by_id_success(self, client_with_auth: AsyncClient, preset_template):
        """Test GET /api/presets/templates/{id} - Success."""
        template_id = str(preset_template.id)
        response = await client_with_auth.get(f"/api/presets/templates/{template_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["template_id"] == template_id
        assert data["name"] == "Test Template"
    
    @pytest.mark.asyncio
    async def test_get_template_by_id_not_found(self, client_with_auth: AsyncClient):
        """Test GET /api/presets/templates/{id} - Not Found."""
        fake_id = str(PydanticObjectId())
        response = await client_with_auth.get(f"/api/presets/templates/{fake_id}")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_get_template_by_id_invalid_id(self, client_with_auth: AsyncClient):
        """Test GET /api/presets/templates/{id} - Invalid ID format."""
        response = await client_with_auth.get("/api/presets/templates/invalid_id")
        
        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()


# ============================================================================
# User Preset CRUD Tests
# ============================================================================

class TestUserPresetsCRUD:
    """Test suite for user preset CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_create_preset_success(self, client_with_auth: AsyncClient, mock_auth_dependency, test_user):
        """Test POST /api/presets/user - Success."""
        preset_data = {
            "name": "New Test Preset",
            "description": "Test description",
            "category": "lighting",
            "visibility": "private",
            "config": {
                "parameters": [
                    {
                        "name": "brightness",
                        "type": "range",
                        "value": 50,
                        "min_value": 0,
                        "max_value": 100
                    }
                ]
            }
        }
        
        response = await client_with_auth.post(
            "/api/presets/user",
            json=preset_data
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Test Preset"
        assert data["user_id"] == str(test_user.id)
    
    @pytest.mark.asyncio
    async def test_create_preset_validation_name_too_short(self, client_with_auth: AsyncClient, mock_auth_dependency):
        """Test POST /api/presets/user - Name too short."""
        preset_data = {
            "name": "AB",  # Too short (min 3)
            "category": "lighting",
            "config": {"parameters": [{"name": "test", "type": "range", "value": 50}]}
        }
        
        response = await client_with_auth.post(
            "/api/presets/user",
            json=preset_data
        )
        
        assert response.status_code == 400
        assert "at least 3 characters" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_create_preset_validation_name_too_long(self, client_with_auth: AsyncClient, mock_auth_dependency):
        """Test POST /api/presets/user - Name too long."""
        preset_data = {
            "name": "x" * 101,  # Too long (max 100)
            "category": "lighting",
            "config": {"parameters": [{"name": "test", "type": "range", "value": 50}]}
        }
        
        response = await client_with_auth.post(
            "/api/presets/user",
            json=preset_data
        )
        
        assert response.status_code == 400
        assert "exceed 100 characters" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_create_preset_validation_invalid_category(self, client_with_auth: AsyncClient, mock_auth_dependency):
        """Test POST /api/presets/user - Invalid category."""
        preset_data = {
            "name": "Test Preset",
            "category": "invalid_category",
            "config": {"parameters": [{"name": "test", "type": "range", "value": 50}]}
        }
        
        response = await client_with_auth.post(
            "/api/presets/user",
            json=preset_data
        )
        
        assert response.status_code == 400
        assert "invalid category" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_create_preset_validation_invalid_parameter_type(self, client_with_auth: AsyncClient, mock_auth_dependency):
        """Test POST /api/presets/user - Invalid parameter type."""
        preset_data = {
            "name": "Test Preset",
            "category": "lighting",
            "config": {
                "parameters": [
                    {
                        "name": "test",
                        "type": "invalid_type",
                        "value": 50
                    }
                ]
            }
        }
        
        response = await client_with_auth.post(
            "/api/presets/user",
            json=preset_data
        )
        
        assert response.status_code == 400
        assert "invalid type" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_create_preset_no_auth(self, client_with_auth: AsyncClient):
        """Test POST /api/presets/user - No authentication."""
        preset_data = {
            "name": "Test",
            "category": "lighting",
            "config": {"parameters": [{"name": "test", "type": "range", "value": 50}]}
        }
        
        response = await client_with_auth.post("/api/presets/user", json=preset_data)
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_user_presets(self, client_with_auth: AsyncClient, mock_auth_dependency, user_preset):
        """Test GET /api/presets/user - Get all user presets."""
        response = await client_with_auth.get("/api/presets/user")
        
        assert response.status_code == 200
        data = response.json()
        assert "presets" in data
        assert len(data["presets"]) >= 1
    
    @pytest.mark.asyncio
    async def test_get_user_preset_by_id(self, client_with_auth: AsyncClient, mock_auth_dependency, user_preset):
        """Test GET /api/presets/user/{id} - Get specific preset."""
        preset_id = str(user_preset.id)
        response = await client_with_auth.get(f"/api/presets/user/{preset_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["preset_id"] == preset_id
    
    @pytest.mark.asyncio
    async def test_update_preset_success(self, client_with_auth: AsyncClient, mock_auth_dependency, user_preset):
        """Test PUT /api/presets/user/{id} - Update preset."""
        preset_id = str(user_preset.id)
        update_data = {
            "name": "Updated Preset Name",
            "description": "Updated description"
        }
        
        response = await client_with_auth.put(
            f"/api/presets/user/{preset_id}",
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Preset Name"
        assert data["description"] == "Updated description"
    
    @pytest.mark.asyncio
    async def test_update_preset_validation_error(self, client_with_auth: AsyncClient, mock_auth_dependency, user_preset):
        """Test PUT /api/presets/user/{id} - Validation error."""
        preset_id = str(user_preset.id)
        update_data = {
            "name": "AB"  # Too short
        }
        
        response = await client_with_auth.put(
            f"/api/presets/user/{preset_id}",
            json=update_data
        )
        
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_delete_preset_success(self, client_with_auth: AsyncClient, mock_auth_dependency, user_preset):
        """Test DELETE /api/presets/user/{id} - Success."""
        preset_id = str(user_preset.id)
        response = await client_with_auth.delete(
            f"/api/presets/user/{preset_id}"
        )
        
        assert response.status_code == 204
        
        # Verify deletion
        verify_response = await client_with_auth.get(
            f"/api/presets/user/{preset_id}"
        )
        assert verify_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_preset_not_owner(self, client_with_auth: AsyncClient, user_preset, prepare_db):
        """Test DELETE /api/presets/user/{id} - Not owner."""
        # Create another user
        other_user = User(
            email="other@example.com",
            username="otheruser",
            hashed_password="hash",
            is_active=True
        )
        await other_user.insert()
        
        # Mock auth to return other_user
        from dmm_backend.dependencies import auth
        
        async def mock_other_user(credentials=None):
            return other_user
        
        import pytest
        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setattr(auth, "get_current_user", mock_other_user)
        
        preset_id = str(user_preset.id)
        
        response = await client_with_auth.delete(
            f"/api/presets/user/{preset_id}"
        )
        
        assert response.status_code == 403


# ============================================================================
# Favorite Toggle Tests
# ============================================================================

class TestFavoriteFeature:
    """Test suite for favorite toggle functionality."""
    
    @pytest.mark.asyncio
    async def test_toggle_favorite_add(self, client_with_auth: AsyncClient, mock_auth_dependency, user_preset):
        """Test POST /api/presets/user/{id}/favorite - Add to favorites."""
        preset_id = str(user_preset.id)
        response = await client_with_auth.post(
            f"/api/presets/user/{preset_id}/favorite"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_favorite"] is True
    
    @pytest.mark.asyncio
    async def test_toggle_favorite_remove(self, client_with_auth: AsyncClient, mock_auth_dependency, user_preset):
        """Test POST /api/presets/user/{id}/favorite - Remove from favorites."""
        # First add to favorites
        preset_id = str(user_preset.id)
        await client_with_auth.post(f"/api/presets/user/{preset_id}/favorite")
        
        # Then remove
        response = await client_with_auth.post(
            f"/api/presets/user/{preset_id}/favorite"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_favorite"] is False


# ============================================================================
# Duplicate Preset Tests
# ============================================================================

class TestDuplicatePreset:
    """Test suite for preset duplication."""
    
    @pytest.mark.asyncio
    async def test_duplicate_user_preset(self, client_with_auth: AsyncClient, mock_auth_dependency, user_preset, test_user):
        """Test POST /api/presets/user/{id}/duplicate - Duplicate user preset."""
        preset_id = str(user_preset.id)
        response = await client_with_auth.post(
            f"/api/presets/user/{preset_id}/duplicate"
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "Copy of" in data["name"]
        assert data["user_id"] == str(test_user.id)
        assert data["preset_id"] != preset_id  # Different ID
    
    @pytest.mark.asyncio
    async def test_duplicate_template(self, client_with_auth: AsyncClient, mock_auth_dependency, preset_template, test_user):
        """Test POST /api/presets/templates/{id}/duplicate - Duplicate template to user preset."""
        template_id = str(preset_template.id)
        response = await client_with_auth.post(
            f"/api/presets/templates/{template_id}/duplicate"
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == str(test_user.id)
        assert data["visibility"] == "private"  # User preset, not template


# ============================================================================
# Validation Unit Tests
# ============================================================================

class TestPresetValidation:
    """Test suite for PresetValidator utility."""
    
    def test_validate_name_valid(self):
        """Test name validation with valid input."""
        from dmm_backend.utils.preset_validators import PresetValidator
        
        # Should not raise exception
        PresetValidator.validate_preset_name("Valid Name")
        PresetValidator.validate_preset_name("Name-With_Underscores")
        PresetValidator.validate_preset_name("Name (With Parentheses)")
        PresetValidator.validate_preset_name("ชื่อภาษาไทย")
    
    def test_validate_name_too_short(self):
        """Test name validation with too short input."""
        from dmm_backend.utils.preset_validators import PresetValidator
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException) as exc_info:
            PresetValidator.validate_preset_name("AB")
        
        assert exc_info.value.status_code == 400
        assert "at least 3 characters" in str(exc_info.value.detail)
    
    def test_validate_name_too_long(self):
        """Test name validation with too long input."""
        from dmm_backend.utils.preset_validators import PresetValidator
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException) as exc_info:
            PresetValidator.validate_preset_name("x" * 101)
        
        assert exc_info.value.status_code == 400
        assert "exceed 100 characters" in str(exc_info.value.detail)
    
    def test_validate_name_invalid_chars(self):
        """Test name validation with invalid characters."""
        from dmm_backend.utils.preset_validators import PresetValidator
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException):
            PresetValidator.validate_preset_name("Name@Email")
        
        with pytest.raises(HTTPException):
            PresetValidator.validate_preset_name("Name$Money")
    
    def test_validate_parameter_range(self):
        """Test parameter validation for range type."""
        from dmm_backend.utils.preset_validators import PresetValidator
        
        valid_param = {
            "name": "brightness",
            "type": "range",
            "value": 50,
            "min_value": 0,
            "max_value": 100
        }
        
        # Should not raise
        PresetValidator.validate_parameter(valid_param, 1)
    
    def test_validate_parameter_select(self):
        """Test parameter validation for select type."""
        from dmm_backend.utils.preset_validators import PresetValidator
        
        valid_param = {
            "name": "shot_type",
            "type": "select",
            "value": "wide",
            "options": ["wide", "medium", "close"]
        }
        
        # Should not raise
        PresetValidator.validate_parameter(valid_param, 1)
    
    def test_validate_parameter_missing_name(self):
        """Test parameter validation with missing name."""
        from dmm_backend.utils.preset_validators import PresetValidator
        from fastapi import HTTPException
        
        invalid_param = {
            "type": "range",
            "value": 50
        }
        
        with pytest.raises(HTTPException) as exc_info:
            PresetValidator.validate_parameter(invalid_param, 1)
        
        assert "name is required" in str(exc_info.value.detail)


# ============================================================================
# Edge Cases and Error Handling Tests
# ============================================================================

class TestEdgeCases:
    """Test suite for edge cases and error scenarios."""
    
    @pytest.mark.asyncio
    async def test_create_preset_with_empty_name(self, client_with_auth: AsyncClient, mock_auth_dependency):
        """Test creating preset with empty name."""
        preset_data = {
            "name": "",
            "category": "lighting",
            "config": {"parameters": [{"name": "test", "type": "range", "value": 50}]}
        }
        
        response = await client_with_auth.post(
            "/api/presets/user",
            json=preset_data
        )
        
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_create_preset_with_whitespace_name(self, client_with_auth: AsyncClient, mock_auth_dependency):
        """Test creating preset with whitespace-only name."""
        preset_data = {
            "name": "   ",
            "category": "lighting",
            "config": {"parameters": [{"name": "test", "type": "range", "value": 50}]}
        }
        
        response = await client_with_auth.post(
            "/api/presets/user",
            json=preset_data
        )
        
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_get_preset_with_malformed_id(self, client_with_auth: AsyncClient, mock_auth_dependency):
        """Test getting preset with malformed ID."""
        response = await client_with_auth.get(
            "/api/presets/user/not-a-valid-id"
        )
        
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_update_nonexistent_preset(self, client_with_auth: AsyncClient, mock_auth_dependency):
        """Test updating non-existent preset."""
        fake_id = str(PydanticObjectId())
        update_data = {"name": "Updated Name"}
        
        response = await client_with_auth.put(
            f"/api/presets/user/{fake_id}",
            json=update_data
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_create_preset_with_no_parameters(self, client_with_auth: AsyncClient, mock_auth_dependency):
        """Test creating preset with no parameters."""
        preset_data = {
            "name": "Test Preset",
            "category": "lighting",
            "config": {"parameters": []}
        }
        
        response = await client_with_auth.post(
            "/api/presets/user",
            json=preset_data
        )
        
        assert response.status_code == 400
        assert "at least one parameter" in response.json()["detail"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
