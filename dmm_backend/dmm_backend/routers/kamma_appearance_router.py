"""
🔸 Kamma Appearance API Router
FastAPI endpoints for Kamma-based Physical Appearance System

Endpoints:
- POST /api/kamma-appearance/generate - Generate appearance from kamma
- GET /api/kamma-appearance/analysis/{model_id} - Get detailed analysis
- GET /api/kamma-appearance/profile/{model_id} - Get saved profile
- GET /api/kamma-appearance/history/{model_id} - Get appearance history
- POST /api/kamma-appearance/regenerate/{model_id} - Force regeneration
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
import base64
from motor import motor_asyncio

from kamma_appearance_models import (
    KammaAppearanceProfile,
    KammaAppearanceDocument,
    HealthScore,
    VoiceScore,
    DemeanorScore
)
from documents_actors import ExternalCharacter, ActorProfile
from modules.kamma_appearance_analyzer import KammaAppearanceAnalyzer, analyze_model_appearance
from modules.appearance_synthesizer import AppearanceSynthesizer, synthesize_from_model
from modules.ai_image_generator import StableDiffusionClient, SDConfig, generate_character_image
from modules.voice_synthesizer import VoiceSynthesizer, TTSConfig, synthesize_character_voice, get_voice_description
from modules.animation_controller import AnimationController, get_animation_parameters, get_animation_description
from modules.temporal_tracker import (
    TemporalTracker, 
    TimelineGenerator,
    create_appearance_snapshot,
    get_appearance_history,
    compare_appearance_over_time
)
from core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/api/kamma-appearance",
    tags=["Kamma Appearance"]
)


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class GenerateAppearanceRequest(BaseModel):
    """Request body for appearance generation"""
    model_id: str = Field(..., description="DigitalMindModel ID")
    base_template: Optional[dict] = Field(None, description="Optional genetic/cultural template")
    force_regenerate: bool = Field(False, description="Force new generation even if exists")
    
    class Config:
        json_schema_extra = {
            "example": {
                "model_id": "peace-mind-001",
                "base_template": {
                    "age": 28,
                    "gender": "male",
                    "ethnicity": "Thai",
                    "eye_color": "brown",
                    "hair_color": "black"
                },
                "force_regenerate": False
            }
        }


class AppearanceAnalysisResponse(BaseModel):
    """Response with detailed appearance analysis"""
    model_id: str
    health_score: HealthScore
    voice_score: VoiceScore
    demeanor_score: DemeanorScore
    overall_balance: float
    kusala_percentage: float
    akusala_percentage: float
    total_kamma_analyzed: int
    summary: str
    distinctive_features: List[str]
    timestamp: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "model_id": "peace-mind-001",
                "overall_balance": 35.5,
                "kusala_percentage": 67.75,
                "akusala_percentage": 32.25,
                "total_kamma_analyzed": 45,
                "summary": "High mettā creates warm, trustworthy appearance.",
                "distinctive_features": [
                    "Warm smile from mettā practice",
                    "Clear voice from truthful speech"
                ]
            }
        }


class GenerateAppearanceResponse(BaseModel):
    """Response with generated appearance"""
    model_id: str
    external_character: dict
    analysis: AppearanceAnalysisResponse
    status: str
    generated_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "model_id": "peace-mind-001",
                "status": "success",
                "generated_at": "2025-10-17T10:30:00Z"
            }
        }


class AppearanceHistoryItem(BaseModel):
    """Single history item"""
    timestamp: datetime
    overall_health: float
    voice_clarity: float
    approachability: float
    kusala_percentage: float
    summary: str


class AppearanceHistoryResponse(BaseModel):
    """Response with appearance change history"""
    model_id: str
    history: List[AppearanceHistoryItem]
    total_records: int


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

async def get_model_profile(model_id: str) -> dict:
    """
    Get DigitalMindModel profile from MongoDB
    """
    try:
        from documents import DigitalMindModel
        
        # Query MongoDB for the model
        model = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
        
        if not model:
            logger.warning(f"Model not found: {model_id}, using default profile")
            return {
                "model_id": model_id,
                "CoreProfile": {
                    "SpiritualAssets": {
                        "KammaLedger": {
                            "kusala_stock_points": 100.0,
                            "akusala_stock_points": 50.0,
                            "kamma_log": []
                        }
                    }
                }
            }
        
        # Extract kamma data from core_profile
        core_profile = model.core_profile or {}
        spiritual_assets = core_profile.get("SpiritualAssets", {})
        kamma_ledger = spiritual_assets.get("KammaLedger", {})
        
        # Build response with actual data
        return {
            "model_id": model.model_id,
            "CoreProfile": {
                "SpiritualAssets": {
                    "KammaLedger": {
                        "kusala_stock_points": kamma_ledger.get("kusala_stock_points", 100.0),
                        "akusala_stock_points": kamma_ledger.get("akusala_stock_points", 50.0),
                        "kamma_log": kamma_ledger.get("kamma_log", [])
                    }
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching model profile for {model_id}: {e}")
        # Return default profile on error
        return {
            "model_id": model_id,
            "CoreProfile": {
                "SpiritualAssets": {
                    "KammaLedger": {
                        "kusala_stock_points": 100.0,
                        "akusala_stock_points": 50.0,
                        "kamma_log": []
                    }
                }
            }
        }


async def save_appearance_profile(profile: KammaAppearanceProfile) -> bool:
    """Save appearance profile to database"""
    try:
        doc = KammaAppearanceDocument(
            model_id=profile.model_id,
            profile=profile
        )
        await doc.insert()
        logger.info(f"Saved appearance profile for {profile.model_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to save appearance profile: {e}")
        return False


async def get_saved_appearance_profile(model_id: str) -> Optional[KammaAppearanceProfile]:
    """Get saved appearance profile from database"""
    try:
        doc = await KammaAppearanceDocument.find_one({"model_id": model_id})
        if doc:
            return doc.profile
        return None
    except Exception as e:
        logger.error(f"Failed to get appearance profile: {e}")
        return None


async def get_cached_profile(model_id: str) -> Optional[KammaAppearanceProfile]:
    """Alias for get_saved_appearance_profile"""
    return await get_saved_appearance_profile(model_id)


async def get_external_character(model_id: str) -> Optional[ExternalCharacter]:
    """
    Get ExternalCharacter from database
    
    Retrieves saved appearance profile from MongoDB via get_saved_appearance_profile()
    and synthesizes ExternalCharacter representation.
    """
    # Try to get from saved appearance (queries KammaAppearanceDocument)
    profile = await get_saved_appearance_profile(model_id)
    
    if profile:
        # Generate from saved profile
        synthesizer = AppearanceSynthesizer()
        return synthesizer.synthesize_appearance(
            model_id=model_id,
            kamma_profile=profile,
            base_template=None
        )
    
    # If no saved profile, need to generate new one first
    logger.warning(f"No saved appearance for {model_id}, need to generate first")
    return None


async def save_image_to_gridfs(model_id: str, image_base64: str, metadata: dict = None) -> str:
    """
    Save base64 image to MongoDB GridFS
    
    Args:
        model_id: Model ID for filename reference
        image_base64: Base64-encoded image data
        metadata: Optional metadata dict (prompts, seed, etc.)
    
    Returns:
        GridFS file_id as string
    """
    try:
        from database import get_motor_db
        import base64
        from motor import motor_asyncio
        import gridfs.grid_file
        
        # Get GridFS instance (using motor's GridFS support)
        db = get_motor_db()
        # GridFS operations in motor
        fs_bucket = motor_asyncio.AsyncIOMotorGridFSBucket(db)
        
        # Decode base64 to bytes
        image_bytes = base64.b64decode(image_base64)
        
        # Prepare metadata
        file_metadata = {
            "model_id": model_id,
            "uploaded_at": datetime.utcnow(),
            "content_type": "image/png",
            **(metadata or {})
        }
        
        # Upload to GridFS using GridFSBucket
        filename = f"{model_id}_{datetime.utcnow().timestamp()}.png"
        file_id = await fs_bucket.upload_from_stream(
            filename,
            image_bytes,
            metadata=file_metadata
        )
        
        logger.info(f"Saved image to GridFS: {file_id} for model {model_id}")
        return str(file_id)
        
    except Exception as e:
        logger.error(f"Failed to save image to GridFS: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to save image: {str(e)}")


async def get_image_from_gridfs(file_id: str) -> tuple[bytes, dict]:
    """
    Retrieve image from MongoDB GridFS
    
    Args:
        file_id: GridFS file ID
    
    Returns:
        Tuple of (image_bytes, metadata)
    """
    try:
        from database import get_motor_db
        from bson import ObjectId
        from motor import motor_asyncio
        
        db = get_motor_db()
        fs_bucket = motor_asyncio.AsyncIOMotorGridFSBucket(db)
        
        # Get file by ID and read content
        grid_out = await fs_bucket.open_download_stream(ObjectId(file_id))
        image_bytes = await grid_out.read()
        metadata = grid_out.metadata or {}
        
        return image_bytes, metadata
        
    except Exception as e:
        logger.error(f"Failed to retrieve image from GridFS: {e}", exc_info=True)
        raise HTTPException(status_code=404, detail=f"Image not found: {str(e)}")


# =============================================================================
# API ENDPOINTS
# =============================================================================

@router.post("/generate", response_model=GenerateAppearanceResponse)
async def generate_appearance(request: GenerateAppearanceRequest):
    """
    Generate physical appearance from kamma ledger
    
    This endpoint:
    1. Retrieves DigitalMindModel profile
    2. Analyzes kamma ledger
    3. Generates Rupa modifications
    4. Creates ExternalCharacter profile
    5. Saves to database
    
    Returns complete appearance profile with analysis.
    """
    try:
        logger.info(f"Generating appearance for model: {request.model_id}")
        
        # Check if already exists and not forcing regeneration
        if not request.force_regenerate:
            existing = await get_saved_appearance_profile(request.model_id)
            if existing:
                logger.info(f"Using cached appearance for {request.model_id}")
                # Still generate ExternalCharacter from cached profile
                synthesizer = AppearanceSynthesizer()
                external = synthesizer.synthesize_appearance(
                    model_id=request.model_id,
                    kamma_profile=existing,
                    base_template=request.base_template
                )
                
                return GenerateAppearanceResponse(
                    model_id=request.model_id,
                    external_character=external.dict(),
                    analysis=AppearanceAnalysisResponse(
                        model_id=existing.model_id,
                        health_score=existing.health_score,
                        voice_score=existing.voice_score,
                        demeanor_score=existing.demeanor_score,
                        overall_balance=existing.overall_kamma_balance,
                        kusala_percentage=existing.kusala_percentage,
                        akusala_percentage=existing.akusala_percentage,
                        total_kamma_analyzed=existing.total_kamma_analyzed,
                        summary=existing.kamma_influence_summary,
                        distinctive_features=existing.distinctive_features,
                        timestamp=existing.analysis_timestamp
                    ),
                    status="cached",
                    generated_at=datetime.utcnow()
                )
        
        # Get model profile
        profile = await get_model_profile(request.model_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail=f"Model not found: {request.model_id}")
        
        # Analyze kamma
        analyzer = KammaAppearanceAnalyzer()
        kamma_ledger = profile.get("CoreProfile", {}).get("SpiritualAssets", {}).get("KammaLedger", {})
        appearance_profile = analyzer.analyze_kamma_ledger(kamma_ledger, request.model_id)
        
        # Save profile
        await save_appearance_profile(appearance_profile)
        
        # Synthesize external character
        synthesizer = AppearanceSynthesizer()
        external = synthesizer.synthesize_appearance(
            model_id=request.model_id,
            kamma_profile=appearance_profile,
            base_template=request.base_template
        )
        
        logger.info(f"Successfully generated appearance for {request.model_id}")
        
        return GenerateAppearanceResponse(
            model_id=request.model_id,
            external_character=external.dict(),
            analysis=AppearanceAnalysisResponse(
                model_id=appearance_profile.model_id,
                health_score=appearance_profile.health_score,
                voice_score=appearance_profile.voice_score,
                demeanor_score=appearance_profile.demeanor_score,
                overall_balance=appearance_profile.overall_kamma_balance,
                kusala_percentage=appearance_profile.kusala_percentage,
                akusala_percentage=appearance_profile.akusala_percentage,
                total_kamma_analyzed=appearance_profile.total_kamma_analyzed,
                summary=appearance_profile.kamma_influence_summary,
                distinctive_features=appearance_profile.distinctive_features,
                timestamp=appearance_profile.analysis_timestamp
            ),
            status="success",
            generated_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating appearance: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate appearance: {str(e)}")


@router.get("/analysis/{model_id}", response_model=AppearanceAnalysisResponse)
async def get_appearance_analysis(model_id: str):
    """
    Get detailed kamma appearance analysis without generating full ExternalCharacter
    
    Useful for:
    - Quick analysis of kamma impact
    - Monitoring kamma changes
    - Dashboard displays
    """
    try:
        logger.info(f"Getting appearance analysis for model: {model_id}")
        
        # Try to get cached profile first
        cached = await get_saved_appearance_profile(model_id)
        if cached:
            return AppearanceAnalysisResponse(
                model_id=cached.model_id,
                health_score=cached.health_score,
                voice_score=cached.voice_score,
                demeanor_score=cached.demeanor_score,
                overall_balance=cached.overall_kamma_balance,
                kusala_percentage=cached.kusala_percentage,
                akusala_percentage=cached.akusala_percentage,
                total_kamma_analyzed=cached.total_kamma_analyzed,
                summary=cached.kamma_influence_summary,
                distinctive_features=cached.distinctive_features,
                timestamp=cached.analysis_timestamp
            )
        
        # If not cached, analyze fresh
        profile = await get_model_profile(model_id)
        if not profile:
            raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")
        
        analyzer = KammaAppearanceAnalyzer()
        kamma_ledger = profile.get("CoreProfile", {}).get("SpiritualAssets", {}).get("KammaLedger", {})
        appearance_profile = analyzer.analyze_kamma_ledger(kamma_ledger, model_id)
        
        # Save for future use
        await save_appearance_profile(appearance_profile)
        
        return AppearanceAnalysisResponse(
            model_id=appearance_profile.model_id,
            health_score=appearance_profile.health_score,
            voice_score=appearance_profile.voice_score,
            demeanor_score=appearance_profile.demeanor_score,
            overall_balance=appearance_profile.overall_kamma_balance,
            kusala_percentage=appearance_profile.kusala_percentage,
            akusala_percentage=appearance_profile.akusala_percentage,
            total_kamma_analyzed=appearance_profile.total_kamma_analyzed,
            summary=appearance_profile.kamma_influence_summary,
            distinctive_features=appearance_profile.distinctive_features,
            timestamp=appearance_profile.analysis_timestamp
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get analysis: {str(e)}")


@router.get("/profile/{model_id}")
async def get_appearance_profile(model_id: str):
    """
    Get complete saved appearance profile including ExternalCharacter
    """
    try:
        profile = await get_saved_appearance_profile(model_id)
        
        if not profile:
            raise HTTPException(
                status_code=404,
                detail=f"No appearance profile found for model: {model_id}. Generate one first."
            )
        
        return {
            "model_id": model_id,
            "profile": profile.dict(),
            "status": "found"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting profile: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get profile: {str(e)}")


@router.post("/regenerate/{model_id}", response_model=GenerateAppearanceResponse)
async def regenerate_appearance(
    model_id: str,
    base_template: Optional[dict] = None
):
    """
    Force regeneration of appearance even if cached version exists
    
    Use when:
    - Kamma ledger has been updated
    - Want fresh analysis
    - Testing different templates
    """
    request = GenerateAppearanceRequest(
        model_id=model_id,
        base_template=base_template,
        force_regenerate=True
    )
    return await generate_appearance(request)


@router.get("/history/{model_id}", response_model=AppearanceHistoryResponse)
async def get_appearance_history(
    model_id: str,
    limit: int = Query(default=10, ge=1, le=100, description="Number of history items to return")
):
    """
    Get appearance change history over time
    
    Shows how appearance has evolved as kamma accumulated.
    Useful for temporal tracking visualization.
    """
    try:
        from kamma_appearance_models import KammaAppearanceDocument
        
        # Query all appearance profiles for this model, sorted by created_at
        profiles = await KammaAppearanceDocument.find(
            KammaAppearanceDocument.model_id == model_id
        ).sort("-created_at").limit(limit).to_list()
        
        if not profiles:
            logger.warning(f"No history found for model: {model_id}")
            return AppearanceHistoryResponse(
                model_id=model_id,
                history=[],
                total_records=0
            )
        
        # Convert profiles to history items
        history = []
        for doc in profiles:
            profile = doc.profile
            
            # Extract scores from profile
            health_score = profile.health_score
            voice_score = profile.voice_score
            demeanor_score = profile.demeanor_score
            
            # Use the overall score fields
            overall_health = health_score.overall_health
            voice_clarity = voice_score.clarity_score
            approachability = demeanor_score.approachability
            
            history_item = AppearanceHistoryItem(
                timestamp=doc.created_at,
                overall_health=overall_health,
                voice_clarity=voice_clarity,
                approachability=approachability,
                kusala_percentage=profile.kusala_percentage,
                summary=f"Kamma balance: {profile.overall_kamma_balance:.1f}%"
            )
            history.append(history_item)
        
        # Get total count
        total_count = await KammaAppearanceDocument.find(
            KammaAppearanceDocument.model_id == model_id
        ).count()
        
        return AppearanceHistoryResponse(
            model_id=model_id,
            history=history,
            total_records=total_count
        )
        
    except Exception as e:
        logger.error(f"Error getting history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")


@router.delete("/profile/{model_id}")
async def delete_appearance_profile(model_id: str):
    """
    Delete cached appearance profile
    
    Use when:
    - Resetting character
    - Cleaning up old data
    """
    try:
        doc = await KammaAppearanceDocument.find_one({"model_id": model_id})
        
        if not doc:
            raise HTTPException(
                status_code=404,
                detail=f"No profile found for model: {model_id}"
            )
        
        await doc.delete()
        
        logger.info(f"Deleted appearance profile for {model_id}")
        
        return {
            "model_id": model_id,
            "status": "deleted",
            "message": "Appearance profile successfully deleted"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting profile: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete profile: {str(e)}")


@router.get("/mappings")
async def get_kamma_appearance_mappings():
    """
    Get complete Kamma-to-Appearance mapping tables
    
    Returns all mapping data for:
    - Kāyakamma → Health/Body
    - Vacīkamma → Voice/Speech
    - Manokamma → Demeanor/Expression
    
    Useful for documentation and UI displays.
    """
    from kamma_appearance_models import KammaAppearanceMapping
    
    return {
        "kayakamma_to_health": {
            k.value: v for k, v in KammaAppearanceMapping.KAYAKAMMA_TO_HEALTH.items()
        },
        "vacikamma_to_voice": {
            k.value: v for k, v in KammaAppearanceMapping.VACIKAMMA_TO_VOICE.items()
        },
        "manokamma_to_demeanor": {
            k.value: v for k, v in KammaAppearanceMapping.MANOKAMMA_TO_DEMEANOR.items()
        },
        "total_mappings": (
            len(KammaAppearanceMapping.KAYAKAMMA_TO_HEALTH) +
            len(KammaAppearanceMapping.VACIKAMMA_TO_VOICE) +
            len(KammaAppearanceMapping.MANOKAMMA_TO_DEMEANOR)
        )
    }


# =============================================================================
# AI IMAGE GENERATION ENDPOINTS
# =============================================================================

class GenerateImageRequest(BaseModel):
    """Request for AI image generation"""
    model_id: str = Field(..., description="DigitalMindModel ID")
    style: str = Field("realistic", description="Image style (realistic/anime/portrait/cinematic)")
    sd_api_url: str = Field("http://localhost:7860", description="Stable Diffusion API URL")
    save_to_db: bool = Field(True, description="Save image to database")
    
    class Config:
        json_schema_extra = {
            "example": {
                "model_id": "peace-mind-001",
                "style": "realistic",
                "sd_api_url": "http://localhost:7860",
                "save_to_db": True
            }
        }


class GenerateImageResponse(BaseModel):
    """Response with generated image"""
    model_id: str
    success: bool
    image_base64: Optional[str] = None
    prompts: dict
    error: Optional[str] = None
    seed: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    model: Optional[str] = None
    saved_to: Optional[str] = None
    gridfs_file_id: Optional[str] = None  # GridFS file ID if saved to DB
    generated_at: datetime


@router.post("/generate-image", response_model=GenerateImageResponse)
async def generate_character_image_api(request: GenerateImageRequest):
    """
    Generate AI image from character's appearance
    
    **Requires Stable Diffusion WebUI API running**
    
    Process:
    1. Get ExternalCharacter for model
    2. Convert to SD prompt
    3. Call Stable Diffusion API
    4. Return image (base64)
    5. Optionally save to database
    
    Example:
        ```json
        {
            "model_id": "peace-mind-001",
            "style": "realistic",
            "sd_api_url": "http://localhost:7860"
        }
        ```
    """
    try:
        logger.info(f"Generating AI image for model: {request.model_id}")
        
        # 1. Get ExternalCharacter
        external = await get_external_character(request.model_id)
        if not external:
            raise HTTPException(
                status_code=404,
                detail=f"ExternalCharacter not found for model: {request.model_id}"
            )
        
        # 2. Get kamma profile (for additional traits)
        profile = await get_cached_profile(request.model_id)
        
        # 3. Generate image
        result = generate_character_image(
            external=external,
            kamma_profile=profile,
            output_path=None,  # Don't save to file system yet
            sd_api_url=request.sd_api_url,
            style=request.style
        )
        
        # 4. Check success
        if not result.get("success"):
            return GenerateImageResponse(
                model_id=request.model_id,
                success=False,
                prompts=result.get("prompts", {}),
                error=result.get("error", "Unknown error"),
                generated_at=datetime.utcnow()
            )
        
        # 5. Save to database (if requested)
        gridfs_file_id = None
        if request.save_to_db:
            try:
                # Save image to GridFS
                image_base64 = result.get("image_base64")
                if image_base64:
                    metadata = {
                        "prompts": result.get("prompts", {}),
                        "seed": result.get("seed"),
                        "width": result.get("width"),
                        "height": result.get("height"),
                        "model": result.get("model"),
                        "style": request.style
                    }
                    gridfs_file_id = await save_image_to_gridfs(
                        model_id=request.model_id,
                        image_base64=image_base64,
                        metadata=metadata
                    )
                    logger.info(f"Image saved to GridFS: {gridfs_file_id}")
                else:
                    logger.warning("No image_base64 to save")
            except Exception as e:
                logger.error(f"Failed to save image to GridFS: {e}", exc_info=True)
                # Continue even if GridFS save fails
        
        # 6. Return response
        response_data = {
            "model_id": request.model_id,
            "success": True,
            "image_base64": result.get("image_base64"),
            "prompts": result.get("prompts"),
            "seed": result.get("seed"),
            "width": result.get("width"),
            "height": result.get("height"),
            "model": result.get("model"),
            "saved_to": result.get("saved_to"),
            "generated_at": datetime.utcnow()
        }
        
        # Add GridFS file_id if saved
        if gridfs_file_id:
            response_data["gridfs_file_id"] = gridfs_file_id
        
        return GenerateImageResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prompt/{model_id}")
async def get_sd_prompt(
    model_id: str,
    style: str = Query("realistic", description="Image style")
):
    """
    Get Stable Diffusion prompt for character without generating image
    
    Useful for:
    - Testing prompt generation
    - Manual image generation
    - Debugging
    
    Returns:
        Dict with 'positive' and 'negative' prompts
    """
    try:
        # Get ExternalCharacter
        external = await get_external_character(model_id)
        if not external:
            raise HTTPException(
                status_code=404,
                detail=f"ExternalCharacter not found for model: {model_id}"
            )
        
        # Get kamma profile
        profile = await get_cached_profile(model_id)
        
        # Generate prompt only
        from modules.ai_image_generator import get_prompt_for_character
        prompts = get_prompt_for_character(external, profile, style=style)
        
        return {
            "model_id": model_id,
            "style": style,
            "prompts": prompts,
            "prompt_length": len(prompts["positive"]),
            "timestamp": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating prompt: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# VOICE SYNTHESIS ENDPOINTS
# =============================================================================

class SynthesizeVoiceRequest(BaseModel):
    """Request for voice synthesis"""
    model_id: str = Field(..., description="DigitalMindModel ID")
    text: str = Field(..., min_length=1, max_length=5000, description="Text to speak")
    engine: str = Field("gtts", description="TTS engine (gtts/elevenlabs/coqui)")
    language: str = Field("th", description="Language code (th/en/etc)")
    use_cache: bool = Field(True, description="Use cached audio if available")
    
    class Config:
        json_schema_extra = {
            "example": {
                "model_id": "peace-mind-001",
                "text": "สวัสดีครับ ผมชื่อพีช ยินดีที่ได้รู้จักครับ",
                "engine": "gtts",
                "language": "th",
                "use_cache": True
            }
        }


class SynthesizeVoiceResponse(BaseModel):
    """Response with synthesized voice"""
    model_id: str
    success: bool
    audio_path: Optional[str] = None
    audio_base64: Optional[str] = None
    voice_parameters: Optional[dict] = None
    voice_description: Optional[str] = None
    engine: str
    text_length: int
    cached: bool = False
    error: Optional[str] = None
    generated_at: datetime


class VoiceParametersResponse(BaseModel):
    """Response with voice parameters only"""
    model_id: str
    voice_parameters: dict
    voice_description: str
    voice_score: dict
    timestamp: datetime


@router.post("/synthesize-voice", response_model=SynthesizeVoiceResponse)
async def synthesize_voice_api(request: SynthesizeVoiceRequest):
    """
    Synthesize character's voice from text
    
    **Supported TTS Engines:**
    - `gtts` - Google TTS (free, supports Thai/English)
    - `elevenlabs` - ElevenLabs (premium, requires API key)
    - `coqui` - Coqui TTS (local, open source)
    
    **Process:**
    1. Get VoiceScore from kamma profile
    2. Map to TTS parameters (pitch, speed, warmth, etc.)
    3. Synthesize audio with chosen engine
    4. Return audio file path (and optionally base64)
    
    **Example:**
    ```json
    {
        "model_id": "peace-mind-001",
        "text": "สวัสดีครับ",
        "engine": "gtts",
        "language": "th"
    }
    ```
    """
    try:
        logger.info(f"Synthesizing voice for model: {request.model_id}")
        
        # 1. Get VoiceScore
        profile = await get_cached_profile(request.model_id)
        if not profile:
            raise HTTPException(
                status_code=404,
                detail=f"Kamma profile not found for model: {request.model_id}. Generate appearance first."
            )
        
        voice_score = profile.voice_score
        
        # 2. Get voice description
        voice_desc = get_voice_description(voice_score)
        
        # 3. Configure TTS
        config = TTSConfig(
            engine=request.engine,
            gtts_lang=request.language,
            cache_audio=request.use_cache
        )
        
        # 4. Synthesize
        synthesizer = VoiceSynthesizer(config)
        result = synthesizer.synthesize_voice(
            text=request.text,
            voice_score=voice_score,
            use_cache=request.use_cache
        )
        
        # 5. Check success
        if not result.get("success"):
            return SynthesizeVoiceResponse(
                model_id=request.model_id,
                success=False,
                engine=request.engine,
                text_length=len(request.text),
                error=result.get("error", "Unknown error"),
                generated_at=datetime.utcnow()
            )
        
        # 6. Get voice parameters
        voice_params = synthesizer.get_voice_parameters(voice_score)
        
        # 7. Optionally encode to base64
        audio_base64 = None
        if result.get("output_path"):
            try:
                import base64
                with open(result["output_path"], "rb") as f:
                    audio_bytes = f.read()
                    audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            except Exception as e:
                logger.warning(f"Could not encode audio to base64: {e}")
        
        # 8. Return response
        return SynthesizeVoiceResponse(
            model_id=request.model_id,
            success=True,
            audio_path=result.get("output_path"),
            audio_base64=audio_base64,
            voice_parameters=voice_params.dict(),
            voice_description=voice_desc,
            engine=request.engine,
            text_length=len(request.text),
            cached=result.get("cached", False),
            generated_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error synthesizing voice: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voice-parameters/{model_id}", response_model=VoiceParametersResponse)
async def get_voice_parameters(model_id: str):
    """
    Get voice synthesis parameters without generating audio
    
    Useful for:
    - Testing voice characteristics
    - Understanding kamma influence on voice
    - Debugging TTS issues
    
    Returns voice parameters derived from VoiceScore:
    - Pitch, speed, volume
    - Warmth, clarity, resonance
    - Emotional tone
    - Mettā influence, truthfulness marker
    """
    try:
        # Get VoiceScore
        profile = await get_cached_profile(model_id)
        if not profile:
            raise HTTPException(
                status_code=404,
                detail=f"Kamma profile not found for model: {model_id}"
            )
        
        voice_score = profile.voice_score
        
        # Map to parameters
        from modules.voice_synthesizer import VoiceParameterMapper
        mapper = VoiceParameterMapper()
        params = mapper.map_voice_score(voice_score)
        
        # Get description
        voice_desc = get_voice_description(voice_score)
        
        return VoiceParametersResponse(
            model_id=model_id,
            voice_parameters=params.dict(),
            voice_description=voice_desc,
            voice_score=voice_score.dict(),
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting voice parameters: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voice-description/{model_id}")
async def get_voice_description_api(model_id: str):
    """
    Get human-readable voice description
    
    Example response:
    ```json
    {
        "model_id": "peace-mind-001",
        "description": "Warm, gentle voice with excellent clarity. High mettā influence creates compassionate tone.",
        "voice_quality": 85,
        "vocal_warmth": 90,
        "speech_clarity": 88
    }
    ```
    """
    try:
        # Get VoiceScore
        profile = await get_cached_profile(model_id)
        if not profile:
            raise HTTPException(
                status_code=404,
                detail=f"Kamma profile not found for model: {model_id}"
            )
        
        voice_score = profile.voice_score
        description = get_voice_description(voice_score)
        
        return {
            "model_id": model_id,
            "description": description,
            "voice_quality": voice_score.voice_quality,
            "vocal_warmth": voice_score.vocal_warmth,
            "speech_clarity": voice_score.speech_clarity,
            "truthful_speech_score": voice_score.truthful_speech_score,
            "timestamp": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting voice description: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# 3D ANIMATION ENDPOINTS
# =============================================================================

class AnimationConfigRequest(BaseModel):
    """Request for animation configuration"""
    model_id: str = Field(..., description="DigitalMindModel ID")
    context: str = Field("idle", description="Animation context (idle/greeting/meditation/etc.)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "model_id": "peace-mind-001",
                "context": "greeting"
            }
        }


class AnimationConfigResponse(BaseModel):
    """Response with animation configuration"""
    model_id: str
    parameters: dict
    gestures: List[dict]
    context: str
    description: str
    generated_at: str


@router.post("/animation-config", response_model=AnimationConfigResponse)
async def get_animation_config_api(request: AnimationConfigRequest):
    """
    Get 3D animation configuration from demeanor
    
    **Process:**
    1. Get DemeanorScore from kamma profile
    2. Map to animation parameters (posture, movements, expressions)
    3. Select appropriate gestures for context
    4. Return configuration for Three.js frontend
    
    **Contexts:**
    - `idle` - Default standing/sitting animation
    - `greeting` - Greeting gestures (wai, nod, etc.)
    - `meditation` - Meditative postures
    - `speaking` - Speaking animations
    - `walking` - Walking style
    
    **Example:**
    ```json
    {
        "model_id": "peace-mind-001",
        "context": "greeting"
    }
    ```
    
    **Response includes:**
    - Posture parameters (spine curvature, shoulder tension)
    - Movement characteristics (speed, fluidity)
    - Facial expressions (smile, eye openness)
    - Gesture sequences (wai, nod, etc.)
    - Buddhist influence markers (mettā radiance, meditation calmness)
    """
    try:
        logger.info(f"Getting animation config for model: {request.model_id}, context: {request.context}")
        
        # Get DemeanorScore
        profile = await get_cached_profile(request.model_id)
        if not profile:
            raise HTTPException(
                status_code=404,
                detail=f"Kamma profile not found for model: {request.model_id}"
            )
        
        demeanor = profile.demeanor_score
        
        # Get animation configuration
        controller = AnimationController()
        config = controller.get_animation_config(demeanor, context=request.context)
        
        # Get description
        description = controller.get_animation_description(demeanor)
        
        return AnimationConfigResponse(
            model_id=request.model_id,
            parameters=config["parameters"],
            gestures=config["gestures"],
            context=request.context,
            description=description,
            generated_at=config["generated_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting animation config: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/animation-parameters/{model_id}")
async def get_animation_parameters_api(model_id: str):
    """
    Get animation parameters without gestures
    
    Returns raw animation parameters for frontend Three.js:
    - Posture (type, spine curvature, shoulder tension)
    - Movement (speed, fluidity, gesture frequency)
    - Facial expressions (smile, eye openness, brow position)
    - Gaze behavior (steadiness, warmth)
    - Energy & presence
    - Buddhist influence markers
    - Idle animation settings
    """
    try:
        # Get DemeanorScore
        profile = await get_cached_profile(model_id)
        if not profile:
            raise HTTPException(
                status_code=404,
                detail=f"Kamma profile not found for model: {model_id}"
            )
        
        demeanor = profile.demeanor_score
        
        # Get parameters
        params = get_animation_parameters(demeanor)
        
        return {
            "model_id": model_id,
            "parameters": params.dict(),
            "demeanor_score": demeanor.dict(),
            "timestamp": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting animation parameters: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/animation-description/{model_id}")
async def get_animation_description_api(model_id: str):
    """
    Get human-readable animation description
    
    Example response:
    ```json
    {
        "model_id": "peace-mind-001",
        "description": "Upright posture. Fluid, graceful movements. Warm smile. Radiating mettā. Deep meditative calm.",
        "posture_type": "upright",
        "facial_expression": "warm smile",
        "metta_radiance": 0.92,
        "meditation_calmness": 0.85
    }
    ```
    """
    try:
        # Get DemeanorScore
        profile = await get_cached_profile(model_id)
        if not profile:
            raise HTTPException(
                status_code=404,
                detail=f"Kamma profile not found for model: {model_id}"
            )
        
        demeanor = profile.demeanor_score
        
        # Get description and params
        description = get_animation_description(demeanor)
        params = get_animation_parameters(demeanor)
        
        return {
            "model_id": model_id,
            "description": description,
            "posture_type": params.posture_type,
            "facial_expression": params.facial_expression,
            "metta_radiance": params.metta_radiance,
            "meditation_calmness": params.meditation_calmness,
            "confidence_marker": params.confidence_marker,
            "timestamp": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting animation description: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gestures/{model_id}")
async def get_gestures_for_context(
    model_id: str,
    context: str = Query("greeting", description="Gesture context")
):
    """
    Get appropriate gestures for specific context
    
    **Contexts:**
    - `greeting` - Wai, nod, wave
    - `meditation` - Dhyana mudra, still presence
    - `compassion` - Open palm, anjali mudra
    - `confidence` - Upright stance, steady gaze
    - `agreement` - Nod, smile
    
    Returns list of gesture definitions with:
    - Name, type, duration
    - Triggers and intensity
    - Human-readable description
    """
    try:
        # Get DemeanorScore
        profile = await get_cached_profile(model_id)
        if not profile:
            raise HTTPException(
                status_code=404,
                detail=f"Kamma profile not found for model: {model_id}"
            )
        
        demeanor = profile.demeanor_score
        
        # Get gestures
        from modules.animation_controller import AnimationParameterMapper
        mapper = AnimationParameterMapper()
        gestures = mapper.select_gestures(demeanor, trigger=context)
        
        return {
            "model_id": model_id,
            "context": context,
            "gestures": [g.dict() for g in gestures],
            "count": len(gestures),
            "timestamp": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting gestures: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# TEMPORAL TRACKING ENDPOINTS
# =============================================================================

class CreateSnapshotRequest(BaseModel):
    """Request to create appearance snapshot"""
    model_id: str = Field(..., description="DigitalMindModel ID")
    trigger_event: str = Field("manual", description="What triggered this snapshot")
    notes: Optional[str] = Field(None, description="Optional notes about this moment")
    
    class Config:
        json_schema_extra = {
            "example": {
                "model_id": "peace-mind-001",
                "trigger_event": "meditation_completion",
                "notes": "After completing 7-day meditation retreat"
            }
        }


@router.post("/snapshot")
async def create_snapshot_api(request: CreateSnapshotRequest):
    """
    Create appearance snapshot at current moment
    
    **Use this to:**
    - Record appearance before/after significant events
    - Track progress over time
    - Enable temporal comparisons
    
    **Trigger Events:**
    - `meditation_completion` - After meditation practice
    - `kamma_milestone` - After significant kusala/akusala accumulation
    - `life_event` - Major life change
    - `retreat_completion` - After retreat
    - `manual` - User-initiated snapshot
    
    **Example:**
    ```json
    {
        "model_id": "peace-mind-001",
        "trigger_event": "meditation_completion",
        "notes": "After 7-day retreat"
    }
    ```
    """
    try:
        logger.info(f"Creating snapshot for {request.model_id}, trigger: {request.trigger_event}")
        
        # Get current profile
        profile = await get_cached_profile(request.model_id)
        if not profile:
            raise HTTPException(
                status_code=404,
                detail=f"Kamma profile not found for model: {request.model_id}"
            )
        
        # Create snapshot
        snapshot = await create_appearance_snapshot(
            profile,
            trigger=request.trigger_event,
            notes=request.notes
        )
        
        return {
            "success": True,
            "snapshot": snapshot.dict(),
            "message": "Snapshot created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating snapshot: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{model_id}")
async def get_history_api(
    model_id: str,
    limit: int = Query(50, ge=1, le=200, description="Max number of snapshots"),
    days: Optional[int] = Query(None, description="Filter last N days")
):
    """
    Get appearance history for character
    
    Returns list of appearance snapshots ordered by time (newest first).
    
    **Query Parameters:**
    - `limit` - Maximum snapshots to return (1-200, default 50)
    - `days` - Optional filter for last N days
    
    **Response includes:**
    - Timestamp of each snapshot
    - Full appearance scores (health, voice, demeanor)
    - Trigger event and notes
    - Kamma metrics (kusala/akusala percentages)
    
    **Example:**
    ```
    GET /api/kamma-appearance/history/peace-mind-001?limit=10&days=30
    ```
    """
    try:
        logger.info(f"Getting history for {model_id}, limit={limit}, days={days}")
        
        # Calculate date range if days specified
        start_date = None
        if days:
            from datetime import timedelta
            start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get history
        snapshots = await TemporalTracker.get_history(
            model_id,
            limit=limit,
            start_date=start_date
        )
        
        return {
            "model_id": model_id,
            "total_snapshots": len(snapshots),
            "snapshots": [s.dict() for s in snapshots],
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error getting history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compare/{model_id}")
async def compare_snapshots_api(
    model_id: str,
    days_ago: int = Query(7, ge=1, le=365, description="Compare to N days ago")
):
    """
    Compare current appearance to past snapshot
    
    **Detects changes in:**
    - Overall health (body strength, skin quality, vitality)
    - Voice characteristics (quality, warmth, clarity)
    - Demeanor (peacefulness, mettā, confidence)
    - Kamma balance (kusala/akusala percentages)
    
    **Change Significance Levels:**
    - `minor` - Small change (< 5 points)
    - `moderate` - Noticeable change (5-10 points)
    - `major` - Significant change (10-20 points)
    - `profound` - Life-changing shift (> 20 points)
    
    **Example:**
    ```
    GET /api/kamma-appearance/compare/peace-mind-001?days_ago=7
    ```
    
    **Response:**
    ```json
    {
        "overall_trend": "improving",
        "kusala_change": +8.5,
        "changes": [
            {
                "aspect": "voice_quality",
                "delta": +10,
                "significance": "major",
                "description": "Voice quality improved from truthful speech practice"
            }
        ],
        "summary": "Overall improvement over 7 days. Major changes in: voice quality, peacefulness."
    }
    ```
    """
    try:
        logger.info(f"Comparing {model_id} to {days_ago} days ago")
        
        # Get comparison
        comparison = await compare_appearance_over_time(model_id, days_ago=days_ago)
        
        if not comparison:
            raise HTTPException(
                status_code=404,
                detail=f"Not enough history to compare. Need at least 2 snapshots."
            )
        
        return comparison.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing snapshots: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/timeline/{model_id}")
async def get_timeline_api(
    model_id: str,
    metrics: List[str] = Query(
        ["overall_balance", "kusala_percentage", "peacefulness"],
        description="Metrics to include in timeline"
    ),
    limit: int = Query(100, ge=10, le=500, description="Max snapshots")
):
    """
    Get timeline data for visualization
    
    **Supported Metrics:**
    - `overall_balance` - Overall kamma balance
    - `kusala_percentage` - Wholesome kamma percentage
    - `akusala_percentage` - Unwholesome kamma percentage
    - `peacefulness` - Inner peace level
    - `voice_quality` - Voice quality score
    - `body_strength` - Physical strength
    
    **Use this data for:**
    - Creating time-series charts
    - Visualizing kamma evolution
    - Tracking spiritual progress
    - Identifying patterns and trends
    
    **Example:**
    ```
    GET /api/kamma-appearance/timeline/peace-mind-001?metrics=kusala_percentage&metrics=peacefulness&limit=50
    ```
    
    **Response Format:**
    ```json
    {
        "timestamps": ["2025-10-01T10:00:00Z", "2025-10-08T10:00:00Z", ...],
        "metrics": {
            "kusala_percentage": [65.5, 67.8, 70.2, ...],
            "peacefulness": [72.0, 75.5, 78.0, ...]
        }
    }
    ```
    """
    try:
        logger.info(f"Getting timeline for {model_id}, metrics={metrics}")
        
        # Get snapshots
        snapshots = await get_appearance_history(model_id, limit=limit)
        
        if not snapshots:
            raise HTTPException(
                status_code=404,
                detail=f"No history found for model: {model_id}"
            )
        
        # Generate timeline data
        timeline_data = TimelineGenerator.generate_timeline_data(snapshots, metrics=metrics)
        
        return {
            "model_id": model_id,
            "timeline": timeline_data,
            "snapshot_count": len(snapshots),
            "timestamp": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating timeline: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Health check endpoint for Kamma Appearance API
    """
    return {
        "status": "healthy",
        "service": "Kamma Appearance API",
        "version": "2.0.0",
        "features": [
            "appearance_generation",
            "ai_image_generation",
            "voice_synthesis",
            "3d_animation_control",
            "temporal_tracking"
        ],
        "total_endpoints": 17,
        "timestamp": datetime.utcnow()
    }
