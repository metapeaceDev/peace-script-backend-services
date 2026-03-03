"""
🔗 Rupa Jivitindriya Sync Layer - ชั้นซิงค์ชีวิตินทรีย์

Purpose: Synchronize Jivitindriya between two systems
- CoreProfile.life_essence.jivitindriya_mechanics (LifeEssence)
- RupaProfile.jivita_state.rupa_jivitindriya (28 Material Forms)

Usage:
    # Sync LifeEssence → RupaProfile (after updating life_force)
    await RupaJivitindriaSyncLayer.sync_life_essence_to_rupa(model_id)
    
    # Sync RupaProfile → LifeEssence (after calculating rupa)
    await RupaJivitindriaSyncLayer.sync_rupa_to_life_essence(model_id)
    
    # Bidirectional sync (both ways)
    await RupaJivitindriaSyncLayer.sync_bidirectional(model_id)

Author: Peace Mind System
Date: 17 October 2568
"""

from typing import Optional
from datetime import datetime

from documents import DigitalMindModel
from rupa_models import RupaProfile


class RupaJivitindriaSyncLayer:
    """
    Synchronizes Jivitindriya (Life Faculty) between:
    1. CoreProfile.life_essence.jivitindriya_mechanics.current_jivitindriya
    2. RupaProfile.jivita_state.rupa_jivitindriya
    
    Buddhist Principle:
    - ชีวิตินทรีย์ (Jivitindriya) is THE life faculty that maintains existence
    - In Nama-Rupa system: Nama depends on Rupa (life faculty)
    - Must be synchronized to maintain consistency
    """
    
    @staticmethod
    async def sync_life_essence_to_rupa(model_id: str) -> bool:
        """
        Sync: LifeEssence → RupaProfile
        
        Use case:
        - User updates life_force via PATCH /nama-rupa/rupa
        - Aging simulation depletes jivitindriya
        - Training/meditation regenerates life force
        
        Args:
            model_id: DigitalMindModel ID
        
        Returns:
            True if synced successfully, False if model/rupa not found
        """
        # Get model (use find_one because model_id is string, not ObjectId)
        model = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
        if not model:
            return False
        
        # Get or create RupaProfile
        rupa = await RupaProfile.find_one(RupaProfile.model_id == model_id)
        if not rupa:
            # RupaProfile doesn't exist yet - will be created later
            return False
        
        # Extract jivitindriya from LifeEssence
        try:
            profile = model.get_core_profile()
            jiv_mechanics = profile.life_essence.jivitindriya_mechanics
            current_jiv = jiv_mechanics.current_jivitindriya
        except (AttributeError, Exception):
            # LifeEssence doesn't have jivitindriya_mechanics
            return False
        
        # Update RupaProfile
        rupa.jivita_state.rupa_jivitindriya = current_jiv
        rupa.last_updated = datetime.utcnow()
        await rupa.save()
        
        return True
    
    @staticmethod
    async def sync_rupa_to_life_essence(model_id: str) -> bool:
        """
        Sync: RupaProfile → LifeEssence
        
        Use case:
        - Rupa calculation engine updates jivitindriya
        - Manual rupa update via new /rupa endpoints
        - Migration script creates new RupaProfile
        
        Args:
            model_id: DigitalMindModel ID
        
        Returns:
            True if synced successfully, False if model/rupa not found
        """
        # Get RupaProfile
        rupa = await RupaProfile.find_one(RupaProfile.model_id == model_id)
        if not rupa:
            return False
        
        # Get model (use find_one because model_id is string, not ObjectId)
        model = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
        if not model:
            return False
        
        # Extract jivitindriya from RupaProfile
        rupa_jiv = rupa.jivita_state.rupa_jivitindriya
        
        # Update LifeEssence
        try:
            profile = model.get_core_profile()
            profile.life_essence.jivitindriya_mechanics.current_jivitindriya = rupa_jiv
            # Update model's core_profile
            model.update_core_profile({"life_essence": profile.life_essence})
            await model.save()
        except (AttributeError, Exception):
            # LifeEssence doesn't have jivitindriya_mechanics
            return False
        
        return True
    
    @staticmethod
    async def sync_bidirectional(
        model_id: str,
        source: str = "life_essence"
    ) -> bool:
        """
        Bidirectional sync (both ways)
        
        Args:
            model_id: DigitalMindModel ID
            source: Which system is the source of truth
                   - "life_essence": Sync LifeEssence → RupaProfile
                   - "rupa": Sync RupaProfile → LifeEssence
        
        Returns:
            True if synced successfully
        """
        if source == "life_essence":
            return await RupaJivitindriaSyncLayer.sync_life_essence_to_rupa(model_id)
        elif source == "rupa":
            return await RupaJivitindriaSyncLayer.sync_rupa_to_life_essence(model_id)
        else:
            raise ValueError(f"Invalid source: {source}. Must be 'life_essence' or 'rupa'")
    
    @staticmethod
    async def validate_sync(model_id: str) -> tuple[bool, float, float]:
        """
        Validate that both systems have same jivitindriya value
        
        Args:
            model_id: DigitalMindModel ID
        
        Returns:
            (is_synced: bool, life_essence_value: float, rupa_value: float)
        """
        # Get model (use find_one because model_id is string, not ObjectId)
        model = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
        if not model:
            return (False, 0.0, 0.0)
        
        # Get RupaProfile
        rupa = await RupaProfile.find_one(RupaProfile.model_id == model_id)
        if not rupa:
            return (False, 0.0, 0.0)
        
        # Extract values
        try:
            profile = model.get_core_profile()
            life_essence_jiv = profile.life_essence.jivitindriya_mechanics.current_jivitindriya
        except (AttributeError, Exception):
            life_essence_jiv = 0.0
        
        rupa_jiv = rupa.jivita_state.rupa_jivitindriya
        
        # Check if synced (allow 0.1% tolerance)
        is_synced = abs(life_essence_jiv - rupa_jiv) < 0.1
        
        return (is_synced, life_essence_jiv, rupa_jiv)
    
    @staticmethod
    async def auto_sync_on_update(
        model_id: str,
        updated_system: str,
        new_value: float
    ) -> bool:
        """
        Automatically sync after an update
        
        Args:
            model_id: DigitalMindModel ID
            updated_system: Which system was updated ("life_essence" or "rupa")
            new_value: New jivitindriya value
        
        Returns:
            True if synced successfully
        """
        if updated_system == "life_essence":
            # Update LifeEssence first, then sync to Rupa
            model = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
            if not model:
                return False
            
            profile = model.get_core_profile()
            profile.life_essence.jivitindriya_mechanics.current_jivitindriya = new_value
            model.update_core_profile({"life_essence": profile.life_essence})
            await model.save()
            
            # Sync to Rupa
            return await RupaJivitindriaSyncLayer.sync_life_essence_to_rupa(model_id)
        
        elif updated_system == "rupa":
            # Update Rupa first, then sync to LifeEssence
            rupa = await RupaProfile.find_one(RupaProfile.model_id == model_id)
            if not rupa:
                return False
            
            rupa.jivita_state.rupa_jivitindriya = new_value
            await rupa.save()
            
            # Sync to LifeEssence
            return await RupaJivitindriaSyncLayer.sync_rupa_to_life_essence(model_id)
        
        else:
            raise ValueError(f"Invalid updated_system: {updated_system}")


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

async def ensure_jivitindriya_synced(model_id: str) -> bool:
    """
    Ensure jivitindriya is synced between LifeEssence and RupaProfile
    Uses LifeEssence as source of truth
    
    Args:
        model_id: DigitalMindModel ID
    
    Returns:
        True if synced successfully
    """
    is_synced, life_val, rupa_val = await RupaJivitindriaSyncLayer.validate_sync(model_id)
    
    if is_synced:
        return True
    
    # Not synced - sync from LifeEssence to Rupa
    return await RupaJivitindriaSyncLayer.sync_life_essence_to_rupa(model_id)


async def get_jivitindriya_status(model_id: str) -> dict:
    """
    Get jivitindriya status from both systems
    
    Returns:
        {
            "model_id": str,
            "is_synced": bool,
            "life_essence_value": float,
            "rupa_value": float,
            "difference": float,
            "source_of_truth": str
        }
    """
    is_synced, life_val, rupa_val = await RupaJivitindriaSyncLayer.validate_sync(model_id)
    
    return {
        "model_id": model_id,
        "is_synced": is_synced,
        "life_essence_value": life_val,
        "rupa_value": rupa_val,
        "difference": abs(life_val - rupa_val),
        "source_of_truth": "life_essence"  # LifeEssence is canonical
    }
