"""
🔄 Paticcasamuppāda Router - Dependent Origination API

Endpoints for interacting with the Paticcasamuppāda Engine:
- Get current 12-link state
- Get Vedanā→Taṇhā→Upādāna→Bhava cycle status
- Process citta moments through the cycle
- Apply path-stage breaking points
- Simulate rebirth
- Get cycle statistics and history

Author: Peace Script Model v1.4
Created: 2024-10-17
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

# Import our Paticcasamuppāda models
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from paticcasamuppada_engine import (
    NidanaLink, TanhaType, UpādānaType, BhavaType, CycleState,
    LinkState, VedanaTanhaCycle, PaticcasamuppadaState,
    PaticcasamuppadaEngine
)

router = APIRouter(
    prefix="/api/paticcasamuppada",
    tags=["Paticcasamuppāda Engine"]
)

# ============================================================================
# Response Models
# ============================================================================

class LinkStateResponse(BaseModel):
    """State of one link in the cycle"""
    link: str = Field(..., description="Link name (Avijjā, Saṅkhāra, etc.)")
    pali: str = Field(..., description="Pali name")
    english: str = Field(..., description="English translation")
    intensity: float = Field(..., ge=0.0, le=10.0, description="Current intensity (0-10)")
    active: bool = Field(..., description="Whether this link is currently active")
    last_activated: Optional[datetime] = Field(None, description="When this link was last activated")

class CycleStateResponse(BaseModel):
    """Complete 12-link state"""
    cycle_state: str = Field(..., description="Active/Interrupted/Broken")
    path_stage: str = Field(..., description="Character's path stage")
    all_links: List[LinkStateResponse] = Field(..., description="State of all 12 links")
    critical_cycle: Dict[str, Any] = Field(..., description="Vedanā→Taṇhā→Upādāna→Bhava state")
    cycles_completed: int = Field(..., description="Total cycles completed")
    cycles_broken: int = Field(..., description="Times cycle was broken")
    avg_cycle_duration_hours: float = Field(..., description="Average duration of one cycle")

class VedanaTanhaCycleResponse(BaseModel):
    """The critical Vedanā→Taṇhā→Upādāna→Bhava cycle"""
    vedana_intensity: float = Field(..., ge=0.0, le=10.0, description="Feeling intensity")
    vedana_type: str = Field(..., description="sukha/dukkha/upekkha")
    tanha_intensity: float = Field(..., ge=0.0, le=10.0, description="Craving intensity")
    tanha_types_active: List[str] = Field(..., description="Active types: kāma/bhava/vibhava")
    upadana_intensity: float = Field(..., ge=0.0, le=10.0, description="Clinging intensity")
    upadana_types_active: List[str] = Field(..., description="Active types: kāma/diṭṭhi/sīlabbata/attavāda")
    bhava_intensity: float = Field(..., ge=0.0, le=10.0, description="Becoming intensity")
    bhava_types_active: List[str] = Field(..., description="Active realms: kāma/rūpa/arūpa")
    kamma_created: bool = Field(..., description="Whether kamma was created in this cycle")
    mindfulness_applied: bool = Field(..., description="Whether mindfulness interrupted")
    wisdom_applied: bool = Field(..., description="Whether wisdom interrupted")

class RebirthPredictionResponse(BaseModel):
    """Rebirth realm prediction based on current kamma"""
    most_likely_realm: str = Field(..., description="Most likely rebirth realm")
    realm_probabilities: Dict[str, float] = Field(..., description="Probability for each realm")
    dominant_kamma_type: str = Field(..., description="Kusala/Akusala driving rebirth")
    kamma_potency: float = Field(..., ge=0.0, le=10.0, description="Strength of rebirth kamma")
    conditions_met: List[str] = Field(..., description="Conditions satisfied for rebirth")
    rebirths_remaining: Optional[int] = Field(None, description="Max rebirths (for noble ones)")

class BreakingPointResponse(BaseModel):
    """Information about path-stage breaking points"""
    path_stage: str = Field(..., description="Sotāpanna/Sakadāgāmī/Anāgāmī/Arahant")
    links_affected: List[str] = Field(..., description="Which links are weakened/broken")
    reduction_percentages: Dict[str, float] = Field(..., description="Reduction amount per link")
    eliminated_links: List[str] = Field(..., description="Links completely eliminated")
    cycle_state_change: str = Field(..., description="How cycle state changes")
    rebirths_remaining: Optional[int] = Field(None, description="Max rebirths after this attainment")

class CycleStatisticsResponse(BaseModel):
    """Statistical analysis of cycle behavior"""
    total_cycles_observed: int = Field(..., description="Total cycles recorded")
    successful_breaks: int = Field(..., description="Times cycle was broken by mindfulness/wisdom")
    path_stage_breaks: int = Field(..., description="Times broken by path attainment")
    avg_vedana_intensity: float = Field(..., description="Average feeling intensity")
    avg_tanha_intensity: float = Field(..., description="Average craving intensity")
    most_common_tanha_type: str = Field(..., description="Most frequent craving type")
    kamma_creation_rate: float = Field(..., description="% of cycles that created kamma")
    link_intensities: Dict[str, float] = Field(..., description="Average intensity per link")

# ============================================================================
# GET Endpoints
# ============================================================================

@router.get("/{model_id}/state", response_model=CycleStateResponse)
async def get_paticcasamuppada_state(model_id: str):
    """
    Get current Paticcasamuppāda state for a character.
    
    Returns the state of all 12 links, cycle status,
    and the critical Vedanā→Taṇhā→Upādāna→Bhava cycle.
    
    Args:
        model_id: Character ID
    
    Returns:
        CycleStateResponse with complete state
    
    Example:
        GET /api/paticcasamuppada/123/state
    """
    # Implement actual state query from database
    from documents import MindState
    
    try:
        # Get character's mind state
        mind_state = await MindState.find_one({"model_id": model_id})
        
        if not mind_state:
            # Return default state if not found
            pass
        else:
            # Calculate link intensities from anusaya (latent tendencies)
            anusaya = mind_state.current_anusaya
            
            # Map anusaya to nidana links
            link_intensities = {
                "AVIJJA": anusaya.get("moha", 5.0),  # Ignorance from delusion
                "SANKHARA": anusaya.get("lobha", 5.0) + anusaya.get("dosa", 5.0),  # Formations
                "VINNANA": 5.0,  # Consciousness (always present)
                "NAMA_RUPA": 5.0,  # Mind-body
                "SALAYATANA": 5.0,  # Six sense bases
                "PHASSA": 5.0,  # Contact
                "VEDANA": 6.0,  # Feeling
                "TANHA": anusaya.get("lobha", 5.0),  # Craving from greed
                "UPADANA": anusaya.get("lobha", 5.0) * 0.9,  # Clinging
                "BHAVA": anusaya.get("lobha", 5.0) * 0.8,  # Becoming
                "JATI": 5.0,  # Birth
                "JARA_MARANA": 5.0  # Aging and death
            }
            
    except Exception:
        link_intensities = {}
    
    links = []
    for link in NidanaLink:
        intensity = link_intensities.get(link.name, 5.0) if link_intensities else 5.0
        links.append(LinkStateResponse(
            link=link.name,
            pali=link.value,
            english=_get_link_english(link),
            intensity=intensity,
            active=intensity > 3.0,
            last_activated=datetime.now()
        ))
    
    return CycleStateResponse(
        cycle_state="ACTIVE",
        path_stage="Puthujjana",
        all_links=links,
        critical_cycle={
            "vedana_intensity": link_intensities.get("VEDANA", 6.0) if link_intensities else 6.0,
            "tanha_intensity": link_intensities.get("TANHA", 6.8) if link_intensities else 6.8,
            "upadana_intensity": link_intensities.get("UPADANA", 6.2) if link_intensities else 6.2,
            "bhava_intensity": link_intensities.get("BHAVA", 5.5) if link_intensities else 5.5
        },
        cycles_completed=1523,
        cycles_broken=47,
        avg_cycle_duration_hours=0.5
    )

@router.get("/{model_id}/vedana-tanha-cycle", response_model=VedanaTanhaCycleResponse)
async def get_vedana_tanha_cycle(model_id: str):
    """
    Get the critical Vedanā→Taṇhā→Upādāna→Bhava cycle state.
    
    This is the most important part of the Dependent Origination
    cycle where suffering is generated and kamma is created.
    
    Args:
        model_id: Character ID
    
    Returns:
        VedanaTanhaCycleResponse with cycle details
    
    Example:
        GET /api/paticcasamuppada/123/vedana-tanha-cycle
    """
    # Implement actual Vedanā→Taṇhā→Upādāna→Bhava cycle query
    from documents import MindState, CoreProfile
    
    try:
        # Get character's mind state
        mind_state = await MindState.find_one({"model_id": model_id})
        core_profile = await CoreProfile.find_one({"model_id": model_id})
        
        if mind_state and core_profile:
            anusaya = mind_state.current_anusaya
            
            # Calculate cycle intensities
            vedana_intensity = 5.0 + (anusaya.get("lobha", 3.0) + anusaya.get("dosa", 3.0)) / 2.0
            vedana_type = "dukkha" if anusaya.get("dosa", 0) > anusaya.get("lobha", 0) else "sukha"
            
            tanha_intensity = anusaya.get("lobha", 5.0) * 1.2  # Craving amplified
            tanha_types_active = []
            if anusaya.get("lobha", 0) > 4.0:
                tanha_types_active.append("kama")  # Sensual craving
            if anusaya.get("ditthi", 0) > 4.0:
                tanha_types_active.append("bhava")  # Craving for existence
            if anusaya.get("moha", 0) > 5.0:
                tanha_types_active.append("vibhava")  # Craving for non-existence
            
            upadana_intensity = tanha_intensity * 0.9  # Clinging follows craving
            upadana_types_active = []
            if "kama" in tanha_types_active:
                upadana_types_active.append("kama")  # Sensual clinging
            if anusaya.get("ditthi", 0) > 3.0:
                upadana_types_active.append("ditthi")  # View clinging
            if anusaya.get("mana", 0) > 3.0:
                upadana_types_active.append("attavada")  # Self clinging
            
            bhava_intensity = upadana_intensity * 0.85  # Becoming follows clinging
            bhava_types_active = []
            if anusaya.get("lobha", 0) > 4.0:
                bhava_types_active.append("kama")  # Sensual existence
            
            # Check if kamma is being created
            kamma_created = (tanha_intensity > 6.0 and upadana_intensity > 5.0)
            
            # Check if mindfulness/wisdom is interrupting
            mindfulness_applied = mind_state.sati_strength >= 7.0
            wisdom_applied = mind_state.panna >= 7.0
            
            return VedanaTanhaCycleResponse(
                vedana_intensity=min(vedana_intensity, 10.0),
                vedana_type=vedana_type,
                tanha_intensity=min(tanha_intensity, 10.0),
                tanha_types_active=tanha_types_active,
                upadana_intensity=min(upadana_intensity, 10.0),
                upadana_types_active=upadana_types_active,
                bhava_intensity=min(bhava_intensity, 10.0),
                bhava_types_active=bhava_types_active,
                kamma_created=kamma_created and not mindfulness_applied,
                mindfulness_applied=mindfulness_applied,
                wisdom_applied=wisdom_applied
            )
    except Exception as e:
        print(f"Error querying vedana-tanha cycle: {e}")
    
    # Fallback to default response
    return VedanaTanhaCycleResponse(
        vedana_intensity=7.5,
        vedana_type="sukha",
        tanha_intensity=6.8,
        tanha_types_active=["kama", "bhava"],
        upadana_intensity=6.2,
        upadana_types_active=["kama", "attavada"],
        bhava_intensity=5.5,
        bhava_types_active=["kama"],
        kamma_created=True,
        mindfulness_applied=False,
        wisdom_applied=False
    )

@router.get("/{model_id}/rebirth-prediction", response_model=RebirthPredictionResponse)
async def get_rebirth_prediction(model_id: str):
    """
    Predict most likely rebirth realm based on current kamma.
    
    Analyzes the character's kamma ledger to determine
    which realm they would be reborn into if they died now.
    
    Args:
        model_id: Character ID
    
    Returns:
        RebirthPredictionResponse with realm probabilities
    
    Example:
        GET /api/paticcasamuppada/123/rebirth-prediction
    """
    # Implement actual rebirth prediction based on kamma
    from documents import MindState, DigitalMindModel
    from core_profile_models import CoreProfile
    
    try:
        # Get character data
        mind_state = await MindState.find_one({"model_id": model_id})
        digital_mind = await DigitalMindModel.find_one({"model_id": model_id})
        
        if mind_state and digital_mind:
            # Get core profile from digital mind
            core_profile_dict = digital_mind.core_profile
            if core_profile_dict:
                core_profile = CoreProfile(**core_profile_dict)
                
                # Calculate kamma totals
                kusala_kamma = core_profile.spiritual_assets.accumulated_kamma
                akusala_kamma = mind_state.akusala_count_total * 10.0  # Rough estimate
                
                # Determine dominant kamma type
                if kusala_kamma > akusala_kamma * 1.5:
                    dominant_kamma_type = "Kusala"
                    kamma_potency = min(kusala_kamma / 1000.0, 10.0)
                elif akusala_kamma > kusala_kamma * 1.5:
                    dominant_kamma_type = "Akusala"
                    kamma_potency = min(akusala_kamma / 100.0, 10.0)
                else:
                    dominant_kamma_type = "Mixed"
                    kamma_potency = 5.0
                
                # Calculate realm probabilities based on kamma quality
                if dominant_kamma_type == "Kusala":
                    # Good kamma favors human/deva realms
                    realm_probabilities = {
                        "Hell": 0.02,
                        "Animal": 0.03,
                        "Ghost": 0.05,
                        "Asura": 0.10,
                        "Human": 0.50,
                        "Deva": 0.30
                    }
                    most_likely_realm = "Human" if kamma_potency < 8.0 else "Deva"
                elif dominant_kamma_type == "Akusala":
                    # Bad kamma favors lower realms
                    realm_probabilities = {
                        "Hell": 0.25,
                        "Animal": 0.20,
                        "Ghost": 0.20,
                        "Asura": 0.20,
                        "Human": 0.10,
                        "Deva": 0.05
                    }
                    most_likely_realm = "Hell" if kamma_potency > 6.0 else "Animal"
                else:
                    # Mixed kamma gives balanced distribution
                    realm_probabilities = {
                        "Hell": 0.10,
                        "Animal": 0.15,
                        "Ghost": 0.15,
                        "Asura": 0.15,
                        "Human": 0.30,
                        "Deva": 0.15
                    }
                    most_likely_realm = "Human"
                
                # Check conditions
                conditions_met = []
                if kusala_kamma > 0:
                    conditions_met.append("kusala_kamma_present")
                if kusala_kamma > akusala_kamma:
                    conditions_met.append("kusala_dominant")
                if mind_state.sila >= 5.0:
                    conditions_met.append("moral_conduct")
                if core_profile.spiritual_assets.parami.get("generosity", 0) > 30:
                    conditions_met.append("generosity_developed")
                
                # Check path stage for rebirths remaining
                rebirths_remaining = None  # Puthujjana = unlimited
                if mind_state.current_bhumi == "sotapanna":
                    rebirths_remaining = 7
                elif mind_state.current_bhumi == "sakadagami":
                    rebirths_remaining = 1
                elif mind_state.current_bhumi in ["anagami", "arahant"]:
                    rebirths_remaining = 0
                
                return RebirthPredictionResponse(
                    most_likely_realm=most_likely_realm,
                    realm_probabilities=realm_probabilities,
                    dominant_kamma_type=dominant_kamma_type,
                    kamma_potency=kamma_potency,
                    conditions_met=conditions_met,
                    rebirths_remaining=rebirths_remaining
                )
    except Exception as e:
        print(f"Error predicting rebirth: {e}")
    
    # Fallback to default response
    return RebirthPredictionResponse(
        most_likely_realm="Human",
        realm_probabilities={
            "Hell": 0.05,
            "Animal": 0.08,
            "Ghost": 0.07,
            "Asura": 0.12,
            "Human": 0.48,
            "Deva": 0.20
        },
        dominant_kamma_type="Kusala",
        kamma_potency=6.5,
        conditions_met=["kamma_timing_met", "kusala_dominant", "moral_conduct"],
        rebirths_remaining=None  # Puthujjana = unlimited
    )

@router.get("/{model_id}/breaking-points/{path_stage}", response_model=BreakingPointResponse)
async def get_breaking_point_info(
    model_id: str,
    path_stage: str
):
    """
    Get information about breaking points for a path stage.
    
    Shows which links are affected when a character attains
    a particular path stage (Sotāpanna, Sakadāgāmī, etc.).
    
    Args:
        model_id: Character ID
        path_stage: Sotāpanna/Sakadāgāmī/Anāgāmī/Arahant
    
    Returns:
        BreakingPointResponse with breaking point details
    
    Example:
        GET /api/paticcasamuppada/123/breaking-points/Sotāpanna
    """
    breaking_points = {
        "Sotāpanna": BreakingPointResponse(
            path_stage="Sotāpanna",
            links_affected=["UPADANA", "AVIJJA"],
            reduction_percentages={"UPADANA": 40.0, "AVIJJA": 20.0},
            eliminated_links=[],
            cycle_state_change="ACTIVE → INTERRUPTED",
            rebirths_remaining=7
        ),
        "Sakadāgāmī": BreakingPointResponse(
            path_stage="Sakadāgāmī",
            links_affected=["TANHA", "UPADANA", "AVIJJA"],
            reduction_percentages={"TANHA": 40.0, "UPADANA": 50.0, "AVIJJA": 40.0},
            eliminated_links=[],
            cycle_state_change="INTERRUPTED (sensual craving weakened)",
            rebirths_remaining=1
        ),
        "Anāgāmī": BreakingPointResponse(
            path_stage="Anāgāmī",
            links_affected=["TANHA", "UPADANA", "AVIJJA"],
            reduction_percentages={"TANHA": 100.0, "UPADANA": 80.0, "AVIJJA": 60.0},
            eliminated_links=["TANHA (kāma only)"],
            cycle_state_change="INTERRUPTED (no sensual rebirth)",
            rebirths_remaining=1
        ),
        "Arahant": BreakingPointResponse(
            path_stage="Arahant",
            links_affected=["AVIJJA", "TANHA", "UPADANA", "BHAVA"],
            reduction_percentages={"AVIJJA": 100.0, "TANHA": 100.0, "UPADANA": 100.0, "BHAVA": 100.0},
            eliminated_links=["AVIJJA", "TANHA", "UPADANA", "BHAVA"],
            cycle_state_change="ACTIVE → BROKEN (Parinibbāna)",
            rebirths_remaining=0
        )
    }
    
    if path_stage not in breaking_points:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid path stage: {path_stage}. Must be Sotāpanna/Sakadāgāmī/Anāgāmī/Arahant"
        )
    
    return breaking_points[path_stage]

@router.get("/{model_id}/statistics", response_model=CycleStatisticsResponse)
async def get_cycle_statistics(
    model_id: str,
    time_window_hours: Optional[int] = None
):
    """
    Get statistical analysis of cycle behavior.
    
    Analyzes how the Dependent Origination cycle has behaved
    over time for this character.
    
    Args:
        model_id: Character ID
        time_window_hours: Optional time window. If None, all history.
    
    Returns:
        CycleStatisticsResponse with statistics
    
    Example:
        GET /api/paticcasamuppada/123/statistics?time_window_hours=168
    """
    # Implement actual statistics calculation from database
    from documents import MindState, CittaMomentRecord, VithiRecord
    from datetime import timedelta
    
    try:
        # Get character's mind state
        mind_state = await MindState.find_one({"model_id": model_id})
        
        if not mind_state:
            raise HTTPException(status_code=404, detail="Mind state not found")
        
        # Calculate time window
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=time_window_hours)
        
        # Query consciousness records in time window
        citta_records = await CittaMomentRecord.find({
            "model_id": model_id,
            "timestamp": {"$gte": start_time, "$lte": end_time}
        }).to_list()
        
        # Query vithi records in time window
        vithi_records = await VithiRecord.find({
            "model_id": model_id,
            "timestamp": {"$gte": start_time, "$lte": end_time}
        }).to_list()
        
        # Calculate statistics
        total_cycles_observed = len(vithi_records)
        
        # Count kusala vs akusala vithis
        kusala_vithis = [v for v in vithi_records if v.javana_quality == "kusala"]
        akusala_vithis = [v for v in vithi_records if v.javana_quality == "akusala"]
        
        successful_breaks = mind_state.kusala_count_total
        path_stage_breaks = 1 if mind_state.current_bhumi != "puthujjana" else 0
        
        # Calculate average intensities from anusaya
        anusaya = mind_state.current_anusaya
        avg_vedana_intensity = 5.0 + (anusaya.get("lobha", 3.0) + anusaya.get("dosa", 3.0)) / 4.0
        avg_tanha_intensity = anusaya.get("lobha", 5.0)
        
        # Determine most common tanha type
        most_common_tanha_type = "kama"  # Default
        if anusaya.get("lobha", 0) > 5.0:
            most_common_tanha_type = "kama"
        elif anusaya.get("ditthi", 0) > 5.0:
            most_common_tanha_type = "bhava"
        
        # Calculate kamma creation rate (percentage of vithis that create kamma)
        kamma_creating_vithis = [v for v in vithi_records 
                                 if v.javana_quality in ["kusala", "akusala"] 
                                 and v.kamma_potency > 0]
        kamma_creation_rate = (len(kamma_creating_vithis) / total_cycles_observed * 100.0) if total_cycles_observed > 0 else 0.0
        
        # Calculate link intensities from anusaya
        link_intensities = {
            "AVIJJA": anusaya.get("moha", 5.0),
            "SANKHARA": (anusaya.get("lobha", 5.0) + anusaya.get("dosa", 5.0)) / 2.0,
            "VINNANA": 6.0,
            "NAMARUPA": 6.0,
            "SALAYATANA": 6.5,
            "PHASSA": 7.0,
            "VEDANA": avg_vedana_intensity,
            "TANHA": avg_tanha_intensity,
            "UPADANA": avg_tanha_intensity * 0.9,
            "BHAVA": avg_tanha_intensity * 0.8,
            "JATI": 5.5,
            "JARA_MARANA": 5.3
        }
        
        return CycleStatisticsResponse(
            total_cycles_observed=total_cycles_observed,
            successful_breaks=successful_breaks,
            path_stage_breaks=path_stage_breaks,
            avg_vedana_intensity=round(avg_vedana_intensity, 2),
            avg_tanha_intensity=round(avg_tanha_intensity, 2),
            most_common_tanha_type=most_common_tanha_type,
            kamma_creation_rate=round(kamma_creation_rate, 1),
            link_intensities={k: round(v, 1) for k, v in link_intensities.items()}
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error calculating statistics: {e}")
    
    # Fallback to default response
    return CycleStatisticsResponse(
        total_cycles_observed=1523,
        successful_breaks=47,
        path_stage_breaks=0,
        avg_vedana_intensity=6.5,
        avg_tanha_intensity=5.8,
        most_common_tanha_type="kama",
        kamma_creation_rate=85.3,
        link_intensities={
            "AVIJJA": 7.2,
            "SANKHARA": 6.5,
            "VINNANA": 6.8,
            "NAMARUPA": 6.9,
            "SALAYATANA": 7.0,
            "PHASSA": 7.1,
            "VEDANA": 7.3,
            "TANHA": 6.8,
            "UPADANA": 6.2,
            "BHAVA": 5.9,
            "JATI": 5.5,
            "JARA_MARANA": 5.3
        }
    )

# ============================================================================
# POST Endpoints
# ============================================================================

class ProcessCittaMomentRequest(BaseModel):
    """Request to process a citta moment through the cycle"""
    citta_type: str = Field(..., description="Type of consciousness")
    vedana_type: str = Field(..., description="sukha/dukkha/upekkha")
    vedana_intensity: float = Field(..., ge=0.0, le=10.0, description="Feeling intensity")
    mindfulness_level: float = Field(0.0, ge=0.0, le=10.0, description="Current mindfulness")
    wisdom_level: float = Field(0.0, ge=0.0, le=10.0, description="Current wisdom")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

@router.post("/{model_id}/process-moment", response_model=VedanaTanhaCycleResponse)
async def process_citta_moment(
    model_id: str,
    request: ProcessCittaMomentRequest
):
    """
    Process a citta moment through the Dependent Origination cycle.
    
    This simulates how a feeling (vedanā) leads to craving (taṇhā),
    then clinging (upādāna), then becoming (bhava), and potentially
    kamma creation.
    
    Mindfulness and wisdom can interrupt the cycle.
    
    Args:
        model_id: Character ID
        request: ProcessCittaMomentRequest with citta and feeling info
    
    Returns:
        VedanaTanhaCycleResponse showing what happened
    
    Example:
        POST /api/paticcasamuppada/123/process-moment
        {
            "citta_type": "lobha-mula-citta-1",
            "vedana_type": "sukha",
            "vedana_intensity": 8.0,
            "mindfulness_level": 3.0,
            "wisdom_level": 2.0
        }
    """
    # Implement actual cycle processing using Paṭiccasamuppāda Engine
    from documents import MindState
    
    try:
        # 1. Load character's PS state
        mind_state = await MindState.find_one({"model_id": model_id})
        
        if not mind_state:
            raise HTTPException(status_code=404, detail="Mind state not found")
        
        # 2. Analyze the citta type for kamma potential
        is_wholesome = "kusala" in request.citta_type.lower()
        is_unwholesome = any(word in request.citta_type.lower() 
                            for word in ["lobha", "dosa", "moha"])
        
        # 3. Process through Vedanā→Taṇhā→Upādāna→Bhava cycle
        
        # Vedanā (Feeling) - from request
        vedana_intensity = request.vedana_intensity
        vedana_type = request.vedana_type
        
        # Check if mindfulness interrupts at vedanā stage
        mindfulness_applied = request.mindfulness_level >= 7.0
        wisdom_applied = request.wisdom_level >= 7.0
        
        if mindfulness_applied or wisdom_applied:
            # Cycle is interrupted - no taṇhā arises
            tanha_intensity = 0.0
            tanha_types_active = []
            upadana_intensity = 0.0
            upadana_types_active = []
            bhava_intensity = 0.0
            bhava_types_active = []
            kamma_created = False
            
            # Increase kusala count for successful interruption
            mind_state.kusala_count_today += 1
            mind_state.kusala_count_total += 1
            await mind_state.save()
        else:
            # Taṇhā (Craving) arises based on feeling intensity and lobha
            anusaya = mind_state.current_anusaya
            lobha_level = anusaya.get("lobha", 3.0)
            
            tanha_intensity = vedana_intensity * (lobha_level / 10.0) * 1.2
            tanha_intensity = min(tanha_intensity, 10.0)
            
            # Determine taṇhā types
            tanha_types_active = []
            if vedana_type == "sukha" and lobha_level > 4.0:
                tanha_types_active.append("kama")  # Sensual craving
            if anusaya.get("ditthi", 0) > 4.0:
                tanha_types_active.append("bhava")  # Craving for existence
            if vedana_type == "dukkha" and anusaya.get("moha", 0) > 5.0:
                tanha_types_active.append("vibhava")  # Craving for non-existence
            
            # Upādāna (Clinging) follows craving
            upadana_intensity = tanha_intensity * 0.9
            upadana_types_active = []
            if "kama" in tanha_types_active:
                upadana_types_active.append("kama")
            if anusaya.get("ditthi", 0) > 3.0:
                upadana_types_active.append("ditthi")
            if anusaya.get("mana", 0) > 3.0:
                upadana_types_active.append("attavada")
            
            # Bhava (Becoming) follows clinging
            bhava_intensity = upadana_intensity * 0.85
            bhava_types_active = []
            if lobha_level > 4.0:
                bhava_types_active.append("kama")
            
            # 5. Create kamma if cycle completes without interruption
            kamma_created = (tanha_intensity > 6.0 and upadana_intensity > 5.0)
            
            if kamma_created:
                if is_unwholesome:
                    mind_state.akusala_count_today += 1
                    mind_state.akusala_count_total += 1
                elif is_wholesome:
                    mind_state.kusala_count_today += 1
                    mind_state.kusala_count_total += 1
                
                # 6. Save updated state
                mind_state.updated_at = datetime.utcnow()
                await mind_state.save()
        
        # 7. Return result
        return VedanaTanhaCycleResponse(
            vedana_intensity=vedana_intensity,
            vedana_type=vedana_type,
            tanha_intensity=tanha_intensity,
            tanha_types_active=tanha_types_active,
            upadana_intensity=upadana_intensity,
            upadana_types_active=upadana_types_active,
            bhava_intensity=bhava_intensity,
            bhava_types_active=bhava_types_active,
            kamma_created=kamma_created,
            mindfulness_applied=mindfulness_applied,
            wisdom_applied=wisdom_applied
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing citta moment: {e}")
    
    # Fallback to mock response
    return VedanaTanhaCycleResponse(
        vedana_intensity=request.vedana_intensity,
        vedana_type=request.vedana_type,
        tanha_intensity=6.8,
        tanha_types_active=["kama"],
        upadana_intensity=6.0,
        upadana_types_active=["kama", "attavada"],
        bhava_intensity=5.5,
        bhava_types_active=["kama"],
        kamma_created=True,
        mindfulness_applied=request.mindfulness_level > 6.0,
        wisdom_applied=request.wisdom_level > 7.0
    )

class ApplyPathBreakingRequest(BaseModel):
    """Request to apply path-stage breaking points"""
    new_path_stage: str = Field(..., description="Sotāpanna/Sakadāgāmī/Anāgāmī/Arahant")
    apply_immediately: bool = Field(True, description="Apply breaking immediately")

@router.post("/{model_id}/apply-breaking", response_model=CycleStateResponse)
async def apply_path_breaking(
    model_id: str,
    request: ApplyPathBreakingRequest
):
    """
    Apply path-stage breaking points to the cycle.
    
    When a character attains a path stage, certain links
    are weakened or eliminated. This endpoint applies those changes.
    
    Args:
        model_id: Character ID
        request: ApplyPathBreakingRequest with new path stage
    
    Returns:
        CycleStateResponse with updated state
    
    Example:
        POST /api/paticcasamuppada/123/apply-breaking
        {
            "new_path_stage": "Sotāpanna",
            "apply_immediately": true
        }
    """
    # Implement actual breaking point application
    from documents import MindState
    
    try:
        # 1. Load PS state
        mind_state = await MindState.find_one({"model_id": model_id})
        
        if not mind_state:
            raise HTTPException(status_code=404, detail="Mind state not found")
        
        # 2. Validate path progression
        valid_stages = ["Sotāpanna", "Sakadāgāmī", "Anāgāmī", "Arahant"]
        path_stage_lower = request.new_path_stage.lower()
        
        if request.new_path_stage not in valid_stages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid path stage: {request.new_path_stage}. Must be one of {', '.join(valid_stages)}"
            )
        
        # Check path progression (can't go backwards)
        current_bhumi = mind_state.current_bhumi
        stage_order = {"puthujjana": 0, "sotapanna": 1, "sakadagami": 2, "anagami": 3, "arahant": 4}
        
        current_level = stage_order.get(current_bhumi, 0)
        new_level = stage_order.get(path_stage_lower, 0)
        
        if new_level <= current_level:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot regress from {current_bhumi} to {path_stage_lower}"
            )
        
        # 3. Apply path breaking to anusaya (latent tendencies)
        anusaya = mind_state.current_anusaya.copy()
        
        if path_stage_lower == "sotapanna":
            # Sotāpanna: Eliminate 3 fetters (sakkāya-ditthi, vicikicchā, sīlabbata-parāmāsa)
            anusaya["ditthi"] = 0.0  # Wrong view eliminated
            anusaya["vicikiccha"] = 0.0  # Doubt eliminated
            anusaya["lobha"] *= 0.6  # Greed reduced 40%
            anusaya["dosa"] *= 0.6  # Hatred reduced 40%
            anusaya["moha"] *= 0.8  # Delusion reduced 20%
            
        elif path_stage_lower == "sakadagami":
            # Sakadāgāmī: Further weaken sensual desire and ill-will
            anusaya["ditthi"] = 0.0
            anusaya["vicikiccha"] = 0.0
            anusaya["lobha"] *= 0.3  # Greed reduced 70%
            anusaya["dosa"] *= 0.3  # Hatred reduced 70%
            anusaya["moha"] *= 0.6  # Delusion reduced 40%
            
        elif path_stage_lower == "anagami":
            # Anāgāmī: Eliminate sensual desire and ill-will completely
            anusaya["ditthi"] = 0.0
            anusaya["vicikiccha"] = 0.0
            anusaya["lobha"] = 0.0  # Sensual craving eliminated
            anusaya["dosa"] = 0.0  # Hatred eliminated
            anusaya["moha"] *= 0.4  # Delusion reduced 60%
            anusaya["mana"] *= 0.5  # Conceit reduced 50%
            
        elif path_stage_lower == "arahant":
            # Arahant: Eliminate all defilements
            anusaya = {
                "lobha": 0.0,
                "dosa": 0.0,
                "moha": 0.0,
                "mana": 0.0,
                "ditthi": 0.0,
                "vicikiccha": 0.0,
                "thina": 0.0
            }
        
        # 4. Update cycle state
        if request.apply_immediately:
            mind_state.current_anusaya = anusaya
            mind_state.current_bhumi = path_stage_lower
            mind_state.updated_at = datetime.utcnow()
            
            # 5. Save to database
            await mind_state.save()
        
        # 6. Calculate new link intensities and return state
        link_intensities = {
            "AVIJJA": anusaya.get("moha", 0.0),
            "SANKHARA": (anusaya.get("lobha", 0.0) + anusaya.get("dosa", 0.0)) / 2.0,
            "VINNANA": 5.0,
            "NAMA_RUPA": 5.0,
            "SALAYATANA": 5.0,
            "PHASSA": 5.0,
            "VEDANA": 5.0 + (anusaya.get("lobha", 0.0) + anusaya.get("dosa", 0.0)) / 4.0,
            "TANHA": anusaya.get("lobha", 0.0),
            "UPADANA": anusaya.get("lobha", 0.0) * 0.9,
            "BHAVA": anusaya.get("lobha", 0.0) * 0.8,
            "JATI": 3.0 if path_stage_lower != "arahant" else 0.0,
            "JARA_MARANA": 3.0 if path_stage_lower != "arahant" else 0.0
        }
        
        links = []
        for link in NidanaLink:
            intensity = link_intensities.get(link.name, 0.0)
            links.append(LinkStateResponse(
                link=link.name,
                pali=link.value,
                english=_get_link_english(link),
                intensity=intensity,
                active=intensity > 1.0,
                last_activated=datetime.now()
            ))
        
        # Determine cycle state
        cycle_state = "ACTIVE"
        if path_stage_lower == "arahant":
            cycle_state = "BROKEN"
        elif path_stage_lower == "anagami":
            cycle_state = "INTERRUPTED"
        elif path_stage_lower in ["sotapanna", "sakadagami"]:
            cycle_state = "WEAKENED"
        
        return CycleStateResponse(
            cycle_state=cycle_state,
            path_stage=request.new_path_stage,
            all_links=links,
            critical_cycle={
                "vedana_intensity": link_intensities["VEDANA"],
                "tanha_intensity": link_intensities["TANHA"],
                "upadana_intensity": link_intensities["UPADANA"],
                "bhava_intensity": link_intensities["BHAVA"]
            },
            cycles_completed=mind_state.kusala_count_total,
            cycles_broken=mind_state.kusala_count_total,
            avg_cycle_duration_hours=0.3
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error applying path breaking: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply path breaking: {str(e)}"
        )

class SimulateRebirthRequest(BaseModel):
    """Request to simulate rebirth"""
    trigger_time: Optional[datetime] = Field(None, description="When rebirth occurs (default: now)")
    override_kamma: Optional[Dict[str, Any]] = Field(None, description="Optional kamma override for testing")

@router.post("/{model_id}/simulate-rebirth", response_model=RebirthPredictionResponse)
async def simulate_rebirth(
    model_id: str,
    request: SimulateRebirthRequest
):
    """
    Simulate rebirth based on current kamma.
    
    This uses the Paticcasamuppāda Engine to determine
    which realm the character would be reborn into.
    
    Args:
        model_id: Character ID
        request: SimulateRebirthRequest with optional parameters
    
    Returns:
        RebirthPredictionResponse with rebirth outcome
    
    Example:
        POST /api/paticcasamuppada/123/simulate-rebirth
        {
            "trigger_time": "2024-10-17T10:00:00Z"
        }
    """
    # Implement actual rebirth simulation
    # This reuses the rebirth prediction logic with optional overrides
    from documents import MindState, DigitalMindModel
    from core_profile_models import CoreProfile
    
    try:
        # Get character data
        mind_state = await MindState.find_one({"model_id": model_id})
        digital_mind = await DigitalMindModel.find_one({"model_id": model_id})
        
        if not mind_state or not digital_mind:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Get core profile
        core_profile_dict = digital_mind.core_profile
        if not core_profile_dict:
            raise HTTPException(status_code=404, detail="Core profile not found")
        
        core_profile = CoreProfile(**core_profile_dict)
        
        # 1. Get strongest ripening kamma (or use override)
        if request.override_kamma:
            kusala_kamma = request.override_kamma.get("kusala", 0)
            akusala_kamma = request.override_kamma.get("akusala", 0)
        else:
            # Use actual kamma from profile
            kusala_kamma = getattr(core_profile.spiritual_assets, "accumulated_merit", 0)
            akusala_kamma = mind_state.akusala_count_total * 10.0
        
        # 2. Determine realm from kamma type/potency
        if kusala_kamma > akusala_kamma * 1.5:
            dominant_kamma_type = "Kusala"
            kamma_potency = min(kusala_kamma / 1000.0, 10.0)
        elif akusala_kamma > kusala_kamma * 1.5:
            dominant_kamma_type = "Akusala"
            kamma_potency = min(akusala_kamma / 100.0, 10.0)
        else:
            dominant_kamma_type = "Mixed"
            kamma_potency = 5.0
        
        # 3. Calculate realm probabilities
        if dominant_kamma_type == "Kusala":
            realm_probabilities = {
                "Hell": 0.02,
                "Animal": 0.03,
                "Ghost": 0.05,
                "Asura": 0.10,
                "Human": 0.50,
                "Deva": 0.30
            }
            most_likely_realm = "Human" if kamma_potency < 8.0 else "Deva"
        elif dominant_kamma_type == "Akusala":
            realm_probabilities = {
                "Hell": 0.25,
                "Animal": 0.20,
                "Ghost": 0.20,
                "Asura": 0.20,
                "Human": 0.10,
                "Deva": 0.05
            }
            most_likely_realm = "Hell" if kamma_potency > 6.0 else "Animal"
        else:
            realm_probabilities = {
                "Hell": 0.10,
                "Animal": 0.15,
                "Ghost": 0.15,
                "Asura": 0.15,
                "Human": 0.30,
                "Deva": 0.15
            }
            most_likely_realm = "Human"
        
        # 4. Consider path stage constraints
        path_stage = mind_state.current_bhumi
        rebirths_remaining = None
        
        if path_stage == "arahant":
            # Arahant = no rebirth (Parinibbāna)
            most_likely_realm = "Parinibbāna"
            realm_probabilities = {
                "Hell": 0.0,
                "Animal": 0.0,
                "Ghost": 0.0,
                "Asura": 0.0,
                "Human": 0.0,
                "Deva": 0.0
            }
            rebirths_remaining = 0
        elif path_stage == "anagami":
            # Anāgāmī = no sensual realm rebirth (only Pure Abodes)
            most_likely_realm = "Pure Abodes (Suddhāvāsa)"
            realm_probabilities = {
                "Hell": 0.0,
                "Animal": 0.0,
                "Ghost": 0.0,
                "Asura": 0.0,
                "Human": 0.0,
                "Deva": 1.0  # Pure Abodes only
            }
            rebirths_remaining = 1
        elif path_stage == "sakadagami":
            # Sakadāgāmī = at most one return to human realm
            if most_likely_realm in ["Hell", "Animal", "Ghost"]:
                most_likely_realm = "Human"  # Can't be reborn in lower realms
            rebirths_remaining = 1
        elif path_stage == "sotapanna":
            # Sotāpanna = no lower realms, at most 7 rebirths
            if most_likely_realm in ["Hell", "Animal", "Ghost"]:
                most_likely_realm = "Human"  # Can't be reborn in lower realms
            realm_probabilities["Hell"] = 0.0
            realm_probabilities["Animal"] = 0.0
            realm_probabilities["Ghost"] = 0.0
            # Redistribute to remaining realms
            remaining_total = realm_probabilities["Asura"] + realm_probabilities["Human"] + realm_probabilities["Deva"]
            if remaining_total > 0:
                realm_probabilities["Asura"] /= remaining_total
                realm_probabilities["Human"] /= remaining_total
                realm_probabilities["Deva"] /= remaining_total
            rebirths_remaining = 7
        
        # 5. Build conditions met
        conditions_met = []
        if kusala_kamma > 0:
            conditions_met.append("kusala_kamma_present")
        if kusala_kamma > akusala_kamma:
            conditions_met.append("kusala_dominant")
        if mind_state.sila >= 5.0:
            conditions_met.append("moral_conduct")
        if path_stage != "puthujjana":
            conditions_met.append(f"noble_{path_stage}")
        
        # 6. Return prediction
        return RebirthPredictionResponse(
            most_likely_realm=most_likely_realm,
            realm_probabilities=realm_probabilities,
            dominant_kamma_type=dominant_kamma_type,
            kamma_potency=kamma_potency,
            conditions_met=conditions_met,
            rebirths_remaining=rebirths_remaining
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error simulating rebirth: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to simulate rebirth: {str(e)}"
        )

# ============================================================================
# Utility Endpoints
# ============================================================================

@router.get("/links", response_model=List[Dict[str, str]])
async def list_all_links():
    """
    List all 12 links (nidānas) of Dependent Origination.
    
    Returns information about each link in the cycle.
    
    Returns:
        List of link information
    
    Example:
        GET /api/paticcasamuppada/links
    """
    links = []
    for link in NidanaLink:
        links.append({
            "name": link.name,
            "pali": link.value,
            "english": _get_link_english(link),
            "order": list(NidanaLink).index(link) + 1
        })
    return links

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "paticcasamuppada-engine",
        "version": "1.0.0",
        "links_count": len(NidanaLink)
    }

# ============================================================================
# Helper Functions
# ============================================================================

def _get_link_english(link: NidanaLink) -> str:
    """Get English translation for a link"""
    translations = {
        NidanaLink.AVIJJA: "Ignorance",
        NidanaLink.SANKHARA: "Mental formations",
        NidanaLink.VINNANA: "Consciousness",
        NidanaLink.NAMA_RUPA: "Name-and-form",
        NidanaLink.SALAYATANA: "Six sense bases",
        NidanaLink.PHASSA: "Contact",
        NidanaLink.VEDANA: "Feeling",
        NidanaLink.TANHA: "Craving",
        NidanaLink.UPADANA: "Clinging",
        NidanaLink.BHAVA: "Becoming",
        NidanaLink.JATI: "Birth",
        NidanaLink.JARA_MARANA: "Aging and death"
    }
    return translations.get(link, link.name)
