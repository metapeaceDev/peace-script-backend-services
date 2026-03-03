"""
Actor Classification System - API Router
RESTful API endpoints for Actor Management
"""

from typing import List, Optional
from datetime import datetime
import logging
from fastapi import APIRouter, HTTPException, Query, status

from documents_actors import ActorProfile, ActorRoleType, ActorImportance
from documents import DigitalMindModel
from core.ai_provider import get_ai_provider_service
from schemas_actors import (
    ActorProfileCreate,
    ActorProfileUpdate,
    ActorProfileResponse,
    ActorStatsResponse,
    CastBreakdownResponse,
    RelationshipGraphResponse,
    MessageResponse
)

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/actors",
    tags=["actors"],
    responses={404: {"description": "Not found"}}
)


# ============================================================================
# AI Provider Management
# ============================================================================

@router.get(
    "/ai-providers",
    summary="List Available AI Providers",
    description="Get list of available AI providers with their status and capabilities"
)
async def list_ai_providers():
    """
    List all available AI providers for character generation
    
    Returns:
        [
            {
                "provider": "qwen2.5",
                "name": "Qwen2.5:7b (Ollama)",
                "available": true,
                "cost": "🆓 Free",
                "speed": "⚡⚡ Medium (5-10s)",
                "quality": "⭐⭐⭐⭐ Very Good",
                "thai_support": "⭐⭐⭐⭐⭐ Excellent",
                ...
            },
            ...
        ]
    """
    ai_service = get_ai_provider_service()
    providers = await ai_service.list_available_providers()
    return {
        "success": True,
        "providers": providers,
        "total": len(providers),
        "available_count": len([p for p in providers if p.get("available")])
    }


# ============================================================================
# CRUD Operations
# ============================================================================

@router.post(
    "/",
    response_model=ActorProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Actor Profile",
    description="Create a new actor profile with classification and metadata"
)
async def create_actor_profile(profile_data: ActorProfileCreate):
    """
    Create new actor profile
    
    - **model_id**: Must link to existing DigitalMindModel
    - **role_type**: lead, supporting, extra, cameo
    - **importance**: critical, high, medium, low
    - **character_arc_type**: positive, negative, flat, transformation, complex
    """
    # Verify model_id exists
    model = await DigitalMindModel.find_one({"model_id": profile_data.model_id})
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"DigitalMindModel '{profile_data.model_id}' not found"
        )
    
    # Create actor profile
    actor = ActorProfile(**profile_data.model_dump())
    await actor.insert()
    
    return ActorProfileResponse.model_validate(actor)


@router.get(
    "/",
    response_model=List[ActorProfileResponse],
    summary="List Actor Profiles",
    description="Get list of actors with optional filtering"
)
async def list_actors(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    role_type: Optional[ActorRoleType] = Query(None, description="Filter by role type"),
    importance: Optional[ActorImportance] = Query(None, description="Filter by importance"),
    model_id: Optional[str] = Query(None, description="Filter by model ID"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    min_screen_time: Optional[float] = Query(None, ge=0, description="Minimum screen time"),
    limit: int = Query(100, ge=1, le=500, description="Maximum results"),
    skip: int = Query(0, ge=0, description="Skip results")
):
    """
    List actors with filtering options
    
    **Filters:**
    - project_id: Get actors for specific project
    - role_type: lead | supporting | extra | cameo
    - importance: critical | high | medium | low
    - model_id: Get actor for specific model
    - tags: Comma-separated tags (e.g., "hero,lead")
    - min_screen_time: Minimum screen time in minutes
    """
    # Build query
    query_filter = {}
    filters_applied = {}
    
    if project_id:
        query_filter["project_id"] = project_id
        filters_applied["project_id"] = project_id
    
    if role_type:
        query_filter["role_type"] = role_type
        filters_applied["role_type"] = role_type
    
    if importance:
        query_filter["importance"] = importance
        filters_applied["importance"] = importance
    
    if model_id:
        query_filter["model_id"] = model_id
        filters_applied["model_id"] = model_id
    
    if min_screen_time is not None:
        query_filter["estimated_screen_time"] = {"$gte": min_screen_time}
        filters_applied["min_screen_time"] = min_screen_time
    
    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
        query_filter["tags"] = {"$in": tag_list}
        filters_applied["tags"] = tag_list
    
    # Execute query
    actors = await ActorProfile.find(query_filter).skip(skip).limit(limit).to_list()
    
    # Return array directly (consistent with projects API)
    return [ActorProfileResponse.model_validate(a) for a in actors]


@router.get(
    "/{actor_id}",
    response_model=ActorProfileResponse,
    summary="Get Actor Profile",
    description="Get specific actor profile by ID"
)
async def get_actor(actor_id: str):
    """Get actor profile by actor_id"""
    actor = await ActorProfile.find_one({"actor_id": actor_id})
    if not actor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Actor '{actor_id}' not found"
        )
    
    return ActorProfileResponse.model_validate(actor)


@router.patch(
    "/{actor_id}",
    response_model=ActorProfileResponse,
    summary="Update Actor Profile",
    description="Update actor profile (partial update)"
)
async def update_actor(actor_id: str, update_data: ActorProfileUpdate):
    """Update actor profile with partial data"""
    logger.info(f"🔄 PATCH /api/actors/{actor_id} - Request received")
    logger.info(f"📦 Update data: {update_data.model_dump(exclude_unset=True)}")
    
    actor = await ActorProfile.find_one({"actor_id": actor_id})
    if not actor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Actor '{actor_id}' not found"
        )
    
    logger.info(f"📝 BEFORE PATCH - actor: {actor_id}, avatar exists: {bool(actor.avatar_thumbnail_url)}")
    
    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    
    # ✅ FIX: Protect avatar_thumbnail_url from being overwritten with None
    # If avatar_thumbnail_url is not provided (None or not in update_dict),
    # remove it from update to preserve existing value
    if "avatar_thumbnail_url" in update_dict and update_dict["avatar_thumbnail_url"] is None:
        logger.info(f"🛡️ Protection: Removing None avatar_thumbnail_url from update")
        del update_dict["avatar_thumbnail_url"]
    
    if update_dict:
        update_dict["updated_at"] = datetime.utcnow()
        await actor.update({"$set": update_dict})
        
        # Reload actor
        actor = await ActorProfile.find_one({"actor_id": actor_id})
    
    # Check avatar_thumbnail_url exists only if actor is not None
    avatar_exists = bool(actor.avatar_thumbnail_url) if actor else False
    logger.info(f"✅ AFTER PATCH - actor: {actor_id}, avatar exists: {avatar_exists}")
    
    return ActorProfileResponse.model_validate(actor)


@router.delete(
    "/{actor_id}",
    response_model=MessageResponse,
    summary="Delete Actor Profile",
    description="Delete actor profile by ID"
)
async def delete_actor(actor_id: str):
    """Delete actor profile"""
    actor = await ActorProfile.find_one({"actor_id": actor_id})
    if not actor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Actor '{actor_id}' not found"
        )
    
    await actor.delete()
    
    return MessageResponse(
        message=f"Actor profile '{actor_id}' deleted successfully",
        actor_id=actor_id
    )


# === Analytics & Reports ===

@router.get(
    "/projects/{project_id}/cast-breakdown",
    response_model=CastBreakdownResponse,
    summary="Get Cast Breakdown",
    description="Get detailed cast breakdown by role types for a project"
)
async def get_cast_breakdown(project_id: str):
    """
    Get cast breakdown report for project
    
    Returns actors grouped by role type with statistics
    """
    actors = await ActorProfile.find({"project_id": project_id}).to_list()
    
    if not actors:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No actors found for project '{project_id}'"
        )
    
    # Group by role type
    breakdown = {
        "lead": [],
        "supporting": [],
        "extra": [],
        "cameo": []
    }
    
    total_screen_time = 0.0
    total_plot_impact = 0.0
    by_role_type = {"lead": 0, "supporting": 0, "extra": 0, "cameo": 0}
    by_importance = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    by_budget_tier = {"A": 0, "B": 0, "C": 0, "D": 0}
    
    for actor in actors:
        breakdown[actor.role_type].append({
            "actor_id": actor.actor_id,
            "name": actor.actor_name,
            "model_id": actor.model_id,
            "importance": actor.importance,
            "screen_time": actor.estimated_screen_time,
            "scenes": actor.scene_appearances,
            "plot_impact": actor.plot_impact_weight,
            "budget_tier": actor.budget_allocation_tier
        })
        
        total_screen_time += actor.estimated_screen_time
        total_plot_impact += actor.plot_impact_weight
        by_role_type[actor.role_type] += 1
        by_importance[actor.importance] += 1
        by_budget_tier[actor.budget_allocation_tier] += 1
    
    # Calculate stats
    total_actors = len(actors)
    avg_screen_time = total_screen_time / total_actors if total_actors > 0 else 0
    avg_plot_impact = total_plot_impact / total_actors if total_actors > 0 else 0
    
    # Get top actors
    top_actors = sorted(actors, key=lambda a: a.plot_impact_weight, reverse=True)[:5]
    top_actors_list = [
        {
            "actor_id": a.actor_id,
            "name": a.actor_name,
            "role_type": a.role_type,
            "plot_impact": a.plot_impact_weight,
            "screen_time": a.estimated_screen_time
        }
        for a in top_actors
    ]
    
    stats = ActorStatsResponse(
        total_actors=total_actors,
        by_role_type=by_role_type,
        by_importance=by_importance,
        by_budget_tier=by_budget_tier,
        total_screen_time=total_screen_time,
        average_screen_time=avg_screen_time,
        average_plot_impact=avg_plot_impact,
        top_actors=top_actors_list
    )
    
    project_name = actors[0].project_name if actors else None
    
    return CastBreakdownResponse(
        project_id=project_id,
        project_name=project_name,
        total_actors=total_actors,
        breakdown=breakdown,
        stats=stats
    )


@router.get(
    "/projects/{project_id}/relationship-graph",
    response_model=RelationshipGraphResponse,
    summary="Get Relationship Graph",
    description="Get actor relationship graph for visualization"
)
async def get_relationship_graph(project_id: str):
    """
    Get relationship graph for project
    
    Returns nodes (actors) and edges (relationships) for graph visualization
    """
    actors = await ActorProfile.find({"project_id": project_id}).to_list()
    
    if not actors:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No actors found for project '{project_id}'"
        )
    
    # Build nodes
    nodes = [
        {
            "id": actor.actor_id,
            "name": actor.actor_name,
            "role_type": actor.role_type,
            "importance": actor.importance,
            "plot_impact": actor.plot_impact_weight,
            "screen_time": actor.estimated_screen_time
        }
        for actor in actors
    ]
    
    # Build edges
    edges = []
    for actor in actors:
        for rel in actor.relationships:
            edges.append({
                "source": actor.actor_id,
                "target": rel.actor_id,
                "type": rel.relationship_type,
                "importance": rel.importance,
                "is_primary": rel.is_primary,
                "description": rel.description
            })
    
    return RelationshipGraphResponse(
        project_id=project_id,
        nodes=nodes,
        edges=edges
    )


@router.get(
    "/stats/global",
    response_model=ActorStatsResponse,
    summary="Get Global Statistics",
    description="Get aggregated statistics across all actors"
)
async def get_global_stats():
    """Get global actor statistics"""
    actors = await ActorProfile.find_all().to_list()
    
    if not actors:
        return ActorStatsResponse(
            total_actors=0,
            by_role_type={},
            by_importance={},
            by_budget_tier={},
            total_screen_time=0.0,
            average_screen_time=0.0,
            average_plot_impact=0.0,
            top_actors=[]
        )
    
    total_screen_time = sum(a.estimated_screen_time for a in actors)
    total_plot_impact = sum(a.plot_impact_weight for a in actors)
    
    by_role_type = {}
    by_importance = {}
    by_budget_tier = {}
    
    for actor in actors:
        by_role_type[actor.role_type] = by_role_type.get(actor.role_type, 0) + 1
        by_importance[actor.importance] = by_importance.get(actor.importance, 0) + 1
        by_budget_tier[actor.budget_allocation_tier] = by_budget_tier.get(actor.budget_allocation_tier, 0) + 1
    
    total = len(actors)
    avg_screen_time = total_screen_time / total if total > 0 else 0
    avg_plot_impact = total_plot_impact / total if total > 0 else 0
    
    top_actors = sorted(actors, key=lambda a: a.plot_impact_weight, reverse=True)[:10]
    top_actors_list = [
        {
            "actor_id": a.actor_id,
            "name": a.actor_name,
            "role_type": a.role_type,
            "plot_impact": a.plot_impact_weight,
            "screen_time": a.estimated_screen_time,
            "project_id": a.project_id
        }
        for a in top_actors
    ]
    
    return ActorStatsResponse(
        total_actors=total,
        by_role_type=by_role_type,
        by_importance=by_importance,
        by_budget_tier=by_budget_tier,
        total_screen_time=total_screen_time,
        average_screen_time=avg_screen_time,
        average_plot_impact=avg_plot_impact,
        top_actors=top_actors_list
    )


# === Avatar Design Endpoints ===

@router.put(
    "/{actor_id}/avatar",
    response_model=ActorProfileResponse,
    summary="Save Avatar Design",
    description="Save character avatar design data for an actor"
)
async def save_actor_avatar(
    actor_id: str,
    avatar_data: dict
):
    """
    Save avatar design data for an actor
    
    - **actor_id**: Actor identifier
    - **avatar_data**: Complete avatar design JSON from Character Avatar Designer
    
    Expected avatar_data structure:
    ```json
    {
        "hair_style": "...",
        "hair_color": "...",
        "face_shape": "...",
        "eye_color": "...",
        "skin_tone": "...",
        "body_type": "...",
        "height": "...",
        "clothing_style": "...",
        "accessories": [],
        "special_features": [],
        "thumbnail": "base64_or_url"
    }
    ```
    """
    # Find actor
    actor = await ActorProfile.find_one({"actor_id": actor_id})
    if not actor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Actor with id '{actor_id}' not found"
        )
    
    # Extract thumbnail if present
    thumbnail = avatar_data.get("thumbnail", None)
    
    logger.info(f"💾 PUT /avatar - Actor: {actor_id}")
    logger.info(f"   Thumbnail in request: {bool(thumbnail)}")
    logger.info(f"   Current avatar_thumbnail_url exists: {bool(actor.avatar_thumbnail_url)}")
    
    # Update actor with avatar data
    actor.avatar_data = avatar_data
    
    # ✅ FIX: Only update avatar_thumbnail_url if thumbnail is provided
    # This prevents overwriting avatar set by Character Image Generation
    # with None when saving avatar design without thumbnail
    if thumbnail is not None:
        actor.avatar_thumbnail_url = thumbnail
        logger.info(f"   ✅ Updated avatar_thumbnail_url with new thumbnail")
    else:
        logger.info(f"   🛡️ Preserved existing avatar_thumbnail_url (no thumbnail in request)")
    
    actor.updated_at = datetime.utcnow()
    
    await actor.save()
    
    logger.info(f"   ✅ Avatar saved - avatar_thumbnail_url exists: {bool(actor.avatar_thumbnail_url)}")
    
    return ActorProfileResponse.from_orm(actor)


@router.get(
    "/{actor_id}/avatar",
    response_model=dict,
    summary="Get Avatar Design",
    description="Retrieve avatar design data for an actor"
)
async def get_actor_avatar(actor_id: str):
    """
    Get avatar design data for an actor
    
    Returns the complete avatar_data JSON or 404 if not found
    """
    actor = await ActorProfile.find_one({"actor_id": actor_id})
    if not actor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Actor with id '{actor_id}' not found"
        )
    
    if not actor.avatar_data:
        return {
            "actor_id": actor_id,
            "actor_name": actor.actor_name,
            "avatar_data": None,
            "message": "No avatar design data found for this actor"
        }
    
    return {
        "actor_id": actor_id,
        "actor_name": actor.actor_name,
        "avatar_data": actor.avatar_data,
        "avatar_thumbnail_url": actor.avatar_thumbnail_url,
        "updated_at": actor.updated_at
    }


# === AI Image Generation ===
def _generate_prompt_from_external(external, internal=None, style: str = "realistic") -> str:
    """
    Generate Stable Diffusion prompt from ExternalCharacter + InternalCharacter data
    
    Converts Actor's physical AND psychological attributes into detailed SD prompt
    - external: Physical appearance (age, gender, body, face, hair, etc.)
    - internal: Personality, emotions, temperament → facial expression, body language
    """
    parts = []
    
    # Age + Gender (most important!)
    if external.age and external.gender:
        parts.append(f"{external.age} year old {external.gender}")
    elif external.gender:
        parts.append(external.gender)
    elif external.age:
        parts.append(f"{external.age} year old person")
    
    # Physical attributes
    if external.skin_tone:
        parts.append(f"{external.skin_tone} skin")
    
    if external.body_type:
        parts.append(f"{external.body_type} build")
    
    # Hair
    if external.hair_color and external.hair_style:
        parts.append(f"{external.hair_style} {external.hair_color} hair")
    elif external.hair_color:
        parts.append(f"{external.hair_color} hair")
    elif external.hair_style:
        parts.append(f"{external.hair_style} hair")
    
    # Eyes
    if external.eye_color:
        parts.append(f"{external.eye_color} eyes")
    
    # Eye expression from external_character
    if hasattr(external, 'eye_expression') and external.eye_expression:
        parts.append(f"{external.eye_expression}")
    
    # Face
    if external.face_shape:
        parts.append(f"{external.face_shape} face")
    
    # Smile type from external_character
    if hasattr(external, 'smile_type') and external.smile_type:
        parts.append(f"{external.smile_type}")
    
    # === INTERNAL CHARACTER → Facial Expression & Body Language ===
    if internal:
        # Core values → Expression
        if hasattr(internal, 'core_values') and internal.core_values:
            values_lower = [v.lower() for v in internal.core_values[:3]]
            if any(word in values_lower for word in ['courage', 'honor', 'justice']):
                parts.append("noble determined expression")
            if any(word in values_lower for word in ['loyalty', 'family']):
                parts.append("protective caring gaze")
        
        # Default mood → Expression
        if hasattr(internal, 'default_mood') and internal.default_mood:
            mood = internal.default_mood.lower()
            if 'calm' in mood or 'peaceful' in mood:
                parts.append("calm serene look")
            elif 'focus' in mood or 'determined' in mood:
                parts.append("focused determined eyes")
            elif 'optimistic' in mood or 'cheerful' in mood:
                parts.append("warm gentle smile")
            elif 'melancholic' in mood or 'sad' in mood:
                parts.append("melancholic thoughtful expression")
        
        # Personality traits (Big Five) → Expression
        if hasattr(internal, 'extraversion') and internal.extraversion >= 7:
            parts.append("approachable friendly demeanor")
        if hasattr(internal, 'agreeableness') and internal.agreeableness >= 7:
            parts.append("kind warm expression")
        if hasattr(internal, 'conscientiousness') and internal.conscientiousness >= 7:
            parts.append("composed professional look")
        
        # Thai cultural values → Expression
        if hasattr(internal, 'nam_jai') and internal.nam_jai >= 7:
            parts.append("compassionate gentle eyes")
        
        # Emotional stability → Composure
        if hasattr(internal, 'emotional_stability') and internal.emotional_stability >= 7:
            parts.append("stable balanced expression")
        elif hasattr(internal, 'emotional_stability') and internal.emotional_stability <= 4:
            parts.append("intense emotional gaze")
    
    # Distinctive features
    if external.distinctive_features:
        parts.extend(external.distinctive_features[:2])  # Limit to 2
    
    # Posture from external_character
    if hasattr(external, 'posture') and external.posture:
        parts.append(f"{external.posture} posture")
    
    # Style modifiers
    if style == "realistic":
        parts.insert(0, "photo-realistic portrait of")
        parts.append("highly detailed")
        parts.append("professional photography")
        parts.append("8k uhd")
    elif style == "anime":
        parts.insert(0, "anime character")
        parts.append("vibrant colors")
        parts.append("anime art style")
    elif style == "cinematic":
        parts.insert(0, "cinematic portrait of")
        parts.append("dramatic lighting")
        parts.append("film grain")
    
    return ", ".join(parts)


def _generate_negative_prompt(external) -> str:
    """Generate negative prompt based on gender and attributes"""
    base_negative = "ugly, deformed, blurry, low quality, worst quality, bad anatomy, extra limbs, disfigured, bad proportions, malformed, mutated"
    
    # Add gender-specific negatives
    if external.gender == "male":
        base_negative += ", feminine features, breasts, makeup, long eyelashes"
    elif external.gender == "female":
        base_negative += ", masculine features, facial hair, beard, mustache, adam's apple"
    
    return base_negative


# =============================================================================
# ACTOR IMAGE GENERATION
# =============================================================================

from pydantic import BaseModel, Field

class GenerateActorImageRequest(BaseModel):
    """Request to generate actor avatar image"""
    style: str = Field(default="realistic", description="Image style: realistic, anime, cartoon, etc.")
    width: int = Field(default=512, description="Image width")
    height: int = Field(default=768, description="Image height")
    steps: int = Field(default=30, description="Diffusion steps")
    cfg: float = Field(default=7.0, description="Classifier-free guidance scale")
    num_variations: int = Field(default=1, description="Number of image variations")


@router.post("/{actor_id}/generate-image")
async def generate_actor_image(
    actor_id: str,
    request: GenerateActorImageRequest
):
    """
    Generate avatar image for Actor using ComfyUI
    
    Uses ActorProfile.external_character to generate AI image.
    Works for all actor types (Lead, Supporting, Extra) without requiring DigitalMindModel.
    
    Process:
    1. Get ActorProfile by actor_id
    2. Extract external_character data
    3. Generate SD prompt from appearance
    4. Call ComfyUI to generate image
    5. Save to character_images collection
    6. Update actor.avatar_thumbnail_url
    
    Args:
        actor_id: Actor ID (e.g., ACT-20251110-767096)
        request: Generation parameters (style, size, steps, cfg)
        
    Returns:
        {
            "success": bool,
            "images": [{"image_base64": str, "seed": int, "prompt": str}],
            "actor_id": str,
            "actor_name": str
        }
    """
    import time
    import base64
    from datetime import datetime
    from core.logging_config import get_logger
    from modules.comfyui_client import ComfyUIClient, generate_with_comfyui
    from modules.ai_image_generator import AppearancePromptGenerator
    
    logger = get_logger(__name__)
    start_time = time.time()
    
    logger.info(f"🎭 Generating image for Actor: {actor_id}")
    
    # 1. Get Actor
    actor = await ActorProfile.find_one({"actor_id": actor_id})
    if not actor:
        logger.error(f"Actor not found: {actor_id}")
        raise HTTPException(
            status_code=404,
            detail=f"Actor '{actor_id}' not found"
        )
    
    logger.info(f"✅ Found actor: {actor.actor_name}")
    
    # 2. Check external_character exists
    if not actor.external_character:
        logger.error(f"Actor {actor_id} has no external_character")
        raise HTTPException(
            status_code=400,
            detail=f"Actor '{actor.actor_name}' has no appearance data. Please update actor profile with physical attributes first."
        )
    
    logger.info(f"✅ External character found: age={actor.external_character.age}, gender={actor.external_character.gender}")
    
    # 3. Check ComfyUI availability (optional - use placeholder if not available)
    client = ComfyUIClient("http://127.0.0.1:8188")
    comfyui_available = client.check_health()
    
    if not comfyui_available:
        logger.warning("⚠️ ComfyUI server not running - will use placeholder avatar")
        # Return placeholder avatar instead of raising error
        name_encoded = actor.actor_name.replace(" ", "+")
        placeholder_url = f"https://ui-avatars.com/api/?name={name_encoded}&size=512&background=random&color=fff&bold=true"
        
        return {
            "success": True,
            "images": [placeholder_url],
            "actor_id": actor.actor_id,
            "actor_name": actor.actor_name,
            "used_comfyui": False,
            "message": "ComfyUI not available - using placeholder avatar"
        }
    
    logger.info("✅ ComfyUI server is running")
    
    # 4. Generate prompt from external_character
    # Validate and cast style to Literal type
    valid_styles = ["realistic", "anime", "portrait", "cinematic"]
    style = request.style if request.style in valid_styles else "realistic"
    
    prompt_generator = AppearancePromptGenerator()
    prompts = prompt_generator.generate_prompt(
        external=actor.external_character,
        style=style  # type: ignore
    )
    positive_prompt = prompts["positive"]
    negative_prompt = prompts["negative"]
    
    logger.info(f"✅ Generated prompts (positive: {len(positive_prompt)} chars)")
    
    # 5. Generate image with ComfyUI
    image_bytes = generate_with_comfyui(
        prompt=positive_prompt,
        negative_prompt=negative_prompt,
        width=request.width,
        height=request.height,
        steps=request.steps,
        cfg=request.cfg,
        comfyui_url="http://127.0.0.1:8188"
    )
    
    if not image_bytes:
        logger.error("ComfyUI returned no image data")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate image - ComfyUI returned no data"
        )
    
    # 6. Convert to base64 WITHOUT RESIZING (send full quality)
    from PIL import Image
    import io
    
    # Load image
    image = Image.open(io.BytesIO(image_bytes))
    
    # ✨ KEEP FULL SIZE - Do NOT resize!
    # User requested 768×768, they should get 768×768
    # Frontend will handle thumbnails for display optimization
    logger.info(f"✅ Image loaded: {image.width}×{image.height} pixels")
    
    # Save with minimal compression (preserve quality)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=False, compress_level=1)
    full_quality_bytes = buffer.getvalue()
    
    # Convert to base64
    image_base64 = base64.b64encode(full_quality_bytes).decode('utf-8')
    logger.info(f"✅ Full quality image: {len(image_bytes)} → {len(full_quality_bytes)} bytes ({image.width}×{image.height} px)")
    
    # 7. Update actor avatar_thumbnail_url (use full quality)
    actor.avatar_thumbnail_url = f"data:image/png;base64,{image_base64}"
    actor.updated_at = datetime.utcnow()
    await actor.save()
    
    logger.info(f"✅ Updated actor avatar_thumbnail_url")
    
    # 8. Return response
    generation_time = time.time() - start_time
    logger.info(f"✅ Generation complete in {generation_time:.2f}s")
    
    return {
        "success": True,
        "images": [{
            "image_base64": image_base64,
            "seed": None,
            "prompt": positive_prompt,
            "negative_prompt": negative_prompt
        }],
        "actor_id": actor_id,
        "actor_name": actor.actor_name,
        "prompt_used": positive_prompt,
        "generation_time": generation_time,
        "message": f"Generated avatar for {actor.actor_name}"
    }


# === Extra Actor Upgrade: Create Digital Mind ===

@router.post(
    "/{actor_id}/create-digital-mind",
    summary="Create DigitalMindModel for Extra Actor",
    description="Upgrade Extra/Cameo actor to full character with mental/spiritual simulation"
)
async def create_digital_mind_for_extra(
    actor_id: str,
    base_personality: Optional[str] = Query(None, description="calm, energetic, melancholic, etc."),
    kamma_seed: Optional[dict] = None
):
    """
    Create DigitalMindModel for Extra actor (upgrade to full character)
    
    This endpoint allows "ตัวประกอบ (Extra)" actors to be upgraded to full characters
    with mental state simulation, kamma tracking, and spiritual development.
    
    Architecture (Hybrid Approach - Buddhist Nama-Rupa):
    - ActorProfile.external_character (Rupa) remains as Single Source of Truth
    - New DigitalMindModel (Nama) provides mental/spiritual simulation
    - Actor.model_id links to the new DigitalMindModel
    
    Steps:
    1. Verify actor exists and is Extra/Cameo (no model_id)
    2. Extract external_character data from ActorProfile
    3. Create new DigitalMindModel with default Buddhist psychology
    4. Link actor to new model via model_id
    5. Return complete digital mind data
    
    Args:
        actor_id: Actor ID (e.g., ACT-20251110-767096)
        base_personality: Optional personality seed (calm, energetic, etc.)
        kamma_seed: Optional initial kamma values
        
    Returns:
        {
            "success": true,
            "actor_id": "ACT-20251110-767096",
            "model_id": "actor_ACT-20251110-767096",
            "message": "DigitalMindModel created successfully",
            "digital_mind_model": { ... }
        }
    """
    from documents import DigitalMindModel
    from core_profile_models import (
        CoreProfile, CharacterStatus, LifeEssence, LifeBlueprintVipaka,
        JivitindriyaMechanics, InitialConditions, SocialStanding,
        PsychologicalMatrix, DominantTemperament, LatentTendencies,
        SpiritualAssets, KammaLedger, VirtueEngine, ParamiPortfolio,
        ParamiEntry, MasteryLevel, SamadhiLevel, AbhinnaCapabilities
    )
    
    logger.info(f"🧠 Creating DigitalMindModel for Extra actor: {actor_id}")
    
    # 1. Fetch actor
    actor = await ActorProfile.find_one({"actor_id": actor_id})
    if not actor:
        raise HTTPException(
            status_code=404,
            detail=f"Actor '{actor_id}' not found"
        )
    
    # 2. Verify actor is Extra/Cameo (no existing model)
    if actor.model_id:
        raise HTTPException(
            status_code=400,
            detail=f"Actor already has DigitalMindModel: {actor.model_id}. Cannot create duplicate."
        )
    
    # 3. Verify external_character exists
    if not actor.external_character:
        raise HTTPException(
            status_code=400,
            detail="Actor missing external_character data. Cannot create DigitalMindModel without appearance info."
        )
    
    # 4. Create model_id
    model_id = f"actor_{actor_id}"
    
    # 5. Check if model already exists (safety check)
    existing_model = await DigitalMindModel.find_one({"model_id": model_id})
    if existing_model:
        # Link actor to existing model
        actor.model_id = model_id
        await actor.save()
        logger.info(f"✅ Linked actor to existing model: {model_id}")
        return {
            "success": True,
            "actor_id": actor_id,
            "model_id": model_id,
            "message": "Linked to existing DigitalMindModel",
            "digital_mind_model": existing_model.dict()
        }
    
    # 6. Get age from external_character
    try:
        if hasattr(actor.external_character, 'age'):
            age = actor.external_character.age or 25
        else:
            age = actor.external_character.get('age', 25) if isinstance(actor.external_character, dict) else 25
    except:
        age = 25
    
    # 7. Create CoreProfile components using Pydantic models
    character_status = CharacterStatus(
        type="Puthujjana",
        stage="Common Worldling",
        path_stage=None,
        fetters_broken=[],
        fetters_remaining=[
            "sakkayaditthi", "vicikiccha", "silabbataparamasa",
            "kamaraga", "patigha", "ruparaga", "aruparaga",
            "mana", "uddhacca", "avijja"
        ]
    )
    
    life_essence = LifeEssence(
        age_in_years=age,
        life_blueprint_vipaka=LifeBlueprintVipaka(
            birth_bhumi="Human Realm",
            initial_conditions=InitialConditions(
                social_standing=SocialStanding(
                    birth_family_status="Middle-class working family",
                    karmic_reputation_baseline="Neutral",
                    inherited_social_capital=50.0
                ),
                health_baseline=75.0,
                mental_clarity_baseline=70.0,
                emotional_stability_baseline=65.0
            ),
            lifespan_potential=80,
            special_abilities=[]
        ),
        jivitindriya_mechanics=JivitindriyaMechanics(
            current_jivitindriya=85.0,
            max_jivitindriya=100.0,
            depletion_rate_per_day=0.027,
            natural_regeneration_rate=0.02,
            meditation_boost_factor=1.5
        )
    )
    
    psychological_matrix = PsychologicalMatrix(
        dominant_temperament=DominantTemperament(
            primary_carita="Moha-carita (Deluded Temperament)",
            secondary_carita="Raga-carita (Lustful Temperament)"
        ),
        latent_tendencies=LatentTendencies(
            anusaya_kilesa={
                "kama_raga": {"level": 7.0},
                "patigha": {"level": 5.0},
                "mana": {"level": 4.0},
                "ditthi": {"level": 6.0},
                "vicikiccha": {"level": 5.0},
                "bhava_raga": {"level": 4.0},
                "avijja": {"level": 8.0}
            }
        )
    )
    
    # Import additional models for SpiritualAssets (already imported above)
    
    # Create Kamma Ledger
    kamma_ledger = KammaLedger(
        kusala_stock_points=500,
        akusala_stock_points=1200,
        kiriya_actions_count=0,
        pending_vipaka_seeds=[],
        dominant_pending_kamma=[],
        kamma_log=[]
    )
    
    # Create Parami Portfolio
    parami_portfolio = ParamiPortfolio(
        perfections={
            "dana": ParamiEntry(level=1, exp=0),
            "sila": ParamiEntry(level=1, exp=0),
            "nekkhamma": ParamiEntry(level=0, exp=0),
            "panna": ParamiEntry(level=0, exp=0),
            "viriya": ParamiEntry(level=1, exp=0),
            "khanti": ParamiEntry(level=1, exp=0),
            "sacca": ParamiEntry(level=1, exp=0),
            "adhitthana": ParamiEntry(level=1, exp=0),
            "metta": ParamiEntry(level=1, exp=0),
            "upekkha": ParamiEntry(level=0, exp=0)
        }
    )
    
    # Create Virtue Engine
    virtue_engine = VirtueEngine(
        panna_mastery=MasteryLevel(level=2, exp=70),
        sati_mastery=MasteryLevel(level=3, exp=120),
        parami_portfolio=parami_portfolio,
        samadhi_attainment=SamadhiLevel(
            current_jhana=None,
            jhana_stability=0.0,
            access_concentration_strength=3.0
        ),
        abhinna_capabilities=AbhinnaCapabilities(
            iddhividha=False,
            dibbasota=False,
            cetopariya=False,
            pubbenivasanussati=False,
            dibbacakkhu=False,
            asavakkhaya=False
        )
    )
    
    spiritual_assets = SpiritualAssets(
        kamma_ledger=kamma_ledger,
        virtue_engine=virtue_engine
    )
    
    core_profile = CoreProfile(
        character_status=character_status,
        life_essence=life_essence,
        psychological_matrix=psychological_matrix,
        spiritual_assets=spiritual_assets
    )
    
    # 8. Create DigitalMindModel with required fields
    digital_mind = DigitalMindModel(
        model_id=model_id,
        name=actor.actor_name or "Unnamed Character",
        status_label="active",
        overall_level=1,
        level_progress_percent=0.0,
        image_url="",  # Empty initially
        core_state={},  # Empty initial state
        conscious_profile={},  # Empty initial profile
        kamma_profile={},  # Empty initial kamma
        CoreProfile=core_profile,  # Use alias for core_profile_obj
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # 9. Save to database
    await digital_mind.save()
    logger.info(f"✅ Created DigitalMindModel: {model_id}")
    
    # 10. Link actor to new model
    actor.model_id = model_id
    await actor.save()
    logger.info(f"✅ Linked actor {actor_id} to model {model_id}")
    
    return {
        "success": True,
        "actor_id": actor_id,
        "model_id": model_id,
        "message": f"DigitalMindModel created successfully for {actor.actor_name}",
        "digital_mind_model": digital_mind.dict()
    }


# ============================================================================
# AI Character Generation
# ============================================================================

# === AI Auto-Generate Character Profile ===

@router.post(
    "/{actor_id}/ai-generate-character",
    summary="AI Generate Complete Character Profile (External + Internal)",
    description="Use AI to auto-generate all ExternalCharacter and InternalCharacter fields"
)
async def ai_generate_character_profile(
    actor_id: str,
    generate_external: bool = Query(True, description="Generate ExternalCharacter"),
    generate_internal: bool = Query(True, description="Generate InternalCharacter"),
    overwrite_existing: bool = Query(False, description="Overwrite existing fields or only fill empty ones"),
    provider: str = Query("qwen2.5", description="AI Provider: gpt-4 | qwen2.5 | llama3.2")
):
    """
    AI Auto-Generate ExternalCharacter Profile
    
    Uses AI (GPT-4) to intelligently generate ALL ExternalCharacter fields based on:
    - actor.actor_name
    - actor.character_bio
    - actor.internal_character (if exists)
    - existing external_character fields (for context)
    
    Fields Generated (35+ fields):
    - Physical: age, gender, ethnicity, height, weight, body_type, fitness_level
    - Facial: face_shape, eye_color, eye_expression, hair_color, hair_style, skin_tone, smile_type
    - Style: fashion_style, color_palette[], accessories[]
    - Movement: posture, gait
    - Voice: voice_tone, voice_characteristics[], speech_pattern, accent
    - Social: first_impression, charisma_level, approachability
    
    Args:
        actor_id: Actor ID (e.g., ACT-xxx or peace-mind-001)
        overwrite_existing: If True, regenerate all fields. If False, only fill empty fields.
        
    Returns:
        {
            "success": true,
            "actor_id": "peace-mind-001",
            "external_character": { ... all 35+ fields ... },
            "fields_generated": ["age", "gender", "height", ...],
            "ai_confidence": 0.85,
            "message": "AI generated 28 fields for External Character"
        }
    """
    logger.info(f"🤖 AI generating character profile for: {actor_id}")
    
    # 1. Fetch actor
    actor = await ActorProfile.find_one({"actor_id": actor_id})
    if not actor:
        # Try as model_id
        actor = await ActorProfile.find_one({"model_id": actor_id})
        if not actor:
            raise HTTPException(
                status_code=404,
                detail=f"Actor '{actor_id}' not found"
            )
    
    # 2. Prepare context for AI
    context_info = {
        "actor_name": actor.actor_name or "Unnamed Character",
        "character_bio": actor.character_bio or "",
        "role_type": actor.role_type.value if actor.role_type else "unknown",
        "importance": actor.importance.value if actor.importance else "medium",
    }
    
    # Add existing external_character for context
    existing_external = {}
    if actor.external_character:
        existing_external = actor.external_character.dict(exclude_none=True)
    
    # Add internal_character dict for context
    internal_char_dict = None
    if actor.internal_character:
        internal_char_dict = actor.internal_character.dict(exclude_none=True)
    
    # 3. Use Multi-Provider AI Service
    ai_service = get_ai_provider_service()
    
    try:
        result = await ai_service.generate_character(
            actor_name=context_info['actor_name'],
            character_bio=context_info.get('character_bio'),
            internal_character=internal_char_dict,
            existing_external=existing_external,
            provider=provider,
            temperature=0.7,
            max_tokens=2000
        )
        
        generated_data = result['generated_data']
        provider_name = result['provider_name']
        generation_time = result['generation_time']
        
        logger.info(f"✅ {provider_name} generated {len(generated_data)} fields in {generation_time}s")
        
    except ValueError as e:
        logger.error(f"❌ Provider '{provider}' failed: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ AI generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"AI generation failed: {str(e)}"
        )
    
    # 4. Merge with existing data
    from documents_actors import ExternalCharacter
    
    # Get valid field names from ExternalCharacter model
    valid_fields = set(ExternalCharacter.__fields__.keys())
    
    # Filter generated_data to only include valid fields
    filtered_data = {k: v for k, v in generated_data.items() if k in valid_fields}
    
    invalid_fields = [k for k in generated_data.keys() if k not in valid_fields]
    if invalid_fields:
        logger.warning(f"⚠️ AI generated invalid fields (ignored): {invalid_fields}")
    
    if actor.external_character and not overwrite_existing:
        # Only fill empty fields
        current_data = actor.external_character.dict(exclude_none=True)
        
        for field, value in filtered_data.items():
            if field not in current_data or current_data[field] is None or current_data[field] == "":
                try:
                    setattr(actor.external_character, field, value)
                except Exception as e:
                    logger.warning(f"⚠️ Failed to set {field}={value}: {e}")
        
        fields_generated = [k for k in filtered_data.keys() if k not in current_data or not current_data[k]]
    else:
        # Overwrite all or create new
        try:
            actor.external_character = ExternalCharacter(**filtered_data)
            fields_generated = list(filtered_data.keys())
        except Exception as e:
            logger.error(f"❌ Failed to create ExternalCharacter: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to create character: {str(e)}")
    
    # 6. Save to database
    await actor.save()
    
    logger.info(f"✅ Saved ExternalCharacter with {len(fields_generated)} new fields")
    
    return {
        "success": True,
        "provider": provider,
        "provider_name": provider_name,
        "generation_time": generation_time,
        "actor_id": actor.actor_id,
        "model_id": actor.model_id,
        "actor_name": actor.actor_name,
        "external_character": actor.external_character.dict() if actor.external_character else {},
        "fields_generated": fields_generated,
        "total_fields": len(filtered_data),
        "overwrite_mode": overwrite_existing,
        "message": f"✅ {provider_name} generated {len(fields_generated)} fields for {actor.actor_name} in {generation_time}s"
    }
