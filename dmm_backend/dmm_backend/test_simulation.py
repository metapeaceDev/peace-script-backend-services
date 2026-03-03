#!/usr/bin/env python3
"""
Test script for simulation API with database integration
Phase 1: Database Integration Testing
"""

import asyncio
import sys
from datetime import datetime
from typing import Optional

# Import our models and router
from database import init_db
from documents import MindState, SimulationHistory
from routers.simulation_router import get_simulation_engine
from pydantic import BaseModel, Field


class SimulationRequest(BaseModel):
    """Request to run a simulation"""
    scenario_id: str
    choice_index: int
    user_id: str
    reflection: Optional[str] = None


async def test_simulation():
    """Test the complete simulation flow with database"""
    
    print("🧪 Starting Simulation Test with Database Integration\n")
    print("=" * 60)
    
    # Initialize database
    print("📦 Step 1: Initializing database...")
    await init_db()
    print("✅ Database initialized\n")
    
    # Check if test user exists
    print("👤 Step 2: Loading user from database...")
    user_id = "test_user_001"
    mind_state = await MindState.find_one({"user_id": user_id})
    
    if mind_state:
        print(f"✅ Found user: {user_id}")
        print(f"   Sila: {mind_state.sila}, Samadhi: {mind_state.samadhi}, Panna: {mind_state.panna}")
        print(f"   Kusala/Akusala (total): {mind_state.kusala_count_total}/{mind_state.akusala_count_total}")
    else:
        print(f"❌ User {user_id} not found")
        return
    
    print()
    
    # Get simulation engine
    print("🎭 Step 3: Getting simulation engine...")
    engine = get_simulation_engine()
    scenario_list = engine.list_scenarios()
    print(f"✅ Loaded {len(scenario_list)} scenarios")
    for s in scenario_list:
        print(f"   - {s['scenario_id']}: {s['title']}")
    print()
    
    # Prepare simulation request
    print("⚡ Step 4: Running simulation...")
    request = SimulationRequest(
        user_id=user_id,
        scenario_id="marketplace_expensive",
        choice_index=0  # First choice (usually kusala)
    )
    
    # Get scenario and choice
    scenario = engine.get_scenario(request.scenario_id)
    if not scenario:
        print(f"❌ Scenario {request.scenario_id} not found")
        return
    
    selected_choice = scenario.choices[request.choice_index]
    choice_id = selected_choice.choice_id
    
    print(f"   Scenario: {scenario.title}")
    print(f"   Choice #{request.choice_index}: {selected_choice.label}")
    print(f"   Type: {selected_choice.choice_type}")
    print()
    
    # Prepare initial state from database
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
        "active_hindrances": {}
    }
    
    # Run simulation
    result = await engine.simulate(
        scenario_id=request.scenario_id,
        choice_id=choice_id,
        current_state=initial_state,
        model_id=user_id
    )
    
    print(f"✅ Simulation completed!")
    print(f"   Citta Generated: {result.citta_generated}")
    print(f"   Kamma Potency: {result.kamma_generated}")
    print(f"   Wisdom Gained: {result.wisdom_gained}")
    print()
    
    # Update database
    print("💾 Step 5: Saving results to database...")
    
    # Update MindState
    mind_state.sila = result.state_after.get("virtue", {}).get("sila", mind_state.sila)
    mind_state.samadhi = result.state_after.get("virtue", {}).get("samadhi", mind_state.samadhi)
    mind_state.panna = result.state_after.get("virtue", {}).get("panna", mind_state.panna)
    mind_state.kusala_count_today = result.state_after.get("kusala_count", mind_state.kusala_count_today)
    mind_state.akusala_count_today = result.state_after.get("akusala_count", mind_state.akusala_count_today)
    
    if result.choice_made.choice_type == "kusala":
        mind_state.kusala_count_total += 1
    elif result.choice_made.choice_type == "akusala":
        mind_state.akusala_count_total += 1
    
    mind_state.updated_at = datetime.utcnow()
    await mind_state.save()
    print("✅ MindState updated")
    
    # Create SimulationHistory
    simulation_id = f"sim_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
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
    print(f"✅ SimulationHistory created: {simulation_id}")
    print()
    
    # Verify saved data
    print("🔍 Step 6: Verifying saved data...")
    updated_mind = await MindState.find_one({"user_id": user_id})
    print(f"   Updated Kusala/Akusala: {updated_mind.kusala_count_total}/{updated_mind.akusala_count_total}")
    
    history_count = await SimulationHistory.find({"user_id": user_id}).count()
    print(f"   Total simulations in history: {history_count}")
    print()
    
    print("=" * 60)
    print("✨ TEST COMPLETE! Database Integration Working 🎉")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(test_simulation())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
