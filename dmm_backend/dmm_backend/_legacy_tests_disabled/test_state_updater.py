"""
Unit Tests for Phase 3.3: Real-time State Updater
Tests state updates, hindrance tracking, kamma maturation, and virtue changes
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from modules.state_updater import (
    RealTimeStateUpdater,
    ActiveHindrance,
    KammaQueueEntry,
    MindStateSnapshot,
    StateUpdateResult
)
from models.api_models import MindState
from modules.citta_vithi_engine import CittaVithiResult

# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def updater():
    """Create a state updater instance"""
    return RealTimeStateUpdater()

@pytest.fixture
def initial_state():
    """Create an initial mind state"""
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
        akusala_count_today=5,
        consciousness_state="bhavanga",
        active_hindrances={},
        kamma_queue=[]
    )

@pytest.fixture
def akusala_lobha_result():
    """Create an akusala lobha citta vithi result"""
    return CittaVithiResult(
        javana_citta="โลภมูลจิต",
        javana_type="akusala",
        javana_subtype="lobha",
        kamma_potency=650.0,
        sati_intervened=False,
        sequence=[],  # Simplified for testing
        total_duration_ms=280
    )

@pytest.fixture
def kusala_result():
    """Create a kusala citta vithi result"""
    return CittaVithiResult(
        javana_citta="มหากุศลจิต",
        javana_type="kusala",
        javana_subtype="dana",
        kamma_potency=0.0,
        sati_intervened=False,
        sequence=[],
        total_duration_ms=290
    )

# ============================================================================
# Test State Updates After Vithi
# ============================================================================

@pytest.mark.asyncio
async def test_update_after_akusala_vithi(updater, initial_state, akusala_lobha_result):
    """Test state update after akusala lobha vithi"""
    result = await updater.update_after_vithi(initial_state, akusala_lobha_result)
    
    # Check that changes were recorded
    assert len(result.changes) > 0
    
    # Check consciousness state returned to bhavanga
    assert result.state_snapshot.consciousness_state == "bhavanga"
    assert result.state_snapshot.last_citta == "โลภมูลจิต"
    
    # Check counters updated
    assert result.state_snapshot.kusala_count == initial_state.kusala_count_today
    assert result.state_snapshot.akusala_count == initial_state.akusala_count_today + 1
    
    # Check hindrances increased (kāmacchanda for lobha)
    assert "kāmacchanda" in result.state_snapshot.active_hindrances
    assert result.state_snapshot.active_hindrances["kāmacchanda"] > 0
    
    # Check kamma added to queue
    assert result.state_snapshot.kamma_queue_size == 1
    
    # Check virtue decreased
    assert result.state_snapshot.virtue_levels["sila"] < initial_state.sila
    assert result.state_snapshot.virtue_levels["samadhi"] < initial_state.samadhi
    assert result.state_snapshot.virtue_levels["panna"] < initial_state.panna

@pytest.mark.asyncio
async def test_update_after_kusala_vithi(updater, initial_state, kusala_result):
    """Test state update after kusala vithi"""
    result = await updater.update_after_vithi(initial_state, kusala_result)
    
    # Check kusala count increased
    assert result.state_snapshot.kusala_count == initial_state.kusala_count_today + 1
    assert result.state_snapshot.akusala_count == initial_state.akusala_count_today
    
    # Check no kamma added (kusala kamma = 0)
    assert result.state_snapshot.kamma_queue_size == 0
    
    # Check virtue increased
    assert result.state_snapshot.virtue_levels["sila"] >= initial_state.sila
    assert result.state_snapshot.virtue_levels["samadhi"] >= initial_state.samadhi
    assert result.state_snapshot.virtue_levels["panna"] >= initial_state.panna

# ============================================================================
# Test Hindrance Management
# ============================================================================

@pytest.mark.asyncio
async def test_hindrance_increases_on_akusala(updater, initial_state, akusala_lobha_result):
    """Test that hindrances increase on akusala"""
    result = await updater.update_after_vithi(initial_state, akusala_lobha_result)
    
    # Lobha should increase kāmacchanda
    assert "kāmacchanda" in result.state_snapshot.active_hindrances
    hindrance_level = result.state_snapshot.active_hindrances["kāmacchanda"]
    assert hindrance_level > 0

@pytest.mark.asyncio
async def test_hindrance_decreases_on_kusala(updater, initial_state, kusala_result):
    """Test that hindrances decrease on kusala"""
    # Set initial hindrances
    initial_state.active_hindrances = {
        "kāmacchanda": 5.0,
        "byāpāda": 3.0
    }
    
    result = await updater.update_after_vithi(initial_state, kusala_result)
    
    # Hindrances should decrease
    if "kāmacchanda" in result.state_snapshot.active_hindrances:
        assert result.state_snapshot.active_hindrances["kāmacchanda"] < 5.0
    if "byāpāda" in result.state_snapshot.active_hindrances:
        assert result.state_snapshot.active_hindrances["byāpāda"] < 3.0

def test_hindrance_decay_over_time(updater):
    """Test that hindrances decay over time"""
    state = MindState(
        user_id="test_user",
        sila=5.0,
        samadhi=4.0,
        panna=4.0,
        sati_strength=5.0,
        current_anusaya={"lobha": 3.0},
        active_hindrances={
            "kāmacchanda": 5.0,
            "byāpāda": 3.0
        },
        last_decay_time=datetime.now() - timedelta(hours=2)  # 2 hours ago
    )
    
    updated_state = updater.decay_hindrances(state)
    
    # After 2 hours, decay should be 0.1 * 2 = 0.2
    assert updated_state.active_hindrances["kāmacchanda"] < 5.0
    assert updated_state.active_hindrances["byāpāda"] < 3.0
    
    # Check decay is approximately correct (0.1 per hour)
    expected_kama = max(0, 5.0 - 0.2)
    expected_byapada = max(0, 3.0 - 0.2)
    
    assert abs(updated_state.active_hindrances["kāmacchanda"] - expected_kama) < 0.1
    assert abs(updated_state.active_hindrances["byāpāda"] - expected_byapada) < 0.1

# ============================================================================
# Test Kamma Queue Management
# ============================================================================

@pytest.mark.asyncio
async def test_kamma_added_to_queue(updater, initial_state, akusala_lobha_result):
    """Test that kamma is added to queue"""
    result = await updater.update_after_vithi(initial_state, akusala_lobha_result)
    
    assert result.state_snapshot.kamma_queue_size == 1
    
    # Check kamma entry in actual state
    assert len(initial_state.kamma_queue) == 1
    entry = initial_state.kamma_queue[0]
    
    assert entry["citta_type"] == "โลภมูลจิต"
    assert entry["potency"] == akusala_lobha_result.kamma_potency
    assert entry["maturity_level"] == "seed"
    assert entry["maturity_percentage"] == 0.0

def test_kamma_maturation_progress(updater):
    """Test that kamma matures over time"""
    state = MindState(
        user_id="test_user",
        sila=5.0,
        samadhi=4.0,
        panna=4.0,
        sati_strength=5.0,
        current_anusaya={"lobha": 3.0},
        kamma_queue=[
            {
                "citta_type": "โลภมูลจิต",
                "potency": 500.0,
                "maturity_level": "seed",
                "maturity_percentage": 0.0,
                "timestamp": (datetime.now() - timedelta(days=7)).isoformat()
            }
        ]
    )
    
    # Mature kamma over 7 days
    updated_state = updater.mature_kamma(state, days_elapsed=7)
    
    # Kamma should have progressed
    entry = updated_state.kamma_queue[0]
    assert entry["maturity_percentage"] > 0.0
    assert entry["maturity_level"] in ["seed", "germinating", "growing"]

def test_kamma_maturation_stages(updater):
    """Test kamma progresses through all maturation stages"""
    state = MindState(
        user_id="test_user",
        sila=5.0,
        samadhi=4.0,
        panna=4.0,
        sati_strength=5.0,
        current_anusaya={"lobha": 3.0},
        kamma_queue=[
            {
                "citta_type": "โลภมูลจิต",
                "potency": 800.0,
                "maturity_level": "seed",
                "maturity_percentage": 0.0,
                "timestamp": (datetime.now() - timedelta(days=100)).isoformat()
            }
        ]
    )
    
    # Mature over long period
    updated_state = updater.mature_kamma(state, days_elapsed=100)
    
    entry = updated_state.kamma_queue[0]
    
    # Should reach mature or beyond
    assert entry["maturity_level"] in ["mature", "fruiting", "exhausted"]
    assert entry["maturity_percentage"] >= 100.0

# ============================================================================
# Test Virtue Level Changes
# ============================================================================

@pytest.mark.asyncio
async def test_virtue_increases_gradually(updater, initial_state, kusala_result):
    """Test that virtue increases gradually"""
    result = await updater.update_after_vithi(initial_state, kusala_result)
    
    # Changes should be small (max 0.1)
    sila_change = abs(result.state_snapshot.virtue_levels["sila"] - initial_state.sila)
    samadhi_change = abs(result.state_snapshot.virtue_levels["samadhi"] - initial_state.samadhi)
    panna_change = abs(result.state_snapshot.virtue_levels["panna"] - initial_state.panna)
    
    assert sila_change <= 0.1
    assert samadhi_change <= 0.1
    assert panna_change <= 0.1

@pytest.mark.asyncio
async def test_virtue_decreases_on_akusala(updater, initial_state, akusala_lobha_result):
    """Test that virtue decreases on akusala"""
    initial_sila = initial_state.sila
    initial_samadhi = initial_state.samadhi
    initial_panna = initial_state.panna
    
    result = await updater.update_after_vithi(initial_state, akusala_lobha_result)
    
    # Virtue should decrease
    assert result.state_snapshot.virtue_levels["sila"] < initial_sila
    assert result.state_snapshot.virtue_levels["samadhi"] < initial_samadhi
    assert result.state_snapshot.virtue_levels["panna"] < initial_panna

@pytest.mark.asyncio
async def test_virtue_stays_within_bounds(updater, initial_state, kusala_result):
    """Test that virtue stays within 0-10 bounds"""
    # Set very high initial virtue
    initial_state.sila = 9.95
    initial_state.samadhi = 9.95
    initial_state.panna = 9.95
    
    # Multiple kusala vithis
    for _ in range(20):
        result = await updater.update_after_vithi(initial_state, kusala_result)
    
    # Should not exceed 10
    assert result.state_snapshot.virtue_levels["sila"] <= 10.0
    assert result.state_snapshot.virtue_levels["samadhi"] <= 10.0
    assert result.state_snapshot.virtue_levels["panna"] <= 10.0

# ============================================================================
# Test Threshold Triggers
# ============================================================================

@pytest.mark.asyncio
async def test_appearance_update_trigger(updater, initial_state, akusala_lobha_result):
    """Test that high kamma triggers appearance update"""
    # Create high kamma result
    high_kamma_result = CittaVithiResult(
        javana_citta="โลภมูลจิต",
        javana_type="akusala",
        javana_subtype="lobha",
        kamma_potency=1200.0,  # Above 1000 threshold
        sati_intervened=False,
        sequence=[],
        total_duration_ms=280
    )
    
    result = await updater.update_after_vithi(initial_state, high_kamma_result)
    
    # Should have triggered event
    assert len(result.triggered_events) > 0
    assert any("appearance" in event.lower() for event in result.triggered_events)

@pytest.mark.asyncio
async def test_significant_virtue_change_trigger(updater, initial_state, kusala_result):
    """Test that large virtue change triggers event"""
    # Set state close to triggering threshold
    initial_state.sila = 5.0
    
    # Multiple kusala vithis to accumulate 0.5+ change
    for _ in range(10):
        result = await updater.update_after_vithi(initial_state, kusala_result)
    
    # Should eventually trigger significant change event
    # (may take multiple iterations)

# ============================================================================
# Test State Snapshot
# ============================================================================

def test_state_snapshot_captures_all_data(initial_state):
    """Test that snapshot captures complete state"""
    snapshot = MindStateSnapshot(
        consciousness_state=initial_state.consciousness_state or "bhavanga",
        last_citta="Test Citta",
        kusala_count=initial_state.kusala_count_today,
        akusala_count=initial_state.akusala_count_today,
        active_hindrances=initial_state.active_hindrances or {},
        virtue_levels={
            "sila": initial_state.sila,
            "samadhi": initial_state.samadhi,
            "panna": initial_state.panna
        },
        kamma_queue_size=len(initial_state.kamma_queue or [])
    )
    
    assert snapshot.consciousness_state == "bhavanga"
    assert snapshot.last_citta == "Test Citta"
    assert snapshot.kusala_count == initial_state.kusala_count_today
    assert snapshot.akusala_count == initial_state.akusala_count_today
    assert snapshot.kamma_queue_size == 0

# ============================================================================
# Test Edge Cases
# ============================================================================

@pytest.mark.asyncio
async def test_update_with_zero_kamma(updater, initial_state, kusala_result):
    """Test update with zero kamma potency"""
    result = await updater.update_after_vithi(initial_state, kusala_result)
    
    # Should not add to kamma queue
    assert result.state_snapshot.kamma_queue_size == 0

@pytest.mark.asyncio
async def test_update_with_very_high_kamma(updater, initial_state):
    """Test update with very high kamma"""
    extreme_result = CittaVithiResult(
        javana_citta="โลภมูลจิต",
        javana_type="akusala",
        javana_subtype="lobha",
        kamma_potency=2000.0,  # Very high
        sati_intervened=False,
        sequence=[],
        total_duration_ms=280
    )
    
    result = await updater.update_after_vithi(initial_state, extreme_result)
    
    # Should handle gracefully
    assert result.state_snapshot.kamma_queue_size == 1
    assert len(result.triggered_events) > 0

def test_decay_with_no_hindrances(updater, initial_state):
    """Test decay when no hindrances present"""
    initial_state.active_hindrances = {}
    
    updated_state = updater.decay_hindrances(initial_state)
    
    # Should handle gracefully
    assert updated_state.active_hindrances == {}

def test_decay_immediately_after_update(updater, initial_state):
    """Test decay when no time has passed"""
    initial_state.active_hindrances = {"kāmacchanda": 5.0}
    initial_state.last_decay_time = datetime.now()  # Just now
    
    updated_state = updater.decay_hindrances(initial_state)
    
    # Should not decay significantly
    assert updated_state.active_hindrances["kāmacchanda"] >= 4.9

# ============================================================================
# Performance Tests
# ============================================================================

@pytest.mark.asyncio
async def test_update_performance(updater, initial_state, akusala_lobha_result):
    """Test that state update is fast enough"""
    import time
    
    start = time.time()
    result = await updater.update_after_vithi(initial_state, akusala_lobha_result)
    duration = time.time() - start
    
    # Should complete in less than 10ms
    assert duration < 0.01

def test_decay_performance(updater, initial_state):
    """Test that decay calculation is fast"""
    import time
    
    initial_state.active_hindrances = {
        "kāmacchanda": 5.0,
        "byāpāda": 3.0,
        "thīnamiddha": 2.0,
        "uddhaccakukkucca": 4.0,
        "vicikicchā": 1.5
    }
    initial_state.last_decay_time = datetime.now() - timedelta(hours=5)
    
    start = time.time()
    updated_state = updater.decay_hindrances(initial_state)
    duration = time.time() - start
    
    # Should complete in less than 5ms
    assert duration < 0.005

# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
