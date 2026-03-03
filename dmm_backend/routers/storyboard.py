"""
Storyboard API Router

Provides endpoints for storyboard management and shot sequencing.
Supports CRUD operations, shot reordering, and PDF export.

Author: Peace Script Team
Date: 20 November 2568
Version: 1.0
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from documents_storyboard import Storyboard, StoryboardShot, CameraAngle, ShotType

router = APIRouter(prefix="/api/storyboard", tags=["storyboard"])


# ============================================================================
# Schemas
# ============================================================================

class StoryboardCreate(BaseModel):
    """Create storyboard request"""
    project_id: str
    title: str
    description: Optional[str] = None
    shots: List[StoryboardShot] = []


class StoryboardUpdate(BaseModel):
    """Update storyboard request"""
    title: Optional[str] = None
    description: Optional[str] = None
    shots: Optional[List[StoryboardShot]] = None


class ShotCreate(BaseModel):
    """Create/add shot request"""
    shot_number: int = Field(..., ge=1)
    description: str
    camera_angle: CameraAngle = CameraAngle.MEDIUM
    shot_type: ShotType = ShotType.MASTER
    duration: float = Field(default=3.0, ge=0.1)
    dialogue: Optional[str] = None
    action: Optional[str] = None
    notes: Optional[str] = None
    characters: List[str] = []
    thumbnail_url: Optional[str] = None
    scene_id: Optional[str] = None


class ShotUpdate(BaseModel):
    """Update shot request"""
    shot_number: Optional[int] = None
    description: Optional[str] = None
    camera_angle: Optional[CameraAngle] = None
    shot_type: Optional[ShotType] = None
    duration: Optional[float] = None
    dialogue: Optional[str] = None
    action: Optional[str] = None
    notes: Optional[str] = None
    characters: Optional[List[str]] = None
    thumbnail_url: Optional[str] = None


class ShotReorder(BaseModel):
    """Reorder shots request"""
    shot_orders: List[dict]  # [{"shot_id": "...", "new_number": 1}, ...]


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/", response_model=dict, status_code=201)
async def create_storyboard(data: StoryboardCreate):
    """
    Create a new storyboard
    
    **Request Body:**
    - project_id: Link to narrative project
    - title: Storyboard title
    - description: Optional description
    - shots: Initial shots (optional)
    """
    # Generate unique ID
    storyboard_id = f"storyboard_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{data.project_id[:8]}"
    
    # Create storyboard
    storyboard = Storyboard(
        storyboard_id=storyboard_id,
        project_id=data.project_id,
        title=data.title,
        description=data.description,
        shots=data.shots
    )
    
    # Update stats
    storyboard.update_stats()
    
    # Save to database
    await storyboard.insert()
    
    return {
        "message": "Storyboard created successfully",
        "storyboard_id": storyboard.storyboard_id,
        "total_shots": storyboard.total_shots,
        "total_duration": storyboard.total_duration
    }


@router.get("/", response_model=List[dict])
async def list_storyboards(
    project_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """
    List all storyboards
    
    **Query Parameters:**
    - project_id: Filter by project
    - skip: Pagination offset
    - limit: Items per page
    """
    query = {}
    if project_id:
        query["project_id"] = project_id
    
    storyboards = await Storyboard.find(query).skip(skip).limit(limit).to_list()
    
    return [
        {
            "storyboard_id": sb.storyboard_id,
            "project_id": sb.project_id,
            "title": sb.title,
            "description": sb.description,
            "total_shots": sb.total_shots,
            "total_duration": sb.total_duration,
            "created_at": sb.created_at,
            "updated_at": sb.updated_at
        }
        for sb in storyboards
    ]


@router.get("/{storyboard_id}", response_model=dict)
async def get_storyboard(storyboard_id: str):
    """
    Get storyboard by ID with all shots
    """
    storyboard = await Storyboard.find_one({"storyboard_id": storyboard_id})
    
    if not storyboard:
        raise HTTPException(status_code=404, detail="Storyboard not found")
    
    return {
        "storyboard_id": storyboard.storyboard_id,
        "project_id": storyboard.project_id,
        "title": storyboard.title,
        "description": storyboard.description,
        "shots": [shot.dict() for shot in storyboard.shots],
        "total_shots": storyboard.total_shots,
        "total_duration": storyboard.total_duration,
        "created_at": storyboard.created_at,
        "updated_at": storyboard.updated_at
    }


@router.put("/{storyboard_id}", response_model=dict)
async def update_storyboard(storyboard_id: str, data: StoryboardUpdate):
    """
    Update storyboard metadata and shots
    """
    storyboard = await Storyboard.find_one({"storyboard_id": storyboard_id})
    
    if not storyboard:
        raise HTTPException(status_code=404, detail="Storyboard not found")
    
    # Update fields
    if data.title is not None:
        storyboard.title = data.title
    if data.description is not None:
        storyboard.description = data.description
    if data.shots is not None:
        storyboard.shots = data.shots
    
    # Update stats and timestamp
    storyboard.update_stats()
    
    await storyboard.save()
    
    return {
        "message": "Storyboard updated successfully",
        "storyboard_id": storyboard.storyboard_id,
        "total_shots": storyboard.total_shots
    }


@router.delete("/{storyboard_id}", response_model=dict)
async def delete_storyboard(storyboard_id: str):
    """
    Delete storyboard
    """
    storyboard = await Storyboard.find_one({"storyboard_id": storyboard_id})
    
    if not storyboard:
        raise HTTPException(status_code=404, detail="Storyboard not found")
    
    await storyboard.delete()
    
    return {
        "message": "Storyboard deleted successfully",
        "storyboard_id": storyboard_id
    }


@router.post("/{storyboard_id}/shots", response_model=dict)
async def add_shot(storyboard_id: str, shot: ShotCreate):
    """
    Add new shot to storyboard
    """
    storyboard = await Storyboard.find_one({"storyboard_id": storyboard_id})
    
    if not storyboard:
        raise HTTPException(status_code=404, detail="Storyboard not found")
    
    # Generate shot ID
    shot_id = f"shot_{storyboard_id}_{shot.shot_number}_{datetime.utcnow().strftime('%H%M%S')}"
    
    # Create shot object
    new_shot = StoryboardShot(
        shot_id=shot_id,
        **shot.dict()
    )
    
    # Add to shots array
    storyboard.shots.append(new_shot)
    storyboard.update_stats()
    
    await storyboard.save()
    
    return {
        "message": "Shot added successfully",
        "shot_id": shot_id,
        "total_shots": storyboard.total_shots
    }


@router.put("/{storyboard_id}/shots/{shot_id}", response_model=dict)
async def update_shot(storyboard_id: str, shot_id: str, data: ShotUpdate):
    """
    Update specific shot
    """
    storyboard = await Storyboard.find_one({"storyboard_id": storyboard_id})
    
    if not storyboard:
        raise HTTPException(status_code=404, detail="Storyboard not found")
    
    # Find shot
    shot_index = next((i for i, s in enumerate(storyboard.shots) if s.shot_id == shot_id), None)
    
    if shot_index is None:
        raise HTTPException(status_code=404, detail="Shot not found")
    
    # Update shot fields
    shot = storyboard.shots[shot_index]
    for field, value in data.dict(exclude_unset=True).items():
        setattr(shot, field, value)
    
    storyboard.shots[shot_index] = shot
    storyboard.update_stats()
    
    await storyboard.save()
    
    return {
        "message": "Shot updated successfully",
        "shot_id": shot_id
    }


@router.delete("/{storyboard_id}/shots/{shot_id}", response_model=dict)
async def delete_shot(storyboard_id: str, shot_id: str):
    """
    Delete shot from storyboard
    """
    storyboard = await Storyboard.find_one({"storyboard_id": storyboard_id})
    
    if not storyboard:
        raise HTTPException(status_code=404, detail="Storyboard not found")
    
    # Filter out shot
    original_count = len(storyboard.shots)
    storyboard.shots = [s for s in storyboard.shots if s.shot_id != shot_id]
    
    if len(storyboard.shots) == original_count:
        raise HTTPException(status_code=404, detail="Shot not found")
    
    storyboard.update_stats()
    await storyboard.save()
    
    return {
        "message": "Shot deleted successfully",
        "shot_id": shot_id,
        "total_shots": storyboard.total_shots
    }


@router.post("/{storyboard_id}/reorder", response_model=dict)
async def reorder_shots(storyboard_id: str, data: ShotReorder):
    """
    Reorder shots in storyboard
    
    **Request Body:**
    ```json
    {
        "shot_orders": [
            {"shot_id": "shot_1", "new_number": 3},
            {"shot_id": "shot_2", "new_number": 1},
            {"shot_id": "shot_3", "new_number": 2}
        ]
    }
    ```
    """
    storyboard = await Storyboard.find_one({"storyboard_id": storyboard_id})
    
    if not storyboard:
        raise HTTPException(status_code=404, detail="Storyboard not found")
    
    # Create mapping of shot_id to new number
    order_map = {item["shot_id"]: item["new_number"] for item in data.shot_orders}
    
    # Update shot numbers
    for shot in storyboard.shots:
        if shot.shot_id in order_map:
            shot.shot_number = order_map[shot.shot_id]
    
    # Sort shots by new number
    storyboard.shots.sort(key=lambda s: s.shot_number)
    
    storyboard.updated_at = datetime.utcnow()
    await storyboard.save()
    
    return {
        "message": "Shots reordered successfully",
        "total_shots": len(storyboard.shots)
    }


@router.get("/{storyboard_id}/export", response_model=dict)
async def export_storyboard(
    storyboard_id: str,
    format: str = Query("json", regex="^(json|csv|pdf)$")
):
    """
    Export storyboard
    
    **Query Parameters:**
    - format: Export format (json, csv, pdf)
    
    **Note:** PDF export requires additional setup
    """
    storyboard = await Storyboard.find_one({"storyboard_id": storyboard_id})
    
    if not storyboard:
        raise HTTPException(status_code=404, detail="Storyboard not found")
    
    if format == "json":
        return {
            "format": "json",
            "data": {
                "storyboard_id": storyboard.storyboard_id,
                "project_id": storyboard.project_id,
                "title": storyboard.title,
                "shots": [shot.dict() for shot in storyboard.shots],
                "total_duration": storyboard.total_duration
            }
        }
    
    elif format == "csv":
        # Simple CSV data
        csv_rows = []
        csv_rows.append("Shot #,Description,Camera Angle,Duration,Dialogue,Notes")
        for shot in storyboard.shots:
            csv_rows.append(f"{shot.shot_number},{shot.description},{shot.camera_angle},{shot.duration},{shot.dialogue or ''},{shot.notes or ''}")
        
        return {
            "format": "csv",
            "data": "\n".join(csv_rows)
        }
    
    elif format == "pdf":
        # PDF export placeholder
        return {
            "format": "pdf",
            "message": "PDF export not yet implemented",
            "note": "Use external PDF generation library"
        }
    
    return {"error": "Invalid format"}
