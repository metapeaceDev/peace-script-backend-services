import pytest
pytestmark = pytest.mark.asyncio(loop_scope="function")
from httpx import AsyncClient
from documents import DigitalMindModel, KammaLogEntry, TrainingLog
from dmm_backend.schemas import StimulusObject, EnvironmentModifiers


@pytest.mark.asyncio
async def test_get_editor_profile(async_client: AsyncClient):
    """Test fetching the editor profile for a model."""
    response = await async_client.get("/models/test_model_001/editor_profile")
    assert response.status_code == 200
    data = response.json()
    assert data["model_id"] == "test_model_001"
    assert data["character_card"]["name"] == "Test Model"
    assert "core_stats" in data
    assert len(data["core_stats"]["summary_metrics"]) > 0


@pytest.mark.asyncio
async def test_get_editor_profile_not_found(async_client: AsyncClient):
    """Test fetching a non-existent editor profile."""
    response = await async_client.get("/models/non_existent_model/editor_profile")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_all_models(async_client: AsyncClient):
    """Test fetching all model profiles."""
    response = await async_client.get("/models/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["model_id"] == "test_model_001"


@pytest.mark.asyncio
async def test_get_full_profile(async_client: AsyncClient):
    """Test fetching the full raw profile for a model."""
    response = await async_client.get("/models/test_model_001/full_profile")
    assert response.status_code == 200
    data = response.json()
    assert data["model_id"] == "test_model_001"
    assert "conscious_profile" in data
    assert "kamma_profile" in data


@pytest.mark.asyncio
async def test_get_kamma_log(async_client: AsyncClient):
    """Test fetching the kamma log for a model."""
    log_entry = KammaLogEntry(
        model_id="test_model_001", 
        event_type="test",
        description="test",
        impact_level=1,
        context={"stimulus": {"type": "test", "source": "test", "intensity": 50, "details": "Test Stimulus"}},
    )
    await log_entry.insert()

    response = await async_client.get("/models/test_model_001/kamma_log")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["context"]["stimulus"]["details"] == "Test Stimulus"


@pytest.mark.asyncio
async def test_get_training_log(async_client: AsyncClient):
    """Test fetching the training log for a model."""
    log_entry = TrainingLog(model_id="test_model_001", training_type="Meditation", details={"duration_minutes": 30})
    await log_entry.insert()

    response = await async_client.get("/models/test_model_001/training_log")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["training_type"] == "Meditation"


@pytest.mark.asyncio
async def test_simulate_reaction(async_client: AsyncClient):
    """Test simulating a reaction with the correct payload structure."""
    payload = {
        "model_id": "test_model_001",
        "stimulus_object": {
            "type": "verbal",
            "source": "External",
            "intensity": 75,
            "details": "Insult"
        },
        "environment_modifiers": {
            "ambient_stress_level": 0.2
        }
    }
    response = await async_client.post("/simulation/react", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "log_entry" in data
    log_entry = data["log_entry"]
    assert log_entry["context"]["stimulus"]["details"] == "Insult"

    logs = await KammaLogEntry.find(KammaLogEntry.model_id == "test_model_001").to_list()
    assert len(logs) == 1
    assert logs[0].context["stimulus"]["details"] == "Insult"
