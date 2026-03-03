"""
🎯 Training API Router for Digital Mind Model v1.4

Endpoints for managing training sessions, tracking spiritual practice,
and modifying character development based on training results.

Endpoints:
- POST /api/v1/training/start - Start new training session
- POST /api/v1/training/complete - Complete training session
- POST /api/v1/training/{session_id}/cancel - Cancel training session
- GET /api/v1/training-log/{model_id} - Get training history
- GET /api/v1/training-log/{model_id}/stats - Get training statistics
"""

from fastapi import APIRouter, HTTPException, Header, Query
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from training_models import (
    StartTrainingRequest,
    StartTrainingResponse,
    CompleteTrainingRequest,
    CompleteTrainingResponse,
    TrainingSession,
    TrainingLog,
    TrainingStatsResponse,
    TrainingResultDetails,
    TrainingModification,
    get_training_type_info,
    calculate_exp_gain
)
# from database import get_database  # Not needed - using Beanie ODM
from config import settings

router = APIRouter(prefix="/api/v1", tags=["training"])


# ============================================================================
# IN-MEMORY STORAGE (Temporary - Replace with MongoDB in production)
# ============================================================================

training_sessions_store = {}  # session_id -> TrainingSession
active_sessions = {}  # session_id -> start_time


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def verify_api_key(x_api_key: str = Header(...)):
    """Verify API key from header"""
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key


def generate_session_id() -> str:
    """Generate unique session ID"""
    return f"train-{uuid.uuid4().hex[:8]}"


async def get_model_profile(model_id: str):
    """Fetch model's core profile from database"""
    from documents import DigitalMindModel
    model = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found")
    return model


async def update_model_profile(model_id: str, updates: dict):
    """Update model's core profile in database"""
    from documents import DigitalMindModel
    model = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
    if not model:
        return False
    # Apply updates to model
    for key, value in updates.items():
        if hasattr(model, key):
            setattr(model, key, value)
    await model.save()
    return True


def calculate_modifications(
    training_type: str,
    result: str,
    metrics: dict,
    current_profile: dict
) -> List[TrainingModification]:
    """
    Calculate character modifications based on training results.
    
    Logic:
    - Successful: Full exp gain, positive modifications
    - Partially Successful: Reduced exp gain, mixed modifications
    - Failed: No exp gain, possible negative modifications
    """
    modifications = []
    
    info = get_training_type_info(training_type)
    if not info:
        return modifications
    
    # Get current values from profile
    core_profile = current_profile.get("CoreProfile", {})
    spiritual_assets = core_profile.get("SpiritualAssets", {})
    virtue_engine = spiritual_assets.get("VirtueEngine", {})
    parami_portfolio = virtue_engine.get("Paramī_Portfolio", {})
    perfections = parami_portfolio.get("perfections", {})
    
    quality = metrics.get("quality_score", 5.0)
    duration = metrics.get("duration_minutes", info["typical_duration"])
    
    if result == "Successful":
        # Award full experience to target pāramī
        target_parami = info["target_parami"]
        current_parami = perfections.get(target_parami, {"level": 0, "exp": 0})
        
        exp_gained = calculate_exp_gain(training_type, quality, duration)
        new_exp = current_parami.get("exp", 0) + exp_gained
        
        # Check for level up (every 200 exp = 1 level, max level 10)
        exp_per_level = 200
        new_level = min(new_exp // exp_per_level, 10)
        old_level = current_parami.get("level", 0)
        
        modifications.append(TrainingModification(
            target=f"Barami.{target_parami}",
            old_value=old_level,
            new_value=new_level,
            delta=f"+{new_level - old_level} level" if new_level > old_level else f"+{exp_gained} exp",
            exp_change=f"+{exp_gained} exp"
        ))
        
        # Add kusala kamma
        kamma_ledger = spiritual_assets.get("KammaLedger", {})
        old_kusala = kamma_ledger.get("total_kusala", 0)
        kusala_gained = int(exp_gained * 0.8)
        
        modifications.append(TrainingModification(
            target="KammaLedger.kusala",
            old_value=old_kusala,
            new_value=old_kusala + kusala_gained,
            delta=f"+{kusala_gained}"
        ))
        
        # Special effects for certain training types
        if training_type == "MEDITATION":
            # Increase sati & panna mastery
            sati_mastery = virtue_engine.get("Sati_mastery", {"level": 0, "exp": 0})
            sati_exp_gained = metrics.get("sati_exp_gained", int(exp_gained * 0.6))
            
            modifications.append(TrainingModification(
                target="Sati_mastery",
                old_value=sati_mastery.get("exp", 0),
                new_value=sati_mastery.get("exp", 0) + sati_exp_gained,
                delta=f"+{sati_exp_gained} exp"
            ))
            
            # Reduce avijja (ignorance) slightly
            psych_matrix = core_profile.get("PsychologicalMatrix", {})
            latent = psych_matrix.get("LatentTendencies", {})
            anusaya = latent.get("anusaya_kilesa", {})
            avijja = anusaya.get("avijja", {"level": 0})
            
            if avijja.get("level", 0) > 0:
                reduction = min(0.5, avijja.get("level", 0))
                modifications.append(TrainingModification(
                    target="Anusaya.avijja",
                    old_value=avijja.get("level", 0),
                    new_value=avijja.get("level", 0) - reduction,
                    delta=f"-{reduction} (reduced ignorance)"
                ))
        
        elif training_type == "LOVING_KINDNESS":
            # Reduce patigha (aversion)
            psych_matrix = core_profile.get("PsychologicalMatrix", {})
            latent = psych_matrix.get("LatentTendencies", {})
            anusaya = latent.get("anusaya_kilesa", {})
            patigha = anusaya.get("patigha", {"level": 0})
            
            reduction = metrics.get("patigha_reduction", 0.5)
            if patigha.get("level", 0) > 0:
                modifications.append(TrainingModification(
                    target="Anusaya.patigha",
                    old_value=patigha.get("level", 0),
                    new_value=max(0, patigha.get("level", 0) - reduction),
                    delta=f"-{reduction} (reduced aversion)"
                ))
    
    elif result == "Partially Successful":
        # Reduced rewards, possible mixed effects
        target_parami = info["target_parami"]
        current_parami = perfections.get(target_parami, {"level": 0, "exp": 0})
        
        exp_gained = calculate_exp_gain(training_type, quality, duration) // 2
        
        modifications.append(TrainingModification(
            target=f"Barami.{target_parami}",
            old_value=current_parami.get("exp", 0),
            new_value=current_parami.get("exp", 0) + exp_gained,
            delta=f"+{exp_gained} exp"
        ))
        
        # Possible negative side effect
        if metrics.get("vedana_tolerance_change", 0) < 0:
            psych_matrix = core_profile.get("PsychologicalMatrix", {})
            vedana = psych_matrix.get("VedanaToleranceProfile", {})
            mental = vedana.get("mental_suffering_threshold", {})
            
            change = metrics.get("vedana_tolerance_change", -0.5)
            modifications.append(TrainingModification(
                target="VedanaTolerance.mental",
                old_value=mental.get("total_threshold", 5.0),
                new_value=mental.get("total_threshold", 5.0) + change,
                delta=f"{change}"
            ))
    
    elif result == "Failed":
        # Negative consequences
        kamma_ledger = spiritual_assets.get("KammaLedger", {})
        old_akusala = kamma_ledger.get("total_akusala", 0)
        akusala_gained = 10
        
        modifications.append(TrainingModification(
            target="KammaLedger.akusala",
            old_value=old_akusala,
            new_value=old_akusala + akusala_gained,
            delta=f"+{akusala_gained}"
        ))
        
        # Possible increase in kilesa
        if training_type == "RENUNCIATION":
            psych_matrix = core_profile.get("PsychologicalMatrix", {})
            latent = psych_matrix.get("LatentTendencies", {})
            anusaya = latent.get("anusaya_kilesa", {})
            kama_raga = anusaya.get("kama_raga", {"level": 0})
            
            increase = metrics.get("kama_raga_increase", 0.5)
            modifications.append(TrainingModification(
                target="Anusaya.kama_raga",
                old_value=kama_raga.get("level", 0),
                new_value=kama_raga.get("level", 0) + increase,
                delta=f"+{increase} (increased sensual desire)"
            ))
    
    return modifications


def apply_modifications_to_profile(profile: dict, modifications: List[TrainingModification]) -> dict:
    """Apply calculated modifications to profile structure"""
    updated = profile.copy()
    
    for mod in modifications:
        parts = mod.target.split(".")
        
        # Navigate to target location
        current = updated.get("CoreProfile", {}).get("SpiritualAssets", {})
        
        if parts[0] == "Barami":
            # Update pāramī
            parami_name = parts[1]
            perfections = current.get("VirtueEngine", {}).get("Paramī_Portfolio", {}).get("perfections", {})
            
            if parami_name not in perfections:
                perfections[parami_name] = {"level": 0, "exp": 0}
            
            if mod.new_value is not None:
                if "level" in mod.delta:
                    perfections[parami_name]["level"] = int(mod.new_value)
                else:
                    perfections[parami_name]["exp"] = int(mod.new_value)
        
        elif parts[0] == "KammaLedger":
            # Update kamma
            kamma_type = parts[1]
            kamma_ledger = current.get("KammaLedger", {})
            
            if kamma_type == "kusala":
                kamma_ledger["total_kusala"] = int(mod.new_value)
            elif kamma_type == "akusala":
                kamma_ledger["total_akusala"] = int(mod.new_value)
            
            # Recalculate balance
            kusala = kamma_ledger.get("total_kusala", 0)
            akusala = kamma_ledger.get("total_akusala", 0)
            kamma_ledger["net_balance"] = kusala - akusala
            kamma_ledger["balance_ratio"] = round(kusala / max(akusala, 1), 2)
        
        elif parts[0] == "Sati_mastery":
            # Update mindfulness
            virtue_engine = current.get("VirtueEngine", {})
            if "Sati_mastery" not in virtue_engine:
                virtue_engine["Sati_mastery"] = {"level": 0, "exp": 0}
            virtue_engine["Sati_mastery"]["exp"] = int(mod.new_value)
        
        elif parts[0] == "Anusaya":
            # Update kilesa
            kilesa_name = parts[1]
            psych = updated.get("CoreProfile", {}).get("PsychologicalMatrix", {})
            latent = psych.get("LatentTendencies", {})
            anusaya = latent.get("anusaya_kilesa", {})
            
            if kilesa_name in anusaya:
                anusaya[kilesa_name]["level"] = float(mod.new_value)
    
    updated["last_updated"] = datetime.utcnow().isoformat() + "Z"
    
    return updated


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post("/training/start", response_model=StartTrainingResponse)
async def start_training(
    request: StartTrainingRequest,
    x_api_key: str = Header(...)
):
    """
    Start a new training session.
    
    - Validates model exists
    - Validates training type
    - Creates session record
    - Returns session ID and estimated completion
    """
    verify_api_key(x_api_key)
    
    # Validate model exists
    model = await get_model_profile(request.model_id)
    
    # Validate training type
    if not get_training_type_info(request.training_type):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid training type: {request.training_type}"
        )
    
    # Generate session
    session_id = generate_session_id()
    start_time = datetime.utcnow()
    estimated_completion = start_time + timedelta(minutes=request.duration_minutes)
    
    # Store active session
    active_sessions[session_id] = {
        "model_id": request.model_id,
        "training_type": request.training_type,
        "start_time": start_time,
        "duration_minutes": request.duration_minutes,
        "notes": request.notes
    }
    
    return StartTrainingResponse(
        success=True,
        session_id=session_id,
        message=f"Training session started: {request.training_type}",
        estimated_completion=estimated_completion
    )


@router.post("/training/complete", response_model=CompleteTrainingResponse)
async def complete_training(
    request: CompleteTrainingRequest,
    x_api_key: str = Header(...)
):
    """
    Complete a training session and apply modifications.
    
    - Validates session exists
    - Calculates modifications based on result
    - Updates character profile
    - Stores training record
    - Returns modifications made
    """
    verify_api_key(x_api_key)
    
    # Get active session
    if request.session_id not in active_sessions:
        raise HTTPException(
            status_code=404,
            detail=f"Training session '{request.session_id}' not found or already completed"
        )
    
    session_data = active_sessions[request.session_id]
    model_id = session_data["model_id"]
    
    # Get current profile
    model = await get_model_profile(model_id)
    
    # Calculate modifications
    metrics_dict = request.metrics.dict(exclude_none=True)
    modifications = calculate_modifications(
        session_data["training_type"],
        request.result,
        metrics_dict,
        model
    )
    
    # Apply modifications to profile
    updated_profile = apply_modifications_to_profile(model, modifications)
    
    # Update database
    await update_model_profile(model_id, updated_profile)
    
    # Create training session record
    training_session = TrainingSession(
        id=request.session_id,
        model_id=model_id,
        training_type=session_data["training_type"],
        date=datetime.utcnow().strftime("%Y-%m-%d"),
        duration_minutes=session_data["duration_minutes"],
        result=request.result,
        result_details=TrainingResultDetails(
            status=request.result.lower().replace(" ", "_"),
            metrics=request.metrics,
            notes=request.notes
        ),
        modifications=modifications,
        completed_at=datetime.utcnow()
    )
    
    # Store session
    training_sessions_store[request.session_id] = training_session
    
    # Remove from active sessions
    del active_sessions[request.session_id]
    
    # Prepare response
    relevant_updates = {
        "spiritual_score": updated_profile.get("spiritual_score"),
        "modifications_count": len(modifications)
    }
    
    return CompleteTrainingResponse(
        success=True,
        modifications=modifications,
        updated_profile=relevant_updates,
        message=f"Training completed: {request.result}"
    )


@router.get("/training-log/{model_id}", response_model=TrainingLog)
async def get_training_log(
    model_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    x_api_key: str = Header(...)
):
    """
    Get training history for a model.
    
    Returns paginated list of training sessions with statistics.
    """
    verify_api_key(x_api_key)
    
    # Validate model exists
    await get_model_profile(model_id)
    
    # Get sessions for this model
    sessions = [
        s for s in training_sessions_store.values()
        if s.model_id == model_id
    ]
    
    # Sort by date descending
    sessions.sort(key=lambda x: x.completed_at, reverse=True)
    
    # Paginate
    total = len(sessions)
    paginated = sessions[offset:offset + limit]
    
    # Calculate statistics
    if total > 0:
        successful = sum(1 for s in sessions if s.result == "Successful")
        success_rate = (successful / total) * 100
        
        total_exp = sum(
            m.exp_change for s in sessions for m in s.modifications
            if m.exp_change and "+" in m.exp_change
        )
        
        last_date = sessions[0].date if sessions else None
    else:
        success_rate = 0.0
        total_exp = 0
        last_date = None
    
    return TrainingLog(
        model_id=model_id,
        training_sessions=paginated,
        total_sessions=total,
        success_rate=round(success_rate, 1),
        total_exp_gained=total_exp,
        last_training_date=last_date
    )


@router.get("/training-log/{model_id}/stats", response_model=TrainingStatsResponse)
async def get_training_stats(
    model_id: str,
    x_api_key: str = Header(...)
):
    """
    Get training statistics summary for a model.
    """
    verify_api_key(x_api_key)
    
    # Validate model exists
    await get_model_profile(model_id)
    
    # Get sessions
    sessions = [
        s for s in training_sessions_store.values()
        if s.model_id == model_id
    ]
    
    if not sessions:
        return TrainingStatsResponse(
            model_id=model_id,
            total_sessions=0,
            success_rate=0.0,
            total_exp_gained=0,
            total_kusala_earned=0,
            total_akusala_earned=0,
            streak_days=0,
            average_duration=0
        )
    
    # Calculate stats
    successful = sum(1 for s in sessions if s.result == "Successful")
    success_rate = (successful / len(sessions)) * 100
    
    avg_duration = sum(s.duration_minutes for s in sessions) // len(sessions)
    
    # Count training types
    type_counts = {}
    for s in sessions:
        type_counts[s.training_type] = type_counts.get(s.training_type, 0) + 1
    
    most_practiced = max(type_counts, key=lambda k: type_counts[k]) if type_counts else None
    
    # Calculate total exp from modifications
    total_exp_gained = 0
    for s in sessions:
        for mod in s.modifications:
            if mod.exp_change:
                # Extract numeric exp value (e.g., "+25 exp" -> 25)
                try:
                    exp_str = mod.exp_change.replace("exp", "").replace("+", "").strip()
                    total_exp_gained += int(exp_str)
                except (ValueError, AttributeError):
                    pass
    
    # Calculate streak days (consecutive days with sessions)
    streak_days = 0
    if sessions:
        # Sort sessions by date
        sorted_sessions = sorted(sessions, key=lambda x: x.date, reverse=True)
        
        # Check consecutive days from most recent
        from datetime import datetime, timedelta
        current_date = datetime.strptime(sorted_sessions[0].date, "%Y-%m-%d").date()
        check_date = current_date
        
        session_dates = set(datetime.strptime(s.date, "%Y-%m-%d").date() for s in sorted_sessions)
        
        while check_date in session_dates:
            streak_days += 1
            check_date -= timedelta(days=1)
    
    return TrainingStatsResponse(
        model_id=model_id,
        total_sessions=len(sessions),
        success_rate=round(success_rate, 1),
        total_exp_gained=total_exp_gained,
        total_kusala_earned=0,
        total_akusala_earned=0,
        streak_days=streak_days,
        average_duration=avg_duration,
        most_practiced_type=most_practiced
    )


@router.post("/training/{session_id}/cancel")
async def cancel_training(
    session_id: str,
    x_api_key: str = Header(...)
):
    """Cancel an active training session"""
    verify_api_key(x_api_key)
    
    if session_id not in active_sessions:
        raise HTTPException(
            status_code=404,
            detail=f"Active session '{session_id}' not found"
        )
    
    del active_sessions[session_id]
    
    return {
        "success": True,
        "message": f"Training session '{session_id}' cancelled"
    }
