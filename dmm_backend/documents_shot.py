"""
Shot Document Models for MongoDB (Beanie ODM)

This module contains MongoDB document models for shot-level storyboard data.
Integrates with Peace Script narrative system.

Author: Peace Script Team
Date: 25 November 2025
Version: 1.0
"""

from beanie import Document
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# =============================================================================
# ENUMS (matching schemas_shot.py)
# =============================================================================

class ShotType(str, Enum):
    """Camera shot types"""
    EXTREME_CLOSE_UP = "extreme_close_up"
    CLOSE_UP = "close_up"
    MEDIUM = "medium"
    MEDIUM_WIDE = "medium_wide"
    WIDE = "wide"
    EXTREME_WIDE = "extreme_wide"
    OVERHEAD = "overhead"
    BIRDS_EYE = "birds_eye"
    WORMS_EYE = "worms_eye"


class CameraAngle(str, Enum):
    """Camera angles"""
    EYE_LEVEL = "eye_level"
    HIGH = "high"
    LOW = "low"
    DUTCH = "dutch"
    OVER_SHOULDER = "over_shoulder"


class CameraMovement(str, Enum):
    """Camera movement types"""
    STATIC = "static"
    PAN_LEFT = "pan_left"
    PAN_RIGHT = "pan_right"
    TILT_UP = "tilt_up"
    TILT_DOWN = "tilt_down"
    DOLLY_IN = "dolly_in"
    DOLLY_OUT = "dolly_out"
    TRACKING = "tracking"
    CRANE = "crane"
    HANDHELD = "handheld"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"


class ShotStatus(str, Enum):
    """Shot generation/rendering status"""
    DRAFT = "draft"
    GENERATING = "generating"
    GENERATED = "generated"
    RENDERING = "rendering"
    COMPLETED = "completed"
    FAILED = "failed"


# =============================================================================
# EMBEDDED MODELS
# =============================================================================

class CameraSettings(BaseModel):
    """Camera configuration embedded in shot"""
    shot_type: ShotType = ShotType.MEDIUM
    angle: CameraAngle = CameraAngle.EYE_LEVEL
    movement: CameraMovement = CameraMovement.STATIC
    focal_length: Optional[int] = Field(None, ge=10, le=200)
    aperture: Optional[str] = None


class MotionParameters(BaseModel):
    """Motion parameters for video generation"""
    zoom_start: float = 1.0
    zoom_end: float = 1.0
    move_x: float = 0.0
    move_y: float = 0.0
    rotate_start: float = 0.0
    rotate_end: float = 0.0
    duration: int = 3
    speed: float = 1.0


class LocationTag(BaseModel):
    """Location tag"""
    tag_id: str
    name: str
    description: Optional[str] = None
    environment: Optional[str] = None
    social_context: Optional[str] = None


class StyleTag(BaseModel):
    """Visual style tag"""
    tag_id: str
    name: str
    description: Optional[str] = None
    genre_based: bool = True
    custom_prompt_additions: Optional[str] = None


# =============================================================================
# MAIN DOCUMENT
# =============================================================================

class Shot(Document):
    """
    Shot Document - Individual shot within a scene
    
    Represents a single shot in the storyboard with camera settings,
    generated visuals, and motion parameters for video generation.
    """
    
    # Identifiers
    shot_id: str = Field(..., description="Unique shot identifier (e.g., shot_xxx)")
    scene_id: str = Field(..., description="Parent scene ID")
    project_id: str = Field(..., description="Parent project ID")
    
    # Shot Info
    shot_number: int = Field(..., ge=1, description="Shot number within scene")
    
    # Descriptions
    caption: Optional[str] = Field(None, max_length=500, description="Short caption (@Maria walks...)")
    shot_description: Optional[str] = Field(None, max_length=2000, description="Detailed description")
    
    # Camera
    camera: Optional[CameraSettings] = None
    
    # Generated Assets
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    
    # Motion
    motion_parameters: Optional[MotionParameters] = None
    
    # AI Generation
    prompt: Optional[str] = Field(None, max_length=2000)
    negative_prompt: Optional[str] = Field(None, max_length=1000)
    
    # Status
    status: ShotStatus = ShotStatus.DRAFT
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Generation Info
    generation_timestamp: Optional[datetime] = None
    generation_model: Optional[str] = None  # e.g., "stable-diffusion-xl", "comfyui"
    generation_params: Optional[Dict[str, Any]] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "shots"
        indexes = [
            "shot_id",
            "scene_id",
            "project_id",
            [("scene_id", 1), ("shot_number", 1)],  # Compound index for ordering
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "shot_id": "shot_1732570800000_a1b2c3",
                "scene_id": "scene_1732570800000_x1y2z3",
                "project_id": "proj_001",
                "shot_number": 1,
                "caption": "@Maria walks through the meadow",
                "shot_description": "Wide shot of Maria walking in golden meadow at sunset",
                "camera": {
                    "shot_type": "wide",
                    "angle": "eye_level",
                    "movement": "tracking",
                    "focal_length": 35,
                    "aperture": "f/2.8"
                },
                "image_url": "/api/shots/images/shot_xxx.jpg",
                "prompt": "Wide cinematic shot, woman walking in meadow, golden hour",
                "status": "generated"
            }
        }


class SceneGroup(Document):
    """
    Scene Group Document - Grouping of scenes with common location/style
    
    LTX Studio-inspired organization where multiple scenes share
    location and visual style tags.
    """
    
    # Identifiers
    group_id: str = Field(..., description="Unique group identifier")
    project_id: str = Field(..., description="Parent project ID")
    
    # Group Info
    title: str = Field(..., max_length=200, description="Group title")
    description: Optional[str] = Field(None, max_length=1000)
    
    # Tags
    location_tags: List[LocationTag] = Field(default_factory=list)
    style_tags: List[StyleTag] = Field(default_factory=list)
    
    # Narrative Structure Reference
    beat_id: Optional[str] = None  # From Step 4 structure
    chapter_number: Optional[int] = Field(None, ge=1, le=3)
    
    # Scene References
    scene_ids: List[str] = Field(default_factory=list, description="Scene IDs in this group")
    
    # Stats
    total_shots: int = Field(default=0, ge=0)
    total_scenes: int = Field(default=0, ge=0)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "scene_groups"
        indexes = [
            "group_id",
            "project_id",
            "beat_id",
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "group_id": "group_departure",
                "project_id": "proj_001",
                "title": "Departure from home",
                "description": "Thomas bids farewell marking the start of his journey",
                "location_tags": [
                    {
                        "tag_id": "loc_hillside",
                        "name": "Rural Hillside",
                        "description": "Scenic hillside home"
                    }
                ],
                "style_tags": [
                    {
                        "tag_id": "style_warm",
                        "name": "Warm Cinematic",
                        "description": "Golden hour lighting"
                    }
                ],
                "beat_id": "beat_1",
                "chapter_number": 1,
                "scene_ids": ["scene_1", "scene_2"],
                "total_shots": 8,
                "total_scenes": 2
            }
        }

