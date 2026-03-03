"""
Actor Classification System - API Schemas
Request/Response schemas for Actor Management API
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from documents_actors import (
    ActorRoleType,
    ActorImportance,
    CharacterArcType,
    BudgetTier,
    ActorRelationship,
    InternalCharacter,
    ExternalCharacter
)

# Import new STEP 3 models
from models.character_consciousness import Consciousness
from models.character_defilement import Defilement
from models.character_subconscious import Attachment, Taanha
from models.social_status import SocialStatus
from models.character_goals import CharacterGoals
from models.health_history import HealthHistory
from models.character_aspirations import CharacterAspirations


# === Request Schemas ===

class ActorProfileCreate(BaseModel):
    """Schema for creating new actor profile"""
    model_id: str = Field(..., description="Link to DigitalMindModel")
    actor_name: str = Field(..., description="Actor/Character name")
    role_type: ActorRoleType = Field(default=ActorRoleType.SUPPORTING)
    importance: ActorImportance = Field(default=ActorImportance.MEDIUM)
    narrative_functions: List[str] = Field(default_factory=list)
    character_arc_type: CharacterArcType = Field(default=CharacterArcType.FLAT)
    arc_description: Optional[str] = None
    estimated_screen_time: float = Field(default=0.0, ge=0)
    scene_appearances: int = Field(default=0, ge=0)
    dialogue_lines_count: int = Field(default=0, ge=0)
    plot_impact_weight: float = Field(default=5.0, ge=0, le=10)
    emotional_arc_trajectory: List[float] = Field(default_factory=list)
    key_scenes: List[str] = Field(default_factory=list)
    relationships: List[ActorRelationship] = Field(default_factory=list)
    
    # NEW: Character Development
    internal_character: Optional[InternalCharacter] = None
    external_character: Optional[ExternalCharacter] = None
    character_bio: Optional[str] = None
    character_summary: Optional[str] = None
    
    # NEW: STEP 3 Enhancement
    social_status: Optional[SocialStatus] = None
    character_goals: Optional[CharacterGoals] = None
    aspirations: Optional[CharacterAspirations] = None
    sleep_dreams: List[str] = Field(default_factory=list)
    
    casting_priority: int = Field(default=5, ge=1, le=10)
    budget_allocation_tier: BudgetTier = Field(default=BudgetTier.C_TIER)
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "model_id": "peace-mind-001",
                "actor_name": "รินรดา (ตัวเอก)",
                "role_type": "lead",
                "importance": "critical",
                "narrative_functions": ["protagonist", "emotional_anchor"],
                "character_arc_type": "transformation",
                "estimated_screen_time": 85.5,
                "scene_appearances": 42,
                "plot_impact_weight": 9.5,
                "casting_priority": 10,
                "budget_allocation_tier": "A",
                "project_id": "PROJ-001",
                "tags": ["hero", "lead", "female"]
            }
        }


class ActorProfileUpdate(BaseModel):
    """Schema for updating actor profile (all fields optional)"""
    actor_name: Optional[str] = None
    role_type: Optional[ActorRoleType] = None
    importance: Optional[ActorImportance] = None
    narrative_functions: Optional[List[str]] = None
    character_arc_type: Optional[CharacterArcType] = None
    arc_description: Optional[str] = None
    estimated_screen_time: Optional[float] = Field(None, ge=0)
    scene_appearances: Optional[int] = Field(None, ge=0)
    dialogue_lines_count: Optional[int] = Field(None, ge=0)
    plot_impact_weight: Optional[float] = Field(None, ge=0, le=10)
    emotional_arc_trajectory: Optional[List[float]] = None
    key_scenes: Optional[List[str]] = None
    relationships: Optional[List[ActorRelationship]] = None
    
    # NEW: Character Development
    internal_character: Optional[InternalCharacter] = None
    external_character: Optional[ExternalCharacter] = None
    character_bio: Optional[str] = None
    character_summary: Optional[str] = None
    
    # NEW: STEP 3 Enhancement
    social_status: Optional[SocialStatus] = None
    character_goals: Optional[CharacterGoals] = None
    aspirations: Optional[CharacterAspirations] = None
    sleep_dreams: Optional[List[str]] = None
    
    casting_priority: Optional[int] = Field(None, ge=1, le=10)
    budget_allocation_tier: Optional[BudgetTier] = None
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


# === Response Schemas ===

class ActorProfileResponse(BaseModel):
    """Schema for actor profile response"""
    actor_id: str
    model_id: str
    actor_name: str
    role_type: ActorRoleType
    importance: ActorImportance
    narrative_functions: List[str]
    character_arc_type: CharacterArcType
    arc_description: Optional[str] = None
    estimated_screen_time: float
    scene_appearances: int
    dialogue_lines_count: int
    plot_impact_weight: float
    emotional_arc_trajectory: List[float]
    key_scenes: List[str]
    relationships: List[ActorRelationship]
    
    # NEW: Character Development
    internal_character: Optional[InternalCharacter] = None
    external_character: Optional[ExternalCharacter] = None
    character_bio: Optional[str] = None
    character_summary: Optional[str] = None
    
    # NEW: Avatar Design Data
    avatar_data: Optional[Dict] = None
    avatar_thumbnail_url: Optional[str] = None
    
    # NEW: STEP 3 Enhancement
    social_status: Optional[SocialStatus] = None
    character_goals: Optional[CharacterGoals] = None
    aspirations: Optional[CharacterAspirations] = None
    sleep_dreams: List[str]
    
    casting_priority: int
    budget_allocation_tier: BudgetTier
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    tags: List[str]
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "actor_id": "ACT-A1B2C3D4",
                "model_id": "peace-mind-001",
                "actor_name": "รินรดา (ตัวเอก)",
                "role_type": "lead",
                "importance": "critical",
                "narrative_functions": ["protagonist", "emotional_anchor"],
                "character_arc_type": "transformation",
                "estimated_screen_time": 85.5,
                "scene_appearances": 42,
                "dialogue_lines_count": 156,
                "plot_impact_weight": 9.5,
                "casting_priority": 10,
                "budget_allocation_tier": "A",
                "project_id": "PROJ-001"
            }
        }


class ActorListResponse(BaseModel):
    """Schema for list of actors response"""
    actors: List[ActorProfileResponse]
    total: int
    filters_applied: Dict[str, Any] = Field(default_factory=dict)


class ActorStatsResponse(BaseModel):
    """Schema for actor statistics response"""
    total_actors: int
    by_role_type: Dict[str, int]
    by_importance: Dict[str, int]
    by_budget_tier: Dict[str, int]
    total_screen_time: float
    average_screen_time: float
    average_plot_impact: float
    top_actors: List[Dict[str, Any]]


class CastBreakdownResponse(BaseModel):
    """Schema for cast breakdown response"""
    project_id: str
    project_name: Optional[str] = None
    total_actors: int
    breakdown: Dict[str, List[Dict[str, Any]]]
    stats: ActorStatsResponse
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "PROJ-001",
                "project_name": "เงาแค้น",
                "total_actors": 15,
                "breakdown": {
                    "lead": [
                        {
                            "actor_id": "ACT-001",
                            "name": "รินรดา",
                            "importance": "critical",
                            "screen_time": 85.5
                        }
                    ],
                    "supporting": [
                        {
                            "actor_id": "ACT-002",
                            "name": "พี่ชาย",
                            "importance": "high",
                            "screen_time": 45.2
                        }
                    ]
                },
                "stats": {
                    "total_actors": 15,
                    "by_role_type": {"lead": 2, "supporting": 5, "extra": 8},
                    "total_screen_time": 450.5
                }
            }
        }


class RelationshipGraphResponse(BaseModel):
    """Schema for actor relationship graph response"""
    project_id: str
    nodes: List[Dict[str, Any]]  # Actor nodes
    edges: List[Dict[str, Any]]  # Relationship edges
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "PROJ-001",
                "nodes": [
                    {
                        "id": "ACT-001",
                        "name": "รินรดา",
                        "role_type": "lead",
                        "importance": "critical"
                    }
                ],
                "edges": [
                    {
                        "source": "ACT-001",
                        "target": "ACT-002",
                        "type": "rival",
                        "importance": 8.5
                    }
                ]
            }
        }


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    actor_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Actor profile created successfully",
                "actor_id": "ACT-A1B2C3D4"
            }
        }
