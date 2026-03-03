# Backend API Integration Tests for Dhamma Theme System
# Tests all 6 theme endpoints with 200 themes
# Validates performance, data integrity, and business logic

import pytest
import json
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the application
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app
from fastapi.testclient import TestClient

# Initialize test client
client = TestClient(app)

# ============================================================================
# FIXTURES & SETUP
# ============================================================================

@pytest.fixture
def themes_data():
    """Load themes from database"""
    db_path = Path(__file__).parent.parent.parent / "definitions" / "dhamma_themes.json"
    with open(db_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("dhamma_themes", {})


# ============================================================================
# TEST GROUP 1: Theme Loading & Basic Functionality
# ============================================================================

class TestThemeLoading:
    """Test theme loading and retrieval"""
    
    def test_get_all_themes(self):
        """Test GET /api/dhamma/themes - Retrieve all 200 themes"""
        response = client.get("/api/dhamma/themes")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Verify structure
        assert "themes" in data, "Response should contain 'themes' key"
        assert "total_count" in data, "Response should contain 'total_count' key"
        
        # Verify count
        assert data["total_count"] == 200, f"Expected 200 themes, got {data['total_count']}"
        assert len(data["themes"]) == 200, f"Expected 200 theme objects, got {len(data['themes'])}"
        
        print(f"PASS: GET /api/dhamma/themes - All {data['total_count']} themes loaded")
    
    
    def test_get_theme_by_id(self):
        """Test GET /api/dhamma/themes/{id} - Retrieve specific theme"""
        theme_id = "THEME_METTA_COMPASSION"
        response = client.get(f"/api/dhamma/themes/{theme_id}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        theme = response.json()
        
        # Verify theme structure
        assert theme["id"] == theme_id
        assert "thai_name" in theme
        assert "pali_name" in theme
        assert "category" in theme
        assert "core_principles" in theme
        assert "recommended_sub_themes" in theme
        assert "story_guidelines" in theme
        
        print(f"PASS: GET /api/dhamma/themes/{theme_id} - Theme retrieved successfully")
    
    
    def test_get_nonexistent_theme(self):
        """Test GET with invalid theme ID"""
        theme_id = "THEME_INVALID_NONEXISTENT"
        response = client.get(f"/api/dhamma/themes/{theme_id}")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"PASS: GET /api/dhamma/themes/{theme_id} - Correctly returns 404")


# ============================================================================
# TEST GROUP 2: Sub-Theme Recommendations
# ============================================================================

class TestSubThemeRecommendations:
    """Test sub-theme recommendation logic"""
    
    def test_sub_themes_exist(self):
        """Test that all themes have recommended sub-themes"""
        response = client.get("/api/dhamma/themes")
        assert response.status_code == 200
        
        themes = response.json()["themes"]
        orphaned_themes = []
        
        for theme in themes:
            sub_themes = theme.get("recommended_sub_themes", [])
            if not sub_themes or len(sub_themes) == 0:
                orphaned_themes.append(theme["id"])
        
        assert len(orphaned_themes) == 0, f"Found {len(orphaned_themes)} themes without sub-themes: {orphaned_themes}"
        print(f"PASS: All {len(themes)} themes have recommended sub-themes")
    
    
    def test_sub_theme_validity(self):
        """Test that all recommended sub-themes exist in database"""
        response = client.get("/api/dhamma/themes")
        assert response.status_code == 200
        
        themes = response.json()["themes"]
        theme_ids = {t["id"] for t in themes}
        
        invalid_refs = []
        total_refs = 0
        
        for theme in themes:
            for sub_id in theme.get("recommended_sub_themes", []):
                total_refs += 1
                if sub_id not in theme_ids:
                    invalid_refs.append({
                        "parent": theme["id"],
                        "invalid_sub": sub_id
                    })
        
        assert len(invalid_refs) == 0, f"Found {len(invalid_refs)} invalid sub-theme references"
        print(f"PASS: Verified {total_refs} sub-theme references - All valid")
    
    
    def test_no_circular_dependencies(self):
        """Test that theme relationships don't create circular dependencies"""
        response = client.get("/api/dhamma/themes")
        assert response.status_code == 200
        
        themes_by_id = {t["id"]: t for t in response.json()["themes"]}
        
        def has_circular_dependency(theme_id, visited=None):
            if visited is None:
                visited = set()
            
            if theme_id in visited:
                return True
            
            visited.add(theme_id)
            theme = themes_by_id.get(theme_id)
            
            if theme:
                for sub_id in theme.get("recommended_sub_themes", []):
                    if has_circular_dependency(sub_id, visited.copy()):
                        return True
            
            return False
        
        circular_themes = []
        for theme_id in themes_by_id.keys():
            if has_circular_dependency(theme_id):
                circular_themes.append(theme_id)
        
        assert len(circular_themes) == 0, f"Found circular dependencies in: {circular_themes}"
        print(f"PASS: No circular dependencies found in {len(themes_by_id)} themes")


# ============================================================================
# TEST GROUP 3: Story Guidelines Completeness
# ============================================================================

class TestStoryGuidelines:
    """Test story guidelines for all themes"""
    
    def test_story_guidelines_completeness(self):
        """Test that all themes have complete story guidelines"""
        response = client.get("/api/dhamma/themes")
        assert response.status_code == 200
        
        themes = response.json()["themes"]
        required_fields = ["theme_stated", "b_story", "break_into_three", "finale"]
        incomplete_themes = []
        
        for theme in themes:
            sg = theme.get("story_guidelines", {})
            missing_fields = [f for f in required_fields if not sg.get(f)]
            
            if missing_fields:
                incomplete_themes.append({
                    "id": theme["id"],
                    "missing": missing_fields
                })
        
        assert len(incomplete_themes) == 0, f"Found {len(incomplete_themes)} themes with incomplete story guidelines"
        print(f"PASS: All {len(themes)} themes have complete story guidelines")
    
    
    def test_story_guidelines_non_empty(self):
        """Test that story guidelines contain actual content"""
        response = client.get("/api/dhamma/themes")
        assert response.status_code == 200
        
        themes = response.json()["themes"]
        empty_guidelines = []
        
        for theme in themes:
            sg = theme.get("story_guidelines", {})
            for field in ["theme_stated", "b_story", "break_into_three", "finale"]:
                if not sg.get(field) or len(str(sg.get(field)).strip()) == 0:
                    empty_guidelines.append({
                        "id": theme["id"],
                        "field": field
                    })
        
        assert len(empty_guidelines) == 0, f"Found {len(empty_guidelines)} empty story guideline fields"
        print(f"PASS: All story guideline fields have meaningful content")


# ============================================================================
# TEST GROUP 4: Data Integrity & Validation
# ============================================================================

class TestDataIntegrity:
    """Test data integrity and validation rules"""
    
    def test_all_required_fields_present(self):
        """Test that all themes have required fields"""
        response = client.get("/api/dhamma/themes")
        assert response.status_code == 200
        
        themes = response.json()["themes"]
        required_fields = [
            "id", "thai_name", "pali_name", "category", "description",
            "core_principles", "recommended_sub_themes", "story_guidelines",
            "validation_rules"
        ]
        
        invalid_themes = []
        
        for theme in themes:
            missing = [f for f in required_fields if f not in theme]
            if missing:
                invalid_themes.append({
                    "id": theme["id"],
                    "missing_fields": missing
                })
        
        assert len(invalid_themes) == 0, f"Found {len(invalid_themes)} themes with missing fields"
        print(f"PASS: All {len(themes)} themes have all required fields")
    
    
    def test_core_principles_non_empty(self):
        """Test that all themes have core principles"""
        response = client.get("/api/dhamma/themes")
        assert response.status_code == 200
        
        themes = response.json()["themes"]
        invalid_themes = []
        
        for theme in themes:
            principles = theme.get("core_principles", [])
            if not principles or len(principles) == 0:
                invalid_themes.append(theme["id"])
        
        assert len(invalid_themes) == 0, f"Found {len(invalid_themes)} themes without core principles"
        print(f"PASS: All {len(themes)} themes have core principles")
    
    
    def test_validation_rules_exist(self):
        """Test that all themes have validation rules"""
        response = client.get("/api/dhamma/themes")
        assert response.status_code == 200
        
        themes = response.json()["themes"]
        invalid_themes = []
        
        for theme in themes:
            rules = theme.get("validation_rules", [])
            if not rules or len(rules) == 0:
                invalid_themes.append(theme["id"])
        
        assert len(invalid_themes) == 0, f"Found {len(invalid_themes)} themes without validation rules"
        print(f"PASS: All {len(themes)} themes have validation rules")


# ============================================================================
# TEST GROUP 5: Performance & Load Testing
# ============================================================================

class TestPerformance:
    """Test performance and load characteristics"""
    
    def test_theme_loading_performance(self):
        """Test that loading all themes is fast (<2 seconds)"""
        start_time = time.time()
        response = client.get("/api/dhamma/themes")
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed < 2.0, f"Theme loading took {elapsed:.2f}s, expected <2s"
        
        print(f"PASS: Theme loading completed in {elapsed:.3f}s (target: <2s)")
    
    
    def test_single_theme_retrieval_performance(self):
        """Test that retrieving a single theme is very fast (<100ms)"""
        start_time = time.time()
        response = client.get("/api/dhamma/themes/THEME_METTA_COMPASSION")
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed < 0.1, f"Single theme retrieval took {elapsed:.3f}s, expected <0.1s"
        
        print(f"PASS: Single theme retrieval completed in {elapsed:.3f}s (target: <100ms)")
    
    
    def test_response_payload_size(self):
        """Test that response payload is reasonable"""
        response = client.get("/api/dhamma/themes")
        assert response.status_code == 200
        
        payload_size = len(response.content)
        size_mb = payload_size / (1024 * 1024)
        
        # Should be less than 2MB for 200 themes
        assert payload_size < 2 * 1024 * 1024, f"Payload size is {size_mb:.2f}MB, expected <2MB"
        
        print(f"PASS: Response payload size: {size_mb:.2f}MB (target: <2MB)")


if __name__ == "__main__":
    # Run with: pytest test_theme_api_integration.py -v
    pytest.main([__file__, "-v", "--tb=short"])
