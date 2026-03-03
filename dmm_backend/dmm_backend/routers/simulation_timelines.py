from typing import List, Optional, Any

from fastapi import APIRouter, HTTPException, Depends, Body, Response, Request
from documents_extra import SimulationTimeline  # type: ignore
from core.logging_config import get_logger
logger = get_logger(__name__)
from beanie.exceptions import CollectionWasNotInitialized
from core.security import get_api_key
from pydantic import BaseModel
from config import settings
try:
    from database import get_motor_db as _get_db
except Exception:
    from motor.motor_asyncio import AsyncIOMotorClient  # type: ignore
    from config import settings as _settings  # type: ignore

    def _get_db():
        client = AsyncIOMotorClient(_settings.MONGO_URI)
        return client.get_database(_settings.MONGO_DB_NAME)
from core.ratelimit import limiter
from bson import ObjectId
from beanie.exceptions import CollectionWasNotInitialized

router = APIRouter(
    prefix="/api/v1/simulation-timelines",
    tags=["Simulation Timelines"],
    dependencies=[Depends(get_api_key)],
)


class SimulationTimelineUpdate(BaseModel):
    model_id: Optional[str] = None
    simulation_id: Optional[str] = None
    timeline_type: Optional[str] = None
    events: Optional[list] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    playback_mode: Optional[str] = None
    meta: Optional[dict] = None

    class Config:
        extra = "ignore"


@router.get("/", response_model=List[dict])
async def list_timelines(
    response: Response,
    model_id: Optional[str] = None,
    type: Optional[str] = None,
    from_: Optional[str] = None,
    to: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    after_id: Optional[str] = None,
):
    logger.info(f"SimulationTimeline in router: {SimulationTimeline.__module__}@{id(SimulationTimeline)}")
    try:
        db = _get_db()
        coll = db.get_collection('simulation_timelines')
        query = {"model_id": model_id} if model_id else {}
        if type:
            query["timeline_type"] = type
        # date range on start_time
        if from_ or to:
            date_filter = {}
            try:
                if from_:
                    from datetime import datetime
                    date_filter["$gte"] = datetime.fromisoformat(from_).replace(hour=0, minute=0, second=0, microsecond=0)
                if to:
                    from datetime import datetime
                    date_filter["$lte"] = datetime.fromisoformat(to).replace(hour=23, minute=59, second=59, microsecond=999999)
            except Exception:
                pass
            if date_filter:
                query["start_time"] = date_filter
        # Optional cursor-based pagination: filter by _id < after_id when provided
        if after_id:
            try:
                query["_id"] = {"$lt": ObjectId(after_id)}
            except Exception:
                query["_id"] = {"$lt": after_id}
        # Stable sort by _id descending for consistent pagination
        page_limit = max(1, int(limit))
        cursor = (
            coll.find(query)
            .sort("_id", -1)
            .skip(max(0, int(skip)))
            .limit(page_limit)
        )
        docs = await cursor.to_list(length=page_limit)
        docs = docs[:page_limit]
        for d in docs:
            if "_id" in d:
                d["_id"] = str(d["_id"]) 
        # Optional simple pagination headers
        if response is not None:
            try:
                total = await coll.count_documents(query)
            except Exception:
                total = -1
            response.headers["X-Page-Skip"] = str(skip)
            response.headers["X-Page-Limit"] = str(limit)
            response.headers["X-Returned"] = str(len(docs))
            response.headers["X-Next-Skip"] = str(skip + len(docs))
            if total >= 0:
                response.headers["X-Total-Count"] = str(total)
                has_more = (skip + len(docs)) < total
                response.headers["X-Has-More"] = "true" if has_more else "false"
            if docs:
                response.headers["X-Next-After-Id"] = docs[-1]["_id"]
        return docs
    except Exception as e:
        logger.exception("SimulationTimeline list failed: %s", e)
        raise HTTPException(status_code=500, detail=f"SimulationTimeline error: {e}")


@router.post("/", response_model=dict, status_code=201)
@limiter.limit("30/minute")
async def create_timeline(request: Request, timeline: dict = Body(...)):
    db = _get_db()
    coll = db.get_collection('simulation_timelines')
    # Insert via Motor to avoid Beanie collection init requirements in test contexts
    try:
        res = await coll.insert_one(timeline)
        raw = await coll.find_one({"_id": res.inserted_id})
    except Exception:
        # Fallback to Beanie path if Motor insert fails for any reason
        try:
            doc = SimulationTimeline(**timeline)
            await doc.insert()
            raw = await coll.find_one({"_id": doc.id})
        except CollectionWasNotInitialized:
            raw = timeline
    if raw and "_id" in raw:
        raw["_id"] = str(raw["_id"]) 
    return raw or {}


@router.get("/{timeline_id}", response_model=dict)
async def get_timeline(timeline_id: str):
    db = _get_db()
    coll = db.get_collection('simulation_timelines')
    try:
        raw = await coll.find_one({"_id": ObjectId(timeline_id)})
    except Exception:
        raw = await coll.find_one({"_id": timeline_id})
    if not raw:
        raise HTTPException(status_code=404, detail="Timeline not found")
    if "_id" in raw:
        raw["_id"] = str(raw["_id"]) 
    return raw


@router.delete("/{timeline_id}", status_code=204)
@limiter.limit("60/minute")
async def delete_timeline(request: Request, timeline_id: str):
    doc = await SimulationTimeline.get(timeline_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Timeline not found")
    await doc.delete()


@router.patch("/{timeline_id}", response_model=dict)
@limiter.limit("60/minute")
async def patch_timeline(request: Request, timeline_id: str, patch: SimulationTimelineUpdate):
    doc = await SimulationTimeline.get(timeline_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Timeline not found")
    updates = patch.model_dump(exclude_unset=True)
    for k, v in updates.items():
        setattr(doc, k, v)
    await doc.save()
    db = _get_db()
    coll = db.get_collection('simulation_timelines')
    raw = await coll.find_one({"_id": doc.id})
    if raw and "_id" in raw:
        raw["_id"] = str(raw["_id"]) 
    return raw or {}


@router.put("/{timeline_id}", response_model=dict)
@limiter.limit("30/minute")
async def replace_timeline(request: Request, timeline_id: str, timeline: Any):
    existing = await SimulationTimeline.get(timeline_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Timeline not found")
    if isinstance(timeline, dict):
        doc = SimulationTimeline(**timeline)
    else:
        doc = timeline
    doc.id = existing.id
    await doc.replace()
    db = _get_db()
    coll = db.get_collection('simulation_timelines')
    raw = await coll.find_one({"_id": doc.id})
    if raw and "_id" in raw:
        raw["_id"] = str(raw["_id"]) 
    return raw or {}


# ===========================
# ADVANCED TIMELINE FEATURES
# ===========================

class TimelineEventRequest(BaseModel):
    """Request model for adding event to timeline"""
    event_id: str
    event_type: str  # simulation_event, branch_point, marker
    timestamp: float  # Relative time in seconds
    duration: Optional[float] = None
    data: dict = {}
    
    class Config:
        extra = "ignore"


class PlaybackControlRequest(BaseModel):
    """Request model for playback control"""
    action: str  # play, pause, stop, seek, fast_forward, rewind
    timestamp: Optional[float] = None  # For seek action
    speed: Optional[float] = 1.0  # Playback speed (0.5x, 1x, 2x)
    
    class Config:
        extra = "ignore"


class TimelineMarkerRequest(BaseModel):
    """Request model for adding timeline marker"""
    marker_id: str
    timestamp: float  # Relative time in seconds
    label: str
    marker_type: str  # bookmark, annotation, branch_point, key_moment
    color: Optional[str] = "#FFD700"  # Default gold color
    description: Optional[str] = None
    metadata: Optional[dict] = {}
    
    class Config:
        extra = "ignore"


@router.post("/{timeline_id}/events", response_model=dict)
@limiter.limit("60/minute")
async def add_event_to_timeline(
    request: Request,
    timeline_id: str,
    event: TimelineEventRequest = Body(...)
):
    """
    Add an event to the timeline's event list.
    
    This endpoint allows you to append simulation events, branch points,
    or custom markers to a timeline's event sequence.
    
    Args:
        timeline_id: ID of the timeline to modify
        event: Event data to add
        
    Returns:
        Updated timeline with new event added
        
    Example:
        POST /api/v1/simulation-timelines/{id}/events
        {
            "event_id": "EVT-001",
            "event_type": "simulation_event",
            "timestamp": 5.5,
            "duration": 2.0,
            "data": {"character": "รินรดา", "action": "speak"}
        }
    """
    db = _get_db()
    coll = db.get_collection('simulation_timelines')
    
    # Get existing timeline
    try:
        timeline = await coll.find_one({"_id": ObjectId(timeline_id)})
    except Exception:
        timeline = await coll.find_one({"_id": timeline_id})
    
    if not timeline:
        raise HTTPException(status_code=404, detail="Timeline not found")
    
    # Prepare event data
    event_data = {
        "event_id": event.event_id,
        "event_type": event.event_type,
        "timestamp": event.timestamp,
        "duration": event.duration,
        "data": event.data,
        "added_at": str(__import__("datetime").datetime.now())
    }
    
    # Append to events array
    if "events" not in timeline or timeline["events"] is None:
        timeline["events"] = []
    
    timeline["events"].append(event_data)
    
    # Sort events by timestamp
    timeline["events"].sort(key=lambda e: e.get("timestamp", 0))
    
    # Update timeline
    try:
        await coll.update_one(
            {"_id": ObjectId(timeline_id) if isinstance(timeline["_id"], ObjectId) else timeline_id},
            {"$set": {"events": timeline["events"]}}
        )
    except Exception as e:
        logger.error(f"Failed to update timeline events: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add event: {str(e)}")
    
    # Return updated timeline
    updated = await coll.find_one({"_id": timeline["_id"]})
    if updated and "_id" in updated:
        updated["_id"] = str(updated["_id"])
    
    logger.info(f"Added event {event.event_id} to timeline {timeline_id}")
    return updated or {}


@router.post("/{timeline_id}/playback", response_model=dict)
@limiter.limit("100/minute")
async def control_playback(
    request: Request,
    timeline_id: str,
    control: PlaybackControlRequest = Body(...)
):
    """
    Control timeline playback (play, pause, stop, seek).
    
    This endpoint allows real-time control of timeline playback state,
    including playback speed and seeking to specific timestamps.
    
    Args:
        timeline_id: ID of the timeline to control
        control: Playback control command
        
    Returns:
        Current playback status
        
    Actions:
        - play: Start/resume playback
        - pause: Pause playback
        - stop: Stop and reset to beginning
        - seek: Jump to specific timestamp
        - fast_forward: Increase playback speed
        - rewind: Decrease playback speed or go backwards
        
    Example:
        POST /api/v1/simulation-timelines/{id}/playback
        {
            "action": "seek",
            "timestamp": 10.5,
            "speed": 1.0
        }
    """
    db = _get_db()
    coll = db.get_collection('simulation_timelines')
    
    # Get existing timeline
    try:
        timeline = await coll.find_one({"_id": ObjectId(timeline_id)})
    except Exception:
        timeline = await coll.find_one({"_id": timeline_id})
    
    if not timeline:
        raise HTTPException(status_code=404, detail="Timeline not found")
    
    # Initialize meta if not exists
    if "meta" not in timeline or timeline["meta"] is None:
        timeline["meta"] = {}
    
    # Get current playback state
    playback = timeline["meta"].get("playback", {})
    current_time = playback.get("current_time", 0.0)
    is_playing = playback.get("is_playing", False)
    speed = playback.get("speed", 1.0)
    
    # Process action
    action = control.action.lower()
    
    if action == "play":
        is_playing = True
        logger.info(f"Timeline {timeline_id} playback started")
        
    elif action == "pause":
        is_playing = False
        logger.info(f"Timeline {timeline_id} playback paused at {current_time}s")
        
    elif action == "stop":
        is_playing = False
        current_time = 0.0
        speed = 1.0
        logger.info(f"Timeline {timeline_id} playback stopped")
        
    elif action == "seek":
        if control.timestamp is None:
            raise HTTPException(status_code=400, detail="Timestamp required for seek action")
        current_time = max(0.0, control.timestamp)
        logger.info(f"Timeline {timeline_id} seeked to {current_time}s")
        
    elif action == "fast_forward":
        speed = min(4.0, speed * 2.0)  # Max 4x speed
        logger.info(f"Timeline {timeline_id} speed increased to {speed}x")
        
    elif action == "rewind":
        speed = max(0.25, speed / 2.0)  # Min 0.25x speed
        logger.info(f"Timeline {timeline_id} speed decreased to {speed}x")
        
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action: {action}. Must be one of: play, pause, stop, seek, fast_forward, rewind"
        )
    
    # Apply speed override if provided
    if control.speed is not None:
        speed = max(0.25, min(4.0, control.speed))  # Clamp between 0.25x and 4x
    
    # Update playback state
    playback = {
        "is_playing": is_playing,
        "current_time": current_time,
        "speed": speed,
        "last_action": action,
        "updated_at": str(__import__("datetime").datetime.now())
    }
    
    timeline["meta"]["playback"] = playback
    timeline["playback_mode"] = "playing" if is_playing else "paused"
    
    # Save to database
    try:
        await coll.update_one(
            {"_id": ObjectId(timeline_id) if isinstance(timeline["_id"], ObjectId) else timeline_id},
            {"$set": {
                "meta": timeline["meta"],
                "playback_mode": timeline["playback_mode"]
            }}
        )
    except Exception as e:
        logger.error(f"Failed to update playback state: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to control playback: {str(e)}")
    
    # Return playback status
    return {
        "timeline_id": str(timeline["_id"]),
        "playback": playback,
        "action_performed": action,
        "status": "success"
    }


@router.post("/{timeline_id}/markers", response_model=dict)
@limiter.limit("60/minute")
async def add_marker(
    request: Request,
    timeline_id: str,
    marker: TimelineMarkerRequest = Body(...)
):
    """
    Add a marker to the timeline for annotations, bookmarks, or key moments.
    
    Markers help organize and navigate long timelines by highlighting
    important moments, branch points, or user annotations.
    
    Args:
        timeline_id: ID of the timeline to modify
        marker: Marker data to add
        
    Returns:
        Updated timeline with new marker added
        
    Marker Types:
        - bookmark: User-created navigation point
        - annotation: Note or comment at specific time
        - branch_point: Decision point in simulation
        - key_moment: Significant event or turning point
        
    Example:
        POST /api/v1/simulation-timelines/{id}/markers
        {
            "marker_id": "MRK-001",
            "timestamp": 15.5,
            "label": "Key Decision Point",
            "marker_type": "branch_point",
            "color": "#FF6B6B",
            "description": "Character makes crucial choice",
            "metadata": {"importance": "high"}
        }
    """
    db = _get_db()
    coll = db.get_collection('simulation_timelines')
    
    # Get existing timeline
    try:
        timeline = await coll.find_one({"_id": ObjectId(timeline_id)})
    except Exception:
        timeline = await coll.find_one({"_id": timeline_id})
    
    if not timeline:
        raise HTTPException(status_code=404, detail="Timeline not found")
    
    # Initialize meta if not exists
    if "meta" not in timeline or timeline["meta"] is None:
        timeline["meta"] = {}
    
    if "markers" not in timeline["meta"]:
        timeline["meta"]["markers"] = []
    
    # Check for duplicate marker_id
    existing_ids = [m.get("marker_id") for m in timeline["meta"]["markers"]]
    if marker.marker_id in existing_ids:
        raise HTTPException(
            status_code=400,
            detail=f"Marker with ID {marker.marker_id} already exists in this timeline"
        )
    
    # Prepare marker data
    marker_data = {
        "marker_id": marker.marker_id,
        "timestamp": marker.timestamp,
        "label": marker.label,
        "marker_type": marker.marker_type,
        "color": marker.color,
        "description": marker.description,
        "metadata": marker.metadata,
        "created_at": str(__import__("datetime").datetime.now())
    }
    
    # Add marker
    timeline["meta"]["markers"].append(marker_data)
    
    # Sort markers by timestamp
    timeline["meta"]["markers"].sort(key=lambda m: m.get("timestamp", 0))
    
    # Update timeline
    try:
        await coll.update_one(
            {"_id": ObjectId(timeline_id) if isinstance(timeline["_id"], ObjectId) else timeline_id},
            {"$set": {"meta": timeline["meta"]}}
        )
    except Exception as e:
        logger.error(f"Failed to add marker: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add marker: {str(e)}")
    
    # Return updated timeline
    updated = await coll.find_one({"_id": timeline["_id"]})
    if updated and "_id" in updated:
        updated["_id"] = str(updated["_id"])
    
    logger.info(f"Added marker {marker.marker_id} to timeline {timeline_id} at {marker.timestamp}s")
    return updated or {}
