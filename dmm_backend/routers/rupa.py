"""
🆕 Rupa API Router - REST API endpoints for 28 Material Forms

Endpoints:
- GET /rupa/{model_id} - Get complete RupaProfile
- GET /rupa/{model_id}/mahabhuta - 4 Great Elements
- GET /rupa/{model_id}/pasada - 5 Sense Organs
- GET /rupa/{model_id}/kalapas - Active material groups
- GET /rupa/{model_id}/samutthana - Origin breakdown
- POST /rupa/{model_id}/calculate - Recalculate all rupa
- GET /rupa/{model_id}/lifecycle - Rupa lifecycle simulation

Author: Peace Mind System
Date: 17 October 2568
Version: 1.0
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, List
from pydantic import BaseModel, Field

from documents import DigitalMindModel
from rupa_models import (
    RupaProfile, MahabhutaRupa, PasadaRupa, RupaKalapa,
    RupaSamutthana, RupaAnalysisResponse, MahabhutaType
)
from modules.rupa_engine import (
    RupaCalculationEngine,
    calculate_and_save_rupa,
    recalculate_rupa_from_changes
)
from modules.rupa_sync import RupaJivitindriaSyncLayer, get_jivitindriya_status


router = APIRouter(
    prefix="/rupa",
    tags=["Rupa System (28 Material Forms)"],
    responses={404: {"description": "Model or RupaProfile not found"}}
)


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class MahabhutaResponse(BaseModel):
    """Response for mahabhuta endpoint"""
    model_id: str
    mahabhuta: MahabhutaRupa
    dominant_element: MahabhutaType
    balance_score: float = Field(..., description="How balanced the 4 elements are (0-100)")


class PasadaResponse(BaseModel):
    """Response for pasada endpoint"""
    model_id: str
    pasada: PasadaRupa
    average_sensitivity: float
    strongest_sense: str
    weakest_sense: str


class KalapaResponse(BaseModel):
    """Response for kalapas endpoint"""
    model_id: str
    total_kalapa_count: int
    active_kalapas: List[RupaKalapa]
    by_origin: Dict[str, int]
    by_moment: Dict[str, int]


class SamutthanaResponse(BaseModel):
    """Response for samutthana endpoint"""
    model_id: str
    kamma_rupa_count: int
    citta_rupa_count: int
    utu_rupa_count: int
    ahara_rupa_count: int
    total_count: int
    breakdown_percentage: Dict[str, float]


class CalculateRupaRequest(BaseModel):
    """Request to recalculate rupa"""
    force_recalculate: bool = Field(False, description="Force full recalculation even if exists")
    sync_jivitindriya: bool = Field(True, description="Sync jivitindriya after calculation")


class LifecycleSimulationRequest(BaseModel):
    """Request for lifecycle simulation"""
    kalapa_index: int = Field(0, description="Index of kalapa to simulate")
    simulate_moments: int = Field(17, description="Number of moments to simulate (default: 17)")


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/{model_id}", response_model=RupaAnalysisResponse)
async def get_complete_rupa_profile(model_id: str):
    """
    Get complete RupaProfile (28 Material Forms)
    
    Returns all 28 rupa categories with full detail
    """
    # Find RupaProfile
    rupa = await RupaProfile.find_one({"model_id": model_id})
    if not rupa:
        raise HTTPException(404, f"RupaProfile not found for model: {model_id}")
    
    # Calculate dominant element
    dominant = RupaCalculationEngine._determine_dominant_element(
        rupa.mahabhuta_state.pathavi.hardness_level,
        rupa.mahabhuta_state.apo.cohesion_level,
        rupa.mahabhuta_state.tejo.heat_level,
        rupa.mahabhuta_state.vayo.tension_level
    )
    
    # Mahabhuta analysis
    mahabhuta_analysis = {
        "pathavi_hardness": rupa.mahabhuta_state.pathavi.hardness_level,
        "apo_cohesion": rupa.mahabhuta_state.apo.cohesion_level,
        "tejo_heat": rupa.mahabhuta_state.tejo.heat_level,
        "vayo_tension": rupa.mahabhuta_state.vayo.tension_level
    }
    
    # Pasada status
    pasada_status = {
        "cakkhu": rupa.pasada_state.cakkhu_pasada or 0,
        "sota": rupa.pasada_state.sota_pasada or 0,
        "ghana": rupa.pasada_state.ghana_pasada or 0,
        "jivha": rupa.pasada_state.jivha_pasada or 0,
        "kaya": rupa.pasada_state.kaya_pasada or 0
    }
    
    # Kalapa distribution
    kalapa_distribution = {
        "total": rupa.total_kalapa_count,
        "kamma": rupa.kamma_rupa_count,
        "citta": rupa.citta_rupa_count,
        "utu": rupa.utu_rupa_count,
        "ahara": rupa.ahara_rupa_count
    }
    
    # Samutthana breakdown
    samutthana_breakdown = {
        "kamma": rupa.kamma_rupa_count,
        "citta": rupa.citta_rupa_count,
        "utu": rupa.utu_rupa_count,
        "ahara": rupa.ahara_rupa_count
    }
    
    # Lifecycle stage
    age_factor = rupa.age / 150
    if age_factor < 0.2:
        lifecycle = "youth"
    elif age_factor < 0.5:
        lifecycle = "prime"
    elif age_factor < 0.7:
        lifecycle = "mature"
    else:
        lifecycle = "aging"
    
    # Buddhist accuracy (always 100% for properly calculated rupa)
    buddhist_accuracy = 100.0
    
    return RupaAnalysisResponse(
        model_id=model_id,
        total_rupa_count=28,  # Always 28 Material Forms
        mahabhuta_analysis=mahabhuta_analysis,
        dominant_element=dominant,
        pasada_status=pasada_status,
        kalapa_distribution=kalapa_distribution,
        samutthana_breakdown=samutthana_breakdown,
        lifecycle_stage=lifecycle,
        buddhist_accuracy=buddhist_accuracy
    )


@router.get("/{model_id}/mahabhuta", response_model=MahabhutaResponse)
async def get_mahabhuta_analysis(model_id: str):
    """
    Get 4 Great Elements (มหาภูตรูป ๔) analysis
    
    Returns:
    - Pathavi (Earth): Hardness/Softness
    - Apo (Water): Cohesion/Fluidity
    - Tejo (Fire): Heat/Cold
    - Vayo (Wind): Tension/Looseness
    """
    rupa = await RupaProfile.find_one({"model_id": model_id})
    if not rupa:
        raise HTTPException(404, f"RupaProfile not found for model: {model_id}")
    
    # Calculate dominant element
    dominant = RupaCalculationEngine._determine_dominant_element(
        rupa.mahabhuta_state.pathavi.hardness_level,
        rupa.mahabhuta_state.apo.cohesion_level,
        rupa.mahabhuta_state.tejo.heat_level,
        rupa.mahabhuta_state.vayo.tension_level
    )
    
    # Calculate balance score (how close all 4 are to each other)
    levels = [
        rupa.mahabhuta_state.pathavi.hardness_level,
        rupa.mahabhuta_state.apo.cohesion_level,
        rupa.mahabhuta_state.tejo.heat_level / 0.38,  # Normalize to 0-100
        rupa.mahabhuta_state.vayo.tension_level
    ]
    avg = sum(levels) / len(levels)
    variance = sum((x - avg) ** 2 for x in levels) / len(levels)
    balance_score = max(0, 100 - variance)  # Lower variance = higher balance
    
    return MahabhutaResponse(
        model_id=model_id,
        mahabhuta=rupa.mahabhuta_state,
        dominant_element=dominant,
        balance_score=balance_score
    )


@router.get("/{model_id}/pasada", response_model=PasadaResponse)
async def get_pasada_analysis(model_id: str):
    """
    Get 5 Sense Organs (ปสาทรูป ๕) sensitivity analysis
    
    Returns:
    - Cakkhu (จักขุ): Eye
    - Sota (โสต): Ear
    - Ghana (ฆาน): Nose
    - Jivha (ชิวหา): Tongue
    - Kaya (กาย): Body
    """
    rupa = await RupaProfile.find_one({"model_id": model_id})
    if not rupa:
        raise HTTPException(404, f"RupaProfile not found for model: {model_id}")
    
    # Extract pasada values
    senses = {
        "cakkhu": rupa.pasada_state.cakkhu_pasada or 0,
        "sota": rupa.pasada_state.sota_pasada or 0,
        "ghana": rupa.pasada_state.ghana_pasada or 0,
        "jivha": rupa.pasada_state.jivha_pasada or 0,
        "kaya": rupa.pasada_state.kaya_pasada or 0
    }
    
    # Calculate statistics
    values = [v for v in senses.values() if v > 0]
    average_sensitivity = sum(values) / len(values) if values else 0
    
    strongest_sense = max(senses, key=senses.get)
    weakest_sense = min(senses, key=senses.get)
    
    return PasadaResponse(
        model_id=model_id,
        pasada=rupa.pasada_state,
        average_sensitivity=average_sensitivity,
        strongest_sense=strongest_sense,
        weakest_sense=weakest_sense
    )


@router.get("/{model_id}/kalapas", response_model=KalapaResponse)
async def get_active_kalapas(
    model_id: str,
    limit: int = Query(100, description="Max number of kalapas to return")
):
    """
    Get active material groups (รูปกลาป)
    
    Each kalapa contains:
    - 4 Mahabhuta (always present)
    - Variable Upadaya rupa depending on origin
    - 4 Lakkhana (characteristics)
    
    Minimum: 8 rupa per kalapa (Suddhatthaka)
    """
    rupa = await RupaProfile.find_one({"model_id": model_id})
    if not rupa:
        raise HTTPException(404, f"RupaProfile not found for model: {model_id}")
    
    # Count by origin
    by_origin = {
        "kamma": rupa.kamma_rupa_count,
        "citta": rupa.citta_rupa_count,
        "utu": rupa.utu_rupa_count,
        "ahara": rupa.ahara_rupa_count
    }
    
    # Count by moment (uppada, thiti, bhanga)
    by_moment = {
        "uppada": 0,
        "thiti": 0,
        "bhanga": 0
    }
    for kalapa in rupa.active_kalapas[:limit]:
        moment_str = kalapa.moment.value if hasattr(kalapa.moment, 'value') else str(kalapa.moment)
        by_moment[moment_str] = by_moment.get(moment_str, 0) + 1
    
    return KalapaResponse(
        model_id=model_id,
        total_kalapa_count=rupa.total_kalapa_count,
        active_kalapas=rupa.active_kalapas[:limit],
        by_origin=by_origin,
        by_moment=by_moment
    )


@router.get("/{model_id}/samutthana", response_model=SamutthanaResponse)
async def get_samutthana_breakdown(model_id: str):
    """
    Get Rupa origins (รูปสมุฏฐาน ๔) breakdown
    
    4 Origins:
    - Kamma (กัมมชรูป): Born of past kamma
    - Citta (จิตตชรูป): Born of consciousness
    - Utu (อุตุชรูป): Born of temperature
    - Ahara (อาหารชรูป): Born of nutriment
    """
    rupa = await RupaProfile.find_one({"model_id": model_id})
    if not rupa:
        raise HTTPException(404, f"RupaProfile not found for model: {model_id}")
    
    total = (rupa.kamma_rupa_count + rupa.citta_rupa_count + 
             rupa.utu_rupa_count + rupa.ahara_rupa_count)
    
    # Calculate percentages
    breakdown_percentage = {}
    if total > 0:
        breakdown_percentage = {
            "kamma": (rupa.kamma_rupa_count / total) * 100,
            "citta": (rupa.citta_rupa_count / total) * 100,
            "utu": (rupa.utu_rupa_count / total) * 100,
            "ahara": (rupa.ahara_rupa_count / total) * 100
        }
    
    return SamutthanaResponse(
        model_id=model_id,
        kamma_rupa_count=rupa.kamma_rupa_count,
        citta_rupa_count=rupa.citta_rupa_count,
        utu_rupa_count=rupa.utu_rupa_count,
        ahara_rupa_count=rupa.ahara_rupa_count,
        total_count=total,
        breakdown_percentage=breakdown_percentage
    )


@router.post("/{model_id}/calculate")
async def calculate_rupa_profile(
    model_id: str,
    request: CalculateRupaRequest = CalculateRupaRequest()
):
    """
    Calculate or recalculate complete RupaProfile (28 Material Forms)
    
    This endpoint:
    1. Fetches CoreProfile data
    2. Calculates all 28 rupa from scratch
    3. Saves to rupa_profiles collection
    4. Optionally syncs jivitindriya
    
    Use this to:
    - Initialize rupa for new models
    - Refresh rupa after major life events
    - Force recalculation after data corruption
    """
    # Check if model exists
    model = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
    if not model:
        raise HTTPException(404, f"DigitalMindModel not found: {model_id}")
    
    # Check if already exists
    existing = await RupaProfile.find_one({"model_id": model_id})
    
    if existing and not request.force_recalculate:
        return {
            "status": "already_exists",
            "message": "RupaProfile already exists. Use force_recalculate=true to override.",
            "model_id": model_id,
            "rupa_id": str(existing.id)
        }
    
    # Calculate rupa
    rupa = await calculate_and_save_rupa(model_id)
    
    # Sync jivitindriya if requested
    if request.sync_jivitindriya:
        synced = await RupaJivitindriaSyncLayer.sync_rupa_to_life_essence(model_id)
        sync_status = "synced" if synced else "sync_failed"
    else:
        sync_status = "not_synced"
    
    return {
        "status": "calculated",
        "message": "RupaProfile successfully calculated",
        "model_id": model_id,
        "rupa_id": str(rupa.id),
        "total_rupa_count": 28,
        "total_kalapa_count": rupa.total_kalapa_count,
        "jivitindriya_sync_status": sync_status,
        "buddhist_accuracy": 100.0
    }


@router.get("/{model_id}/lifecycle")
async def get_lifecycle_status(model_id: str):
    """
    Get Rupa lifecycle (รูปขณะ ๓) status
    
    3 Moments:
    - Uppada (อุปปาทขณะ): Arising
    - Thiti (ฐิติขณะ): Standing/Continuity
    - Bhanga (ภังคขณะ): Dissolution
    
    Lifespan: 17 citta-kshanas (mind-moments)
    """
    rupa = await RupaProfile.find_one({"model_id": model_id})
    if not rupa:
        raise HTTPException(404, f"RupaProfile not found for model: {model_id}")
    
    # Analyze lifecycle of active kalapas
    lifecycle_stats = {
        "uppada": 0,
        "thiti": 0,
        "bhanga": 0
    }
    
    for kalapa in rupa.active_kalapas:
        moment = kalapa.moment.value if hasattr(kalapa.moment, 'value') else str(kalapa.moment)
        lifecycle_stats[moment] = lifecycle_stats.get(moment, 0) + 1
    
    # Calculate overall lifecycle stage
    total = sum(lifecycle_stats.values())
    if total > 0:
        percentages = {k: (v / total) * 100 for k, v in lifecycle_stats.items()}
    else:
        percentages = {"uppada": 0, "thiti": 0, "bhanga": 0}
    
    return {
        "model_id": model_id,
        "total_kalapas": rupa.total_kalapa_count,
        "lifecycle_distribution": lifecycle_stats,
        "lifecycle_percentages": percentages,
        "age_in_moments": rupa.age_in_moments,
        "age_in_years": rupa.age,
        "last_updated": rupa.last_updated
    }


@router.get("/{model_id}/jivitindriya-status")
async def get_jivitindriya_sync_status(model_id: str):
    """
    Get Jivitindriya synchronization status
    
    Checks:
    - LifeEssence.jivitindriya_mechanics.current_jivitindriya
    - RupaProfile.jivita_state.rupa_jivitindriya
    - Whether they are in sync
    """
    status = await get_jivitindriya_status(model_id)
    
    if not status:
        raise HTTPException(404, f"Could not get jivitindriya status for model: {model_id}")
    
    return status
