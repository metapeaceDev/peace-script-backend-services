"""
Unit Tests for AI Image Generation Features
Tests LoRA management, image generation, gallery, and avatar endpoints.

Note: These tests are integration tests that require external dependencies.
They are skipped in unit test runs to maintain fast test execution.
Run with: pytest -m integration to include these tests.
"""

import pytest
from unittest.mock import patch, Mock, MagicMock
import base64


# Mark all tests in this module as integration tests
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skip(reason="Integration test - requires ComfyUI service and file system access")
]


class TestLoRAManagement:
    """Test GET /api/character/loras/available endpoint"""
    
    @pytest.mark.asyncio
    async def test_get_available_loras(self, async_client):
        """Test successful LoRA retrieval"""
        with patch('os.path.exists') as mock_exists, \
             patch('glob.glob') as mock_glob, \
             patch('os.path.getsize') as mock_getsize, \
             patch('os.getenv') as mock_getenv:
            
            # Setup mocks
            mock_getenv.return_value = "/fake/comfyui"
            mock_exists.return_value = True
            mock_glob.return_value = [
                "/fake/comfyui/models/loras/add_detail.safetensors",
                "/fake/comfyui/models/loras/style_enhance.safetensors"
            ]
            mock_getsize.side_effect = [36100000, 48500000]  # 36.1 MB, 48.5 MB
            
            # Make request
            response = await async_client.get("/api/character/loras/available")
            
            # Assertions
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["total_count"] == 2
            assert len(data["loras"]) == 2
            assert data["loras"][0]["name"] == "add_detail"
            assert data["loras"][1]["name"] == "style_enhance"
    
    @pytest.mark.asyncio
    async def test_get_loras_directory_not_exists(self, async_client):
        """Test when LoRA directory doesn't exist"""
        with patch('os.path.exists') as mock_exists, \
             patch('os.getenv') as mock_getenv:
            
            mock_getenv.return_value = "/fake/comfyui"
            mock_exists.return_value = False
            
            response = await async_client.get("/api/character/loras/available")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["total_count"] == 0
            assert len(data["loras"]) == 0


class TestImageGeneration:
    """Test POST /api/character/{model_id}/generate-image endpoint"""
    
    @pytest.mark.asyncio
    @patch('modules.comfyui_client.generate_with_comfyui')
    @patch('modules.comfyui_client.ComfyUIClient')
    async def test_generate_simple_image(self, mock_client_class, mock_generate, async_client):
        """Test basic image generation"""
        # Mock ComfyUI client
        mock_client = Mock()
        mock_client.check_health.return_value = True
        mock_client_class.return_value = mock_client
        
        # Mock ComfyUI response
        mock_image_bytes = b"fake_image_data" * 100
        mock_generate.return_value = mock_image_bytes
        
        # Request payload
        payload = {
            "style": "realistic",
            "num_variations": 1,
            "width": 512,
            "height": 512,
            "steps": 20,
            "cfg": 7.0
        }
        
        # Make request
        response = await async_client.post(
            "/api/character/test_model_001/generate-image",
            json=payload
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["images"]) == 1
        assert "image_base64" in data["images"][0]
        assert data["style"] == "realistic"
    
    @pytest.mark.asyncio
    @patch('modules.comfyui_client.batch_generate_with_comfyui')
    @patch('modules.comfyui_client.ComfyUIClient')
    async def test_generate_batch_images(self, mock_client_class, mock_batch, async_client):
        """Test batch image generation"""
        # Mock ComfyUI client
        mock_client = Mock()
        mock_client.check_health.return_value = True
        mock_client_class.return_value = mock_client
        
        # Mock batch response
        mock_batch.return_value = [
            b"image1_data" * 100,
            b"image2_data" * 100,
            b"image3_data" * 100
        ]
        
        # Request payload
        payload = {
            "style": "anime",
            "num_variations": 3,
            "width": 512,
            "height": 512,
            "steps": 20,
            "cfg": 7.0
        }
        
        # Make request
        response = await async_client.post(
            "/api/character/test_model_001/generate-image",
            json=payload
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["images"]) == 3
    
    @pytest.mark.asyncio
    async def test_generate_character_not_found(self, async_client):
        """Test generation with non-existent character"""
        payload = {
            "style": "realistic",
            "num_variations": 1
        }
        
        response = await async_client.post(
            "/api/character/nonexistent-id/generate-image",
            json=payload
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_generate_invalid_style(self, async_client):
        """Test generation with invalid style"""
        payload = {
            "style": "invalid_style",
            "num_variations": 1
        }
        
        response = await async_client.post(
            "/api/character/test_model_001/generate-image",
            json=payload
        )
        
        assert response.status_code == 422  # Validation error


class TestGalleryManagement:
    """Test gallery-related endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_generated_images_empty(self, async_client):
        """Test getting images from empty gallery"""
        response = await async_client.get(
            "/api/character/test_model_001/generated-images",
            params={"limit": 10, "skip": 0}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total_count"] == 0
        assert len(data["images"]) == 0
    
    @pytest.mark.asyncio
    async def test_save_generated_image(self, async_client):
        """Test saving generated image to gallery"""
        # Create test image data
        image_data = b"test_image_data" * 100
        image_base64 = base64.b64encode(image_data).decode()
        
        payload = {
            "image_base64": image_base64,
            "metadata": {
                "style": "realistic",
                "width": 512,
                "height": 512,
                "steps": 20,
                "cfg": 7.0,
                "seed": 12345678
            },
            "notes": "Test save"
        }
        
        response = await async_client.post(
            "/api/character/test_model_001/save-generated-image",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "saved_image_id" in data


class TestAvatarManagement:
    """Test PATCH /api/character/{model_id}/set-avatar endpoint"""
    
    @pytest.mark.asyncio
    async def test_set_avatar_image_not_found(self, async_client):
        """Test setting avatar with non-existent image"""
        payload = {"image_id": "nonexistent_image_id"}
        
        response = await async_client.patch(
            "/api/character/test_model_001/set-avatar",
            json=payload
        )
        
        assert response.status_code == 404


class TestWorkflowBuilder:
    """Test ComfyUI workflow building logic"""
    
    def test_create_basic_workflow(self):
        """Test basic workflow creation"""
        from modules.comfyui_client import WorkflowBuilder
        
        workflow = WorkflowBuilder.create_txt2img_workflow(
            prompt="test prompt",
            negative_prompt="test negative",
            width=512,
            height=512,
            steps=20,
            cfg=7.0,
            seed=12345
        )
        
        # Verify workflow structure
        assert isinstance(workflow, dict)
        assert "3" in workflow  # KSampler node
        assert "6" in workflow  # CLIP text encode positive
        assert workflow["3"]["inputs"]["seed"] == 12345
        assert workflow["6"]["inputs"]["text"] == "test prompt"
    
    def test_create_workflow_with_lora(self):
        """Test workflow with LoRA"""
        from modules.comfyui_client import WorkflowBuilder
        
        workflow = WorkflowBuilder.create_txt2img_workflow(
            prompt="portrait",
            negative_prompt="blurry",
            width=512,
            height=512,
            steps=20,
            cfg=7.0,
            seed=12345,
            lora_name="add_detail",
            lora_strength=1.0
        )
        
        # Verify LoRA loader exists
        assert "10" in workflow
        assert workflow["10"]["class_type"] == "LoraLoader"
        # ComfyUI uses full filename with extension
        assert "add_detail" in workflow["10"]["inputs"]["lora_name"]
        assert workflow["10"]["inputs"]["strength_model"] == 1.0


class TestInputValidation:
    """Test input validation for all endpoints"""
    
    @pytest.mark.asyncio
    async def test_generate_invalid_dimensions(self, async_client):
        """Test generation with invalid dimensions"""
        payload = {
            "style": "realistic",
            "num_variations": 1,
            "width": 2048,  # Too large
            "height": 512
        }
        
        response = await async_client.post(
            "/api/character/test_model_001/generate-image",
            json=payload
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_generate_invalid_variations(self, async_client):
        """Test generation with too many variations"""
        payload = {
            "style": "realistic",
            "num_variations": 10,  # Max is 4
            "width": 512,
            "height": 512
        }
        
        response = await async_client.post(
            "/api/character/test_model_001/generate-image",
            json=payload
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_save_invalid_base64(self, async_client):
        """Test saving with invalid base64 data"""
        payload = {
            "image_base64": "invalid_base64!!!",
            "metadata": {
                "style": "realistic",
                "width": 512,
                "height": 512
            }
        }
        
        response = await async_client.post(
            "/api/character/test_model_001/save-generated-image",
            json=payload
        )
        
        # Should either reject or handle gracefully
        assert response.status_code in [400, 422]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
