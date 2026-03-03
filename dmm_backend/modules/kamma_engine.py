"""
Peace Script V.14 - Kamma Engine Module
========================================
Core engine for Kamma (Karma) management system following Buddhist principles
Based on planning documents Step 2.2.5 - 2.2.8

Features:
- Log new kamma from simulation/liberation/dream
- Trace kamma chains (parent-child relationships)
- Update kamma status (pending → active → finished/expired)
- Causal chain tracking with condition matching
- Integration with DigitalMindModel KammaLedger

Buddhist Concept Alignment:
- Kusala (กรรมดี) vs Akusala (กรรมชั่ว)
- Pending Kamma (กรรมค้าง) = kamma awaiting conditions
- Kamma giving fruit (วิบาก) = consequence manifestation
- Liberation (ประหารสังโยชน์) expires certain kamma types
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid
from enum import Enum

from core.logging_config import get_logger

logger = get_logger(__name__)


# =====================================================================
# Kamma Enums
# =====================================================================

class KammaCategory(str, Enum):
    """
    Specific Kamma Categories based on Akusala-kammapatha 10 and Kusala-kammapatha 10
    อกุศลกรรมบถ ๑๐ และ กุศลกรรมบถ ๑๐
    """
    # Akusala Kayakamma (Physical)
    PANATIPATA = "panatipata"                # 1. ปาณาติปาตา (Killing)
    ADINNADANA = "adinnadana"                # 2. อทินนาทานา (Stealing)
    KAMESU_MICCHACARA = "kamesu_micchacara"  # 3. กาเมสุมิจฉาจารา (Sexual misconduct)

    # Akusala Vacikamma (Verbal)
    MUSAVADA = "musavada"                    # 4. มุสาวาทา (Lying)
    PISUNAVACA = "pisunavaca"                # 5. ปิสุณาวาจา (Slanderous speech)
    PHARUSAVACA = "pharusavaca"              # 6. ผรุสวาจา (Harsh speech)
    SAMPHAPPALAPA = "samphappalapa"          # 7. สัมผัปปลาปา (Frivolous talk)

    # Akusala Manokamma (Mental)
    ABHIJJHA = "abhijjha"                    # 8. อภิชฌา (Covetousness)
    BYAPADA = "byapada"                      # 9. พยาบาท (Ill-will)
    MICCHADITTHI = "micchaditthi"            # 10. มิจฉาทิฏฐิ (Wrong view)

    # Kusala Virati (Abstinence) & Actions
    PANATIPATA_VIRATI = "panatipata_virati"          # Abstinence from killing -> Metta
    ADINNADANA_VIRATI = "adinnadana_virati"          # Abstinence from stealing -> Dana
    KAMESU_MICCHACARA_VIRATI = "kamesu_micchacara_virati" # Abstinence from sexual misconduct
    MUSAVADA_VIRATI = "musavada_virati"              # Abstinence from lying -> Sacca
    PISUNAVACA_VIRATI = "pisunavaca_virati"          # Abstinence from slander
    PHARUSAVACA_VIRATI = "pharusavaca_virati"        # Abstinence from harsh speech
    SAMPHAPPALAPA_VIRATI = "samphappalapa_virati"    # Abstinence from frivolous talk
    ANABHIJJHA = "anabhijjha"                        # Non-covetousness
    ABYAPADA = "abyapada"                            # Non-ill-will / Metta
    SAMMADITTHI = "sammaditthi"                      # Right view

    # General Kusala
    DANA = "dana"                                    # Generosity
    SILA = "sila"                                    # Morality
    BHAVANA = "bhavana"                              # Meditation
    METTA = "metta"                                  # Loving-kindness
    KARUNA = "karuna"                                # Compassion
    MUDITA = "mudita"                                # Sympathetic joy
    UPPEKKHA = "upekkha"                             # Equanimity
    
    # Other
    UNKNOWN = "unknown"


class KammaStatus(str, Enum):
    """Kamma lifecycle status constants"""
    PENDING = "pending"      # รอเงื่อนไข
    ACTIVE = "active"        # กำลังส่งผล
    FINISHED = "finished"    # ส่งผลเสร็จสิ้น
    EXPIRED = "expired"      # หมดกำลัง


class KammaOrigin(str, Enum):
    """Kamma action origins"""
    SIMULATION = "simulation"
    LIBERATION = "liberation"
    DREAM = "dream"
    MANUAL = "manual"
    TEACHING = "teaching"


# =====================================================================
# Core Kamma Engine Functions
# =====================================================================

def log_new_kamma(
    profile: Dict[str, Any],
    kamma_category: KammaCategory,
    details: Dict[str, Any],
    origin: KammaOrigin = KammaOrigin.SIMULATION,
    is_kusala: bool = True,
    intensity: float = 1.0,
    consequence_link: Optional[str] = None,
    trace_parent: Optional[str] = None,
    condition: Optional[str] = None
) -> str:
    """
    Log new kamma entry to profile's KammaLedger with specific category.
    
    Args:
        profile: DigitalMindModel profile dict
        kamma_category: Specific type of kamma (e.g., KammaCategory.PANATIPATA)
        details: Action details dict
        origin: The origin of the kamma action (e.g., simulation, dream)
        is_kusala: True for wholesome (kusala), False for unwholesome (akusala)
        intensity: Intensity/impact level (0.0-99.0)
        consequence_link: Optional link to consequence/result
        trace_parent: Optional parent kamma_id for chain tracking
        condition: Optional condition string for pending kamma triggering
        
    Returns:
        kamma_id: New kamma entry ID
        
    Example:
        >>> kamma_id = log_new_kamma(
        ...     profile, 
        ...     kamma_category=KammaCategory.BHAVANA,
        ...     details={"duration_minutes": 30, "type": "samatha"},
        ...     is_kusala=True,
        ...     intensity=5.0
        ... )
    """
    kamma_id = f"kamma_{uuid.uuid4().hex[:12]}"
    timestamp = datetime.utcnow().isoformat()
    
    # Ensure KammaLedger structure exists
    if "CoreProfile" not in profile:
        profile["CoreProfile"] = {}
    if "SpiritualAssets" not in profile["CoreProfile"]:
        profile["CoreProfile"]["SpiritualAssets"] = {}
    if "KammaLedger" not in profile["CoreProfile"]["SpiritualAssets"]:
        profile["CoreProfile"]["SpiritualAssets"]["KammaLedger"] = {
            "kusala_stock_points": 0,
            "akusala_stock_points": 0,
            "dominant_pending_kamma": [],
            "kamma_log": []
        }
    
    ledger = profile["CoreProfile"]["SpiritualAssets"]["KammaLedger"]
    
    # Create kamma entry
    kamma_entry = {
        "kamma_id": kamma_id,
        "timestamp": timestamp,
        "origin": origin.value,
        "category": kamma_category.value,
        "is_kusala": is_kusala,
        "details": details,
        "intensity": intensity,
        "consequence_link": consequence_link,
        "trace_parent": trace_parent,
        "trace_children": [],
        "status": KammaStatus.PENDING.value if condition else KammaStatus.FINISHED.value,
        "condition": condition,
        "activated_at": None,
        "finished_at": None if condition else timestamp,
        "expired_at": None
    }
    
    # Add to log
    ledger["kamma_log"].append(kamma_entry)
    
    # Update stock points
    impact_points = intensity * (1 if is_kusala else -1)
    if is_kusala:
        ledger["kusala_stock_points"] = ledger.get("kusala_stock_points", 0) + impact_points
    else:
        ledger["akusala_stock_points"] = ledger.get("akusala_stock_points", 0) + abs(impact_points)
    
    # Add to pending if has condition
    if condition:
        ledger["dominant_pending_kamma"].append({
            "kamma_id": kamma_id,
            "category": kamma_category.value,
            "condition": condition,
            "status": KammaStatus.PENDING.value,
            "created_at": timestamp,
            "activated_at": None,
            "finished_at": None,
            "expired_at": None
        })
    
    # Link parent-child if trace_parent provided
    if trace_parent:
        for log in ledger["kamma_log"]:
            if log["kamma_id"] == trace_parent:
                if "trace_children" not in log:
                    log["trace_children"] = []
                log["trace_children"].append(kamma_id)
                break
    
    logger.info(
        f"Logged new kamma: {kamma_id} | category={kamma_category.value} | kusala={is_kusala} | "
        f"intensity={intensity} | pending={bool(condition)}"
    )
    
    return kamma_id


def trace_kamma(profile: Dict[str, Any], kamma_id: str) -> Optional[Dict[str, Any]]:
    """
    Trace kamma entry with full parent-child chain
    
    Args:
        profile: DigitalMindModel profile dict
        kamma_id: Kamma ID to trace
        
    Returns:
        Dict with log, parent, children structure, or None if not found
        
    Example:
        >>> result = trace_kamma(profile, "kamma_abc123")
        >>> print(result["log"]["kamma_id"])
        >>> print([c["log"]["kamma_id"] for c in result["children"]])
    """
    ledger = profile.get("CoreProfile", {}).get("SpiritualAssets", {}).get("KammaLedger", {})
    kamma_log = ledger.get("kamma_log", [])
    
    # Find target kamma
    target_log = None
    for log in kamma_log:
        if log["kamma_id"] == kamma_id:
            target_log = log
            break
    
    if not target_log:
        logger.warning(f"Kamma not found: {kamma_id}")
        return None
    
    # Trace parent (shallow - no recursive children to avoid infinite loop)
    parent_trace = None
    if target_log.get("trace_parent"):
        parent_log = None
        for log in kamma_log:
            if log["kamma_id"] == target_log["trace_parent"]:
                parent_log = log
                break
        if parent_log:
            parent_trace = {"log": parent_log, "parent": None, "children": []}
    
    # Trace children (shallow - no recursive parents to avoid infinite loop)
    children_trace = []
    for child_id in target_log.get("trace_children", []):
        child_log = None
        for log in kamma_log:
            if log["kamma_id"] == child_id:
                child_log = log
                break
        if child_log:
            children_trace.append({"log": child_log, "parent": None, "children": []})
    
    return {
        "log": target_log,
        "parent": parent_trace,
        "children": children_trace
    }


def update_kamma_status(
    profile: Dict[str, Any],
    kamma_id: str,
    new_status: str,
    event_type: Optional[str] = None,
    event_detail: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Update kamma status (pending → active → finished/expired)
    
    Args:
        profile: DigitalMindModel profile dict
        kamma_id: Kamma ID to update
        new_status: New status (active/finished/expired)
        event_type: Optional event type that triggered status change
        event_detail: Optional event details for condition matching
        
    Returns:
        bool: True if updated successfully, False otherwise
        
    Example:
        >>> updated = update_kamma_status(
        ...     profile, 
        ...     "KAMMA-abc123", 
        ...     KammaStatus.ACTIVE,
        ...     event_type="simulation",
        ...     event_detail={"trigger": "insult"}
        ... )
    """
    ledger = profile.get("CoreProfile", {}).get("SpiritualAssets", {}).get("KammaLedger", {})
    kamma_log = ledger.get("kamma_log", [])
    pending_kamma = ledger.get("dominant_pending_kamma", [])
    
    now = datetime.utcnow().isoformat()
    updated = False
    
    # Update in kamma_log
    for log in kamma_log:
        if log["kamma_id"] == kamma_id:
            old_status = log.get("status")
            log["status"] = new_status
            
            if new_status == KammaStatus.ACTIVE and not log.get("activated_at"):
                log["activated_at"] = now
            elif new_status == KammaStatus.FINISHED and not log.get("finished_at"):
                log["finished_at"] = now
            elif new_status == KammaStatus.EXPIRED and not log.get("expired_at"):
                log["expired_at"] = now
            
            logger.info(f"Updated kamma status: {kamma_id} | {old_status} → {new_status}")
            updated = True
            break
    
    # Update in dominant_pending_kamma
    for pending in pending_kamma:
        if pending["kamma_id"] == kamma_id:
            old_status = pending.get("status")
            pending["status"] = new_status
            
            if new_status == KammaStatus.ACTIVE and not pending.get("activated_at"):
                pending["activated_at"] = now
            elif new_status == KammaStatus.FINISHED and not pending.get("finished_at"):
                pending["finished_at"] = now
            elif new_status == KammaStatus.EXPIRED and not pending.get("expired_at"):
                pending["expired_at"] = now
            
            break
    
    return updated


def check_and_trigger_pending_kamma(
    profile: Dict[str, Any],
    event_type: str,
    event_detail: Dict[str, Any]
) -> List[str]:
    """
    Check pending kamma and trigger those matching conditions
    
    Args:
        profile: DigitalMindModel profile dict
        event_type: Event type (simulation/liberation/dream)
        event_detail: Event details for condition matching
        
    Returns:
        List of triggered kamma_ids
        
    Example:
        >>> triggered = check_and_trigger_pending_kamma(
        ...     profile,
        ...     event_type="simulation",
        ...     event_detail={"event": "insult", "intensity": 8}
        ... )
    """
    ledger = profile.get("CoreProfile", {}).get("SpiritualAssets", {}).get("KammaLedger", {})
    pending_kamma = ledger.get("dominant_pending_kamma", [])
    
    triggered_ids = []
    
    for kamma in pending_kamma:
        if kamma.get("status") != KammaStatus.PENDING:
            continue
        
        condition = kamma.get("condition", "")
        
        # Simple condition matching (can be extended with expression evaluator)
        if matches_condition(condition, event_type, event_detail):
            # Trigger: pending → active
            update_kamma_status(
                profile,
                kamma["kamma_id"],
                KammaStatus.ACTIVE,
                event_type=event_type,
                event_detail=event_detail
            )
            triggered_ids.append(kamma["kamma_id"])
            
            logger.info(
                f"Triggered pending kamma: {kamma['kamma_id']} | "
                f"condition='{condition}' | event={event_type}"
            )
    
    return triggered_ids


def expire_kamma_by_liberation(
    profile: Dict[str, Any],
    liberation_type: str,
    liberation_detail: Dict[str, Any]
) -> List[str]:
    """
    Expire kamma that loses opportunity due to liberation/path attainment
    
    Args:
        profile: DigitalMindModel profile dict
        liberation_type: Type of liberation (sotāpanna/sakadāgāmi/anāgāmi/arahant)
        liberation_detail: Liberation event details
        
    Returns:
        List of expired kamma_ids
        
    Example:
        >>> expired = expire_kamma_by_liberation(
        ...     profile,
        ...     liberation_type="sotāpanna",
        ...     liberation_detail={"samyojana_broken": ["sakkāya-diṭṭhi", "vicikicchā"]}
        ... )
    """
    ledger = profile.get("CoreProfile", {}).get("SpiritualAssets", {}).get("KammaLedger", {})
    kamma_log = ledger.get("kamma_log", [])
    
    expired_ids = []
    
    for kamma in kamma_log:
        # Skip already expired kamma (but allow finished kamma to be expired by liberation)
        if kamma.get("status") == KammaStatus.EXPIRED:
            continue
        
        # Check if this kamma type expires with this liberation
        if should_expire_by_liberation(kamma, liberation_type, liberation_detail):
            update_kamma_status(
                profile,
                kamma["kamma_id"],
                KammaStatus.EXPIRED,
                event_type="liberation",
                event_detail=liberation_detail
            )
            expired_ids.append(kamma["kamma_id"])
            
            logger.info(
                f"Expired kamma by liberation: {kamma['kamma_id']} | "
                f"liberation={liberation_type}"
            )
    
    return expired_ids


# =====================================================================
# Helper Functions
# =====================================================================

def matches_condition(condition: str, event_type: str, event_detail: Dict[str, Any]) -> bool:
    """
    Simple condition matcher (can be extended with expression evaluator)
    
    Args:
        condition: Condition string (e.g., "event:insult intensity>=5")
        event_type: Event type
        event_detail: Event details dict
        
    Returns:
        bool: True if condition matches
        
    Example:
        >>> matches_condition(
        ...     "event:insult intensity>=5",
        ...     "simulation",
        ...     {"event": "insult", "intensity": 8}
        ... )
        True
    """
    if not condition:
        return False
    
    condition_lower = condition.lower().strip()
    
    # Parse conditions (space-separated)
    conditions = condition_lower.split()
    
    for cond in conditions:
        # Format: "key:value" or "key>=value" or "key<=value" or "key==value"
        if ":" in cond:
            # key:value format
            key, value = cond.split(":", 1)
            event_value = str(event_detail.get(key, "")).lower()
            if value not in event_value:
                return False
        elif ">=" in cond:
            # key>=value format
            key, value = cond.split(">=", 1)
            try:
                event_value = float(event_detail.get(key, 0))
                threshold = float(value)
                if event_value < threshold:
                    return False
            except (ValueError, TypeError):
                return False
        elif "<=" in cond:
            # key<=value format
            key, value = cond.split("<=", 1)
            try:
                event_value = float(event_detail.get(key, 999))
                threshold = float(value)
                if event_value > threshold:
                    return False
            except (ValueError, TypeError):
                return False
        elif "==" in cond:
            # key==value format
            key, value = cond.split("==", 1)
            event_value = str(event_detail.get(key, "")).lower()
            if event_value != value:
                return False
    
    # All conditions must match
    return True


def should_expire_by_liberation(
    kamma: Dict[str, Any],
    liberation_type: str,
    liberation_detail: Dict[str, Any]
) -> bool:
    """
    Determine if kamma should expire based on liberation event
    
    Args:
        kamma: Kamma entry dict
        liberation_type: Liberation type
        liberation_detail: Liberation details
        
    Returns:
        bool: True if should expire
        
    Buddhist Logic:
        - Sotāpanna: Expires kamma related to lower realms (apāya)
        - Sakadāgāmi: Expires certain sensual desire kamma
        - Anāgāmi: Expires all sensual realm kamma
        - Arahant: Expires all kamma (no more rebirth)
    """
    kamma_type = kamma.get("action_type", kamma.get("type", ""))
    kamma_details = kamma.get("details", {})
    
    # Simple logic (can be extended with Buddhist text references)
    if liberation_type == "arahant":
        # Arahant: All pending kamma expires (no more rebirth)
        return True
    
    elif liberation_type == "anāgāmi" or liberation_type == "anagami":
        # Anāgāmi: Sensual realm kamma expires
        if "sensual" in str(kamma_details).lower():
            return True
    
    elif liberation_type == "sakadāgāmi" or liberation_type == "sakadagami":
        # Sakadāgāmi: Certain coarse sensual kamma expires
        if "coarse_sensual" in str(kamma_details).lower():
            return True
    
    elif liberation_type == "sotāpanna" or liberation_type == "sotapanna":
        # Sotāpanna: Lower realm kamma expires (hell, hungry ghost, animal, asura)
        realm = kamma_details.get("realm", "").lower()
        lower_realms = ["hell", "hungry_ghost", "animal", "asura", "apāya", "lower_realm"]
        if any(lr in realm for lr in lower_realms):
            return True
        if "lower_realm" in str(kamma_details).lower() or "apāya" in str(kamma_details).lower():
            return True
    
    return False


# =====================================================================
# Analytics & Export
# =====================================================================

def get_kamma_summary(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get summary statistics for kamma ledger
    
    Args:
        profile: DigitalMindModel profile dict
        
    Returns:
        Summary dict with counts and totals
    """
    ledger = profile.get("CoreProfile", {}).get("SpiritualAssets", {}).get("KammaLedger", {})
    kamma_log = ledger.get("kamma_log", [])
    pending_kamma = ledger.get("dominant_pending_kamma", [])
    
    summary = {
        "total_kamma": len(kamma_log),
        "kusala_stock_points": ledger.get("kusala_stock_points", 0),
        "akusala_stock_points": ledger.get("akusala_stock_points", 0),
        "pending_count": len([k for k in kamma_log if k.get("status") == KammaStatus.PENDING]),
        "active_count": len([k for k in kamma_log if k.get("status") == KammaStatus.ACTIVE]),
        "finished_count": len([k for k in kamma_log if k.get("status") == KammaStatus.FINISHED]),
        "expired_count": len([k for k in kamma_log if k.get("status") == KammaStatus.EXPIRED]),
        "kusala_count": len([k for k in kamma_log if k.get("kusala")]),
        "akusala_count": len([k for k in kamma_log if not k.get("kusala")]),
    }
    
    return summary
