"""
Integration Tests for Database Operations
==========================================

Tests for MindState, SimulationHistory, KammaLogEntry, and User models
with actual MongoDB integration.

Run with:
    pytest tests/test_integration_database.py -v
"""

import pytest
import asyncio
from datetime import datetime
from typing import AsyncGenerator

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from documents import (
    DigitalMindModel,
    User,
    MindState,
    SimulationHistory,
    KammaLogEntry,
    TrainingLog
)
from utils.security import hash_password
from config import settings


# ============================================================================
# Test Configuration & Fixtures
# ============================================================================

# Global database client and initialization flag
_db_initialized = False
_test_db = None


@pytest.fixture(scope="function")
async def init_test_db():
    """Initialize Beanie with test database (once per test session)"""
    global _db_initialized, _test_db
    
    if not _db_initialized:
        # Create MongoDB client
        client = AsyncIOMotorClient(settings.MONGO_URI)
        
        # Use test database
        test_db_name = f"{settings.MONGO_DB_NAME}_test"
        _test_db = client[test_db_name]
        
        # Initialize Beanie with all document models
        await init_beanie(
            database=_test_db,
            document_models=[
                DigitalMindModel,
                User,
                MindState,
                SimulationHistory,
                KammaLogEntry,
                TrainingLog
            ]
        )
        
        _db_initialized = True
    
    # Clean all collections before each test
    await User.delete_all()
    await MindState.delete_all()
    await SimulationHistory.delete_all()
    await KammaLogEntry.delete_all()
    await DigitalMindModel.delete_all()
    await TrainingLog.delete_all()
    
    yield _test_db
    
    # Cleanup after each test
    await User.delete_all()
    await MindState.delete_all()
    await SimulationHistory.delete_all()
    await KammaLogEntry.delete_all()
    await DigitalMindModel.delete_all()
    await TrainingLog.delete_all()


# ============================================================================
# User Model Tests
# ============================================================================

@pytest.mark.asyncio
async def test_user_create(init_test_db):
    """Test creating a new user"""
    user = User(
        email="test@example.com",
        hashed_password=hash_password("SecurePass123"),
        display_name="Test User",
        is_active=True,
        is_verified=False
    )
    
    await user.insert()
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.is_active is True
    assert user.display_name == "Test User"


@pytest.mark.asyncio
async def test_user_find_by_email(init_test_db):
    """Test finding user by email"""
    # Create user
    user = User(
        email="find@example.com",
        hashed_password=hash_password("Pass123"),
        display_name="Find Test"
    )
    await user.insert()
    
    # Find by email
    found_user = await User.find_one(User.email == "find@example.com")
    
    assert found_user is not None
    assert found_user.email == "find@example.com"
    assert found_user.display_name == "Find Test"


@pytest.mark.asyncio
async def test_user_update(init_test_db):
    """Test updating user data"""
    user = User(
        email="update@example.com",
        hashed_password=hash_password("Pass123"),
        display_name="Original Name"
    )
    await user.insert()
    
    # Update user
    user.display_name = "Updated Name"
    user.is_verified = True
    await user.save()
    
    # Verify update
    updated_user = await User.get(user.id)
    assert updated_user.display_name == "Updated Name"
    assert updated_user.is_verified is True


@pytest.mark.asyncio
async def test_user_delete(init_test_db):
    """Test deleting a user"""
    user = User(
        email="delete@example.com",
        hashed_password=hash_password("Pass123"),
        display_name="Delete Test"
    )
    await user.insert()
    user_id = user.id
    
    # Delete user
    await user.delete()
    
    # Verify deletion
    deleted_user = await User.get(user_id)
    assert deleted_user is None


# ============================================================================
# MindState Model Tests
# ============================================================================

@pytest.mark.asyncio
async def test_mindstate_create(init_test_db):
    """Test creating a MindState"""
    mind_state = MindState(
        user_id="test_user_001",
        sila=7.5,
        samadhi=6.0,
        panna=5.5,
        sati_strength=6.5,
        current_anusaya={"lobha": 3.0, "dosa": 2.5, "moha": 3.5},
        kusala_count_today=5,
        akusala_count_today=2,
        current_bhumi="puthujjana"
    )
    
    await mind_state.insert()
    
    assert mind_state.id is not None
    assert mind_state.user_id == "test_user_001"
    assert mind_state.sila == 7.5
    assert mind_state.current_anusaya["lobha"] == 3.0
    assert mind_state.created_at is not None


@pytest.mark.asyncio
async def test_mindstate_update_counters(init_test_db):
    """Test updating kusala/akusala counters"""
    mind_state = MindState(
        user_id="test_user_002",
        kusala_count_today=0,
        akusala_count_today=0,
        kusala_count_total=0,
        akusala_count_total=0
    )
    await mind_state.insert()
    
    # Simulate kusala action
    mind_state.kusala_count_today += 1
    mind_state.kusala_count_total += 1
    await mind_state.save()
    
    # Verify
    updated_state = await MindState.get(mind_state.id)
    assert updated_state.kusala_count_today == 1
    assert updated_state.kusala_count_total == 1


@pytest.mark.asyncio
async def test_mindstate_find_by_user(init_test_db):
    """Test finding MindState by user_id"""
    # Create multiple states
    for i in range(3):
        mind_state = MindState(
            user_id="user_multi_001",
            sila=5.0 + i
        )
        await mind_state.insert()
    
    # Find all states for user
    states = await MindState.find(
        MindState.user_id == "user_multi_001"
    ).to_list()
    
    assert len(states) == 3


# ============================================================================
# SimulationHistory Model Tests
# ============================================================================

@pytest.mark.asyncio
async def test_simulation_history_create(init_test_db):
    """Test creating SimulationHistory record"""
    history = SimulationHistory(
        simulation_id="SIM-001",
        user_id="user_001",
        scenario_id="scenario_001",
        choice_index=0,
        choice_id="choice_kusala_001",
        choice_type="kusala",
        choice_label="Give generously",
        citta_generated="Kusala-Dana",
        citta_quality="kusala",  # Added required field
        kamma_generated=5.0,
        sati_intervened=False,
        state_before={"sila": 5.0, "samadhi": 4.0},
        state_after={"sila": 5.5, "samadhi": 4.0},
        state_changes=["sila +0.5"],
        immediate_consequences=["Feeling of joy and satisfaction"],  # Changed to list
        short_term_consequences=["Increased merit and good karma"],  # Changed to list
        long_term_consequences=["Progress toward stream-entry"],  # Changed to list
        wisdom_gained="Generosity brings happiness",
        practice_tip="Continue practicing dana daily"
    )
    
    await history.insert()
    
    assert history.id is not None
    assert history.simulation_id == "SIM-001"
    assert history.choice_type == "kusala"
    assert history.kamma_generated == 5.0
    assert history.timestamp is not None  # SimulationHistory uses timestamp, not created_at


@pytest.mark.asyncio
async def test_simulation_history_query_by_user(init_test_db):
    """Test querying simulation history by user"""
    # Create multiple history records
    for i in range(3):
        history = SimulationHistory(
            simulation_id=f"SIM-{i:03d}",
            user_id="user_history_001",
            scenario_id=f"scenario_{i:03d}",
            choice_index=i,
            choice_id=f"choice_{i}",
            choice_type="kusala" if i % 2 == 0 else "akusala",
            choice_label=f"Choice {i}",
            citta_generated=f"Citta-{i}",
            citta_quality="kusala" if i % 2 == 0 else "akusala",  # Added
            kamma_generated=float(i),
            state_before={},
            state_after={},
            state_changes=[],
            immediate_consequences=["Test"],  # Changed to list
            short_term_consequences=["Test"],  # Changed to list
            long_term_consequences=["Test"],  # Changed to list
            wisdom_gained="Test",
            practice_tip="Test"
        )
        await history.insert()
    
    # Query all history for user
    histories = await SimulationHistory.find(
        SimulationHistory.user_id == "user_history_001"
    ).to_list()
    
    assert len(histories) == 3
    
    # Query only kusala choices
    kusala_histories = await SimulationHistory.find(
        SimulationHistory.user_id == "user_history_001",
        SimulationHistory.choice_type == "kusala"
    ).to_list()
    
    assert len(kusala_histories) == 2


@pytest.mark.asyncio
async def test_simulation_history_sort_by_created(init_test_db):
    """Test sorting simulation history by creation time"""
    # Create records with delays to ensure different timestamps
    import asyncio
    for i in range(3):
        history = SimulationHistory(
            simulation_id=f"SIM-SORT-{i}",
            user_id="user_sort_001",
            scenario_id="scenario_001",
            choice_index=i,
            choice_id=f"choice_{i}",
            choice_type="kusala",
            choice_label=f"Choice {i}",
            citta_generated="Test",
            citta_quality="kusala",  # Added
            kamma_generated=1.0,
            state_before={},
            state_after={},
            state_changes=[],
            immediate_consequences=["Test"],  # Changed to list
            short_term_consequences=["Test"],  # Changed to list
            long_term_consequences=["Test"],  # Changed to list
            wisdom_gained="Test",
            practice_tip="Test"
        )
        await history.insert()
        await asyncio.sleep(0.01)  # Small delay to ensure different timestamps
    
    # Query sorted by newest first
    histories = await SimulationHistory.find(
        SimulationHistory.user_id == "user_sort_001"
    ).sort("-timestamp").to_list()  # Use string "-timestamp"
    
    assert len(histories) == 3
    assert histories[0].simulation_id == "SIM-SORT-2"  # Most recent


# ============================================================================
# KammaLogEntry Model Tests
# ============================================================================

@pytest.mark.asyncio
async def test_kamma_log_create(init_test_db):
    """Test creating KammaLogEntry"""
    log_entry = KammaLogEntry(
        model_id="DM-001",
        event_type="reaction",
        description="User chose to practice generosity",
        impact_level=5,
        context={
            "stimulus": "Saw someone in need",
            "choice": "Give help",
            "outcome": "Positive karma generated"
        }
    )
    
    await log_entry.insert()
    
    assert log_entry.id is not None
    assert log_entry.model_id == "DM-001"
    assert log_entry.event_type == "reaction"
    assert log_entry.impact_level == 5
    assert log_entry.timestamp is not None


@pytest.mark.asyncio
async def test_kamma_log_query_by_model(init_test_db):
    """Test querying kamma logs by model_id"""
    # Create multiple log entries
    for i in range(5):
        log = KammaLogEntry(
            model_id="DM-LOG-001",
            event_type="cultivation" if i % 2 == 0 else "reaction",
            description=f"Event {i}",
            impact_level=i,
            context={"event_num": i}
        )
        await log.insert()
    
    # Query all logs for model
    logs = await KammaLogEntry.find(
        KammaLogEntry.model_id == "DM-LOG-001"
    ).to_list()
    
    assert len(logs) == 5
    
    # Query only cultivation events
    cultivation_logs = await KammaLogEntry.find(
        KammaLogEntry.model_id == "DM-LOG-001",
        KammaLogEntry.event_type == "cultivation"
    ).to_list()
    
    assert len(cultivation_logs) == 3


@pytest.mark.asyncio
async def test_kamma_log_sort_by_timestamp(init_test_db):
    """Test sorting kamma logs by timestamp"""
    # Create logs with delays to ensure different timestamps
    import asyncio
    for i in range(3):
        log = KammaLogEntry(
            model_id="DM-SORT-001",
            event_type="reaction",
            description=f"Event {i}",
            impact_level=i,
            context={}
        )
        await log.insert()
        await asyncio.sleep(0.01)  # Small delay to ensure different timestamps
    
    # Query sorted by newest first
    logs = await KammaLogEntry.find(
        KammaLogEntry.model_id == "DM-SORT-001"
    ).sort("-timestamp").to_list()  # Use string "-timestamp"
    
    assert len(logs) == 3
    # Most recent should be first
    assert logs[0].description == "Event 2"


# ============================================================================
# Cross-Model Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_complete_simulation_flow(init_test_db):
    """Test complete simulation flow with multiple models"""
    # 1. Create user
    user = User(
        email="simulation@test.com",
        hashed_password=hash_password("Test123"),
        display_name="Simulation Test"
    )
    await user.insert()
    user_id = str(user.id)
    
    # 2. Create initial MindState
    mind_state = MindState(
        user_id=user_id,
        sila=5.0,
        samadhi=4.0,
        panna=4.0,
        kusala_count_today=0,
        kusala_count_total=0,
        last_simulation_at=None,
        last_reset_at=None
    )
    await mind_state.insert()
    
    # 3. Simulate kusala action
    history = SimulationHistory(
        simulation_id="SIM-FLOW-001",
        user_id=user_id,
        scenario_id="scenario_dana",
        choice_index=0,
        choice_id="dana_choice",
        choice_type="kusala",
        choice_label="Practice generosity",
        choice_description="Choose to practice dana",
        citta_generated="Kusala-Dana",
        citta_quality="kusala",
        kamma_generated=5.0,
        sati_intervened=False,
        state_before={"sila": 5.0},
        state_after={"sila": 5.5},
        state_changes=["sila +0.5"],
        immediate_consequences=["Joy"],  # Changed to list
        short_term_consequences=["Merit"],  # Changed to list
        long_term_consequences=["Progress"],  # Changed to list
        wisdom_gained="Generosity brings happiness",
        practice_tip="Continue dana"
    )
    await history.insert()
    
    # 4. Update MindState
    mind_state.sila += 0.5
    mind_state.kusala_count_today += 1
    mind_state.kusala_count_total += 1
    await mind_state.save()
    
    # 5. Log kamma
    kamma_log = KammaLogEntry(
        model_id=user_id,
        event_type="kusala_action",
        description="Practiced generosity",
        impact_level=5,
        context={
            "simulation_id": "SIM-FLOW-001",
            "kamma_generated": 5.0
        }
    )
    await kamma_log.insert()
    
    # Verify complete flow
    assert user.id is not None
    assert mind_state.sila == 5.5
    assert mind_state.kusala_count_total == 1
    
    # Verify history recorded
    found_history = await SimulationHistory.find_one(
        SimulationHistory.simulation_id == "SIM-FLOW-001"
    )
    assert found_history is not None
    assert found_history.kamma_generated == 5.0
    
    # Verify kamma logged
    found_log = await KammaLogEntry.find_one(
        KammaLogEntry.model_id == user_id
    )
    assert found_log is not None
    assert found_log.impact_level == 5


@pytest.mark.asyncio
async def test_user_with_multiple_mind_states(init_test_db):
    """Test user with multiple MindState snapshots over time"""
    import asyncio
    user_id = "user_states_001"
    
    # Create multiple MindState snapshots with delays to ensure different timestamps
    states_data = [
        {"sila": 5.0, "samadhi": 4.0, "panna": 3.0},
        {"sila": 5.5, "samadhi": 4.5, "panna": 3.5},
        {"sila": 6.0, "samadhi": 5.0, "panna": 4.0},
    ]
    
    for data in states_data:
        state = MindState(
            user_id=user_id,
            **data
        )
        await state.insert()
        await asyncio.sleep(0.01)  # 10ms delay to ensure different created_at
    
    # Query all states
    states = await MindState.find(
        MindState.user_id == user_id
    ).sort("-created_at").to_list()  # Use string "-created_at"
    
    assert len(states) == 3
    # Most recent should show highest values
    assert states[0].sila == 6.0


# ============================================================================
# Performance & Bulk Operations Tests
# ============================================================================

@pytest.mark.asyncio
async def test_bulk_kamma_log_insert(init_test_db):
    """Test bulk insertion of kamma logs"""
    logs = []
    for i in range(100):
        log = KammaLogEntry(
            model_id="DM-BULK-001",
            event_type="reaction",
            description=f"Bulk event {i}",
            impact_level=i % 10,
            context={"index": i}
        )
        logs.append(log)
    
    # Bulk insert
    await KammaLogEntry.insert_many(logs)
    
    # Verify count
    count = await KammaLogEntry.find(
        KammaLogEntry.model_id == "DM-BULK-001"
    ).count()
    
    assert count == 100


@pytest.mark.asyncio
async def test_pagination_simulation_history(init_test_db):
    """Test pagination of simulation history"""
    # Create 50 records
    for i in range(50):
        history = SimulationHistory(
            simulation_id=f"SIM-PAGE-{i:03d}",
            user_id="user_page_001",
            scenario_id="scenario_001",
            choice_index=i,
            choice_id=f"choice_{i}",
            choice_type="kusala",
            choice_label=f"Choice {i}",
            citta_generated="Test",
            citta_quality="kusala",  # Added
            kamma_generated=1.0,
            state_before={},
            state_after={},
            state_changes=[],
            immediate_consequences=["Test"],  # Changed to list
            short_term_consequences=["Test"],  # Changed to list
            long_term_consequences=["Test"],  # Changed to list
            wisdom_gained="Test",
            practice_tip="Test"
        )
        await history.insert()
    
    # Page 1: First 10
    page1 = await SimulationHistory.find(
        SimulationHistory.user_id == "user_page_001"
    ).sort("-timestamp").limit(10).to_list()  # Use string "-timestamp"
    
    # Page 2: Next 10
    page2 = await SimulationHistory.find(
        SimulationHistory.user_id == "user_page_001"
    ).sort("-timestamp").skip(10).limit(10).to_list()  # Use string "-timestamp"
    
    assert len(page1) == 10
    assert len(page2) == 10
    # Verify different records
    assert page1[0].simulation_id != page2[0].simulation_id


# ============================================================================
# Summary Statistics
# ============================================================================

if __name__ == "__main__":
    print("Integration Test Suite for Database Operations")
    print("=" * 60)
    print("\nTest Coverage:")
    print("- User: Create, Read, Update, Delete")
    print("- MindState: Create, Update, Query by user")
    print("- SimulationHistory: Create, Query, Sort, Pagination")
    print("- KammaLogEntry: Create, Query, Sort, Bulk operations")
    print("- Cross-model integration flow")
    print("\nRun with: pytest tests/test_integration_database.py -v")
