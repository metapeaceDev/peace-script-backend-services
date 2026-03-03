"""
Test Suite for Kamma Analytics Router
=====================================
Integration tests for /api/v1/kamma/* endpoints
"""

import pytest
from typing import Dict, Any
from httpx import AsyncClient, ASGITransport
from main import app
from documents import DigitalMindModel, CoreProfile
from modules.kamma_engine import log_new_kamma


# ====================================================================
# HELPER FUNCTIONS
# ====================================================================

async def log_new_kamma_and_save(
    profile_doc: DigitalMindModel,
    action_type: str,
    details: Dict[str, Any],
    is_kusala: bool = True,
    intensity: float = 1.0,
    **kwargs
) -> str:
    """
    Log kamma and save to database
    
    Wrapper around log_new_kamma() that:
    1. Converts Beanie document to dict
    2. Calls log_new_kamma() to modify dict
    3. Updates MongoDB directly to bypass Beanie caching issues
    
    Args:
        profile_doc: DigitalMindModel Beanie document
        action_type: Type of action
        details: Action details dict
        is_kusala: True for good kamma, False for bad
        intensity: Kamma intensity (0.0 - 10.0)
        **kwargs: Additional arguments for log_new_kamma()
        
    Returns:
        kamma_id: Generated kamma ID
    """
    # Convert to dict for log_new_kamma()
    profile_dict = profile_doc.model_dump()
    
    # Import kamma enums
    from modules.kamma_engine import KammaCategory, KammaOrigin
    
    # Map action_type to KammaOrigin
    origin_map = {
        "simulation": KammaOrigin.SIMULATION,
        "teaching": KammaOrigin.TEACHING,
        "dream": KammaOrigin.DREAM,
        "manual": KammaOrigin.MANUAL
    }
    origin = origin_map.get(action_type, KammaOrigin.SIMULATION)
    
    # Default to BHAVANA (cultivation) for kusala, MUSAVADA for akusala
    category = KammaCategory.BHAVANA if is_kusala else KammaCategory.MUSAVADA
    
    # Log kamma (modifies dict in-place)
    kamma_id = log_new_kamma(
        profile=profile_dict,
        kamma_category=category,
        origin=origin,
        details=details,
        is_kusala=is_kusala,
        intensity=intensity,
        **kwargs
    )
    
    # Update database directly using MongoDB update operation
    # Important: API reads from 'core_profile' (lowercase) not 'CoreProfile'!
    collection = DigitalMindModel.get_motor_collection()
    result = await collection.update_one(
        {"_id": profile_doc.id},
        {
            "$set": {
                "core_profile": profile_dict["CoreProfile"]  # Save to lowercase field
            }
        }
    )
    
    # Debug: Check if update succeeded
    print(f"✅ MongoDB update result: matched={result.matched_count}, modified={result.modified_count}")
    
    # Debug: Verify kamma log length
    ledger = profile_dict.get("CoreProfile", {}).get("SpiritualAssets", {}).get("KammaLedger", {})
    kamma_log = ledger.get("kamma_log", [])
    print(f"✅ Kamma log after update: {len(kamma_log)} entries")
    
    return kamma_id


# ====================================================================
# FIXTURES
# ====================================================================


@pytest.fixture
async def test_client():
    """Async test client"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def test_profile_with_kamma(test_client):
    """Create test profile with kamma data"""
    # Create profile with CoreProfile as dict (simpler approach)
    # We'll let get_core_profile() handle the conversion
    profile = DigitalMindModel(
        model_id="TEST_KAMMA_ANALYTICS",
        name="Test Kamma Profile",
        status_label="Testing",
        overall_level=1,
        level_progress_percent=0.0,
        image_url="http://test.com/image.png",
        core_state={
            "level_progress": 0,
            "level_up_threshold": 1000
        },
        conscious_profile={
            "parami_potentials": []
        },
        kamma_profile={
            "latent_tendencies": []
        }
    )
    await profile.insert()
    
    # IMPORTANT: Create dict once and reuse it for all kamma logging
    # Don't call model_dump() again or it will overwrite previous kammas
    profile_dict = profile.model_dump()
    
    # Add kamma entries (all modifications happen on the same dict)
    from modules.kamma_engine import KammaCategory, KammaOrigin
    
    # Parent kamma
    parent_id = log_new_kamma(
        profile=profile_dict,
        kamma_category=KammaCategory.BHAVANA,  # Meditation/cultivation
        origin=KammaOrigin.SIMULATION,
        details={"event": "meditation"},
        is_kusala=True,
        intensity=5.0
    )
    
    # Child kamma
    log_new_kamma(
        profile=profile_dict,
        kamma_category=KammaCategory.BHAVANA,  # Teaching mindfulness
        origin=KammaOrigin.TEACHING,
        details={"topic": "mindfulness"},
        is_kusala=True,
        intensity=3.0,
        trace_parent=parent_id
    )
    
    # Bad kamma
    log_new_kamma(
        profile=profile_dict,
        kamma_category=KammaCategory.PANATIPATA,  # Harm/violence in dream
        origin=KammaOrigin.DREAM,
        details={"theme": "nightmare"},
        is_kusala=False,
        intensity=2.0
    )
    
    # Pending kamma
    log_new_kamma(
        profile=profile_dict,
        kamma_category=KammaCategory.MUSAVADA,  # Speech-related
        origin=KammaOrigin.SIMULATION,
        details={"event": "anger_trigger"},
        is_kusala=False,
        intensity=7.0,
        condition="event:insult intensity>=5"
    )
    
    # Now save all kammas to database
    # Save the modified dict back to core_profile field
    profile.core_profile = profile_dict.get("CoreProfile", {})
    
    # Save using Beanie
    await profile.save()
    
    # Debug: Check raw data
    collection = DigitalMindModel.get_motor_collection()
    raw_doc = await collection.find_one({"_id": profile.id})
    
    if raw_doc:
        has_core_profile = "core_profile" in raw_doc
        has_CoreProfile = "CoreProfile" in raw_doc
        print(f"✅ MongoDB fields: core_profile={has_core_profile}, CoreProfile={has_CoreProfile}")
        
        if has_core_profile:
            raw_ledger = raw_doc["core_profile"].get("SpiritualAssets", {}).get("KammaLedger", {})
            raw_log = raw_ledger.get("kamma_log", [])
            print(f"✅ core_profile dict has: {len(raw_log)} kammas")
    
    # Debug: Test get_core_profile() method
    fresh_profile = await DigitalMindModel.find_one(DigitalMindModel.model_id == "TEST_KAMMA_ANALYTICS")
    if fresh_profile:
        # Try to get core profile using the method
        try:
            core_profile_obj = fresh_profile.get_core_profile()
            print(f"✅ get_core_profile() returned: {type(core_profile_obj)}")
            print(f"✅ spiritual_assets type: {type(core_profile_obj.spiritual_assets)}")
            
            # Access KammaLedger through spiritual_assets
            ledger = core_profile_obj.spiritual_assets.kamma_ledger
            print(f"✅ KammaLedger has {len(ledger.kamma_log)} kammas")
        except Exception as e:
            import traceback
            print(f"❌ get_core_profile() failed: {e}")
            traceback.print_exc()
    
    yield "TEST_KAMMA_ANALYTICS"
    
    # Cleanup
    await profile.delete()


class TestKammaSummaryEndpoint:
    """Test GET /api/v1/kamma/summary"""
    
    async def test_get_summary_success(self, test_client, test_profile_with_kamma):
        """Test getting kamma summary"""
        response = await test_client.get(
            "/api/v1/kamma/summary",
            params={"model_id": test_profile_with_kamma}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Debug: Print actual response
        print(f"\n🔍 API Response: {data}")
        print(f"🔍 total_kamma: {data.get('total_kamma')}")
        print(f"🔍 kusala_count: {data.get('kusala_count')}")
        
        assert "total_kamma" in data
        assert "kusala_stock_points" in data
        assert "akusala_stock_points" in data
        assert "pending_count" in data
        assert "pie" in data
        
        # Check counts
        assert data["total_kamma"] == 4
        assert data["kusala_count"] == 2
        assert data["akusala_count"] == 2
        assert data["pending_count"] == 1
    
    async def test_get_summary_model_not_found(self, test_client):
        """Test 404 when model not found"""
        response = await test_client.get(
            "/api/v1/kamma/summary",
            params={"model_id": "NONEXISTENT"}
        )
        
        assert response.status_code == 404


class TestKammaSankeyEndpoint:
    """Test GET /api/v1/kamma/sankey"""
    
    async def test_get_sankey_success(self, test_client, test_profile_with_kamma):
        """Test getting sankey diagram data"""
        response = await test_client.get(
            "/api/v1/kamma/sankey",
            params={"model_id": test_profile_with_kamma}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "nodes" in data
        assert "links" in data
        assert len(data["nodes"]) == 4
        assert len(data["links"]) >= 1  # At least one parent-child link


class TestKammaTimelineEndpoint:
    """Test GET /api/v1/kamma/timeline"""
    
    async def test_get_timeline_success(self, test_client, test_profile_with_kamma):
        """Test getting timeline"""
        response = await test_client.get(
            "/api/v1/kamma/timeline",
            params={"model_id": test_profile_with_kamma, "limit": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "timeline" in data
        assert "total" in data
        assert len(data["timeline"]) == 4
        assert data["total"] == 4
    
    async def test_get_timeline_with_limit(self, test_client, test_profile_with_kamma):
        """Test timeline with limit"""
        response = await test_client.get(
            "/api/v1/kamma/timeline",
            params={"model_id": test_profile_with_kamma, "limit": 2}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["timeline"]) == 2


class TestKammaByStatusEndpoint:
    """Test GET /api/v1/kamma/by_status"""
    
    async def test_get_by_status_success(self, test_client, test_profile_with_kamma):
        """Test getting kamma by status"""
        response = await test_client.get(
            "/api/v1/kamma/by_status",
            params={"model_id": test_profile_with_kamma}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "pending" in data
        assert "active" in data
        assert "finished" in data
        assert "expired" in data
        
        assert len(data["pending"]) == 1


class TestKammaDetailEndpoint:
    """Test GET /api/v1/kamma/detail"""
    
    async def test_get_detail_success(self, test_client, test_profile_with_kamma):
        """Test getting kamma detail with chain"""
        # First get timeline to find a kamma_id
        timeline_response = await test_client.get(
            "/api/v1/kamma/timeline",
            params={"model_id": test_profile_with_kamma, "limit": 1}
        )
        kamma_id = timeline_response.json()["timeline"][0]["kamma_id"]
        
        # Get detail
        response = await test_client.get(
            "/api/v1/kamma/detail",
            params={"model_id": test_profile_with_kamma, "kamma_id": kamma_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["kamma_id"] == kamma_id
        assert "chain_length" in data
        assert "age_days" in data
    
    async def test_get_detail_not_found(self, test_client, test_profile_with_kamma):
        """Test 404 when kamma not found"""
        response = await test_client.get(
            "/api/v1/kamma/detail",
            params={"model_id": test_profile_with_kamma, "kamma_id": "nonexistent"}
        )
        
        assert response.status_code == 404


class TestKammaFilterEndpoint:
    """Test GET /api/v1/kamma/filter"""
    
    async def test_filter_by_kusala(self, test_client, test_profile_with_kamma):
        """Test filtering by kusala"""
        response = await test_client.get(
            "/api/v1/kamma/filter",
            params={"model_id": test_profile_with_kamma, "kusala": True}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert "total" in data
        assert data["total"] == 2  # 2 kusala kamma
        
        # All results should be kusala
        for kamma in data["results"]:
            assert kamma["is_kusala"] is True
    
    async def test_filter_by_type(self, test_client, test_profile_with_kamma):
        """Test filtering by type"""
        response = await test_client.get(
            "/api/v1/kamma/filter",
            params={"model_id": test_profile_with_kamma, "type": "simulation"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total"] == 2  # 2 simulation kamma
    
    async def test_filter_by_intensity(self, test_client, test_profile_with_kamma):
        """Test filtering by intensity range"""
        response = await test_client.get(
            "/api/v1/kamma/filter",
            params={
                "model_id": test_profile_with_kamma,
                "intensity_min": 5.0,
                "intensity_max": 10.0
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should find kamma with intensity >= 5
        assert data["total"] >= 1


class TestKammaExportEndpoint:
    """Test GET /api/v1/kamma/export"""
    
    async def test_export_json(self, test_client, test_profile_with_kamma):
        """Test exporting kamma data as JSON"""
        response = await test_client.get(
            "/api/v1/kamma/export",
            params={"model_id": test_profile_with_kamma, "format": "json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "data" in data
        assert "metadata" in data
        assert data["metadata"]["format"] == "json"
        assert data["metadata"]["total_kamma"] == 4
    
    async def test_export_with_chains(self, test_client, test_profile_with_kamma):
        """Test exporting with full chain data"""
        response = await test_client.get(
            "/api/v1/kamma/export",
            params={
                "model_id": test_profile_with_kamma,
                "format": "json",
                "include_chains": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "chains" in data["data"]
        assert data["metadata"]["include_chains"] is True
