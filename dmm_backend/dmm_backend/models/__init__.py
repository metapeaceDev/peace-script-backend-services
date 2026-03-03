"""
Character System Models
Extended models for comprehensive character development based on STEP 3
"""

from .character_consciousness import Consciousness
from .character_defilement import Defilement
from .character_subconscious import Attachment, Taanha
from .social_status import SocialStatus
from .character_goals import CharacterGoals
from .health_history import (
    HealthHistory,
    HealthCondition,
    Injury,
    Surgery,
    Medication,
    Allergy,
    Disability,
    MentalHealthHistory
)
from .character_aspirations import (
    CharacterAspirations,
    LifeAspiration,
    AspirationConflict,
    AspirationType,
    AspirationTimeline,
    AspirationStatus,
    AspirationSource
)
from .kamma_graph import (
    KammaNode,
    KammaEdge,
    KammaGraph
)
from .wardrobe import (
    ClothingItem,
    Accessory,
    Outfit,
    Wardrobe,
    WardrobeStats,
    ClothingType,
    ClothingCategory,
    AccessoryType,
    AccessoryCategory,
    ClothingStyle,
    Season,
    Occasion
)

__all__ = [
    "Consciousness",
    "Defilement",
    "Attachment",
    "Taanha",
    "SocialStatus",
    "CharacterGoals",
    "HealthHistory",
    "HealthCondition",
    "Injury",
    "Surgery",
    "Medication",
    "Allergy",
    "Disability",
    "MentalHealthHistory",
    "CharacterAspirations",
    "LifeAspiration",
    "AspirationConflict",
    "AspirationType",
    "AspirationTimeline",
    "AspirationStatus",
    "AspirationSource",
    "KammaNode",
    "KammaEdge",
    "KammaGraph",
    # Wardrobe System (STEP 3.5)
    "ClothingItem",
    "Accessory",
    "Outfit",
    "Wardrobe",
    "WardrobeStats",
    "ClothingType",
    "ClothingCategory",
    "AccessoryType",
    "AccessoryCategory",
    "ClothingStyle",
    "Season",
    "Occasion"
]
