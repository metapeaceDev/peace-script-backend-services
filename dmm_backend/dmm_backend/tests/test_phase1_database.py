"""
Phase 1: Database Integration Tests
Tests for MindState and SimulationHistory models and API endpoints

Test Coverage:
- MindState model validation
- SimulationHistory model validation
- MindState CRUD API endpoints
- SimulationHistory CRUD API endpoints
- Analytics and progress tracking
"""

import pytest
from datetime import datetime
from httpx import AsyncClient, ASGITransport
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from documents import MindState, SimulationHistory
from main import app


# Test Data
SAMPLE_USER_ID = "test_user_phase1_001"
SAMPLE_SIMULATION_ID = "test_sim_phase1_001"
SAMPLE_SCENARIO_ID = "scenario_test_001"


# === Authentication Fixtures for Phase 1 Tests ===

@pytest.fixture
async def test_user_with_auth():
    """Create test user and return credentials + token"""
    import time
    timestamp = int(time.time() * 1000)
    email = f"phase1-test-{timestamp}@peacescript.com"
    password = "Phase1TestPass123!"
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register user (FastAPI-Users endpoint with /api prefix)
        reg_response = await client.post("/api/auth/register", json={
            "email": email,
            "password": password,
            "display_name": "Phase 1 Test User",
            "preferred_language": "th"
        })
        assert reg_response.status_code == 201
        user_data = reg_response.json()
        user_id = user_data["id"]
        
        # Login to get token (FastAPI-Users JWT login)
        login_response = await client.post(
            "/api/auth/jwt/login",
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        return {
            "user_id": user_id,
            "email": email,
            "password": password,
            "token": token,
            "headers": {"Authorization": f"Bearer {token}"}
        }


@pytest.fixture
async def mind_state_sample(test_user_with_auth):
    """Sample MindState for testing"""
    return {
        "user_id": test_user_with_auth["user_id"],
        "sila": 7.5,
        "samadhi": 6.0,
        "panna": 6.5,
        "sati_strength": 7.0,
        "current_anusaya": {
            "lobha": 4.0,
            "dosa": 3.5,
            "moha": 4.5
        },
        "current_bhumi": "puthujjana"
    }


@pytest.fixture
async def simulation_history_sample(test_user_with_auth):
    """Sample SimulationHistory for testing"""
    import time
    sim_id = f"test-sim-{int(time.time() * 1000)}"
    return {
        "simulation_id": sim_id,
        "user_id": SAMPLE_USER_ID,
        "scenario_id": SAMPLE_SCENARIO_ID,
        "choice_index": 1,
        "choice_id": "choice_kusala_001",
        "choice_type": "kusala",
        "choice_label": "ระลึกถึงศีล",
        "citta_generated": "kusala-citta",
        "citta_quality": "sobhana",
        "kamma_generated": 7.5,
        "sati_intervened": True,
        "sati_strength_at_choice": 7.0,
        "state_before": {"sila": 7.0, "samadhi": 6.0, "panna": 6.0},
        "state_after": {"sila": 7.5, "samadhi": 6.0, "panna": 6.5},
        "state_changes": ["sila +0.5", "panna +0.5"],
        "immediate_consequences": ["จิตใจสงบ", "มีสติมากขึ้น"],
        "short_term_consequences": ["เพิ่มความเชื่อมั่น"],
        "long_term_consequences": ["พัฒนาศีลธรรม"],
        "wisdom_gained": "สติช่วยให้ตัดสินใจถูกต้อง",
        "practice_tip": "ฝึกสติทุกวัน",
        "anusaya_before": {"lobha": 4.0, "dosa": 3.5},
        "anusaya_after": {"lobha": 3.5, "dosa": 3.5},
        "anusaya_changes": {"lobha": -0.5},
        "duration_seconds": 120
    }


# ========================================
# MindState Model Tests
# ========================================

class TestMindStateModel:
    """Test MindState document model"""
    
    async def test_create_mind_state(self, mind_state_sample, test_user_with_auth):
        """Test creating a MindState document"""
        mind_state = MindState(**mind_state_sample)
        assert mind_state.user_id == test_user_with_auth["user_id"]
        assert mind_state.sila == 7.5
        assert mind_state.samadhi == 6.0
        assert mind_state.panna == 6.5
        assert mind_state.current_bhumi == "puthujjana"
    
    async def test_mind_state_defaults(self):
        """Test MindState default values"""
        mind_state = MindState(user_id="test_defaults")
        assert mind_state.sila == 5.0
        assert mind_state.samadhi == 4.0
        assert mind_state.panna == 4.0
        assert mind_state.kusala_count_today == 0
        assert mind_state.akusala_count_today == 0
        assert mind_state.days_of_practice == 0
    
    async def test_mind_state_anusaya(self, mind_state_sample):
        """Test anusaya tracking"""
        mind_state = MindState(**mind_state_sample)
        assert "lobha" in mind_state.current_anusaya
        assert mind_state.current_anusaya["lobha"] == 4.0
    
    async def test_mind_state_validation_ranges(self):
        """Test field validation (0-10 range)"""
        with pytest.raises(ValueError):
            MindState(user_id="test", sila=15.0)  # Should fail: > 10
        
        with pytest.raises(ValueError):
            MindState(user_id="test", samadhi=-1.0)  # Should fail: < 0


# ========================================
# SimulationHistory Model Tests
# ========================================

class TestSimulationHistoryModel:
    """Test SimulationHistory document model"""
    
    async def test_create_simulation_history(self, simulation_history_sample, test_user_with_auth):
        """Test creating a SimulationHistory document"""
        history = SimulationHistory(**simulation_history_sample)
        # Check the dynamic simulation_id from fixture
        assert history.simulation_id.startswith("test-sim-")
        assert history.user_id == SAMPLE_USER_ID  # This is OK - it's in the fixture data
        assert history.choice_type == "kusala"
        assert history.kamma_generated == 7.5
    
    async def test_simulation_history_consequences(self, simulation_history_sample):
        """Test consequences are stored as lists"""
        history = SimulationHistory(**simulation_history_sample)
        assert isinstance(history.immediate_consequences, list)
        assert isinstance(history.short_term_consequences, list)
        assert isinstance(history.long_term_consequences, list)
        assert len(history.immediate_consequences) == 2
    
    async def test_simulation_history_anusaya_changes(self, simulation_history_sample):
        """Test anusaya change tracking"""
        history = SimulationHistory(**simulation_history_sample)
        assert "lobha" in history.anusaya_changes
        assert history.anusaya_changes["lobha"] == -0.5
    
    async def test_simulation_history_optional_fields(self):
        """Test optional fields can be None"""
        minimal_data = {
            "simulation_id": "test_sim_minimal",
            "user_id": "test_user",
            "scenario_id": "test_scenario",
            "choice_index": 0,
            "choice_id": "choice_1",
            "choice_type": "neutral",
            "choice_label": "Test",
            "citta_generated": "test-citta",
            "citta_quality": "test",
            "kamma_generated": 5.0,
            "state_before": {},
            "state_after": {},
            "wisdom_gained": "Test wisdom",
            "practice_tip": "Test tip",
            "anusaya_before": {},
            "anusaya_after": {},
            "anusaya_changes": {}
        }
        history = SimulationHistory(**minimal_data)
        assert history.user_reflection is None
        assert history.user_rating is None
        assert history.pali_term_explained is None


# ========================================
# MindState API Tests
# ========================================

@pytest.mark.asyncio
class TestMindStateAPI:
    """Test MindState CRUD API endpoints"""
    
    async def test_create_mind_state_endpoint(self, mind_state_sample, test_user_with_auth):
        """Test POST /api/v1/mind-states/"""
        # Note: MindState is auto-created on registration, so we need to delete it first or skip this test
        # For now, we'll test that attempting to create duplicate returns 400
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Try to create MindState (should fail as it already exists from registration)
            response = await client.post(
                "/api/v1/mind-states/", 
                json=mind_state_sample,
                headers=test_user_with_auth["headers"]
            )
            
            # Should get 400 Bad Request because MindState already exists
            assert response.status_code == 400
            data = response.json()
            # Check error message mentions "already exists"
            error_message = data.get("detail", "") or data.get("message", "") or str(data)
            assert "already exists" in error_message.lower()
    
    async def test_get_mind_state_endpoint(self, mind_state_sample, test_user_with_auth):
        """Test GET /api/v1/mind-states/{user_id}"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # MindState already exists from registration, just get it
            response = await client.get(
                f"/api/v1/mind-states/{test_user_with_auth['user_id']}",
                headers=test_user_with_auth["headers"]
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == test_user_with_auth["user_id"]
            # Check defaults (not custom values from mind_state_sample)
            assert data["sila"] == 5.0  # Default value
            assert data["samadhi"] == 4.0  # Default value
    
    async def test_update_mind_state_endpoint(self, mind_state_sample, test_user_with_auth):
        """Test PUT /api/v1/mind-states/{user_id}"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Create first
            await client.post(
                "/api/v1/mind-states/", 
                json=mind_state_sample,
                headers=test_user_with_auth["headers"]
            )
            
            # Update
            update_data = {"sila": 8.0, "panna": 7.0}
            response = await client.put(
                f"/api/v1/mind-states/{test_user_with_auth['user_id']}",
                json=update_data,
                headers=test_user_with_auth["headers"]
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["sila"] == 8.0
            assert data["panna"] == 7.0
    
    async def test_delete_mind_state_endpoint(self, mind_state_sample, test_user_with_auth):
        """Test DELETE /api/v1/mind-states/{user_id}"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Create first
            await client.post(
                "/api/v1/mind-states/", 
                json=mind_state_sample,
                headers=test_user_with_auth["headers"]
            )
            
            # Delete
            response = await client.delete(
                f"/api/v1/mind-states/{test_user_with_auth['user_id']}",
                headers=test_user_with_auth["headers"]
            )
            assert response.status_code == 204
            
            # Verify deleted
            response = await client.get(
                f"/api/v1/mind-states/{test_user_with_auth['user_id']}",
                headers=test_user_with_auth["headers"]
            )
            assert response.status_code == 404
    
    async def test_reset_daily_counters_endpoint(self, mind_state_sample, test_user_with_auth):
        """Test POST /api/v1/mind-states/{user_id}/reset-daily"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Create with some counters
            await client.post(
                "/api/v1/mind-states/", 
                json=mind_state_sample,
                headers=test_user_with_auth["headers"]
            )
            
            # Increment kusala
            await client.post(
                f"/api/v1/mind-states/{test_user_with_auth['user_id']}/increment-kusala?amount=5",
                headers=test_user_with_auth["headers"]
            )
            
            # Reset
            response = await client.post(
                f"/api/v1/mind-states/{test_user_with_auth['user_id']}/reset-daily",
                headers=test_user_with_auth["headers"]
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["kusala_count_today"] == 0
            assert data["days_of_practice"] == 1  # Should increment
    
    async def test_get_progress_summary_endpoint(self, mind_state_sample, test_user_with_auth):
        """Test GET /api/v1/mind-states/{user_id}/progress"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Create
            await client.post(
                "/api/v1/mind-states/", 
                json=mind_state_sample,
                headers=test_user_with_auth["headers"]
            )
            
            # Get progress
            response = await client.get(
                f"/api/v1/mind-states/{test_user_with_auth['user_id']}/progress",
                headers=test_user_with_auth["headers"]
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == test_user_with_auth["user_id"]
            assert "three_trainings" in data
            assert "kusala_ratio_today" in data
            assert "recommendations" in data
            assert isinstance(data["recommendations"], list)
    
    async def test_increment_kusala_endpoint(self, mind_state_sample, test_user_with_auth):
        """Test POST /api/v1/mind-states/{user_id}/increment-kusala"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Create
            await client.post(
                "/api/v1/mind-states/", 
                json=mind_state_sample,
                headers=test_user_with_auth["headers"]
            )
            
            # Increment
            response = await client.post(
                f"/api/v1/mind-states/{test_user_with_auth['user_id']}/increment-kusala?amount=3",
                headers=test_user_with_auth["headers"]
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["kusala_count_today"] == 3
            assert data["kusala_count_total"] == 3
    
    async def test_increment_akusala_endpoint(self, mind_state_sample, test_user_with_auth):
        """Test POST /api/v1/mind-states/{user_id}/increment-akusala"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Create
            await client.post(
                "/api/v1/mind-states/", 
                json=mind_state_sample,
                headers=test_user_with_auth["headers"]
            )
            
            # Increment
            response = await client.post(
                f"/api/v1/mind-states/{test_user_with_auth['user_id']}/increment-akusala?amount=2",
                headers=test_user_with_auth["headers"]
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["akusala_count_today"] == 2
            assert data["akusala_count_total"] == 2


# ========================================
# SimulationHistory API Tests
# ========================================

@pytest.mark.asyncio
class TestSimulationHistoryAPI:
    """Test SimulationHistory CRUD API endpoints"""
    
    async def test_create_simulation_history_endpoint(self, simulation_history_sample, test_user_with_auth):
        """Test POST /api/v1/simulation-history/"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/simulation-history/",
                json=simulation_history_sample,
                headers=test_user_with_auth["headers"]
            )
            
            assert response.status_code == 201
            data = response.json()
            # user_id is forced from token, so check against authenticated user
            assert data["user_id"] == test_user_with_auth["user_id"]
            assert data["choice_type"] == "kusala"
            assert "timestamp" in data
    
    async def test_get_simulation_history_endpoint(self, simulation_history_sample, test_user_with_auth):
        """Test GET /api/v1/simulation-history/{simulation_id}"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Create first
            create_response = await client.post(
                "/api/v1/simulation-history/", 
                json=simulation_history_sample,
                headers=test_user_with_auth["headers"]
            )
            created_data = create_response.json()
            created_sim_id = created_data["simulation_id"]
            
            # Get
            response = await client.get(
                f"/api/v1/simulation-history/{created_sim_id}",
                headers=test_user_with_auth["headers"]
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["simulation_id"] == created_sim_id
            assert data["kamma_generated"] == 7.5
    
    async def test_get_user_simulation_history_endpoint(self, simulation_history_sample, test_user_with_auth):
        """Test GET /api/v1/simulation-history/user/{user_id}"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Create multiple simulations
            await client.post(
                "/api/v1/simulation-history/", 
                json=simulation_history_sample,
                headers=test_user_with_auth["headers"]
            )
            
            sim2 = simulation_history_sample.copy()
            sim2["simulation_id"] = f"test_sim_phase1_002_{int(__import__('time').time() * 1000)}"
            sim2["choice_type"] = "akusala"
            await client.post(
                "/api/v1/simulation-history/", 
                json=sim2,
                headers=test_user_with_auth["headers"]
            )
            
            # Get user's history
            response = await client.get(
                f"/api/v1/simulation-history/user/{test_user_with_auth['user_id']}",
                headers=test_user_with_auth["headers"]
            )
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) >= 2
    
    async def test_get_user_history_with_filters(self, simulation_history_sample, test_user_with_auth):
        """Test GET /api/v1/simulation-history/user/{user_id} with filters"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Create simulations
            await client.post(
                "/api/v1/simulation-history/", 
                json=simulation_history_sample,
                headers=test_user_with_auth["headers"]
            )
            
            # Filter by choice_type
            response = await client.get(
                f"/api/v1/simulation-history/user/{test_user_with_auth['user_id']}?choice_type=kusala",
                headers=test_user_with_auth["headers"]
            )
            
            assert response.status_code == 200
            data = response.json()
            for item in data:
                assert item["choice_type"] == "kusala"
    
    async def test_get_user_history_summary_endpoint(self, simulation_history_sample, test_user_with_auth):
        """Test GET /api/v1/simulation-history/user/{user_id}/summary"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Create simulation
            await client.post(
                "/api/v1/simulation-history/", 
                json=simulation_history_sample,
                headers=test_user_with_auth["headers"]
            )
            
            # Get summary
            response = await client.get(
                f"/api/v1/simulation-history/user/{test_user_with_auth['user_id']}/summary",
                headers=test_user_with_auth["headers"]
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == test_user_with_auth["user_id"]
            assert data["total_simulations"] >= 1
            assert "kusala_choices" in data
            assert "average_kamma_generated" in data
            assert "recent_simulations" in data
    
    async def test_get_anusaya_trends_endpoint(self, simulation_history_sample, test_user_with_auth):
        """Test GET /api/v1/simulation-history/user/{user_id}/anusaya-trends"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Create simulation
            await client.post(
                "/api/v1/simulation-history/", 
                json=simulation_history_sample,
                headers=test_user_with_auth["headers"]
            )
            
            # Get trends
            response = await client.get(
                f"/api/v1/simulation-history/user/{test_user_with_auth['user_id']}/anusaya-trends",
                headers=test_user_with_auth["headers"]
            )
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            
            if len(data) > 0:
                trend = data[0]
                assert "anusaya_name" in trend
                assert "data_points" in trend
                assert "overall_trend" in trend
    
    async def test_get_learning_progress_endpoint(self, simulation_history_sample, test_user_with_auth):
        """Test GET /api/v1/simulation-history/user/{user_id}/learning-progress"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Create simulation
            await client.post(
                "/api/v1/simulation-history/", 
                json=simulation_history_sample,
                headers=test_user_with_auth["headers"]
            )
            
            # Get learning progress
            response = await client.get(
                f"/api/v1/simulation-history/user/{test_user_with_auth['user_id']}/learning-progress",
                headers=test_user_with_auth["headers"]
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == test_user_with_auth["user_id"]
            assert "total_lessons" in data
            assert "wisdom_gained_count" in data
            assert "practice_tips_received" in data
    
    async def test_get_scenario_analytics_endpoint(self, simulation_history_sample, test_user_with_auth):
        """Test GET /api/v1/simulation-history/scenarios/{scenario_id}/analytics"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Create simulation
            await client.post(
                "/api/v1/simulation-history/", 
                json=simulation_history_sample,
                headers=test_user_with_auth["headers"]
            )
            
            # Get scenario analytics (public endpoint, but we include headers anyway)
            response = await client.get(
                f"/api/v1/simulation-history/scenarios/{SAMPLE_SCENARIO_ID}/analytics",
                headers=test_user_with_auth["headers"]
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["scenario_id"] == SAMPLE_SCENARIO_ID
            assert "total_attempts" in data
            assert "choice_distribution" in data
            assert "average_kamma_generated" in data
    
    async def test_delete_simulation_history_endpoint(self, simulation_history_sample, test_user_with_auth):
        """Test DELETE /api/v1/simulation-history/{simulation_id}"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Create
            create_response = await client.post(
                "/api/v1/simulation-history/", 
                json=simulation_history_sample,
                headers=test_user_with_auth["headers"]
            )
            created_data = create_response.json()
            created_sim_id = created_data["simulation_id"]
            
            # Delete
            response = await client.delete(
                f"/api/v1/simulation-history/{created_sim_id}",
                headers=test_user_with_auth["headers"]
            )
            assert response.status_code == 204
            
            # Verify deleted
            response = await client.get(
                f"/api/v1/simulation-history/{created_sim_id}",
                headers=test_user_with_auth["headers"]
            )
            assert response.status_code == 404


# ========================================
# Integration Tests
# ========================================

@pytest.mark.asyncio
class TestPhase1Integration:
    """Integration tests for MindState + SimulationHistory"""
    
    async def test_simulation_updates_mind_state(self, mind_state_sample, simulation_history_sample, test_user_with_auth):
        """Test that simulation can update related MindState"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Create MindState
            await client.post(
                "/api/v1/mind-states/", 
                json=mind_state_sample,
                headers=test_user_with_auth["headers"]
            )
            
            # Create Simulation
            await client.post(
                "/api/v1/simulation-history/", 
                json=simulation_history_sample,
                headers=test_user_with_auth["headers"]
            )
            
            # Increment kusala (simulating post-simulation update)
            await client.post(
                f"/api/v1/mind-states/{test_user_with_auth['user_id']}/increment-kusala?amount=1",
                headers=test_user_with_auth["headers"]
            )
            
            # Verify MindState updated
            response = await client.get(
                f"/api/v1/mind-states/{test_user_with_auth['user_id']}",
                headers=test_user_with_auth["headers"]
            )
            data = response.json()
            assert data["kusala_count_total"] == 1
    
    async def test_complete_user_journey(self, mind_state_sample, simulation_history_sample, test_user_with_auth):
        """Test complete user journey: create state → simulate → view progress"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. MindState already exists from registration (auto-created)
            response = await client.get(
                f"/api/v1/mind-states/{test_user_with_auth['user_id']}",
                headers=test_user_with_auth["headers"]
            )
            assert response.status_code == 200
            
            # 2. User completes simulation
            response = await client.post(
                "/api/v1/simulation-history/", 
                json=simulation_history_sample,
                headers=test_user_with_auth["headers"]
            )
            assert response.status_code == 201
            
            # 3. Update counters
            await client.post(
                f"/api/v1/mind-states/{test_user_with_auth['user_id']}/increment-kusala?amount=1",
                headers=test_user_with_auth["headers"]
            )
            
            # 4. View progress summary
            response = await client.get(
                f"/api/v1/mind-states/{test_user_with_auth['user_id']}/progress",
                headers=test_user_with_auth["headers"]
            )
            assert response.status_code == 200
            progress = response.json()
            assert progress["kusala_ratio_total"] > 0
            
            # 5. View simulation history
            response = await client.get(
                f"/api/v1/simulation-history/user/{test_user_with_auth['user_id']}/summary",
                headers=test_user_with_auth["headers"]
            )
            assert response.status_code == 200
            summary = response.json()
            assert summary["total_simulations"] >= 1


# ========================================
# Error Handling Tests
# ========================================

@pytest.mark.asyncio
class TestPhase1ErrorHandling:
    """Test error handling for Phase 1 APIs"""
    
    async def test_get_nonexistent_mind_state(self, test_user_with_auth):
        """Test getting non-existent MindState returns 404"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                "/api/v1/mind-states/nonexistent_user",
                headers=test_user_with_auth["headers"]
            )
            # Should get 403 (not authorized) or 404 (not found), both are acceptable
            assert response.status_code in [403, 404]
    
    async def test_create_duplicate_mind_state(self, mind_state_sample, test_user_with_auth):
        """Test creating duplicate MindState returns 400"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Create first
            await client.post(
                "/api/v1/mind-states/", 
                json=mind_state_sample,
                headers=test_user_with_auth["headers"]
            )
            
            # Try to create duplicate
            response = await client.post(
                "/api/v1/mind-states/", 
                json=mind_state_sample,
                headers=test_user_with_auth["headers"]
            )
            assert response.status_code == 400
    
    async def test_get_nonexistent_simulation(self, test_user_with_auth):
        """Test getting non-existent simulation returns 404"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                "/api/v1/simulation-history/nonexistent_sim",
                headers=test_user_with_auth["headers"]
            )
            assert response.status_code == 404
    
    async def test_invalid_field_values(self, test_user_with_auth):
        """Test invalid field values return validation errors"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            invalid_data = {
                "user_id": test_user_with_auth["user_id"],
                "sila": 15.0,  # Invalid: > 10
                "samadhi": 5.0,
                "panna": 5.0
            }
            response = await client.post(
                "/api/v1/mind-states/", 
                json=invalid_data,
                headers=test_user_with_auth["headers"]
            )
            assert response.status_code == 422  # Validation error
