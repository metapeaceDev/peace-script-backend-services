"""
Core Profile Router - Advanced Buddhist Psychology API

Provides comprehensive endpoints for managing CoreProfile:
- CharacterStatus (spiritual development)
- LifeEssence (life force & blueprint)
- PsychologicalMatrix (mental structure)
- SpiritualAssets (kamma & virtues)
"""

from datetime import datetime
from typing import Any, Dict, Optional
import logging

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

from documents import DigitalMindModel
# Robust import of CoreProfile models to support both package and local execution contexts
try:
    from dmm_backend.core_profile_models import NamaRupaProfile, NamaProfile, RupaProfileSimplified  # type: ignore
except Exception:  # pragma: no cover - fallback for local module execution
    from core_profile_models import NamaRupaProfile, NamaProfile, RupaProfileSimplified

router = APIRouter(prefix="/api/core-profile", tags=["Core Profile"])


# ============================================================
# Request/Response Models
# ============================================================

class CoreProfileResponse(BaseModel):
    """Complete CoreProfile response"""
    model_id: str
    CoreProfile: Dict[str, Any]
    spiritual_score: float
    is_noble: bool
    last_updated: datetime


class CharacterStatusUpdate(BaseModel):
    """Update character status"""
    type: Optional[str] = None
    stage: Optional[str] = None
    path_stage: Optional[str] = None


class LifeEssenceUpdate(BaseModel):
    """Update life essence"""
    age_in_years: Optional[int] = Field(None, ge=0, le=150, description="Current age")
    current_jivitindriya: Optional[float] = Field(None, ge=0, le=100)
    depletion_rate_per_day: Optional[float] = Field(None, ge=0, le=1)
    natural_regeneration_rate: Optional[float] = Field(None, ge=0, le=1)
    health_baseline: Optional[float] = Field(
        None, ge=0, le=100, description="Baseline physical health (0-100)"
    )


class AnusayaUpdate(BaseModel):
    """Update anusaya kilesa levels"""
    kama_raga: Optional[float] = Field(None, ge=0, le=10)
    patigha: Optional[float] = Field(None, ge=0, le=10)
    mana: Optional[float] = Field(None, ge=0, le=10)
    ditthi: Optional[float] = Field(None, ge=0, le=10)
    vicikiccha: Optional[float] = Field(None, ge=0, le=10)
    bhava_raga: Optional[float] = Field(None, ge=0, le=10)
    avijja: Optional[float] = Field(None, ge=0, le=10)


class ParamiUpdate(BaseModel):
    """Update specific pāramī"""
    parami_name: str = Field(..., description="dana, sila, nekkhamma, etc.")
    level: Optional[int] = Field(None, ge=0, le=10)
    exp: Optional[int] = Field(None, ge=0)


class FetterBreakRequest(BaseModel):
    """Request to break a fetter"""
    fetter_name: str = Field(
        ...,
        description="Fetter to break: sakkayaditthi, vicikiccha, silabbataparamasa, kamaraga, patigha, ruparaga, aruparaga, mana, uddhacca, avijja"
    )


# ============================================================
# Core Profile Endpoints
# ============================================================

@router.get("/{model_id}/nama-rupa", response_model=NamaRupaProfile)
async def get_nama_rupa(
    model_id: str,
    detailed: bool = Query(False, description="Return detailed 28 Material Forms if True, simplified 4-field if False")
):
    """
    Get Nama/Rupa (นาม/รูป) computed profile for a model.
    - Nama derives from mental components (temperament, anusaya, sati/panna)
    - Rupa derives from physical/life components (age, health baseline, jivitindriya)
    
    Query Parameters:
    - detailed=false (default): Returns simplified RupaProfile (4 fields) - BACKWARD COMPATIBLE
    - detailed=true: Returns reference to complete RupaProfile (28 Material Forms)
    """
    model = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")

    profile = model.get_core_profile()

    # Helper accessors to support both snake_case (core_profile_models) and PascalCase (legacy) fields
    def _attr(obj, *names, default=None):
        for n in names:
            if hasattr(obj, n):
                return getattr(obj, n)
        return default

    # Psychological side (Nama)
    psych = _attr(profile, "psychological_matrix", "PsychologicalMatrix")
    dom_temp = None
    anusaya = {}
    if psych:
        dom = _attr(psych, "dominant_temperament", "DominantTemperament")
        if dom:
            dom_temp = _attr(dom, "primary_carita", "primary_carita")
        lt = _attr(psych, "latent_tendencies", "LatentTendencies")
        if lt:
            anusaya = _attr(lt, "anusaya_kilesa", "anusaya_kilesa", default={}) or {}

    avg_kilesa = 0.0
    if isinstance(anusaya, dict) and anusaya:
        try:
            avg_kilesa = sum(v.get("level", 0.0) for v in anusaya.values()) / max(len(anusaya), 1)
        except Exception:
            avg_kilesa = 0.0

    assets = _attr(profile, "spiritual_assets", "SpiritualAssets")
    virtue = _attr(assets, "virtue_engine", "VirtueEngine") if assets else None
    sati = _attr(virtue, "sati_mastery", "Sati_mastery") if virtue else None
    panna = _attr(virtue, "panna_mastery", "Panna_mastery") if virtue else None
    sati_level = _attr(sati, "level", "level", default=0) if sati else 0
    panna_level = _attr(panna, "level", "level", default=0) if panna else 0

    nama = {
        "dominant_temperament": dom_temp or "",
        "anusaya_levels_avg": round(avg_kilesa, 2),
        "sati_level": int(sati_level or 0),
        "panna_level": int(panna_level or 0),
        "notes": "Derived from PsychologicalMatrix and VirtueEngine"
    }

    # Physical side (Rupa) - always compute simplified version
    le = _attr(profile, "life_essence", "LifeEssence")
    age = _attr(le, "age_in_years", "age_in_years", default=0) if le else 0
    jiv = _attr(le, "jivitindriya_mechanics", "jivitindriya_mechanics") if le else None
    current_life_force = _attr(jiv, "current_jivitindriya", "current_jivitindriya", default=0.0) if jiv else 0.0
    lbv = _attr(le, "life_blueprint_vipaka", "LifeBlueprint_Vipaka") if le else None
    init_cond = _attr(lbv, "initial_conditions", "initial_conditions") if lbv else None
    health_baseline = _attr(init_cond, "health_baseline", "health_baseline", default=0.0) if init_cond else 0.0
    lifespan_potential = _attr(lbv, "lifespan_potential", "lifespan_potential", default=0) if lbv else 0
    lifespan_remaining = max(int((lifespan_potential or 0) - (age or 0)), 0)

    rupa_simplified = {
        "age": int(age or 0),
        "health_baseline": float(health_baseline or 0.0),
        "current_life_force": round(float(current_life_force or 0.0), 2),
        "lifespan_remaining": lifespan_remaining,
        "notes": "Derived from LifeEssence (Vipaka blueprint and Jīvitindriya)"
    }

    # Check if detailed RupaProfile exists
    rupa_ref = None
    migration_status = "legacy"
    detailed_rupa_available = False
    
    if detailed:
        # Try to fetch detailed RupaProfile
        try:
            from rupa_models import RupaProfile
            detailed_rupa = await RupaProfile.find_one(RupaProfile.model_id == model_id)
            if detailed_rupa:
                rupa_ref = str(detailed_rupa.id)
                migration_status = "migrated"
                detailed_rupa_available = True
        except ImportError:
            pass  # RupaProfile not available
        except Exception as e:
            logger.error(f"Error fetching detailed RupaProfile for {model_id}: {e}")
    
    summary = (
        "นาม (Nama): อุปนิสัยเด่น = "
        f"{nama['dominant_temperament']}, อนุสัยเฉลี่ย = {nama['anusaya_levels_avg']}; "
        "รูป (Rupa): อายุ = "
        f"{rupa_simplified['age']}, พลังชีวิต = {rupa_simplified['current_life_force']:.1f}%, สุขภาพพื้นฐาน = {rupa_simplified['health_baseline']:.1f}"
    )
    
    if detailed_rupa_available:
        summary += f" [รูป ๒๘ available via rupa_ref]"

    return NamaRupaProfile(
        nama=NamaProfile(**nama),
        rupa=RupaProfileSimplified(**rupa_simplified),
        rupa_ref=rupa_ref,
        migration_status=migration_status,
        detailed_rupa_available=detailed_rupa_available,
        summary=summary
    )

@router.get("/{model_id}", response_model=CoreProfileResponse)
async def get_core_profile(model_id: str):
    """
    Get complete CoreProfile for a model
    
    Returns:
    - Full CoreProfile structure
    - Spiritual development score
    - Noble status
    """
    model = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    profile = model.get_core_profile()
    
    return CoreProfileResponse(
        model_id=model.model_id,
        CoreProfile=profile.model_dump(),
        spiritual_score=profile.get_overall_spiritual_score(),
        is_noble=profile.is_noble(),
        last_updated=profile.last_updated
    )


@router.get("/{model_id}/character-status")
async def get_character_status(model_id: str):
    """Get CharacterStatus component"""
    model = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    profile = model.get_core_profile()
    return {
        "model_id": model_id,
        "CharacterStatus": profile.character_status.model_dump(),
        "is_noble": profile.is_noble(),
        "fetters_broken_count": len(profile.character_status.fetters_broken),
        "fetters_remaining_count": len(profile.character_status.fetters_remaining)
    }


@router.patch("/{model_id}/character-status")
async def update_character_status(model_id: str, update: CharacterStatusUpdate):
    """Update CharacterStatus"""
    model = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    profile = model.get_core_profile()
    
    if update.type:
        profile.character_status.type = update.type
    if update.stage:
        profile.character_status.stage = update.stage
    if update.path_stage:
        profile.character_status.path_stage = update.path_stage
    
    model.update_core_profile({})  # Sync changes
    await model.save()
    
    return {
        "success": True,
        "model_id": model_id,
        "updated_status": profile.character_status.model_dump()
    }


@router.get("/{model_id}/life-essence")
async def get_life_essence(model_id: str):
    """Get LifeEssence component"""
    model = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    profile = model.get_core_profile()
    life_essence = profile.life_essence
    
    return {
        "model_id": model_id,
        "LifeEssence": life_essence.model_dump(),
        "age": life_essence.age_in_years,
        "life_percentage": life_essence.jivitindriya_mechanics.current_jivitindriya,
        "lifespan_potential": life_essence.life_blueprint_vipaka.lifespan_potential,
        "lifespan_remaining": life_essence.life_blueprint_vipaka.lifespan_potential - life_essence.age_in_years,
        "birth_realm": life_essence.life_blueprint_vipaka.birth_bhumi
    }


@router.patch("/{model_id}/life-essence")
async def update_life_essence(model_id: str, update: LifeEssenceUpdate):
    """
    Update LifeEssence
    
    Can update:
    - age_in_years: Current age (affects lifespan remaining)
    - current_jivitindriya: Life force percentage
    - depletion_rate_per_day: Rate of life force loss
    - natural_regeneration_rate: Rate of life force recovery
    """
    model = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    profile = model.get_core_profile()
    # Support both snake_case and PascalCase CoreProfile internals
    life_essence = getattr(profile, "life_essence", None) or getattr(profile, "LifeEssence", None)
    
    # Update age if provided
    if update.age_in_years is not None and life_essence is not None:
        try:
            life_essence.age_in_years = update.age_in_years
        except Exception:
            pass
    
    # Update jivitindriya if provided
    if update.current_jivitindriya is not None and life_essence is not None:
        try:
            life_essence.jivitindriya_mechanics.current_jivitindriya = update.current_jivitindriya
        except Exception:
            pass
    
    # Update depletion rate if provided
    if update.depletion_rate_per_day is not None and life_essence is not None:
        try:
            life_essence.jivitindriya_mechanics.depletion_rate_per_day = update.depletion_rate_per_day
        except Exception:
            pass
    
    # Update regeneration rate if provided
    if update.natural_regeneration_rate is not None and life_essence is not None:
        try:
            life_essence.jivitindriya_mechanics.natural_regeneration_rate = update.natural_regeneration_rate
        except Exception:
            pass

    # Update health baseline if provided (under LifeBlueprintVipaka.initial_conditions)
    if update.health_baseline is not None and life_essence is not None:
        # Update both snake_case and legacy path if available
        try:
            lbv = getattr(life_essence, "life_blueprint_vipaka", None) or getattr(life_essence, "LifeBlueprint_Vipaka", None)
            init_cond = getattr(lbv, "initial_conditions", None) if lbv else None
            if init_cond is not None:
                setattr(init_cond, "health_baseline", update.health_baseline)
        except Exception:
            pass
    
    model.update_core_profile({})
    await model.save()
    
    result = {
        "success": True,
        "model_id": model_id
    }
    
    if life_essence:
        result["updated_life_essence"] = life_essence.model_dump()
        result["age"] = life_essence.age_in_years
        result["lifespan_remaining"] = life_essence.life_blueprint_vipaka.lifespan_potential - life_essence.age_in_years
    
    return result


@router.post("/{model_id}/advance-age")
async def advance_age(model_id: str, years: int = 1):
    """
    Advance character age with automatic life force calculations
    
    Effects:
    - Increases age by specified years
    - Depletes life force based on age factor
    - Returns warnings if approaching end of life
    - Useful for time-skip simulations
    """
    model = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    profile = model.get_core_profile()
    
    # Advance age and get summary
    result = profile.advance_age(years)
    
    model.update_core_profile({})
    await model.save()
    
    return {
        "success": True,
        "model_id": model_id,
        "years_advanced": years,
        "summary": result,
        "current_age": profile.life_essence.age_in_years,
        "current_life_force": profile.life_essence.jivitindriya_mechanics.current_jivitindriya
    }


@router.get("/{model_id}/psychological-matrix")
async def get_psychological_matrix(model_id: str):
    """Get PsychologicalMatrix component"""
    model = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    profile = model.get_core_profile()
    matrix = profile.psychological_matrix
    
    # Calculate average kilesa level
    anusaya = matrix.latent_tendencies.anusaya_kilesa
    avg_kilesa = sum(v["level"] for v in anusaya.values()) / len(anusaya)
    
    return {
        "model_id": model_id,
        "PsychologicalMatrix": matrix.model_dump(),
        "average_kilesa_level": round(avg_kilesa, 2),
        "dominant_temperament": matrix.dominant_temperament.primary_carita,
        "mental_suffering_threshold": matrix.vedana_tolerance_profile.mental_suffering_threshold.total_threshold
    }


@router.patch("/{model_id}/anusaya")
async def update_anusaya(model_id: str, update: AnusayaUpdate):
    """
    Update Anusaya kilesa levels
    
    Updates one or more of the 7 latent tendencies:
    - kama_raga: Sensual desire
    - patigha: Aversion
    - mana: Conceit
    - ditthi: Wrong view
    - vicikiccha: Doubt
    - bhava_raga: Craving for existence
    - avijja: Ignorance
    """
    model = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    profile = model.get_core_profile()
    anusaya = profile.psychological_matrix.latent_tendencies.anusaya_kilesa
    
    # Update provided kilesa levels
    update_dict = update.model_dump(exclude_none=True)
    for kilesa_name, level in update_dict.items():
        if kilesa_name in anusaya:
            anusaya[kilesa_name]["level"] = level
    
    model.update_core_profile({})
    await model.save()
    
    return {
        "success": True,
        "model_id": model_id,
        "updated_anusaya": anusaya
    }

# Convenience alias under nama-rupa namespace (same body as /anusaya)
@router.patch("/{model_id}/nama-rupa/anusaya")
async def update_anusaya_namarupa(model_id: str, update: AnusayaUpdate):
    return await update_anusaya(model_id, update)

# Convenience alias to update health baseline under nama-rupa namespace
@router.patch("/{model_id}/nama-rupa/rupa")
async def update_rupa_health_baseline(model_id: str, payload: Dict[str, Any]):
    """
    Update Rupa related fields (currently supports health_baseline only).
    Payload: { "health_baseline": <0-100>, "current_jivitindriya"?: <0-100>, "age_in_years"?: <int> }
    """
    update = LifeEssenceUpdate(**{k: v for k, v in payload.items() if k in {"health_baseline", "current_jivitindriya", "age_in_years"}})
    return await update_life_essence(model_id, update)


@router.get("/{model_id}/spiritual-assets")
async def get_spiritual_assets(model_id: str):
    """Get SpiritualAssets component"""
    model = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    profile = model.get_core_profile()
    assets = profile.spiritual_assets
    
    # Calculate total kamma balance
    kamma_balance = (
        assets.kamma_ledger.kusala_stock_points - 
        assets.kamma_ledger.akusala_stock_points
    )
    
    # Calculate average pāramī level
    parami_dict = assets.virtue_engine.parami_portfolio.perfections
    avg_parami = sum(p.level for p in parami_dict.values()) / len(parami_dict)
    
    return {
        "model_id": model_id,
        "SpiritualAssets": assets.model_dump(),
        "kamma_balance": kamma_balance,
        "average_parami_level": round(avg_parami, 2),
        "sati_level": assets.virtue_engine.sati_mastery.level,
        "panna_level": assets.virtue_engine.panna_mastery.level
    }


@router.patch("/{model_id}/parami")
async def update_parami(model_id: str, update: ParamiUpdate):
    """
    Update specific Pāramī (perfection)
    
    10 Pāramī:
    - dana (generosity)
    - sila (virtue)
    - nekkhamma (renunciation)
    - panna (wisdom)
    - viriya (energy)
    - khanti (patience)
    - sacca (truthfulness)
    - adhitthana (determination)
    - metta (loving-kindness)
    - upekkha (equanimity)
    """
    model = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    profile = model.get_core_profile()
    parami_dict = profile.spiritual_assets.virtue_engine.parami_portfolio.perfections
    
    if update.parami_name not in parami_dict:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid pāramī name. Must be one of: {', '.join(parami_dict.keys())}"
        )
    
    parami = parami_dict[update.parami_name]
    
    if update.level is not None:
        parami.level = update.level
    if update.exp is not None:
        parami.exp = update.exp
    
    # Update mastery percentage
    parami.mastery_percentage = min((parami.level / 10) * 100, 100)
    
    model.update_core_profile({})
    await model.save()
    
    return {
        "success": True,
        "model_id": model_id,
        "parami_name": update.parami_name,
        "updated_parami": parami.model_dump()
    }


@router.post("/{model_id}/break-fetter")
async def break_fetter(model_id: str, request: FetterBreakRequest):
    """
    Break a samyojana (fetter)
    
    10 Fetters:
    1-3 (Sotāpanna): sakkayaditthi, vicikiccha, silabbataparamasa
    4-5 (Sakadāgāmī/Anāgāmī): kamaraga, patigha
    6-10 (Arahant): ruparaga, aruparaga, mana, uddhacca, avijja
    
    Breaking fetters automatically updates CharacterStatus
    """
    model = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    success = await model.break_fetter(request.fetter_name)
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail=f"Fetter '{request.fetter_name}' already broken or invalid"
        )
    
    profile = model.get_core_profile()
    
    return {
        "success": True,
        "model_id": model_id,
        "broken_fetter": request.fetter_name,
        "total_fetters_broken": len(profile.character_status.fetters_broken),
        "updated_character_status": profile.character_status.model_dump(),
        "is_noble": profile.is_noble(),
        "spiritual_score": profile.get_overall_spiritual_score()
    }


@router.get("/{model_id}/spiritual-score")
async def get_spiritual_score(model_id: str):
    """
    Calculate comprehensive spiritual development score (0-100)
    
    Based on:
    - Character stage (40 points)
    - Pāramī development (30 points)
    - Kilesa reduction (30 points)
    """
    model = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    profile = model.get_core_profile()
    score = profile.get_overall_spiritual_score()
    
    # Breakdown
    stage_scores = {
        "Puthujjana": 0,
        "Sotāpanna": 25,
        "Sakadāgāmī": 30,
        "Anāgāmī": 35,
        "Arahant": 40
    }
    stage_score = stage_scores.get(profile.character_status.type, 0)
    
    parami_dict = profile.spiritual_assets.virtue_engine.parami_portfolio.perfections
    parami_avg = sum(p.level for p in parami_dict.values()) / 10
    parami_score = (parami_avg / 10) * 30
    
    anusaya = profile.psychological_matrix.latent_tendencies.anusaya_kilesa
    kilesa_avg = sum(v["level"] for v in anusaya.values()) / 7
    kilesa_score = ((10 - kilesa_avg) / 10) * 30
    
    return {
        "model_id": model_id,
        "total_score": score,
        "breakdown": {
            "character_stage_score": round(stage_score, 2),
            "parami_score": round(parami_score, 2),
            "kilesa_reduction_score": round(kilesa_score, 2)
        },
        "character_type": profile.character_status.type,
        "is_noble": profile.is_noble(),
        "fetters_broken": len(profile.character_status.fetters_broken),
        "average_parami_level": round(parami_avg, 2),
        "average_kilesa_level": round(kilesa_avg, 2)
    }


@router.get("/{model_id}/progress-summary")
async def get_progress_summary(model_id: str):
    """
    Get comprehensive progress summary
    
    Shows:
    - Spiritual development
    - Life status
    - Mental defilements
    - Virtue development
    """
    model = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    profile = model.get_core_profile()
    
    return {
        "model_id": model_id,
        "model_name": model.name,
        "spiritual_development": {
            "character_type": profile.character_status.type,
            "stage": profile.character_status.stage,
            "is_noble": profile.is_noble(),
            "fetters_broken": profile.character_status.fetters_broken,
            "fetters_remaining": profile.character_status.fetters_remaining,
            "spiritual_score": profile.get_overall_spiritual_score()
        },
        "life_status": {
            "age": profile.life_essence.age_in_years,
            "life_force_percentage": profile.life_essence.jivitindriya_mechanics.current_jivitindriya,
            "max_life_force": profile.life_essence.jivitindriya_mechanics.max_jivitindriya,
            "lifespan_potential": profile.life_essence.life_blueprint_vipaka.lifespan_potential,
            "lifespan_remaining": profile.life_essence.life_blueprint_vipaka.lifespan_potential - profile.life_essence.age_in_years,
            "birth_realm": profile.life_essence.life_blueprint_vipaka.birth_bhumi,
            "depletion_rate": profile.life_essence.jivitindriya_mechanics.depletion_rate_per_day
        },
        "psychological_profile": {
            "dominant_temperament": profile.psychological_matrix.dominant_temperament.primary_carita,
            "anusaya_kilesa": profile.psychological_matrix.latent_tendencies.anusaya_kilesa,
            "mental_suffering_threshold": profile.psychological_matrix.vedana_tolerance_profile.mental_suffering_threshold.total_threshold
        },
        "spiritual_assets": {
            "kamma_balance": (
                profile.spiritual_assets.kamma_ledger.kusala_stock_points -
                profile.spiritual_assets.kamma_ledger.akusala_stock_points
            ),
            "sati_level": profile.spiritual_assets.virtue_engine.sati_mastery.level,
            "panna_level": profile.spiritual_assets.virtue_engine.panna_mastery.level,
            "top_parami": sorted(
                [
                    {"name": k, "level": v.level, "exp": v.exp}
                    for k, v in profile.spiritual_assets.virtue_engine.parami_portfolio.perfections.items()
                ],
                key=lambda x: x["level"],
                reverse=True
            )[:3]
        },
        "last_updated": profile.last_updated
    }


@router.get("/{model_id}/current-state")
async def get_current_state(model_id: str):
    """
    Get unified current state by merging CoreProfile + MindState
    
    Combines:
    - CoreProfile: Long-term character blueprint (anusaya baseline, parami, character stage)
    - MindState: Real-time state (current virtue levels, daily counters, active anusaya)
    
    Returns unified data with computed consciousness metrics:
    - streamBalance: Balance of consciousness stream (0-100)
    - cravingIntensity: Current craving/attachment strength (0-100)
    - wisdomLevel: Combined panna from both sources (0-100)
    
    Used for: ConsciousnessStream visualization, real-time profile display
    """
    from documents import MindState
    
    # Get CoreProfile
    model = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    profile = model.get_core_profile()
    
    # Get MindState (assuming model_id == user_id for now)
    mind_state = await MindState.find_one({"user_id": model_id})
    
    if not mind_state:
        # Return CoreProfile only if no MindState exists
        return {
            "model_id": model_id,
            "has_mind_state": False,
            "core_profile": {
                "character_type": profile.character_status.type,
                "stage": profile.character_status.stage,
                "is_noble": profile.is_noble(),
                "spiritual_score": profile.get_overall_spiritual_score()
            },
            "mind_state": None,
            "consciousness_metrics": {
                "streamBalance": 50.0,
                "cravingIntensity": 0.0,
                "wisdomLevel": 0.0
            }
        }
    
    # Merge both sources
    # Map anusaya names: CoreProfile uses Pali (kama_raga), MindState uses mixed (lobha)
    core_anusaya = profile.psychological_matrix.latent_tendencies.anusaya_kilesa
    current_anusaya = mind_state.current_anusaya or {}
    
    # Normalize anusaya names
    anusaya_mapping = {
        "kama_raga": "lobha",
        "patigha": "dosa",
        "avijja": "moha"
    }
    
    merged_anusaya = {}
    for pali_name, ms_name in anusaya_mapping.items():
        core_val = core_anusaya.get(pali_name, {}).get("level", 0.0)
        current_val = current_anusaya.get(ms_name, 0.0)
        # Current state takes precedence, with baseline from core
        merged_anusaya[ms_name] = current_val if current_val > 0 else core_val
    
    # Add remaining anusaya
    for key in ["mana", "ditthi", "vicikiccha", "thina"]:
        if key in current_anusaya:
            merged_anusaya[key] = current_anusaya[key]
        elif key in core_anusaya:
            merged_anusaya[key] = core_anusaya[key].get("level", 0.0)
    
    # Compute consciousness metrics
    # streamBalance: Balance between kusala and akusala (0-100)
    total_actions = mind_state.kusala_count_total + mind_state.akusala_count_total
    if total_actions > 0:
        kusala_ratio = mind_state.kusala_count_total / total_actions
        streamBalance = kusala_ratio * 100
    else:
        streamBalance = 50.0  # Neutral
    
    # cravingIntensity: Average of greed-related anusaya (0-100)
    lobha = merged_anusaya.get("lobha", 0.0)
    cravingIntensity = (lobha / 10) * 100
    
    # wisdomLevel: Combine MindState.panna + CoreProfile panna_mastery (0-100)
    mind_panna = mind_state.panna  # 0-10 scale
    core_panna = profile.spiritual_assets.virtue_engine.panna_mastery.level  # 0-10 scale
    combined_panna = (mind_panna * 0.6 + core_panna * 0.4)  # Weighted: 60% current, 40% baseline
    wisdomLevel = (combined_panna / 10) * 100
    
    return {
        "model_id": model_id,
        "has_mind_state": True,
        "core_profile": {
            "character_type": profile.character_status.type,
            "stage": profile.character_status.stage,
            "path_stage": profile.character_status.path_stage,
            "is_noble": profile.is_noble(),
            "spiritual_score": profile.get_overall_spiritual_score(),
            "fetters_broken": profile.character_status.fetters_broken,
            "fetters_remaining": profile.character_status.fetters_remaining,
            "baseline_anusaya": core_anusaya,
            "parami": {
                name: {"level": p.level, "exp": p.exp}
                for name, p in profile.spiritual_assets.virtue_engine.parami_portfolio.perfections.items()
            }
        },
        "mind_state": {
            "virtue": {
                "sila": mind_state.sila,
                "samadhi": mind_state.samadhi,
                "panna": mind_state.panna
            },
            "current_anusaya": current_anusaya,
            "sati_strength": mind_state.sati_strength,
            "current_bhumi": mind_state.current_bhumi,
            "daily_counts": {
                "kusala_today": mind_state.kusala_count_today,
                "akusala_today": mind_state.akusala_count_today
            },
            "total_counts": {
                "kusala_total": mind_state.kusala_count_total,
                "akusala_total": mind_state.akusala_count_total
            },
            "updated_at": mind_state.updated_at
        },
        "merged_data": {
            "anusaya": merged_anusaya,
            "virtue_combined": {
                "sila": mind_state.sila,
                "samadhi": mind_state.samadhi,
                "panna": combined_panna
            }
        },
        "consciousness_metrics": {
            "streamBalance": round(streamBalance, 1),
            "cravingIntensity": round(cravingIntensity, 1),
            "wisdomLevel": round(wisdomLevel, 1)
        },
        "timestamp": datetime.utcnow()
    }
