"""
Placement Router - Camera & Scene Positioning System
Priority #7.2 - Camera positions, Scene layouts, 3D coordinates

Features:
- Camera position management
- Scene layout configurations
- 3D coordinate snapping
- Placement presets
- Character/Object positioning

Endpoints:
- GET /api/v1/placements/scenes - List all scenes
- POST /api/v1/placements/scenes - Create scene
- GET /api/v1/placements/scenes/{scene_id} - Get scene details
- PATCH /api/v1/placements/scenes/{scene_id} - Update scene
- GET /api/v1/placements/cameras - List camera positions
- POST /api/v1/placements/cameras - Create camera position
- DELETE /api/v1/placements/cameras/{camera_id} - Delete camera
"""

from typing import List, Dict, Optional, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from core.security import get_api_key
from core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/api/v1/placements",
    tags=["Placements"],
    dependencies=[Depends(get_api_key)],
)


# ===== Pydantic Models =====

class Vector3D(BaseModel):
    """3D coordinate vector"""
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    z: float = Field(..., description="Z coordinate")


class CameraPosition(BaseModel):
    """Camera position and orientation"""
    name: str = Field(..., description="Camera name")
    position: Vector3D = Field(..., description="Camera position")
    rotation: Vector3D = Field(..., description="Camera rotation (Euler angles)")
    fov: float = Field(60.0, description="Field of view in degrees")
    preset: Optional[str] = Field(None, description="Preset type (close-up, wide, aerial)")


class SceneObject(BaseModel):
    """Object in scene"""
    id: str = Field(..., description="Object ID")
    name: str = Field(..., description="Object name")
    type: str = Field(..., description="Object type (character, prop, light)")
    position: Vector3D = Field(..., description="Object position")
    rotation: Vector3D = Field(default_factory=lambda: Vector3D(x=0, y=0, z=0), description="Object rotation")
    scale: Vector3D = Field(default_factory=lambda: Vector3D(x=1, y=1, z=1), description="Object scale")


class SceneLayout(BaseModel):
    """Scene layout configuration"""
    scene_id: str = Field(..., description="Unique scene ID")
    name: str = Field(..., description="Scene name")
    description: Optional[str] = Field(None, description="Scene description")
    cameras: List[CameraPosition] = Field(default_factory=list, description="Camera positions")
    objects: List[SceneObject] = Field(default_factory=list, description="Scene objects")
    grid_size: float = Field(1.0, description="Grid snap size")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CreateSceneRequest(BaseModel):
    """Request to create new scene"""
    name: str = Field(..., description="Scene name")
    description: Optional[str] = Field(None, description="Scene description")
    grid_size: float = Field(1.0, ge=0.1, le=10.0, description="Grid snap size")


class UpdateSceneRequest(BaseModel):
    """Request to update scene"""
    name: Optional[str] = Field(None, description="Scene name")
    description: Optional[str] = Field(None, description="Scene description")
    grid_size: Optional[float] = Field(None, ge=0.1, le=10.0, description="Grid snap size")
    cameras: Optional[List[CameraPosition]] = Field(None, description="Camera positions")
    objects: Optional[List[SceneObject]] = Field(None, description="Scene objects")


class CreateCameraRequest(BaseModel):
    """Request to create camera position"""
    scene_id: str = Field(..., description="Scene ID")
    name: str = Field(..., description="Camera name")
    position: Vector3D = Field(..., description="Camera position")
    rotation: Vector3D = Field(..., description="Camera rotation")
    fov: float = Field(60.0, ge=10.0, le=120.0, description="Field of view")
    preset: Optional[str] = Field(None, description="Preset type")


# ===== In-Memory Storage (Replace with database in production) =====

scenes_db: Dict[str, SceneLayout] = {}
cameras_db: Dict[str, CameraPosition] = {}


# ===== Endpoints =====

@router.get("/scenes", response_model=List[SceneLayout])
async def list_scenes(
    skip: int = Query(0, ge=0, description="Skip N scenes"),
    limit: int = Query(50, ge=1, le=100, description="Limit results")
):
    """
    List all scene layouts
    
    Returns list of scenes with pagination
    """
    try:
        all_scenes = list(scenes_db.values())
        # Sort by updated_at descending
        all_scenes.sort(key=lambda s: s.updated_at, reverse=True)
        
        return all_scenes[skip:skip + limit]
        
    except Exception as e:
        logger.error(f"Error listing scenes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scenes", response_model=SceneLayout)
async def create_scene(request: CreateSceneRequest):
    """
    Create new scene layout
    
    Returns created scene with generated ID
    """
    try:
        import uuid
        scene_id = f"scene-{uuid.uuid4().hex[:8]}"
        
        scene = SceneLayout(
            scene_id=scene_id,
            name=request.name,
            description=request.description,
            grid_size=request.grid_size,
        )
        
        scenes_db[scene_id] = scene
        logger.info(f"Created scene: {scene_id} - {request.name}")
        
        return scene
        
    except Exception as e:
        logger.error(f"Error creating scene: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scenes/{scene_id}", response_model=SceneLayout)
async def get_scene(scene_id: str):
    """
    Get scene details by ID
    
    Returns full scene layout with cameras and objects
    """
    if scene_id not in scenes_db:
        raise HTTPException(status_code=404, detail=f"Scene not found: {scene_id}")
    
    return scenes_db[scene_id]


@router.patch("/scenes/{scene_id}", response_model=SceneLayout)
async def update_scene(scene_id: str, request: UpdateSceneRequest):
    """
    Update scene layout
    
    Allows partial updates of name, description, cameras, objects
    """
    if scene_id not in scenes_db:
        raise HTTPException(status_code=404, detail=f"Scene not found: {scene_id}")
    
    try:
        scene = scenes_db[scene_id]
        
        # Update fields
        if request.name is not None:
            scene.name = request.name
        if request.description is not None:
            scene.description = request.description
        if request.grid_size is not None:
            scene.grid_size = request.grid_size
        if request.cameras is not None:
            scene.cameras = request.cameras
        if request.objects is not None:
            scene.objects = request.objects
        
        scene.updated_at = datetime.utcnow()
        logger.info(f"Updated scene: {scene_id}")
        
        return scene
        
    except Exception as e:
        logger.error(f"Error updating scene: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/scenes/{scene_id}")
async def delete_scene(scene_id: str):
    """
    Delete scene layout
    
    Returns success message
    """
    if scene_id not in scenes_db:
        raise HTTPException(status_code=404, detail=f"Scene not found: {scene_id}")
    
    try:
        del scenes_db[scene_id]
        logger.info(f"Deleted scene: {scene_id}")
        
        return {"success": True, "message": f"Scene {scene_id} deleted"}
        
    except Exception as e:
        logger.error(f"Error deleting scene: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cameras", response_model=List[CameraPosition])
async def list_cameras(
    scene_id: Optional[str] = Query(None, description="Filter by scene ID")
):
    """
    List all camera positions
    
    Optionally filter by scene_id
    """
    try:
        if scene_id:
            if scene_id not in scenes_db:
                raise HTTPException(status_code=404, detail=f"Scene not found: {scene_id}")
            
            scene = scenes_db[scene_id]
            return scene.cameras
        
        # Return all cameras from all scenes
        all_cameras = []
        for scene in scenes_db.values():
            all_cameras.extend(scene.cameras)
        
        return all_cameras
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing cameras: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cameras", response_model=CameraPosition)
async def create_camera(request: CreateCameraRequest):
    """
    Create new camera position in scene
    
    Returns created camera
    """
    if request.scene_id not in scenes_db:
        raise HTTPException(status_code=404, detail=f"Scene not found: {request.scene_id}")
    
    try:
        scene = scenes_db[request.scene_id]
        
        camera = CameraPosition(
            name=request.name,
            position=request.position,
            rotation=request.rotation,
            fov=request.fov,
            preset=request.preset,
        )
        
        scene.cameras.append(camera)
        scene.updated_at = datetime.utcnow()
        
        logger.info(f"Created camera in scene {request.scene_id}: {request.name}")
        
        return camera
        
    except Exception as e:
        logger.error(f"Error creating camera: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cameras/{scene_id}/{camera_name}")
async def delete_camera(scene_id: str, camera_name: str):
    """
    Delete camera from scene
    
    Returns success message
    """
    if scene_id not in scenes_db:
        raise HTTPException(status_code=404, detail=f"Scene not found: {scene_id}")
    
    try:
        scene = scenes_db[scene_id]
        
        # Find and remove camera
        initial_count = len(scene.cameras)
        scene.cameras = [c for c in scene.cameras if c.name != camera_name]
        
        if len(scene.cameras) == initial_count:
            raise HTTPException(status_code=404, detail=f"Camera not found: {camera_name}")
        
        scene.updated_at = datetime.utcnow()
        logger.info(f"Deleted camera from scene {scene_id}: {camera_name}")
        
        return {"success": True, "message": f"Camera {camera_name} deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting camera: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/presets")
async def get_camera_presets():
    """
    Get camera preset templates
    
    Returns list of preset configurations
    """
    presets = [
        {
            "name": "Close-up",
            "position": {"x": 0, "y": 1.6, "z": 1.5},
            "rotation": {"x": 0, "y": 180, "z": 0},
            "fov": 50,
        },
        {
            "name": "Medium Shot",
            "position": {"x": 0, "y": 1.6, "z": 3.0},
            "rotation": {"x": 0, "y": 180, "z": 0},
            "fov": 60,
        },
        {
            "name": "Wide Shot",
            "position": {"x": 0, "y": 2.0, "z": 6.0},
            "rotation": {"x": 10, "y": 180, "z": 0},
            "fov": 70,
        },
        {
            "name": "Over-the-Shoulder",
            "position": {"x": -0.5, "y": 1.5, "z": 1.0},
            "rotation": {"x": 0, "y": 135, "z": 0},
            "fov": 55,
        },
        {
            "name": "Top-Down",
            "position": {"x": 0, "y": 5.0, "z": 0},
            "rotation": {"x": 90, "y": 0, "z": 0},
            "fov": 65,
        },
        {
            "name": "Dutch Angle",
            "position": {"x": 1.0, "y": 1.6, "z": 2.0},
            "rotation": {"x": 0, "y": 150, "z": 15},
            "fov": 60,
        },
    ]
    
    return {"presets": presets}
