"""
Shot Router - API endpoints for shot management and generation

Handles shot-level operations including:
- CRUD operations for shots
- AI-based shot generation from scene descriptions
- Batch shot generation for scene groups
- Shot reordering and organization

Author: Peace Script Team
Date: 25 November 2025
Version: 1.0
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from datetime import datetime

from schemas_shot import (
    ShotCreate, ShotUpdate, ShotResponse,
    SceneGroupMetadata, LocationTag, StyleTag
)
from documents_shot import Shot, SceneGroup

router = APIRouter(prefix="/api/shots", tags=["shots"])


# =============================================================================
# SHOT CRUD OPERATIONS
# =============================================================================

@router.post("/", response_model=ShotResponse, status_code=status.HTTP_201_CREATED)
async def create_shot(shot_data: ShotCreate):
    """
    Create a new shot
    
    - **scene_id**: Parent scene ID
    - **shot_number**: Shot number within scene
    - **caption**: Short description (e.g., "@Maria walks...")
    - **camera**: Camera settings (optional)
    """
    try:
        # Generate shot_id
        timestamp = int(datetime.utcnow().timestamp() * 1000)
        import random
        import string
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        shot_id = f"shot_{timestamp}_{random_suffix}"
        
        # Create shot document
        shot = Shot(
            shot_id=shot_id,
            **shot_data.dict()
        )
        
        await shot.insert()
        
        return ShotResponse(
            id=str(shot.id),
            shot_id=shot.shot_id,
            **shot.dict(exclude={'id'})
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create shot: {str(e)}"
        )


@router.get("/{shot_id}", response_model=ShotResponse)
async def get_shot(shot_id: str):
    """Get shot by ID"""
    shot = await Shot.find_one(Shot.shot_id == shot_id)
    if not shot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shot {shot_id} not found"
        )
    
    return ShotResponse(
        id=str(shot.id),
        shot_id=shot.shot_id,
        **shot.dict(exclude={'id'})
    )


@router.get("/scene/{scene_id}", response_model=List[ShotResponse])
async def get_shots_by_scene(scene_id: str):
    """Get all shots for a scene, ordered by shot_number"""
    shots = await Shot.find(Shot.scene_id == scene_id).sort("+shot_number").to_list()
    
    return [
        ShotResponse(
            id=str(shot.id),
            shot_id=shot.shot_id,
            **shot.dict(exclude={'id'})
        )
        for shot in shots
    ]


@router.put("/{shot_id}", response_model=ShotResponse)
async def update_shot(shot_id: str, shot_data: ShotUpdate):
    """Update shot"""
    shot = await Shot.find_one(Shot.shot_id == shot_id)
    if not shot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shot {shot_id} not found"
        )
    
    # Update fields
    update_data = shot_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(shot, key, value)
    
    shot.updated_at = datetime.utcnow()
    await shot.save()
    
    return ShotResponse(
        id=str(shot.id),
        shot_id=shot.shot_id,
        **shot.dict(exclude={'id'})
    )


@router.delete("/{shot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shot(shot_id: str):
    """Delete shot"""
    shot = await Shot.find_one(Shot.shot_id == shot_id)
    if not shot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shot {shot_id} not found"
        )
    
    await shot.delete()


# =============================================================================
# SHOT GENERATION (AI)
# =============================================================================

@router.post("/generate-from-scene")
async def generate_shots_from_scene(
    scene_id: str,
    scene_description: str,
    num_shots: int = 4,
    location_tags: Optional[List[str]] = None,
    style_tags: Optional[List[str]] = None,
    ai_provider: str = "qwen2.5"
):
    """
    Generate shots from scene description using AI
    
    - **scene_id**: Parent scene ID
    - **scene_description**: Scene description/content
    - **num_shots**: Number of shots to generate (default: 4)
    - **location_tags**: Location tags for context
    - **style_tags**: Style tags for visual guidance
    - **ai_provider**: AI model to use (qwen2.5, claude, openai)
    
    Returns list of generated shots with:
    - shot_number
    - caption (e.g., "@Character performs action...")
    - camera settings recommendations
    - prompt for image generation
    
    **DEPRECATED**: This endpoint is no longer supported.
    Use /api/narrative/projects/generate-scene-step instead.
    """
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="This endpoint is deprecated. Please use /api/narrative/projects/generate-scene-step for scene and shot generation."
    )


# =============================================================================
# SHOT REORDERING
# =============================================================================

@router.post("/reorder")
async def reorder_shots(scene_id: str, shot_order: List[str]):
    """
    Reorder shots within a scene
    
    - **scene_id**: Scene ID
    - **shot_order**: List of shot_ids in desired order
    
    Updates shot_number for each shot based on new order
    """
    try:
        shots = await Shot.find(Shot.scene_id == scene_id).to_list()
        
        # Create mapping of shot_id to shot document
        shot_map = {shot.shot_id: shot for shot in shots}
        
        # Update shot numbers based on new order
        for index, shot_id in enumerate(shot_order, start=1):
            if shot_id in shot_map:
                shot = shot_map[shot_id]
                shot.shot_number = index
                shot.updated_at = datetime.utcnow()
                await shot.save()
        
        return {
            "success": True,
            "message": f"Reordered {len(shot_order)} shots in scene {scene_id}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reorder shots: {str(e)}"
        )
