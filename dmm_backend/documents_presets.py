"""
Custom Preset Models for Camera Director System
Sprint 2: Days 9-16
Created: 28 ตุลาคม 2568
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

from beanie import Document
from pydantic import BaseModel, Field


# --- Enums --- #

class PresetCategory(str, Enum):
    """Preset categories for organization"""
    SHOT_COMPOSITION = "shot_composition"
    CAMERA_MOVEMENT = "camera_movement"
    LIGHTING = "lighting"
    EMOTION_FOCUS = "emotion_focus"
    GENRE_STYLE = "genre_style"
    CUSTOM = "custom"


class PresetVisibility(str, Enum):
    """Preset visibility levels"""
    PRIVATE = "private"  # Only creator can see
    SHARED = "shared"    # Shared with specific users
    PUBLIC = "public"    # Available to all users
    SYSTEM = "system"    # System-provided templates


# --- Nested Models --- #

class PresetParameter(BaseModel):
    """Individual parameter in a preset"""
    name: str
    value: Any
    type: str  # "string", "number", "boolean", "select", "range"
    description: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    options: Optional[List[str]] = None  # For select type


class PresetConfig(BaseModel):
    """Complete configuration for a preset"""
    parameters: List[PresetParameter] = []
    camera_settings: Optional[Dict[str, Any]] = None
    shot_settings: Optional[Dict[str, Any]] = None
    feedback_triggers: Optional[Dict[str, Any]] = None


class PresetUsageStats(BaseModel):
    """Statistics for preset usage"""
    total_uses: int = 0
    successful_uses: int = 0
    failed_uses: int = 0
    average_rating: float = 0.0
    last_used: Optional[datetime] = None


class PresetTag(BaseModel):
    """Tags for preset organization"""
    name: str
    color: Optional[str] = None


# --- Document Models --- #

class PresetTemplate(Document):
    """
    System-provided preset templates
    These are base templates that users can customize
    """
    template_id: str = Field(index=True, unique=True)
    name: str
    description: str
    category: PresetCategory
    visibility: PresetVisibility = PresetVisibility.SYSTEM
    
    # Configuration
    config: PresetConfig
    
    # Preview/Display
    thumbnail_url: Optional[str] = None
    preview_data: Optional[Dict[str, Any]] = None
    
    # Metadata
    tags: List[PresetTag] = []
    created_by: str = "system"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Usage statistics
    usage_stats: PresetUsageStats = Field(default_factory=PresetUsageStats)
    
    # Version control
    version: str = "1.0.0"
    is_active: bool = True
    
    class Settings:
        name = "preset_templates"
        indexes = [
            "template_id",
            "category",
            "visibility",
            "created_at"
        ]


class UserPreset(Document):
    """
    User-created or customized presets
    Can be based on templates or created from scratch
    """
    preset_id: str = Field(index=True, unique=True)
    name: str
    description: Optional[str] = None
    category: PresetCategory
    visibility: PresetVisibility = PresetVisibility.PRIVATE
    
    # Configuration
    config: PresetConfig
    
    # Template relationship
    based_on_template_id: Optional[str] = None  # Reference to PresetTemplate
    is_modified: bool = False  # True if modified from template
    
    # Owner and sharing
    owner_id: str = Field(index=True)
    shared_with: List[str] = []  # List of user IDs
    
    # Preview/Display
    thumbnail_url: Optional[str] = None
    preview_data: Optional[Dict[str, Any]] = None
    
    # Organization
    tags: List[PresetTag] = []
    folder: Optional[str] = None  # For user organization
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None
    
    # Usage statistics
    usage_stats: PresetUsageStats = Field(default_factory=PresetUsageStats)
    
    # Favorites and ratings
    is_favorite: bool = False
    rating: Optional[float] = None  # User's own rating
    
    # Version control
    version: str = "1.0.0"
    is_active: bool = True
    
    class Settings:
        name = "user_presets"
        indexes = [
            "preset_id",
            "owner_id",
            "category",
            "visibility",
            "is_favorite",
            "created_at"
        ]


class PresetCollection(Document):
    """
    Collections/folders for organizing presets
    Users can group related presets together
    """
    collection_id: str = Field(index=True, unique=True)
    name: str
    description: Optional[str] = None
    
    # Owner
    owner_id: str = Field(index=True)
    
    # Contents
    preset_ids: List[str] = []  # References to UserPreset IDs
    
    # Display
    icon: Optional[str] = None
    color: Optional[str] = None
    
    # Organization
    parent_collection_id: Optional[str] = None  # For nested collections
    sort_order: int = 0
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "preset_collections"
        indexes = [
            "collection_id",
            "owner_id",
            "parent_collection_id"
        ]


class PresetUsageLog(Document):
    """
    Log of preset usage for analytics
    Tracks when and how presets are used
    """
    log_id: str = Field(index=True, unique=True)
    
    # Preset reference
    preset_id: str = Field(index=True)
    preset_type: str  # "template" or "user"
    
    # User reference
    user_id: str = Field(index=True)
    
    # Context
    project_id: Optional[str] = None
    scene_id: Optional[str] = None
    shot_id: Optional[str] = None
    
    # Usage details
    used_at: datetime = Field(default_factory=datetime.utcnow)
    duration_seconds: Optional[int] = None
    success: bool = True
    
    # Feedback
    rating: Optional[float] = None
    feedback_text: Optional[str] = None
    
    # Modified parameters (if user adjusted preset during use)
    modified_parameters: Optional[Dict[str, Any]] = None
    
    class Settings:
        name = "preset_usage_logs"
        indexes = [
            "log_id",
            "preset_id",
            "user_id",
            "used_at",
            "project_id"
        ]


class PresetShare(Document):
    """
    Sharing relationships for presets
    Tracks who has access to shared presets
    """
    share_id: str = Field(index=True, unique=True)
    
    # Preset reference
    preset_id: str = Field(index=True)
    
    # Sharing details
    shared_by_user_id: str
    shared_with_user_id: str = Field(index=True)
    
    # Permissions
    can_view: bool = True
    can_edit: bool = False
    can_reshare: bool = False
    
    # Status
    accepted: bool = False
    accepted_at: Optional[datetime] = None
    
    # Metadata
    shared_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    message: Optional[str] = None
    
    class Settings:
        name = "preset_shares"
        indexes = [
            "share_id",
            "preset_id",
            "shared_with_user_id",
            "shared_at"
        ]
