"""
SimulationHistory API Router
Provides CRUD operations for simulation session records and analytics

Endpoints:
- POST   /api/v1/simulation-history/           Create new simulation record
- GET    /api/v1/simulation-history/{sim_id}   Get specific simulation
- GET    /api/v1/simulation-history/user/{user_id}  Get user's simulation history
- DELETE /api/v1/simulation-history/{sim_id}   Delete simulation record
- GET    /api/v1/simulation-history/user/{user_id}/analytics  Get analytics
- GET    /api/v1/simulation-history/user/{user_id}/anusaya-trends  Anusaya changes over time
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, status, Query, Depends
from pydantic import BaseModel, Field

from documents import SimulationHistory
from core.logging_config import get_logger

# Import authentication dependency
from auth import current_active_user
from auth.models import User

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/simulation-history", tags=["simulation_history"])


# === Request/Response Models ===

class SimulationHistoryCreate(BaseModel):
    """Request model for creating simulation history"""
    simulation_id: str = Field(..., description="Unique simulation identifier")
    user_id: str = Field(..., description="User identifier")
    scenario_id: str = Field(..., description="Scenario identifier")
    
    # Choice information
    choice_index: int = Field(..., ge=0)
    choice_id: str
    choice_type: str  # kusala, akusala, neutral
    choice_label: str
    choice_description: Optional[str] = None
    
    # Mental process
    citta_generated: str  # Type of consciousness
    citta_quality: str  # Quality assessment
    kamma_generated: float = Field(..., ge=0, le=10)
    
    # Intervention flags
    sati_intervened: bool = False
    sati_strength_at_choice: Optional[float] = None
    panna_intervened: bool = False
    
    # State tracking
    state_before: Dict[str, Any]
    state_after: Dict[str, Any]
    state_changes: List[str] = []
    
    # Consequences
    immediate_consequences: List[str]
    short_term_consequences: List[str]
    long_term_consequences: List[str]
    
    # Learning outcomes
    wisdom_gained: str
    practice_tip: str
    pali_term_explained: Optional[str] = None
    
    # User engagement
    user_reflection: Optional[str] = None
    user_rating: Optional[int] = Field(None, ge=1, le=5)
    
    # Anusaya tracking
    anusaya_before: Dict[str, float]
    anusaya_after: Dict[str, float]
    anusaya_changes: Dict[str, float]
    
    # Metadata
    duration_seconds: Optional[int] = None


class SimulationHistoryResponse(BaseModel):
    """Response model for simulation history"""
    simulation_id: str
    user_id: str
    scenario_id: str
    choice_index: int
    choice_id: str
    choice_type: str
    choice_label: str
    choice_description: Optional[str]
    citta_generated: str
    citta_quality: str
    kamma_generated: float
    sati_intervened: bool
    panna_intervened: bool
    state_changes: List[str]
    immediate_consequences: List[str]
    wisdom_gained: str
    practice_tip: str
    user_rating: Optional[int]
    anusaya_changes: Dict[str, float]
    duration_seconds: Optional[int]
    timestamp: datetime


class UserHistorySummary(BaseModel):
    """Summary of user's simulation history"""
    user_id: str
    total_simulations: int
    kusala_choices: int
    akusala_choices: int
    neutral_choices: int
    sati_intervention_count: int
    panna_intervention_count: int
    average_kamma_generated: float
    total_duration_seconds: int
    average_rating: Optional[float]
    scenarios_attempted: List[str]
    recent_simulations: List[Dict[str, Any]]  # Last 5 simulations


class AnusayaTrendData(BaseModel):
    """Anusaya changes over time"""
    user_id: str
    anusaya_name: str  # lobha, dosa, moha, etc.
    data_points: List[Dict[str, Any]]  # [{"timestamp": ..., "value": ..., "change": ...}]
    overall_trend: str  # "increasing", "decreasing", "stable"
    total_change: float


# === Helper Functions ===

async def get_simulation_or_404(simulation_id: str) -> SimulationHistory:
    """Get SimulationHistory or raise 404"""
    history = await SimulationHistory.find_one(SimulationHistory.simulation_id == simulation_id)
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Simulation not found: {simulation_id}"
        )
    return history


def calculate_trend(values: List[float]) -> str:
    """Calculate overall trend from list of values"""
    if len(values) < 2:
        return "insufficient_data"
    
    # Simple linear trend: compare first half vs second half average
    mid = len(values) // 2
    first_half_avg = sum(values[:mid]) / len(values[:mid])
    second_half_avg = sum(values[mid:]) / len(values[mid:])
    
    diff = second_half_avg - first_half_avg
    if abs(diff) < 0.3:
        return "stable"
    elif diff > 0:
        return "increasing"
    else:
        return "decreasing"


# === API Endpoints ===

@router.post("/", response_model=SimulationHistoryResponse, status_code=status.HTTP_201_CREATED)
async def create_simulation_history(
    data: SimulationHistoryCreate,
    current_user: User = Depends(current_active_user)
):
    """
    Create new simulation history record
    
    Records complete information about a simulation session including:
    - User's choice and mental process (citta, kamma)
    - Sati/Paññā intervention status
    - State changes and consequences
    - Learning outcomes
    - Anusaya changes
    
    **Authentication required**
    """
    # Force user_id from authenticated user (prevent spoofing)
    data.user_id = str(current_user.id)
    
    # Check if simulation_id already exists
    existing = await SimulationHistory.find_one(
        SimulationHistory.simulation_id == data.simulation_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Simulation history already exists: {data.simulation_id}"
        )
    
    # Create new record
    history = SimulationHistory(
        **data.dict(),
        timestamp=datetime.utcnow()
    )
    
    await history.insert()
    logger.info(f"Created simulation history {data.simulation_id} for user {current_user.email}")
    
    return SimulationHistoryResponse(**history.dict())


@router.get("/{simulation_id}", response_model=SimulationHistoryResponse)
async def get_simulation_history(
    simulation_id: str,
    current_user: User = Depends(current_active_user)
):
    """
    Get specific simulation history record
    
    Returns complete simulation details including all choices,
    consequences, and learning outcomes
    
    **Authentication required** - Users can only access their own simulations
    """
    history = await get_simulation_or_404(simulation_id)
    
    # Check ownership
    if str(history.user_id) != str(current_user.id) and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' simulation history"
        )
    
    return SimulationHistoryResponse(**history.dict())


@router.delete("/{simulation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_simulation_history(
    simulation_id: str,
    current_user: User = Depends(current_active_user)
):
    """
    Delete simulation history record
    
    Warning: This operation cannot be undone
    
    **Authentication required** - Users can only delete their own simulations
    """
    history = await get_simulation_or_404(simulation_id)
    
    # Check ownership
    if str(history.user_id) != str(current_user.id) and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete other users' simulation history"
        )
    
    await history.delete()
    logger.info(f"Deleted simulation history {simulation_id} by user {current_user.email}")
    return None


@router.get("/user/{user_id}", response_model=List[SimulationHistoryResponse])
async def get_user_simulation_history(
    user_id: str,
    current_user: User = Depends(current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    scenario_id: Optional[str] = None,
    choice_type: Optional[str] = None
):
    """
    Get user's simulation history with optional filters
    
    - **user_id**: User identifier
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return (1-100)
    - **scenario_id**: Optional filter by scenario
    - **choice_type**: Optional filter by choice type (kusala/akusala/neutral)
    
    Returns simulations sorted by timestamp (newest first)
    
    **Authentication required** - Users can only access their own history
    """
    # Check access permission
    if user_id != str(current_user.id) and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' simulation history"
        )
    
    # Build query dictionary
    query = {"user_id": user_id}
    
    # Apply filters
    if scenario_id:
        query["scenario_id"] = scenario_id
    if choice_type:
        query["choice_type"] = choice_type
    
    # Execute query with pagination
    histories = await SimulationHistory.find(query)\
        .sort("-timestamp")\
        .skip(skip)\
        .limit(limit)\
        .to_list()
    
    return [SimulationHistoryResponse(**h.dict()) for h in histories]


@router.get("/user/{user_id}/summary", response_model=UserHistorySummary)
async def get_user_history_summary(
    user_id: str,
    current_user: User = Depends(current_active_user)
):
    """
    Get summary statistics of user's simulation history
    
    Returns:
    - Total simulations and breakdown by choice type
    - Intervention statistics (Sati/Paññā usage)
    - Average kamma generated
    - Total time spent
    - Average user rating
    - List of scenarios attempted
    - Recent simulations (last 5)
    
    **Authentication required** - Users can only access their own summary
    """
    # Check access permission
    if user_id != str(current_user.id) and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' simulation summary"
        )
    
    # Get all user's simulations
    all_histories = await SimulationHistory.find(
        SimulationHistory.user_id == user_id
    ).to_list()
    
    if not all_histories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No simulation history found for user: {user_id}"
        )
    
    # Calculate statistics
    total = len(all_histories)
    kusala = sum(1 for h in all_histories if h.choice_type == "kusala")
    akusala = sum(1 for h in all_histories if h.choice_type == "akusala")
    neutral = sum(1 for h in all_histories if h.choice_type == "neutral")
    
    sati_count = sum(1 for h in all_histories if h.sati_intervened)
    panna_count = sum(1 for h in all_histories if h.panna_intervened)
    
    avg_kamma = sum(h.kamma_generated for h in all_histories) / total
    
    total_duration = sum(h.duration_seconds or 0 for h in all_histories)
    
    ratings = [h.user_rating for h in all_histories if h.user_rating is not None]
    avg_rating = sum(ratings) / len(ratings) if ratings else None
    
    scenarios = list(set(h.scenario_id for h in all_histories))
    
    # Get recent simulations (last 5)
    recent = sorted(all_histories, key=lambda h: h.timestamp, reverse=True)[:5]
    recent_data = [
        {
            "simulation_id": h.simulation_id,
            "scenario_id": h.scenario_id,
            "choice_type": h.choice_type,
            "kamma_generated": h.kamma_generated,
            "sati_intervened": h.sati_intervened,
            "timestamp": h.timestamp.isoformat()
        }
        for h in recent
    ]
    
    return UserHistorySummary(
        user_id=user_id,
        total_simulations=total,
        kusala_choices=kusala,
        akusala_choices=akusala,
        neutral_choices=neutral,
        sati_intervention_count=sati_count,
        panna_intervention_count=panna_count,
        average_kamma_generated=round(avg_kamma, 2),
        total_duration_seconds=total_duration,
        average_rating=round(avg_rating, 2) if avg_rating else None,
        scenarios_attempted=scenarios,
        recent_simulations=recent_data
    )


@router.get("/user/{user_id}/anusaya-trends", response_model=List[AnusayaTrendData])
async def get_anusaya_trends(
    user_id: str,
    current_user: User = Depends(current_active_user),
    anusaya_names: Optional[List[str]] = Query(None, description="Specific anusaya to track")
):
    """
    Get anusaya (latent tendencies) changes over time
    
    - **user_id**: User identifier
    - **anusaya_names**: Optional list of specific anusaya to track
      (lobha, dosa, moha, mana, ditthi, vicikiccha, uddhacca)
    
    Returns trend data showing how each anusaya has changed
    across simulation sessions, with overall trend analysis
    
    **Authentication required** - Users can only access their own trends
    """
    # Check access permission
    if user_id != str(current_user.id) and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' anusaya trends"
        )
    
    # Get all simulations sorted by time
    histories = await SimulationHistory.find(
        SimulationHistory.user_id == user_id
    ).sort("timestamp").to_list()
    
    if not histories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No simulation history found for user: {user_id}"
        )
    
    # Default anusaya names if not specified
    if not anusaya_names:
        anusaya_names = ["lobha", "dosa", "moha", "mana", "ditthi", "vicikiccha", "uddhacca"]
    
    # Build trend data for each anusaya
    trends = []
    
    for anusaya_name in anusaya_names:
        data_points = []
        values = []
        
        for history in histories:
            # Get anusaya value after this simulation
            value_after = history.anusaya_after.get(anusaya_name)
            change = history.anusaya_changes.get(anusaya_name, 0)
            
            if value_after is not None:
                data_points.append({
                    "timestamp": history.timestamp.isoformat(),
                    "simulation_id": history.simulation_id,
                    "value": value_after,
                    "change": change
                })
                values.append(value_after)
        
        if data_points:
            overall_trend = calculate_trend(values)
            total_change = values[-1] - values[0] if len(values) >= 2 else 0
            
            trends.append(AnusayaTrendData(
                user_id=user_id,
                anusaya_name=anusaya_name,
                data_points=data_points,
                overall_trend=overall_trend,
                total_change=round(total_change, 2)
            ))
    
    return trends


@router.get("/user/{user_id}/learning-progress")
async def get_learning_progress(
    user_id: str,
    current_user: User = Depends(current_active_user)
):
    """
    Get user's learning progress from simulations
    
    Analyzes wisdom gained and practice tips across all simulations
    to show learning development over time
    
    **Authentication required** - Users can only access their own learning progress
    """
    # Check access permission
    if user_id != str(current_user.id) and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' learning progress"
        )
    
    histories = await SimulationHistory.find(
        SimulationHistory.user_id == user_id
    ).sort("timestamp").to_list()
    
    if not histories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No simulation history found for user: {user_id}"
        )
    
    # Collect all wisdom and tips
    wisdom_list = [h.wisdom_gained for h in histories if h.wisdom_gained]
    tips_list = [h.practice_tip for h in histories if h.practice_tip]
    pali_terms = [h.pali_term_explained for h in histories if h.pali_term_explained]
    
    # Count reflections
    reflection_count = sum(1 for h in histories if h.user_reflection)
    
    return {
        "user_id": user_id,
        "total_lessons": len(histories),
        "wisdom_gained_count": len(wisdom_list),
        "practice_tips_received": len(tips_list),
        "pali_terms_learned": len(set(pali_terms)),  # Unique terms
        "user_reflections": reflection_count,
        "reflection_rate": round(reflection_count / len(histories) * 100, 1) if histories else 0,
        "recent_wisdom": wisdom_list[-3:] if wisdom_list else [],
        "recent_tips": tips_list[-3:] if tips_list else []
    }


@router.get("/scenarios/{scenario_id}/analytics")
async def get_scenario_analytics(scenario_id: str):
    """
    Get analytics for a specific scenario across all users
    
    Shows how users typically perform on this scenario:
    - Choice distribution (kusala/akusala/neutral)
    - Average kamma generated
    - Intervention rates
    - Average ratings
    """
    histories = await SimulationHistory.find(
        SimulationHistory.scenario_id == scenario_id
    ).to_list()
    
    if not histories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No simulation history found for scenario: {scenario_id}"
        )
    
    total = len(histories)
    kusala = sum(1 for h in histories if h.choice_type == "kusala")
    akusala = sum(1 for h in histories if h.choice_type == "akusala")
    neutral = sum(1 for h in histories if h.choice_type == "neutral")
    
    sati_rate = sum(1 for h in histories if h.sati_intervened) / total * 100
    panna_rate = sum(1 for h in histories if h.panna_intervened) / total * 100
    
    avg_kamma = sum(h.kamma_generated for h in histories) / total
    
    ratings = [h.user_rating for h in histories if h.user_rating is not None]
    avg_rating = sum(ratings) / len(ratings) if ratings else None
    
    unique_users = len(set(h.user_id for h in histories))
    
    return {
        "scenario_id": scenario_id,
        "total_attempts": total,
        "unique_users": unique_users,
        "choice_distribution": {
            "kusala": kusala,
            "akusala": akusala,
            "neutral": neutral,
            "kusala_percentage": round(kusala / total * 100, 1),
            "akusala_percentage": round(akusala / total * 100, 1)
        },
        "intervention_rates": {
            "sati_rate": round(sati_rate, 1),
            "panna_rate": round(panna_rate, 1)
        },
        "average_kamma_generated": round(avg_kamma, 2),
        "average_rating": round(avg_rating, 2) if avg_rating else None,
        "difficulty_assessment": "easy" if avg_kamma > 7 else "medium" if avg_kamma > 5 else "hard"
    }
