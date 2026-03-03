"""
Unit Tests for NarrativeStructure Models (Peace Script Integration - Week 1)

Tests all 6 models: Project, StoryScope, Character, Scene, Shot, Visual

Run tests:
    cd dmm_backend
    source ./venv/bin/activate
    pytest tests/test_narrative_models.py -v
    
Run specific test:
    pytest tests/test_narrative_models.py::TestProjectModel::test_create_project -v
"""

import pytest
from datetime import datetime
from documents_narrative import (
    Project,
    StoryScope,
    Character,
    Scene,
    Shot,
    Visual,
    GenreEnum,
    CharacterRole,
    ProjectStatus,
    VisualStatus
)


# ============================================================================
# Test Project Model
# ============================================================================

class TestProjectModel:
    """Test cases for Project model"""
    
    def test_create_project(self):
        """Test creating a valid Project instance"""
        project = Project(
            project_id="proj_test_001",
            script_name="เงาแค้น",
            genre=GenreEnum.DRAMA,
            studio="Peace Studio",
            writer="สมชาย ใจดี",
            language="th"
        )
        
        assert project.project_id == "proj_test_001"
        assert project.script_name == "เงาแค้น"
        assert project.genre == GenreEnum.DRAMA
        assert project.studio == "Peace Studio"
        assert project.writer == "สมชาย ใจดี"
        assert project.language == "th"
        assert project.status == ProjectStatus.DRAFT
        assert isinstance(project.created_at, datetime)
    
    def test_project_validation(self):
        """Test Project validation rules"""
        # Test empty script name
        with pytest.raises(ValueError, match="Script name cannot be empty"):
            Project(
                project_id="proj_test_002",
                script_name="   ",  # Only whitespace
                genre=GenreEnum.DRAMA,
                studio="Peace Studio",
                writer="Test Writer"
            )
    
    def test_project_repr(self):
        """Test Project __repr__ and __str__"""
        project = Project(
            project_id="proj_test_003",
            script_name="Test Script",
            genre=GenreEnum.COMEDY,
            studio="Test Studio",
            writer="Test Writer"
        )
        
        assert "Test Script" in repr(project)
        assert "comedy" in repr(project)
        assert "Test Writer" in str(project)


# ============================================================================
# Test StoryScope Model
# ============================================================================

class TestStoryScopeModel:
    """Test cases for StoryScope model"""
    
    def test_create_story_scope(self):
        """Test creating a valid StoryScope instance"""
        scope = StoryScope(
            scope_id="scope_test_001",
            project_id="proj_test_001",
            big_idea="A woman's quest for revenge becomes a journey of redemption",
            theme="Revenge and forgiveness",
            premise="After her family is killed, Rinrada seeks revenge but finds redemption",
            timeline_start="January 2024",
            timeline_end="December 2024",
            timeline_duration="1 year"
        )
        
        assert scope.scope_id == "scope_test_001"
        assert scope.project_id == "proj_test_001"
        assert "revenge" in scope.big_idea.lower()
        assert scope.timeline_duration == "1 year"
        assert scope.tone == "balanced"  # Default value
    
    def test_story_scope_custom_tone(self):
        """Test StoryScope with custom tone"""
        scope = StoryScope(
            scope_id="scope_test_002",
            project_id="proj_test_001",
            big_idea="A dark tale of vengeance",
            theme="Darkness",
            premise="Test premise",
            timeline_start="Now",
            timeline_end="Later",
            timeline_duration="6 months",
            tone="dark"
        )
        
        assert scope.tone == "dark"


# ============================================================================
# Test Character Model
# ============================================================================

class TestCharacterModel:
    """Test cases for Character model"""
    
    def test_create_character(self):
        """Test creating a valid Character instance"""
        character = Character(
            project_id="proj_test_001",
            name="รินรดา สมพงษ์",
            role=CharacterRole.PROTAGONIST,
            age=28,
            gender="female",
            personality="Strong-willed, haunted by past trauma",
            appearance="Tall with dark hair, intense eyes that reflect inner turmoil"
        )
        
        assert character.name == "รินรดา สมพงษ์"
        assert character.role == CharacterRole.PROTAGONIST
        assert character.age == 28
        assert character.gender == "female"
        assert len(character.narrative_function) == 0  # Default empty list
    
    def test_character_age_validation(self):
        """Test Character age validation (0-120)"""
        # Valid age
        char1 = Character(
            project_id="proj_test_001",
            name="Test Character",
            role=CharacterRole.SUPPORT,
            age=50,
            gender="male",
            personality="Test personality description here",
            appearance="Test appearance description here"
        )
        assert char1.age == 50
        
        # Invalid age (negative)
        with pytest.raises(ValueError):
            Character(
                project_id="proj_test_001",
                name="Test Character",
                role=CharacterRole.SUPPORT,
                age=-5,  # Invalid
                gender="male",
                personality="Test personality",
                appearance="Test appearance"
            )
        
        # Invalid age (too high)
        with pytest.raises(ValueError):
            Character(
                project_id="proj_test_001",
                name="Test Character",
                role=CharacterRole.SUPPORT,
                age=150,  # Invalid
                gender="male",
                personality="Test personality",
                appearance="Test appearance"
            )
    
    def test_character_roles(self):
        """Test all CharacterRole enum values"""
        roles = [
            CharacterRole.PROTAGONIST,
            CharacterRole.ANTAGONIST,
            CharacterRole.MAIN,
            CharacterRole.SUPPORT,
            CharacterRole.EXTRA
        ]
        
        for i, role in enumerate(roles):
            char = Character(
                project_id="proj_test_001",
                name=f"Test Character {i}",
                role=role,
                age=30,
                gender="other",
                personality="Test personality",
                appearance="Test appearance"
            )
            assert char.role == role


# ============================================================================
# Test Scene Model
# ============================================================================

class TestSceneModel:
    """Test cases for Scene model"""
    
    def test_create_scene(self):
        """Test creating a valid Scene instance"""
        scene = Scene(
            project_id="proj_test_001",
            scene_number=1,
            point_number=1,
            chapter_number=1,
            title="Opening Scene - The Letter",
            description="Rinrada receives a mysterious letter that changes her life forever",
            location="Rinrada's apartment",
            time_of_day="night",
            characters=["char_test_001"]
        )
        
        assert scene.scene_number == 1
        assert scene.point_number == 1
        assert scene.chapter_number == 1
        assert scene.title == "Opening Scene - The Letter"
        assert scene.time_of_day == "night"
        assert len(scene.characters) == 1
    
    def test_scene_save_the_cat_structure(self):
        """Test Scene with Save the Cat 15-Point structure"""
        # Point 1: Opening Scene
        scene1 = Scene(
            project_id="proj_test_001",
            scene_number=1,
            point_number=1,
            chapter_number=1,
            title="Opening Image",
            description="Before snapshot",
            location="Home",
            characters=[]
        )
        assert scene1.point_number == 1
        
        # Point 8: Midpoint (middle of 15 points)
        scene8 = Scene(
            project_id="proj_test_001",
            scene_number=23,
            point_number=8,
            chapter_number=2,
            title="Midpoint",
            description="False victory or defeat",
            location="Unknown",
            characters=[]
        )
        assert scene8.point_number == 8
        assert scene8.chapter_number == 2
        
        # Point 15: Final Image
        scene15 = Scene(
            project_id="proj_test_001",
            scene_number=45,
            point_number=15,
            chapter_number=3,
            title="Final Image",
            description="After snapshot",
            location="Home",
            characters=[]
        )
        assert scene15.point_number == 15
        assert scene15.chapter_number == 3


# ============================================================================
# Test Shot Model
# ============================================================================

class TestShotModel:
    """Test cases for Shot model"""
    
    def test_create_shot(self):
        """Test creating a valid Shot instance"""
        shot = Shot(
            scene_id="scene_test_001",
            project_id="proj_test_001",
            shot_number=1,
            shot_title="Opening Wide Shot",
            shot_description="Wide shot of old mansion exterior at night, moonlight casting long shadows",
            camera_angle="wide",
            camera_movement="static",
            lens_type="wide",
            lighting_type="low-key",
            lighting_time="night",
            motion_parameters={
                "zoom_start": 1.0,
                "zoom_end": 1.5,
                "move_x": 10,
                "move_y": 0,
                "rotate_start": 0,
                "rotate_end": 0,
                "duration": 3,
                "speed": 1.0
            },
            duration_seconds=3
        )
        
        assert shot.scene_id == "scene_test_001"
        assert shot.shot_number == 1
        assert shot.shot_title == "Opening Wide Shot"
        assert shot.camera_angle == "wide"
        assert shot.duration_seconds == 3
        
        # Test motion parameters
        assert shot.motion_parameters["zoom_start"] == 1.0
        assert shot.motion_parameters["zoom_end"] == 1.5
        assert shot.motion_parameters["move_x"] == 10
        assert shot.motion_parameters["duration"] == 3
    
    def test_shot_default_motion_parameters(self):
        """Test Shot with default motion parameters"""
        shot = Shot(
            scene_id="scene_test_001",
            project_id="proj_test_001",
            shot_number=2,
            shot_title="Medium Character Shot",
            shot_description="Medium shot of character face",
            camera_angle="medium",
            camera_movement="static",
            lens_type="standard",
            lighting_type="three-point",
            lighting_time="day",
            duration_seconds=3
        )
        
        # Should have default motion parameters
        assert shot.motion_parameters["zoom_start"] == 1.0
        assert shot.motion_parameters["zoom_end"] == 1.0
        assert shot.motion_parameters["move_x"] == 0
        assert shot.motion_parameters["move_y"] == 0
        assert shot.motion_parameters["rotate_start"] == 0
        assert shot.motion_parameters["rotate_end"] == 0
        assert shot.motion_parameters["duration"] == 3
        assert shot.motion_parameters["speed"] == 1.0
    
    def test_shot_motion_effects(self):
        """Test various motion effects"""
        # Zoom in effect
        shot_zoom = Shot(
            scene_id="scene_test_001",
            project_id="proj_test_001",
            shot_number=1,
            shot_title="Zoom Shot",
            shot_description="Zoom into character eyes",
            camera_angle="close-up",
            camera_movement="zoom",
            lens_type="telephoto",
            lighting_type="natural",
            lighting_time="day",
            duration_seconds=4,
            motion_parameters={
                "zoom_start": 1.0,
                "zoom_end": 2.5,
                "move_x": 0,
                "move_y": 0,
                "rotate_start": 0,
                "rotate_end": 0,
                "duration": 4,
                "speed": 1.0
            }
        )
        assert shot_zoom.motion_parameters["zoom_end"] > shot_zoom.motion_parameters["zoom_start"]
        
        # Pan effect (horizontal movement)
        shot_pan = Shot(
            scene_id="scene_test_001",
            project_id="proj_test_001",
            shot_number=2,
            shot_title="Pan Shot",
            shot_description="Pan across room",
            camera_angle="eye-level",
            camera_movement="pan",
            lens_type="wide",
            lighting_type="natural",
            lighting_time="day",
            duration_seconds=5,
            motion_parameters={
                "zoom_start": 1.0,
                "zoom_end": 1.0,
                "move_x": 100,
                "move_y": 0,
                "rotate_start": 0,
                "rotate_end": 0,
                "duration": 5,
                "speed": 1.0
            }
        )
        assert shot_pan.motion_parameters["move_x"] != 0
        
        # Rotation effect
        shot_rotate = Shot(
            scene_id="scene_test_001",
            project_id="proj_test_001",
            shot_number=3,
            shot_title="Rotating Shot",
            shot_description="Rotating shot",
            camera_angle="dutch",
            camera_movement="static",
            lens_type="standard",
            lighting_type="dramatic",
            lighting_time="evening",
            duration_seconds=6,
            motion_parameters={
                "zoom_start": 1.0,
                "zoom_end": 1.0,
                "move_x": 0,
                "move_y": 0,
                "rotate_start": 0,
                "rotate_end": 45,
                "duration": 3,
                "speed": 1.0
            }
        )
        assert shot_rotate.motion_parameters["rotate_end"] != 0


# ============================================================================
# Test Visual Model
# ============================================================================

class TestVisualModel:
    """Test cases for Visual model"""
    
    def test_create_visual_pending(self):
        """Test creating a Visual in pending status"""
        visual = Visual(
            shot_id="shot_test_001",
            project_id="proj_test_001",
            image_prompt="A dark mansion at night, cinematic lighting, 4K quality",
            generation_provider="stable-diffusion",
            status=VisualStatus.PENDING
        )
        
        assert visual.shot_id == "shot_test_001"
        assert visual.status == VisualStatus.PENDING
        assert visual.generation_provider == "stable-diffusion"
        assert visual.image_url is None  # Not generated yet
        assert visual.video_url is None
    
    def test_visual_complete_status(self):
        """Test Visual with complete status and URLs"""
        visual = Visual(
            shot_id="shot_test_001",
            project_id="proj_test_001",
            image_prompt="Test prompt",
            generation_provider="stable-diffusion",
            status=VisualStatus.COMPLETE,
            image_url="https://storage.example.com/images/shot_001.png",
            video_url="https://storage.example.com/videos/shot_001.mp4",
            generated_at=datetime.utcnow()
        )
        
        assert visual.status == VisualStatus.COMPLETE
        assert visual.image_url is not None
        assert visual.video_url is not None
        assert visual.generated_at is not None
    
    def test_visual_failed_status(self):
        """Test Visual with failed status"""
        visual = Visual(
            shot_id="shot_test_001",
            project_id="proj_test_001",
            image_prompt="Test prompt",
            generation_provider="dalle",
            status=VisualStatus.FAILED,
            error_message="API timeout after 30 seconds"
        )
        
        assert visual.status == VisualStatus.FAILED
        assert visual.error_message is not None
        assert "timeout" in visual.error_message.lower()
    
    def test_visual_generation_providers(self):
        """Test different AI generation providers"""
        providers = ["stable-diffusion", "dalle", "midjourney", "runwayml"]
        
        for provider in providers:
            visual = Visual(
                shot_id="shot_test_001",
                project_id="proj_test_001",
                image_prompt="Test prompt",
                generation_provider=provider
            )
            assert visual.generation_provider == provider


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
