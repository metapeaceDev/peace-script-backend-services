"""
Shot Schemas for Storyboard System (LTX Studio-inspired)

This module contains schemas for shot-level storyboard management.
Extends the scene-based structure with detailed shot breakdowns.

Author: Peace Script Team  
Date: 25 November 2025
Version: 1.0
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# =============================================================================
# ENUMS
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
# CAMERA SETTINGS
# =============================================================================

class CameraSettings(BaseModel):
    """Camera configuration for a shot"""
    shot_type: ShotType = Field(default=ShotType.MEDIUM, description="Type of shot (CU, MS, WS, etc.)")
    angle: CameraAngle = Field(default=CameraAngle.EYE_LEVEL, description="Camera angle")
    movement: CameraMovement = Field(default=CameraMovement.STATIC, description="Camera movement")
    focal_length: Optional[int] = Field(None, ge=10, le=200, description="Focal length in mm (10-200)")
    aperture: Optional[str] = Field(None, description="Aperture value (e.g., f/2.8, f/5.6)")
    
    class Config:
        schema_extra = {
            "example": {
                "shot_type": "medium",
                "angle": "eye_level",
                "movement": "dolly_in",
                "focal_length": 50,
                "aperture": "f/2.8"
            }
        }


class MotionParameters(BaseModel):
    """Motion parameters for video generation (ComfyUI integration)"""
    zoom_start: float = Field(default=1.0, ge=0.5, le=2.0, description="Starting zoom level")
    zoom_end: float = Field(default=1.0, ge=0.5, le=2.0, description="Ending zoom level")
    move_x: float = Field(default=0.0, ge=-100.0, le=100.0, description="Horizontal movement (-100 to 100)")
    move_y: float = Field(default=0.0, ge=-100.0, le=100.0, description="Vertical movement (-100 to 100)")
    rotate_start: float = Field(default=0.0, ge=-180.0, le=180.0, description="Starting rotation angle")
    rotate_end: float = Field(default=0.0, ge=-180.0, le=180.0, description="Ending rotation angle")
    duration: int = Field(default=3, ge=1, le=10, description="Duration in seconds")
    speed: float = Field(default=1.0, ge=0.1, le=3.0, description="Playback speed multiplier")
    
    class Config:
        schema_extra = {
            "example": {
                "zoom_start": 1.0,
                "zoom_end": 1.2,
                "move_x": 0,
                "move_y": -10,
                "rotate_start": 0,
                "rotate_end": 0,
                "duration": 3,
                "speed": 1.0
            }
        }


# =============================================================================
# SHOT SCHEMAS
# =============================================================================

class ShotCreate(BaseModel):
    """Schema for creating a new shot"""
    scene_id: str = Field(..., description="Parent scene ID")
    shot_number: int = Field(..., ge=1, description="Shot number within scene")
    
    # Description
    caption: Optional[str] = Field(None, max_length=500, description="Shot caption/description (e.g., '@Maria walks...')")
    shot_description: Optional[str] = Field(None, max_length=2000, description="Detailed shot description")
    
    # Camera
    camera: Optional[CameraSettings] = Field(default=None, description="Camera settings")
    
    # Visual
    image_url: Optional[str] = Field(None, description="Generated image URL")
    video_url: Optional[str] = Field(None, description="Generated video URL")
    
    # Motion (for video generation)
    motion_parameters: Optional[MotionParameters] = Field(None, description="Motion parameters for video")
    
    # AI Generation
    prompt: Optional[str] = Field(None, max_length=2000, description="Image generation prompt")
    negative_prompt: Optional[str] = Field(None, max_length=1000, description="Negative prompt")
    
    # Status
    status: ShotStatus = Field(default=ShotStatus.DRAFT, description="Shot status")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        schema_extra = {
            "example": {
                "scene_id": "scene_xxx",
                "shot_number": 1,
                "caption": "@Maria walks through the sunlit meadow, surrounded by butterflies",
                "shot_description": "Wide shot of Maria walking slowly through a golden meadow",
                "camera": {
                    "shot_type": "wide",
                    "angle": "eye_level",
                    "movement": "tracking"
                },
                "prompt": "Wide cinematic shot, woman walking in meadow, golden hour lighting, butterflies",
                "status": "draft"
            }
        }


class ShotUpdate(BaseModel):
    """Schema for updating a shot"""
    shot_number: Optional[int] = Field(None, ge=1)
    caption: Optional[str] = Field(None, max_length=500)
    shot_description: Optional[str] = Field(None, max_length=2000)
    camera: Optional[CameraSettings] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    motion_parameters: Optional[MotionParameters] = None
    prompt: Optional[str] = Field(None, max_length=2000)
    negative_prompt: Optional[str] = Field(None, max_length=1000)
    status: Optional[ShotStatus] = None
    metadata: Optional[Dict[str, Any]] = None


class ShotResponse(BaseModel):
    """Schema for shot response"""
    id: str
    scene_id: str
    shot_id: str  # Unique identifier
    shot_number: int
    caption: Optional[str]
    shot_description: Optional[str]
    camera: CameraSettings
    image_url: Optional[str]
    video_url: Optional[str]
    motion_parameters: Optional[MotionParameters]
    prompt: Optional[str]
    negative_prompt: Optional[str]
    status: ShotStatus
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# =============================================================================
# LOCATION & STYLE TAG SCHEMAS
# =============================================================================

class LocationTag(BaseModel):
    """Location tag for scene grouping"""
    tag_id: str = Field(..., description="Unique tag identifier")
    name: str = Field(..., max_length=100, description="Location name (e.g., 'Forest', 'Urban')")
    description: Optional[str] = Field(None, max_length=500, description="Location description")
    
    # Derived from Step 2 timeline
    environment: Optional[str] = Field(None, description="Environment type from Step 2")
    social_context: Optional[str] = Field(None, description="Social context from Step 2")
    
    class Config:
        schema_extra = {
            "example": {
                "tag_id": "loc_forest",
                "name": "Dense Forest",
                "description": "Deep forest with tall trees and mystical atmosphere",
                "environment": "ป่าทึบภาคเหนือ"
            }
        }


class StyleTag(BaseModel):
    """Visual style tag for scene grouping"""
    tag_id: str = Field(..., description="Unique tag identifier")
    name: str = Field(..., max_length=100, description="Style name (e.g., 'Cinematic', 'Grit')")
    description: Optional[str] = Field(None, max_length=500, description="Style description")
    
    # Derived from Step 1 genres
    genre_based: Optional[bool] = Field(default=True, description="Whether style comes from genre")
    custom_prompt_additions: Optional[str] = Field(None, description="Custom prompt modifiers for this style")
    
    class Config:
        schema_extra = {
            "example": {
                "tag_id": "style_cinematic",
                "name": "Cinematic",
                "description": "Epic cinematic look with dramatic lighting",
                "genre_based": True,
                "custom_prompt_additions": "cinematic lighting, dramatic composition, film grain"
            }
        }


class SceneGroupMetadata(BaseModel):
    """Extended metadata for scene groups (LTX-style organization)"""
    group_id: str = Field(..., description="Scene group identifier")
    title: str = Field(..., max_length=200, description="Group title (e.g., 'Departure from...')")
    description: Optional[str] = Field(None, max_length=1000, description="Group description")
    
    # Tags
    location_tags: List[LocationTag] = Field(default_factory=list, description="Location tags")
    style_tags: List[StyleTag] = Field(default_factory=list, description="Style tags")
    
    # Relation to narrative structure
    beat_id: Optional[str] = Field(None, description="Related story beat from Step 4")
    chapter_number: Optional[int] = Field(None, ge=1, le=3, description="Act/Chapter number")
    
    # Shot count
    total_shots: int = Field(default=0, ge=0, description="Total shots in this group")
    
    class Config:
        schema_extra = {
            "example": {
                "group_id": "group_departure",
                "title": "Departure from home",
                "description": "Thomas bids farewell to his family marking the start of his journey",
                "location_tags": [
                    {"tag_id": "loc_hillside", "name": "Hillside", "description": "Rural hillside home"}
                ],
                "style_tags": [
                    {"tag_id": "style_warm", "name": "Warm Cinematic", "description": "Golden hour lighting"}
                ],
                "beat_id": "beat_1",
                "chapter_number": 1,
                "total_shots": 4
            }
        }
