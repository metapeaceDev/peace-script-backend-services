"""
Storyboard Document Models

MongoDB document models for storyboard management.
Provides shot-by-shot visual planning with thumbnails.

Author: Peace Script Team
Date: 20 November 2568
Version: 1.0
"""

from beanie import Document
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class CameraAngle(str, Enum):
    """Camera angle options"""
    WIDE = "wide"
    MEDIUM = "medium"
    CLOSE_UP = "close_up"
    EXTREME_CLOSE_UP = "extreme_close_up"
    OVER_SHOULDER = "over_shoulder"
    POV = "pov"
    BIRD_EYE = "bird_eye"
    LOW_ANGLE = "low_angle"
    HIGH_ANGLE = "high_angle"
    DUTCH_ANGLE = "dutch_angle"


class ShotType(str, Enum):
    """Shot type options"""
    ESTABLISHING = "establishing"
    MASTER = "master"
    TWO_SHOT = "two_shot"
    CUTAWAY = "cutaway"
    INSERT = "insert"
    REACTION = "reaction"
    ACTION = "action"


class StoryboardShot(BaseModel):
    """Individual shot in storyboard"""
    shot_id: str
    shot_number: int = Field(..., ge=1)
    thumbnail_url: Optional[str] = None
    description: str
    camera_angle: CameraAngle = CameraAngle.MEDIUM
    shot_type: ShotType = ShotType.MASTER
    duration: float = Field(default=3.0, ge=0.1)  # seconds
    dialogue: Optional[str] = None
    action: Optional[str] = None
    notes: Optional[str] = None
    characters: List[str] = []
    
    # Technical specs
    lens: Optional[str] = None  # "50mm", "24mm", etc.
    movement: Optional[str] = None  # "pan left", "dolly in", etc.
    lighting: Optional[str] = None
    sfx: List[str] = []
    
    # References
    scene_id: Optional[str] = None
    reference_images: List[str] = []


class Storyboard(Document):
    """
    Storyboard Document
    
    Represents a complete storyboard for a project with shots arranged in sequence.
    """
    storyboard_id: str = Field(..., description="Unique storyboard identifier")
    project_id: str = Field(..., description="Link to narrative project")
    title: str
    description: Optional[str] = None
    
    # Shots array
    shots: List[StoryboardShot] = []
    
    # Metadata
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Statistics
    total_duration: float = 0.0  # Total duration in seconds
    total_shots: int = 0
    
    # Export info
    last_exported_at: Optional[datetime] = None
    export_format: Optional[str] = None  # "pdf", "csv", etc.
    
    class Settings:
        name = "storyboards"
        indexes = [
            "storyboard_id",
            "project_id",
            "created_at"
        ]
    
    def update_stats(self):
        """Update statistics based on shots"""
        self.total_shots = len(self.shots)
        self.total_duration = sum(shot.duration for shot in self.shots)
        self.updated_at = datetime.utcnow()
