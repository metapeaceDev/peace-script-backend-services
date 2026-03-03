"""
Character Avatar & Animation API Router
========================================

API endpoints for character avatar visualization and animation generation.

Features:
1. Get current character visual state (based on Citta, Kamma, Path)
2. Generate animation based on mental state
3. Calculate state probability analysis
4. Provide Buddhist-accurate recommendations

Buddhist Framework Integration:
- Citta-Cetasika System: 89 consciousness types → visual states
- Kamma Engine: Balance affects avatar appearance
- Paticcasamuppāda: Probability calculations
- Path Attainment: Special visual markers (Sotāpanna+)

Dependencies:
- citta_cetasika_models: Current consciousness state
- kamma_engine: Kamma balance
- core_profile_models: Path stage
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime
from enum import Enum

router = APIRouter(
    prefix="",
    tags=["Character Avatar & Animation"]
)


# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class VisualState(str, Enum):
    """Visual states mapped from Citta categories"""
    KUSALA = "kusala"  # Wholesome - green aura
    AKUSALA = "akusala"  # Unwholesome - red aura
    VIPAKA = "vipaka"  # Resultant - blue aura
    KIRIYA = "kiriya"  # Functional - purple aura
    UNKNOWN = "unknown"  # Unknown/Loading - gray


class AnimationType(str, Enum):
    """Types of animations that can be generated"""
    PEACEFUL_BREATHING = "peaceful-breathing"  # Kusala states
    AGITATED_PULSE = "agitated-pulse"  # Akusala states
    NEUTRAL_FLOAT = "neutral-float"  # Vipāka states
    STEADY_GLOW = "steady-glow"  # Kiriya states
    MEDITATION = "meditation"  # Deep concentration
    ENLIGHTENMENT = "enlightenment"  # Path attainment


class PathStage(str, Enum):
    """Path attainment stages"""
    SOTAPANNA = "sotapanna"
    SAKADAGAMI = "sakadagami"
    ANAGAMI = "anagami"
    ARAHANT = "arahant"


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class AvatarStateResponse(BaseModel):
    """Current avatar visual state"""
    model_id: str
    visual_state: VisualState
    color: str = Field(..., description="Hex color code")
    aura: str = Field(..., description="RGBA aura color")
    glow: str = Field(..., description="RGBA glow color")
    animation: str = Field(..., description="CSS animation class")
    brightness: float = Field(ge=0.0, le=2.0, description="Brightness multiplier")
    
    # Current mental state
    citta_category: Optional[str] = None
    vedana: Optional[str] = None
    intensity: Optional[float] = None
    
    # Kamma influence
    kamma_balance_percentage: Optional[float] = None
    
    # Path attainment
    path_stage: Optional[PathStage] = None
    path_marker: Optional[Dict[str, Any]] = None
    
    timestamp: datetime = Field(default_factory=datetime.now)


class GenerateAnimationRequest(BaseModel):
    """Request to generate character animation"""
    citta_state: Optional[Dict[str, Any]] = Field(
        None,
        description="Current citta state data"
    )
    kamma_balance: Optional[Dict[str, Any]] = Field(
        None,
        description="Kamma balance data"
    )
    path_stage: Optional[str] = None
    animation_type: str = Field(
        default="neutral-float",
        description="Type of animation to generate"
    )
    duration_seconds: int = Field(
        default=5,
        ge=1,
        le=30,
        description="Animation duration"
    )
    resolution: str = Field(
        default="1920x1080",
        description="Video resolution"
    )


class GenerateAnimationResponse(BaseModel):
    """Response with generated animation"""
    animation_id: str
    animation_url: str
    animation_type: str
    duration_seconds: int
    resolution: str
    file_size_mb: Optional[float] = None
    generated_at: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None


class ProbabilityAnalysisResponse(BaseModel):
    """Probability analysis of current mental state"""
    model_id: str
    current_state: str
    probability_percentage: float = Field(ge=0.0, le=100.0)
    confidence_level: str  # "high", "medium", "low"
    
    # Contributing factors
    kamma_influence: float = Field(ge=0.0, le=100.0)
    path_influence: Optional[float] = Field(None, ge=0.0, le=100.0)
    anusaya_influence: float = Field(ge=0.0, le=100.0)
    
    # Predictions
    likely_next_states: List[Dict[str, Any]]
    
    # Recommendations
    recommendation: str
    practices: List[str]
    
    timestamp: datetime = Field(default_factory=datetime.now)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def map_citta_to_visual_state(citta_category: str) -> VisualState:
    """Map citta category to visual state"""
    category_lower = citta_category.lower()
    
    if "kusala" in category_lower:
        return VisualState.KUSALA
    elif "akusala" in category_lower:
        return VisualState.AKUSALA
    elif "vipaka" in category_lower or "vipāka" in category_lower:
        return VisualState.VIPAKA
    elif "kiriya" in category_lower or "kriyā" in category_lower:
        return VisualState.KIRIYA
    else:
        return VisualState.UNKNOWN


def calculate_brightness(kamma_balance: Dict[str, Any]) -> float:
    """Calculate brightness based on kamma balance"""
    if not kamma_balance or "balance" not in kamma_balance:
        return 1.0
    
    kusala_percentage = kamma_balance["balance"].get("net_kusala_percentage", 50)
    # Map 0-100% to 0.5-1.5 brightness
    brightness = 0.5 + (kusala_percentage / 100)
    return round(brightness, 2)


def get_path_marker(path_stage: Optional[str]) -> Optional[Dict[str, Any]]:
    """Get visual marker for path attainment"""
    if not path_stage:
        return None
    
    markers = {
        "sotapanna": {
            "halo": "#fbbf24",  # Amber
            "particles": 7,
            "label": "โสดาบัน (Stream-Enterer)",
            "icon": "🌟"
        },
        "sakadagami": {
            "halo": "#f59e0b",  # Orange
            "particles": 14,
            "label": "สกทาคามี (Once-Returner)",
            "icon": "✨"
        },
        "anagami": {
            "halo": "#dc2626",  # Red
            "particles": 21,
            "label": "อนาคามี (Non-Returner)",
            "icon": "🔥"
        },
        "arahant": {
            "halo": "#ffffff",  # White
            "particles": 108,  # Buddhist sacred number
            "label": "อรหันต์ (Arahant)",
            "icon": "💎"
        }
    }
    
    return markers.get(path_stage.lower())


def calculate_state_probability(
    citta_category: str,
    kamma_balance: Dict[str, Any],
    path_stage: Optional[str]
) -> Dict[str, Any]:
    """
    Calculate probability of current mental state arising.
    
    Buddhist Logic:
    - Kusala probability ∝ Kusala kamma percentage
    - Akusala probability ∝ Akusala kamma percentage
    - Path attainment reduces akusala probability
    """
    kusala_percentage = 50  # Default
    if kamma_balance and "balance" in kamma_balance:
        kusala_percentage = kamma_balance["balance"].get("net_kusala_percentage", 50)
    
    akusala_percentage = 100 - kusala_percentage
    
    is_kusala = "kusala" in citta_category.lower()
    is_akusala = "akusala" in citta_category.lower()
    
    if is_kusala:
        base_probability = kusala_percentage
    elif is_akusala:
        base_probability = akusala_percentage
    else:
        base_probability = 50  # Neutral
    
    # Path stage modifier
    if path_stage and is_akusala:
        # Path attainment reduces unwholesome probability
        base_probability *= 0.5  # 50% reduction
    
    # Determine confidence
    if base_probability >= 70:
        confidence = "high"
    elif base_probability >= 40:
        confidence = "medium"
    else:
        confidence = "low"
    
    return {
        "probability": round(base_probability, 1),
        "confidence": confidence,
        "kamma_influence": kusala_percentage,
        "path_influence": 50.0 if path_stage else None
    }


def generate_recommendations(
    visual_state: VisualState,
    probability: float,
    path_stage: Optional[str]
) -> Dict[str, Any]:
    """Generate Buddhist practice recommendations"""
    
    if visual_state == VisualState.AKUSALA:
        recommendation = "⚠️ ควรเพิ่มการปฏิบัติธรรม เจริญสติ และพิจารณามรณานุสติ"
        practices = [
            "🧘 เจริญสติปัฏฐาน (Satipaṭṭhāna)",
            "💀 พิจารณามรณานุสติ (Maraṇānussati)",
            "🙏 เจริญเมตตาภาวนา (Mettā)",
            "📖 ศึกษาอริยสัจ (Four Noble Truths)"
        ]
    elif visual_state == VisualState.KUSALA:
        if probability >= 70:
            recommendation = "✅ สภาวะจิตดีมาก ควรรักษาและพัฒนาต่อไป"
        else:
            recommendation = "⚙️ ควรรักษาสติต่อเนื่อง มีสติในการกระทำ"
        
        practices = [
            "✅ รักษาสติต่อเนื่อง",
            "📖 ศึกษาธรรมะเพิ่มเติม",
            "🎁 เจริญทานบารมี",
            "🧘 ฝึกสมถะและวิปัสสนา"
        ]
    elif visual_state == VisualState.VIPAKA:
        recommendation = "👁️ สังเกตวิบากกรรม เข้าใจกฎแห่งกรรม สร้างกุศลกรรมใหม่"
        practices = [
            "👁️ สังเกตวิบากกรรมที่เกิดขึ้น",
            "🔄 เข้าใจกฎแห่งกรรม (Kamma-niyāma)",
            "⚖️ สร้างกุศลกรรมใหม่",
            "🙏 เจริญกตัญญูกตเวทิตา"
        ]
    else:
        recommendation = "⚙️ รักษาสติและความตระหนักรู้ในปัจจุบันขณะ"
        practices = [
            "🧘 เจริญสติในปัจจุบันขณะ",
            "📖 ศึกษาอภิธรรม",
            "🔄 พิจารณาไตรลักษณ์"
        ]
    
    return {
        "recommendation": recommendation,
        "practices": practices
    }


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.get("/{model_id}/avatar-state", response_model=AvatarStateResponse)
async def get_avatar_state(model_id: str):
    """
    Get current avatar visual state based on latest citta moment.
    
    Returns visual properties (color, aura, animation) that represent
    the character's current mental state according to Buddhist psychology.
    
    Example:
        GET /api/character/peace-mind-001/avatar-state
    """
    # Fetch actual data from DigitalMindModel and MindState
    try:
        from documents import DigitalMindModel, MindState
        
        # Get model
        model = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
        if not model:
            raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
        
        # Get latest mind state for this model (using model_id as user_id)
        mind_state = await MindState.find_one(MindState.user_id == model_id)
        
        # Calculate kamma balance from MindState counters
        kusala_total = mind_state.kusala_count_total if mind_state else 0
        akusala_total = mind_state.akusala_count_total if mind_state else 0
        total_actions = kusala_total + akusala_total
        kamma_balance = (kusala_total / total_actions * 100) if total_actions > 0 else 50.0
        
        # Determine visual state from kamma balance and virtue levels
        if mind_state and mind_state.sila >= 7.0 and mind_state.panna >= 6.0:
            visual_state = VisualState.KUSALA
            color = "#10b981"  # Emerald green
            animation = "peaceful-breathing"
            citta_category = "Kusala"
            vedana = "somanassa"
            brightness = 1.2
        elif mind_state and (mind_state.sila < 4.0 or mind_state.current_anusaya.get("dosa", 0) > 6.0):
            visual_state = VisualState.AKUSALA
            color = "#ef4444"  # Red
            animation = "agitated-pulse"
            citta_category = "Akusala"
            vedana = "domanassa"
            brightness = 0.8
        else:
            visual_state = VisualState.VIPAKA
            color = "#8b5cf6"  # Purple
            animation = "neutral-float"
            citta_category = "Vipāka"
            vedana = "upekka"
            brightness = 1.0
        
        # Check path attainment from core_profile
        path_stage = None
        path_marker = None
        if model.core_profile_obj:
            if model.core_profile_obj.is_noble():
                bhumi_type = model.core_profile_obj.character_status.type
                # Map CoreProfile types to PathStage enum
                type_to_path = {
                    "Sotāpanna": PathStage.SOTAPANNA,
                    "Sakadāgāmī": PathStage.SAKADAGAMI,
                    "Anāgāmī": PathStage.ANAGAMI,
                    "Arahant": PathStage.ARAHANT
                }
                path_stage = type_to_path.get(bhumi_type)
                if path_stage:
                    path_marker = {
                        "icon": "🏅",
                        "stage": bhumi_type,
                        "fetters_broken": len(model.core_profile_obj.character_status.fetters_broken)
                    }
        
        return AvatarStateResponse(
            model_id=model_id,
            visual_state=visual_state,
            color=color,
            aura=f"rgba{tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.3,)}".replace("'", ""),
            glow=f"rgba{tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.6,)}".replace("'", ""),
            animation=animation,
            brightness=brightness,
            citta_category=citta_category,
            vedana=vedana,
            intensity=mind_state.sati_strength if mind_state else 5.0,
            kamma_balance_percentage=round(kamma_balance, 1),
            path_stage=path_stage,
            path_marker=path_marker
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching avatar state: {e} - character_avatar.py:419")
        # Fallback to safe defaults
        return AvatarStateResponse(
            model_id=model_id,
            visual_state=VisualState.VIPAKA,
            color="#8b5cf6",
            aura="rgba(139, 92, 246, 0.3)",
            glow="rgba(139, 92, 246, 0.6)",
            animation="neutral-float",
            brightness=1.0,
            citta_category="Vipāka",
            vedana="upekka",
            intensity=5.0,
            kamma_balance_percentage=50.0,
            path_stage=None,
            path_marker=None
        )


@router.post("/{model_id}/generate-animation", response_model=GenerateAnimationResponse)
async def generate_animation(
    model_id: str,
    request: GenerateAnimationRequest
):
    """
    Generate animation based on current mental state.
    
    Creates a visual animation that represents the character's
    consciousness state (Kusala/Akusala/Vipāka/Kiriya).
    
    Animation types:
    - peaceful-breathing: Kusala states (smooth, calm)
    - agitated-pulse: Akusala states (rapid, unstable)
    - neutral-float: Vipāka states (flowing, passive)
    - steady-glow: Kiriya states (constant, functional)
    - meditation: Deep concentration states
    - enlightenment: Path attainment moments
    
    Example:
        POST /api/character/peace-mind-001/generate-animation
        {
            "animation_type": "peaceful-breathing",
            "duration_seconds": 10,
            "resolution": "1920x1080"
        }
    """
    try:
        # Import animation engine
        from modules.animation_engine import create_animation_engine
        
        # Extract citta state
        citta_category = "kusala"  # Default
        brightness = 1.0
        
        if request.citta_state:
            category = request.citta_state.get("category", "").lower()
            if "kusala" in category:
                citta_category = "kusala"
                brightness = 1.3
            elif "akusala" in category:
                citta_category = "akusala"
                brightness = 0.8
            elif "vipaka" in category:
                citta_category = "vipaka"
                brightness = 1.0
            elif "kiriya" in category:
                citta_category = "kiriya"
                brightness = 1.1
        
        # Parse resolution
        width, height = 1920, 1080
        if request.resolution:
            parts = request.resolution.lower().split('x')
            if len(parts) == 2:
                width, height = int(parts[0]), int(parts[1])
        
        # Create animation engine
        engine = create_animation_engine()
        
        # Generate animation
        result = engine.generate_animation(
            model_id=model_id,
            citta_state=citta_category,
            animation_type=request.animation_type,
            duration_seconds=request.duration_seconds,
            resolution=(width, height),
            brightness=brightness,
            path_stage=request.path_stage,
            output_format="mp4"
        )
        
        # Check for errors
        if "error" in result:
            # Fallback to mock if rendering fails
            animation_id = f"anim_{model_id}_{int(datetime.now().timestamp())}"
            return GenerateAnimationResponse(
                animation_id=animation_id,
                animation_url=f"/media/animations/{animation_id}.mp4",
                animation_type=request.animation_type,
                duration_seconds=request.duration_seconds,
                resolution=request.resolution,
                file_size_mb=25.8,
                metadata={
                    "citta_category": citta_category,
                    "kamma_balance": request.kamma_balance.get("balance", {}).get("net_kusala_percentage", 50) if request.kamma_balance else 50,
                    "path_stage": request.path_stage,
                    "render_engine": "Blender + FFmpeg",
                    "status": "render_failed",
                    "error": result["error"]
                }
            )
        
        # Success - return actual result
        return GenerateAnimationResponse(
            animation_id=result["animation_id"],
            animation_url=result["animation_url"],
            animation_type=request.animation_type,
            duration_seconds=result["duration_seconds"],
            resolution=result["resolution"],
            file_size_mb=result.get("file_size_mb", 0),
            metadata={
                "citta_category": citta_category,
                "kamma_balance": request.kamma_balance.get("balance", {}).get("net_kusala_percentage", 50) if request.kamma_balance else 50,
                "path_stage": request.path_stage,
                "render_engine": "Blender + FFmpeg",
                "status": "success",
                "rendered_at": result.get("rendered_at")
            }
        )
    
    except Exception as e:
        # Fallback to mock response
        animation_id = f"anim_{model_id}_{int(datetime.now().timestamp())}"
        return GenerateAnimationResponse(
            animation_id=animation_id,
            animation_url=f"/media/animations/{animation_id}.mp4",
            animation_type=request.animation_type,
            duration_seconds=request.duration_seconds,
            resolution=request.resolution,
            file_size_mb=25.8,
            metadata={
                "citta_category": request.citta_state.get("category") if request.citta_state else "unknown",
                "kamma_balance": request.kamma_balance.get("balance", {}).get("net_kusala_percentage", 50) if request.kamma_balance else 50,
                "path_stage": request.path_stage,
                "render_engine": "Blender + FFmpeg",
                "status": "fallback_mock",
                "error": str(e)
            }
        )


@router.get("/{model_id}/probability-analysis", response_model=ProbabilityAnalysisResponse)
async def get_probability_analysis(
    model_id: str,
    include_predictions: bool = Query(True, description="Include next state predictions")
):
    """
    Analyze probability of current mental state arising.
    
    Buddhist Analysis:
    - Current state probability based on kamma balance
    - Path stage influence on wholesome/unwholesome states
    - Anusaya (latent tendencies) influence
    - Predictions for likely next states
    - Practice recommendations
    
    Example:
        GET /api/character/peace-mind-001/probability-analysis?include_predictions=true
    """
    # Implement actual probability calculation integrating:
    # 1. Kamma Engine: Balance analysis
    # 2. Citta-Cetasika: Current state
    # 3. Paticcasamuppāda: Conditional arising
    # 4. Anusaya: Latent tendencies
    
    try:
        from documents import DigitalMindModel, MindState
        
        # Get model and mind state
        model = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
        if not model:
            raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
        
        mind_state = await MindState.find_one(MindState.user_id == model_id)
        if not mind_state:
            raise HTTPException(status_code=404, detail=f"Mind state for {model_id} not found")
        
        # 1. Calculate kamma balance influence
        kusala_total = mind_state.kusala_count_total
        akusala_total = mind_state.akusala_count_total
        total_actions = kusala_total + akusala_total
        kamma_balance = (kusala_total / total_actions * 100) if total_actions > 0 else 50.0
        
        # 2. Determine current state from virtue levels
        virtue_avg = (mind_state.sila + mind_state.samadhi + mind_state.panna) / 3
        if virtue_avg >= 7.0:
            current_state = "Kusala (Wholesome)"
            probability = kamma_balance
            confidence = "high" if kamma_balance > 70 else "medium"
        elif virtue_avg <= 4.0:
            current_state = "Akusala (Unwholesome)"
            probability = 100 - kamma_balance
            confidence = "high" if kamma_balance < 30 else "medium"
        else:
            current_state = "Vipāka (Neutral/Result)"
            probability = 50.0
            confidence = "medium"
        
        # 3. Path influence (if noble being)
        path_influence = None
        if model.core_profile_obj and model.core_profile_obj.is_noble():
            bhumi_type = model.core_profile_obj.character_status.type
            # Map character types to path influence multipliers
            type_influence = {
                "Sotāpanna": 15.0,
                "Sakadāgāmī": 25.0,
                "Anāgāmī": 40.0,
                "Arahant": 100.0
            }
            path_influence = type_influence.get(bhumi_type, 0.0)
            probability = min(probability + path_influence, 100.0)
            confidence = "very_high"
        
        # 4. Anusaya influence (latent tendencies pushing toward akusala)
        anusaya_avg = sum(mind_state.current_anusaya.values()) / len(mind_state.current_anusaya)
        anusaya_influence = round(anusaya_avg * 10, 1)  # Scale 0-100
        
        # 5. Predict likely next states (if include_predictions)
        likely_next_states = []
        if include_predictions:
            # Kusala continuation probability
            kusala_momentum = kamma_balance * 0.7
            likely_next_states.append({
                "state": "Kusala (continued)",
                "probability": round(kusala_momentum, 1),
                "reason": f"Strong kusala kamma momentum ({kamma_balance:.1f}%)"
            })
            
            # Vipāka result probability
            vipaka_prob = 30.0 if kamma_balance > 60 else 15.0
            likely_next_states.append({
                "state": "Vipāka (pleasant result)" if kamma_balance > 50 else "Vipāka (unpleasant result)",
                "probability": round(vipaka_prob, 1),
                "reason": "Kusala kamma ripening" if kamma_balance > 50 else "Akusala kamma ripening"
            })
            
            # Akusala possibility (from anusaya)
            akusala_prob = anusaya_influence * 0.4
            if akusala_prob > 5.0:
                likely_next_states.append({
                    "state": "Akusala (brief)",
                    "probability": round(akusala_prob, 1),
                    "reason": f"Latent tendencies (anusaya: {anusaya_avg:.1f}/10)"
                })
            
            # Sort by probability
            likely_next_states.sort(key=lambda x: x["probability"], reverse=True)
        
        # 6. Generate recommendation
        if virtue_avg >= 7.0 and kamma_balance > 70:
            recommendation = "✅ สภาวะจิตดีมาก ควรรักษาและพัฒนาต่อไป รักษาสติต่อเนื่อง"
            practices = [
                "✅ รักษาสติต่อเนื่อง",
                "📖 ศึกษาธรรมะเพิ่มเติม",
                "🎁 เจริญทานบารมี",
                "🧘 ฝึกสมถะและวิปัสสนา"
            ]
        elif virtue_avg < 5.0 or anusaya_avg > 5.0:
            recommendation = "⚠️ สภาวะจิตไม่มั่นคง ควรระมัดระวังและเพิ่มสติ"
            practices = [
                "🧘 ฝึกสมถะภาวนาเพื่อสร้างสมาธิ",
                "🛡️ รักษาศีล 5 อย่างเคร่งครัด",
                "📿 พิจารณากรรมและผลกรรม",
                "💬 ปรึกษาครูบาอาจารย์"
            ]
        else:
            recommendation = "💡 สภาวะจิตปานกลาง ควรพัฒนาต่อเนื่อง"
            practices = [
                "📖 ศึกษาธรรมะเพื่อเพิ่มปัญญา",
                "🧘 ฝึกสติปัฏฐานสี่",
                "🎁 เจริญทานบารมี",
                "🛡️ รักษาศีลให้มั่นคง"
            ]
        
        return ProbabilityAnalysisResponse(
            model_id=model_id,
            current_state=current_state,
            probability_percentage=round(probability, 1),
            confidence_level=confidence,
            kamma_influence=round(kamma_balance, 1),
            path_influence=path_influence,
            anusaya_influence=round(anusaya_influence, 1),
            likely_next_states=likely_next_states,
            recommendation=recommendation,
            practices=practices
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error calculating probability: {e} - character_avatar.py:719")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error calculating probability: {str(e)}")


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@router.get("/animation-types", response_model=List[Dict[str, Any]])
async def list_animation_types():
    """
    List available animation types with descriptions.
    
    Returns all animation types that can be generated,
    mapped to Buddhist mental states.
    """
    return [
        {
            "type": "peaceful-breathing",
            "label": "Peaceful Breathing",
            "description": "Smooth, calm animation for Kusala (wholesome) states",
            "citta_types": ["Kusala"],
            "duration_range": "3-30 seconds"
        },
        {
            "type": "agitated-pulse",
            "label": "Agitated Pulse",
            "description": "Rapid, unstable animation for Akusala (unwholesome) states",
            "citta_types": ["Akusala"],
            "duration_range": "2-15 seconds"
        },
        {
            "type": "neutral-float",
            "label": "Neutral Float",
            "description": "Flowing, passive animation for Vipāka (resultant) states",
            "citta_types": ["Vipāka"],
            "duration_range": "5-30 seconds"
        },
        {
            "type": "steady-glow",
            "label": "Steady Glow",
            "description": "Constant, functional animation for Kiriya states",
            "citta_types": ["Kiriya"],
            "duration_range": "3-30 seconds"
        },
        {
            "type": "meditation",
            "label": "Deep Meditation",
            "description": "Concentrated, still animation for Jhāna states",
            "citta_types": ["Kusala Jhāna"],
            "duration_range": "10-60 seconds"
        },
        {
            "type": "enlightenment",
            "label": "Path Attainment",
            "description": "Radiant, transformative animation for Magga (path) moments",
            "citta_types": ["Magga", "Phala"],
            "duration_range": "5-30 seconds"
        }
    ]


# ============================================================================
# LORA MODELS (Must be defined before endpoint)
# ============================================================================

class LoRAModel(BaseModel):
    """LoRA model information"""
    name: str = Field(..., description="LoRA model filename (without extension)")
    filename: str = Field(..., description="Full filename including extension")
    size_mb: float = Field(..., description="File size in MB")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "add_detail",
                "filename": "add_detail.safetensors",
                "size_mb": 36.1
            }
        }


class GetLoRAsResponse(BaseModel):
    """Response with available LoRA models"""
    success: bool
    loras: List[LoRAModel]
    total_count: int
    comfyui_path: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "loras": [
                    {
                        "name": "add_detail",
                        "filename": "add_detail.safetensors",
                        "size_mb": 36.1
                    }
                ],
                "total_count": 1,
                "comfyui_path": "/Users/surasak.peace/ComfyUI/models/loras"
            }
        }


# ============================================================================
# LORA ENDPOINT
# ============================================================================

@router.get("/loras/available", response_model=GetLoRAsResponse)
async def get_available_loras():
    """
    รายการโมเดล LoRA ที่มีใน ComfyUI
    
    Get list of available LoRA models from ComfyUI/models/loras folder.
    Scans for .safetensors and .ckpt files.
    
    Returns:
        GetLoRAsResponse with list of LoRA models
        
    Example:
        GET /api/character/loras/available
    """
    from core.logging_config import get_logger
    import os
    import glob
    
    logger = get_logger(__name__)
    logger.info("📂 Scanning for available LoRA models")
    
    try:
        # Get ComfyUI path from environment or use default
        comfyui_base = os.getenv('COMFYUI_PATH', '/Users/surasak.peace/ComfyUI')
        loras_path = os.path.join(comfyui_base, 'models', 'loras')
        
        logger.info(f"   Scanning path: {loras_path}")
        
        if not os.path.exists(loras_path):
            logger.warning(f"⚠️ LoRA path does not exist: {loras_path}")
            return GetLoRAsResponse(
                success=True,
                loras=[],
                total_count=0,
                comfyui_path=loras_path
            )
        
        # Scan for .safetensors and .ckpt files
        lora_files = []
        lora_files.extend(glob.glob(os.path.join(loras_path, '*.safetensors')))
        lora_files.extend(glob.glob(os.path.join(loras_path, '*.ckpt')))
        lora_files.extend(glob.glob(os.path.join(loras_path, '*.pt')))
        
        # Build response
        loras = []
        for filepath in lora_files:
            filename = os.path.basename(filepath)
            name = os.path.splitext(filename)[0]
            size_bytes = os.path.getsize(filepath)
            size_mb = size_bytes / (1024 * 1024)
            
            loras.append(LoRAModel(
                name=name,
                filename=filename,
                size_mb=round(size_mb, 1)
            ))
        
        # Sort by name
        loras.sort(key=lambda x: x.name)
        
        logger.info(f"✅ Found {len(loras)} LoRA models")
        for lora in loras:
            logger.info(f"   - {lora.filename} ({lora.size_mb} MB)")
        
        return GetLoRAsResponse(
            success=True,
            loras=loras,
            total_count=len(loras),
            comfyui_path=loras_path
        )
        
    except Exception as e:
        logger.error(f"❌ Error scanning LoRA models: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to scan LoRA models: {str(e)}"
        )


# ============================================================================
# NEW ENDPOINT: FULL APPEARANCE (Added 2 Nov 2568)
# ============================================================================

@router.get("/{model_id}/full-appearance")
async def get_full_appearance(model_id: str):
    """
    🎭 Get Complete Appearance Profile
    
    Combines all appearance aspects:
    - Physical (from Kāyakamma via kamma_appearance_analyzer)
    - Voice (from Vacīkamma)
    - Movement/Demeanor (from Manokamma)
    - Current Citta State
    - Kamma Influence Breakdown
    - 28 Rūpa Data
    
    Returns unified appearance data for comprehensive character visualization.
    
    Buddhist Accuracy: 100% aligned with Abhidhamma
    - กายกรรม → Physical appearance
    - วจีกรรม → Voice characteristics  
    - มโนกรรม → Movement & demeanor
    """
    try:
        from documents import DigitalMindModel
        from modules.kamma_appearance_analyzer import KammaAppearanceAnalyzer
        from modules.rupa_engine import RupaCalculationEngine
        from core.logging_config import get_logger
        
        logger = get_logger(__name__)
        logger.info(f"Getting full appearance for model: {model_id}")
        
        # 1. Get DigitalMindModel
        dmm = await DigitalMindModel.find_one(
            DigitalMindModel.model_id == model_id
        )
        
        if not dmm:
            raise HTTPException(
                status_code=404,
                detail=f"DigitalMindModel not found: {model_id}"
            )
        
        # 2. Get current citta state (existing function)
        citta_state_response = await get_avatar_state(model_id)
        
        # 3. Analyze kamma for appearance
        analyzer = KammaAppearanceAnalyzer()
        
        # Build kamma_ledger from kamma_profile
        # DigitalMindModel has kamma_profile dict, not kamma_engine object
        kamma_profile = dmm.kamma_profile or {}
        kamma_ledger = {
            "kamma_log": kamma_profile.get("recent_kamma_events", []),
            "kusala_stock_points": kamma_profile.get("kusala_points", 0),
            "akusala_stock_points": kamma_profile.get("akusala_points", 0)
        }
        
        appearance_profile = analyzer.analyze_kamma_ledger(
            kamma_ledger=kamma_ledger,
            model_id=model_id
        )
        
        # 4. Calculate 28 Rūpa
        rupa_engine = RupaCalculationEngine()
        rupa_profile = None
        
        try:
            rupa_profile = rupa_engine.calculate_mahabhuta_from_core_profile(dmm)
        except Exception as e:
            logger.warning(f"Could not calculate rūpa: {str(e)}")
        
        # 5. Build unified response
        full_appearance = {
            "model_id": model_id,
            "timestamp": datetime.now().isoformat(),
            
            # Physical Appearance (from HealthScore)
            "physical": {
                "overall_health": appearance_profile.health_score.overall_health,
                "vitality_level": appearance_profile.health_score.vitality_level,
                "body_strength": appearance_profile.health_score.body_strength,
                "skin_quality": appearance_profile.health_score.skin_quality,
                "skin_tone": appearance_profile.health_score.skin_quality,
                "skin_tone_desc": appearance_profile.health_score.skin_tone_desc,
                "body_type": appearance_profile.health_score.body_type_tendency,
                "fitness_level": appearance_profile.health_score.fitness_level,
                "energy_level": appearance_profile.health_score.energy_level,
                
                # Default external character attributes
                "hair_color": "black",
                "hair_style": "short",
                "eye_color": "brown",
                "facial_features": [],
                "height_cm": 170,
                "weight_kg": 65
            },
            
            # Voice Characteristics (from VoiceScore)
            "voice": {
                "clarity_score": appearance_profile.voice_score.clarity_score,
                "pleasantness_score": appearance_profile.voice_score.pleasantness_score,
                "confidence_score": appearance_profile.voice_score.confidence_score,
                "tone_quality": appearance_profile.voice_score.clarity_score,
                "clarity": appearance_profile.voice_score.clarity_score,
                "pleasantness": appearance_profile.voice_score.pleasantness_score,
                "confidence": appearance_profile.voice_score.confidence_score,
                "voice_character": appearance_profile.voice_score.voice_tone_desc,
                "voice_tone_desc": appearance_profile.voice_score.voice_tone_desc,
                "speech_pattern_desc": appearance_profile.voice_score.speech_pattern_desc,
                "pitch_range": appearance_profile.voice_score.pitch_tendency,
                "pitch_tendency": appearance_profile.voice_score.pitch_tendency,
                "volume_level": appearance_profile.voice_score.volume_tendency,
                "volume_tendency": appearance_profile.voice_score.volume_tendency,
                "articulation_quality": appearance_profile.voice_score.articulation_quality,
                
                # Kamma influence on voice
                "truthful_kamma": appearance_profile.voice_score.truthful_kamma_score,
                "lying_kamma": appearance_profile.voice_score.lying_kamma_score,
                "gentle_speech": appearance_profile.voice_score.gentle_speech_score,
                "harsh_speech": appearance_profile.voice_score.harsh_speech_score,
                "harmonious_speech": appearance_profile.voice_score.harmonious_speech_score,
                "divisive_speech": appearance_profile.voice_score.divisive_speech_score
            },
            
            # Movement & Demeanor (from DemeanorScore)
            "movement": {
                "approachability": appearance_profile.demeanor_score.approachability,
                "charisma": appearance_profile.demeanor_score.charisma,
                "peacefulness": appearance_profile.demeanor_score.peacefulness,
                "tension_level": appearance_profile.demeanor_score.tension_level,
                "default_expression": appearance_profile.demeanor_score.default_expression,
                "eye_expression": appearance_profile.demeanor_score.eye_expression,
                "facial_tension": appearance_profile.demeanor_score.facial_tension,
                "posture_desc": appearance_profile.demeanor_score.posture_desc,
                "gait_desc": appearance_profile.demeanor_score.gait_desc,
                "movement_quality": appearance_profile.demeanor_score.movement_quality,
                
                # Kamma influence on demeanor (with defaults)
                "metta_kamma": getattr(appearance_profile.demeanor_score, 'metta_kamma_score', 0),
                "byapada_kamma": getattr(appearance_profile.demeanor_score, 'byapada_kamma_score', 0),
                "meditation_kamma": getattr(appearance_profile.demeanor_score, 'meditation_kamma_score', 0)
            },
            
            # Current Mental State (Citta)
            "citta_state": {
                "visual_state": citta_state_response.visual_state,
                "color": citta_state_response.color,
                "animation": citta_state_response.animation,
                "citta_category": citta_state_response.citta_category,
                "vedana": citta_state_response.vedana,
                "intensity": citta_state_response.intensity,
                "brightness": citta_state_response.brightness
            },
            
            # Kamma Influence
            "kamma_influence": {
                "kusala_percentage": appearance_profile.kusala_percentage,
                "akusala_percentage": appearance_profile.akusala_percentage,
                "overall_balance": appearance_profile.overall_kamma_balance,
                "kamma_balance_percentage": citta_state_response.kamma_balance_percentage,
                "dominant_categories": getattr(appearance_profile, 'dominant_kamma_categories', []),
                "total_analyzed": getattr(appearance_profile, 'total_kamma_analyzed', 0)
            },
            
            # Rūpa Data (28 Types)
            "rupa": {
                "available": rupa_profile is not None,
                "mahabhuta": rupa_profile.dict() if rupa_profile else None
            },
            
            # Overall Summary
            "summary": getattr(appearance_profile, 'summary', 'Character appearance based on kamma analysis'),
            "distinctive_features": getattr(appearance_profile, 'distinctive_features', []),
            "charisma_score": getattr(appearance_profile, 'charisma_score', 5.0)
        }
        
        logger.info(f"Successfully generated full appearance for model: {model_id}")
        return full_appearance
    
    except HTTPException:
        raise
    except Exception as e:
        from core.logging_config import get_logger
        logger = get_logger(__name__)
        logger.error(f"Error generating full appearance: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate full appearance: {str(e)}"
        )


# ============================================================================
# AI IMAGE GENERATION ENDPOINT
# ============================================================================

class GenerateImageRequest(BaseModel):
    """Request for AI image generation"""
    style: Literal["realistic", "anime", "portrait", "cinematic"] = Field("realistic", description="Image style")
    width: int = Field(512, description="Image width", ge=256, le=1024)
    height: int = Field(768, description="Image height", ge=256, le=1024)
    steps: int = Field(30, description="Number of generation steps", ge=20, le=50)
    cfg: float = Field(7.0, description="CFG scale", ge=5.0, le=15.0)
    num_variations: int = Field(1, description="Number of variations to generate", ge=1, le=4)
    
    # Advanced controls (optional)
    seed: Optional[int] = Field(None, description="Random seed for reproducibility")
    custom_prompt: Optional[str] = Field(None, description="Override auto-generated prompt")
    custom_negative_prompt: Optional[str] = Field(None, description="Override auto-generated negative prompt")
    lora_name: Optional[str] = Field(None, description="LoRA model name to use (without extension)")
    lora_strength: float = Field(1.0, description="LoRA strength/weight", ge=0.0, le=2.0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "style": "realistic",
                "width": 512,
                "height": 768,
                "steps": 30,
                "cfg": 7.0,
                "num_variations": 1,
                "seed": 1234567890,
                "custom_prompt": "a serene Thai Buddhist monk meditating",
                "custom_negative_prompt": "ugly, blurry, deformed",
                "lora_name": "add_detail",
                "lora_strength": 1.0
            }
        }


class GeneratedImageData(BaseModel):
    """Single generated image with metadata"""
    image_base64: str = Field(..., description="Base64 encoded PNG image")
    prompt: str = Field(..., description="Positive prompt used")
    negative_prompt: str = Field(..., description="Negative prompt used")
    seed: Optional[int] = Field(default=None, description="Random seed used")


class GenerateImageResponse(BaseModel):
    """Response with generated images"""
    success: bool = Field(..., description="Whether generation was successful")
    images: List[GeneratedImageData] = Field(..., description="List of generated images")
    generation_time: float = Field(..., description="Time taken to generate (seconds)")
    model_used: str = Field(..., description="ComfyUI model used")
    error: Optional[str] = Field(default=None, description="Error message if failed")


@router.post("/{model_id}/generate-image", response_model=GenerateImageResponse)
async def generate_character_avatar_image(
    model_id: str,
    request: GenerateImageRequest
):
    """
    Generate AI image using ComfyUI based on character's appearance
    
    This endpoint:
    1. Retrieves character data (ExternalCharacter)
    2. Generates SD prompt from appearance using AppearancePromptGenerator
    3. Calls ComfyUI to generate image(s)
    4. Returns image(s) as base64
    
    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/v1/character-avatar/peace-mind-001/generate-image" \\
          -H "Content-Type: application/json" \\
          -d '{
            "style": "realistic",
            "width": 512,
            "height": 768,
            "steps": 30,
            "cfg": 7.0,
            "num_variations": 1
          }'
        ```
    
    Args:
        model_id: DigitalMindModel ID
        request: Generation parameters
    
    Returns:
        GenerateImageResponse with base64 images
    
    Raises:
        404: Character not found
        500: ComfyUI generation failed
        503: ComfyUI service not available
    """
    import time
    import base64
    from modules.comfyui_client import generate_with_comfyui, batch_generate_with_comfyui, ComfyUIClient
    from modules.ai_image_generator import AppearancePromptGenerator
    from core.logging_config import get_logger
    
    logger = get_logger(__name__)
    start_time = time.time()
    
    try:
        logger.info(f"🎨 Generating AI image for character: {model_id}")
        logger.info(f"📊 Full Parameters Received:")
        logger.info(f"  - Style: {request.style}")
        logger.info(f"  - Size: {request.width} × {request.height}")
        logger.info(f"  - Steps: {request.steps}")
        logger.info(f"  - CFG Scale: {request.cfg}")
        logger.info(f"  - Seed: {request.seed if request.seed else 'random'}")
        logger.info(f"  - Variations: {request.num_variations}")
        logger.info(f"  - LoRA: {request.lora_name if request.lora_name else 'None'}")
        
        # 1. Check if ComfyUI is available (optional - use placeholder if not)
        client = ComfyUIClient("http://127.0.0.1:8188")
        comfyui_available = client.check_health()
        
        if not comfyui_available:
            logger.warning("⚠️ ComfyUI server not running - returning placeholder image")
            
            # Generate placeholder base64 image
            from PIL import Image, ImageDraw, ImageFont
            import io
            import base64
            
            # Create simple placeholder
            img = Image.new('RGB', (request.width, request.height), color=(100, 100, 100))
            draw = ImageDraw.Draw(img)
            
            # Add text
            text = f"{model_id}\n(ComfyUI not available)"
            bbox = draw.textbbox((0, 0), text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            position = ((request.width - text_width) // 2, (request.height - text_height) // 2)
            draw.text(position, text, fill=(200, 200, 200))
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            elapsed = time.time() - start_time
            logger.info(f"✅ Generated placeholder in {elapsed:.2f}s")
            
            return GenerateImageResponse(
                images=[base64_image],
                prompt="placeholder",
                negative_prompt="",
                seed=0,
                used_comfyui=False,
                generation_time=elapsed
            )
        
        logger.info("✅ ComfyUI server is running")
        
        # 2. Get character data (with auto-generation if needed)
        from routers.kamma_appearance_router import get_external_character
        from documents import DigitalMindModel
        
        # First try to get existing ExternalCharacter
        external = await get_external_character(model_id)
        
        # If not found, check if model exists and throw helpful error
        if not external:
            logger.warning(f"No appearance profile for {model_id}")
            
            # Check if model exists
            dmm = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
            if not dmm:
                logger.error(f"Model not found: {model_id}")
                raise HTTPException(
                    status_code=404,
                    detail=f"Character model '{model_id}' not found. Please create the character first."
                )
            
            # Model exists but has no appearance - instruct user
            logger.error(f"Model {model_id} has no appearance profile")
            raise HTTPException(
                status_code=400,
                detail=f"Character '{model_id}' has no appearance profile. Please generate one first by calling POST /api/kamma-appearance/generate with body: {{\"model_id\": \"{model_id}\"}}"
            )
        
        logger.info(f"✅ Retrieved character data for: {model_id}")
        
        # 3. Generate prompt from character appearance (or use custom)
        if request.custom_prompt:
            logger.info("Using custom prompt provided by user")
            positive_prompt = request.custom_prompt
        else:
            prompt_generator = AppearancePromptGenerator()
            prompts = prompt_generator.generate_prompt(
                external=external,
                style=request.style
            )
            positive_prompt = prompts["positive"]
            logger.info(f"✅ Auto-generated prompt (length: {len(positive_prompt)} chars)")
        
        if request.custom_negative_prompt:
            logger.info("Using custom negative prompt provided by user")
            negative_prompt = request.custom_negative_prompt
        else:
            if not request.custom_prompt:
                # Use auto-generated negative prompt
                negative_prompt = prompts["negative"]
            else:
                # Default negative prompt for custom prompts
                negative_prompt = "ugly, deformed, blurry, low quality, worst quality, bad anatomy"
            logger.info(f"✅ Auto-generated negative prompt (length: {len(negative_prompt)} chars)")
        
        logger.debug(f"Positive: {positive_prompt[:100]}...")
        logger.debug(f"Negative: {negative_prompt[:100]}...")
        
        # Log seed if provided
        if request.seed is not None:
            logger.info(f"🌱 Using custom seed: {request.seed}")
        
        # Log LoRA if provided
        if request.lora_name:
            logger.info(f"🎨 Using LoRA: {request.lora_name} (strength: {request.lora_strength})")
        
        # 4. Generate with ComfyUI
        model_name = "realisticVisionV60B1_v51HyperVAE.safetensors"
        size_factor = max(1.0, (request.width * request.height) / (512 * 768))
        step_factor = max(0.5, request.steps / 30)
        comfy_timeout = int(min(max(600 * size_factor * step_factor, 600), 1200))
        logger.info(
            f"⏱️ Configured ComfyUI timeout: {comfy_timeout}s "
            f"(size_factor={size_factor:.2f}, step_factor={step_factor:.2f})"
        )
        
        if request.num_variations == 1:
            # Single image generation
            logger.info("🖼️  Generating single image...")
            logger.info(f"🔧 Calling ComfyUI with:")
            logger.info(f"   width={request.width}, height={request.height}")
            logger.info(f"   steps={request.steps}, cfg={request.cfg}")
            logger.info(f"   seed={request.seed if request.seed else 'random'}")
            
            image_data = generate_with_comfyui(
                prompt=positive_prompt,
                negative_prompt=negative_prompt,
                width=request.width,
                height=request.height,
                steps=request.steps,
                cfg=request.cfg,
                seed=request.seed,  # Pass seed from request
                comfyui_url="http://127.0.0.1:8188",
                model_name=model_name,
                lora_name=request.lora_name,
                lora_strength=request.lora_strength,
                timeout=comfy_timeout
            )
            
            if not image_data:
                logger.error("ComfyUI generation failed - no image data returned")
                raise HTTPException(
                    status_code=500,
                    detail="ComfyUI image generation failed. Check ComfyUI server logs."
                )
            
            # Convert to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            images = [GeneratedImageData(
                image_base64=image_base64,
                prompt=positive_prompt,
                negative_prompt=negative_prompt
            )]
            
            logger.info(f"✅ Generated image (size: {len(image_data)} bytes)")
        
        else:
            # Multiple variations
            logger.info(f"Generating {request.num_variations} variations...")
            images_data = batch_generate_with_comfyui(
                prompt=positive_prompt,
                negative_prompt=negative_prompt,
                num_variations=request.num_variations,
                width=request.width,
                height=request.height,
                steps=request.steps,
                cfg=request.cfg,
                comfyui_url="http://127.0.0.1:8188",
                model_name=model_name,
                lora_name=request.lora_name,
                lora_strength=request.lora_strength,
                timeout=comfy_timeout
            )
            
            if not images_data:
                logger.error("Batch generation failed - no images returned")
                raise HTTPException(
                    status_code=500,
                    detail="Batch generation failed. Check ComfyUI server logs."
                )
            
            images = []
            for i, img_data in enumerate(images_data):
                images.append(GeneratedImageData(
                    image_base64=base64.b64encode(img_data).decode('utf-8'),
                    prompt=positive_prompt,
                    negative_prompt=negative_prompt
                ))
                logger.info(f"✅ Generated variation {i+1}/{len(images_data)} (size: {len(img_data)} bytes)")
        
        # 5. Calculate generation time
        generation_time = time.time() - start_time
        
        logger.info(f"🎉 Successfully generated {len(images)} image(s) in {generation_time:.2f}s")
        
        return GenerateImageResponse(
            success=True,
            images=images,
            generation_time=generation_time,
            model_used=model_name
        )
    
    except TimeoutError as e:
        logger.error(f"ComfyUI generation timed out: {e}")
        raise HTTPException(
            status_code=504,
            detail="ComfyUI generation exceeded the allotted time. Please try again with smaller resolution or fewer steps."
        )
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Image generation failed: {e}", exc_info=True)
        
        generation_time = time.time() - start_time
        
        return GenerateImageResponse(
            success=False,
            images=[],
            generation_time=generation_time,
            model_used="N/A",
            error=str(e)
        )


# ============================================================================
# ENDPOINT: Save Generated Image to Gallery
# ============================================================================

class SaveImageRequest(BaseModel):
    """Request to save generated image to gallery"""
    image_base64: str = Field(..., description="Base64 encoded image")
    image_format: str = Field("png", description="Image format")
    image_size_kb: float = Field(0.0, description="Image size in KB")
    
    # Reference (NEW: actor_id for character-specific filtering)
    actor_id: Optional[str] = Field(None, description="Actor ID (for character-specific images)")
    
    # Generation parameters
    style: str = Field(..., description="Image style used")
    width: int = Field(512, description="Image width")
    height: int = Field(768, description="Image height")
    steps: int = Field(30, description="Sampling steps")
    cfg: float = Field(7.0, description="CFG scale")
    
    # Prompts
    positive_prompt: str = Field(..., description="Prompt used")
    negative_prompt: str = Field(..., description="Negative prompt used")
    seed: Optional[int] = Field(None, description="Random seed")
    
    # Generation info
    generation_time: float = Field(0.0, description="Generation time (seconds)")
    model_used: str = Field("", description="Model name used")
    
    # User notes (optional)
    notes: str = Field("", description="User notes")
    is_favorite: bool = Field(False, description="Mark as favorite")
    
    class Config:
        json_schema_extra = {
            "example": {
                "image_base64": "iVBORw0KGgoAAAANSUhEUg...",
                "style": "realistic",
                "width": 768,
                "height": 1024,
                "steps": 35,
                "cfg": 8.5,
                "positive_prompt": "a serene Thai Buddhist monk...",
                "negative_prompt": "ugly, deformed...",
                "seed": 1234567890,
                "generation_time": 18.5,
                "model_used": "realisticVisionV60B1",
                "notes": "Perfect for profile",
                "is_favorite": True
            }
        }


class SaveImageResponse(BaseModel):
    """Response from saving image"""
    success: bool
    image_id: str
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "image_id": "img_abc123xyz",
                "message": "Image saved to gallery successfully"
            }
        }


@router.post("/{model_id}/save-generated-image", response_model=SaveImageResponse)
async def save_generated_image(
    model_id: str,
    request: SaveImageRequest
):
    """
    บันทึกภาพที่สร้างลง Image Gallery
    
    Save generated image to gallery with full metadata for:
    - Viewing history of generated images
    - Reproducing images with same parameters
    - Managing favorite images
    - Setting images as profile avatars
    
    Args:
        model_id: Character model ID
        request: Image data and metadata
        
    Returns:
        SaveImageResponse with image_id
        
    Example:
        POST /api/character/peace-mind-001/save-generated-image
        {
            "image_base64": "iVBORw0KGgo...",
            "style": "realistic",
            "seed": 1234567890,
            "notes": "Best image so far!"
        }
    """
    import uuid
    from core.logging_config import get_logger
    from kamma_appearance_models import GeneratedImageDocument, GeneratedImageMetadata
    from modules.image_optimizer import ImageOptimizer  # ✨ RE-ENABLED: Generate thumbnails for gallery performance
    
    logger = get_logger(__name__)
    logger.info(f"💾 Saving generated image for model: {model_id}")
    
    try:
        # Generate unique image ID
        image_id = f"img_{uuid.uuid4().hex[:12]}"
        
        # Calculate image size if not provided
        if request.image_size_kb == 0.0:
            import base64
            image_bytes = base64.b64decode(request.image_base64)
            request.image_size_kb = len(image_bytes) / 1024
        
        # ✨ GENERATE HIGH-QUALITY THUMBNAILS for gallery performance
        # Gallery displays medium (512x512), modal displays full image
        logger.info(f"📸 Generating high-quality thumbnails (max quality settings)")
        
        optimizer = ImageOptimizer()
        thumbnails = optimizer.create_thumbnails(
            image_base64=request.image_base64,
            sizes=['medium']  # Only medium (512x512) for gallery grid
        )
        
        thumbnail_small = None  # Not needed for now
        thumbnail_medium = thumbnails.get('thumbnail_medium_base64')
        size_small_kb = None
        size_medium_kb = thumbnails.get('size_medium_kb')
        
        logger.info(f"   ✅ Medium thumbnail: {size_medium_kb:.2f} KB")
        
        # Create metadata WITHOUT thumbnails (use full image)
        metadata = GeneratedImageMetadata(
            # Full resolution image
            image_base64=request.image_base64,
            image_format=request.image_format,
            image_size_kb=round(request.image_size_kb, 2),
            
            # NEW: Optimized thumbnails
            thumbnail_small_base64=thumbnail_small,
            thumbnail_medium_base64=thumbnail_medium,
            thumbnail_small_size_kb=round(size_small_kb, 2) if size_small_kb else None,
            thumbnail_medium_size_kb=round(size_medium_kb, 2) if size_medium_kb else None,
            
            # Metadata
            model_id=model_id,
            actor_id=request.actor_id,  # Store actor_id for filtering
            style=request.style,
            width=request.width,
            height=request.height,
            steps=request.steps,
            cfg=request.cfg,
            positive_prompt=request.positive_prompt,
            negative_prompt=request.negative_prompt,
            seed=request.seed,
            generation_time=request.generation_time,
            model_used=request.model_used,
            timestamp=datetime.utcnow(),
            is_favorite=request.is_favorite,
            is_profile_avatar=False,
            notes=request.notes
        )
        
        # Create document
        doc = GeneratedImageDocument(
            image_id=image_id,
            model_id=model_id,
            actor_id=request.actor_id,  # NEW: Store actor_id at document level for efficient filtering
            metadata=metadata,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Save to MongoDB
        await doc.insert()
        
        logger.info(f"✅ Image saved successfully: {image_id}")
        logger.info(f"   Size: {metadata.image_size_kb:.2f} KB")
        logger.info(f"   Style: {request.style}")
        logger.info(f"   Seed: {request.seed}")
        logger.info(f"   Favorite: {request.is_favorite}")
        
        return SaveImageResponse(
            success=True,
            image_id=image_id,
            message="Image saved to gallery successfully"
        )
        
    except Exception as e:
        logger.error(f"❌ Error saving image: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save image: {str(e)}"
        )


# ============================================================================
# ENDPOINT: Get Generated Images History
# ============================================================================

class GeneratedImageHistoryItem(BaseModel):
    """Single image in history"""
    image_id: str
    image_base64: str
    actor_id: Optional[str] = None  # Actor ID for filtering
    
    # NEW: Thumbnails for optimal performance
    thumbnail_small_base64: Optional[str] = None  # 256x256 for actor cards
    thumbnail_medium_base64: Optional[str] = None  # 512x512 for gallery grid
    thumbnail_small_size_kb: Optional[float] = None
    thumbnail_medium_size_kb: Optional[float] = None
    
    style: str
    width: int
    height: int
    seed: Optional[int]
    positive_prompt: str
    generation_time: float
    timestamp: datetime
    is_favorite: bool
    notes: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "image_id": "img_abc123",
                "actor_id": "ACT-123",
                "style": "realistic",
                "seed": 1234567890,
                "timestamp": "2024-11-03T10:30:00"
            }
        }


class GetImagesHistoryResponse(BaseModel):
    """Response with list of generated images"""
    success: bool
    images: List[GeneratedImageHistoryItem]
    total_count: int
    model_id: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "images": [],
                "total_count": 10,
                "model_id": "peace-mind-001"
            }
        }


@router.get("/{model_id}/generated-images", response_model=GetImagesHistoryResponse)
async def get_generated_images_history(
    model_id: str,
    limit: int = Query(20, ge=1, le=100, description="Number of images to return"),
    skip: int = Query(0, ge=0, description="Number of images to skip"),
    favorites_only: bool = Query(False, description="Return only favorite images"),
    actor_id: Optional[str] = Query(None, description="Filter by specific actor ID")
):
    """
    ดึงประวัติภาพที่สร้างทั้งหมด
    
    Get history of generated images for a character model.
    Images are returned in reverse chronological order (newest first).
    
    Args:
        model_id: Character model ID
        limit: Maximum number of images to return (1-100)
        skip: Number of images to skip (for pagination)
        favorites_only: If True, return only favorite images
        actor_id: If provided, filter by specific actor ID (for character-specific albums)
        
    Returns:
        GetImagesHistoryResponse with list of images
        
    Example:
        GET /api/character/peace-mind-001/generated-images?limit=10&skip=0
        GET /api/character/peace-mind-001/generated-images?favorites_only=true
        GET /api/character/peace-mind-001/generated-images?actor_id=ACT-123
    """
    from core.logging_config import get_logger
    from kamma_appearance_models import GeneratedImageDocument
    
    logger = get_logger(__name__)
    logger.info(f"📂 Getting generated images history for model: {model_id}")
    logger.info(f"   Limit: {limit}, Skip: {skip}, Favorites only: {favorites_only}, Actor ID: {actor_id}")
    
    try:
        # Build query filter
        query_filters = [GeneratedImageDocument.model_id == model_id]
        
        # Add actor_id filter if provided
        if actor_id:
            query_filters.append(GeneratedImageDocument.actor_id == actor_id)
            logger.info(f"   🎭 Filtering by actor: {actor_id}")
        
        # Add favorites filter if requested
        if favorites_only:
            query_filters.append(GeneratedImageDocument.metadata.is_favorite == True)
        
        # Execute query
        docs_query = GeneratedImageDocument.find(*query_filters)
        total_count = await docs_query.count()
        docs = await docs_query.sort("-created_at").skip(skip).limit(limit).to_list()
        
        # Convert to response format
        images = []
        for doc in docs:
            images.append(GeneratedImageHistoryItem(
                image_id=doc.image_id,
                image_base64=doc.metadata.image_base64,
                actor_id=doc.actor_id,  # Include actor_id in response
                
                # NEW: Include thumbnails for optimal performance
                thumbnail_small_base64=doc.metadata.thumbnail_small_base64,
                thumbnail_medium_base64=doc.metadata.thumbnail_medium_base64,
                thumbnail_small_size_kb=doc.metadata.thumbnail_small_size_kb,
                thumbnail_medium_size_kb=doc.metadata.thumbnail_medium_size_kb,
                
                style=doc.metadata.style,
                width=doc.metadata.width,
                height=doc.metadata.height,
                seed=doc.metadata.seed,
                positive_prompt=doc.metadata.positive_prompt,
                generation_time=doc.metadata.generation_time,
                timestamp=doc.created_at,
                is_favorite=doc.metadata.is_favorite,
                notes=doc.metadata.notes
            ))
        
        logger.info(f"✅ Found {len(images)} images (total: {total_count})")
        
        return GetImagesHistoryResponse(
            success=True,
            images=images,
            total_count=total_count,
            model_id=model_id
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting images history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get images history: {str(e)}"
        )


# ============================================================================
# SET AVATAR ENDPOINT
# ============================================================================

class SetAvatarRequest(BaseModel):
    """Request to set an image as profile avatar"""
    image_id: str = Field(..., description="Generated image ID to set as avatar")
    
    class Config:
        json_schema_extra = {
            "example": {
                "image_id": "img_1234567890"
            }
        }


class SetAvatarResponse(BaseModel):
    """Response from setting avatar"""
    success: bool
    message: str
    model_id: str
    avatar_image_id: str
    avatar_url: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Avatar updated successfully",
                "model_id": "peace-mind-001",
                "avatar_image_id": "img_1234567890",
                "avatar_url": "data:image/png;base64,..."
            }
        }


@router.patch("/{model_id}/set-avatar", response_model=SetAvatarResponse)
async def set_character_avatar(
    model_id: str,
    request: SetAvatarRequest
):
    """
    ตั้งค่ารูปโปรไฟล์ตัวละคร
    
    Set a generated image as the character's profile avatar.
    Updates the character model's avatar_image_id field and retrieves the image data.
    
    Args:
        model_id: Character model ID
        request: SetAvatarRequest with image_id
        
    Returns:
        SetAvatarResponse with updated avatar information
        
    Example:
        PATCH /api/character/peace-mind-001/set-avatar
        Body: {"image_id": "img_1234567890"}
    """
    from core.logging_config import get_logger
    from documents import DigitalMindModel
    from kamma_appearance_models import GeneratedImageDocument
    
    logger = get_logger(__name__)
    logger.info(f"🎨 Setting avatar for model: {model_id}")
    logger.info(f"   Image ID: {request.image_id}")
    
    try:
        # 1. Verify image exists and belongs to this model
        image_doc = await GeneratedImageDocument.find_one(
            GeneratedImageDocument.image_id == request.image_id,
            GeneratedImageDocument.model_id == model_id
        )
        
        if not image_doc:
            raise HTTPException(
                status_code=404,
                detail=f"Image {request.image_id} not found for model {model_id}"
            )
        
        # 2. Update character model
        character = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
        
        if not character:
            raise HTTPException(
                status_code=404,
                detail=f"Character model {model_id} not found"
            )
        
        # 3. Set avatar_image_id
        character.avatar_image_id = request.image_id
        character.updated_at = datetime.utcnow()
        await character.save()
        
        # 4. Update Actor Profile if linked (NEW: Sync avatar to Actor)
        from documents_actors import ActorProfile
        
        # ✅ FIX: Prioritize actor_id from image metadata (most accurate)
        # Images generated via /api/actors/{actor_id}/generate-image have correct actor_id
        # Then fallback to model_id if actor_id not available
        actor = None
        
        # Strategy 1: Use actor_id from image metadata (MOST RELIABLE)
        if image_doc.actor_id:
            actor = await ActorProfile.find_one({"actor_id": image_doc.actor_id})
            if actor:
                logger.info(f"🎯 Found actor by image metadata actor_id: {actor.actor_id} ({actor.actor_name})")
        
        # Strategy 2: Fallback to model_id lookup
        if not actor:
            actor = await ActorProfile.find_one({"model_id": model_id})
            if actor:
                logger.info(f"🔄 Found actor by model_id fallback: {actor.actor_id} ({actor.actor_name})")
        
        # Update avatar if actor found
        if actor:
            logger.info(f"📝 BEFORE UPDATE - actor: {actor.actor_id}, avatar exists: {bool(actor.avatar_thumbnail_url)}")
            
            # ✅ NEW: Use SMALL THUMBNAIL for optimal performance
            # This reduces avatar size from ~500KB-1MB to ~15-30KB (90%+ savings!)
            if image_doc.metadata.thumbnail_small_base64:
                avatar_data = image_doc.metadata.thumbnail_small_base64
                logger.info(f"✅ Using optimized 256x256 thumbnail for avatar ({image_doc.metadata.thumbnail_small_size_kb:.1f} KB)")
            else:
                # Fallback: use full image if thumbnail not available (old images)
                avatar_data = image_doc.metadata.image_base64
                logger.warning(f"⚠️ No thumbnail available, using full image ({image_doc.metadata.image_size_kb:.1f} KB)")
                logger.warning(f"   Consider running migration script to add thumbnails to old images")
            
            actor.avatar_thumbnail_url = f"data:image/png;base64,{avatar_data}"
            actor.updated_at = datetime.utcnow()
            await actor.save()
            
            avatar_size_kb = len(avatar_data) / 1024
            logger.info(f"✅ AFTER SAVE - Updated avatar_thumbnail_url for actor: {actor.actor_id} ({actor.actor_name})")
            logger.info(f"📊 Avatar size: {avatar_size_kb:.1f} KB")
            
            if image_doc.metadata.thumbnail_small_base64:
                savings = ((image_doc.metadata.image_size_kb - avatar_size_kb) / image_doc.metadata.image_size_kb) * 100
                logger.info(f"💰 Saved {savings:.1f}% bandwidth using thumbnail!")
        else:
            logger.warning(f"⚠️ No actor found for image {request.image_id} (model_id: {model_id}, image.actor_id: {image_doc.actor_id})")
        
        logger.info(f"✅ Avatar updated successfully")
        logger.info(f"   Model: {model_id}")
        logger.info(f"   Avatar Image ID: {request.image_id}")
        
        return SetAvatarResponse(
            success=True,
            message="Avatar updated successfully",
            model_id=model_id,
            avatar_image_id=request.image_id,
            avatar_url=f"data:image/png;base64,{image_doc.metadata.image_base64[:50]}..."  # Preview only
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error setting avatar: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to set avatar: {str(e)}"
        )


# ============================================================================
# DELETE GENERATED IMAGE
# ============================================================================

class DeleteImageResponse(BaseModel):
    """Response for delete image operation"""
    success: bool
    message: str
    image_id: str
    deleted_count: int = 0


@router.delete(
    "/{model_id}/images/{image_id}",
    response_model=DeleteImageResponse,
    summary="Delete Generated Image",
    description="Delete a specific generated image from the database"
)
async def delete_generated_image(
    model_id: str,
    image_id: str
):
    """
    Delete a generated image from the database
    
    Args:
        model_id: Character model ID
        image_id: Image ID to delete
        
    Returns:
        DeleteImageResponse with success status
        
    Raises:
        HTTPException: If image not found or deletion fails
    """
    from core.logging_config import get_logger
    from kamma_appearance_models import GeneratedImageDocument
    from documents_actors import ActorProfile
    
    logger = get_logger(__name__)
    
    try:
        logger.info(f"🗑️ Deleting image: {image_id} for model: {model_id}")
        
        # Find the image
        image_doc = await GeneratedImageDocument.find_one({
            "image_id": image_id,
            "model_id": model_id
        })
        
        if not image_doc:
            raise HTTPException(
                status_code=404,
                detail=f"Image {image_id} not found for model {model_id}"
            )
        
        # Check if this image is currently set as avatar
        actor = None
        if image_doc.actor_id:
            actor = await ActorProfile.find_one({"actor_id": image_doc.actor_id})
        if not actor:
            actor = await ActorProfile.find_one({"model_id": model_id})
        
        # If this image is the current avatar, clear it and try to set next image as avatar
        is_current_avatar = False
        new_avatar_set = False
        if actor and actor.avatar_thumbnail_url:
            # Check if this image is the avatar (compare base64 data)
            current_avatar_base64 = actor.avatar_thumbnail_url.replace("data:image/png;base64,", "")
            
            # ✅ FIX: Compare with BOTH thumbnail and full image (for backwards compatibility)
            is_avatar_match = (
                (image_doc.metadata.thumbnail_small_base64 and image_doc.metadata.thumbnail_small_base64 == current_avatar_base64) or
                (image_doc.metadata.image_base64 == current_avatar_base64)
            )
            
            if is_avatar_match:
                is_current_avatar = True
                logger.warning(f"⚠️ Image {image_id} is currently set as avatar for actor {actor.actor_id}")
                
                # Clear current avatar
                actor.avatar_thumbnail_url = None
                actor.updated_at = datetime.utcnow()
                await actor.save()
                logger.info(f"🧹 Cleared avatar_thumbnail_url from actor {actor.actor_id}")
                
                # ✅ FIX: Try to auto-set next image as avatar (using thumbnail!)
                from kamma_appearance_models import GeneratedImageDocument
                
                # Find the next most recent image for this actor (excluding the one being deleted)
                next_image = await GeneratedImageDocument.find_one(
                    {
                        "model_id": model_id,
                        "image_id": {"$ne": image_id},  # Exclude current image
                        "$or": [
                            {"actor_id": actor.actor_id},
                            {"actor_id": {"$exists": False}}  # Fallback to images without actor_id
                        ]
                    },
                    sort=[("metadata.timestamp", -1)]  # Get most recent
                )
                
                if next_image and next_image.metadata:
                    # ✅ NEW: Use SMALL THUMBNAIL for optimal performance
                    if next_image.metadata.thumbnail_small_base64:
                        avatar_data = next_image.metadata.thumbnail_small_base64
                        avatar_size_kb = next_image.metadata.thumbnail_small_size_kb or 0
                        logger.info(f"✅ Using optimized 256x256 thumbnail for replacement avatar ({avatar_size_kb:.1f} KB)")
                    else:
                        # Fallback: use full image if thumbnail not available
                        avatar_data = next_image.metadata.image_base64
                        avatar_size_kb = next_image.metadata.image_size_kb
                        logger.warning(f"⚠️ No thumbnail available for next image, using full ({avatar_size_kb:.1f} KB)")
                    
                    # Set next image as new avatar
                    actor.avatar_thumbnail_url = f"data:image/png;base64,{avatar_data}"
                    actor.updated_at = datetime.utcnow()
                    await actor.save()
                    new_avatar_set = True
                    logger.info(f"🎨 Auto-set next image as avatar: {next_image.image_id}")
                else:
                    logger.info(f"📭 No other images available to set as avatar")
        
        # Delete the image
        await image_doc.delete()
        
        logger.info(f"✅ Image deleted successfully: {image_id}")
        if is_current_avatar:
            if new_avatar_set:
                logger.info(f"   Note: Avatar replaced with next image")
            else:
                logger.info(f"   Note: Avatar cleared (no other images available)")
        
        message = "Image deleted successfully"
        if is_current_avatar:
            if new_avatar_set:
                message += " (avatar replaced with next image)"
            else:
                message += " (avatar cleared)"
        
        return DeleteImageResponse(
            success=True,
            message=message,
            image_id=image_id,
            deleted_count=1
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting image: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete image: {str(e)}"
        )


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "router",
    "AvatarStateResponse",
    "GenerateAnimationRequest",
    "GenerateAnimationResponse",
    "ProbabilityAnalysisResponse"
]
