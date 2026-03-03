"""
Production Breakdown Models for Peace Script

This module contains MongoDB models for production planning and management.
Implements the production breakdown system from Peace Script workflow (STEP 5):
- Breakdown Q: Production queue management
- Scene Breakdown: Scene-level production details
- Crew Sheet: Crew and equipment management
- Props Inventory: Props tracking

Author: Peace Script Team
Date: 18 November 2568
Version: 1.0
"""

from beanie import Document
from pydantic import BaseModel, Field, validator
from datetime import datetime, date, time
from typing import Optional, List
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class ShootingPeriod(str, Enum):
    """Shooting time period"""
    DAY = "D"           # Day shooting
    NIGHT = "N"         # Night shooting
    DAWN = "DN"         # Dawn
    DUSK = "DK"         # Dusk
    MAGIC_HOUR = "MH"   # Magic hour


class LocationType(str, Enum):
    """Location type"""
    INTERIOR = "INT"    # Interior
    EXTERIOR = "EXT"    # Exterior
    INT_EXT = "INT/EXT" # Both


class ProductionStatus(str, Enum):
    """Production status"""
    PLANNING = "planning"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PropCategory(str, Enum):
    """Props category"""
    HAND_PROPS = "hand_props"           # Props held by actors
    SET_DRESSING = "set_dressing"       # Background decoration
    CONSUMABLES = "consumables"         # Food, drinks, etc.
    VEHICLES = "vehicles"               # Cars, motorcycles, etc.
    WEAPONS = "weapons"                 # Weapons (real/prop)
    SPECIAL_EFFECTS = "special_effects" # SFX props
    DOCUMENTS = "documents"             # Papers, books, etc.
    TECHNOLOGY = "technology"           # Phones, computers, etc.


# ============================================================================
# Sub-Models
# ============================================================================

class CrewMember(BaseModel):
    """Crew member information"""
    name: str
    role: str                           # Director, DP, AD, etc.
    phone: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None


class CastMember(BaseModel):
    """Cast member information"""
    character_id: str                   # Reference to Character
    character_name: str
    actor_name: str
    actor_id: Optional[str] = None      # Reference to Actor (if exists)
    costume_notes: Optional[str] = None
    makeup_notes: Optional[str] = None


class ExtraRequirement(BaseModel):
    """Extra/background actor requirement"""
    description: str                    # "ชาวบ้าน", "คนในตลาด"
    count: int                          # จำนวนคน
    costume_type: Optional[str] = None  # ประเภทเครื่องแต่งกาย
    special_requirements: Optional[str] = None


class PropItem(BaseModel):
    """Individual prop item"""
    name: str
    category: PropCategory
    quantity: int = 1
    description: Optional[str] = None
    source: Optional[str] = None        # Where to get it
    cost_estimate: Optional[float] = None
    notes: Optional[str] = None


class EquipmentItem(BaseModel):
    """Equipment item"""
    name: str                           # Camera, lens, lighting, etc.
    type: str                           # "camera", "lens", "lighting", "sound"
    quantity: int = 1
    specifications: Optional[str] = None
    rental_cost: Optional[float] = None
    notes: Optional[str] = None


# ============================================================================
# Main Models
# ============================================================================

class ProductionQueue(Document):
    """Production Queue (Breakdown Q)
    
    Represents a filming queue/day.
    Part 1 of the 3-table breakdown system.
    
    Attributes:
        queue_id: Unique queue identifier (e.g., "Q001", "Q002")
        queue_number: Queue sequence number
        project_id: Reference to parent Project
        company_name: Production company
        filming_date: Scheduled filming date
        call_time: Crew call time
        location: Filming location address
        breakdown_by: Person who created breakdown
        director: Director name
        first_ad: First Assistant Director
        first_ad_phone: 1st AD phone number
        pm_phone: Production Manager phone
        status: Queue status
        notes: Additional notes
    
    Example:
        ```python
        queue = ProductionQueue(
            queue_id="Q001",
            queue_number=1,
            project_id="proj_001",
            company_name="Peace Studio",
            filming_date=date(2025, 1, 20),
            call_time=time(6, 0),
            location="บ้านในชนบท ปากช่อง นครราชสีมา",
            director="สมชาย ใจดี",
            first_ad="สมหญิง ขยัน",
            first_ad_phone="08-1234-5678",
            pm_phone="08-8765-4321"
        )
        await queue.insert()
        ```
    """
    
    # Primary fields
    queue_id: str = Field(
        ...,
        description="Unique queue identifier"
    )
    queue_number: int = Field(
        ...,
        ge=1,
        description="Queue sequence number"
    )
    project_id: str = Field(
        ...,
        description="Reference to parent Project"
    )
    
    # Production details
    company_name: str = Field(
        default="Peace Studio",
        description="Production company name"
    )
    theme: Optional[str] = Field(
        default=None,
        description="Theme/concept for this queue"
    )
    filming_date: date = Field(
        ...,
        description="Scheduled filming date"
    )
    call_time: time = Field(
        default=time(6, 0),
        description="Crew call time"
    )
    location: str = Field(
        ...,
        description="Filming location address"
    )
    
    # Personnel
    breakdown_by: str = Field(
        default="Peace Script System",
        description="Person who created breakdown"
    )
    director: str = Field(
        ...,
        description="Director name"
    )
    first_ad: str = Field(
        ...,
        description="First Assistant Director name"
    )
    first_ad_phone: Optional[str] = Field(
        default=None,
        description="1st AD phone number"
    )
    pm_phone: Optional[str] = Field(
        default=None,
        description="Production Manager phone"
    )
    
    # Status
    status: ProductionStatus = Field(
        default=ProductionStatus.PLANNING,
        description="Queue status"
    )
    
    # Additional
    weather_forecast: Optional[str] = None
    backup_location: Optional[str] = None
    notes: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    class Settings:
        name = "production_queues"
        indexes = [
            "queue_id",
            "project_id",
            "filming_date",
            [("project_id", 1), ("queue_number", 1)]
        ]


class SceneBreakdown(Document):
    """Scene Breakdown
    
    Detailed breakdown for each scene within a queue.
    Part 2 of the 3-table breakdown system.
    
    Attributes:
        breakdown_id: Unique breakdown identifier
        queue_id: Reference to ProductionQueue
        scene_id: Reference to Scene
        scene_number: Scene number
        shooting_time: Estimated time to shoot this scene
        location: Specific location for this scene
        int_ext: Interior/Exterior
        day_night: Day or Night shooting
        set_name: Name of the set
        scene_name: Short scene description
        description: Detailed scene description
        cast: List of cast members in this scene
        extras: List of extra requirements
        props: List of required props
        costumes: List of costume requirements
        special_requirements: Special needs (SFX, stunts, etc.)
        estimated_duration: Estimated scene duration in minutes
    
    Example:
        ```python
        breakdown = SceneBreakdown(
            breakdown_id="BD_Q001_S001",
            queue_id="Q001",
            scene_id="scene_001",
            scene_number=1,
            shooting_time=120,  # 2 hours
            location="บ้านพ่อของคอย - ห้องนั่งเล่น",
            int_ext=LocationType.INTERIOR,
            day_night=ShootingPeriod.DAY,
            set_name="บ้านพ่อคอย",
            scene_name="คอยกลับบ้านพบพ่อป่วย",
            cast=[
                {"character_id": "char_001", "character_name": "คอย", "actor_name": "..."},
                {"character_id": "char_002", "character_name": "พ่อ", "actor_name": "..."}
            ],
            props=[
                {"name": "เตียงนอน", "category": "set_dressing", "quantity": 1},
                {"name": "ยา", "category": "hand_props", "quantity": 3}
            ]
        )
        await breakdown.insert()
        ```
    """
    
    # Primary fields
    breakdown_id: str = Field(
        ...,
        description="Unique breakdown identifier"
    )
    queue_id: str = Field(
        ...,
        description="Reference to ProductionQueue"
    )
    scene_id: str = Field(
        ...,
        description="Reference to Scene"
    )
    scene_number: int = Field(
        ...,
        ge=1,
        description="Scene number in script"
    )
    
    # Timing
    shooting_time: int = Field(
        ...,
        ge=1,
        description="Estimated shooting time in minutes"
    )
    estimated_duration: Optional[float] = Field(
        default=None,
        description="Estimated scene duration in final cut (seconds)"
    )
    
    # Location details
    location: str = Field(
        ...,
        description="Specific location for this scene"
    )
    int_ext: LocationType = Field(
        ...,
        description="Interior or Exterior"
    )
    day_night: ShootingPeriod = Field(
        ...,
        description="Day or Night shooting"
    )
    set_name: str = Field(
        ...,
        description="Name of the set"
    )
    
    # Scene details
    scene_name: str = Field(
        ...,
        description="Short scene description"
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed scene description"
    )
    
    # Production requirements
    cast: List[CastMember] = Field(
        default_factory=list,
        description="Cast members in this scene"
    )
    extras: List[ExtraRequirement] = Field(
        default_factory=list,
        description="Extra/background actors needed"
    )
    props: List[PropItem] = Field(
        default_factory=list,
        description="Props required for this scene"
    )
    costumes: List[str] = Field(
        default_factory=list,
        description="Costume requirements (list of descriptions)"
    )
    special_requirements: Optional[str] = Field(
        default=None,
        description="Special requirements (SFX, stunts, animals, etc.)"
    )
    
    # Additional notes
    camera_notes: Optional[str] = None
    lighting_notes: Optional[str] = None
    sound_notes: Optional[str] = None
    remarks: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    class Settings:
        name = "scene_breakdowns"
        indexes = [
            "breakdown_id",
            "queue_id",
            "scene_id",
            [("queue_id", 1), ("scene_number", 1)]
        ]


class CrewSheet(Document):
    """Crew and Equipment Sheet
    
    Crew and equipment management for a production queue.
    Part 3 of the 3-table breakdown system.
    
    Attributes:
        sheet_id: Unique sheet identifier
        queue_id: Reference to ProductionQueue
        crew: List of crew members
        actors: List of actors for this queue
        extras: List of extras (consolidated from all scenes)
        equipment: List of equipment needed
        on_location_time: Expected arrival time on location
        ready_to_shoot_time: Expected ready-to-shoot time
        wrap_time: Expected wrap time
        total_extras: Total number of extras
        total_costumes: Total number of costumes
        total_props: Total number of props
        support_notes: Additional support requirements
        special_notes: Special considerations
    
    Example:
        ```python
        sheet = CrewSheet(
            sheet_id="CS_Q001",
            queue_id="Q001",
            crew=[
                {"name": "สมชาย ใจดี", "role": "Director", "phone": "08-1111-1111"},
                {"name": "สมหญิง ขยัน", "role": "1st AD", "phone": "08-2222-2222"}
            ],
            equipment=[
                {"name": "Sony FX6", "type": "camera", "quantity": 2},
                {"name": "Canon 24-70mm", "type": "lens", "quantity": 2}
            ],
            on_location_time=time(6, 30),
            ready_to_shoot_time=time(8, 0),
            total_extras=15,
            total_costumes=20,
            total_props=45
        )
        await sheet.insert()
        ```
    """
    
    # Primary fields
    sheet_id: str = Field(
        ...,
        description="Unique sheet identifier"
    )
    queue_id: str = Field(
        ...,
        description="Reference to ProductionQueue"
    )
    
    # Personnel
    crew: List[CrewMember] = Field(
        default_factory=list,
        description="Crew members for this queue"
    )
    actors: List[CastMember] = Field(
        default_factory=list,
        description="Actors scheduled for this queue"
    )
    extras: List[ExtraRequirement] = Field(
        default_factory=list,
        description="Consolidated extras requirements"
    )
    
    # Equipment
    equipment: List[EquipmentItem] = Field(
        default_factory=list,
        description="Equipment needed for this queue"
    )
    
    # Timing
    on_location_time: Optional[time] = Field(
        default=None,
        description="Expected arrival time on location"
    )
    ready_to_shoot_time: Optional[time] = Field(
        default=None,
        description="Expected ready-to-shoot time"
    )
    wrap_time: Optional[time] = Field(
        default=None,
        description="Expected wrap time"
    )
    
    # Totals
    total_extras: int = Field(
        default=0,
        ge=0,
        description="Total number of extras"
    )
    total_costumes: int = Field(
        default=0,
        ge=0,
        description="Total number of costumes"
    )
    total_props: int = Field(
        default=0,
        ge=0,
        description="Total number of props"
    )
    
    # Support
    support_notes: Optional[str] = Field(
        default=None,
        description="Additional support requirements"
    )
    special_notes: Optional[str] = Field(
        default=None,
        description="Special considerations (safety, permits, etc.)"
    )
    
    # Budget
    estimated_budget: Optional[float] = Field(
        default=None,
        description="Estimated budget for this queue"
    )
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    class Settings:
        name = "crew_sheets"
        indexes = [
            "sheet_id",
            "queue_id"
        ]


class PropsInventory(Document):
    """Props Inventory
    
    Master list of all props for a project.
    Tracks availability, source, and usage across scenes.
    
    Attributes:
        prop_id: Unique prop identifier
        project_id: Reference to Project
        name: Prop name
        category: Prop category
        description: Detailed description
        quantity_needed: Total quantity needed
        quantity_available: Quantity currently available
        source: Where to acquire (buy/rent/make/have)
        cost_estimate: Estimated cost
        scenes_used: List of scene IDs where this prop is used
        status: Acquisition status
    
    Example:
        ```python
        prop = PropsInventory(
            prop_id="PROP_001",
            project_id="proj_001",
            name="ถุงมือชกหนังแท้",
            category=PropCategory.HAND_PROPS,
            description="ถุงมือชกสีแดง ขนาด 10 oz",
            quantity_needed=2,
            quantity_available=2,
            source="Rent from Fairtex",
            cost_estimate=1500.0,
            scenes_used=["scene_005", "scene_012", "scene_025"],
            status="acquired"
        )
        await prop.insert()
        ```
    """
    
    # Primary fields
    prop_id: str = Field(
        ...,
        description="Unique prop identifier"
    )
    project_id: str = Field(
        ...,
        description="Reference to Project"
    )
    
    # Prop details
    name: str = Field(
        ...,
        description="Prop name"
    )
    category: PropCategory = Field(
        ...,
        description="Prop category"
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed prop description"
    )
    
    # Quantity tracking
    quantity_needed: int = Field(
        ...,
        ge=1,
        description="Total quantity needed for production"
    )
    quantity_available: int = Field(
        default=0,
        ge=0,
        description="Quantity currently available"
    )
    
    # Acquisition
    source: Optional[str] = Field(
        default=None,
        description="Where to acquire (buy/rent/make/have)"
    )
    supplier: Optional[str] = Field(
        default=None,
        description="Supplier name/contact"
    )
    cost_estimate: Optional[float] = Field(
        default=None,
        ge=0,
        description="Estimated cost (Baht)"
    )
    actual_cost: Optional[float] = Field(
        default=None,
        ge=0,
        description="Actual cost paid"
    )
    
    # Usage
    scenes_used: List[str] = Field(
        default_factory=list,
        description="List of scene IDs where this prop is used"
    )
    usage_notes: Optional[str] = Field(
        default=None,
        description="Notes on how prop is used"
    )
    
    # Status
    status: str = Field(
        default="needed",
        description="Status: needed, ordered, acquired, returned"
    )
    
    # Storage
    storage_location: Optional[str] = None
    responsible_person: Optional[str] = None
    
    # Images
    reference_images: List[str] = Field(
        default_factory=list,
        description="URLs to reference images"
    )
    
    # Additional notes
    notes: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    class Settings:
        name = "props_inventory"
        indexes = [
            "prop_id",
            "project_id",
            "category",
            "status"
        ]
    
    @validator("quantity_available")
    def validate_quantity(cls, v, values):
        """Ensure available doesn't exceed needed"""
        if "quantity_needed" in values and v > values["quantity_needed"]:
            raise ValueError("Available quantity cannot exceed needed quantity")
        return v


# ============================================================================
# Helper Models
# ============================================================================

class SceneSetDetails(Document):
    """Scene Set Details
    
    Detailed information about sets/locations.
    
    Attributes:
        set_id: Unique set identifier
        project_id: Reference to Project
        set_name: Name of the set
        location_type: Interior/Exterior
        address: Physical address
        description: Set description
        dimensions: Set dimensions
        power_available: Available electrical power
        water_available: Water availability
        parking: Parking information
        permits_required: Required permits
        contact_person: Location contact
        rental_cost: Rental cost (if applicable)
        scenes_shot_here: List of scenes shot at this location
    """
    
    set_id: str = Field(..., description="Unique set identifier")
    project_id: str = Field(..., description="Reference to Project")
    set_name: str = Field(..., description="Name of the set")
    location_type: LocationType = Field(..., description="INT/EXT")
    
    address: Optional[str] = None
    description: Optional[str] = None
    dimensions: Optional[str] = None  # "10x12 meters"
    
    # Facilities
    power_available: Optional[str] = None
    water_available: bool = Field(default=False)
    restrooms: bool = Field(default=False)
    parking: Optional[str] = None
    
    # Permissions
    permits_required: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    
    # Cost
    rental_cost: Optional[float] = None
    rental_period: Optional[str] = None  # "per day", "per hour"
    
    # Usage
    scenes_shot_here: List[str] = Field(
        default_factory=list,
        description="List of scene IDs shot at this location"
    )
    
    # Photos
    location_photos: List[str] = Field(
        default_factory=list,
        description="URLs to location photos"
    )
    
    notes: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "scene_set_details"
        indexes = ["set_id", "project_id"]
