"""
Video Generation & Album Models

Features:
- Video generation jobs and results
- Album/gallery organization
- Export formats and metadata
- Video thumbnails and previews

Author: Peace Script Team
Date: January 2025
Version: 1.0
"""

from beanie import Document
from pydantic import Field, BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class VideoStatus(str, Enum):
    """Video generation status"""
    PENDING = "pending"
    QUEUED = "queued"
    GENERATING = "generating"
    PROCESSING = "processing"
    COMPLETE = "complete"
    FAILED = "failed"
    CANCELLED = "cancelled"


class VideoFormat(str, Enum):
    """Supported video formats"""
    MP4 = "mp4"
    WEBM = "webm"
    MOV = "mov"
    AVI = "avi"


class VideoQuality(str, Enum):
    """Video quality presets"""
    PREVIEW = "preview"   # 256p, ultra-fast for testing
    LOW = "low"           # 480p, faster generation
    MEDIUM = "medium"     # 720p, balanced
    HIGH = "high"         # 1080p, best quality
    ULTRA = "ultra"       # 1080p+ with maximum settings


class ExportPreset(str, Enum):
    """Export presets"""
    WEB = "web"           # Optimized for web (H.264, medium quality)
    SOCIAL = "social"     # Social media (square/vertical, compressed)
    ARCHIVE = "archive"   # High quality archive (lossless)
    PREVIEW = "preview"   # Low quality preview (fast)


# ============================================================================
# Nested Models
# ============================================================================

class MotionParameters(BaseModel):
    """Motion effect parameters"""
    zoom: float = Field(default=1.0, ge=0.5, le=3.0)
    pan_x: float = Field(default=0.0, ge=-1.0, le=1.0)
    pan_y: float = Field(default=0.0, ge=-1.0, le=1.0)
    tilt: float = Field(default=0.0, ge=-45.0, le=45.0)
    rotate: float = Field(default=0.0, ge=-180.0, le=180.0)
    speed: float = Field(default=1.0, ge=0.1, le=5.0)
    easing: str = Field(default="linear")  # linear, ease-in, ease-out, ease-in-out


class CameraSettings(BaseModel):
    """Camera settings for shot"""
    shot_type: str = "medium"  # wide, medium, closeup, extreme-closeup
    angle: str = "eye-level"    # eye-level, high-angle, low-angle, dutch
    movement: str = "static"    # static, pan, tilt, dolly, crane


class LightingSettings(BaseModel):
    """Lighting settings"""
    type: str = "natural"       # natural, studio, dramatic, soft
    time_of_day: str = "day"    # day, night, golden-hour, blue-hour
    intensity: float = Field(default=1.0, ge=0.0, le=2.0)


class AISettings(BaseModel):
    """AI generation settings"""
    model: str = "runway-gen2"  # runway-gen2, pika, stable-video
    style: str = "cinematic"    # cinematic, anime, realistic, artistic
    cfg_scale: float = Field(default=7.5, ge=1.0, le=20.0)
    steps: int = Field(default=30, ge=10, le=100)
    seed: Optional[int] = None


class VideoMetadata(BaseModel):
    """Video file metadata"""
    width: int
    height: int
    fps: int = 24
    duration: float  # seconds
    codec: str = "h264"
    bitrate: Optional[int] = None  # kbps
    file_size: int  # bytes
    thumbnail_url: Optional[str] = None


# ============================================================================
# Main Documents
# ============================================================================

class VideoGenerationJob(Document):
    """Video generation job tracking
    
    Tracks async video generation jobs from Motion Editor.
    Uses job queue (Celery/Redis) for background processing.
    
    Attributes:
        job_id: Unique job identifier
        project_id: Associated narrative project
        shot_id: Shot being generated (optional)
        status: Current generation status
        progress: Generation progress (0-100)
        input_settings: All generation parameters
        output_video_id: Reference to GeneratedVideo when complete
        error_message: Error details if failed
        created_at: Job creation time
        started_at: Generation start time
        completed_at: Generation completion time
    """
    
    job_id: str = Field(unique=True, index=True)
    project_id: str = Field(index=True)
    shot_id: Optional[str] = None
    
    status: VideoStatus = VideoStatus.PENDING
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    status_message: Optional[str] = None  # Detailed status message
    current_step: Optional[int] = None    # Current step number
    total_steps: Optional[int] = None     # Total number of steps
    
    # Input parameters
    input_settings: Dict[str, Any] = Field(default_factory=dict)
    motion_parameters: Optional[MotionParameters] = None
    camera_settings: Optional[CameraSettings] = None
    lighting_settings: Optional[LightingSettings] = None
    ai_settings: Optional[AISettings] = None
    
    # Output
    output_video_id: Optional[str] = None
    error_message: Optional[str] = None
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    
    class Settings:
        name = "video_generation_jobs"
        indexes = [
            "job_id",
            "project_id",
            "status",
            "created_at"
        ]


class GeneratedVideo(Document):
    """Generated video result
    
    Stores metadata and URLs for successfully generated videos.
    Can be organized into albums.
    
    Attributes:
        video_id: Unique video identifier
        job_id: Source generation job
        project_id: Associated project
        shot_id: Associated shot (optional)
        
        file_url: Primary video file URL
        thumbnail_url: Thumbnail image URL
        preview_url: Low-quality preview URL (optional)
        
        format: Video file format (mp4, webm)
        quality: Quality preset used
        metadata: Technical video metadata
        
        album_ids: Albums this video belongs to
        tags: Searchable tags
        description: User description
        
        created_at: Video creation time
        views: View count
        downloads: Download count
    """
    
    video_id: str = Field(unique=True, index=True)
    job_id: str = Field(index=True)
    project_id: str = Field(index=True)
    shot_id: Optional[str] = None
    
    # File URLs
    file_url: str  # e.g., /storage/videos/proj_001/video_001.mp4
    thumbnail_url: Optional[str] = None
    preview_url: Optional[str] = None
    
    # Technical details
    format: VideoFormat = VideoFormat.MP4
    quality: VideoQuality = VideoQuality.MEDIUM
    metadata: Optional[VideoMetadata] = None
    
    # Organization
    album_ids: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    
    # Generation settings (for reference)
    generation_settings: Optional[Dict[str, Any]] = None
    
    # Stats
    created_at: datetime = Field(default_factory=datetime.utcnow)
    views: int = Field(default=0)
    downloads: int = Field(default=0)
    
    # User info (optional)
    created_by: Optional[str] = None
    
    class Settings:
        name = "generated_videos"
        indexes = [
            "video_id",
            "project_id",
            "job_id",
            "album_ids",
            "created_at",
            "tags"
        ]


class Album(Document):
    """Video album/collection
    
    NOTE: This model is for VIDEO albums only.
    For IMAGE albums (character profiles, concept art), use ImageAlbum from documents_gallery.py
    
    Organizes videos into collections.
    Similar to photo albums or playlists.
    
    Attributes:
        album_id: Unique album identifier
        project_id: Associated project (optional)
        name: Album name
        description: Album description
        cover_video_id: Video to use as cover
        video_ids: Videos in this album (ordered)
        tags: Album tags
        created_at: Creation time
        updated_at: Last update time
        created_by: Creator user ID
    """
    
    album_id: str = Field(unique=True, index=True)
    project_id: Optional[str] = None
    
    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    cover_video_id: Optional[str] = None
    
    # Videos in album (ordered)
    video_ids: List[str] = Field(default_factory=list)
    
    # Organization
    tags: List[str] = Field(default_factory=list)
    is_public: bool = Field(default=False)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    
    class Settings:
        name = "albums"
        indexes = [
            "album_id",
            "project_id",
            "created_at",
            "tags"
        ]


class ExportTask(Document):
    """Video export task
    
    Tracks video export/download tasks.
    Supports different formats and quality presets.
    
    Attributes:
        task_id: Unique task identifier
        video_id: Source video
        preset: Export preset (web, social, archive)
        format: Output format
        quality: Output quality
        status: Export status
        output_url: Exported file URL
        created_at: Task creation time
    """
    
    task_id: str = Field(unique=True, index=True)
    video_id: str = Field(index=True)
    
    preset: ExportPreset = ExportPreset.WEB
    format: VideoFormat = VideoFormat.MP4
    quality: VideoQuality = VideoQuality.MEDIUM
    
    # Custom settings (optional)
    custom_width: Optional[int] = None
    custom_height: Optional[int] = None
    custom_fps: Optional[int] = None
    custom_bitrate: Optional[int] = None
    
    status: VideoStatus = VideoStatus.PENDING
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    
    output_url: Optional[str] = None
    error_message: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    class Settings:
        name = "export_tasks"
        indexes = [
            "task_id",
            "video_id",
            "status",
            "created_at"
        ]
