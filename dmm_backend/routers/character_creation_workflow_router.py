"""
🔸 Character Creation Workflow Router - Hybrid Approach
Manages 2D→3D workflow integration

Endpoints:
- POST /api/workflow/create-character - Generate ExternalCharacter + 2D image
- POST /api/workflow/{id}/approve - User approves 2D image
- POST /api/workflow/{id}/regenerate - Regenerate 2D with different seed
- GET /api/workflow/{id}/status - Get workflow status
- DELETE /api/workflow/{id} - Cancel workflow

Version: 1.0.0
Created: 2025-01-27
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import random

from documents_actors import ExternalCharacter
from modules.ai_image_generator import generate_character_image
from core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/workflow", tags=["Character Creation Workflow"])

# ============================================================================
# IN-MEMORY WORKFLOW STATE STORAGE
# (In production, use Redis or MongoDB)
# ============================================================================

workflows_db: Dict[str, Dict[str, Any]] = {}


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class CreateCharacterRequest(BaseModel):
    """Request to create new character with 2D preview"""
    name: str = Field(..., min_length=1, max_length=100, description="Character name")
    role: str = Field(..., min_length=1, max_length=100, description="Character role")
    personality: Optional[str] = Field(None, max_length=500, description="Personality description")
    
    # Physical appearance
    skin_tone: str = Field("fair", description="Skin tone")
    hair_color: str = Field("black", description="Hair color")
    hair_style: str = Field("short", description="Hair style")
    eye_color: str = Field("brown", description="Eye color")
    height_cm: int = Field(170, ge=140, le=220, description="Height in cm")
    weight_kg: int = Field(65, ge=40, le=150, description="Weight in kg")
    clothing_color: str = Field("#2563eb", description="Clothing color (hex)")


class CreateCharacterResponse(BaseModel):
    """Response with workflow ID and generated data"""
    workflow_id: str
    external_character: Dict[str, Any]
    image_2d: Optional[str] = None  # Base64 image data
    metadata: Dict[str, Any]
    status: str = "pending_approval"
    created_at: str


class WorkflowStatusResponse(BaseModel):
    """Current workflow status"""
    workflow_id: str
    status: str
    external_character: Dict[str, Any]
    image_2d: Optional[str] = None
    metadata: Dict[str, Any]
    created_at: str
    approved_at: Optional[str] = None


class ApprovalResponse(BaseModel):
    """Response after user approves 2D image"""
    workflow_id: str
    status: str = "approved"
    ready_for_3d: bool = True
    approved_at: str


class RegenerateResponse(BaseModel):
    """Response after regenerating 2D image"""
    workflow_id: str
    image_2d: str = ""  # New Base64 image (empty string if SD not available)
    metadata: Dict[str, Any]
    regeneration_count: int


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_external_character(request: CreateCharacterRequest) -> ExternalCharacter:
    """
    Create ExternalCharacter from request data
    
    In future, this can integrate with AppearanceSynthesizer
    to generate from kamma profile
    """
    return ExternalCharacter(
        # Required fields
        age=25,
        age_appearance="actual",
        gender="neutral",
        ethnicity="asian",
        height=request.height_cm,
        weight=request.weight_kg,
        body_type="average",
        face_shape="oval",
        eye_color=request.eye_color,
        hair_color=request.hair_color,
        hair_style=request.hair_style,
        skin_tone=request.skin_tone,
        fashion_style="casual",
        health_status="healthy",
        gait="confident",
        posture="upright",
        voice_tone="calm",
        speech_pattern="normal",
        accent=None,
        catchphrase=None,
        signature_gesture=None,
        first_impression="friendly",
        preferred_environment="urban",
        comfort_zone="home"
    )


def generate_2d_preview(
    external: ExternalCharacter,
    style: str = "realistic",
    seed: Optional[int] = None
) -> Dict[str, Any]:
    """
    Generate 2D preview image using Stable Diffusion
    
    Returns:
        {
            "success": bool,
            "image_base64": str,
            "seed": int,
            "prompts": {...},
            "metadata": {...}
        }
    """
    try:
        logger.info(f"Generating 2D preview with style: {style}")
        
        # Call AI Image Generator
        result = generate_character_image(
            external=external,
            kamma_profile=None,
            output_path=None,
            sd_api_url="http://localhost:7860",
            style=style
        )
        
        if not result.get("success"):
            # Return mock image if SD not available
            logger.warning("SD API not available, returning mock response")
            return {
                "success": False,
                "image_base64": "",  # Empty string instead of None
                "seed": seed or random.randint(1, 999999999),
                "prompts": {
                    "positive": "Mock prompt (SD not running)",
                    "negative": "ugly, deformed"
                },
                "metadata": {
                    "model": "mock",
                    "steps": 0,
                    "width": 512,
                    "height": 768,
                    "style": style,
                    "note": "Stable Diffusion not available"
                }
            }
        
        return result
        
    except Exception as e:
        logger.error(f"2D preview generation error: {e}")
        return {
            "success": False,
            "image_base64": "",  # Empty string instead of None
            "seed": seed or random.randint(1, 999999999),
            "error": str(e)
        }


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post("/create-character", response_model=CreateCharacterResponse)
async def create_character_workflow(request: CreateCharacterRequest):
    """
    Create new character with 2D preview generation
    
    Workflow:
    1. Generate ExternalCharacter from request
    2. Generate 2D image via Stable Diffusion
    3. Save workflow state
    4. Return workflow_id + image for approval
    """
    try:
        logger.info(f"Creating character workflow: {request.name}")
        
        # Step 1: Generate ExternalCharacter
        external = create_external_character(request)
        
        # Step 2: Generate 2D preview
        image_result = generate_2d_preview(external, style="realistic")
        
        # Step 3: Create workflow ID and save state
        workflow_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        
        workflows_db[workflow_id] = {
            "workflow_id": workflow_id,
            "status": "pending_approval",
            "external_character": external.dict(),
            "image_2d": image_result.get("image_base64"),
            "metadata": {
                "seed": image_result.get("seed"),
                "style": "realistic",
                "positive_prompt": image_result.get("prompts", {}).get("positive"),
                "negative_prompt": image_result.get("prompts", {}).get("negative"),
                "model": image_result.get("metadata", {}).get("model", "realisticVisionV51_v51VAE"),
                "steps": image_result.get("metadata", {}).get("steps", 30),
                "width": image_result.get("metadata", {}).get("width", 512),
                "height": image_result.get("metadata", {}).get("height", 768)
            },
            "character_data": {
                "name": request.name,
                "role": request.role,
                "personality": request.personality,
                "clothing_color": request.clothing_color
            },
            "created_at": created_at,
            "regeneration_count": 0
        }
        
        logger.info(f"Workflow created: {workflow_id}")
        
        return CreateCharacterResponse(
            workflow_id=workflow_id,
            external_character=external.dict(),
            image_2d=image_result.get("image_base64") or "",  # Empty string if None
            metadata=workflows_db[workflow_id]["metadata"],
            status="pending_approval",
            created_at=created_at
        )
        
    except Exception as e:
        logger.error(f"Character workflow creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow creation failed: {str(e)}"
        )


@router.get("/{workflow_id}/status", response_model=WorkflowStatusResponse)
async def get_workflow_status(workflow_id: str):
    """Get current status of workflow"""
    
    if workflow_id not in workflows_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found"
        )
    
    workflow = workflows_db[workflow_id]
    
    return WorkflowStatusResponse(
        workflow_id=workflow["workflow_id"],
        status=workflow["status"],
        external_character=workflow["external_character"],
        image_2d=workflow["image_2d"],
        metadata=workflow["metadata"],
        created_at=workflow["created_at"],
        approved_at=workflow.get("approved_at")
    )


@router.post("/{workflow_id}/approve", response_model=ApprovalResponse)
async def approve_2d_image(workflow_id: str):
    """
    User approves 2D image → Ready for 3D generation
    """
    try:
        if workflow_id not in workflows_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow {workflow_id} not found"
            )
        
        workflow = workflows_db[workflow_id]
        
        # Update status
        workflow["status"] = "approved"
        workflow["approved_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"Workflow {workflow_id} approved by user")
        
        return ApprovalResponse(
            workflow_id=workflow_id,
            status="approved",
            ready_for_3d=True,
            approved_at=workflow["approved_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Approval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Approval failed: {str(e)}"
        )


@router.post("/{workflow_id}/regenerate", response_model=RegenerateResponse)
async def regenerate_2d_image(workflow_id: str):
    """
    Regenerate 2D image with different seed
    Keeps same ExternalCharacter, changes random seed
    """
    try:
        if workflow_id not in workflows_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow {workflow_id} not found"
            )
        
        workflow = workflows_db[workflow_id]
        external_dict = workflow["external_character"]
        external = ExternalCharacter(**external_dict)
        
        # Generate new seed
        new_seed = random.randint(1, 999999999)
        logger.info(f"Regenerating 2D image for {workflow_id} with seed: {new_seed}")
        
        # Generate new image
        image_result = generate_2d_preview(external, style="realistic", seed=new_seed)
        
        # Update workflow
        workflow["image_2d"] = image_result.get("image_base64") or ""  # Ensure string, not None
        workflow["metadata"]["seed"] = image_result.get("seed", new_seed)
        workflow["regeneration_count"] += 1
        
        logger.info(f"Regeneration count: {workflow['regeneration_count']}")
        
        return RegenerateResponse(
            workflow_id=workflow_id,
            image_2d=workflow["image_2d"],  # Use updated workflow value
            metadata=workflow["metadata"],
            regeneration_count=workflow["regeneration_count"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Regeneration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Regeneration failed: {str(e)}"
        )


@router.delete("/{workflow_id}")
async def cancel_workflow(workflow_id: str):
    """Cancel/delete workflow"""
    
    if workflow_id not in workflows_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found"
        )
    
    del workflows_db[workflow_id]
    logger.info(f"Workflow {workflow_id} cancelled")
    
    return {"message": "Workflow cancelled", "workflow_id": workflow_id}


@router.get("/list")
async def list_workflows():
    """List all workflows (admin/debug endpoint)"""
    
    workflows_list = []
    for wf_id, wf in workflows_db.items():
        workflows_list.append({
            "workflow_id": wf_id,
            "status": wf["status"],
            "character_name": wf.get("character_data", {}).get("name", "Unknown"),
            "created_at": wf["created_at"],
            "regeneration_count": wf.get("regeneration_count", 0)
        })
    
    return {
        "total_workflows": len(workflows_list),
        "workflows": workflows_list
    }
