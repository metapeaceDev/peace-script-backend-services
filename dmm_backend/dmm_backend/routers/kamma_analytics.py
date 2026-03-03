"""
Peace Script V.14 - Kamma Analytics Router
===========================================
API endpoints for Kamma Ledger analytics, dashboard, and visualizations
Based on planning documents Step 2.2.6, 2.2.9, 2.2.10, 2.2.11, 2.2.12

Endpoints:
- GET /summary              - Pie chart data (kusala/akusala/pending)
- GET /sankey               - Sankey diagram data (parent-child flow)
- GET /timeline             - Timeline data (events by time)
- GET /by_status                i        core_profile = profile.get_core_profile()
        # Use snake_case field names (from core_profile_models.py)
        ledger = core_profile.spiritual_assets.kamma_ledger
        kamma_log = get_kamma_log_from_profile(profile)
        
        # Get pending kamma
        pending_kamma = [entry.model_dump() if hasattr(entry, 'model_dump') else entry 
                        for entry in ledger.dominant_pending_kamma]rofile:
            raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")
        
        core_profile = profile.get_core_profile()
        # Use snake_case field names (from core_profile_models.py)
        ledger = core_profile.spiritual_assets.kamma_ledger
        kamma_log = get_kamma_log_from_profile(profile)Split by status (pending/active/finished/expired)
- GET /detail               - Detail with chain trace
- GET /filter               - Filter and search kamma
- GET /export               - Export kamma data (CSV/JSON)
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends

from core.logging_config import get_logger
from documents import DigitalMindModel
from modules.kamma_engine import (
    KammaStatus,
    get_kamma_summary,
    trace_kamma
)

logger = get_logger(__name__)

router = APIRouter(prefix="/api/kamma", tags=["Kamma Analytics"])


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_kamma_log_from_profile(profile: DigitalMindModel) -> List[Dict[str, Any]]:
    """
    Safely extract kamma_log from profile using dict access.
    
    This function works with the raw dict structure in MongoDB:
    core_profile -> CoreProfile -> SpiritualAssets -> KammaLedger -> kamma_log
    
    Returns:
        List of kamma entries as dicts
    """
    try:
        # Access as dict (more reliable than object conversion)
        if hasattr(profile, "core_profile") and profile.core_profile:
            core_dict = profile.core_profile
            if isinstance(core_dict, dict):
                spiritual = core_dict.get("SpiritualAssets", {})
                ledger = spiritual.get("KammaLedger", {})
                kamma_log = ledger.get("kamma_log", [])
                return kamma_log if isinstance(kamma_log, list) else []
        
        logger.warning(f"No core_profile found for profile {profile.model_id}")
        return []
    except Exception as e:
        logger.warning(f"Failed to get kamma_log from profile: {e}")
        return []


# ============================================================================
# API ENDPOINTS
# ============================================================================



# =====================================================================
# Analytics Endpoints
# =====================================================================

@router.get("/summary")
async def get_kamma_summary_endpoint(model_id: str = Query(..., description="Model ID")):
    """
    Get kamma summary for pie chart and gauge display
    
    Returns:
        - kusala_stock_points: Total kusala (good kamma) points
        - akusala_stock_points: Total akusala (bad kamma) points
        - pending_count: Number of pending kamma
        - active_count: Number of active kamma
        - finished_count: Number of finished kamma
        - expired_count: Number of expired kamma
        - kusala_count: Count of kusala actions
        - akusala_count: Count of akusala actions
    """
    try:
        # Fetch profile from database
        profile = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
        if not profile:
            raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")
        
        # Get core profile dict directly
        core_dict = profile.core_profile if hasattr(profile, "core_profile") and profile.core_profile else {}
        spiritual = core_dict.get("SpiritualAssets", {}) if isinstance(core_dict, dict) else {}
        ledger = spiritual.get("KammaLedger", {}) if isinstance(spiritual, dict) else {}
        
        kamma_log = get_kamma_log_from_profile(profile)
        
        # Calculate summary statistics
        kusala_count = sum(1 for k in kamma_log if k.get("is_kusala", False))
        akusala_count = len(kamma_log) - kusala_count
        pending_count = sum(1 for k in kamma_log if k.get("status") == "pending")
        active_count = sum(1 for k in kamma_log if k.get("status") == "active")
        finished_count = sum(1 for k in kamma_log if k.get("status") == "finished")
        expired_count = sum(1 for k in kamma_log if k.get("status") == "expired")
        
        summary = {
            "kusala_stock_points": ledger.get("kusala_stock_points", 0),
            "akusala_stock_points": ledger.get("akusala_stock_points", 0),
            "total_kamma": len(kamma_log),
            "kusala_count": kusala_count,
            "akusala_count": akusala_count,
            "pending_count": pending_count,
            "active_count": active_count,
            "finished_count": finished_count,
            "expired_count": expired_count,
            "pie": {
                "kusala": kusala_count,
                "akusala": akusala_count,
                "pending": pending_count
            }
        }
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting kamma summary: {repr(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get kamma summary: {str(e)}")


@router.get("/{model_id}/balance")
async def get_kamma_balance(model_id: str):
    """
    Get kamma balance for a specific model.
    
    Returns kusala/akusala balance, total kamma, and karma ratio.
    
    Args:
        model_id: Digital Mind Model ID
        
    Returns:
        - kusala_balance: Total kusala (good) stock points
        - akusala_balance: Total akusala (bad) stock points
        - total_kamma: Total number of kamma entries
        - karma_ratio: Kusala to Akusala ratio
        - net_balance: Kusala minus Akusala points
        
    Example:
        GET /api/kamma/peace-mind-001/balance
        
        Response:
        {
            "model_id": "peace-mind-001",
            "kusala_balance": 500,
            "akusala_balance": 1200,
            "total_kamma": 0,
            "karma_ratio": 0.42,
            "net_balance": -700
        }
    """
    try:
        # Fetch profile from database
        profile = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
        if not profile:
            raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")
        
        # Get core profile dict directly
        core_dict = profile.core_profile if hasattr(profile, "core_profile") and profile.core_profile else {}
        spiritual = core_dict.get("SpiritualAssets", {}) if isinstance(core_dict, dict) else {}
        ledger = spiritual.get("KammaLedger", {}) if isinstance(spiritual, dict) else {}
        
        # Extract balance data
        kusala_balance = ledger.get("kusala_stock_points", 0)
        akusala_balance = ledger.get("akusala_stock_points", 0)
        
        # Get kamma log for total count
        kamma_log = get_kamma_log_from_profile(profile)
        total_kamma = len(kamma_log)
        
        # Calculate ratio (avoid division by zero)
        if akusala_balance > 0:
            karma_ratio = round(kusala_balance / akusala_balance, 2)
        else:
            karma_ratio = float('inf') if kusala_balance > 0 else 0.0
        
        # Calculate net balance
        net_balance = kusala_balance - akusala_balance
        
        return {
            "model_id": model_id,
            "kusala_balance": kusala_balance,
            "akusala_balance": akusala_balance,
            "total_kamma": total_kamma,
            "karma_ratio": karma_ratio,
            "net_balance": net_balance,
            "status": "wholesome" if net_balance > 0 else "unwholesome" if net_balance < 0 else "neutral"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting kamma balance for {model_id}: {repr(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get kamma balance: {str(e)}")


@router.get("/sankey")
async def get_kamma_sankey_endpoint(model_id: str = Query(..., description="Model ID")):
    """
    Get Sankey diagram data (nodes + links for kamma flow visualization)
    
    Returns:
        - nodes: List of node objects {id, name, type}
        - links: List of link objects {source, target, value}
    """
    try:
        profile = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
        if not profile:
            raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")
        
        kamma_log = get_kamma_log_from_profile(profile)
        
        nodes = []
        links = []
        node_map = {}
        
        # Create nodes for each kamma
        for i, log in enumerate(kamma_log):
            kamma_id = log["kamma_id"]
            node = {
                "id": kamma_id,
                "name": f'{log.get("action_type", "action")}#{i}',
                "type": "kusala" if log.get("kusala") else "akusala",
                "status": log.get("status", "finished"),
                "intensity": log.get("intensity", 1.0)
            }
            node_map[kamma_id] = node
            nodes.append(node)
        
        # Create links from parent-child relationships
        for log in kamma_log:
            kamma_id = log["kamma_id"]
            for child_id in log.get("trace_children", []):
                if child_id in node_map:
                    links.append({
                        "source": kamma_id,
                        "target": child_id,
                        "value": 1  # Can be weighted by intensity
                    })
        
        return {
            "nodes": nodes,
            "links": links
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sankey data: {repr(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get sankey data: {str(e)}")


@router.get("/timeline")
async def get_kamma_timeline_endpoint(
    model_id: str = Query(..., description="Model ID"),
    limit: Optional[int] = Query(None, description="Limit results"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)")
):
    """
    Get kamma timeline (events sorted by time)
    
    Returns:
        - timeline: List of kamma events with timestamp, type, details
    """
    try:
        profile = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
        if not profile:
            raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")
        
        kamma_log = get_kamma_log_from_profile(profile)
        
        # Sort by timestamp
        reverse = (sort_order.lower() == "desc")
        timeline = sorted(kamma_log, key=lambda l: l.get("timestamp", ""), reverse=reverse)
        
        # Apply limit if provided
        if limit:
            timeline = timeline[:limit]
        
        # Format for frontend
        formatted_timeline = []
        for log in timeline:
            formatted_timeline.append({
                "kamma_id": log["kamma_id"],
                "timestamp": log.get("timestamp"),
                "type": log.get("action_type"),
                "kusala": log.get("kusala"),
                "status": log.get("status"),
                "intensity": log.get("intensity", 1.0),
                "details": log.get("details", {}),
                "condition": log.get("condition"),
                "parent": log.get("trace_parent"),
                "children_count": len(log.get("trace_children", []))
            })
        
        return {
            "timeline": formatted_timeline,
            "total": len(kamma_log)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting timeline: {repr(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get timeline: {str(e)}")


@router.get("/by_status")
async def get_kamma_by_status_endpoint(model_id: str = Query(..., description="Model ID")):
    """
    Get kamma split by status for tabs/cards display
    
    Returns:
        - pending: List of pending kamma
        - active: List of active kamma
        - finished: List of finished kamma
        - expired: List of expired kamma
    """
    try:
        profile = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
        if not profile:
            raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")
        
        # Get all kamma and filter by status
        kamma_log = get_kamma_log_from_profile(profile)
        
        result = {
            "pending": [],
            "active": [],
            "finished": [],
            "expired": []
        }
        
        for kamma in kamma_log:
            status = kamma.get("status", KammaStatus.PENDING)
            if status == KammaStatus.PENDING:
                result["pending"].append(kamma)
            elif status == KammaStatus.ACTIVE:
                result["active"].append(kamma)
            elif status == KammaStatus.FINISHED:
                result["finished"].append(kamma)
            elif status == KammaStatus.EXPIRED:
                result["expired"].append(kamma)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting kamma by status: {repr(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get kamma by status: {str(e)}")


@router.get("/detail")
async def get_kamma_detail_endpoint(
    model_id: str = Query(..., description="Model ID"),
    kamma_id: str = Query(..., description="Kamma ID to get details")
):
    """
    Get detailed kamma information with full chain trace
    
    Returns:
        - kamma: Full kamma log entry
        - parent: Parent kamma (if exists)
        - children: List of child kamma
        - chain_length: Total chain depth
        - age_days: Age in days since creation
    """
    try:
        profile = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
        if not profile:
            raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")
        
        kamma_log = get_kamma_log_from_profile(profile)
        
        # Find the specific kamma
        target_kamma = next((k for k in kamma_log if k["kamma_id"] == kamma_id), None)
        if not target_kamma:
            raise HTTPException(status_code=404, detail=f"Kamma not found: {kamma_id}")
        
        # Build trace (parent and children)
        parent = None
        children = []
        
        if target_kamma.get("trace_parent"):
            parent = next((k for k in kamma_log if k["kamma_id"] == target_kamma["trace_parent"]), None)
        
        for k in kamma_log:
            if k.get("trace_parent") == kamma_id:
                children.append(k)
        
        # Calculate additional context
        age_days = None
        if target_kamma.get("timestamp"):
            try:
                created = datetime.fromisoformat(target_kamma["timestamp"].replace('Z', ''))
                age_days = (datetime.utcnow() - created).days
            except:
                pass
        
        # Count chain length (recursively)
        def count_chain_depth(kamma_dict, visited=None):
            if visited is None:
                visited = set()
            if kamma_dict["kamma_id"] in visited:
                return 0
            visited.add(kamma_dict["kamma_id"])
            
            max_depth = 0
            if children:
                for child in children:
                    max_depth = max(max_depth, count_chain_depth(child, visited))
            return max_depth + 1
        
        chain_length = count_chain_depth(target_kamma)
        
        return {
            **target_kamma,
            "parent": parent,
            "children": children,
            "chain_length": chain_length,
            "age_days": age_days,
            "context": {
                "type": target_kamma.get("action_type"),
                "status": target_kamma.get("status"),
                "intensity": target_kamma.get("intensity", 1.0),
                "condition": target_kamma.get("condition"),
                "kusala": target_kamma.get("kusala")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting kamma detail: {repr(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get kamma detail: {str(e)}")


@router.get("/filter")
async def filter_kamma_endpoint(
    model_id: str = Query(..., description="Model ID"),
    type: Optional[str] = Query(None, description="Filter by action type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    kusala: Optional[bool] = Query(None, description="Filter by kusala (true/false)"),
    intensity_min: Optional[float] = Query(None, description="Min intensity"),
    intensity_max: Optional[float] = Query(None, description="Max intensity"),
    date_from: Optional[str] = Query(None, description="Date from (ISO format)"),
    date_to: Optional[str] = Query(None, description="Date to (ISO format)"),
    limit: Optional[int] = Query(100, description="Max results")
):
    """
    Filter and search kamma with multiple criteria
    
    Returns:
        - results: Filtered kamma list
        - total: Total matching count
        - filters_applied: Summary of filters used
    """
    try:
        profile = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
        if not profile:
            raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")
        
        kamma_log = get_kamma_log_from_profile(profile)
        
        # Apply filters
        results = []
        for log in kamma_log:
            # Type filter (check 'origin' field, not 'action_type')
            if type and log.get("origin") != type:
                continue
            
            # Status filter
            if status and log.get("status") != status:
                continue
            
            # Kusala filter
            if kusala is not None and log.get("is_kusala") != kusala:
                continue
            
            # Intensity filter
            log_intensity = log.get("intensity", 0)
            if intensity_min is not None and log_intensity < intensity_min:
                continue
            if intensity_max is not None and log_intensity > intensity_max:
                continue
            
            # Date filter
            log_timestamp = log.get("timestamp")
            if date_from and log_timestamp < date_from:
                continue
            if date_to and log_timestamp > date_to:
                continue
            
            results.append(log)
        
        # Apply limit
        total = len(results)
        if limit:
            results = results[:limit]
        
        return {
            "results": results,
            "total": total,
            "returned": len(results),
            "filters_applied": {
                "type": type,
                "status": status,
                "kusala": kusala,
                "intensity_min": intensity_min,
                "intensity_max": intensity_max,
                "date_from": date_from,
                "date_to": date_to
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error filtering kamma: {repr(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to filter kamma: {str(e)}")


@router.get("/export")
async def export_kamma_endpoint(
    model_id: str = Query(..., description="Model ID"),
    format: str = Query("json", description="Export format (json/csv)"),
    include_chains: bool = Query(False, description="Include full chain data")
):
    """
    Export kamma data for analysis/backup
    
    Returns:
        - data: Exported kamma data in requested format
        - metadata: Export metadata (timestamp, format, count)
    """
    try:
        profile = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
        if not profile:
            raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")
        
        # Get core profile dict
        core_dict = profile.core_profile if hasattr(profile, "core_profile") and profile.core_profile else {}
        spiritual = core_dict.get("SpiritualAssets", {}) if isinstance(core_dict, dict) else {}
        ledger = spiritual.get("KammaLedger", {}) if isinstance(spiritual, dict) else {}
        
        kamma_log = get_kamma_log_from_profile(profile)
        
        # Get pending kamma from dict
        pending_kamma = ledger.get("dominant_pending_kamma", []) if isinstance(ledger, dict) else []
        
        # Calculate summary inline
        summary = {
            "total_kamma": len(kamma_log),
            "by_status": {},
            "by_type": {},
            "by_valence": {}
        }
        for entry in kamma_log:
            status = entry.get("status", "unknown")
            k_type = entry.get("type", "unknown")
            valence = entry.get("valence", 0)
            
            summary["by_status"][status] = summary["by_status"].get(status, 0) + 1
            summary["by_type"][k_type] = summary["by_type"].get(k_type, 0) + 1
            if valence > 0:
                summary["by_valence"]["positive"] = summary["by_valence"].get("positive", 0) + 1
            elif valence < 0:
                summary["by_valence"]["negative"] = summary["by_valence"].get("negative", 0) + 1
            else:
                summary["by_valence"]["neutral"] = summary["by_valence"].get("neutral", 0) + 1
        
        export_data = {
            "model_id": model_id,
            "export_timestamp": datetime.utcnow().isoformat(),
            "summary": summary,
            "kamma_log": kamma_log,
            "pending_kamma": pending_kamma
        }
        
        if include_chains:
            # Build chain traces manually for all kamma
            chains = []
            for log_entry in kamma_log:
                kamma_id = log_entry["kamma_id"]
                
                # Find parent
                parent = None
                if log_entry.get("trace_parent"):
                    parent = next((k for k in kamma_log if k["kamma_id"] == log_entry["trace_parent"]), None)
                
                # Find children
                children = [k for k in kamma_log if k.get("trace_parent") == kamma_id]
                
                chain = {
                    "root": log_entry,
                    "parent": parent,
                    "children": children,
                    "depth": 0  # Could calculate recursively if needed
                }
                chains.append(chain)
            export_data["chains"] = chains
        
        metadata = {
            "format": format,
            "total_kamma": len(kamma_log),
            "total_pending": len(pending_kamma),
            "include_chains": include_chains,
            "export_timestamp": datetime.utcnow().isoformat()
        }
        
        if format == "csv":
            # For CSV, return flattened data (frontend will need to parse)
            # In production, use pandas or csv module for proper CSV formatting
            return {
                "data": "CSV export not fully implemented (use json for now)",
                "metadata": metadata,
                "note": "CSV export requires additional processing"
            }
        
        return {
            "data": export_data,
            "metadata": metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting kamma: {repr(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to export kamma: {str(e)}")


# =====================================================================
# Pending Kamma Management Endpoints (NEW - Priority 1)
# =====================================================================

@router.get("/{model_id}/pending")
async def get_pending_kammas(
    model_id: str,
    status: str = Query("pending", description="Filter by status")
):
    """
    Get all pending kammas for a model.
    
    Pending kammas are actions waiting for specific conditions to manifest
    their vipaka (results).
    
    Args:
        model_id: The DigitalMindModel identifier
        status: Filter by status (pending/active/finished/expired)
    
    Returns:
        List of pending kamma entries with conditions and metadata
    """
    try:
        from modules.pending_kamma_manager import PendingKammaManager
        
        manager = PendingKammaManager()
        pending = await manager.get_pending_kammas(model_id, status=status)
        
        return {
            "model_id": model_id,
            "status_filter": status,
            "count": len(pending),
            "pending_kammas": pending
        }
    
    except Exception as e:
        logger.error(f"Error fetching pending kammas: {repr(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to fetch pending kammas: {str(e)}"
        )


@router.post("/{model_id}/trigger_vipaka")
async def trigger_pending_vipaka(
    model_id: str,
    kamma_id: str = Query(..., description="Kamma entry ID to trigger")
):
    """
    Manually trigger a pending kamma to active state.
    
    This simulates the conditions being met for a pending kamma
    to manifest its vipaka (result).
    
    Args:
        model_id: The DigitalMindModel identifier
        kamma_id: The specific kamma entry ID to trigger
    
    Returns:
        Updated kamma entry with new status
    """
    try:
        from modules.pending_kamma_manager import PendingKammaManager
        
        manager = PendingKammaManager()
        result = await manager.trigger_vipaka(model_id, kamma_id)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=404,
                detail=result.get("error", "Failed to trigger vipaka")
            )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering vipaka: {repr(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger vipaka: {str(e)}"
        )


@router.put("/{model_id}/update_status")
async def update_kamma_status(
    model_id: str,
    kamma_id: str = Query(..., description="Kamma entry ID"),
    new_status: str = Query(..., description="New status (active/finished/expired)"),
    reason: Optional[str] = Query(None, description="Reason for status change")
):
    """
    Update the status of a pending kamma.
    
    Valid transitions:
    - pending → active (conditions met)
    - active → finished (vipaka completed)
    - active → expired (conditions changed, e.g., liberation)
    - pending → expired (conditions no longer possible)
    
    Args:
        model_id: The DigitalMindModel identifier
        kamma_id: The specific kamma entry ID
        new_status: New status (active/finished/expired)
        reason: Optional reason for status change
    
    Returns:
        Updated status confirmation
    """
    try:
        from modules.pending_kamma_manager import PendingKammaManager
        
        manager = PendingKammaManager()
        result = await manager.update_status(
            model_id, kamma_id, new_status, reason
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to update status")
            )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating kamma status: {repr(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update status: {str(e)}"
        )


@router.get("/{model_id}/conditions/{kamma_id}")
async def check_kamma_conditions(
    model_id: str,
    kamma_id: str
):
    """
    Check if trigger conditions are met for a pending kamma.
    
    Conditions can include:
    - Specific bhumi (realm) requirements
    - Cetasika (mental factors) presence
    - Citta (consciousness) states
    - Jhana levels
    - Time elapsed since creation
    
    Args:
        model_id: The DigitalMindModel identifier
        kamma_id: The specific kamma entry ID
    
    Returns:
        Condition check results with boolean met status
    """
    try:
        from modules.pending_kamma_manager import PendingKammaManager
        
        manager = PendingKammaManager()
        result = await manager.check_conditions(model_id, kamma_id)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=404,
                detail=result.get("error", "Failed to check conditions")
            )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking conditions: {repr(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check conditions: {str(e)}"
        )


@router.get("/{model_id}/prioritize")
async def prioritize_pending_kammas(model_id: str):
    """
    Get pending kammas sorted by priority.
    
    Prioritization factors:
    1. Intensity/strength (higher = more urgent)
    2. Age (older pending kammas take precedence)
    3. Type (kusala vs akusala balance)
    
    Args:
        model_id: The DigitalMindModel identifier
    
    Returns:
        List of pending kammas sorted by priority (highest first)
    """
    try:
        from modules.pending_kamma_manager import PendingKammaManager
        
        manager = PendingKammaManager()
        prioritized = await manager.prioritize_pending(model_id)
        
        return {
            "model_id": model_id,
            "count": len(prioritized),
            "pending_kammas": prioritized,
            "note": "Sorted by priority_score (descending)"
        }
    
    except Exception as e:
        logger.error(f"Error prioritizing pending kammas: {repr(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to prioritize: {str(e)}"
        )
