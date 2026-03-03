"""
Camera Director API Router - 7 endpoints for camera planning and AI suggestions
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Request, Body
from pydantic import BaseModel, Field
from datetime import datetime

from documents_extra import CameraPlan, AIFeedback, CameraPosition, CameraRotation, LensSettings, AIMetadata
from services.camera_director import CameraDirector
from core.security import get_api_key
from core.ratelimit import limiter
from core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/api/v1/camera",
    tags=["Camera Director"],
    dependencies=[Depends(get_api_key)],
)

# Initialize camera director service
camera_director = CameraDirector()


# Request/Response Models
class CreateCameraPlanRequest(BaseModel):
    simulation_id: str
    event_id: str
    timeline_id: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    preset_name: Optional[str] = None
    generate_ai: bool = True


class CameraPlanResponse(BaseModel):
    id: str
    simulation_id: str
    event_id: str
    camera_angle: str
    shot_type: str
    movement_type: str
    lens_settings: Dict[str, Any]
    ai_generated: bool
    confidence: Optional[float] = None
    reasoning: Optional[str] = None
    created_at: datetime


class SuggestAngleRequest(BaseModel):
    emotion: str
    intensity: str = "medium"
    context: Dict[str, Any] = Field(default_factory=dict)


class SuggestAngleResponse(BaseModel):
    suggested_angle: str
    confidence: float
    reasoning: str
    alternatives: List[str] = Field(default_factory=list)


class SuggestLensRequest(BaseModel):
    emotion: str
    intensity: str = "medium"
    dhamma_ref: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)


class SuggestLensResponse(BaseModel):
    focal_length_mm: int
    aperture: str
    lens_type: str
    confidence: float
    reasoning: str


class CalculateMovementRequest(BaseModel):
    start_position: Dict[str, float]
    end_position: Dict[str, float]
    movement_type: str = "dolly"
    duration_seconds: float = 5.0
    num_waypoints: int = 10


class CalculateMovementResponse(BaseModel):
    movement_path: List[Dict[str, float]]
    duration_seconds: float
    movement_type: str


class FeedbackRequest(BaseModel):
    plan_id: str
    simulation_id: str
    event_id: str
    feedback_type: str  # "good", "not_good", "modify"
    original_suggestion: Dict[str, Any]
    correction: Optional[Dict[str, Any]] = None
    feedback_notes: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)


class PresetResponse(BaseModel):
    name: str
    camera_angle: str
    shot_type: str
    movement_type: str
    lens_settings: Dict[str, Any]
    description: Optional[str] = None


class SavePresetRequest(BaseModel):
    preset_name: str
    camera_angle: str
    shot_type: str
    movement_type: str
    lens_settings: Dict[str, Any]
    description: Optional[str] = None


# ============================================================================
# Endpoint 1: POST /api/v1/camera/plan - Create camera plan
# ============================================================================
@router.post("/plan", response_model=dict, status_code=201)
@limiter.limit("30/minute")
async def create_camera_plan(
    request: Request,
    plan_request: CreateCameraPlanRequest = Body(...)
):
    """
    Create a complete camera plan for a simulation event
    
    - **simulation_id**: ID of the simulation
    - **event_id**: ID of the event
    - **context**: Context dict with emotion, intensity, dhamma_ref, etc.
    - **preset_name**: Optional preset to use
    - **generate_ai**: Whether to generate AI suggestions (default: true)
    
    Returns complete camera plan with AI suggestions if requested.
    """
    try:
        # Generate camera plan using service
        plan_data = await camera_director.plan_shot(
            simulation_id=plan_request.simulation_id,
            event_id=plan_request.event_id,
            context=plan_request.context,
            preset_name=plan_request.preset_name,
            generate_ai=plan_request.generate_ai
        )
        
        # Add timeline_id if provided
        if plan_request.timeline_id:
            plan_data["timeline_id"] = plan_request.timeline_id
        
        # Create CameraPlan document
        camera_plan = CameraPlan(**plan_data)
        await camera_plan.insert()
        
        # Prepare response
        response = {
            "id": str(camera_plan.id),
            "simulation_id": camera_plan.simulation_id,
            "event_id": camera_plan.event_id,
            "camera_angle": camera_plan.camera_angle,
            "shot_type": camera_plan.shot_type,
            "movement_type": camera_plan.movement_type,
            "lens_settings": camera_plan.lens_settings.model_dump(),
            "ai_generated": camera_plan.ai_generated,
            "created_at": camera_plan.created_at,
        }
        
        # Add AI metadata if available
        if camera_plan.ai_metadata:
            response["confidence"] = camera_plan.ai_metadata.confidence
            response["reasoning"] = camera_plan.ai_metadata.reasoning
        
        logger.info(f"Created camera plan {camera_plan.id} for event {plan_request.event_id}")
        return response
        
    except Exception as e:
        logger.exception(f"Error creating camera plan: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create camera plan: {str(e)}")


# ============================================================================
# Endpoint 2: POST /api/v1/camera/suggest-angle - AI angle suggestion
# ============================================================================
@router.post("/suggest-angle", response_model=SuggestAngleResponse)
@limiter.limit("60/minute")
async def suggest_camera_angle(
    request: Request,
    angle_request: SuggestAngleRequest = Body(...)
):
    """
    Get AI suggestion for camera angle based on emotion and context
    
    - **emotion**: Emotion to convey (compassion, anger, fear, joy, etc.)
    - **intensity**: Intensity level (very_low, low, medium, high, very_high)
    - **context**: Additional context dict
    
    Returns suggested camera angle with reasoning.
    """
    try:
        suggested_angle = camera_director._suggest_angle(
            angle_request.emotion, 
            angle_request.intensity
        )
        
        # Calculate confidence
        confidence = 0.8 if angle_request.emotion in camera_director.EMOTION_TO_ANGLE else 0.5
        
        # Generate reasoning
        reasoning = f"Suggested {suggested_angle} angle for {angle_request.emotion} emotion"
        if angle_request.intensity != "medium":
            reasoning += f" with {angle_request.intensity} intensity"
        
        # Get alternatives
        alternatives = [a for a in camera_director.CAMERA_ANGLES if a != suggested_angle][:3]
        
        return SuggestAngleResponse(
            suggested_angle=suggested_angle,
            confidence=confidence,
            reasoning=reasoning,
            alternatives=alternatives
        )
        
    except Exception as e:
        logger.exception(f"Error suggesting angle: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to suggest angle: {str(e)}")


# ============================================================================
# Endpoint 3: POST /api/v1/camera/suggest-lens - AI lens recommendation
# ============================================================================
@router.post("/suggest-lens", response_model=SuggestLensResponse)
@limiter.limit("60/minute")
async def suggest_camera_lens(
    request: Request,
    lens_request: SuggestLensRequest = Body(...)
):
    """
    Get AI suggestion for lens settings based on context
    
    - **emotion**: Emotion to convey
    - **intensity**: Intensity level
    - **dhamma_ref**: Optional dhamma reference
    - **context**: Additional context dict
    
    Returns suggested lens settings with reasoning.
    """
    try:
        suggested_lens = camera_director._suggest_lens(
            lens_request.emotion,
            lens_request.intensity,
            lens_request.dhamma_ref
        )
        
        # Calculate confidence
        confidence = 0.75
        
        # Generate reasoning
        reasoning = f"Suggested {suggested_lens['lens_type']} lens ({suggested_lens['focal_length_mm']}mm {suggested_lens['aperture']}) "
        if "portrait" in suggested_lens['lens_type']:
            reasoning += "for intimate emotional moments with shallow depth of field"
        elif "wide" in suggested_lens['lens_type']:
            reasoning += "for dynamic action and spatial context"
        else:
            reasoning += "for balanced cinematic look"
        
        return SuggestLensResponse(
            focal_length_mm=suggested_lens["focal_length_mm"],
            aperture=suggested_lens["aperture"],
            lens_type=suggested_lens["lens_type"],
            confidence=confidence,
            reasoning=reasoning
        )
        
    except Exception as e:
        logger.exception(f"Error suggesting lens: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to suggest lens: {str(e)}")


# ============================================================================
# Endpoint 4: POST /api/v1/camera/calculate-movement - Calculate movement path
# ============================================================================
@router.post("/calculate-movement", response_model=CalculateMovementResponse)
@limiter.limit("60/minute")
async def calculate_camera_movement(
    request: Request,
    movement_request: CalculateMovementRequest = Body(...)
):
    """
    Calculate smooth camera movement path between two positions
    
    - **start_position**: Starting position {x, y, z}
    - **end_position**: Ending position {x, y, z}
    - **movement_type**: Type of movement (dolly, crane, etc.)
    - **duration_seconds**: Duration of movement
    - **num_waypoints**: Number of waypoints to generate
    
    Returns interpolated movement path.
    """
    try:
        start = movement_request.start_position
        end = movement_request.end_position
        num_points = movement_request.num_waypoints
        
        # Linear interpolation for waypoints
        movement_path = []
        for i in range(num_points + 1):
            t = i / num_points
            waypoint = {
                "x": start["x"] + t * (end["x"] - start["x"]),
                "y": start["y"] + t * (end["y"] - start["y"]),
                "z": start["z"] + t * (end["z"] - start["z"]),
            }
            movement_path.append(waypoint)
        
        logger.info(f"Calculated movement path with {len(movement_path)} waypoints")
        
        return CalculateMovementResponse(
            movement_path=movement_path,
            duration_seconds=movement_request.duration_seconds,
            movement_type=movement_request.movement_type
        )
        
    except Exception as e:
        logger.exception(f"Error calculating movement: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate movement: {str(e)}")


# ============================================================================
# Endpoint 5: POST /api/v1/camera/feedback - Submit AI feedback
# ============================================================================
@router.post("/feedback", response_model=dict, status_code=201)
@limiter.limit("60/minute")
async def submit_camera_feedback(
    request: Request,
    feedback_request: FeedbackRequest = Body(...)
):
    """
    Submit feedback on AI camera suggestions for learning
    
    - **plan_id**: ID of the camera plan
    - **feedback_type**: "good", "not_good", or "modify"
    - **original_suggestion**: Original AI suggestion
    - **correction**: User's correction (if feedback_type == "modify")
    - **context**: Original context
    
    Stores feedback for AI learning and improvement.
    """
    try:
        # Process feedback using service
        feedback_data = await camera_director.process_feedback(
            plan_id=feedback_request.plan_id,
            feedback_type=feedback_request.feedback_type,
            original_suggestion=feedback_request.original_suggestion,
            correction=feedback_request.correction,
            context=feedback_request.context
        )
        
        # Add additional fields
        feedback_data["simulation_id"] = feedback_request.simulation_id
        feedback_data["event_id"] = feedback_request.event_id
        if feedback_request.feedback_notes:
            feedback_data["meta"] = {"notes": feedback_request.feedback_notes}
        
        # Create AIFeedback document
        ai_feedback = AIFeedback(**feedback_data)
        await ai_feedback.insert()
        
        logger.info(f"Stored feedback {ai_feedback.id} for plan {feedback_request.plan_id}")
        
        return {
            "id": str(ai_feedback.id),
            "feedback_type": ai_feedback.feedback_type,
            "accepted": ai_feedback.accepted,
            "reasoning": ai_feedback.reasoning,
            "created_at": ai_feedback.created_at
        }
        
    except Exception as e:
        logger.exception(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")


# ============================================================================
# Endpoint 6: GET /api/v1/camera/presets - Get all presets
# ============================================================================
@router.get("/presets", response_model=List[PresetResponse])
async def get_camera_presets():
    """
    Get all available camera presets
    
    Returns list of preset configurations with descriptions.
    """
    try:
        presets = camera_director.list_presets()
        
        response = [
            PresetResponse(
                name=preset["name"],
                camera_angle=preset["camera_angle"],
                shot_type=preset["shot_type"],
                movement_type=preset["movement_type"],
                lens_settings=preset["lens_settings"],
                description=preset.get("description")
            )
            for preset in presets
        ]
        
        logger.info(f"Retrieved {len(response)} camera presets")
        return response
        
    except Exception as e:
        logger.exception(f"Error getting presets: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get presets: {str(e)}")


# ============================================================================
# Endpoint 7: POST /api/v1/camera/presets - Save new preset
# ============================================================================
@router.post("/presets", response_model=dict, status_code=201)
@limiter.limit("30/minute")
async def save_camera_preset(
    request: Request,
    preset_request: SavePresetRequest = Body(...)
):
    """
    Save a new camera preset
    
    - **preset_name**: Name for the preset
    - **camera_angle**: Camera angle
    - **shot_type**: Shot type
    - **movement_type**: Movement type
    - **lens_settings**: Lens configuration
    - **description**: Optional description
    
    Stores preset for future use.
    """
    try:
        preset_data = {
            "camera_angle": preset_request.camera_angle,
            "shot_type": preset_request.shot_type,
            "movement_type": preset_request.movement_type,
            "lens_settings": preset_request.lens_settings,
            "description": preset_request.description or f"Custom preset: {preset_request.preset_name}"
        }
        
        success = camera_director.save_preset(preset_request.preset_name, preset_data)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save preset")
        
        logger.info(f"Saved camera preset: {preset_request.preset_name}")
        
        return {
            "preset_name": preset_request.preset_name,
            "saved": True,
            "message": f"Preset '{preset_request.preset_name}' saved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error saving preset: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save preset: {str(e)}")
