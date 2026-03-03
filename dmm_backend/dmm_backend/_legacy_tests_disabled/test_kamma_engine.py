"""
Test Suite for Kamma Engine
===========================
Peace Script V.14 - Kamma System Unit Tests

Tests all kamma_engine functions:
- log_new_kamma()
- trace_kamma()
- update_kamma_status()
- check_and_trigger_pending_kamma()
- expire_kamma_by_liberation()
- get_kamma_summary()
"""

import pytest
from datetime import datetime
from modules.kamma_engine import (
    log_new_kamma,
    trace_kamma,
    update_kamma_status,
    check_and_trigger_pending_kamma,
    expire_kamma_by_liberation,
    get_kamma_summary,
    KammaStatus,
    KammaType,
)


@pytest.fixture
def empty_profile():
    """Empty profile with KammaLedger structure"""
    return {
        "model_id": "TEST_001",
        "CoreProfile": {
            "SpiritualAssets": {
                "KammaLedger": {
                    "kusala_stock_points": 0.0,
                    "akusala_stock_points": 0.0,
                    "dominant_pending_kamma": [],
                    "kamma_log": []
                }
            }
        }
    }


@pytest.fixture
def profile_with_kamma():
    """Profile with some existing kamma"""
    return {
        "model_id": "TEST_002",
        "CoreProfile": {
            "SpiritualAssets": {
                "KammaLedger": {
                    "kusala_stock_points": 10.0,
                    "akusala_stock_points": 5.0,
                    "dominant_pending_kamma": [],
                    "kamma_log": [
                        {
                            "kamma_id": "k001",
                            "timestamp": "2025-01-01T10:00:00Z",
                            "action_type": "simulation",
                            "kusala": True,
                            "intensity": 2.0,
                            "details": {"event": "meditation"},
                            "trace_parent": None,
                            "trace_children": [],
                            "status": KammaStatus.FINISHED,
                            "condition": None,
                        }
                    ]
                }
            }
        }
    }


class TestLogNewKamma:
    """Test log_new_kamma() function"""
    
    def test_log_kusala_kamma(self, empty_profile):
        """Test logging kusala (good) kamma"""
        kamma_id = log_new_kamma(
            profile=empty_profile,
            action_type="simulation",
            details={"event": "dana"},
            is_kusala=True,
            intensity=2.0
        )
        
        assert kamma_id is not None
        assert kamma_id.startswith("kamma_")
        
        ledger = empty_profile["CoreProfile"]["SpiritualAssets"]["KammaLedger"]
        assert ledger["kusala_stock_points"] == 2.0
        assert ledger["akusala_stock_points"] == 0.0
        assert len(ledger["kamma_log"]) == 1
        
        log_entry = ledger["kamma_log"][0]
        assert log_entry["kamma_id"] == kamma_id
        assert log_entry["kusala"] is True
        assert log_entry["intensity"] == 2.0
        assert log_entry["status"] == KammaStatus.FINISHED
    
    def test_log_akusala_kamma(self, empty_profile):
        """Test logging akusala (bad) kamma"""
        kamma_id = log_new_kamma(
            profile=empty_profile,
            action_type="simulation",
            details={"event": "anger"},
            is_kusala=False,
            intensity=3.0
        )
        
        ledger = empty_profile["CoreProfile"]["SpiritualAssets"]["KammaLedger"]
        assert ledger["kusala_stock_points"] == 0.0
        assert ledger["akusala_stock_points"] == 3.0
        
        log_entry = ledger["kamma_log"][0]
        assert log_entry["kusala"] is False
    
    def test_log_pending_kamma_with_condition(self, empty_profile):
        """Test logging pending kamma with condition"""
        kamma_id = log_new_kamma(
            profile=empty_profile,
            action_type="simulation",
            details={"event": "reactive_anger"},
            is_kusala=False,
            intensity=5.0,
            condition="event:insult intensity>=5"
        )
        
        ledger = empty_profile["CoreProfile"]["SpiritualAssets"]["KammaLedger"]
        
        # Pending kamma should be in dominant_pending_kamma
        assert len(ledger["dominant_pending_kamma"]) == 1
        pending = ledger["dominant_pending_kamma"][0]
        assert pending["kamma_id"] == kamma_id
        assert pending["status"] == KammaStatus.PENDING
        assert pending["condition"] == "event:insult intensity>=5"
        
        # Should also be in kamma_log
        log_entry = next(k for k in ledger["kamma_log"] if k["kamma_id"] == kamma_id)
        assert log_entry["status"] == KammaStatus.PENDING
    
    def test_log_kamma_with_parent(self, profile_with_kamma):
        """Test logging kamma with parent relationship"""
        parent_id = "k001"
        
        child_id = log_new_kamma(
            profile=profile_with_kamma,
            action_type="teaching",
            details={"topic": "metta"},
            is_kusala=True,
            intensity=1.5,
            trace_parent=parent_id
        )
        
        ledger = profile_with_kamma["CoreProfile"]["SpiritualAssets"]["KammaLedger"]
        
        # Child should have parent reference
        child = next(k for k in ledger["kamma_log"] if k["kamma_id"] == child_id)
        assert child["trace_parent"] == parent_id
        
        # Parent should have child in trace_children
        parent = next(k for k in ledger["kamma_log"] if k["kamma_id"] == parent_id)
        assert child_id in parent["trace_children"]


class TestTraceKamma:
    """Test trace_kamma() function"""
    
    def test_trace_single_kamma(self, profile_with_kamma):
        """Test tracing kamma without chain"""
        result = trace_kamma(profile_with_kamma, "k001")
        
        assert result is not None
        assert result["log"]["kamma_id"] == "k001"
        assert result["parent"] is None
        assert result["children"] == []
    
    def test_trace_kamma_with_children(self, empty_profile):
        """Test tracing kamma with children"""
        # Create parent
        parent_id = log_new_kamma(
            profile=empty_profile,
            action_type="simulation",
            details={"event": "meditation"},
            is_kusala=True,
            intensity=3.0
        )
        
        # Create children
        child1_id = log_new_kamma(
            profile=empty_profile,
            action_type="teaching",
            details={"topic": "mindfulness"},
            is_kusala=True,
            intensity=2.0,
            trace_parent=parent_id
        )
        
        child2_id = log_new_kamma(
            profile=empty_profile,
            action_type="dream",
            details={"theme": "peace"},
            is_kusala=True,
            intensity=1.0,
            trace_parent=parent_id
        )
        
        # Trace parent
        result = trace_kamma(empty_profile, parent_id)
        
        assert result is not None
        assert len(result["children"]) == 2
        assert result["children"][0]["log"]["kamma_id"] == child1_id
        assert result["children"][1]["log"]["kamma_id"] == child2_id


class TestUpdateKammaStatus:
    """Test update_kamma_status() function"""
    
    def test_activate_pending_kamma(self, empty_profile):
        """Test activating pending kamma"""
        # Create pending kamma
        kamma_id = log_new_kamma(
            profile=empty_profile,
            action_type="simulation",
            details={"event": "anger"},
            is_kusala=False,
            intensity=5.0,
            condition="event:insult"
        )
        
        # Activate it
        success = update_kamma_status(
            profile=empty_profile,
            kamma_id=kamma_id,
            new_status=KammaStatus.ACTIVE,
            event_type="trigger",
            event_detail={"triggered_by": "insult_event"}
        )
        
        assert success is True
        
        ledger = empty_profile["CoreProfile"]["SpiritualAssets"]["KammaLedger"]
        log_entry = ledger["kamma_log"][0]
        assert log_entry["status"] == KammaStatus.ACTIVE
        assert log_entry["activated_at"] is not None
    
    def test_finish_active_kamma(self, empty_profile):
        """Test finishing active kamma"""
        kamma_id = log_new_kamma(
            profile=empty_profile,
            action_type="teaching",
            details={"topic": "patience"},
            is_kusala=True,
            intensity=2.0
        )
        
        # Change to active first
        update_kamma_status(empty_profile, kamma_id, KammaStatus.ACTIVE, "start", {})
        
        # Then finish
        success = update_kamma_status(
            profile=empty_profile,
            kamma_id=kamma_id,
            new_status=KammaStatus.FINISHED,
            event_type="complete",
            event_detail={}
        )
        
        assert success is True
        ledger = empty_profile["CoreProfile"]["SpiritualAssets"]["KammaLedger"]
        log_entry = ledger["kamma_log"][0]
        assert log_entry["status"] == KammaStatus.FINISHED
        assert log_entry["finished_at"] is not None


class TestCheckAndTriggerPendingKamma:
    """Test check_and_trigger_pending_kamma() function"""
    
    def test_trigger_matching_condition(self, empty_profile):
        """Test triggering kamma when condition matches"""
        # Create pending kamma with condition
        log_new_kamma(
            profile=empty_profile,
            action_type="simulation",
            details={"event": "anger_response"},
            is_kusala=False,
            intensity=5.0,
            condition="event:insult intensity>=5"
        )
        
        # Trigger with matching event
        triggered = check_and_trigger_pending_kamma(
            profile=empty_profile,
            event_type="simulation",
            event_detail={"event": "insult", "intensity": 7}
        )
        
        assert len(triggered) == 1
        
        # Check status changed to active
        ledger = empty_profile["CoreProfile"]["SpiritualAssets"]["KammaLedger"]
        log_entry = ledger["kamma_log"][0]
        assert log_entry["status"] == KammaStatus.ACTIVE
    
    def test_no_trigger_insufficient_intensity(self, empty_profile):
        """Test not triggering when intensity too low"""
        log_new_kamma(
            profile=empty_profile,
            action_type="simulation",
            details={"event": "anger_response"},
            is_kusala=False,
            intensity=5.0,
            condition="event:insult intensity>=5"
        )
        
        # Trigger with insufficient intensity
        triggered = check_and_trigger_pending_kamma(
            profile=empty_profile,
            event_type="simulation",
            event_detail={"event": "insult", "intensity": 3}
        )
        
        assert len(triggered) == 0


class TestExpireKammaByLiberation:
    """Test expire_kamma_by_liberation() function"""
    
    def test_sotapanna_expires_lower_realm(self, empty_profile):
        """Test Sotāpanna attainment expires lower realm kamma"""
        # Create various kamma
        log_new_kamma(empty_profile, "simulation", {"realm": "hell"}, False, 5.0)
        log_new_kamma(empty_profile, "simulation", {"realm": "human"}, True, 3.0)
        
        # Attain Sotāpanna
        expired = expire_kamma_by_liberation(
            profile=empty_profile,
            liberation_type="sotapanna",
            liberation_detail={"attainment": "stream_entry"}
        )
        
        assert len(expired) > 0
        
        ledger = empty_profile["CoreProfile"]["SpiritualAssets"]["KammaLedger"]
        # Check some kamma expired
        expired_count = sum(1 for k in ledger["kamma_log"] if k["status"] == KammaStatus.EXPIRED)
        assert expired_count > 0


class TestGetKammaSummary:
    """Test get_kamma_summary() function"""
    
    def test_summary_with_data(self, profile_with_kamma):
        """Test getting summary with existing data"""
        summary = get_kamma_summary(profile_with_kamma)
        
        assert summary["total_kamma"] == 1
        assert summary["kusala_stock_points"] == 10.0
        assert summary["akusala_stock_points"] == 5.0
        assert summary["finished_count"] == 1
    
    def test_summary_empty_profile(self, empty_profile):
        """Test getting summary from empty profile"""
        summary = get_kamma_summary(empty_profile)
        
        assert summary["total_kamma"] == 0
        assert summary["kusala_stock_points"] == 0.0
        assert summary["akusala_stock_points"] == 0.0
        assert summary["pending_count"] == 0
        assert summary["active_count"] == 0
        assert summary["finished_count"] == 0
        assert summary["expired_count"] == 0
