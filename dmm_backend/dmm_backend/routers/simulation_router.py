"""
Interactive Simulation API Router
Provides endpoints for scenario-based Buddhist practice simulation

Path: /api/simulation/*
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

# Import Phase 3 modules
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from modules.simulation_engine import (
    InteractiveSimulationEngine,
    Scenario,
    Choice,
    SimulationResponse,
    SimulationResult
)
# Note: CittaVithiEngine is integrated within simulation_engine
from modules.state_updater import RealTimeStateUpdater

# Phase 1: Database Integration imports
from documents import MindState, SimulationHistory, User

# Phase 2: Authentication
from dependencies.auth import get_current_user, get_optional_user

# Import Character model for updates
from documents_narrative import Character

router = APIRouter(
    prefix="/api/simulation",
    tags=["simulation"]
)

# ============================================================================
# Helper Functions
# ============================================================================

async def update_character_simulation_result(
    character_id: str,
    character_name: str,
    result,
    simulation_id: str
):
    """
    Update character with simulation results
    
    Args:
        character_id: Peace Script character ID
        character_name: Character name for logging
        result: SimulationResult from engine
        simulation_id: Unique simulation ID
    """
    try:
        # Find character in narrative system
        character = await Character.find_one({"character_id": character_id})
        
        if not character:
            print(f"⚠️ Character {character_id} not found in database")
            return
        
        # Initialize simulation tracking fields if not exist
        if not hasattr(character, 'simulation_count'):
            character.simulation_count = 0
        if not hasattr(character, 'simulation_history'):
            character.simulation_history = []
        
        # Update simulation count
        character.simulation_count += 1
        character.last_simulation = datetime.utcnow()
        
        # Create simulation history entry
        history_entry = {
            "simulation_id": simulation_id,
            "timestamp": datetime.utcnow(),
            "choice_type": result.choice_made.choice_type,
            "wisdom_gained": result.wisdom_gained,
            "state_changes": {
                "sila": result.state_after.get("virtue", {}).get("sila"),
                "samadhi": result.state_after.get("virtue", {}).get("samadhi"),
                "panna": result.state_after.get("virtue", {}).get("panna")
            }
        }
        
        # Append to history (keep last 50 simulations)
        character.simulation_history.append(history_entry)
        if len(character.simulation_history) > 50:
            character.simulation_history = character.simulation_history[-50:]
        
        # Save character
        await character.save()
        
        print(f"✅ Character '{character_name}' updated: {character.simulation_count} simulations")
        
    except Exception as e:
        print(f"❌ Error updating character {character_id}: {e}")


def calculate_active_hindrances(mind_state: MindState) -> dict:
    """
    Calculate active hindrances (Nīvaraṇa) from anusaya levels
    
    5 Hindrances (Nīvaraṇa):
    1. Kāmacchanda - Sensual desire (from lobha)
    2. Vyāpāda - Ill-will (from dosa)
    3. Thīna-middha - Sloth & torpor (from moha + thina)
    4. Uddhacca-kukkucca - Restlessness & worry (from uddhacca)
    5. Vicikicchā - Doubt (from vicikiccha)
    
    Args:
        mind_state: MindState with current_anusaya data
        
    Returns:
        Dict of active hindrances with levels (0-10)
    """
    anusaya = mind_state.current_anusaya
    
    # Calculate each hindrance from related anusaya
    hindrances = {
        "kamacchanda": anusaya.get("lobha", 0.0),  # Sensual desire from greed
        "vyapada": anusaya.get("dosa", 0.0),  # Ill-will from aversion
        "thina_middha": (anusaya.get("moha", 0.0) + anusaya.get("thina", 0.0)) / 2.0,  # Sloth from delusion
        "uddhacca_kukkucca": anusaya.get("moha", 0.0) * 0.7,  # Restlessness (estimate from moha)
        "vicikiccha": anusaya.get("vicikiccha", 0.0)  # Doubt
    }
    
    # Filter out hindrances below threshold (< 3.0 = not significantly active)
    active = {k: v for k, v in hindrances.items() if v >= 3.0}
    
    # If no active hindrances above threshold, return empty dict
    return active

# ============================================================================
# Request/Response Models
# ============================================================================

class ScenarioListResponse(BaseModel):
    """List of available scenarios"""
    scenarios: List[dict] = Field(..., description="Available scenarios with metadata")
    total: int = Field(..., description="Total number of scenarios")
    categories: List[str] = Field(..., description="Available categories")

class ScenarioDetailResponse(BaseModel):
    """Detailed scenario information"""
    scenario_id: str
    title: str
    description: str
    category: str
    difficulty: float
    sensory_input: dict
    choices: List[dict]
    
class SimulationRequest(BaseModel):
    """Request to run a simulation"""
    scenario_id: str = Field(..., description="Scenario ID to simulate")
    choice_index: int = Field(..., ge=0, le=2, description="Index of chosen option (0-2)")
    
    # User or Character mode
    user_id: Optional[str] = Field(None, description="User ID (if running as user)")
    character_id: Optional[str] = Field(None, description="Character ID (if running as character)")
    character_name: Optional[str] = Field(None, description="Character name for display")
    initial_mind_state: Optional[dict] = Field(None, description="Initial mind state for character mode")
    
    reflection: Optional[str] = Field(None, description="User's reflection on the choice")
    
class SimulationResultResponse(BaseModel):
    """Full simulation result with consequences"""
    simulation_id: str = Field(..., description="Unique simulation ID")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Choice made
    chosen_option: dict
    
    # Citta Vithi Result
    citta_result: dict
    
    # Consequences at 3 levels
    immediate_consequences: dict
    short_term_consequences: dict
    long_term_consequences: dict
    
    # Learning
    learning: dict
    
    # State changes
    state_before: dict
    state_after: dict
    changes: List[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "simulation_id": "sim_20250122_001",
                "timestamp": "2025-01-22T10:30:00",
                "chosen_option": {
                    "title": "สังเกตความอยาก แล้วเดินผ่าน",
                    "type": "kusala",
                    "difficulty": 7
                },
                "citta_result": {
                    "javana_citta": "มหากุศลจิต",
                    "kamma_potency": 0.0
                },
                "immediate_consequences": {
                    "description": "กุศลจิตเกิด รู้สึกสงบ มีสติ"
                },
                "learning": {
                    "wisdom": "เยี่ยมมาก! การมีสติช่วยให้เลือกกุศล",
                    "practice_tip": "ฝึกให้ชำนาญในการรู้ตัวเร็ว"
                },
                "changes": ["Kusala count increased", "Virtue slightly improved"]
            }
        }

class UserProgressResponse(BaseModel):
    """User's simulation progress and statistics"""
    user_id: str
    total_simulations: int
    kusala_choices: int
    akusala_choices: int
    neutral_choices: int
    favorite_scenarios: List[str]
    difficulty_progression: List[float]
    current_streak: int  # Days of consecutive practice
    
# ============================================================================
# Global Engine Instance (initialized on startup)
# ============================================================================

simulation_engine: Optional[InteractiveSimulationEngine] = None

def get_simulation_engine() -> InteractiveSimulationEngine:
    """Get or create simulation engine instance"""
    global simulation_engine
    
    if simulation_engine is None:
        # Create simulation engine (no parameters needed - self-contained)
        simulation_engine = InteractiveSimulationEngine()
    
    return simulation_engine

# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/scenarios", response_model=List[dict])
async def list_scenarios(
    category: Optional[str] = None,
    min_difficulty: Optional[float] = None,
    max_difficulty: Optional[float] = None
):
    """
    List all available scenarios
    
    Query Parameters:
    - category: Filter by category (temptation, conflict, practice)
    - min_difficulty: Minimum difficulty (0-10)
    - max_difficulty: Maximum difficulty (0-10)
    
    Returns: Array of scenario objects directly (consistent with other APIs)
    """
    engine = get_simulation_engine()
    
    # Get all scenarios
    all_scenarios = engine.list_scenarios()
    
    # Apply filters
    filtered = all_scenarios
    
    if category:
        filtered = [s for s in filtered if s["category"] == category]
    
    if min_difficulty is not None:
        filtered = [s for s in filtered if s["difficulty"] >= min_difficulty]
    
    if max_difficulty is not None:
        filtered = [s for s in filtered if s["difficulty"] <= max_difficulty]
    
    # Return array directly for consistency with Projects and Actors APIs
    return filtered

@router.get("/scenarios/{scenario_id}", response_model=ScenarioDetailResponse)
async def get_scenario_detail(scenario_id: str):
    """
    Get detailed information about a specific scenario
    
    Path Parameters:
    - scenario_id: ID of the scenario
    """
    engine = get_simulation_engine()
    
    scenario = engine.get_scenario(scenario_id)
    
    if not scenario:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found")
    
    # Calculate average difficulty from choices
    avg_difficulty = sum(c.difficulty for c in scenario.choices) / len(scenario.choices) if scenario.choices else 5.0
    
    # Convert to response format (map Scenario fields to response schema)
    return ScenarioDetailResponse(
        scenario_id=scenario.scenario_id,
        title=scenario.title,
        description=scenario.description,
        category=scenario.category,
        difficulty=avg_difficulty,
        sensory_input={
            "dvara": scenario.dvara_type,
            "description": scenario.sensory_description,
            "aramana_quality": "pleasant" if scenario.vedana_nature == "pleasant" else "unpleasant" if scenario.vedana_nature == "unpleasant" else "neutral",
            "vedana": scenario.vedana_nature,
            "intensity": scenario.intensity
        },
        choices=[
            {
                "title": choice.label,  # Fixed: Choice uses 'label' not 'title'
                "description": choice.description,
                "choice_type": choice.choice_type,
                "inner_dialogue": choice.inner_dialogue,
                "difficulty": choice.difficulty,
                "expected_citta": choice.expected_citta,
                "expected_kamma": choice.expected_kamma
            }
            for choice in scenario.choices
        ]
    )

@router.post("/simulate", response_model=SimulationResultResponse)
async def run_simulation(
    request: SimulationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Run an interactive simulation with user's choice
    🔒 Protected: Requires authentication
    
    Request Body:
    - scenario_id: Scenario to simulate
    - choice_index: Index of choice made (0-2)
    - character_id: (Optional) Character ID for character mode
    - character_name: (Optional) Character name
    - initial_mind_state: (Optional) Character's mind state
    - reflection: Optional user reflection
    
    Authentication:
    - User ID extracted from JWT token (no need to provide user_id)
    
    Returns:
    - Full simulation result with consequences and learning
    """
    engine = get_simulation_engine()
    
    # Determine if running in character mode or user mode
    is_character_mode = request.character_id is not None
    
    if is_character_mode:
        # Character mode: use virtual user_id and provided mind state
        user_id = f"char_{request.character_id}"
        print(f"🎭 Character mode: {request.character_name} ({request.character_id})")
    else:
        # User mode: use authenticated user
        user_id = str(current_user.id)
        print(f"👤 User mode: {user_id}")
    
    # Get scenario
    try:
        scenario = engine.get_scenario(request.scenario_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    # Validate choice index
    if request.choice_index >= len(scenario.choices):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid choice index. Scenario has {len(scenario.choices)} choices."
        )
    
    # Get the choice_id from the index
    selected_choice = scenario.choices[request.choice_index]
    choice_id = selected_choice.choice_id
    
    # Phase 1: Load MindState
    if is_character_mode and request.initial_mind_state:
        # Use provided character mind state
        mind_state_dict = request.initial_mind_state
        initial_state = {
            "user_id": user_id,
            "sila": mind_state_dict.get("sila", 5.0),
            "samadhi": mind_state_dict.get("samadhi", 4.0),
            "panna": mind_state_dict.get("panna", 4.0),
            "sati_strength": mind_state_dict.get("sati_strength", 5.0),
            "current_anusaya": mind_state_dict.get("current_anusaya", {}),
            "kusala_count_today": mind_state_dict.get("kusala_count", 0),
            "akusala_count_today": mind_state_dict.get("akusala_count", 0),
            "VirtueLevel": {
                "sila": mind_state_dict.get("sila", 5.0),
                "samadhi": mind_state_dict.get("samadhi", 4.0),
                "panna": mind_state_dict.get("panna", 4.0)
            },
            "total_kusala_count": 0,
            "total_akusala_count": 0,
            "active_hindrances": {}
        }
        print(f"✅ Using character mind state: sila={initial_state['sila']}, samadhi={initial_state['samadhi']}")
    else:
        # Load actual user's MindState from database
        mind_state = await MindState.find_one({"user_id": user_id})
        
        if not mind_state:
            # Create new user with default values
            mind_state = MindState(
                user_id=user_id,
                sila=5.0,
                samadhi=4.0,
                panna=4.0,
                sati_strength=5.0,
                current_anusaya={
                    "lobha": 3.0,
                    "dosa": 2.5,
                    "moha": 3.5,
                    "mana": 2.0,
                    "ditthi": 2.0,
                    "vicikiccha": 2.5,
                    "thina": 3.0
                },
                kusala_count_today=0,
                akusala_count_today=0,
                kusala_count_total=0,
                akusala_count_total=0,
                current_bhumi="puthujjana"
            )
            await mind_state.insert()
        
        # Convert MindState to simulation state dict
        initial_state = {
            "user_id": user_id,
            "sila": mind_state.sila,
            "samadhi": mind_state.samadhi,
            "panna": mind_state.panna,
            "sati_strength": mind_state.sati_strength,
            "current_anusaya": mind_state.current_anusaya,
            "kusala_count_today": mind_state.kusala_count_today,
            "akusala_count_today": mind_state.akusala_count_today,
            "VirtueLevel": {
                "sila": mind_state.sila,
                "samadhi": mind_state.samadhi,
                "panna": mind_state.panna
            },
            "total_kusala_count": mind_state.kusala_count_total,
            "total_akusala_count": mind_state.akusala_count_total,
            "active_hindrances": calculate_active_hindrances(mind_state)
        }
    
    # Run simulation
    try:
        result = await engine.simulate(
            scenario_id=request.scenario_id,
            choice_id=choice_id,
            current_state=initial_state,
            model_id=user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")
    
    # Generate unique simulation ID
    simulation_id = f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id[:8]}"
    
    # Extract consequence descriptions
    immediate_desc = result.immediate_consequences[0].description if result.immediate_consequences else "No immediate effect"
    short_term_desc = result.short_term_consequences[0].description if result.short_term_consequences else "No short-term effect"
    long_term_desc = result.long_term_consequences[0].description if result.long_term_consequences else "No long-term effect"
    
    # Extract state changes as list of strings
    state_changes = []
    if "virtue" in result.state_before and "virtue" in result.state_after:
        for key in ["sila", "samadhi", "panna"]:
            before = result.state_before.get("virtue", {}).get(key, 0)
            after = result.state_after.get("virtue", {}).get(key, 0)
            if after > before:
                state_changes.append(f"{key.capitalize()} increased: {before:.1f} → {after:.1f}")
            elif after < before:
                state_changes.append(f"{key.capitalize()} decreased: {before:.1f} → {after:.1f}")
    
    # Phase 1: Save simulation results to database
    try:
        # If character mode: update character, else update user MindState
        if is_character_mode and request.character_id:
            # Update character simulation results
            await update_character_simulation_result(
                character_id=request.character_id,
                character_name=request.character_name,
                result=result,
                simulation_id=simulation_id
            )
            print(f"✅ Updated character {request.character_name} with simulation results")
        else:
            # Update MindState with new values
            mind_state.sila = result.state_after.get("virtue", {}).get("sila", mind_state.sila)
            mind_state.samadhi = result.state_after.get("virtue", {}).get("samadhi", mind_state.samadhi)
            mind_state.panna = result.state_after.get("virtue", {}).get("panna", mind_state.panna)
            mind_state.kusala_count_today = result.state_after.get("kusala_count", mind_state.kusala_count_today)
            mind_state.akusala_count_today = result.state_after.get("akusala_count", mind_state.akusala_count_today)
            
            # Update total counters based on choice type
            if result.choice_made.choice_type == "kusala":
                mind_state.kusala_count_total += 1
            elif result.choice_made.choice_type == "akusala":
                mind_state.akusala_count_total += 1
            
            mind_state.updated_at = datetime.utcnow()
            await mind_state.save()
        
            # Create SimulationHistory record
            sim_history = SimulationHistory(
                simulation_id=simulation_id,
                user_id=user_id,
                scenario_id=request.scenario_id,
                scenario_title=scenario.title,
                choice_id=choice_id,
                choice_index=request.choice_index,
                choice_label=result.choice_made.label,
                choice_type=result.choice_made.choice_type,
                choice_difficulty=result.choice_made.difficulty,
                citta_generated=result.citta_generated,
                kamma_potency=result.kamma_generated,
                state_before=result.state_before,
                state_after=result.state_after,
                wisdom_gained=result.wisdom_gained,
                practice_tip=result.practice_tip,
                timestamp=datetime.utcnow()
            )
            await sim_history.insert()
        
    except Exception as e:
        # Log error but don't fail the response
        print(f"Warning: Failed to save simulation results: {e} - simulation_router.py:389")
    
    # Format response
    return SimulationResultResponse(
        simulation_id=simulation_id,
        timestamp=result.timestamp,
        chosen_option={
            "title": result.choice_made.label,
            "description": result.choice_made.description,
            "type": result.choice_made.choice_type,
            "difficulty": result.choice_made.difficulty
        },
        citta_result={
            "javana_citta": result.citta_generated,
            "kamma_potency": result.kamma_generated,
            "sati_intervened": False,  # Not yet implemented
            "total_duration_ms": 120  # Mock value
        },
        immediate_consequences={
            "description": immediate_desc,
            "visual_indicator": "✨" if result.choice_made.choice_type == "kusala" else "💥"
        },
        short_term_consequences={
            "description": short_term_desc,
            "visual_indicator": "🌱" if result.choice_made.choice_type == "kusala" else "🌪️"
        },
        long_term_consequences={
            "description": long_term_desc,
            "visual_indicator": "🏔️" if result.choice_made.choice_type == "kusala" else "⚡"
        },
        learning={
            "wisdom": result.wisdom_gained,
            "practice_tip": result.practice_tip,
            "scriptural_reference": None
        },
        state_before={
            "kusala_count": result.state_before.get("kusala_count", 0),
            "akusala_count": result.state_before.get("akusala_count", 0),
            "virtue": result.state_before.get("virtue", {"sila": 5.0, "samadhi": 4.0, "panna": 4.0})
        },
        state_after={
            "kusala_count": result.state_after.get("kusala_count", 0),
            "akusala_count": result.state_after.get("akusala_count", 0),
            "virtue": result.state_after.get("virtue", {"sila": 5.0, "samadhi": 4.0, "panna": 4.0})
        },
        changes=state_changes
    )

@router.get("/progress", response_model=UserProgressResponse)
async def get_user_progress(current_user: User = Depends(get_current_user)):
    """
    Get user's simulation progress and statistics
    🔒 Protected: Requires authentication
    
    Authentication:
    - User ID extracted from JWT token
    
    Phase 1: Query actual database for real statistics
    """
    user_id = str(current_user.id)
    
    # Get user's MindState
    mind_state = await MindState.find_one({"user_id": user_id})
    
    if not mind_state:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    
    # Query SimulationHistory for statistics
    all_simulations = await SimulationHistory.find(
        {"user_id": user_id}
    ).to_list()
    
    total_simulations = len(all_simulations)
    
    # Count by choice type
    kusala_count = sum(1 for sim in all_simulations if sim.choice_type == "kusala")
    akusala_count = sum(1 for sim in all_simulations if sim.choice_type == "akusala")
    neutral_count = sum(1 for sim in all_simulations if sim.choice_type not in ["kusala", "akusala"])
    
    # Find favorite scenarios (most frequently played)
    from collections import Counter
    scenario_counts = Counter(sim.scenario_id for sim in all_simulations)
    favorite_scenarios = [scenario_id for scenario_id, count in scenario_counts.most_common(3)]
    
    # Calculate difficulty progression (average difficulty over last 10 simulations)
    recent_sims = sorted(all_simulations, key=lambda x: x.timestamp)[-10:]
    difficulty_progression = [sim.difficulty_level for sim in recent_sims if sim.difficulty_level]
    
    # Calculate current streak (consecutive kusala choices)
    current_streak = 0
    for sim in reversed(sorted(all_simulations, key=lambda x: x.timestamp)):
        if sim.choice_type == "kusala":
            current_streak += 1
        else:
            break
    
    return UserProgressResponse(
        user_id=user_id,
        total_simulations=total_simulations,
        kusala_choices=kusala_count,
        akusala_choices=akusala_count,
        neutral_choices=neutral_count,
        favorite_scenarios=favorite_scenarios,
        difficulty_progression=difficulty_progression,
        current_streak=current_streak
    )

@router.get("/history")
async def get_simulation_history(
    current_user: User = Depends(get_current_user),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    group_by: str = "day"  # day, week, month
):
    """
    Get simulation history with aggregated statistics
    🔒 Protected: Requires authentication
    
    Query Parameters:
    - start_date: Filter from date (ISO format: YYYY-MM-DD)
    - end_date: Filter to date (ISO format: YYYY-MM-DD)
    - group_by: Grouping period (day, week, month)
    
    Returns:
    Array of time-period objects with kusala/akusala/neutral counts
    Used for EventKammaLog chart visualization
    """
    from datetime import datetime, timedelta
    from collections import defaultdict
    
    # Note: Use model_id instead of user_id for demo data
    # In production, you'd use user_id from current_user
    # user_id = str(current_user.id)
    
    # Build query filter (using all records for demo)
    query_filter = {}
    
    # Parse date filters
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query_filter["timestamp"] = {"$gte": start_dt}
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use ISO format (YYYY-MM-DD)")
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            if "timestamp" in query_filter:
                query_filter["timestamp"]["$lte"] = end_dt
            else:
                query_filter["timestamp"] = {"$lte": end_dt}
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use ISO format (YYYY-MM-DD)")
    
    # Query simulations
    simulations = await SimulationHistory.find(query_filter).sort(+SimulationHistory.timestamp).to_list()
    
    if not simulations:
        return []
    
    # Group by time period
    def get_period_key(timestamp, group_by):
        """Get grouping key based on group_by parameter"""
        if group_by == "day":
            return timestamp.strftime("%Y-%m-%d")
        elif group_by == "week":
            # ISO week format (YYYY-Www)
            return timestamp.strftime("%Y-W%W")
        elif group_by == "month":
            return timestamp.strftime("%Y-%m")
        else:
            return timestamp.strftime("%Y-%m-%d")
    
    # Aggregate by period
    period_data = defaultdict(lambda: {"kusala": 0, "akusala": 0, "neutral": 0})
    
    for sim in simulations:
        period_key = get_period_key(sim.timestamp, group_by)
        
        if sim.choice_type == "kusala":
            period_data[period_key]["kusala"] += 1
        elif sim.choice_type == "akusala":
            period_data[period_key]["akusala"] += 1
        else:
            period_data[period_key]["neutral"] += 1
    
    # Format response
    result = []
    for period, counts in sorted(period_data.items()):
        result.append({
            "period": period,
            "kusala_count": counts["kusala"],
            "akusala_count": counts["akusala"],
            "neutral_count": counts["neutral"],
            "total": counts["kusala"] + counts["akusala"] + counts["neutral"]
        })
    
    return result

@router.get("/analytics/emotions")
async def get_emotion_analytics(current_user: User = Depends(get_current_user)):
    """
    Get emotion distribution analytics from current MindState
    🔒 Protected: Requires authentication
    
    Returns:
    Emotion categories with percentages for donut chart:
    - greed: Lobha (craving, attachment)
    - contentment: Inverse of greed (satisfaction)
    - weak: Low energy states (thina, vicikiccha)
    
    Used for Right Panel Analytic donut chart
    """
    user_id = str(current_user.id)
    
    # Get user's current MindState
    mind_state = await MindState.find_one({"user_id": user_id})
    
    if not mind_state:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    
    # Extract anusaya values (scale 0-10)
    anusaya = mind_state.current_anusaya or {}
    
    lobha = anusaya.get("lobha", 0.0)  # Greed/craving
    dosa = anusaya.get("dosa", 0.0)    # Aversion/anger
    moha = anusaya.get("moha", 0.0)    # Delusion
    thina = anusaya.get("thina", 0.0)  # Sloth/torpor
    vicikiccha = anusaya.get("vicikiccha", 0.0)  # Doubt/uncertainty
    
    # Calculate emotion categories
    # Greed: lobha represents craving/attachment
    greed = lobha
    
    # Contentment: Inverse of greed + factor from virtue
    # High sila/samadhi indicates contentment
    virtue_factor = (mind_state.sila + mind_state.samadhi) / 2  # 0-10
    contentment = max(0, 10 - lobha) * (virtue_factor / 10)
    
    # Weak: Low energy states (thina + vicikiccha + factor from moha)
    weak = (thina + vicikiccha + moha * 0.5) / 2
    
    # Normalize to percentages (sum to 100)
    total = greed + contentment + weak
    
    if total == 0:
        # Default neutral state
        return {
            "greed": 33.3,
            "contentment": 33.3,
            "weak": 33.4,
            "raw_values": {
                "lobha": lobha,
                "virtue_average": virtue_factor,
                "thina": thina,
                "vicikiccha": vicikiccha
            }
        }
    
    greed_pct = (greed / total) * 100
    contentment_pct = (contentment / total) * 100
    weak_pct = (weak / total) * 100
    
    return {
        "greed": round(greed_pct, 1),
        "contentment": round(contentment_pct, 1),
        "weak": round(weak_pct, 1),
        "raw_values": {
            "lobha": lobha,
            "dosa": dosa,
            "moha": moha,
            "thina": thina,
            "vicikiccha": vicikiccha,
            "virtue_average": round(virtue_factor, 1)
        }
    }

@router.post("/scenarios/custom")
async def create_custom_scenario(
    scenario_data: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Create a custom scenario (admin only)
    
    Args:
        scenario_data: Scenario definition with:
            - scenario_id: Unique identifier
            - title: Scenario title
            - description: Full description
            - category: Category (daily_life, work, relationships, etc.)
            - difficulty: 1-10
            - sensory_input: {dvara, aramana_type, description, vedana, intensity}
            - choices: List of choice definitions
        current_user: Authenticated user (must be admin)
        
    Returns:
        Confirmation message with scenario_id
        
    Example:
        POST /api/simulation/scenarios/custom
        {
            "scenario_id": "custom_001",
            "title": "การประชุมที่น่าเบื่อ",
            "description": "คุณอยู่ในการประชุมที่ยืดเยื้อและน่าเบื่อ",
            "category": "work",
            "difficulty": 6.0,
            "sensory_input": {
                "dvara": "mind",
                "aramana_type": "mental",
                "description": "ความเบื่อหน่ายและอยากออกไป",
                "vedana": "dukkha",
                "intensity": 7.0
            },
            "choices": [
                {
                    "choice_id": "c1",
                    "title": "มีสติ สังเกตความเบื่อ",
                    "description": "ใช้สติสังเกตเวทนาเบื่อหน่าย",
                    "choice_type": "kusala",
                    "difficulty": 7.5
                },
                {
                    "choice_id": "c2",
                    "title": "เล่นโทรศัพท์แอบๆ",
                    "description": "หนีความเบื่อด้วยการดูโซเชียลมีเดีย",
                    "choice_type": "akusala",
                    "difficulty": 3.0
                }
            ]
        }
    """
    # Check admin permission
    if "admin" not in current_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can create custom scenarios"
        )
    
    # Validate required fields
    required_fields = ["scenario_id", "title", "description", "category", "difficulty", "sensory_input", "choices"]
    for field in required_fields:
        if field not in scenario_data:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required field: {field}"
            )
    
    # Validate choices
    if not isinstance(scenario_data["choices"], list) or len(scenario_data["choices"]) < 2:
        raise HTTPException(
            status_code=400,
            detail="Scenario must have at least 2 choices"
        )
    
    # Validate sensory_input structure
    sensory_required = ["dvara", "aramana_type", "description", "vedana", "intensity"]
    for field in sensory_required:
        if field not in scenario_data["sensory_input"]:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required field in sensory_input: {field}"
            )
    
    # Create Scenario object
    engine = get_simulation_engine()
    
    try:
        from modules.simulation_engine import Scenario, Choice
        from modules.citta_vithi_engine import SensoryInput, DvaraType, AramanaType, VedanaType
        
        # Map sensory input
        sensory = scenario_data["sensory_input"]
        dvara_map = {
            "eye": DvaraType.CAKKHU,
            "ear": DvaraType.SOTA,
            "nose": DvaraType.GHANA,
            "tongue": DvaraType.JIVHA,
            "body": DvaraType.KAYA,
            "mind": DvaraType.MANO
        }
        aramana_map = {
            "visible_form": AramanaType.RUPA,
            "sound": AramanaType.SADDA,
            "smell": AramanaType.GANDHA,
            "taste": AramanaType.RASA,
            "touch": AramanaType.PHOTTHABBA,
            "mental": AramanaType.DHAMMĀRAMMAṆA
        }
        vedana_map = {
            "sukha": VedanaType.SUKHA,
            "dukkha": VedanaType.DUKKHA,
            "upekkha": VedanaType.UPEKKHA,
            "pleasant": VedanaType.SUKHA,
            "unpleasant": VedanaType.DUKKHA,
            "neutral": VedanaType.UPEKKHA
        }
        
        sensory_input = SensoryInput(
            dvara=dvara_map.get(sensory["dvara"], DvaraType.MANO),
            aramana_type=aramana_map.get(sensory["aramana_type"], AramanaType.DHAMMĀRAMMAṆA),
            aramana_description=sensory["description"],
            natural_vedana=vedana_map.get(sensory["vedana"], VedanaType.UPEKKHA),
            intensity=float(sensory["intensity"])
        )
        
        # Create choices
        choices = []
        for choice_data in scenario_data["choices"]:
            choice = Choice(
                choice_id=choice_data.get("choice_id", f"c{len(choices)+1}"),
                title=choice_data["title"],
                description=choice_data["description"],
                choice_type=choice_data["choice_type"],
                difficulty=float(choice_data.get("difficulty", 5.0))
            )
            choices.append(choice)
        
        # Create scenario
        scenario = Scenario(
            scenario_id=scenario_data["scenario_id"],
            title=scenario_data["title"],
            description=scenario_data["description"],
            category=scenario_data["category"],
            difficulty=float(scenario_data["difficulty"]),
            sensory_input=sensory_input,
            choices=choices
        )
        
        # Add to engine (if engine has add_scenario method)
        if hasattr(engine, 'add_scenario'):
            engine.add_scenario(scenario)
        else:
            # Store in memory for current session
            if not hasattr(engine, 'custom_scenarios'):
                engine.custom_scenarios = {}
            engine.custom_scenarios[scenario.scenario_id] = scenario
        
        return {
            "status": "success",
            "message": f"Custom scenario '{scenario.title}' created successfully",
            "scenario_id": scenario.scenario_id,
            "choices_count": len(choices),
            "created_by": current_user.username,
            "created_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create scenario: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    engine = get_simulation_engine()
    scenarios = engine.list_scenarios()
    
    return {
        "status": "healthy",
        "available_scenarios": len(scenarios),
        "engine_initialized": simulation_engine is not None,
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# Startup Event
# ============================================================================

@router.on_event("startup")
async def startup_event():
    """Initialize simulation engine on startup"""
    global simulation_engine
    
    print("🎭 Initializing Interactive Simulation Engine... - simulation_router.py:696")
    
    # Pre-initialize engine
    get_simulation_engine()
    
    scenarios = simulation_engine.list_scenarios()
    print(f"✅ Simulation Engine Ready: {len(scenarios)} scenarios loaded - simulation_router.py:702")
    
    for scenario in scenarios:
        print(f"[{scenario['category']}] {scenario['title']} (difficulty: {scenario['difficulty']}/10) - simulation_router.py:705")
