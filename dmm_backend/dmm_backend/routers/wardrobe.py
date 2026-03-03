"""
Wardrobe System API Router
เสื้อผ้า เครื่องแต่งกาย และเครื่องประดับสำหรับตัวละคร
STEP 3.5 Enhancement - Character Wardrobe & Styling

API Endpoints:
- GET/POST /api/wardrobe/{character_id}/clothing
- GET/PUT/DELETE /api/wardrobe/{character_id}/clothing/{item_id}
- GET/POST /api/wardrobe/{character_id}/accessories
- GET/PUT/DELETE /api/wardrobe/{character_id}/accessories/{accessory_id}
- GET/POST /api/wardrobe/{character_id}/outfits
- GET/PUT/DELETE /api/wardrobe/{character_id}/outfits/{outfit_id}
- POST /api/wardrobe/{character_id}/outfits/{outfit_id}/wear
- GET /api/wardrobe/{character_id}
- GET /api/wardrobe/{character_id}/stats
- GET /api/wardrobe/{character_id}/current-outfit
"""

from datetime import datetime
from typing import List, Optional, Dict
from fastapi import APIRouter, HTTPException, Query, Path, Body
from pydantic import BaseModel, Field

from models.wardrobe import (
    ClothingItem,
    Accessory,
    Outfit,
    Wardrobe,
    WardrobeStats,
    ClothingCategory,
    ClothingStyle,
    Season,
    Occasion
)
from core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/wardrobe", tags=["Wardrobe"])


# =============================================================================
# REQUEST/RESPONSE SCHEMAS
# =============================================================================

class ClothingItemCreate(BaseModel):
    """Schema for creating a new clothing item"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: ClothingCategory
    type: str
    style: ClothingStyle = ClothingStyle.CASUAL
    color: str
    secondary_colors: List[str] = []
    material: str
    pattern: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[float] = None
    currency: str = "THB"
    size: Optional[str] = None
    fit: Optional[str] = None
    season: List[Season] = []
    occasions: List[Occasion] = []
    tags: List[str] = []
    notes: Optional[str] = None
    image_url: Optional[str] = None
    is_favorite: bool = False
    favorite_score: float = 5.0


class ClothingItemUpdate(BaseModel):
    """Schema for updating a clothing item"""
    name: Optional[str] = None
    description: Optional[str] = None
    style: Optional[ClothingStyle] = None
    color: Optional[str] = None
    secondary_colors: Optional[List[str]] = None
    brand: Optional[str] = None
    price: Optional[float] = None
    size: Optional[str] = None
    fit: Optional[str] = None
    season: Optional[List[Season]] = None
    occasions: Optional[List[Occasion]] = None
    condition: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    image_url: Optional[str] = None
    is_favorite: Optional[bool] = None
    favorite_score: Optional[float] = None


class AccessoryCreate(BaseModel):
    """Schema for creating a new accessory"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: str
    type: str
    style: ClothingStyle = ClothingStyle.CASUAL
    color: str
    secondary_colors: List[str] = []
    material: str
    brand: Optional[str] = None
    price: Optional[float] = None
    currency: str = "THB"
    occasions: List[Occasion] = []
    gemstone: Optional[str] = None
    carat: Optional[float] = None
    bag_capacity: Optional[str] = None
    tags: List[str] = []
    notes: Optional[str] = None
    image_url: Optional[str] = None
    is_favorite: bool = False
    favorite_score: float = 5.0


class AccessoryUpdate(BaseModel):
    """Schema for updating an accessory"""
    name: Optional[str] = None
    description: Optional[str] = None
    style: Optional[ClothingStyle] = None
    color: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[float] = None
    occasions: Optional[List[Occasion]] = None
    condition: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    image_url: Optional[str] = None
    is_favorite: Optional[bool] = None
    favorite_score: Optional[float] = None


class OutfitCreate(BaseModel):
    """Schema for creating a new outfit"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    clothing_items: List[str]
    accessories: List[str] = []
    style: ClothingStyle
    occasion: Occasion
    season: Season = Season.ALL_SEASON
    dominant_colors: List[str] = []
    mood: Optional[str] = None
    vibe: Optional[str] = None
    tags: List[str] = []
    notes: Optional[str] = None
    outfit_image_url: Optional[str] = None
    is_favorite: bool = False


class OutfitUpdate(BaseModel):
    """Schema for updating an outfit"""
    name: Optional[str] = None
    description: Optional[str] = None
    clothing_items: Optional[List[str]] = None
    accessories: Optional[List[str]] = None
    style: Optional[ClothingStyle] = None
    occasion: Optional[Occasion] = None
    season: Optional[Season] = None
    dominant_colors: Optional[List[str]] = None
    mood: Optional[str] = None
    vibe: Optional[str] = None
    rating: Optional[float] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    outfit_image_url: Optional[str] = None
    is_favorite: Optional[bool] = None


class WardrobeResponse(BaseModel):
    """Response for wardrobe data"""
    character_id: str
    character_name: str
    clothing_count: int
    accessory_count: int
    outfit_count: int
    current_outfit_id: Optional[str]
    stats: WardrobeStats


# =============================================================================
# MOCK DATA STORAGE (Replace with MongoDB later)
# =============================================================================

# Temporary in-memory storage
_wardrobes: Dict[str, Wardrobe] = {}


def get_or_create_wardrobe(character_id: str, character_name: str = "") -> Wardrobe:
    """Get existing wardrobe or create new one"""
    if character_id not in _wardrobes:
        _wardrobes[character_id] = Wardrobe(
            character_id=character_id,
            character_name=character_name or f"Character {character_id}"
        )
    return _wardrobes[character_id]


def update_wardrobe_stats(wardrobe: Wardrobe):
    """Update wardrobe statistics"""
    wardrobe.stats.total_clothing = len(wardrobe.clothing_collection)
    wardrobe.stats.total_accessories = len(wardrobe.accessory_collection)
    wardrobe.stats.total_outfits = len(wardrobe.outfit_collection)
    
    # Count by category
    clothing_by_cat = {}
    for item in wardrobe.clothing_collection:
        cat = item.category.value
        clothing_by_cat[cat] = clothing_by_cat.get(cat, 0) + 1
    wardrobe.stats.clothing_by_category = clothing_by_cat
    
    accessory_by_cat = {}
    for acc in wardrobe.accessory_collection:
        cat = acc.category.value
        accessory_by_cat[cat] = accessory_by_cat.get(cat, 0) + 1
    wardrobe.stats.accessories_by_category = accessory_by_cat
    
    # Count favorites
    wardrobe.stats.favorite_items_count = sum(
        1 for item in wardrobe.clothing_collection if item.is_favorite
    ) + sum(
        1 for acc in wardrobe.accessory_collection if acc.is_favorite
    )
    
    wardrobe.stats.favorite_outfits_count = sum(
        1 for outfit in wardrobe.outfit_collection if outfit.is_favorite
    )
    
    # Calculate total value
    total_value = sum(item.price or 0 for item in wardrobe.clothing_collection)
    total_value += sum(acc.price or 0 for acc in wardrobe.accessory_collection)
    wardrobe.stats.total_wardrobe_value = total_value
    
    total_items = wardrobe.stats.total_clothing + wardrobe.stats.total_accessories
    wardrobe.stats.average_item_value = total_value / total_items if total_items > 0 else 0
    
    # Most worn
    if wardrobe.clothing_collection:
        most_worn = max(wardrobe.clothing_collection, key=lambda x: x.wear_count)
        wardrobe.stats.most_worn_item_id = most_worn.item_id
    
    if wardrobe.outfit_collection:
        most_worn_outfit = max(wardrobe.outfit_collection, key=lambda x: x.wear_count)
        wardrobe.stats.most_worn_outfit_id = most_worn_outfit.outfit_id
    
    wardrobe.updated_at = datetime.utcnow()


# =============================================================================
# CLOTHING ENDPOINTS
# =============================================================================

@router.get("/{character_id}/clothing", response_model=List[ClothingItem])
async def get_clothing_items(
    character_id: str = Path(..., description="Character ID"),
    category: Optional[ClothingCategory] = Query(None, description="Filter by category"),
    style: Optional[ClothingStyle] = Query(None, description="Filter by style"),
    occasion: Optional[Occasion] = Query(None, description="Filter by occasion"),
    color: Optional[str] = Query(None, description="Filter by color"),
    favorite: Optional[bool] = Query(None, description="Filter favorites only")
):
    """Get all clothing items for a character with optional filters"""
    try:
        wardrobe = get_or_create_wardrobe(character_id)
        items = wardrobe.clothing_collection
        
        # Apply filters
        if category:
            items = [item for item in items if item.category == category]
        if style:
            items = [item for item in items if item.style == style]
        if occasion:
            items = [item for item in items if occasion in item.occasions]
        if color:
            items = [item for item in items if item.color.lower() == color.lower()]
        if favorite is not None:
            items = [item for item in items if item.is_favorite == favorite]
        
        return items
    except Exception as e:
        logger.error(f"Error getting clothing items: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{character_id}/clothing", response_model=ClothingItem)
async def create_clothing_item(
    character_id: str = Path(..., description="Character ID"),
    item_data: ClothingItemCreate = Body(...)
):
    """Add a new clothing item to wardrobe"""
    try:
        wardrobe = get_or_create_wardrobe(character_id)
        
        # Create new clothing item
        new_item = ClothingItem(**item_data.dict())
        wardrobe.clothing_collection.append(new_item)
        
        # Update stats
        update_wardrobe_stats(wardrobe)
        
        logger.info(f"Created clothing item {new_item.item_id} for {character_id}")
        return new_item
    except Exception as e:
        logger.error(f"Error creating clothing item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{character_id}/clothing/{item_id}", response_model=ClothingItem)
async def get_clothing_item(
    character_id: str = Path(..., description="Character ID"),
    item_id: str = Path(..., description="Clothing item ID")
):
    """Get a specific clothing item"""
    try:
        wardrobe = get_or_create_wardrobe(character_id)
        
        for item in wardrobe.clothing_collection:
            if item.item_id == item_id:
                return item
        
        raise HTTPException(status_code=404, detail=f"Clothing item {item_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting clothing item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{character_id}/clothing/{item_id}", response_model=ClothingItem)
async def update_clothing_item(
    character_id: str = Path(..., description="Character ID"),
    item_id: str = Path(..., description="Clothing item ID"),
    update_data: ClothingItemUpdate = Body(...)
):
    """Update a clothing item"""
    try:
        wardrobe = get_or_create_wardrobe(character_id)
        
        for item in wardrobe.clothing_collection:
            if item.item_id == item_id:
                # Update fields
                update_dict = update_data.dict(exclude_unset=True)
                for key, value in update_dict.items():
                    setattr(item, key, value)
                
                item.updated_at = datetime.utcnow()
                update_wardrobe_stats(wardrobe)
                
                logger.info(f"Updated clothing item {item_id}")
                return item
        
        raise HTTPException(status_code=404, detail=f"Clothing item {item_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating clothing item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{character_id}/clothing/{item_id}")
async def delete_clothing_item(
    character_id: str = Path(..., description="Character ID"),
    item_id: str = Path(..., description="Clothing item ID")
):
    """Delete a clothing item"""
    try:
        wardrobe = get_or_create_wardrobe(character_id)
        
        for i, item in enumerate(wardrobe.clothing_collection):
            if item.item_id == item_id:
                wardrobe.clothing_collection.pop(i)
                update_wardrobe_stats(wardrobe)
                
                logger.info(f"Deleted clothing item {item_id}")
                return {"message": f"Clothing item {item_id} deleted successfully"}
        
        raise HTTPException(status_code=404, detail=f"Clothing item {item_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting clothing item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# ACCESSORIES ENDPOINTS
# =============================================================================

@router.get("/{character_id}/accessories", response_model=List[Accessory])
async def get_accessories(
    character_id: str = Path(..., description="Character ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    type: Optional[str] = Query(None, description="Filter by type"),
    favorite: Optional[bool] = Query(None, description="Filter favorites only")
):
    """Get all accessories for a character"""
    try:
        wardrobe = get_or_create_wardrobe(character_id)
        accessories = wardrobe.accessory_collection
        
        # Apply filters
        if category:
            accessories = [acc for acc in accessories if acc.category.value == category]
        if type:
            accessories = [acc for acc in accessories if acc.type.value == type]
        if favorite is not None:
            accessories = [acc for acc in accessories if acc.is_favorite == favorite]
        
        return accessories
    except Exception as e:
        logger.error(f"Error getting accessories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{character_id}/accessories", response_model=Accessory)
async def create_accessory(
    character_id: str = Path(..., description="Character ID"),
    accessory_data: AccessoryCreate = Body(...)
):
    """Add a new accessory to wardrobe"""
    try:
        wardrobe = get_or_create_wardrobe(character_id)
        
        new_accessory = Accessory(**accessory_data.dict())
        wardrobe.accessory_collection.append(new_accessory)
        
        update_wardrobe_stats(wardrobe)
        
        logger.info(f"Created accessory {new_accessory.accessory_id} for {character_id}")
        return new_accessory
    except Exception as e:
        logger.error(f"Error creating accessory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{character_id}/accessories/{accessory_id}", response_model=Accessory)
async def get_accessory(
    character_id: str = Path(..., description="Character ID"),
    accessory_id: str = Path(..., description="Accessory ID")
):
    """Get a specific accessory"""
    try:
        wardrobe = get_or_create_wardrobe(character_id)
        
        for acc in wardrobe.accessory_collection:
            if acc.accessory_id == accessory_id:
                return acc
        
        raise HTTPException(status_code=404, detail=f"Accessory {accessory_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting accessory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{character_id}/accessories/{accessory_id}", response_model=Accessory)
async def update_accessory(
    character_id: str = Path(..., description="Character ID"),
    accessory_id: str = Path(..., description="Accessory ID"),
    update_data: AccessoryUpdate = Body(...)
):
    """Update an accessory"""
    try:
        wardrobe = get_or_create_wardrobe(character_id)
        
        for acc in wardrobe.accessory_collection:
            if acc.accessory_id == accessory_id:
                update_dict = update_data.dict(exclude_unset=True)
                for key, value in update_dict.items():
                    setattr(acc, key, value)
                
                acc.updated_at = datetime.utcnow()
                update_wardrobe_stats(wardrobe)
                
                logger.info(f"Updated accessory {accessory_id}")
                return acc
        
        raise HTTPException(status_code=404, detail=f"Accessory {accessory_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating accessory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{character_id}/accessories/{accessory_id}")
async def delete_accessory(
    character_id: str = Path(..., description="Character ID"),
    accessory_id: str = Path(..., description="Accessory ID")
):
    """Delete an accessory"""
    try:
        wardrobe = get_or_create_wardrobe(character_id)
        
        for i, acc in enumerate(wardrobe.accessory_collection):
            if acc.accessory_id == accessory_id:
                wardrobe.accessory_collection.pop(i)
                update_wardrobe_stats(wardrobe)
                
                logger.info(f"Deleted accessory {accessory_id}")
                return {"message": f"Accessory {accessory_id} deleted successfully"}
        
        raise HTTPException(status_code=404, detail=f"Accessory {accessory_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting accessory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# OUTFITS ENDPOINTS
# =============================================================================

@router.get("/{character_id}/outfits", response_model=List[Outfit])
async def get_outfits(
    character_id: str = Path(..., description="Character ID"),
    style: Optional[ClothingStyle] = Query(None, description="Filter by style"),
    occasion: Optional[Occasion] = Query(None, description="Filter by occasion"),
    favorite: Optional[bool] = Query(None, description="Filter favorites only")
):
    """Get all outfits for a character"""
    try:
        wardrobe = get_or_create_wardrobe(character_id)
        outfits = wardrobe.outfit_collection
        
        # Apply filters
        if style:
            outfits = [outfit for outfit in outfits if outfit.style == style]
        if occasion:
            outfits = [outfit for outfit in outfits if outfit.occasion == occasion]
        if favorite is not None:
            outfits = [outfit for outfit in outfits if outfit.is_favorite == favorite]
        
        return outfits
    except Exception as e:
        logger.error(f"Error getting outfits: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{character_id}/outfits", response_model=Outfit)
async def create_outfit(
    character_id: str = Path(..., description="Character ID"),
    outfit_data: OutfitCreate = Body(...)
):
    """Create a new outfit"""
    try:
        wardrobe = get_or_create_wardrobe(character_id)
        
        new_outfit = Outfit(**outfit_data.dict())
        wardrobe.outfit_collection.append(new_outfit)
        
        update_wardrobe_stats(wardrobe)
        
        logger.info(f"Created outfit {new_outfit.outfit_id} for {character_id}")
        return new_outfit
    except Exception as e:
        logger.error(f"Error creating outfit: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{character_id}/outfits/{outfit_id}", response_model=Outfit)
async def get_outfit(
    character_id: str = Path(..., description="Character ID"),
    outfit_id: str = Path(..., description="Outfit ID")
):
    """Get a specific outfit"""
    try:
        wardrobe = get_or_create_wardrobe(character_id)
        
        for outfit in wardrobe.outfit_collection:
            if outfit.outfit_id == outfit_id:
                return outfit
        
        raise HTTPException(status_code=404, detail=f"Outfit {outfit_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting outfit: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{character_id}/outfits/{outfit_id}", response_model=Outfit)
async def update_outfit(
    character_id: str = Path(..., description="Character ID"),
    outfit_id: str = Path(..., description="Outfit ID"),
    update_data: OutfitUpdate = Body(...)
):
    """Update an outfit"""
    try:
        wardrobe = get_or_create_wardrobe(character_id)
        
        for outfit in wardrobe.outfit_collection:
            if outfit.outfit_id == outfit_id:
                update_dict = update_data.dict(exclude_unset=True)
                for key, value in update_dict.items():
                    setattr(outfit, key, value)
                
                outfit.updated_at = datetime.utcnow()
                update_wardrobe_stats(wardrobe)
                
                logger.info(f"Updated outfit {outfit_id}")
                return outfit
        
        raise HTTPException(status_code=404, detail=f"Outfit {outfit_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating outfit: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{character_id}/outfits/{outfit_id}")
async def delete_outfit(
    character_id: str = Path(..., description="Character ID"),
    outfit_id: str = Path(..., description="Outfit ID")
):
    """Delete an outfit"""
    try:
        wardrobe = get_or_create_wardrobe(character_id)
        
        for i, outfit in enumerate(wardrobe.outfit_collection):
            if outfit.outfit_id == outfit_id:
                wardrobe.outfit_collection.pop(i)
                update_wardrobe_stats(wardrobe)
                
                logger.info(f"Deleted outfit {outfit_id}")
                return {"message": f"Outfit {outfit_id} deleted successfully"}
        
        raise HTTPException(status_code=404, detail=f"Outfit {outfit_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting outfit: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{character_id}/outfits/{outfit_id}/wear")
async def wear_outfit(
    character_id: str = Path(..., description="Character ID"),
    outfit_id: str = Path(..., description="Outfit ID")
):
    """Wear an outfit (set as current)"""
    try:
        wardrobe = get_or_create_wardrobe(character_id)
        
        # Check if outfit exists
        outfit_found = False
        for outfit in wardrobe.outfit_collection:
            if outfit.outfit_id == outfit_id:
                outfit_found = True
                outfit.wear_count += 1
                outfit.last_worn = datetime.utcnow()
                break
        
        if not outfit_found:
            raise HTTPException(status_code=404, detail=f"Outfit {outfit_id} not found")
        
        # Set as current outfit
        wardrobe.current_outfit_id = outfit_id
        update_wardrobe_stats(wardrobe)
        
        logger.info(f"Character {character_id} is now wearing outfit {outfit_id}")
        return {
            "message": f"Now wearing outfit {outfit_id}",
            "outfit_id": outfit_id,
            "character_id": character_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error wearing outfit: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# WARDROBE MANAGEMENT ENDPOINTS
# =============================================================================

@router.get("/{character_id}", response_model=WardrobeResponse)
async def get_wardrobe(
    character_id: str = Path(..., description="Character ID")
):
    """Get complete wardrobe information"""
    try:
        wardrobe = get_or_create_wardrobe(character_id)
        
        return WardrobeResponse(
            character_id=wardrobe.character_id,
            character_name=wardrobe.character_name,
            clothing_count=len(wardrobe.clothing_collection),
            accessory_count=len(wardrobe.accessory_collection),
            outfit_count=len(wardrobe.outfit_collection),
            current_outfit_id=wardrobe.current_outfit_id,
            stats=wardrobe.stats
        )
    except Exception as e:
        logger.error(f"Error getting wardrobe: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{character_id}/stats", response_model=WardrobeStats)
async def get_wardrobe_stats(
    character_id: str = Path(..., description="Character ID")
):
    """Get wardrobe statistics"""
    try:
        wardrobe = get_or_create_wardrobe(character_id)
        update_wardrobe_stats(wardrobe)
        
        return wardrobe.stats
    except Exception as e:
        logger.error(f"Error getting wardrobe stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{character_id}/current-outfit", response_model=Optional[Outfit])
async def get_current_outfit(
    character_id: str = Path(..., description="Character ID")
):
    """Get the outfit currently being worn"""
    try:
        wardrobe = get_or_create_wardrobe(character_id)
        
        if not wardrobe.current_outfit_id:
            return None
        
        for outfit in wardrobe.outfit_collection:
            if outfit.outfit_id == wardrobe.current_outfit_id:
                return outfit
        
        # Current outfit ID exists but outfit not found - reset it
        wardrobe.current_outfit_id = None
        return None
    except Exception as e:
        logger.error(f"Error getting current outfit: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================

@router.get("/{character_id}/favorites")
async def get_favorites(
    character_id: str = Path(..., description="Character ID")
):
    """Get all favorite items and outfits"""
    try:
        wardrobe = get_or_create_wardrobe(character_id)
        
        return {
            "clothing": [item for item in wardrobe.clothing_collection if item.is_favorite],
            "accessories": [acc for acc in wardrobe.accessory_collection if acc.is_favorite],
            "outfits": [outfit for outfit in wardrobe.outfit_collection if outfit.is_favorite]
        }
    except Exception as e:
        logger.error(f"Error getting favorites: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{character_id}/organize")
async def organize_wardrobe(
    character_id: str = Path(..., description="Character ID")
):
    """Organize and update wardrobe statistics"""
    try:
        wardrobe = get_or_create_wardrobe(character_id)
        update_wardrobe_stats(wardrobe)
        
        return {
            "message": "Wardrobe organized successfully",
            "stats": wardrobe.stats
        }
    except Exception as e:
        logger.error(f"Error organizing wardrobe: {e}")
        raise HTTPException(status_code=500, detail=str(e))
