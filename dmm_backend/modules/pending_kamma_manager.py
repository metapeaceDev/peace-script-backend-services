"""
Pending Kamma Management System
=================================

Implements Buddhist pending kamma (กรรมค้าง) logic according to Peace Script Step 2.2.7.

Pending kamma represents actions (kusala/akusala) that have been recorded but are waiting
for specific conditions to manifest their results (vipaka).

Status transitions:
- pending: Waiting for conditions
- active: Conditions met, currently manifesting
- expired: Conditions no longer valid (e.g., due to liberation)
- finished: Vipaka completed

References:
- Peace Script Step 2.2.7: Pending Kamma Definition
- docs/modules/KAMMA_SYSTEM_COMPLETE_GUIDE.md: Section 7
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from beanie import PydanticObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from documents import DigitalMindModel
from core.logging_config import get_logger

logger = get_logger(__name__)


class PendingKammaManager:
    """
    Manages pending kamma lifecycle and condition checking.
    
    Core responsibilities:
    1. Retrieve pending kammas for a model
    2. Check if trigger conditions are met
    3. Update kamma status (pending → active → finished/expired)
    4. Prioritize pending kammas by strength/urgency
    """
    
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        """
        Initialize manager.
        
        Args:
            db: Optional database instance (will use Beanie's default if not provided)
        """
        self.db = db
        self.logger = logger
    
    async def get_pending_kammas(
        self, 
        model_id: str, 
        status: str = "pending"
    ) -> List[Dict[str, Any]]:
        """
        Get all pending kammas for a model.
        
        Args:
            model_id: The DigitalMindModel identifier
            status: Filter by status (default: "pending")
        
        Returns:
            List of kamma entries matching the status
        """
        try:
            dmm = await DigitalMindModel.find_one(
                DigitalMindModel.model_id == model_id
            )
            
            if not dmm:
                self.logger.warning(f"Model {model_id} not found")
                return []
            
            ledger = dmm.core_profile.spiritual_assets.kamma_ledger
            pending_kammas = ledger.dominant_pending_kamma or []
            
            # Filter by status if specified
            if status:
                pending_kammas = [
                    k for k in pending_kammas 
                    if k.get("status", "pending") == status
                ]
            
            self.logger.info(
                f"Retrieved {len(pending_kammas)} pending kammas for {model_id}"
            )
            return pending_kammas
        
        except Exception as e:
            self.logger.error(
                f"Error retrieving pending kammas for {model_id}: {e}"
            )
            return []
    
    async def trigger_vipaka(
        self, 
        model_id: str, 
        kamma_id: str
    ) -> Dict[str, Any]:
        """
        Manually trigger a pending kamma to active state.
        
        This simulates the conditions being met for a pending kamma
        to manifest its vipaka (result).
        
        Args:
            model_id: The DigitalMindModel identifier
            kamma_id: The specific kamma entry ID to trigger
        
        Returns:
            Updated kamma entry or error details
        """
        try:
            dmm = await DigitalMindModel.find_one(
                DigitalMindModel.model_id == model_id
            )
            
            if not dmm:
                return {
                    "success": False,
                    "error": f"Model {model_id} not found"
                }
            
            ledger = dmm.core_profile.spiritual_assets.kamma_ledger
            pending_kammas = ledger.dominant_pending_kamma or []
            
            # Find the kamma entry
            kamma_entry = None
            kamma_index = None
            
            for idx, k in enumerate(pending_kammas):
                if k.get("id") == kamma_id or k.get("_id") == kamma_id:
                    kamma_entry = k
                    kamma_index = idx
                    break
            
            if not kamma_entry:
                return {
                    "success": False,
                    "error": f"Kamma {kamma_id} not found in pending queue"
                }
            
            # Update status to active
            kamma_entry["status"] = "active"
            kamma_entry["manifested_at"] = datetime.utcnow().isoformat()
            kamma_entry["triggered_by"] = "manual_trigger"
            
            # Update the ledger
            pending_kammas[kamma_index] = kamma_entry
            ledger.dominant_pending_kamma = pending_kammas
            
            # Save to database
            await dmm.save()
            
            self.logger.info(
                f"Triggered vipaka for kamma {kamma_id} in model {model_id}"
            )
            
            return {
                "success": True,
                "kamma": kamma_entry,
                "message": "Vipaka triggered successfully"
            }
        
        except Exception as e:
            self.logger.error(
                f"Error triggering vipaka for {kamma_id}: {e}"
            )
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_status(
        self,
        model_id: str,
        kamma_id: str,
        new_status: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
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
            Updated kamma entry or error details
        """
        valid_statuses = ["pending", "active", "finished", "expired"]
        
        if new_status not in valid_statuses:
            return {
                "success": False,
                "error": f"Invalid status. Must be one of: {valid_statuses}"
            }
        
        try:
            dmm = await DigitalMindModel.find_one(
                DigitalMindModel.model_id == model_id
            )
            
            if not dmm:
                return {
                    "success": False,
                    "error": f"Model {model_id} not found"
                }
            
            ledger = dmm.core_profile.spiritual_assets.kamma_ledger
            pending_kammas = ledger.dominant_pending_kamma or []
            
            # Find and update the kamma entry
            updated = False
            for idx, k in enumerate(pending_kammas):
                if k.get("id") == kamma_id or k.get("_id") == kamma_id:
                    old_status = k.get("status", "pending")
                    k["status"] = new_status
                    k["updated_at"] = datetime.utcnow().isoformat()
                    
                    if reason:
                        k["status_change_reason"] = reason
                    
                    if new_status == "active" and old_status == "pending":
                        k["manifested_at"] = datetime.utcnow().isoformat()
                    elif new_status in ["finished", "expired"]:
                        k["completed_at"] = datetime.utcnow().isoformat()
                    
                    pending_kammas[idx] = k
                    updated = True
                    
                    self.logger.info(
                        f"Updated kamma {kamma_id} status: {old_status} → {new_status}"
                    )
                    break
            
            if not updated:
                return {
                    "success": False,
                    "error": f"Kamma {kamma_id} not found"
                }
            
            # Save to database
            ledger.dominant_pending_kamma = pending_kammas
            await dmm.save()
            
            return {
                "success": True,
                "kamma_id": kamma_id,
                "old_status": old_status,
                "new_status": new_status,
                "message": f"Status updated: {old_status} → {new_status}"
            }
        
        except Exception as e:
            self.logger.error(
                f"Error updating status for {kamma_id}: {e}"
            )
            return {
                "success": False,
                "error": str(e)
            }
    
    async def check_conditions(
        self,
        model_id: str,
        kamma_id: str
    ) -> Dict[str, Any]:
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
            dmm = await DigitalMindModel.find_one(
                DigitalMindModel.model_id == model_id
            )
            
            if not dmm:
                return {
                    "success": False,
                    "error": f"Model {model_id} not found"
                }
            
            ledger = dmm.core_profile.spiritual_assets.kamma_ledger
            pending_kammas = ledger.dominant_pending_kamma or []
            
            # Find the kamma entry
            kamma_entry = None
            for k in pending_kammas:
                if k.get("id") == kamma_id or k.get("_id") == kamma_id:
                    kamma_entry = k
                    break
            
            if not kamma_entry:
                return {
                    "success": False,
                    "error": f"Kamma {kamma_id} not found"
                }
            
            # Extract conditions
            conditions = kamma_entry.get("conditions", {})
            current_state = dmm.core_profile.model_dump()
            
            # Check each condition type
            results = {
                "kamma_id": kamma_id,
                "conditions_met": True,
                "checks": []
            }
            
            # Check bhumi (realm) requirement
            if "required_bhumi" in conditions:
                required_bhumi = conditions["required_bhumi"]
                current_bhumi = current_state.get("character_card", {}).get(
                    "current_bhumi", "unknown"
                )
                bhumi_met = current_bhumi == required_bhumi
                results["checks"].append({
                    "type": "bhumi",
                    "required": required_bhumi,
                    "current": current_bhumi,
                    "met": bhumi_met
                })
                if not bhumi_met:
                    results["conditions_met"] = False
            
            # Check cetasika (mental factors) requirement
            if "required_cetasikas" in conditions:
                required = set(conditions["required_cetasikas"])
                current = set(
                    current_state.get("spiritual_assets", {})
                    .get("dominant_cetasikas", [])
                )
                cetasika_met = required.issubset(current)
                results["checks"].append({
                    "type": "cetasika",
                    "required": list(required),
                    "current": list(current),
                    "met": cetasika_met
                })
                if not cetasika_met:
                    results["conditions_met"] = False
            
            # Check time elapsed
            if "min_time_elapsed" in conditions:
                created_at = datetime.fromisoformat(
                    kamma_entry.get("created_at", datetime.utcnow().isoformat())
                )
                elapsed = (datetime.utcnow() - created_at).total_seconds()
                min_time = conditions["min_time_elapsed"]
                time_met = elapsed >= min_time
                results["checks"].append({
                    "type": "time_elapsed",
                    "required_seconds": min_time,
                    "elapsed_seconds": elapsed,
                    "met": time_met
                })
                if not time_met:
                    results["conditions_met"] = False
            
            self.logger.info(
                f"Condition check for {kamma_id}: "
                f"{'✓ MET' if results['conditions_met'] else '✗ NOT MET'}"
            )
            
            return {
                "success": True,
                **results
            }
        
        except Exception as e:
            self.logger.error(
                f"Error checking conditions for {kamma_id}: {e}"
            )
            return {
                "success": False,
                "error": str(e)
            }
    
    async def prioritize_pending(
        self,
        model_id: str
    ) -> List[Dict[str, Any]]:
        """
        Prioritize pending kammas by strength, age, and type.
        
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
            pending = await self.get_pending_kammas(model_id, status="pending")
            
            if not pending:
                return []
            
            # Calculate priority score for each kamma
            now = datetime.utcnow()
            
            for k in pending:
                score = 0.0
                
                # Factor 1: Intensity (0-100 points)
                intensity = k.get("intensity", 0.5)
                score += intensity * 100
                
                # Factor 2: Age (0-50 points, max at 30 days)
                created_at = datetime.fromisoformat(
                    k.get("created_at", now.isoformat())
                )
                age_days = (now - created_at).days
                age_score = min(age_days / 30.0, 1.0) * 50
                score += age_score
                
                # Factor 3: Type bonus (kusala slightly prioritized)
                if k.get("kusala", False):
                    score += 10
                
                k["priority_score"] = score
            
            # Sort by priority score (descending)
            prioritized = sorted(
                pending,
                key=lambda x: x.get("priority_score", 0),
                reverse=True
            )
            
            self.logger.info(
                f"Prioritized {len(prioritized)} pending kammas for {model_id}"
            )
            
            return prioritized
        
        except Exception as e:
            self.logger.error(
                f"Error prioritizing pending kammas: {e}"
            )
            return []
