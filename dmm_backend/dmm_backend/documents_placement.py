"""
Product Placement Models

This module implements database models for Product Placement (Tie-in สินค้า) system.
Integrated with Step 5: Scene Design in Peace Script workflow.

Features:
- Product management (รายการสินค้า)
- Brand management (แบรนด์)
- Product placement in scenes/shots (การวางสินค้าในฉาก)
- Ethics compliance checking (ตรวจสอบจริยธรรม)
- Analytics and reporting (วิเคราะห์และรายงาน)

Author: Peace Script Team
Date: 20 November 2025
Version: 1.0
"""

from beanie import Document
from pydantic import Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class ProductCategory(str, Enum):
    """Product categories"""
    FOOD_BEVERAGE = "food_beverage"          # อาหารและเครื่องดื่ม
    ELECTRONICS = "electronics"              # อิเล็กทรอนิกส์
    FASHION = "fashion"                      # แฟชั่น
    AUTOMOTIVE = "automotive"                # ยานยนต์
    BEAUTY_PERSONAL_CARE = "beauty_personal_care"  # ความงามและของใช้ส่วนตัว
    HOME_LIVING = "home_living"              # บ้านและการใช้ชีวิต
    SPORTS_FITNESS = "sports_fitness"        # กีฬาและฟิตเนส
    ENTERTAINMENT = "entertainment"          # บันเทิง
    TECHNOLOGY = "technology"                # เทคโนโลยี
    HEALTHCARE = "healthcare"                # สุขภาพ
    EDUCATION = "education"                  # การศึกษา
    TRAVEL_HOSPITALITY = "travel_hospitality"  # ท่องเที่ยว
    FINANCIAL_SERVICES = "financial_services"  # บริการทางการเงิน
    OTHER = "other"                          # อื่นๆ


class PlacementMode(str, Enum):
    """Placement modes (รูปแบบการวางสินค้า)"""
    ORGANIC = "organic"          # กลมกลืนกับบริบท
    EXPLICIT = "explicit"        # เน้นชัดเจน
    BACKGROUND = "background"    # อยู่เบื้องหลัง
    INTERACTIVE = "interactive"  # มีการโต้ตอบ


class Visibility(str, Enum):
    """Visibility levels (ระดับความเห็นชัด)"""
    SUBTLE = "subtle"        # เห็นแทบไม่เห็น
    MODERATE = "moderate"    # เห็นปานกลาง
    PROMINENT = "prominent"  # เห็นชัดเจน


class ContextFit(str, Enum):
    """Context fitting (ความเหมาะสมกับบริบท)"""
    NATURAL = "natural"    # เป็นธรรมชาติ
    FORCED = "forced"      # ดูบังคับ
    AWKWARD = "awkward"    # ไม่เหมาะสม


class DhammaFit(str, Enum):
    """Dhamma/Ethics compliance (ความสอดคล้องกับหลักธรรม)"""
    FIT = "fit"            # สอดคล้อง
    NEUTRAL = "neutral"    # เป็นกลาง
    CONFLICT = "conflict"  # ขัดแย้ง


class Position(str, Enum):
    """Position in frame (ตำแหน่งในเฟรม)"""
    FOREGROUND = "foreground"    # หน้าภาพ
    MIDGROUND = "midground"      # กลางภาพ
    BACKGROUND = "background"    # หลังภาพ


class TargetAudience(str, Enum):
    """Target audience (กลุ่มเป้าหมาย)"""
    CHILD = "child"          # เด็ก (0-12 ปี)
    TEEN = "teen"            # วัยรุ่น (13-19 ปี)
    YOUNG_ADULT = "young_adult"  # ผู้ใหญ่ตอนต้น (20-35 ปี)
    ADULT = "adult"          # ผู้ใหญ่ (36-55 ปี)
    SENIOR = "senior"        # ผู้สูงอายุ (56+ ปี)
    GENERAL = "general"      # ทั่วไป


# ============================================================================
# BRAND MODEL
# ============================================================================

class Brand(Document):
    """Brand Model
    
    Represents a brand/company (แบรนด์/บริษัท).
    Used for organizing products and tracking brand presence.
    
    Attributes:
        brand_id: Unique brand identifier
        brand_name: Brand name (ชื่อแบรนด์)
        logo_url: Brand logo URL
        industry: Industry type (ประเภทอุตสาหกรรม)
        description: Brand description
        values: Brand values/principles (คุณค่า/หลักการ)
        website: Brand website
        contact_email: Contact email
        is_active: Active status
        created_at: Creation timestamp
        updated_at: Last update timestamp
    
    Example:
        ```python
        brand = Brand(
            brand_name="Coca-Cola",
            industry="Food & Beverage",
            values=["happiness", "sharing", "refreshment"],
            website="https://www.coca-cola.com"
        )
        await brand.insert()
        ```
    """
    
    # Primary fields
    brand_id: str = Field(
        default_factory=lambda: f"BRD_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        description="Unique brand identifier"
    )
    brand_name: str = Field(
        ...,
        description="Brand name",
        min_length=2,
        max_length=200
    )
    
    # Brand details
    logo_url: Optional[str] = Field(
        None,
        description="Brand logo URL"
    )
    industry: str = Field(
        ...,
        description="Industry type",
        max_length=100
    )
    description: Optional[str] = Field(
        None,
        description="Brand description",
        max_length=2000
    )
    values: List[str] = Field(
        default_factory=list,
        description="Brand values/principles"
    )
    
    # Contact information
    website: Optional[str] = Field(
        None,
        description="Brand website URL"
    )
    contact_email: Optional[str] = Field(
        None,
        description="Contact email"
    )
    
    # Status
    is_active: bool = Field(
        default=True,
        description="Active status"
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
        name = "placement_brands"
        indexes = [
            "brand_id",
            "brand_name",
            "industry",
            "is_active",
            "created_at"
        ]
    
    def __repr__(self):
        return f"<Brand {self.brand_name} ({self.brand_id})>"
    
    def __str__(self):
        return self.brand_name


# ============================================================================
# PRODUCT MODEL
# ============================================================================

class Product(Document):
    """Product Model
    
    Represents a product/service (สินค้า/บริการ).
    Can be placed in scenes/shots for product placement.
    
    Attributes:
        product_id: Unique product identifier
        product_name: Product name
        brand_id: Reference to Brand
        category: Product category
        description: Product description
        image_url: Product image URL
        target_audience: Target audience groups
        age_restriction: Minimum age requirement
        ethical_restrictions: Ethical restrictions list
        tags: Search tags
        is_active: Active status
        created_at: Creation timestamp
        updated_at: Last update timestamp
    
    Example:
        ```python
        product = Product(
            product_name="iPhone 15 Pro",
            brand_id="BRD_20251120120000",
            category=ProductCategory.ELECTRONICS,
            target_audience=[TargetAudience.YOUNG_ADULT, TargetAudience.ADULT],
            age_restriction=13
        )
        await product.insert()
        ```
    """
    
    # Primary fields
    product_id: str = Field(
        default_factory=lambda: f"PRD_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        description="Unique product identifier"
    )
    product_name: str = Field(
        ...,
        description="Product name",
        min_length=2,
        max_length=200
    )
    brand_id: str = Field(
        ...,
        description="Reference to Brand (MongoDB ObjectId or brand_id)",
        min_length=1,
        max_length=100
    )
    
    # Product details
    category: ProductCategory = Field(
        ProductCategory.OTHER,
        description="Product category"
    )
    description: Optional[str] = Field(
        None,
        description="Product description",
        max_length=2000
    )
    image_url: Optional[str] = Field(
        None,
        description="Product image URL"
    )
    
    # Target audience
    target_audience: List[TargetAudience] = Field(
        default_factory=lambda: [TargetAudience.GENERAL],
        description="Target audience groups"
    )
    age_restriction: int = Field(
        default=0,
        description="Minimum age requirement (0 = no restriction)",
        ge=0,
        le=120
    )
    
    # Ethical compliance
    ethical_restrictions: List[str] = Field(
        default_factory=list,
        description="Ethical restrictions (e.g., 'no violence scenes', 'no alcohol with minors')"
    )
    
    # Search and categorization
    tags: List[str] = Field(
        default_factory=list,
        description="Search tags"
    )
    
    # Status
    is_active: bool = Field(
        default=True,
        description="Active status"
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
        name = "placement_products"
        indexes = [
            "product_id",
            "brand_id",
            "category",
            "is_active",
            "created_at",
            ("product_name", "brand_id")  # Compound index
        ]
    
    @validator("age_restriction")
    def validate_age(cls, v):
        """Ensure age is reasonable"""
        if v < 0 or v > 120:
            raise ValueError("Age restriction must be between 0 and 120")
        return v
    
    def __repr__(self):
        return f"<Product {self.product_name} ({self.product_id})>"
    
    def __str__(self):
        return self.product_name


# ============================================================================
# PRODUCT PLACEMENT MODEL
# ============================================================================

class ProductPlacement(Document):
    """Product Placement Model
    
    Represents a product placement in a scene/shot (การวางสินค้าในฉาก).
    Integrated with Step 5: Scene Design in Peace Script workflow.
    
    Attributes:
        placement_id: Unique placement identifier
        product_id: Reference to Product
        scene_id: Reference to Scene (from documents_narrative.py)
        shot_id: Reference to Shot (from documents_narrative.py)
        project_id: Reference to Project (optional)
        
        # Placement configuration
        placement_mode: Placement mode (organic/explicit/background/interactive)
        visibility: Visibility level (subtle/moderate/prominent)
        context_fit: Context fitting (natural/forced/awkward)
        position: Position in frame (foreground/midground/background)
        
        # Timing
        screen_time_seconds: Screen time in seconds
        timestamp_start: Start timestamp in shot (seconds)
        timestamp_end: End timestamp in shot (seconds)
        
        # Character interaction
        character_interaction: Whether character interacts with product
        interacting_character_ids: List of character IDs interacting
        
        # Ethics and compliance
        ethical_score: Ethical compliance score (0-100)
        dhamma_fit: Dhamma/ethics fit (fit/neutral/conflict)
        age_appropriate: Age appropriateness flag
        
        # Context and reasoning
        context_description: Context description
        placement_reason: Reason for placement
        causal_link: Causal link to story/scene
        
        # Analytics tags
        analytic_tag: Analytics tag
        teaching_tag: Teaching tag
        qa_result: QA result
        
        # Notes and metadata
        notes: Additional notes
        is_approved: Approval status
        approved_by: Approver ID
        approved_at: Approval timestamp
        
        # Timestamps
        created_at: Creation timestamp
        updated_at: Last update timestamp
    
    Example:
        ```python
        placement = ProductPlacement(
            product_id="PRD_20251120120000",
            scene_id="68fcace553611223c213415c",
            shot_id="68fcace553611223c213415d",
            placement_mode=PlacementMode.ORGANIC,
            visibility=Visibility.SUBTLE,
            position=Position.BACKGROUND,
            screen_time_seconds=3,
            ethical_score=85,
            dhamma_fit=DhammaFit.FIT
        )
        await placement.insert()
        ```
    """
    
    # Primary fields
    placement_id: str = Field(
        default_factory=lambda: f"PLM_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        description="Unique placement identifier"
    )
    product_id: str = Field(
        ...,
        description="Reference to Product (MongoDB ObjectId or product_id)",
        min_length=1,
        max_length=100
    )
    
    # Scene/Shot references
    scene_id: str = Field(
        ...,
        description="Reference to Scene (MongoDB ObjectId)",
        min_length=1,
        max_length=100
    )
    shot_id: Optional[str] = Field(
        None,
        description="Reference to Shot (MongoDB ObjectId) - optional",
        min_length=1,
        max_length=100
    )
    project_id: Optional[str] = Field(
        None,
        description="Reference to Project (MongoDB ObjectId) - optional",
        min_length=1,
        max_length=100
    )
    
    # Placement configuration
    placement_mode: PlacementMode = Field(
        PlacementMode.ORGANIC,
        description="Placement mode (organic/explicit/background/interactive)"
    )
    visibility: Visibility = Field(
        Visibility.MODERATE,
        description="Visibility level (subtle/moderate/prominent)"
    )
    context_fit: ContextFit = Field(
        ContextFit.NATURAL,
        description="Context fitting (natural/forced/awkward)"
    )
    position: Position = Field(
        Position.BACKGROUND,
        description="Position in frame (foreground/midground/background)"
    )
    
    # Timing
    screen_time_seconds: int = Field(
        default=0,
        description="Screen time in seconds",
        ge=0,
        le=3600
    )
    timestamp_start: Optional[float] = Field(
        None,
        description="Start timestamp in shot (seconds)",
        ge=0
    )
    timestamp_end: Optional[float] = Field(
        None,
        description="End timestamp in shot (seconds)",
        ge=0
    )
    
    # Character interaction
    character_interaction: bool = Field(
        default=False,
        description="Whether character interacts with product"
    )
    interacting_character_ids: List[str] = Field(
        default_factory=list,
        description="List of character IDs interacting with product"
    )
    
    # Ethics and compliance
    ethical_score: int = Field(
        default=50,
        description="Ethical compliance score (0-100)",
        ge=0,
        le=100
    )
    dhamma_fit: DhammaFit = Field(
        DhammaFit.NEUTRAL,
        description="Dhamma/ethics fit (fit/neutral/conflict)"
    )
    age_appropriate: bool = Field(
        default=True,
        description="Age appropriateness flag"
    )
    
    # Context and reasoning
    context_description: Optional[str] = Field(
        None,
        description="Context description",
        max_length=1000
    )
    placement_reason: Optional[str] = Field(
        None,
        description="Reason for placement",
        max_length=1000
    )
    causal_link: Optional[str] = Field(
        None,
        description="Causal link to story/scene/character",
        max_length=1000
    )
    
    # Analytics tags
    analytic_tag: Optional[str] = Field(
        None,
        description="Analytics tag",
        max_length=100
    )
    teaching_tag: Optional[str] = Field(
        None,
        description="Teaching tag",
        max_length=100
    )
    qa_result: Optional[str] = Field(
        None,
        description="QA result",
        max_length=200
    )
    
    # Notes and metadata
    notes: Optional[str] = Field(
        None,
        description="Additional notes",
        max_length=2000
    )
    
    # Approval workflow
    is_approved: bool = Field(
        default=False,
        description="Approval status"
    )
    approved_by: Optional[str] = Field(
        None,
        description="Approver user ID",
        max_length=100
    )
    approved_at: Optional[datetime] = Field(
        None,
        description="Approval timestamp"
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
        name = "placement_placements"
        indexes = [
            "placement_id",
            "product_id",
            "scene_id",
            "shot_id",
            "project_id",
            "is_approved",
            "created_at",
            ("scene_id", "product_id"),  # Compound index
            ("shot_id", "product_id")     # Compound index
        ]
    
    @validator("ethical_score")
    def validate_ethical_score(cls, v):
        """Ensure ethical score is within range"""
        if v < 0 or v > 100:
            raise ValueError("Ethical score must be between 0 and 100")
        return v
    
    @validator("timestamp_end")
    def validate_timestamps(cls, v, values):
        """Ensure end timestamp is after start timestamp"""
        if v is not None and values.get("timestamp_start") is not None:
            if v <= values["timestamp_start"]:
                raise ValueError("End timestamp must be after start timestamp")
        return v
    
    def __repr__(self):
        return f"<ProductPlacement {self.placement_id} in Scene {self.scene_id}>"
    
    def __str__(self):
        return f"Placement {self.placement_id}"
