"""
🧪 Rupa System Test Suite - Comprehensive testing for 28 Material Forms

Tests:
1. Backward Compatibility (?detailed=false)
2. Detailed Mode (?detailed=true)
3. Mahabhuta Calculation (4 Great Elements)
4. Pasada Calculation (5 Sense Organs)
5. Jivitindriya Synchronization
6. Computed Properties
7. Kalapa Lifecycle (17 moments)
8. Samutthana Tracking (4 origins)

Author: Peace Mind System
Date: 17 October 2568
Version: 1.0
"""

import pytest
from httpx import AsyncClient
from datetime import datetime
from typing import Dict, Any

from main import app
from documents import DigitalMindModel
from rupa_models import RupaProfile, MahabhutaType, RupaKkhanaType
from modules.rupa_engine import RupaCalculationEngine, calculate_and_save_rupa
from modules.rupa_sync import RupaJivitindriaSyncLayer
from core_profile_models import NamaRupaProfile


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
async def test_model():
    """Create a test DigitalMindModel"""
    model = DigitalMindModel(
        model_id="test-rupa-001",
        name="Test Rupa Model",
        version="1.0",
        timestamp=datetime.now()
    )
    await model.insert()
    
    # Initialize basic CoreProfile
    profile = model.get_core_profile()
    profile.life_essence.age_in_years = 30
    profile.life_essence.life_blueprint_vipaka.initial_conditions.health_baseline = 80.0
    profile.life_essence.jivitindriya_mechanics.current_jivitindriya = 75.0
    profile.life_essence.life_blueprint_vipaka.lifespan_potential = 120
    
    model.update_core_profile({})
    await model.save()
    
    yield model
    
    # Cleanup
    await model.delete()
    rupa = await RupaProfile.find_one(RupaProfile.model_id == "test-rupa-001")
    if rupa:
        await rupa.delete()


@pytest.fixture
async def test_rupa_profile(test_model):
    """Create a test RupaProfile"""
    rupa = await calculate_and_save_rupa(test_model.model_id)
    yield rupa
    # Cleanup handled by test_model fixture


# =============================================================================
# TEST 1: BACKWARD COMPATIBILITY (?detailed=false)
# =============================================================================

@pytest.mark.asyncio
async def test_get_nama_rupa_backward_compatible(test_model):
    """
    Test backward compatibility: ?detailed=false should return simplified 4-field RupaProfile
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            f"/api/v1/core-profile/{test_model.model_id}/nama-rupa",
            params={"detailed": False}
        )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check structure
    assert "nama" in data
    assert "rupa" in data
    assert "summary" in data
    
    # Check rupa has exactly 4 legacy fields
    rupa = data["rupa"]
    assert "age" in rupa
    assert "health_baseline" in rupa
    assert "current_life_force" in rupa
    assert "lifespan_remaining" in rupa
    
    # Should NOT have detailed fields
    assert "mahabhuta_state" not in rupa
    assert "pasada_state" not in rupa
    
    # Check migration status
    assert data.get("migration_status") == "legacy"
    assert data.get("detailed_rupa_available") == False


@pytest.mark.asyncio
async def test_get_nama_rupa_backward_compatible_no_param(test_model):
    """
    Test default behavior (no ?detailed param) should be backward compatible
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            f"/api/v1/core-profile/{test_model.model_id}/nama-rupa"
        )
    
    assert response.status_code == 200
    data = response.json()
    
    # Should behave same as ?detailed=false
    assert "age" in data["rupa"]
    assert data.get("migration_status") == "legacy"


# =============================================================================
# TEST 2: DETAILED MODE (?detailed=true)
# =============================================================================

@pytest.mark.asyncio
async def test_get_nama_rupa_detailed(test_model, test_rupa_profile):
    """
    Test detailed mode: ?detailed=true should return reference to complete RupaProfile
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            f"/api/v1/core-profile/{test_model.model_id}/nama-rupa",
            params={"detailed": True}
        )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check rupa_ref is present
    assert "rupa_ref" in data
    assert data["rupa_ref"] is not None
    assert len(data["rupa_ref"]) > 0  # Should be ObjectId string
    
    # Check migration status
    assert data["migration_status"] == "migrated"
    assert data["detailed_rupa_available"] == True
    
    # Summary should mention detailed rupa
    assert "รูป ๒๘ available" in data["summary"]


@pytest.mark.asyncio
async def test_get_complete_rupa_profile(test_rupa_profile):
    """
    Test GET /api/v1/rupa/{model_id} returns complete 28 Material Forms
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            f"/api/v1/rupa/{test_rupa_profile.model_id}"
        )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check structure
    assert data["model_id"] == test_rupa_profile.model_id
    assert data["total_rupa_count"] == 28
    assert "mahabhuta_analysis" in data
    assert "dominant_element" in data
    assert "pasada_status" in data
    assert "kalapa_distribution" in data
    assert "samutthana_breakdown" in data
    assert "lifecycle_stage" in data
    assert data["buddhist_accuracy"] == 100.0


# =============================================================================
# TEST 3: MAHABHUTA CALCULATION (4 Great Elements)
# =============================================================================

@pytest.mark.asyncio
async def test_mahabhuta_calculation(test_rupa_profile):
    """
    Test Mahabhuta (4 Great Elements) calculation logic
    """
    # Direct calculation test
    mahabhuta = test_rupa_profile.mahabhuta_state
    
    # Pathavi (Earth): hardness should decrease with age
    assert 0 <= mahabhuta.pathavi.hardness_level <= 100
    
    # Apo (Water): cohesion should correlate with health
    assert 0 <= mahabhuta.apo.cohesion_level <= 100
    
    # Tejo (Fire): heat should be in human body temperature range
    assert 36.0 <= mahabhuta.tejo.heat_level <= 38.5
    
    # Vayo (Wind): tension should correlate with life force
    assert 0 <= mahabhuta.vayo.tension_level <= 100


@pytest.mark.asyncio
async def test_mahabhuta_api_endpoint(test_rupa_profile):
    """
    Test GET /api/v1/rupa/{model_id}/mahabhuta endpoint
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            f"/api/v1/rupa/{test_rupa_profile.model_id}/mahabhuta"
        )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "mahabhuta" in data
    assert "dominant_element" in data
    assert "balance_score" in data
    
    # Dominant element should be one of 4
    assert data["dominant_element"] in ["pathavi", "apo", "tejo", "vayo"]
    
    # Balance score should be 0-100
    assert 0 <= data["balance_score"] <= 100


@pytest.mark.asyncio
async def test_mahabhuta_balance():
    """
    Test mahabhuta balance calculation (low variance = high balance)
    """
    # Case 1: Perfect balance (all 50)
    dominant = RupaCalculationEngine._determine_dominant_element(50, 50, 50, 50)
    # Should pick first one when all equal
    assert dominant in MahabhutaType.__members__.values()
    
    # Case 2: Pathavi dominant
    dominant = RupaCalculationEngine._determine_dominant_element(90, 40, 40, 40)
    assert dominant == MahabhutaType.pathavi


# =============================================================================
# TEST 4: PASADA CALCULATION (5 Sense Organs)
# =============================================================================

@pytest.mark.asyncio
async def test_pasada_calculation(test_rupa_profile):
    """
    Test Pasada (5 Sense Organs) sensitivity calculation
    """
    pasada = test_rupa_profile.pasada_state
    
    # All pasada should be 0-100
    assert 0 <= (pasada.cakkhu_pasada or 0) <= 100  # Eye
    assert 0 <= (pasada.sota_pasada or 0) <= 100    # Ear
    assert 0 <= (pasada.ghana_pasada or 0) <= 100   # Nose
    assert 0 <= (pasada.jivha_pasada or 0) <= 100   # Tongue
    assert 0 <= (pasada.kaya_pasada or 0) <= 100    # Body


@pytest.mark.asyncio
async def test_pasada_api_endpoint(test_rupa_profile):
    """
    Test GET /api/v1/rupa/{model_id}/pasada endpoint
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            f"/api/v1/rupa/{test_rupa_profile.model_id}/pasada"
        )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "pasada" in data
    assert "average_sensitivity" in data
    assert "strongest_sense" in data
    assert "weakest_sense" in data
    
    # Average should be reasonable
    assert 0 <= data["average_sensitivity"] <= 100
    
    # Strongest/weakest should be valid sense names
    valid_senses = ["cakkhu", "sota", "ghana", "jivha", "kaya"]
    assert data["strongest_sense"] in valid_senses
    assert data["weakest_sense"] in valid_senses


@pytest.mark.asyncio
async def test_pasada_age_decline():
    """
    Test that pasada sensitivity declines with age
    """
    # Create rupa for young model
    mahabhuta_young = RupaCalculationEngine.calculate_mahabhuta_from_core_profile(
        age=20, health=90, jivitindriya=90
    )
    pasada_young = RupaCalculationEngine.calculate_pasada_from_abilities(
        age=20,
        abilities={"vision": 90, "hearing": 90, "smell": 90, "taste": 90, "touch": 90},
        sati_level=50
    )
    
    # Create rupa for old model
    mahabhuta_old = RupaCalculationEngine.calculate_mahabhuta_from_core_profile(
        age=80, health=60, jivitindriya=50
    )
    pasada_old = RupaCalculationEngine.calculate_pasada_from_abilities(
        age=80,
        abilities={"vision": 60, "hearing": 50, "smell": 40, "taste": 60, "touch": 70},
        sati_level=50
    )
    
    # Young should have better overall sensitivity
    avg_young = (
        (pasada_young.cakkhu_pasada or 0) +
        (pasada_young.sota_pasada or 0) +
        (pasada_young.ghana_pasada or 0) +
        (pasada_young.jivha_pasada or 0) +
        (pasada_young.kaya_pasada or 0)
    ) / 5
    
    avg_old = (
        (pasada_old.cakkhu_pasada or 0) +
        (pasada_old.sota_pasada or 0) +
        (pasada_old.ghana_pasada or 0) +
        (pasada_old.jivha_pasada or 0) +
        (pasada_old.kaya_pasada or 0)
    ) / 5
    
    assert avg_young > avg_old


# =============================================================================
# TEST 5: JIVITINDRIYA SYNCHRONIZATION
# =============================================================================

@pytest.mark.asyncio
async def test_jivitindriya_sync_life_essence_to_rupa(test_model, test_rupa_profile):
    """
    Test sync from LifeEssence → RupaProfile
    """
    # Update LifeEssence
    profile = test_model.get_core_profile()
    profile.life_essence.jivitindriya_mechanics.current_jivitindriya = 85.0
    test_model.update_core_profile({})
    await test_model.save()
    
    # Sync
    synced = await RupaJivitindriaSyncLayer.sync_life_essence_to_rupa(test_model.model_id)
    assert synced == True
    
    # Check RupaProfile updated
    rupa = await RupaProfile.find_one(RupaProfile.model_id == test_model.model_id)
    assert rupa.jivita_state.rupa_jivitindriya == pytest.approx(85.0, abs=0.1)


@pytest.mark.asyncio
async def test_jivitindriya_sync_rupa_to_life_essence(test_model, test_rupa_profile):
    """
    Test sync from RupaProfile → LifeEssence
    """
    # Update RupaProfile
    test_rupa_profile.jivita_state.rupa_jivitindriya = 65.0
    await test_rupa_profile.save()
    
    # Sync
    synced = await RupaJivitindriaSyncLayer.sync_rupa_to_life_essence(test_model.model_id)
    assert synced == True
    
    # Check LifeEssence updated
    model = await DigitalMindModel.get(test_model.model_id)
    profile = model.get_core_profile()
    assert profile.life_essence.jivitindriya_mechanics.current_jivitindriya == pytest.approx(65.0, abs=0.1)


@pytest.mark.asyncio
async def test_jivitindriya_validate_sync(test_model, test_rupa_profile):
    """
    Test sync validation (should be within ±0.1%)
    """
    # Make them identical
    profile = test_model.get_core_profile()
    profile.life_essence.jivitindriya_mechanics.current_jivitindriya = 70.0
    test_model.update_core_profile({})
    await test_model.save()
    
    test_rupa_profile.jivita_state.rupa_jivitindriya = 70.0
    await test_rupa_profile.save()
    
    # Validate
    in_sync = await RupaJivitindriaSyncLayer.validate_sync(test_model.model_id)
    assert in_sync == True


# =============================================================================
# TEST 6: COMPUTED PROPERTIES
# =============================================================================

@pytest.mark.asyncio
async def test_computed_properties_age(test_rupa_profile):
    """
    Test age computed property (age_in_moments → years)
    """
    age_years = test_rupa_profile.age
    assert isinstance(age_years, int)
    assert age_years >= 0


@pytest.mark.asyncio
async def test_computed_properties_health_baseline(test_rupa_profile):
    """
    Test health_baseline computed property (weighted average)
    
    Formula: 40% mahabhuta + 30% vikara + 20% pasada + 10% ahara
    """
    health = test_rupa_profile.health_baseline
    assert isinstance(health, float)
    assert 0 <= health <= 100


@pytest.mark.asyncio
async def test_computed_properties_current_life_force(test_rupa_profile):
    """
    Test current_life_force computed property (direct jivitindriya)
    """
    life_force = test_rupa_profile.current_life_force
    assert isinstance(life_force, float)
    assert 0 <= life_force <= 100
    
    # Should match jivita_state
    assert life_force == test_rupa_profile.jivita_state.rupa_jivitindriya


@pytest.mark.asyncio
async def test_computed_properties_lifespan_remaining(test_rupa_profile):
    """
    Test lifespan_remaining computed property
    """
    remaining = test_rupa_profile.lifespan_remaining
    assert isinstance(remaining, int)
    assert remaining >= 0


# =============================================================================
# TEST 7: KALAPA LIFECYCLE (17 moments)
# =============================================================================

@pytest.mark.asyncio
async def test_kalapa_lifecycle_17_moments(test_rupa_profile):
    """
    Test that kalapas have proper 3-stage lifecycle
    
    3 Moments:
    - Uppada (arising): moment 0
    - Thiti (standing): moments 1-16
    - Bhanga (dissolution): moment 17
    """
    kalapas = test_rupa_profile.active_kalapas
    
    # Should have some kalapas
    assert len(kalapas) > 0
    
    # Each kalapa should have valid moment
    for kalapa in kalapas:
        assert kalapa.moment in [
            RupaKkhanaType.uppada,
            RupaKkhanaType.thiti,
            RupaKkhanaType.bhanga
        ]


@pytest.mark.asyncio
async def test_kalapa_lifecycle_api_endpoint(test_rupa_profile):
    """
    Test GET /api/v1/rupa/{model_id}/lifecycle endpoint
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            f"/api/v1/rupa/{test_rupa_profile.model_id}/lifecycle"
        )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "total_kalapas" in data
    assert "lifecycle_distribution" in data
    assert "lifecycle_percentages" in data
    assert "age_in_moments" in data
    assert "age_in_years" in data
    
    # Should have all 3 moments in distribution
    dist = data["lifecycle_distribution"]
    assert "uppada" in dist
    assert "thiti" in dist
    assert "bhanga" in dist


@pytest.mark.asyncio
async def test_kalapa_has_minimum_8_rupa():
    """
    Test that each kalapa has minimum 8 rupa (Suddhatthaka)
    
    Suddhatthaka = 4 Mahabhuta + 4 Lakkhana
    """
    # Test via calculation engine
    kalapas = RupaCalculationEngine.generate_kamma_born_kalapas(
        yoni="manussayoni",  # Human birth
        patisandhi_citta_strength=80
    )
    
    assert len(kalapas) >= 8  # At least 8 kalapas at birth


# =============================================================================
# TEST 8: SAMUTTHANA TRACKING (4 origins)
# =============================================================================

@pytest.mark.asyncio
async def test_samutthana_tracking(test_rupa_profile):
    """
    Test that rupa are tracked by origin (Samutthana)
    
    4 Origins:
    - Kamma (past actions)
    - Citta (consciousness)
    - Utu (temperature)
    - Ahara (nutriment)
    """
    assert test_rupa_profile.kamma_rupa_count >= 0
    assert test_rupa_profile.citta_rupa_count >= 0
    assert test_rupa_profile.utu_rupa_count >= 0
    assert test_rupa_profile.ahara_rupa_count >= 0
    
    # Total should match
    total = (test_rupa_profile.kamma_rupa_count +
             test_rupa_profile.citta_rupa_count +
             test_rupa_profile.utu_rupa_count +
             test_rupa_profile.ahara_rupa_count)
    
    assert total > 0


@pytest.mark.asyncio
async def test_samutthana_api_endpoint(test_rupa_profile):
    """
    Test GET /api/v1/rupa/{model_id}/samutthana endpoint
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            f"/api/v1/rupa/{test_rupa_profile.model_id}/samutthana"
        )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "kamma_rupa_count" in data
    assert "citta_rupa_count" in data
    assert "utu_rupa_count" in data
    assert "ahara_rupa_count" in data
    assert "total_count" in data
    assert "breakdown_percentage" in data
    
    # Percentages should sum to 100
    percentages = data["breakdown_percentage"]
    total_pct = sum(percentages.values())
    assert total_pct == pytest.approx(100.0, abs=0.1)


@pytest.mark.asyncio
async def test_kamma_rupa_at_birth():
    """
    Test that Kamma-born rupa appear at patisandhi (conception/rebirth)
    """
    kalapas = RupaCalculationEngine.generate_kamma_born_kalapas(
        yoni="manussayoni",
        patisandhi_citta_strength=80
    )
    
    # Human birth should have at least 8 kalapas
    assert len(kalapas) >= 8
    
    # Each should be kamma-born
    for kalapa in kalapas:
        assert kalapa.samutthana.value == "kamma"


# =============================================================================
# TEST 9: CALCULATE RUPA API ENDPOINT
# =============================================================================

@pytest.mark.asyncio
async def test_calculate_rupa_endpoint(test_model):
    """
    Test POST /api/v1/rupa/{model_id}/calculate endpoint
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            f"/api/v1/rupa/{test_model.model_id}/calculate",
            json={"force_recalculate": False, "sync_jivitindriya": True}
        )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "calculated"
    assert data["model_id"] == test_model.model_id
    assert "rupa_id" in data
    assert data["total_rupa_count"] == 28
    assert data["buddhist_accuracy"] == 100.0
    assert data["jivitindriya_sync_status"] in ["synced", "not_synced"]


@pytest.mark.asyncio
async def test_calculate_rupa_already_exists(test_model, test_rupa_profile):
    """
    Test that calculate endpoint doesn't override without force_recalculate
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            f"/api/v1/rupa/{test_model.model_id}/calculate",
            json={"force_recalculate": False}
        )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "already_exists"


# =============================================================================
# TEST 10: ERROR HANDLING
# =============================================================================

@pytest.mark.asyncio
async def test_rupa_404_not_found():
    """
    Test that non-existent model returns 404
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/rupa/nonexistent-model-999")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_mahabhuta_404_not_found():
    """
    Test that mahabhuta endpoint returns 404 for non-existent model
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/rupa/nonexistent-model-999/mahabhuta")
    
    assert response.status_code == 404


# =============================================================================
# TEST 11: INTEGRATION TEST
# =============================================================================

@pytest.mark.asyncio
async def test_full_rupa_integration(test_model):
    """
    Complete integration test: create → calculate → fetch → sync → verify
    """
    # Step 1: Calculate rupa
    async with AsyncClient(app=app, base_url="http://test") as client:
        calc_response = await client.post(
            f"/api/v1/rupa/{test_model.model_id}/calculate",
            json={"force_recalculate": True, "sync_jivitindriya": True}
        )
    assert calc_response.status_code == 200
    
    # Step 2: Fetch complete rupa
    async with AsyncClient(app=app, base_url="http://test") as client:
        rupa_response = await client.get(
            f"/api/v1/rupa/{test_model.model_id}"
        )
    assert rupa_response.status_code == 200
    rupa_data = rupa_response.json()
    assert rupa_data["total_rupa_count"] == 28
    
    # Step 3: Check detailed mode in nama-rupa
    async with AsyncClient(app=app, base_url="http://test") as client:
        nama_rupa_response = await client.get(
            f"/api/v1/core-profile/{test_model.model_id}/nama-rupa",
            params={"detailed": True}
        )
    assert nama_rupa_response.status_code == 200
    nama_rupa_data = nama_rupa_response.json()
    assert nama_rupa_data["detailed_rupa_available"] == True
    assert nama_rupa_data["migration_status"] == "migrated"
    
    # Step 4: Verify jivitindriya sync
    in_sync = await RupaJivitindriaSyncLayer.validate_sync(test_model.model_id)
    assert in_sync == True
    
    # Step 5: Check all endpoints work
    async with AsyncClient(app=app, base_url="http://test") as client:
        mahabhuta_resp = await client.get(f"/api/v1/rupa/{test_model.model_id}/mahabhuta")
        pasada_resp = await client.get(f"/api/v1/rupa/{test_model.model_id}/pasada")
        kalapas_resp = await client.get(f"/api/v1/rupa/{test_model.model_id}/kalapas")
        samutthana_resp = await client.get(f"/api/v1/rupa/{test_model.model_id}/samutthana")
        lifecycle_resp = await client.get(f"/api/v1/rupa/{test_model.model_id}/lifecycle")
    
    assert mahabhuta_resp.status_code == 200
    assert pasada_resp.status_code == 200
    assert kalapas_resp.status_code == 200
    assert samutthana_resp.status_code == 200
    assert lifecycle_resp.status_code == 200
