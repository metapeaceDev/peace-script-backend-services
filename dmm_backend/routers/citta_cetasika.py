"""
🧠 Citta-Cetasika Router - Mind and Mental Factors API

Endpoints for interacting with the Citta-Cetasika Model:
- Get current citta distribution statistics
- Get cetasika manifold (active mental factors)
- Record citta moments
- Query citta history
- Get Anusaya-Cetasika mapping
- Get Pāramī-Cetasika mapping

Author: Peace Script Model v1.4
Created: 2024-10-17
"""

from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

# Import our Citta-Cetasika models
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from citta_cetasika_models import (
    CittaCategory, CittaType, CetasikaCategory,
    Cetasika, Citta, CittaMoment, CittaVithi,
    CetasikaManifold, AnusayaCetasikaMap, ParamiCetasikaMap,
    load_cittas_from_json, load_cetasikas_from_json
)

# Import database documents
from documents import CittaMomentRecord, KammaLogEntry

router = APIRouter(
    prefix="/api/citta-cetasika",
    tags=["Citta-Cetasika Engine"]
)

# ============================================================================
# Response Models
# ============================================================================

class CittaStatistics(BaseModel):
    """Statistics about citta distribution"""
    total_moments: int = Field(..., description="Total citta moments recorded")
    by_category: Dict[str, int] = Field(..., description="Count by category (Kusala, Akusala, etc.)")
    by_type: Dict[str, int] = Field(..., description="Count by specific type")
    kusala_percentage: float = Field(..., description="Percentage of wholesome cittas")
    akusala_percentage: float = Field(..., description="Percentage of unwholesome cittas")
    dominant_category: str = Field(..., description="Most frequent category")
    dominant_type: str = Field(..., description="Most frequent type")

class CetasikaManifoldResponse(BaseModel):
    """Active cetasikas at current moment"""
    universal: List[str] = Field(..., description="7 universal cetasikas (always present)")
    particular: List[str] = Field(..., description="Particular cetasikas (context-specific)")
    kusala: List[str] = Field(..., description="Wholesome cetasikas")
    akusala: List[str] = Field(..., description="Unwholesome cetasikas")
    total_count: int = Field(..., description="Total active cetasikas")
    strength_map: Dict[str, float] = Field(..., description="Strength of each active cetasika (0-10)")

class CittaMomentResponse(BaseModel):
    """Single citta moment record"""
    timestamp: datetime = Field(..., description="When the citta moment occurred")
    citta_type: str = Field(..., description="Type of consciousness")
    category: str = Field(..., description="Category (Kusala/Akusala/Abyakata)")
    feeling: str = Field(..., description="Vedanā (sukha/dukkha/upekkha)")
    root: Optional[str] = Field(None, description="Root (lobha/dosa/moha/alobha/adosa/amoha)")
    prompted: bool = Field(..., description="Whether prompted by conditions")
    accompanied_by_knowledge: bool = Field(..., description="With wisdom (ñāṇa)")
    cetasikas: List[str] = Field(..., description="Active cetasikas in this moment")
    intensity: float = Field(..., description="Strength of the citta (0-10)")
    duration_ms: int = Field(default=17, description="Duration in milliseconds (1 cittakkhaṇa ≈ 17ms)")
    context: Optional[Dict[str, Any]] = Field(None, description="Contextual information")

class AnusayaMappingResponse(BaseModel):
    """Anusaya → Cetasika mapping for a character"""
    anusaya_name: str = Field(..., description="Name of the anusaya (latent tendency)")
    pali: str = Field(..., description="Pali name")
    level: float = Field(..., description="Current level (0-10)")
    primary_cetasikas: List[str] = Field(..., description="Primary cetasikas that manifest this anusaya")
    secondary_cetasikas: List[str] = Field(..., description="Secondary supporting cetasikas")
    akusala_frequency: float = Field(..., description="Frequency of related akusala cittas (0-100%)")
    recommended_training: List[str] = Field(..., description="Buddhist practices to weaken this anusaya")

class ParamiMappingResponse(BaseModel):
    """Pāramī → Cetasika mapping for a character"""
    parami_name: str = Field(..., description="Name of the pāramī (perfection)")
    pali: str = Field(..., description="Pali name")
    level: float = Field(..., description="Current level (0-10)")
    primary_cetasikas: List[str] = Field(..., description="Primary cetasikas that manifest this pāramī")
    secondary_cetasikas: List[str] = Field(..., description="Secondary supporting cetasikas")
    kusala_frequency: float = Field(..., description="Frequency of related kusala cittas (0-100%)")
    cultivation_methods: List[str] = Field(..., description="Methods to strengthen this pāramī")

class CittaVithiResponse(BaseModel):
    """Mind-door process (citta vīthi) sequence"""
    vithi_id: str = Field(..., description="Unique ID for this process")
    object_presented: str = Field(..., description="Sense object that triggered the process")
    door: str = Field(..., description="Sense door (eye/ear/nose/tongue/body/mind)")
    stages: List[Dict[str, Any]] = Field(..., description="Sequence of citta moments in the process")
    javana_count: int = Field(..., description="Number of javana (impulsion) moments")
    kamma_created: bool = Field(..., description="Whether kamma was created (in javana stage)")
    total_duration_ms: int = Field(..., description="Total process duration")
    result: str = Field(..., description="Outcome of the process")

# ============================================================================
# GET Endpoints
# ============================================================================

@router.get("/{model_id}/statistics", response_model=CittaStatistics)
async def get_citta_statistics(
    model_id: str,
    time_window_hours: Optional[int] = None
):
    """
    Get statistics about citta distribution for a character.
    
    This analyzes the character's citta history to show:
    - Distribution by category (Kusala, Akusala, Abyākata)
    - Distribution by specific types
    - Dominant patterns
    - Kusala/Akusala ratio
    
    Args:
        model_id: Character ID
        time_window_hours: Optional time window (e.g., last 24 hours). If None, all history.
    
    Returns:
        CittaStatistics with comprehensive analysis
    
    Example:
        GET /api/citta-cetasika/123/statistics?time_window_hours=24
    """
    # Implement actual database query from MindState
    try:
        from documents import DigitalMindModel, MindState
        
        # Get mind state for this model
        mind_state = await MindState.find_one(MindState.user_id == model_id)
        if not mind_state:
            raise HTTPException(
                status_code=404,
                detail=f"Mind state for model {model_id} not found"
            )
        
        # Calculate statistics from actual data
        kusala_total = mind_state.kusala_count_total
        akusala_total = mind_state.akusala_count_total
        total_moments = kusala_total + akusala_total
        
        # Estimate abyakata (neutral) as ~25% of total (based on Buddhist psychology)
        abyakata_estimated = int(total_moments * 0.25)
        total_with_abyakata = total_moments + abyakata_estimated
        
        # Calculate percentages
        kusala_pct = (kusala_total / total_with_abyakata * 100) if total_with_abyakata > 0 else 0
        akusala_pct = (akusala_total / total_with_abyakata * 100) if total_with_abyakata > 0 else 0
        
        # Determine dominant category
        if kusala_total > akusala_total:
            dominant_category = "Kusala"
            dominant_type = "Mahā-kusala-citta"
        elif akusala_total > kusala_total:
            dominant_category = "Akusala"
            # Determine akusala type from anusaya levels
            max_anusaya = max(mind_state.current_anusaya.items(), key=lambda x: x[1])
            if max_anusaya[0] in ["lobha", "kama_raga"]:
                dominant_type = "Lobha-mūla-citta"
            elif max_anusaya[0] in ["dosa", "patigha"]:
                dominant_type = "Dosa-mūla-citta"
            else:
                dominant_type = "Moha-mūla-citta"
        else:
            dominant_category = "Abyakata"
            dominant_type = "Mahā-vipāka-citta"
        
        # Build type distribution (estimate based on anusaya)
        by_type = {}
        if akusala_total > 0:
            lobha_ratio = mind_state.current_anusaya.get("lobha", 0) / 10
            dosa_ratio = mind_state.current_anusaya.get("dosa", 0) / 10
            moha_ratio = mind_state.current_anusaya.get("moha", 0) / 10
            total_ratio = lobha_ratio + dosa_ratio + moha_ratio
            
            if total_ratio > 0:
                by_type["Lobha-mūla-citta"] = int(akusala_total * (lobha_ratio / total_ratio))
                by_type["Dosa-mūla-citta"] = int(akusala_total * (dosa_ratio / total_ratio))
                by_type["Moha-mūla-citta"] = int(akusala_total * (moha_ratio / total_ratio))
        
        if kusala_total > 0:
            by_type["Mahā-kusala-citta"] = kusala_total
        
        if abyakata_estimated > 0:
            by_type["Mahā-vipāka-citta"] = abyakata_estimated
        
        return CittaStatistics(
            total_moments=total_with_abyakata,
            by_category={
                "Kusala": kusala_total,
                "Akusala": akusala_total,
                "Abyakata": abyakata_estimated
            },
            by_type=by_type,
            kusala_percentage=round(kusala_pct, 1),
            akusala_percentage=round(akusala_pct, 1),
            dominant_category=dominant_category,
            dominant_type=dominant_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching citta statistics: {e}")
        # Fallback to mock data
        return CittaStatistics(
            total_moments=0,
            by_category={"Kusala": 0, "Akusala": 0, "Abyakata": 0},
            by_type={},
            kusala_percentage=0.0,
            akusala_percentage=0.0,
            dominant_category="Abyakata",
            dominant_type="Unknown"
        )

@router.get("/{model_id}/current-manifold", response_model=CetasikaManifoldResponse)
async def get_current_cetasika_manifold(model_id: str):
    """
    Get the current active cetasika manifold for a character.
    
    Returns which mental factors are currently active, their strengths,
    and categorization (universal/particular/kusala/akusala).
    
    Args:
        model_id: Character ID
    
    Returns:
        CetasikaManifoldResponse with active cetasikas
    
    Example:
        GET /api/citta-cetasika/123/current-manifold
    """
    # Import documents
    from documents import DigitalMindModel, MindState
    
    # Get character and mind state
    character = await DigitalMindModel.get(model_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character {model_id} not found"
        )
    
    mind_state = await MindState.find_one({"user_id": model_id})
    if not mind_state:
        # Return default universal cetasikas if no mind state
        return CetasikaManifoldResponse(
            universal=["phassa", "vedana", "sanna", "cetana", "ekaggata", "jivitindriya", "manasikara"],
            particular=[],
            kusala=[],
            akusala=[],
            total_count=7,
            strength_map={}
        )
    
    # 7 Universal cetasikas (always present)
    universal = ["phassa", "vedana", "sanna", "cetana", "ekaggata", "jivitindriya", "manasikara"]
    
    # Particular cetasikas based on concentration/thought
    particular = []
    if mind_state.samadhi >= 5.0:
        particular.extend(["vitakka", "vicara"])  # Initial & sustained thought
    if mind_state.sati_strength >= 6.0:
        particular.append("adhimokkha")  # Decision/determination
    
    # Kusala cetasikas based on virtue levels
    kusala = []
    strength_map = {}
    
    # Always present kusala sobhana cetasikas
    kusala.extend(["alobha", "adosa", "amoha"])  # Beautiful universals
    strength_map["alobha"] = 10.0 - mind_state.current_anusaya.get("lobha", 3.0)
    strength_map["adosa"] = 10.0 - mind_state.current_anusaya.get("dosa", 2.5)
    strength_map["amoha"] = 10.0 - mind_state.current_anusaya.get("moha", 3.5)
    
    # Sobhana cetasikas based on virtue strength
    if mind_state.sati_strength >= 4.0:
        kusala.append("sati")
        strength_map["sati"] = mind_state.sati_strength
    
    if mind_state.panna >= 4.0:
        kusala.append("panna")
        strength_map["panna"] = mind_state.panna
    
    if mind_state.samadhi >= 4.0:
        kusala.append("samadhi")
        strength_map["samadhi"] = mind_state.samadhi
    
    if mind_state.sila >= 5.0:
        kusala.extend(["saddha", "viriya"])  # Faith & energy
        strength_map["saddha"] = mind_state.sila * 0.8
        strength_map["viriya"] = mind_state.sila * 0.7
    
    # Akusala cetasikas based on anusaya levels
    akusala = []
    for anusaya_name, level in mind_state.current_anusaya.items():
        if level >= 4.0:  # Threshold for manifestation
            # Map anusaya to akusala cetasikas
            if anusaya_name in ["lobha"]:
                akusala.append("lobha")
                strength_map["lobha"] = level
            elif anusaya_name in ["dosa"]:
                akusala.append("dosa")
                strength_map["dosa"] = level
            elif anusaya_name in ["moha"]:
                akusala.append("moha")
                strength_map["moha"] = level
            elif anusaya_name in ["mana"]:
                akusala.append("mana")
                strength_map["mana"] = level
            elif anusaya_name in ["ditthi"]:
                akusala.append("ditthi")
                strength_map["ditthi"] = level
    
    # Remove duplicates
    kusala = list(set(kusala))
    akusala = list(set(akusala))
    
    total_count = len(universal) + len(particular) + len(kusala) + len(akusala)
    
    return CetasikaManifoldResponse(
        universal=universal,
        particular=particular,
        kusala=kusala,
        akusala=akusala,
        total_count=total_count,
        strength_map=strength_map
    )

@router.get("/{model_id}/anusaya-mapping", response_model=List[AnusayaMappingResponse])
async def get_anusaya_cetasika_mapping(model_id: str):
    """
    Get Anusaya → Cetasika mapping for a character.
    
    Shows which cetasikas manifest each latent tendency (anusaya),
    how frequently they arise, and training recommendations.
    
    Args:
        model_id: Character ID
    
    Returns:
        List of AnusayaMappingResponse for all 7 anusayas
    
    Example:
        GET /api/citta-cetasika/123/anusaya-mapping
    """
    # Import documents
    from documents import DigitalMindModel, MindState
    
    # Get mind state for real anusaya levels
    mind_state = await MindState.find_one({"user_id": model_id})
    if not mind_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mind state for {model_id} not found"
        )
    
    # Map MindState anusaya names to standard 7 anusaya
    # MindState uses: lobha, dosa, moha, mana, ditthi, vicikiccha, thina
    # Standard 7: kāmarāga, paṭigha, māna, diṭṭhi, vicikicchā, bhavarāga, avijjā
    anusaya_mapping = {
        "kamaraga": mind_state.current_anusaya.get("lobha", 3.0),
        "patigha": mind_state.current_anusaya.get("dosa", 2.5),
        "mana": mind_state.current_anusaya.get("mana", 2.0),
        "ditthi": mind_state.current_anusaya.get("ditthi", 2.0),
        "vicikiccha": mind_state.current_anusaya.get("vicikiccha", 2.5),
        "bhavaraga": mind_state.current_anusaya.get("lobha", 3.0) * 0.8,  # Related to existence craving
        "avijja": mind_state.current_anusaya.get("moha", 3.5)  # Ignorance
    }
    
    # Cetasika associations for each anusaya
    anusaya_cetasika_map = {
        "kamaraga": {
            "primary": ["lobha", "raga", "tanha"],
            "secondary": ["vedana", "sanna"],
            "training": ["asubha contemplation", "dana practice", "sense restraint"]
        },
        "patigha": {
            "primary": ["dosa", "patigha", "vyapada"],
            "secondary": ["mana", "issa"],
            "training": ["metta meditation", "patience", "forgiveness"]
        },
        "mana": {
            "primary": ["mana", "atimana"],
            "secondary": ["ditthi", "vicikiccha"],
            "training": ["humility practice", "not-self contemplation", "service to others"]
        },
        "ditthi": {
            "primary": ["ditthi", "miccha-ditthi"],
            "secondary": ["moha", "vicikiccha"],
            "training": ["right view study", "four noble truths", "dependent origination"]
        },
        "vicikiccha": {
            "primary": ["vicikiccha", "moha"],
            "secondary": ["thina", "middha"],
            "training": ["confidence in triple gem", "dhamma study", "kalyana-mitta"]
        },
        "bhavaraga": {
            "primary": ["lobha", "tanha", "upadana"],
            "secondary": ["ditthi", "mana"],
            "training": ["impermanence contemplation", "death reflection", "renunciation"]
        },
        "avijja": {
            "primary": ["moha", "avijja", "aññana"],
            "secondary": ["vicikiccha", "ahirika", "anottappa"],
            "training": ["wisdom development", "four foundations of mindfulness", "investigation"]
        }
    }
    
    results = []
    for anusaya_id, level in anusaya_mapping.items():
        mapping = anusaya_cetasika_map.get(anusaya_id, {})
        
        # Calculate frequency based on level and total actions
        total_actions = mind_state.kusala_count_total + mind_state.akusala_count_total
        akusala_frequency = level * 8.0 if total_actions == 0 else (level / 10.0) * mind_state.akusala_count_total
        
        results.append(AnusayaMappingResponse(
            anusaya_name=anusaya_id.title(),
            pali=anusaya_id,
            level=level,
            primary_cetasikas=mapping.get("primary", []),
            secondary_cetasikas=mapping.get("secondary", []),
            akusala_frequency=akusala_frequency,
            recommended_training=mapping.get("training", [])
        ))
    
    return results

@router.get("/{model_id}/parami-mapping", response_model=List[ParamiMappingResponse])
async def get_parami_cetasika_mapping(model_id: str):
    """
    Get Pāramī → Cetasika mapping for a character.
    
    Shows which cetasikas manifest each perfection (pāramī),
    how frequently they arise, and cultivation methods.
    
    Args:
        model_id: Character ID
    
    Returns:
        List of ParamiMappingResponse for all 10 pāramīs
    
    Example:
        GET /api/citta-cetasika/123/parami-mapping
    """
    # Import documents
    from documents import DigitalMindModel, MindState
    
    # Get character to access CoreProfile
    character = await DigitalMindModel.get(model_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character {model_id} not found"
        )
    
    # Get CoreProfile with spiritual assets
    core_profile = character.get_core_profile()
    parami_portfolio = core_profile.spiritual_assets.virtue_engine.parami_portfolio
    
    # Get pāramī levels from portfolio
    parami_levels = {}
    for parami_name, entry in parami_portfolio.perfections.items():
        parami_levels[parami_name] = entry.level
    
    # Cetasika associations for each pāramī
    parami_cetasika_map = {
        "dana": {
            "primary": ["alobha", "caga", "karuna"],
            "secondary": ["metta", "mudita"],
            "methods": ["generous giving", "letting go practice", "non-attachment meditation"]
        },
        "sila": {
            "primary": ["hiri", "ottappa", "saddha"],
            "secondary": ["sati", "samadhi"],
            "methods": ["precept observance", "right speech", "moral reflection"]
        },
        "nekkhamma": {
            "primary": ["alobha", "viraga", "viveka"],
            "secondary": ["adhitthana", "panna"],
            "methods": ["renunciation practice", "simplicity", "forest dwelling"]
        },
        "panna": {
            "primary": ["amoha", "panna", "yoniso-manasikara"],
            "secondary": ["vitakka", "vicara", "dhamma-vicaya"],
            "methods": ["vipassana meditation", "dhamma study", "wise reflection"]
        },
        "viriya": {
            "primary": ["viriya", "vīriyambojjhanga"],
            "secondary": ["adhitthana", "chanda"],
            "methods": ["effort cultivation", "arousing energy", "diligence practice"]
        },
        "khanti": {
            "primary": ["adosa", "upekkha", "khanti"],
            "secondary": ["metta", "samadhi"],
            "methods": ["patience practice", "endurance training", "acceptance meditation"]
        },
        "sacca": {
            "primary": ["sacca", "saddha"],
            "secondary": ["hiri", "ottappa", "adhitthana"],
            "methods": ["truthfulness", "integrity practice", "keeping promises"]
        },
        "adhitthana": {
            "primary": ["adhitthana", "viriya", "nekkhamma"],
            "secondary": ["sati", "samadhi"],
            "methods": ["determination practice", "resolve strengthening", "commitment training"]
        },
        "metta": {
            "primary": ["metta", "adosa", "avyapada"],
            "secondary": ["mudita", "karuna"],
            "methods": ["metta meditation", "lovingkindness practice", "goodwill cultivation"]
        },
        "upekkha": {
            "primary": ["upekkha", "tatramajjhattata"],
            "secondary": ["panna", "samadhi"],
            "methods": ["equanimity meditation", "balanced mind", "impartiality practice"]
        }
    }
    
    # Get mind state for kusala frequency calculation
    mind_state = await MindState.find_one({"user_id": model_id})
    total_kusala = mind_state.kusala_count_total if mind_state else 0
    
    results = []
    for parami_id, level in parami_levels.items():
        mapping = parami_cetasika_map.get(parami_id, {})
        
        # Calculate frequency based on level and kusala actions
        kusala_frequency = level * 9.0 if total_kusala == 0 else (level / 10.0) * total_kusala * 0.1
        
        results.append(ParamiMappingResponse(
            parami_name=parami_id.title(),
            pali=parami_id,
            level=float(level),
            primary_cetasikas=mapping.get("primary", []),
            secondary_cetasikas=mapping.get("secondary", []),
            kusala_frequency=kusala_frequency,
            cultivation_methods=mapping.get("methods", [])
        ))
    
    return results

@router.get("/{model_id}/history", response_model=List[CittaMomentResponse])
async def get_citta_history(
    model_id: str,
    limit: int = 100,
    offset: int = 0,
    category_filter: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
):
    """
    Get citta moment history for a character.
    
    Retrieves recorded citta moments with optional filtering.
    
    Args:
        model_id: Character ID
        limit: Maximum number of records to return
        offset: Pagination offset
        category_filter: Filter by category (Kusala/Akusala/Abyakata)
        start_time: Filter from this time
        end_time: Filter until this time
    
    Returns:
        List of CittaMomentResponse
    
    Example:
        GET /api/citta-cetasika/123/history?limit=50&category_filter=Kusala
    """
    # Build query filters
    query_filters: Dict[str, Any] = {"model_id": model_id}
    
    # Optional filters
    if category_filter:
        query_filters["category"] = category_filter
    
    if start_time:
        query_filters["timestamp"] = {"$gte": start_time}
    
    if end_time:
        if "timestamp" in query_filters:
            query_filters["timestamp"]["$lte"] = end_time
        else:
            query_filters["timestamp"] = {"$lte": end_time}
    
    # Query database with pagination
    citta_records = await CittaMomentRecord.find(
        query_filters
    ).sort("-timestamp").skip(offset).limit(limit).to_list()
    
    # Convert to response format
    results = []
    for record in citta_records:
        results.append(CittaMomentResponse(
            citta_type=record.citta_type,
            category=record.category,
            root=record.root,
            feeling=record.feeling,
            intensity=record.intensity,
            cetasikas=record.cetasikas,
            prompted=record.prompted,
            accompanied_by_knowledge=record.accompanied_by_knowledge,
            duration_ms=record.duration_ms,
            timestamp=record.timestamp,
            context=record.context
        ))
    
    return results


@router.get("/{model_id}/recent-moments", response_model=List[CittaMomentResponse])
async def get_recent_moments(
    model_id: str,
    limit: int = Query(10, ge=1, le=100, description="Number of recent moments to retrieve")
):
    """
    Get most recent citta moments for a character.
    
    Returns the latest recorded consciousness moments in descending order.
    
    Args:
        model_id: Character ID
        limit: Maximum number of moments (default: 10, max: 100)
    
    Returns:
        List of recent CittaMomentResponse
    
    Example:
        GET /api/citta-cetasika/peace-mind-001/recent-moments?limit=5
    """
    # Query most recent moments
    citta_records = await CittaMomentRecord.find(
        {"model_id": model_id}
    ).sort("-timestamp").limit(limit).to_list()
    
    # Convert to response format
    results = []
    for record in citta_records:
        results.append(CittaMomentResponse(
            citta_type=record.citta_type,
            category=record.category,
            root=record.root,
            feeling=record.feeling,
            intensity=record.intensity,
            cetasikas=record.cetasikas,
            prompted=record.prompted,
            accompanied_by_knowledge=record.accompanied_by_knowledge,
            duration_ms=record.duration_ms,
            timestamp=record.timestamp,
            context=record.context
        ))
    
    return results


# ============================================================================
# POST Endpoints
# ============================================================================

class RecordCittaMomentRequest(BaseModel):
    """Request to record a new citta moment"""
    citta_type: str = Field(..., description="Citta type (e.g., 'lobha-mula-citta-1')")
    feeling: str = Field(..., description="Vedanā: sukha/dukkha/upekkha")
    intensity: float = Field(5.0, ge=0.0, le=10.0, description="Strength (0-10)")
    prompted: bool = Field(False, description="Whether prompted by conditions")
    with_knowledge: bool = Field(False, description="Accompanied by wisdom")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

@router.post("/{model_id}/record-moment", response_model=CittaMomentResponse)
async def record_citta_moment(
    model_id: str,
    request: RecordCittaMomentRequest
):
    """
    Record a new citta moment for a character.
    
    This creates a record of a consciousness moment with its cetasikas.
    If this is a javana (impulsion) moment, it may trigger kamma creation.
    
    Args:
        model_id: Character ID
        request: CittaMomentRequest with citta details
    
    Returns:
        CittaMomentResponse with the recorded moment
    
    Example:
        POST /api/citta-cetasika/123/record-moment
        {
            "citta_type": "lobha-mula-citta-1",
            "feeling": "sukha",
            "intensity": 7.5,
            "prompted": false,
            "with_knowledge": false,
            "context": {"trigger": "seeing beautiful object"}
        }
    """
    # Import documents
    from documents import DigitalMindModel, MindState, CittaMomentRecord, KammaLogEntry
    
    # Validate character exists
    character = await DigitalMindModel.get(model_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character {model_id} not found"
        )
    
    # Load citta definitions to get category and root
    cittas = load_cittas_from_json()
    citta_def = None
    for c in cittas:
        if hasattr(c, 'id') and c.id == request.citta_type:
            citta_def = c
            break
    
    # Determine citta category and root
    category = "Abyakata"
    root = None
    if citta_def:
        if hasattr(citta_def, 'category'):
            category = str(citta_def.category.value) if hasattr(citta_def.category, 'value') else str(citta_def.category)
        if hasattr(citta_def, 'root'):
            root = str(citta_def.root.value) if hasattr(citta_def.root, 'value') else str(citta_def.root)
    else:
        # Infer from citta_type name
        if "lobha" in request.citta_type.lower():
            category = "Akusala"
            root = "lobha"
        elif "dosa" in request.citta_type.lower():
            category = "Akusala"
            root = "dosa"
        elif "kusala" in request.citta_type.lower():
            category = "Kusala"
            root = "alobha"
    
    # Determine accompanying cetasikas
    cetasikas = ["phassa", "vedana", "sanna", "cetana", "ekaggata", "jivitindriya", "manasikara"]  # 7 universals
    
    # Add root-specific cetasikas
    if root in ["lobha"]:
        cetasikas.extend(["lobha", "moha"])
    elif root in ["dosa"]:
        cetasikas.extend(["dosa", "moha"])
    elif root in ["moha"]:
        cetasikas.extend(["moha", "vicikiccha"])
    elif root in ["alobha", "adosa", "amoha"]:
        cetasikas.extend(["alobha", "adosa", "amoha", "saddha", "sati"])
        if request.with_knowledge:
            cetasikas.append("panna")
    
    # Create citta moment record
    citta_moment = CittaMomentRecord(
        model_id=model_id,
        citta_type=request.citta_type,
        category=category,
        root=root,
        feeling=request.feeling,
        intensity=request.intensity,
        cetasikas=cetasikas,
        prompted=request.prompted,
        accompanied_by_knowledge=request.with_knowledge,
        duration_ms=17,
        context=request.context,
        timestamp=datetime.now(),
        is_javana=True,  # Assume javana for kamma creation
        kamma_created=False
    )
    
    # If this is a javana moment and akusala/kusala, create kamma
    kamma_log_id = None
    if citta_moment.is_javana and category in ["Kusala", "Akusala"]:
        # Update mind state counters
        mind_state = await MindState.find_one({"user_id": model_id})
        if mind_state:
            if category == "Kusala":
                mind_state.kusala_count_today += 1
                mind_state.kusala_count_total += 1
            else:
                mind_state.akusala_count_today += 1
                mind_state.akusala_count_total += 1
            mind_state.updated_at = datetime.utcnow()
            await mind_state.save()
        
        # Create kamma log entry
        kamma_entry = KammaLogEntry(
            model_id=model_id,
            kamma_type="kusala" if category == "Kusala" else "akusala",
            action_description=f"Citta moment: {request.citta_type}",
            intensity=request.intensity,
            timestamp=datetime.utcnow()
        )
        await kamma_entry.insert()
        kamma_log_id = str(kamma_entry.id)
        
        citta_moment.kamma_created = True
        citta_moment.kamma_log_id = kamma_log_id
    
    # Save citta moment
    await citta_moment.insert()
    
    return CittaMomentResponse(
        timestamp=citta_moment.timestamp,
        citta_type=citta_moment.citta_type,
        category=citta_moment.category,
        feeling=citta_moment.feeling,
        root=citta_moment.root,
        prompted=citta_moment.prompted,
        accompanied_by_knowledge=citta_moment.accompanied_by_knowledge,
        cetasikas=citta_moment.cetasikas,
        intensity=citta_moment.intensity,
        duration_ms=citta_moment.duration_ms,
        context=citta_moment.context
    )

class SimulateCittaVithiRequest(BaseModel):
    """Request to simulate a mind-door process"""
    sense_object: str = Field(..., description="The object presented to consciousness")
    door: str = Field("eye", description="Sense door: eye/ear/nose/tongue/body/mind")
    character_state: Dict[str, Any] = Field(..., description="Current character state")

@router.post("/{model_id}/simulate-vithi", response_model=CittaVithiResponse)
async def simulate_citta_vithi(
    model_id: str,
    request: SimulateCittaVithiRequest
):
    """
    Simulate a complete citta vīthi (mind-door process).
    
    This simulates the entire sequence from sense-door adverting
    through javana (impulsion) to registration, showing which
    cittas arise at each stage.
    
    Args:
        model_id: Character ID
        request: SimulateCittaVithiRequest with sense object and door
    
    Returns:
        CittaVithiResponse with complete process sequence
    
    Example:
        POST /api/citta-cetasika/123/simulate-vithi
        {
            "sense_object": "beautiful flower",
            "door": "eye",
            "character_state": {"path_stage": "Puthujjana"}
        }
    """
    # Import modules
    from documents import DigitalMindModel, MindState
    from modules.citta_vithi_engine import (
        ChittaVithiGenerator, SensoryInput, VedanaType, DvaraType, AramanaType
    )
    
    # Get character data
    character = await DigitalMindModel.get(model_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character {model_id} not found"
        )
    
    mind_state = await MindState.find_one({"user_id": model_id})
    if not mind_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mind state for {model_id} not found"
        )
    
    # Prepare inputs for vithi generator
    # Map sense door to DvaraType
    door_map = {
        "eye": DvaraType.CAKKHU,
        "ear": DvaraType.SOTA,
        "nose": DvaraType.GHANA,
        "tongue": DvaraType.JIVHA,
        "body": DvaraType.KAYA,
        "mind": DvaraType.MANO
    }
    dvara = door_map.get(request.door, DvaraType.CAKKHU)
    
    # Determine aramana type and vedana from sense door
    aramana_map = {
        "eye": AramanaType.RUPA,
        "ear": AramanaType.SADDA,
        "nose": AramanaType.GANDHA,
        "tongue": AramanaType.RASA,
        "body": AramanaType.PHOTTHABBA,
        "mind": AramanaType.DHAMMĀRAMMAṆA
    }
    aramana_type = aramana_map.get(request.door, AramanaType.RUPA)
    
    # Determine vedana from object description (simple heuristic)
    if any(word in request.sense_object.lower() for word in ["beautiful", "pleasant", "lovely", "attractive"]):
        vedana = VedanaType.SUKHA
    elif any(word in request.sense_object.lower() for word in ["ugly", "painful", "unpleasant", "disgusting"]):
        vedana = VedanaType.DUKKHA
    else:
        vedana = VedanaType.UPEKKHA
    
    # Create sensory input
    sensory_input = SensoryInput(
        dvara=dvara,
        aramana_type=aramana_type,
        aramana_description=request.sense_object,
        natural_vedana=vedana,
        intensity=7.0
    )
    
    # Prepare anusaya levels
    anusaya_levels = {
        "kama_raga": mind_state.current_anusaya.get("lobha", 3.0),
        "patigha": mind_state.current_anusaya.get("dosa", 2.5),
        "mana": mind_state.current_anusaya.get("mana", 2.0),
        "ditthi": mind_state.current_anusaya.get("ditthi", 2.0),
        "vicikiccha": mind_state.current_anusaya.get("vicikiccha", 2.5),
        "bhava_raga": mind_state.current_anusaya.get("lobha", 3.0) * 0.8,
        "avijja": mind_state.current_anusaya.get("moha", 3.5)
    }
    
    # Prepare virtue level
    virtue_level = {
        "sila": mind_state.sila,
        "samadhi": mind_state.samadhi,
        "panna": mind_state.panna
    }
    
    # Active hindrances
    active_hindrances = mind_state.active_hindrances
    
    # Generate vithi
    generator = ChittaVithiGenerator()
    vithi_sequence = generator.generate_eye_door_vithi(
        sensory_input=sensory_input,
        anusaya_levels=anusaya_levels,
        virtue_level=virtue_level,
        active_hindrances=active_hindrances
    )
    
    # Convert to response format
    stages = []
    for i, moment in enumerate(vithi_sequence.citta_moments):
        stage_data = {
            "name": f"{moment.citta_type.value}-{i+1}",
            "citta": moment.citta_type.value,
            "duration_ms": 17
        }
        if "ชวนะ" in moment.notes or "Javana" in moment.notes:
            stage_data["kamma"] = True
        stages.append(stage_data)
    
    return CittaVithiResponse(
        vithi_id=f"vithi_{model_id}_{datetime.now().timestamp()}",
        object_presented=request.sense_object,
        door=request.door,
        stages=stages,
        javana_count=7,
        kamma_created=vithi_sequence.javana_decision.quality in ["kusala", "akusala"],
        total_duration_ms=vithi_sequence.duration_ms * 1000,
        result=f"{vithi_sequence.javana_decision.quality.title()} kamma recorded"
    )

# ============================================================================
# Utility Endpoints
# ============================================================================

@router.get("/cittas", response_model=List[Dict[str, Any]])
async def list_all_cittas():
    """
    List all 89 citta definitions.
    
    Returns complete information about all consciousness types
    from the Abhidhamma classification.
    
    Returns:
        List of citta definitions
    
    Example:
        GET /api/citta-cetasika/cittas
    """
    cittas = load_cittas_from_json()
    return [citta.dict() for citta in cittas]

@router.get("/cetasikas", response_model=List[Dict[str, Any]])
async def list_all_cetasikas():
    """
    List all 52 cetasika definitions.
    
    Returns complete information about all mental factors
    from the Abhidhamma classification.
    
    Returns:
        List of cetasika definitions
    
    Example:
        GET /api/citta-cetasika/cetasikas
    """
    cetasikas = load_cetasikas_from_json()
    return [cetasika.dict() for cetasika in cetasikas]

@router.get("/combinations/{citta_type}", response_model=Dict[str, Any])
async def get_citta_cetasika_combinations(citta_type: str):
    """
    Get which cetasikas can combine with a specific citta type.
    
    Shows the valid cetasika combinations for a given citta,
    following Abhidhamma combination rules.
    
    Args:
        citta_type: Citta identifier (e.g., 'lobha-mula-citta-1')
    
    Returns:
        Dictionary with cetasika combination info
    
    Example:
        GET /api/citta-cetasika/combinations/lobha-mula-citta-1
    """
    # Load citta and cetasika definitions
    cittas = load_cittas_from_json()
    cetasikas = load_cetasikas_from_json()
    
    # Find the requested citta
    citta_def = None
    for c in cittas:
        if hasattr(c, 'id') and c.id == citta_type:
            citta_def = c
            break
        elif hasattr(c, 'name_pali') and citta_type in str(c.name_pali):
            citta_def = c
            break
    
    # Universal cetasikas (always present in every citta)
    universal = ["phassa", "vedana", "sanna", "cetana", "ekaggata", "jivitindriya", "manasikara"]
    
    # Determine required and optional cetasikas based on citta type
    required = []
    optional = []
    forbidden = []
    
    # Buddhist Abhidhamma combination rules
    if "lobha" in citta_type.lower():
        # Lobha-mūla-citta (Greed-rooted)
        required = ["lobha", "moha"]  # Always has greed + delusion
        optional = ["thina", "middha", "uddhacca", "kukkucca"]  # May have hindrances
        forbidden = ["alobha", "adosa", "amoha", "saddha", "sati", "hiri", "ottappa"]  # Cannot have beautiful factors
        
    elif "dosa" in citta_type.lower():
        # Dosa-mūla-citta (Hatred-rooted)
        required = ["dosa", "moha"]  # Always has hatred + delusion
        optional = ["issa", "macchariya", "kukkucca", "thina", "middha", "uddhacca"]
        forbidden = ["alobha", "adosa", "amoha", "saddha", "sati", "metta", "karuna"]
        
    elif "moha" in citta_type.lower():
        # Moha-mūla-citta (Delusion-rooted)
        required = ["moha", "vicikiccha"]  # Always has delusion + doubt
        optional = ["thina", "middha"]
        forbidden = ["alobha", "adosa", "amoha", "saddha", "panna", "yoniso-manasikara"]
        
    elif "kusala" in citta_type.lower():
        # Kusala-citta (Wholesome)
        required = ["alobha", "adosa", "amoha"]  # Three beautiful roots
        optional = ["saddha", "sati", "hiri", "ottappa", "panna", "karuna", "mudita"]
        forbidden = ["lobha", "dosa", "moha", "issa", "macchariya", "thina", "middha", "uddhacca", "kukkucca"]
        
    elif "vipaka" in citta_type.lower():
        # Vipāka-citta (Resultant)
        required = []  # No required akusala/kusala factors
        optional = ["vitakka", "vicara", "piti", "sukha"]
        forbidden = []  # Vipaka has no moral quality
        
    elif "kiriya" in citta_type.lower():
        # Kiriya-citta (Functional - Arahant only)
        required = ["alobha", "adosa", "amoha"]
        optional = ["saddha", "sati", "panna"]
        forbidden = ["lobha", "dosa", "moha", "issa", "macchariya"]
    
    else:
        # Default for unknown types
        required = []
        optional = ["vitakka", "vicara"]
        forbidden = []
    
    # Add citta-specific information if found
    category = "Unknown"
    if citta_def:
        if hasattr(citta_def, 'category'):
            category = str(citta_def.category.value) if hasattr(citta_def.category, 'value') else str(citta_def.category)
    
    return {
        "citta_type": citta_type,
        "category": category,
        "universal": universal,
        "required": required,
        "optional": optional,
        "forbidden": forbidden,
        "total_min": len(universal) + len(required),
        "total_max": len(universal) + len(required) + len(optional),
        "rules": {
            "universal_always_present": "7 universal cetasikas always arise with every citta",
            "akusala_roots": "Akusala citta must have at least 1 unwholesome root (lobha/dosa/moha)",
            "kusala_roots": "Kusala citta must have 3 beautiful roots (alobha/adosa/amoha)",
            "mutual_exclusion": "Kusala and akusala cetasikas cannot coexist",
            "hetu_count": "Citta can be ahetuka (0), dvihetuka (2), or tihetuka (3) roots"
        }
    }

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "citta-cetasika-engine",
        "version": "1.0.0",
        "cittas_loaded": len(load_cittas_from_json()),
        "cetasikas_loaded": len(load_cetasikas_from_json())
    }
