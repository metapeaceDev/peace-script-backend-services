#!/usr/bin/env python3
"""
Quick Test Script for NarrativeStructure Models

Run this to verify all 6 models work correctly:
    cd dmm_backend
    source ./venv/bin/activate
    python test_models_quick.py
"""

import sys
from datetime import datetime

def test_imports():
    """Test 1: Import all models"""
    print("=" * 60)
    print("TEST 1: Importing all NarrativeStructure models...")
    print("=" * 60)
    
    try:
        from documents_narrative import (
            Project, StoryScope, Character, Scene, Shot, Visual,
            GenreEnum, CharacterRole, ProjectStatus, VisualStatus
        )
        print("✅ SUCCESS: All imports successful!")
        print(f"   - Project: {Project}")
        print(f"   - StoryScope: {StoryScope}")
        print(f"   - Character: {Character}")
        print(f"   - Scene: {Scene}")
        print(f"   - Shot: {Shot}")
        print(f"   - Visual: {Visual}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_project_creation():
    """Test 2: Create Project instance"""
    print("\n" + "=" * 60)
    print("TEST 2: Creating Project instance...")
    print("=" * 60)
    
    try:
        from documents_narrative import Project, GenreEnum
        
        project = Project(
            project_id="proj_test_001",
            script_name="เงาแค้น",
            genre=GenreEnum.DRAMA,
            studio="Peace Studio",
            writer="สมชาย ใจดี",
            language="th"
        )
        
        print("✅ SUCCESS: Project created!")
        print(f"   ID: {project.project_id}")
        print(f"   Name: {project.script_name}")
        print(f"   Genre: {project.genre.value}")
        print(f"   Studio: {project.studio}")
        print(f"   Writer: {project.writer}")
        print(f"   Status: {project.status.value}")
        print(f"   Created: {project.created_at}")
        print(f"   __repr__: {repr(project)}")
        print(f"   __str__: {str(project)}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_character_creation():
    """Test 3: Create Character instance"""
    print("\n" + "=" * 60)
    print("TEST 3: Creating Character instance...")
    print("=" * 60)
    
    try:
        from documents_narrative import Character, CharacterRole
        
        character = Character(
            character_id="char_test_001",
            project_id="proj_test_001",
            full_name="รินรดา สมพงษ์",
            role=CharacterRole.PROTAGONIST,
            age=28,
            gender="female",
            personality="Strong-willed, haunted by past trauma",
            appearance_description="Tall with dark hair, intense eyes"
        )
        
        print("✅ SUCCESS: Character created!")
        print(f"   ID: {character.character_id}")
        print(f"   Name: {character.full_name}")
        print(f"   Role: {character.role.value}")
        print(f"   Age: {character.age}")
        print(f"   Gender: {character.gender}")
        print(f"   __repr__: {repr(character)}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_shot_with_motion():
    """Test 4: Create Shot with motion parameters"""
    print("\n" + "=" * 60)
    print("TEST 4: Creating Shot with motion parameters...")
    print("=" * 60)
    
    try:
        from documents_narrative import Shot
        
        shot = Shot(
            shot_id="shot_test_001",
            scene_id="scene_test_001",
            project_id="proj_test_001",
            shot_number=1,
            image_description="Wide shot of old mansion at night",
            camera_angle="wide",
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
        
        print("✅ SUCCESS: Shot created with motion parameters!")
        print(f"   ID: {shot.shot_id}")
        print(f"   Shot Number: {shot.shot_number}")
        print(f"   Description: {shot.image_description}")
        print(f"   Camera Angle: {shot.camera_angle}")
        print(f"   Duration: {shot.duration_seconds}s")
        print(f"   Motion Parameters:")
        for key, value in shot.motion_parameters.items():
            print(f"      {key}: {value}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_visual_status():
    """Test 5: Create Visual with different statuses"""
    print("\n" + "=" * 60)
    print("TEST 5: Creating Visual instances with different statuses...")
    print("=" * 60)
    
    try:
        from documents_narrative import Visual, VisualStatus
        
        # Pending status
        visual_pending = Visual(
            visual_id="visual_test_001",
            shot_id="shot_test_001",
            project_id="proj_test_001",
            image_prompt="Dark mansion at night, cinematic",
            generation_provider="stable-diffusion",
            status=VisualStatus.PENDING
        )
        
        # Complete status
        visual_complete = Visual(
            visual_id="visual_test_002",
            shot_id="shot_test_002",
            project_id="proj_test_001",
            image_prompt="Test prompt",
            generation_provider="dalle",
            status=VisualStatus.COMPLETE,
            image_url="https://example.com/image.png",
            video_url="https://example.com/video.mp4"
        )
        
        print("✅ SUCCESS: Visual instances created!")
        print(f"   Pending Visual: {visual_pending.visual_id} - {visual_pending.status.value}")
        print(f"   Complete Visual: {visual_complete.visual_id} - {visual_complete.status.value}")
        print(f"      Image URL: {visual_complete.image_url}")
        print(f"      Video URL: {visual_complete.video_url}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_all_enums():
    """Test 6: Verify all enum values"""
    print("\n" + "=" * 60)
    print("TEST 6: Verifying all enum values...")
    print("=" * 60)
    
    try:
        from documents_narrative import GenreEnum, CharacterRole, ProjectStatus, VisualStatus
        
        print("✅ SUCCESS: All enums verified!")
        
        print("\n   GenreEnum values:")
        for genre in GenreEnum:
            print(f"      - {genre.value}")
        
        print("\n   CharacterRole values:")
        for role in CharacterRole:
            print(f"      - {role.value}")
        
        print("\n   ProjectStatus values:")
        for status in ProjectStatus:
            print(f"      - {status.value}")
        
        print("\n   VisualStatus values:")
        for status in VisualStatus:
            print(f"      - {status.value}")
        
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🧪 NARRATIVESTRUCTURE MODELS - QUICK TEST SUITE")
    print("   Peace Script Integration - Week 1")
    print("=" * 60 + "\n")
    
    tests = [
        test_imports,
        test_project_creation,
        test_character_creation,
        test_shot_with_motion,
        test_visual_status,
        test_all_enums
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"   Passed: {passed}/{total}")
    print(f"   Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED! Models are working correctly! 🎉")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED. Please check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
