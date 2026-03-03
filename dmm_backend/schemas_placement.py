"""
Product Placement Schemas

This module implements Pydantic schemas for Product Placement API.
Used for request/response validation and serialization.

Author: Peace Script Team
Date: 20 November 2025
Version: 1.0
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from documents_placement import (
    ProductCategory,
    PlacementMode,
    Visibility,
    ContextFit,
    DhammaFit,
    Position,
    TargetAudience
)


# ============================================================================
# BRAND SCHEMAS
# ============================================================================

class BrandCreate(BaseModel):
    """Schema for creating a new brand"""
    brand_name: str = Field(..., min_length=2, max_length=200, description="Brand name")
    industry: str = Field(..., max_length=100, description="Industry type")
    description: Optional[str] = Field(None, max_length=2000, description="Brand description")
    logo_url: Optional[str] = Field(None, description="Brand logo URL")
    values: List[str] = Field(default_factory=list, description="Brand values")
    website: Optional[str] = Field(None, description="Brand website")
    contact_email: Optional[str] = Field(None, description="Contact email")


class BrandUpdate(BaseModel):
    """Schema for updating a brand"""
    brand_name: Optional[str] = Field(None, min_length=2, max_length=200)
    industry: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    logo_url: Optional[str] = None
    values: Optional[List[str]] = None
    website: Optional[str] = None
    contact_email: Optional[str] = None
    is_active: Optional[bool] = None


class BrandResponse(BaseModel):
    """Schema for brand response"""
    id: str
    brand_id: str
    brand_name: str
    industry: str
    description: Optional[str]
    logo_url: Optional[str]
    values: List[str]
    website: Optional[str]
    contact_email: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# ============================================================================
# PRODUCT SCHEMAS
# ============================================================================

class ProductCreate(BaseModel):
    """Schema for creating a new product"""
    product_name: str = Field(..., min_length=2, max_length=200, description="Product name")
    brand_id: str = Field(..., description="Reference to Brand")
    category: ProductCategory = Field(ProductCategory.OTHER, description="Product category")
    description: Optional[str] = Field(None, max_length=2000, description="Product description")
    image_url: Optional[str] = Field(None, description="Product image URL")
    target_audience: List[TargetAudience] = Field(
        default_factory=lambda: [TargetAudience.GENERAL],
        description="Target audience groups"
    )
    age_restriction: int = Field(0, ge=0, le=120, description="Minimum age requirement")
    ethical_restrictions: List[str] = Field(default_factory=list, description="Ethical restrictions")
    tags: List[str] = Field(default_factory=list, description="Search tags")


class ProductUpdate(BaseModel):
    """Schema for updating a product"""
    product_name: Optional[str] = Field(None, min_length=2, max_length=200)
    brand_id: Optional[str] = None
    category: Optional[ProductCategory] = None
    description: Optional[str] = Field(None, max_length=2000)
    image_url: Optional[str] = None
    target_audience: Optional[List[TargetAudience]] = None
    age_restriction: Optional[int] = Field(None, ge=0, le=120)
    ethical_restrictions: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    """Schema for product response"""
    id: str
    product_id: str
    product_name: str
    brand_id: str
    category: ProductCategory
    description: Optional[str]
    image_url: Optional[str]
    target_audience: List[TargetAudience]
    age_restriction: int
    ethical_restrictions: List[str]
    tags: List[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# ============================================================================
# PRODUCT PLACEMENT SCHEMAS
# ============================================================================

class ProductPlacementCreate(BaseModel):
    """Schema for creating a new product placement"""
    product_id: str = Field(..., description="Reference to Product")
    scene_id: str = Field(..., description="Reference to Scene")
    shot_id: Optional[str] = Field(None, description="Reference to Shot (optional)")
    project_id: Optional[str] = Field(None, description="Reference to Project (optional)")
    
    # Placement configuration
    placement_mode: PlacementMode = Field(PlacementMode.ORGANIC, description="Placement mode")
    visibility: Visibility = Field(Visibility.MODERATE, description="Visibility level")
    context_fit: ContextFit = Field(ContextFit.NATURAL, description="Context fitting")
    position: Position = Field(Position.BACKGROUND, description="Position in frame")
    
    # Timing
    screen_time_seconds: int = Field(0, ge=0, le=3600, description="Screen time in seconds")
    timestamp_start: Optional[float] = Field(None, ge=0, description="Start timestamp")
    timestamp_end: Optional[float] = Field(None, ge=0, description="End timestamp")
    
    # Character interaction
    character_interaction: bool = Field(False, description="Character interaction flag")
    interacting_character_ids: List[str] = Field(default_factory=list, description="Interacting characters")
    
    # Ethics and compliance
    ethical_score: int = Field(50, ge=0, le=100, description="Ethical score")
    dhamma_fit: DhammaFit = Field(DhammaFit.NEUTRAL, description="Dhamma fit")
    age_appropriate: bool = Field(True, description="Age appropriate flag")
    
    # Context and reasoning
    context_description: Optional[str] = Field(None, max_length=1000, description="Context description")
    placement_reason: Optional[str] = Field(None, max_length=1000, description="Placement reason")
    causal_link: Optional[str] = Field(None, max_length=1000, description="Causal link")
    
    # Tags
    analytic_tag: Optional[str] = Field(None, max_length=100)
    teaching_tag: Optional[str] = Field(None, max_length=100)
    qa_result: Optional[str] = Field(None, max_length=200)
    
    # Notes
    notes: Optional[str] = Field(None, max_length=2000, description="Additional notes")
    
    @validator("timestamp_end")
    def validate_timestamps(cls, v, values):
        """Ensure end timestamp is after start timestamp"""
        if v is not None and values.get("timestamp_start") is not None:
            if v <= values["timestamp_start"]:
                raise ValueError("End timestamp must be after start timestamp")
        return v


class ProductPlacementUpdate(BaseModel):
    """Schema for updating a product placement"""
    product_id: Optional[str] = None
    scene_id: Optional[str] = None
    shot_id: Optional[str] = None
    project_id: Optional[str] = None
    
    placement_mode: Optional[PlacementMode] = None
    visibility: Optional[Visibility] = None
    context_fit: Optional[ContextFit] = None
    position: Optional[Position] = None
    
    screen_time_seconds: Optional[int] = Field(None, ge=0, le=3600)
    timestamp_start: Optional[float] = Field(None, ge=0)
    timestamp_end: Optional[float] = Field(None, ge=0)
    
    character_interaction: Optional[bool] = None
    interacting_character_ids: Optional[List[str]] = None
    
    ethical_score: Optional[int] = Field(None, ge=0, le=100)
    dhamma_fit: Optional[DhammaFit] = None
    age_appropriate: Optional[bool] = None
    
    context_description: Optional[str] = Field(None, max_length=1000)
    placement_reason: Optional[str] = Field(None, max_length=1000)
    causal_link: Optional[str] = Field(None, max_length=1000)
    
    analytic_tag: Optional[str] = Field(None, max_length=100)
    teaching_tag: Optional[str] = Field(None, max_length=100)
    qa_result: Optional[str] = Field(None, max_length=200)
    
    notes: Optional[str] = Field(None, max_length=2000)
    
    is_approved: Optional[bool] = None
    approved_by: Optional[str] = None


class ProductPlacementResponse(BaseModel):
    """Schema for product placement response"""
    id: str
    placement_id: str
    product_id: str
    scene_id: str
    shot_id: Optional[str]
    project_id: Optional[str]
    
    placement_mode: PlacementMode
    visibility: Visibility
    context_fit: ContextFit
    position: Position
    
    screen_time_seconds: int
    timestamp_start: Optional[float]
    timestamp_end: Optional[float]
    
    character_interaction: bool
    interacting_character_ids: List[str]
    
    ethical_score: int
    dhamma_fit: DhammaFit
    age_appropriate: bool
    
    context_description: Optional[str]
    placement_reason: Optional[str]
    causal_link: Optional[str]
    
    analytic_tag: Optional[str]
    teaching_tag: Optional[str]
    qa_result: Optional[str]
    
    notes: Optional[str]
    
    is_approved: bool
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# ============================================================================
# ANALYTICS SCHEMAS
# ============================================================================

class PlacementAnalytics(BaseModel):
    """Schema for placement analytics response"""
    total_placements: int = Field(..., description="Total number of placements")
    total_products: int = Field(..., description="Total unique products")
    total_brands: int = Field(..., description="Total unique brands")
    
    # By mode
    by_placement_mode: dict = Field(default_factory=dict, description="Placements by mode")
    by_visibility: dict = Field(default_factory=dict, description="Placements by visibility")
    by_position: dict = Field(default_factory=dict, description="Placements by position")
    
    # Ethics compliance
    avg_ethical_score: float = Field(..., description="Average ethical score")
    dhamma_fit_distribution: dict = Field(default_factory=dict, description="Dhamma fit distribution")
    approval_rate: float = Field(..., description="Approval rate percentage")
    
    # Screen time
    total_screen_time_seconds: int = Field(..., description="Total screen time")
    avg_screen_time_seconds: float = Field(..., description="Average screen time per placement")
    
    # Top products/brands
    top_products: List[dict] = Field(default_factory=list, description="Top 10 products by placement count")
    top_brands: List[dict] = Field(default_factory=list, description="Top 10 brands by placement count")


class EthicsAuditRequest(BaseModel):
    """Schema for ethics audit request"""
    placement_id: str = Field(..., description="Placement ID to audit")


class EthicsAuditResponse(BaseModel):
    """Schema for ethics audit response"""
    placement_id: str
    ethical_score: int
    dhamma_fit: DhammaFit
    age_appropriate: bool
    warnings: List[str] = Field(default_factory=list, description="Warning messages")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    audit_passed: bool = Field(..., description="Overall audit result")
    audit_timestamp: datetime = Field(default_factory=datetime.utcnow)
