"""
MindState API Router
Provides CRUD operations for user's mental/spiritual state tracking

Endpoints:
- POST   /api/v1/mind-states/                  Create new MindState
- GET    /api/v1/mind-states/{user_id}         Get user's MindState
- PUT    /api/v1/mind-states/{user_id}         Update MindState
- DELETE /api/v1/mind-states/{user_id}         Delete MindState
- POST   /api/v1/mind-states/{user_id}/reset-daily   Reset daily counters
- GET    /api/v1/mind-states/{user_id}/progress      Get progress summary
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, Query, Depends
from pydantic import BaseModel, Field

from documents import MindState
from core.logging_config import get_logger

# Import authentication dependency
from auth import current_active_user
from auth.models import User

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/mind-states", tags=["mind_states"])


# === Request/Response Models ===

class MindStateCreate(BaseModel):
    """Request model for creating new MindState"""
    user_id: str = Field(..., description="User identifier")
    sila: float = Field(default=5.0, ge=0, le=10)
    samadhi: float = Field(default=4.0, ge=0, le=10)
    panna: float = Field(default=4.0, ge=0, le=10)
    sati_strength: float = Field(default=5.0, ge=0, le=10)
    current_anusaya: Optional[Dict[str, float]] = None
    current_bhumi: str = Field(default="puthujjana")


class MindStateUpdate(BaseModel):
    """Request model for updating MindState"""
    sila: Optional[float] = Field(None, ge=0, le=10)
    samadhi: Optional[float] = Field(None, ge=0, le=10)
    panna: Optional[float] = Field(None, ge=0, le=10)
    sati_strength: Optional[float] = Field(None, ge=0, le=10)
    current_anusaya: Optional[Dict[str, float]] = None
    active_hindrances: Optional[Dict[str, float]] = None
    current_bhumi: Optional[str] = None
    meditation_minutes_add: Optional[int] = None  # Add meditation time


class MindStateResponse(BaseModel):
    """Response model for MindState"""
    user_id: str
    sila: float
    samadhi: float
    panna: float
    sati_strength: float
    current_anusaya: Dict[str, float]
    kusala_count_today: int
    akusala_count_today: int
    kusala_count_total: int
    akusala_count_total: int
    active_hindrances: Dict[str, float]
    current_bhumi: str
    days_of_practice: int
    meditation_minutes_total: int
    created_at: datetime
    updated_at: datetime
    last_simulation_at: Optional[datetime]


class ProgressSummary(BaseModel):
    """Summary of user's progress"""
    user_id: str
    current_level: str  # bhumi
    three_trainings: Dict[str, float]  # sila, samadhi, panna
    kusala_ratio_today: float  # kusala / (kusala + akusala)
    kusala_ratio_total: float
    days_of_practice: int
    meditation_hours: float
    dominant_anusaya: str  # Most prominent tendency
    weakest_area: str  # Area needing improvement
    recommendations: list[str]


# === Helper Functions ===

async def get_mind_state_or_404(user_id: str) -> MindState:
    """Get MindState or raise 404"""
    mind_state = await MindState.find_one(MindState.user_id == user_id)
    if not mind_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MindState not found for user_id: {user_id}"
        )
    return mind_state


def calculate_progress_summary(mind_state: MindState) -> ProgressSummary:
    """Calculate progress summary from MindState"""
    
    # Calculate kusala ratios
    kusala_today = mind_state.kusala_count_today
    akusala_today = mind_state.akusala_count_today
    today_total = kusala_today + akusala_today
    kusala_ratio_today = kusala_today / today_total if today_total > 0 else 0.5
    
    kusala_total = mind_state.kusala_count_total
    akusala_total = mind_state.akusala_count_total
    total_actions = kusala_total + akusala_total
    kusala_ratio_total = kusala_total / total_actions if total_actions > 0 else 0.5
    
    # Find dominant anusaya
    anusaya = mind_state.current_anusaya
    dominant_anusaya = max(anusaya.items(), key=lambda x: x[1])[0] if anusaya else "none"
    
    # Find weakest area
    three_trainings = {
        "sila": mind_state.sila,
        "samadhi": mind_state.samadhi,
        "panna": mind_state.panna
    }
    weakest_area = min(three_trainings.items(), key=lambda x: x[1])[0]
    
    # Generate recommendations
    recommendations = []
    if mind_state.sila < 6.0:
        recommendations.append("Focus on Sīla practice: Keep the five precepts diligently")
    if mind_state.samadhi < 6.0:
        recommendations.append("Strengthen Samādhi: Increase daily meditation time")
    if mind_state.panna < 6.0:
        recommendations.append("Develop Paññā: Study Dhamma and practice vipassanā")
    if mind_state.sati_strength < 6.0:
        recommendations.append("Build Sati: Practice mindfulness in daily activities")
    if kusala_ratio_today < 0.7:
        recommendations.append("Increase wholesome actions today")
    
    # Check dominant anusaya
    if dominant_anusaya != "none" and anusaya.get(dominant_anusaya, 0) > 5.0:
        anusaya_tips = {
            "lobha": "Practice contentment and generosity to reduce greed",
            "dosa": "Practice mettā (loving-kindness) to reduce anger",
            "moha": "Study Dhamma to reduce delusion",
            "mana": "Practice humility to reduce conceit",
            "ditthi": "Study right view to reduce wrong views",
            "vicikiccha": "Study and practice to reduce doubt",
            "uddhacca": "Practice calm and concentration to reduce restlessness"
        }
        if dominant_anusaya in anusaya_tips:
            recommendations.append(anusaya_tips[dominant_anusaya])
    
    return ProgressSummary(
        user_id=mind_state.user_id,
        current_level=mind_state.current_bhumi,
        three_trainings=three_trainings,
        kusala_ratio_today=round(kusala_ratio_today, 3),
        kusala_ratio_total=round(kusala_ratio_total, 3),
        days_of_practice=mind_state.days_of_practice,
        meditation_hours=round(mind_state.meditation_minutes_total / 60, 1),
        dominant_anusaya=dominant_anusaya,
        weakest_area=weakest_area,
        recommendations=recommendations
    )


# === API Endpoints ===

@router.post("/", response_model=MindStateResponse, status_code=status.HTTP_201_CREATED)
async def create_mind_state(data: MindStateCreate):
    """
    Create new MindState for a user
    
    - **user_id**: Unique user identifier
    - **sila, samadhi, panna**: Initial levels (0-10)
    - **sati_strength**: Initial mindfulness strength (0-10)
    - **current_anusaya**: Optional initial latent tendencies
    - **current_bhumi**: Spiritual level (default: puthujjana)
    """
    # Check if MindState already exists
    existing = await MindState.find_one(MindState.user_id == data.user_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"MindState already exists for user_id: {data.user_id}"
        )
    
    # Create new MindState
    mind_state = MindState(
        user_id=data.user_id,
        sila=data.sila,
        samadhi=data.samadhi,
        panna=data.panna,
        sati_strength=data.sati_strength,
        current_anusaya=data.current_anusaya or {},
        current_bhumi=data.current_bhumi
    )
    
    await mind_state.insert()
    logger.info(f"Created MindState for user {data.user_id}")
    
    return MindStateResponse(**mind_state.dict())


@router.get("/{user_id}", response_model=MindStateResponse)
async def get_mind_state(
    user_id: str,
    current_user: User = Depends(current_active_user)
):
    """
    Get MindState for a specific user
    
    **Authentication required**
    
    - **user_id**: User identifier
    
    Returns complete MindState including all levels, counters, and timestamps
    """
    # Check ownership
    if user_id != str(current_user.id) and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Cannot access other users' MindState data"
        )
    
    mind_state = await get_mind_state_or_404(user_id)
    return MindStateResponse(**mind_state.dict())


@router.put("/{user_id}", response_model=MindStateResponse)
async def update_mind_state(user_id: str, data: MindStateUpdate):
    """
    Update MindState for a user
    
    - **user_id**: User identifier
    - **sila, samadhi, panna**: Optional new levels
    - **sati_strength**: Optional new mindfulness strength
    - **current_anusaya**: Optional new anusaya levels
    - **active_hindrances**: Optional new hindrances
    - **current_bhumi**: Optional new spiritual level
    - **meditation_minutes_add**: Optional meditation time to add
    
    Only provided fields will be updated
    """
    mind_state = await get_mind_state_or_404(user_id)
    
    # Update fields if provided
    update_data = data.dict(exclude_unset=True)
    
    # Special handling for meditation minutes
    if "meditation_minutes_add" in update_data:
        mind_state.meditation_minutes_total += update_data.pop("meditation_minutes_add")
    
    # Update other fields
    for field, value in update_data.items():
        setattr(mind_state, field, value)
    
    # Update timestamp
    mind_state.updated_at = datetime.utcnow()
    
    await mind_state.save()
    logger.info(f"Updated MindState for user {user_id}")
    
    return MindStateResponse(**mind_state.dict())


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mind_state(user_id: str):
    """
    Delete MindState for a user
    
    - **user_id**: User identifier
    
    Warning: This operation cannot be undone
    """
    mind_state = await get_mind_state_or_404(user_id)
    await mind_state.delete()
    logger.info(f"Deleted MindState for user {user_id}")
    return None


@router.post("/{user_id}/reset-daily", response_model=MindStateResponse)
async def reset_daily_counters(user_id: str):
    """
    Reset daily kusala/akusala counters
    
    - **user_id**: User identifier
    
    Typically called at the start of each day (e.g., midnight)
    Increments days_of_practice counter
    """
    mind_state = await get_mind_state_or_404(user_id)
    
    # Reset daily counters
    mind_state.kusala_count_today = 0
    mind_state.akusala_count_today = 0
    mind_state.days_of_practice += 1
    mind_state.last_reset_at = datetime.utcnow()
    mind_state.updated_at = datetime.utcnow()
    
    await mind_state.save()
    logger.info(f"Reset daily counters for user {user_id}")
    
    return MindStateResponse(**mind_state.dict())


@router.get("/{user_id}/progress", response_model=ProgressSummary)
async def get_progress_summary(user_id: str):
    """
    Get progress summary and recommendations for a user
    
    - **user_id**: User identifier
    
    Returns:
    - Current spiritual level (bhumi)
    - Three trainings levels (sīla, samādhi, paññā)
    - Kusala ratios (today and total)
    - Practice statistics
    - Dominant anusaya
    - Weakest area
    - Personalized recommendations
    """
    mind_state = await get_mind_state_or_404(user_id)
    summary = calculate_progress_summary(mind_state)
    return summary


@router.post("/{user_id}/increment-kusala", response_model=MindStateResponse)
async def increment_kusala(user_id: str, amount: int = 1):
    """
    Increment kusala (wholesome) action count
    
    - **user_id**: User identifier
    - **amount**: Number to increment (default: 1)
    """
    mind_state = await get_mind_state_or_404(user_id)
    
    mind_state.kusala_count_today += amount
    mind_state.kusala_count_total += amount
    mind_state.updated_at = datetime.utcnow()
    
    await mind_state.save()
    logger.info(f"Incremented kusala for user {user_id} by {amount}")
    
    return MindStateResponse(**mind_state.dict())


@router.post("/{user_id}/increment-akusala", response_model=MindStateResponse)
async def increment_akusala(user_id: str, amount: int = 1):
    """
    Increment akusala (unwholesome) action count
    
    - **user_id**: User identifier
    - **amount**: Number to increment (default: 1)
    """
    mind_state = await get_mind_state_or_404(user_id)
    
    mind_state.akusala_count_today += amount
    mind_state.akusala_count_total += amount
    mind_state.updated_at = datetime.utcnow()
    
    await mind_state.save()
    logger.info(f"Incremented akusala for user {user_id} by {amount}")
    
    return MindStateResponse(**mind_state.dict())
