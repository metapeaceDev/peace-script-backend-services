"""
Motion Editor API Router
Generates video from shot data with motion effects based on simulation results

Path: /api/motion/*
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

router = APIRouter(
    prefix="/api/motion",
    tags=["motion-editor"]
)

# ============================================================================
# Request/Response Models
# ============================================================================

class SimulationResultInput(BaseModel):
    """Simulation result from character"""
    character_id: str
    character_name: str
    emotion: str
    actions: List[str]
    dialogue: str
    state_changes: Dict[str, Any]

class GenerateVideoRequest(BaseModel):
    """Request to generate video from shot"""
    shot_id: str
    scene_id: str
    project_id: str
    
    # Shot data
    shot_data: Dict[str, Any]  # camera_angle, movement, duration, description, etc.
    
    # Simulation results (from character behavior)
    simulation_results: List[SimulationResultInput]
    
    # Style preset
    style_preset: str = "Grit"
    
class VideoJobResponse(BaseModel):
    """Video generation job response"""
    job_id: str
    status: str  # queued, processing, completed, failed
    progress: int  # 0-100
    eta_sec: Optional[int] = None
    video_url: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    
    # Metadata
    shot_id: Optional[str] = None
    dominant_emotion: Optional[str] = None
    characters: List[str] = []

# ============================================================================
# Global Job Storage (In production: use Redis/Celery)
# ============================================================================

video_jobs = {}  # job_id -> VideoJobResponse

# ============================================================================
# Helper Functions
# ============================================================================

def calculate_motion_parameters(emotion: str, intensity: str = "medium") -> dict:
    """
    Calculate camera motion parameters based on emotion
    
    Args:
        emotion: Dominant emotion (joy, sadness, anger, fear, calm, compassion)
        intensity: high, medium, low
        
    Returns:
        dict: Motion parameters for video generation
    """
    motion_params = {
        'zoom_start': 1.0,
        'zoom_end': 1.0,
        'move_x': 0.0,
        'move_y': 0.0,
        'rotate_start': 0.0,
        'rotate_end': 0.0,
        'speed': 1.0
    }
    
    # Emotion-based motion mapping
    if emotion == 'joy':
        motion_params['zoom_end'] = 1.2  # Zoom in for joy
        motion_params['move_x'] = 10  # Slight pan right
    elif emotion == 'sadness':
        motion_params['zoom_end'] = 0.9  # Zoom out for sadness
        motion_params['move_y'] = -15  # Tilt down
    elif emotion == 'anger':
        motion_params['move_x'] = 15  # Dynamic pan
        motion_params['speed'] = 1.3  # Faster movement
    elif emotion == 'fear':
        motion_params['move_y'] = 20  # Tilt up (looking up in fear)
        motion_params['rotate_end'] = 5  # Slight rotation (Dutch angle)
    elif emotion == 'calm':
        motion_params['zoom_end'] = 1.05  # Gentle zoom
        motion_params['speed'] = 0.8  # Slower, calmer movement
    elif emotion == 'compassion':
        motion_params['zoom_end'] = 1.15  # Zoom in to show emotion
        motion_params['move_y'] = 10  # Gentle tilt up
    
    # Intensity adjustments
    if intensity == 'high':
        motion_params['speed'] *= 1.3
    elif intensity == 'low':
        motion_params['speed'] *= 0.7
    
    return motion_params

# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/generate-video", response_model=VideoJobResponse)
async def generate_video_from_shot(request: GenerateVideoRequest):
    """
    🎬 Generate video from shot with motion effects
    
    Process:
    1. Extract dominant emotion from simulation results
    2. Calculate emotion-based motion parameters
    3. Generate video prompt from shot description + character actions
    4. Queue video generation job
    5. Return job_id for polling
    
    Args:
        request: Shot data + simulation results + style preset
        
    Returns:
        Video generation job status with job_id
    """
    # Generate unique job ID
    job_id = f"VID-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
    
    # Extract dominant emotion from simulation results
    emotions = [sim.emotion for sim in request.simulation_results]
    dominant_emotion = emotions[0] if emotions else "neutral"
    
    # Extract character names
    character_names = [sim.character_name for sim in request.simulation_results]
    
    # Calculate motion parameters based on emotion
    motion_params = calculate_motion_parameters(dominant_emotion)
    
    # Extract shot data
    shot_description = request.shot_data.get('description', '')
    camera_angle = request.shot_data.get('camera_angle', 'medium')
    camera_movement = request.shot_data.get('camera_movement', 'static')
    duration = request.shot_data.get('duration', 5.0)
    
    # Build visual prompt from shot + character actions
    character_actions = []
    for sim in request.simulation_results:
        if sim.actions:
            character_actions.append(f"{sim.character_name}: {', '.join(sim.actions)}")
    
    visual_prompt = f"{shot_description}"
    if character_actions:
        visual_prompt += f"\n\nCharacter Actions:\n" + "\n".join(character_actions)
    
    # Create video job
    job = VideoJobResponse(
        job_id=job_id,
        status="queued",
        progress=0,
        eta_sec=120,  # Estimate 2 minutes
        video_url=None,
        created_at=datetime.now(),
        shot_id=request.shot_id,
        dominant_emotion=dominant_emotion,
        characters=character_names
    )
    
    # Store job
    video_jobs[job_id] = job
    
    # Log job details
    print(f"\n🎬 Video Generation Job Created:")
    print(f"   Job ID: {job_id}")
    print(f"   Shot ID: {request.shot_id}")
    print(f"   Scene ID: {request.scene_id}")
    print(f"   Project ID: {request.project_id}")
    print(f"   Dominant Emotion: {dominant_emotion}")
    print(f"   Characters: {', '.join(character_names)}")
    print(f"   Style Preset: {request.style_preset}")
    print(f"   Camera: {camera_angle} / {camera_movement}")
    print(f"   Duration: {duration}s")
    print(f"   Motion Parameters: {motion_params}")
    print(f"   Visual Prompt: {visual_prompt[:200]}...")
    
    # TODO: Send to actual video generation service
    # In production: send to Celery queue or video API (Runway, Stability AI, etc.)
    # video_generation_task.delay(job_id, request.model_dump())
    
    print(f"   ⏳ Job queued (ETA: {job.eta_sec}s)")
    
    return job

@router.get("/jobs/{job_id}", response_model=VideoJobResponse)
async def get_video_job_status(job_id: str):
    """
    📊 Get video generation job status
    
    Used by frontend to poll job progress
    
    Args:
        job_id: Video job ID from generate-video response
        
    Returns:
        Current job status with progress percentage
    """
    if job_id not in video_jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    job = video_jobs[job_id]
    
    # TODO: Query actual job status from Celery/Redis
    # For now, simulate progress
    if job.status == "queued":
        job.status = "processing"
        job.progress = 30
        job.eta_sec = 90
    elif job.status == "processing":
        job.progress = min(100, job.progress + 20)
        job.eta_sec = max(0, job.eta_sec - 20) if job.eta_sec else 0
        
        if job.progress >= 100:
            job.status = "completed"
            # Mock video URL (in production: get from S3/CDN)
            job.video_url = f"https://cdn.example.com/videos/{job_id}.mp4"
            job.eta_sec = 0
    
    return job

@router.delete("/jobs/{job_id}")
async def cancel_video_job(job_id: str):
    """
    ❌ Cancel video generation job
    
    Args:
        job_id: Video job ID to cancel
        
    Returns:
        Cancellation confirmation
    """
    if job_id not in video_jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    job = video_jobs[job_id]
    
    if job.status in ["completed", "failed"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot cancel job in {job.status} state"
        )
    
    # Mark as cancelled (treat as failed)
    job.status = "failed"
    job.error = "Cancelled by user"
    job.progress = 0
    
    print(f"❌ Cancelled job {job_id}")
    
    return {
        "success": True,
        "message": f"Job {job_id} cancelled",
        "job_id": job_id
    }

@router.get("/jobs")
async def list_video_jobs(
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50
):
    """
    📋 List all video generation jobs
    
    Query Parameters:
        - project_id: Filter by project
        - status: Filter by status (queued, processing, completed, failed)
        - limit: Maximum number of results
        
    Returns:
        List of video jobs
    """
    jobs = list(video_jobs.values())
    
    # Apply filters
    if status:
        jobs = [j for j in jobs if j.status == status]
    
    # Sort by creation time (newest first)
    jobs.sort(key=lambda x: x.created_at, reverse=True)
    
    # Limit results
    jobs = jobs[:limit]
    
    return {
        "total": len(jobs),
        "jobs": jobs
    }

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "active_jobs": len([j for j in video_jobs.values() if j.status in ["queued", "processing"]]),
        "completed_jobs": len([j for j in video_jobs.values() if j.status == "completed"]),
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# Development/Testing Endpoints
# ============================================================================

@router.post("/test/simulate-completion/{job_id}")
async def simulate_job_completion(job_id: str):
    """
    🧪 Test endpoint: Immediately mark job as completed
    
    For development/testing only
    """
    if job_id not in video_jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    job = video_jobs[job_id]
    job.status = "completed"
    job.progress = 100
    job.video_url = f"https://cdn.example.com/videos/{job_id}.mp4"
    job.eta_sec = 0
    
    return {
        "success": True,
        "message": f"Job {job_id} marked as completed (test mode)",
        "job": job
    }
