"""
Integration Tests for Phase 3.4: Interactive Simulation Engine
Tests full simulation flow from scenario loading to consequence generation
"""

import pytest
import asyncio
from modules.simulation_engine import (
    InteractiveSimulationEngine,
    Scenario,
    SimulationResponse,
    SimulationResult
)
from modules.citta_vithi_engine import CittaVithiEngine
from modules.state_updater import RealTimeStateUpdater
from models.api_models import MindState

# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mind_state():
    """Create a test mind state"""
    return MindState(
        user_id="test_user",
        sila=5.0,
        samadhi=4.0,
        panna=4.0,
        sati_strength=5.0,
        current_anusaya={
            "lobha": 3.0,
            "dosa": 2.5,
            "moha": 3.5
        },
        kusala_count_today=10,
        akusala_count_today=5
    )

@pytest.fixture
def citta_engine(mind_state):
    """Create citta vithi engine"""
    return CittaVithiEngine(mind_state=mind_state)

@pytest.fixture
def state_updater():
    """Create state updater"""
    return RealTimeStateUpdater()

@pytest.fixture
def simulation_engine(citta_engine, state_updater):
    """Create simulation engine with dependencies"""
    return InteractiveSimulationEngine(
        citta_engine=citta_engine,
        state_updater=state_updater
    )

# ============================================================================
# Test Scenario Management
# ============================================================================

def test_list_scenarios(simulation_engine):
    """Test listing available scenarios"""
    scenarios = simulation_engine.list_scenarios()
    
    assert len(scenarios) >= 3
    assert all("scenario_id" in s for s in scenarios)
    assert all("title" in s for s in scenarios)
    assert all("category" in s for s in scenarios)
    assert all("difficulty" in s for s in scenarios)

def test_get_scenario_marketplace(simulation_engine):
    """Test getting marketplace scenario"""
    scenario = simulation_engine.get_scenario("marketplace_expensive")
    
    assert scenario.scenario_id == "marketplace_expensive"
    assert scenario.category == "temptation"
    assert len(scenario.choices) == 3
    assert scenario.sensory_input.dvara == "eye"

def test_get_scenario_conflict(simulation_engine):
    """Test getting conflict scenario"""
    scenario = simulation_engine.get_scenario("conflict_insult")
    
    assert scenario.scenario_id == "conflict_insult"
    assert scenario.category == "conflict"
    assert len(scenario.choices) == 3

def test_get_scenario_meditation(simulation_engine):
    """Test getting meditation scenario"""
    scenario = simulation_engine.get_scenario("meditation_wandering")
    
    assert scenario.scenario_id == "meditation_wandering"
    assert scenario.category == "practice"
    assert len(scenario.choices) == 3

def test_get_invalid_scenario(simulation_engine):
    """Test getting non-existent scenario"""
    with pytest.raises(ValueError):
        simulation_engine.get_scenario("nonexistent_scenario")

# ============================================================================
# Test Simulation Flow - Kusala Choice
# ============================================================================

@pytest.mark.asyncio
async def test_simulate_marketplace_kusala(simulation_engine, mind_state):
    """Test marketplace scenario with kusala choice"""
    response = SimulationResponse(
        choice_index=0,  # Kusala choice: observe desire mindfully
        reflection="ฉันรู้สึกว่าความอยากเป็นอนิจจัง"
    )
    
    result = await simulation_engine.simulate(
        scenario_id="marketplace_expensive",
        response=response,
        initial_state=mind_state
    )
    
    # Check basic result structure
    assert isinstance(result, SimulationResult)
    assert result.chosen_choice.choice_type == "kusala"
    
    # Check citta result
    assert result.citta_result.javana_type == "kusala"
    assert result.citta_result.kamma_potency == 0.0
    
    # Check consequences exist
    assert result.immediate_consequences is not None
    assert result.short_term_consequences is not None
    assert result.long_term_consequences is not None
    
    # Check learning
    assert "wisdom" in result.learning
    assert "practice_tip" in result.learning
    
    # Check state changes
    assert result.state_after.kusala_count_today > result.state_before.kusala_count_today
    assert result.state_after.akusala_count_today == result.state_before.akusala_count_today
    
    # Check virtue increased or stayed same
    assert result.state_after.sila >= result.state_before.sila
    assert result.state_after.samadhi >= result.state_before.samadhi
    assert result.state_after.panna >= result.state_before.panna

# ============================================================================
# Test Simulation Flow - Akusala Choice
# ============================================================================

@pytest.mark.asyncio
async def test_simulate_marketplace_akusala(simulation_engine, mind_state):
    """Test marketplace scenario with akusala choice"""
    response = SimulationResponse(
        choice_index=1,  # Akusala choice: buy impulsively
        reflection="ต้องมี! สวยมาก!"
    )
    
    result = await simulation_engine.simulate(
        scenario_id="marketplace_expensive",
        response=response,
        initial_state=mind_state
    )
    
    # Check choice type
    assert result.chosen_choice.choice_type == "akusala"
    
    # Check citta result
    assert result.citta_result.javana_type == "akusala"
    assert result.citta_result.kamma_potency > 0
    
    # Check state changes
    assert result.state_after.akusala_count_today > result.state_before.akusala_count_today
    
    # Check virtue decreased
    assert result.state_after.sila <= result.state_before.sila
    assert result.state_after.samadhi <= result.state_before.samadhi
    assert result.state_after.panna <= result.state_before.panna

# ============================================================================
# Test Simulation Flow - Neutral Choice
# ============================================================================

@pytest.mark.asyncio
async def test_simulate_marketplace_neutral(simulation_engine, mind_state):
    """Test marketplace scenario with neutral choice"""
    response = SimulationResponse(
        choice_index=2,  # Neutral choice: take photo, postpone
        reflection="สวยจัง แต่คงไม่จำเป็นตอนนี้"
    )
    
    result = await simulation_engine.simulate(
        scenario_id="marketplace_expensive",
        response=response,
        initial_state=mind_state
    )
    
    # Check choice type
    assert result.chosen_choice.choice_type == "neutral"
    
    # Check citta result (can be ahetuka or subtle kusala/akusala)
    assert result.citta_result.javana_type in ["neutral", "kusala", "akusala"]
    
    # Kamma should be low for neutral
    assert result.citta_result.kamma_potency < 200

# ============================================================================
# Test Different Scenarios
# ============================================================================

@pytest.mark.asyncio
async def test_simulate_conflict_kusala(simulation_engine, mind_state):
    """Test conflict scenario with kusala response"""
    response = SimulationResponse(
        choice_index=0,  # Kusala: breathe, practice khanti
        reflection="ความโกรธเป็นทุกข์ ฉันจะไม่สร้างอกุศลกรรม"
    )
    
    result = await simulation_engine.simulate(
        scenario_id="conflict_insult",
        response=response,
        initial_state=mind_state
    )
    
    assert result.chosen_choice.choice_type == "kusala"
    assert result.citta_result.javana_type == "kusala"
    
    # Conflict kusala is harder - check high difficulty
    assert result.chosen_choice.difficulty >= 7.0

@pytest.mark.asyncio
async def test_simulate_conflict_akusala(simulation_engine, mind_state):
    """Test conflict scenario with akusala response"""
    response = SimulationResponse(
        choice_index=1,  # Akusala: retaliate angrily
        reflection="กล้าดียังไง! จะไม่ปล่อยให้เขาดูถูก!"
    )
    
    result = await simulation_engine.simulate(
        scenario_id="conflict_insult",
        response=response,
        initial_state=mind_state
    )
    
    assert result.chosen_choice.choice_type == "akusala"
    assert result.citta_result.javana_subtype == "dosa"
    assert result.citta_result.kamma_potency > 700  # High kamma for dosa

@pytest.mark.asyncio
async def test_simulate_meditation_kusala(simulation_engine, mind_state):
    """Test meditation scenario with kusala response"""
    response = SimulationResponse(
        choice_index=0,  # Kusala: notice wandering, return to breath
        reflection="การรู้ว่าฟุ้งซ่าน ก็คือสติ"
    )
    
    result = await simulation_engine.simulate(
        scenario_id="meditation_wandering",
        response=response,
        initial_state=mind_state
    )
    
    assert result.chosen_choice.choice_type == "kusala"
    assert result.citta_result.javana_type == "kusala"

# ============================================================================
# Test Consequence Generation
# ============================================================================

@pytest.mark.asyncio
async def test_immediate_consequences(simulation_engine, mind_state):
    """Test immediate consequence generation"""
    response = SimulationResponse(choice_index=0)
    
    result = await simulation_engine.simulate(
        scenario_id="marketplace_expensive",
        response=response,
        initial_state=mind_state
    )
    
    immediate = result.immediate_consequences
    
    # Should have description
    assert len(immediate.description) > 0
    
    # Should mention citta type
    assert "กุศล" in immediate.description or "kusala" in immediate.description.lower()
    
    # Should have visual indicator
    assert len(immediate.visual_indicator) > 0

@pytest.mark.asyncio
async def test_short_term_consequences(simulation_engine, mind_state):
    """Test short-term consequence generation"""
    response = SimulationResponse(choice_index=0)
    
    result = await simulation_engine.simulate(
        scenario_id="marketplace_expensive",
        response=response,
        initial_state=mind_state
    )
    
    short_term = result.short_term_consequences
    
    # Should mention hindrances or virtue
    assert "นิวรณ์" in short_term.description or "ศีล" in short_term.description

@pytest.mark.asyncio
async def test_long_term_consequences(simulation_engine, mind_state):
    """Test long-term consequence generation"""
    response = SimulationResponse(choice_index=1)  # Akusala
    
    result = await simulation_engine.simulate(
        scenario_id="marketplace_expensive",
        response=response,
        initial_state=mind_state
    )
    
    long_term = result.long_term_consequences
    
    # Should mention kamma
    assert "กรรม" in long_term.description or "kamma" in long_term.description.lower()

# ============================================================================
# Test Learning Generation
# ============================================================================

@pytest.mark.asyncio
async def test_learning_wisdom(simulation_engine, mind_state):
    """Test wisdom generation"""
    response = SimulationResponse(choice_index=0)  # Kusala
    
    result = await simulation_engine.simulate(
        scenario_id="marketplace_expensive",
        response=response,
        initial_state=mind_state
    )
    
    wisdom = result.learning.get("wisdom", "")
    
    # Should praise kusala choice
    assert len(wisdom) > 0
    assert "ดี" in wisdom or "เยี่ยม" in wisdom

@pytest.mark.asyncio
async def test_learning_practice_tip(simulation_engine, mind_state):
    """Test practice tip generation"""
    response = SimulationResponse(choice_index=0)  # Kusala
    
    result = await simulation_engine.simulate(
        scenario_id="marketplace_expensive",
        response=response,
        initial_state=mind_state
    )
    
    practice_tip = result.learning.get("practice_tip", "")
    
    # Should provide actionable advice
    assert len(practice_tip) > 0
    assert "ฝึก" in practice_tip or "practice" in practice_tip.lower()

# ============================================================================
# Test State Changes
# ============================================================================

@pytest.mark.asyncio
async def test_state_changes_recorded(simulation_engine, mind_state):
    """Test that state changes are recorded"""
    response = SimulationResponse(choice_index=0)
    
    result = await simulation_engine.simulate(
        scenario_id="marketplace_expensive",
        response=response,
        initial_state=mind_state
    )
    
    # Should have change list
    assert len(result.state_changes) > 0
    
    # Changes should be strings
    assert all(isinstance(change, str) for change in result.state_changes)

@pytest.mark.asyncio
async def test_state_before_after_different(simulation_engine, mind_state):
    """Test that state actually changes"""
    response = SimulationResponse(choice_index=1)  # Akusala
    
    result = await simulation_engine.simulate(
        scenario_id="marketplace_expensive",
        response=response,
        initial_state=mind_state
    )
    
    # Akusala count should increase
    assert result.state_after.akusala_count_today > result.state_before.akusala_count_today
    
    # Virtue should decrease (at least one dimension)
    virtue_decreased = (
        result.state_after.sila < result.state_before.sila or
        result.state_after.samadhi < result.state_before.samadhi or
        result.state_after.panna < result.state_before.panna
    )
    assert virtue_decreased

# ============================================================================
# Test Edge Cases
# ============================================================================

@pytest.mark.asyncio
async def test_invalid_choice_index(simulation_engine, mind_state):
    """Test simulation with invalid choice index"""
    response = SimulationResponse(choice_index=99)  # Out of range
    
    with pytest.raises((ValueError, IndexError)):
        await simulation_engine.simulate(
            scenario_id="marketplace_expensive",
            response=response,
            initial_state=mind_state
        )

@pytest.mark.asyncio
async def test_simulation_with_reflection(simulation_engine, mind_state):
    """Test that reflection is captured"""
    reflection_text = "นี่คือความคิดของฉัน"
    response = SimulationResponse(
        choice_index=0,
        reflection=reflection_text
    )
    
    result = await simulation_engine.simulate(
        scenario_id="marketplace_expensive",
        response=response,
        initial_state=mind_state
    )
    
    # Reflection should be accessible (in result or metadata)
    assert result is not None

# ============================================================================
# Test Multiple Simulations
# ============================================================================

@pytest.mark.asyncio
async def test_multiple_simulations_sequential(simulation_engine, mind_state):
    """Test running multiple simulations sequentially"""
    initial_kusala = mind_state.kusala_count_today
    
    # Run 3 kusala simulations
    for _ in range(3):
        response = SimulationResponse(choice_index=0)  # Kusala
        result = await simulation_engine.simulate(
            scenario_id="marketplace_expensive",
            response=response,
            initial_state=mind_state
        )
    
    # Kusala count should have increased by 3
    assert mind_state.kusala_count_today == initial_kusala + 3

@pytest.mark.asyncio
async def test_alternating_kusala_akusala(simulation_engine, mind_state):
    """Test alternating kusala and akusala choices"""
    initial_kusala = mind_state.kusala_count_today
    initial_akusala = mind_state.akusala_count_today
    
    # Kusala
    response1 = SimulationResponse(choice_index=0)
    await simulation_engine.simulate(
        scenario_id="marketplace_expensive",
        response=response1,
        initial_state=mind_state
    )
    
    # Akusala
    response2 = SimulationResponse(choice_index=1)
    await simulation_engine.simulate(
        scenario_id="marketplace_expensive",
        response=response2,
        initial_state=mind_state
    )
    
    # Both counters should increase
    assert mind_state.kusala_count_today == initial_kusala + 1
    assert mind_state.akusala_count_today == initial_akusala + 1

# ============================================================================
# Performance Tests
# ============================================================================

@pytest.mark.asyncio
async def test_simulation_performance(simulation_engine, mind_state):
    """Test that simulation completes within acceptable time"""
    import time
    
    response = SimulationResponse(choice_index=0)
    
    start = time.time()
    result = await simulation_engine.simulate(
        scenario_id="marketplace_expensive",
        response=response,
        initial_state=mind_state
    )
    duration = time.time() - start
    
    # Should complete in less than 100ms
    assert duration < 0.1

@pytest.mark.asyncio
async def test_scenario_loading_performance(simulation_engine):
    """Test that scenario loading is fast"""
    import time
    
    start = time.time()
    scenario = simulation_engine.get_scenario("marketplace_expensive")
    duration = time.time() - start
    
    # Should complete in less than 10ms
    assert duration < 0.01

# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_full_pipeline_integration(simulation_engine, mind_state):
    """Test complete pipeline from scenario to learning"""
    # 1. List scenarios
    scenarios = simulation_engine.list_scenarios()
    assert len(scenarios) > 0
    
    # 2. Get scenario details
    scenario = simulation_engine.get_scenario(scenarios[0]["scenario_id"])
    assert scenario is not None
    
    # 3. Run simulation
    response = SimulationResponse(choice_index=0)
    result = await simulation_engine.simulate(
        scenario_id=scenario.scenario_id,
        response=response,
        initial_state=mind_state
    )
    
    # 4. Verify all components present
    assert result.citta_result is not None
    assert result.immediate_consequences is not None
    assert result.short_term_consequences is not None
    assert result.long_term_consequences is not None
    assert result.learning is not None
    assert len(result.state_changes) > 0

# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
