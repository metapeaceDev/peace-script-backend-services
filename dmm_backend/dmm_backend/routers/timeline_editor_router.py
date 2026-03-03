"""
Timeline Editor Router
Handles multi-track timeline editing, scene/shot/motion/audio synchronization

Features:
- CRUD operations for timelines
- Multi-track management (video, audio, motion, effects)
- Scene and shot organization
- Audio/Motion synchronization
- Timeline export (JSON, EDL, XML)
- Collaboration (locks, versions)

Endpoints:
- POST   /api/timeline/create          - Create new timeline
- GET    /api/timeline/{timeline_id}   - Get timeline by ID
- PUT    /api/timeline/{timeline_id}   - Update timeline
- DELETE /api/timeline/{timeline_id}   - Delete timeline
- GET    /api/timeline/list            - List all timelines
- POST   /api/timeline/{id}/track      - Add track
- PUT    /api/timeline/{id}/track/{track_id} - Update track
- DELETE /api/timeline/{id}/track/{track_id} - Delete track
- POST   /api/timeline/{id}/clip       - Add clip
- PUT    /api/timeline/{id}/clip/{clip_id}   - Update clip
- DELETE /api/timeline/{id}/clip/{clip_id}   - Delete clip
- POST   /api/timeline/{id}/export     - Export timeline
- GET    /api/timeline/{id}/preview    - Generate preview
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from enum import Enum

router = APIRouter(prefix="/api/timeline", tags=["Timeline Editor"])


# ==================== Enums ====================

class TrackType(str, Enum):
    """Track types"""
    VIDEO = "video"
    AUDIO = "audio"
    MOTION = "motion"
    SFX = "sfx"
    MUSIC = "music"
    DIALOGUE = "dialogue"
    EFFECTS = "effects"
    MARKERS = "markers"


class ClipType(str, Enum):
    """Clip types"""
    SCENE = "scene"
    SHOT = "shot"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    MOTION = "motion"
    EFFECT = "effect"
    MARKER = "marker"


class ExportFormat(str, Enum):
    """Export formats"""
    JSON = "json"
    EDL = "edl"
    XML = "xml"
    CSV = "csv"


# ==================== Models ====================

class TimelineClip(BaseModel):
    """Timeline clip model"""
    id: str
    track_id: str
    clip_type: ClipType
    name: str
    start_time: float = Field(ge=0, description="Start time in seconds")
    duration: float = Field(gt=0, description="Duration in seconds")
    
    # Media references
    media_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    
    # Motion parameters (for motion clips)
    motion_parameters: Optional[Dict[str, float]] = None
    keyframes: Optional[List[Dict[str, Any]]] = None
    
    # Audio parameters (for audio clips)
    volume: float = Field(default=1.0, ge=0, le=1.0)
    fade_in: float = Field(default=0.0, ge=0)
    fade_out: float = Field(default=0.0, ge=0)
    
    # Visual parameters (for video/image clips)
    effects: List[str] = Field(default_factory=list)
    transitions: Optional[Dict[str, Any]] = None
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    locked: bool = False
    
    class Config:
        schema_extra = {
            "example": {
                "id": "clip_001",
                "track_id": "track_video_1",
                "clip_type": "shot",
                "name": "Opening Scene - Shot 1",
                "start_time": 0.0,
                "duration": 5.0,
                "media_url": "/media/shot_001.mp4",
                "volume": 0.8,
                "motion_parameters": {
                    "zoom_in": 0.3,
                    "pan_right": 0.2
                }
            }
        }


class TimelineTrack(BaseModel):
    """Timeline track model"""
    id: str
    name: str
    track_type: TrackType
    order: int = Field(ge=0, description="Track display order")
    clips: List[TimelineClip] = Field(default_factory=list)
    
    # Track settings
    enabled: bool = True
    muted: bool = False
    solo: bool = False
    volume: float = Field(default=1.0, ge=0, le=1.0)
    
    # Visual settings
    color: str = "#3b82f6"
    height: int = Field(default=80, ge=40, le=200)
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    locked: bool = False
    
    class Config:
        schema_extra = {
            "example": {
                "id": "track_video_1",
                "name": "Video Track 1",
                "track_type": "video",
                "order": 0,
                "clips": [],
                "enabled": True,
                "color": "#3b82f6"
            }
        }


class Timeline(BaseModel):
    """Timeline model"""
    id: str
    name: str
    description: Optional[str] = None
    project_id: Optional[str] = None
    
    # Timeline settings
    duration: float = Field(gt=0, description="Total duration in seconds")
    fps: float = Field(default=24.0, gt=0, description="Frames per second")
    resolution: Dict[str, int] = Field(
        default={"width": 1920, "height": 1080}
    )
    
    # Tracks
    tracks: List[TimelineTrack] = Field(default_factory=list)
    
    # Timeline markers
    markers: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Playback settings
    playback_speed: float = Field(default=1.0, gt=0, le=4.0)
    current_time: float = Field(default=0.0, ge=0)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: Optional[str] = None
    version: int = Field(default=1, ge=1)
    
    # Settings
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        schema_extra = {
            "example": {
                "id": "timeline_001",
                "name": "Episode 1 - Main Timeline",
                "duration": 120.0,
                "fps": 24.0,
                "tracks": [],
                "markers": []
            }
        }


# ==================== Request Models ====================

class CreateTimelineRequest(BaseModel):
    """Create timeline request"""
    name: str
    description: Optional[str] = None
    project_id: Optional[str] = None
    duration: float = Field(default=60.0, gt=0)
    fps: float = Field(default=24.0, gt=0)
    resolution: Optional[Dict[str, int]] = None


class UpdateTimelineRequest(BaseModel):
    """Update timeline request"""
    name: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[float] = Field(default=None, gt=0)
    fps: Optional[float] = Field(default=None, gt=0)
    resolution: Optional[Dict[str, int]] = None
    playback_speed: Optional[float] = Field(default=None, gt=0, le=4.0)
    current_time: Optional[float] = Field(default=None, ge=0)
    metadata: Optional[Dict[str, Any]] = None


class AddTrackRequest(BaseModel):
    """Add track request"""
    name: str
    track_type: TrackType
    order: Optional[int] = None
    color: str = "#3b82f6"
    height: int = Field(default=80, ge=40, le=200)


class UpdateTrackRequest(BaseModel):
    """Update track request"""
    name: Optional[str] = None
    order: Optional[int] = None
    enabled: Optional[bool] = None
    muted: Optional[bool] = None
    solo: Optional[bool] = None
    volume: Optional[float] = Field(default=None, ge=0, le=1.0)
    color: Optional[str] = None
    height: Optional[int] = Field(default=None, ge=40, le=200)
    locked: Optional[bool] = None


class AddClipRequest(BaseModel):
    """Add clip request"""
    track_id: str
    clip_type: ClipType
    name: str
    start_time: float = Field(ge=0)
    duration: float = Field(gt=0)
    media_url: Optional[str] = None
    motion_parameters: Optional[Dict[str, float]] = None
    keyframes: Optional[List[Dict[str, Any]]] = None
    volume: float = Field(default=1.0, ge=0, le=1.0)
    effects: List[str] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None


class UpdateClipRequest(BaseModel):
    """Update clip request"""
    name: Optional[str] = None
    start_time: Optional[float] = Field(default=None, ge=0)
    duration: Optional[float] = Field(default=None, gt=0)
    motion_parameters: Optional[Dict[str, float]] = None
    keyframes: Optional[List[Dict[str, Any]]] = None
    volume: Optional[float] = Field(default=None, ge=0, le=1.0)
    fade_in: Optional[float] = Field(default=None, ge=0)
    fade_out: Optional[float] = Field(default=None, ge=0)
    effects: Optional[List[str]] = None
    locked: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class ExportTimelineRequest(BaseModel):
    """Export timeline request"""
    format: ExportFormat
    include_media: bool = False
    include_metadata: bool = True


# ==================== In-Memory Storage (Replace with DB) ====================

# Temporary storage - replace with database
timelines_db: Dict[str, Timeline] = {}


# ==================== Helper Functions ====================

def generate_id(prefix: str = "item") -> str:
    """Generate unique ID"""
    import random
    import string
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{prefix}_{timestamp}_{random_str}"


def find_track(timeline: Timeline, track_id: str) -> Optional[TimelineTrack]:
    """Find track by ID"""
    for track in timeline.tracks:
        if track.id == track_id:
            return track
    return None


def find_clip(timeline: Timeline, clip_id: str) -> Optional[tuple]:
    """Find clip by ID and return (track, clip)"""
    for track in timeline.tracks:
        for clip in track.clips:
            if clip.id == clip_id:
                return (track, clip)
    return None


# ==================== Endpoints ====================

@router.post("/create", response_model=Timeline, status_code=status.HTTP_201_CREATED)
async def create_timeline(request: CreateTimelineRequest):
    """
    Create a new timeline
    
    Creates a new multi-track timeline with default settings
    """
    timeline_id = generate_id("timeline")
    
    timeline = Timeline(
        id=timeline_id,
        name=request.name,
        description=request.description,
        project_id=request.project_id,
        duration=request.duration,
        fps=request.fps,
        resolution=request.resolution or {"width": 1920, "height": 1080},
        tracks=[],
        markers=[],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Create default tracks
    default_tracks = [
        {"name": "Video 1", "type": TrackType.VIDEO, "color": "#3b82f6"},
        {"name": "Audio 1", "type": TrackType.AUDIO, "color": "#10b981"},
        {"name": "Motion", "type": TrackType.MOTION, "color": "#8b5cf6"},
        {"name": "SFX", "type": TrackType.SFX, "color": "#f59e0b"}
    ]
    
    for i, track_data in enumerate(default_tracks):
        track = TimelineTrack(
            id=generate_id("track"),
            name=track_data["name"],
            track_type=track_data["type"],
            order=i,
            color=track_data["color"],
            clips=[]
        )
        timeline.tracks.append(track)
    
    timelines_db[timeline_id] = timeline
    
    return timeline


@router.get("/{timeline_id}", response_model=Timeline)
async def get_timeline(timeline_id: str):
    """Get timeline by ID"""
    if timeline_id not in timelines_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Timeline {timeline_id} not found"
        )
    
    return timelines_db[timeline_id]


@router.put("/{timeline_id}", response_model=Timeline)
async def update_timeline(timeline_id: str, request: UpdateTimelineRequest):
    """Update timeline settings"""
    if timeline_id not in timelines_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Timeline {timeline_id} not found"
        )
    
    timeline = timelines_db[timeline_id]
    
    # Update fields
    if request.name is not None:
        timeline.name = request.name
    if request.description is not None:
        timeline.description = request.description
    if request.duration is not None:
        timeline.duration = request.duration
    if request.fps is not None:
        timeline.fps = request.fps
    if request.resolution is not None:
        timeline.resolution = request.resolution
    if request.playback_speed is not None:
        timeline.playback_speed = request.playback_speed
    if request.current_time is not None:
        timeline.current_time = request.current_time
    if request.metadata is not None:
        timeline.metadata.update(request.metadata)
    
    timeline.updated_at = datetime.now()
    timeline.version += 1
    
    return timeline


@router.delete("/{timeline_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_timeline(timeline_id: str):
    """Delete timeline"""
    if timeline_id not in timelines_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Timeline {timeline_id} not found"
        )
    
    del timelines_db[timeline_id]
    return None


@router.get("/list", response_model=List[Timeline])
async def list_timelines(project_id: Optional[str] = None):
    """List all timelines (optionally filtered by project)"""
    timelines = list(timelines_db.values())
    
    if project_id:
        timelines = [t for t in timelines if t.project_id == project_id]
    
    # Sort by updated_at descending
    timelines.sort(key=lambda t: t.updated_at, reverse=True)
    
    return timelines


@router.post("/{timeline_id}/track", response_model=TimelineTrack, status_code=status.HTTP_201_CREATED)
async def add_track(timeline_id: str, request: AddTrackRequest):
    """Add track to timeline"""
    if timeline_id not in timelines_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Timeline {timeline_id} not found"
        )
    
    timeline = timelines_db[timeline_id]
    
    # Determine order
    order = request.order if request.order is not None else len(timeline.tracks)
    
    track = TimelineTrack(
        id=generate_id("track"),
        name=request.name,
        track_type=request.track_type,
        order=order,
        color=request.color,
        height=request.height,
        clips=[]
    )
    
    timeline.tracks.append(track)
    timeline.updated_at = datetime.now()
    
    return track


@router.put("/{timeline_id}/track/{track_id}", response_model=TimelineTrack)
async def update_track(timeline_id: str, track_id: str, request: UpdateTrackRequest):
    """Update track settings"""
    if timeline_id not in timelines_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Timeline {timeline_id} not found"
        )
    
    timeline = timelines_db[timeline_id]
    track = find_track(timeline, track_id)
    
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Track {track_id} not found"
        )
    
    # Update fields
    if request.name is not None:
        track.name = request.name
    if request.order is not None:
        track.order = request.order
    if request.enabled is not None:
        track.enabled = request.enabled
    if request.muted is not None:
        track.muted = request.muted
    if request.solo is not None:
        track.solo = request.solo
    if request.volume is not None:
        track.volume = request.volume
    if request.color is not None:
        track.color = request.color
    if request.height is not None:
        track.height = request.height
    if request.locked is not None:
        track.locked = request.locked
    
    timeline.updated_at = datetime.now()
    
    return track


@router.delete("/{timeline_id}/track/{track_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_track(timeline_id: str, track_id: str):
    """Delete track from timeline"""
    if timeline_id not in timelines_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Timeline {timeline_id} not found"
        )
    
    timeline = timelines_db[timeline_id]
    track = find_track(timeline, track_id)
    
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Track {track_id} not found"
        )
    
    timeline.tracks.remove(track)
    timeline.updated_at = datetime.now()
    
    return None


@router.post("/{timeline_id}/clip", response_model=TimelineClip, status_code=status.HTTP_201_CREATED)
async def add_clip(timeline_id: str, request: AddClipRequest):
    """Add clip to track"""
    if timeline_id not in timelines_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Timeline {timeline_id} not found"
        )
    
    timeline = timelines_db[timeline_id]
    track = find_track(timeline, request.track_id)
    
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Track {request.track_id} not found"
        )
    
    clip = TimelineClip(
        id=generate_id("clip"),
        track_id=request.track_id,
        clip_type=request.clip_type,
        name=request.name,
        start_time=request.start_time,
        duration=request.duration,
        media_url=request.media_url,
        motion_parameters=request.motion_parameters,
        keyframes=request.keyframes,
        volume=request.volume,
        effects=request.effects,
        metadata=request.metadata or {}
    )
    
    track.clips.append(clip)
    timeline.updated_at = datetime.now()
    
    return clip


@router.put("/{timeline_id}/clip/{clip_id}", response_model=TimelineClip)
async def update_clip(timeline_id: str, clip_id: str, request: UpdateClipRequest):
    """Update clip settings"""
    if timeline_id not in timelines_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Timeline {timeline_id} not found"
        )
    
    timeline = timelines_db[timeline_id]
    result = find_clip(timeline, clip_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clip {clip_id} not found"
        )
    
    track, clip = result
    
    # Update fields
    if request.name is not None:
        clip.name = request.name
    if request.start_time is not None:
        clip.start_time = request.start_time
    if request.duration is not None:
        clip.duration = request.duration
    if request.motion_parameters is not None:
        clip.motion_parameters = request.motion_parameters
    if request.keyframes is not None:
        clip.keyframes = request.keyframes
    if request.volume is not None:
        clip.volume = request.volume
    if request.fade_in is not None:
        clip.fade_in = request.fade_in
    if request.fade_out is not None:
        clip.fade_out = request.fade_out
    if request.effects is not None:
        clip.effects = request.effects
    if request.locked is not None:
        clip.locked = request.locked
    if request.metadata is not None:
        clip.metadata.update(request.metadata)
    
    timeline.updated_at = datetime.now()
    
    return clip


@router.delete("/{timeline_id}/clip/{clip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_clip(timeline_id: str, clip_id: str):
    """Delete clip from track"""
    if timeline_id not in timelines_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Timeline {timeline_id} not found"
        )
    
    timeline = timelines_db[timeline_id]
    result = find_clip(timeline, clip_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clip {clip_id} not found"
        )
    
    track, clip = result
    track.clips.remove(clip)
    timeline.updated_at = datetime.now()
    
    return None


@router.post("/{timeline_id}/export")
async def export_timeline(timeline_id: str, request: ExportTimelineRequest):
    """
    Export timeline in various formats
    
    Supports: JSON, EDL, XML, CSV
    """
    if timeline_id not in timelines_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Timeline {timeline_id} not found"
        )
    
    timeline = timelines_db[timeline_id]
    
    if request.format == ExportFormat.JSON:
        # Export as JSON
        export_data = timeline.dict()
        if not request.include_metadata:
            export_data.pop('metadata', None)
        
        return {
            "format": "json",
            "filename": f"{timeline.name}.json",
            "data": export_data
        }
    
    elif request.format == ExportFormat.EDL:
        # Export as EDL (Edit Decision List)
        edl_lines = [
            f"TITLE: {timeline.name}",
            f"FCM: NON-DROP FRAME",
            ""
        ]
        
        event_num = 1
        for track in timeline.tracks:
            for clip in track.clips:
                start_tc = f"{int(clip.start_time//60):02d}:{int(clip.start_time%60):02d}:{int((clip.start_time%1)*timeline.fps):02d}"
                end_time = clip.start_time + clip.duration
                end_tc = f"{int(end_time//60):02d}:{int(end_time%60):02d}:{int((end_time%1)*timeline.fps):02d}"
                
                edl_lines.append(f"{event_num:03d}  {track.name}  V  C  {start_tc}  {end_tc}  00:00:00:00  {end_tc}")
                edl_lines.append(f"* FROM CLIP NAME: {clip.name}")
                event_num += 1
        
        return {
            "format": "edl",
            "filename": f"{timeline.name}.edl",
            "data": "\n".join(edl_lines)
        }
    
    elif request.format == ExportFormat.XML:
        # Export as XML (FCP XML format)
        # Simplified version
        return {
            "format": "xml",
            "filename": f"{timeline.name}.xml",
            "data": f'<?xml version="1.0"?><timeline name="{timeline.name}" duration="{timeline.duration}" />'
        }
    
    elif request.format == ExportFormat.CSV:
        # Export as CSV
        csv_lines = ["Track,Clip,Type,Start,Duration,Media"]
        for track in timeline.tracks:
            for clip in track.clips:
                csv_lines.append(f'"{track.name}","{clip.name}","{clip.clip_type}",{clip.start_time},{clip.duration},"{clip.media_url or ""}"')
        
        return {
            "format": "csv",
            "filename": f"{timeline.name}.csv",
            "data": "\n".join(csv_lines)
        }


@router.get("/{timeline_id}/preview")
async def generate_preview(timeline_id: str):
    """
    Generate timeline preview
    
    Returns preview metadata and frame references
    """
    if timeline_id not in timelines_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Timeline {timeline_id} not found"
        )
    
    timeline = timelines_db[timeline_id]
    
    # Generate preview data
    preview_data = {
        "timeline_id": timeline_id,
        "duration": timeline.duration,
        "fps": timeline.fps,
        "total_frames": int(timeline.duration * timeline.fps),
        "tracks": len(timeline.tracks),
        "clips": sum(len(track.clips) for track in timeline.tracks),
        "preview_url": f"/media/timeline/{timeline_id}/preview.mp4",
        "thumbnail_url": f"/media/timeline/{timeline_id}/thumb.jpg"
    }
    
    return preview_data
