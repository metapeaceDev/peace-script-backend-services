from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

from beanie import Document
from pydantic import BaseModel, Field
from pymongo import IndexModel, ASCENDING, DESCENDING


class DreamTag(str, Enum):
    """
    Validated dream tags for consistent categorization
    
    Dream Types (6 main categories):
    - NIGHTMARE: Bad dreams from fears/aversion (ฝันร้าย)
    - LUCID: Conscious dreaming (ฝันรู้ตัว)
    - PROPHETIC: Predictive/spiritual dreams (ฝันนิมิต)
    - WISHFUL: Dreams of desires (ฝันปรารถนา)
    - RECURRING: Repeated dreams (ฝันซ้ำ)
    - SYMBOLIC: Dreams requiring interpretation (ฝันสัญลักษณ์)
    
    Common Themes:
    - FLYING, CHASE, FALLING, DEATH, EXAM, etc.
    
    Buddhist Context:
    - SPIRITUAL, PAST_LIFE, KARMA_RELATED, etc.
    """
    # === Main Dream Types (6 categories) ===
    NIGHTMARE = "nightmare"
    LUCID = "lucid"
    PROPHETIC = "prophetic"
    WISHFUL = "wishful"
    RECURRING = "recurring"
    SYMBOLIC = "symbolic"
    
    # === Common Dream Themes ===
    FLYING = "flying"
    CHASE = "chase"
    FALLING = "falling"
    DEATH = "death"
    EXAM = "exam"
    EXAM_FAILURE = "exam_failure"
    LATE = "late"
    LOST = "lost"
    NAKED = "naked"
    TEETH_FALLING = "teeth_falling"
    
    # === Relationship Themes ===
    CHILD_RELATED = "child_related"
    CHILD_SUCCESS = "child_success"
    CHILD_FAILURE = "child_failure"
    PARENT_RELATED = "parent_related"
    FAMILY = "family"
    LOVE = "love"
    BETRAYAL = "betrayal"
    
    # === Buddhist/Spiritual Themes ===
    SPIRITUAL = "spiritual"
    PAST_LIFE = "past_life"
    KARMA_RELATED = "karma_related"
    DHAMMA_TEACHING = "dhamma_teaching"
    MEDITATION = "meditation"
    TEMPLE = "temple"
    MONK = "monk"
    BUDDHA = "buddha"
    LOTUS = "lotus"
    
    # === Emotional States ===
    POSITIVE = "positive"
    NEGATIVE = "negative"
    PEACEFUL = "peaceful"
    ANXIOUS = "anxious"
    JOYFUL = "joyful"
    SCARY = "scary"
    
    # === Location-based ===
    LOCATION_SPECIFIC = "location_specific"
    HOME = "home"
    SCHOOL = "school"
    WORK = "work"
    NATURE = "nature"
    
    # === Special Categories ===
    TRANSFORMATION = "transformation"
    HEALING = "healing"
    WARNING = "warning"
    GUIDANCE = "guidance"
    
    # === Financial/Material ===
    FINANCIAL = "financial"
    WEALTH = "wealth"
    POVERTY = "poverty"
    
    # === Other ===
    STRANGE = "strange"
    VIVID = "vivid"
    FRAGMENT = "fragment"


class DreamJournal(Document):
    model_id: Optional[str] = None
    date: datetime = Field(default_factory=datetime.utcnow)
    dream_text: str
    tags: List[DreamTag] = Field(
        default_factory=list,
        description="Validated dream tags from DreamTag enum"
    )
    emotion_score: Optional[float] = Field(
        None,
        ge=-100,
        le=100,
        description="Emotion score from -100 (very negative) to +100 (very positive)"
    )
    ai_summary: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "dream_journals"
        # Optimize common queries: filter by model_id and paginate by _id desc
        indexes = [
            IndexModel([("model_id", ASCENDING), ("_id", DESCENDING)], name="dj_model_id__id_desc"),
            IndexModel([("date", DESCENDING)], name="dj_date_desc"),
        ]
    
    # Tolerate legacy/extra fields and missing optional fields
    model_config = {
        "extra": "allow",
        "populate_by_name": True,
    }


class SimulationEvent(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    type: str
    payload: Dict[str, Any] = Field(default_factory=dict)


class SimulationTimeline(Document):
    model_id: Optional[str] = None
    simulation_id: Optional[str] = None
    timeline_type: str = "physical"
    events: List[SimulationEvent] = Field(default_factory=list)
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    playback_mode: str = "real"
    meta: Dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "simulation_timelines"
        indexes = [
            IndexModel([("model_id", ASCENDING), ("_id", DESCENDING)], name="st_model_id__id_desc"),
            IndexModel([("model_id", ASCENDING), ("simulation_id", ASCENDING), ("_id", DESCENDING)], name="st_model_sim__id_desc"),
            IndexModel([("simulation_id", ASCENDING)], name="st_simulation_id"),
        ]
    # Allow extra fields in legacy docs
    model_config = {
        "extra": "allow",
        "populate_by_name": True,
    }


# Camera Director Models
class CameraPosition(BaseModel):
    """3D position for camera"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


class CameraRotation(BaseModel):
    """3D rotation for camera (Euler angles)"""
    pitch: float = 0.0  # X-axis rotation
    yaw: float = 0.0    # Y-axis rotation
    roll: float = 0.0   # Z-axis rotation


class LensSettings(BaseModel):
    """Camera lens configuration"""
    focal_length_mm: int = 50  # 8-600mm range
    aperture: str = "f/2.8"   # e.g., "f/1.8", "f/2.8", "f/5.6"
    lens_type: str = "standard"  # wide, standard, portrait, telephoto, macro, fisheye


class AIMetadata(BaseModel):
    """AI-generated suggestions metadata"""
    suggested_angle: Optional[str] = None  # eye_level, high, low, dutch, birds_eye, worms_eye, pov, over_shoulder
    suggested_lens: Optional[Dict[str, Any]] = None
    suggested_movement: Optional[str] = None  # static, pan, tilt, dolly, crane, handheld, etc.
    suggested_shot_type: Optional[str] = None  # close_up, medium, full, wide, etc.
    confidence: float = 0.0  # 0.0-1.0
    reasoning: Optional[str] = None


class CameraPlan(Document):
    """Complete camera plan for a simulation event"""
    # Core identification
    plan_id: Optional[str] = None
    simulation_id: str
    event_id: str
    timeline_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Camera position & orientation
    position: CameraPosition = Field(default_factory=CameraPosition)
    rotation: CameraRotation = Field(default_factory=CameraRotation)
    target_position: Optional[CameraPosition] = None  # Look-at target
    
    # Lens settings
    lens_settings: LensSettings = Field(default_factory=LensSettings)
    
    # Camera movement
    camera_angle: str = "eye_level"  # eye_level, high, low, dutch, birds_eye, worms_eye, pov, over_shoulder
    movement_type: str = "static"  # static, pan, tilt, dolly, crane, handheld, steadicam, drone, zoom, rack_focus, whip_pan, orbit
    movement_path: List[CameraPosition] = Field(default_factory=list)
    movement_duration_seconds: float = 0.0
    
    # Shot composition
    shot_type: str = "medium"  # extreme_close_up, close_up, medium_close_up, medium, medium_wide, full, wide, extreme_wide, establishing
    framing: Optional[str] = None  # rule_of_thirds, centered, golden_ratio, etc.
    composition_notes: Optional[str] = None
    
    # Cut & transition
    cut_type: str = "cut"  # cut, fade, dissolve, wipe, zoom_transition, match_cut, jump_cut
    transition_duration_seconds: float = 0.0
    
    # Context for AI suggestions
    context: Dict[str, Any] = Field(default_factory=dict)  # emotion, intensity, dhamma_reference, etc.
    
    # AI metadata
    ai_metadata: Optional[AIMetadata] = None
    ai_generated: bool = False
    
    # Feedback & learning
    feedback: Optional[str] = None  # "good", "not_good", "modify"
    feedback_notes: Optional[str] = None
    user_corrections: Optional[Dict[str, Any]] = None
    
    # Preset & reference
    preset_name: Optional[str] = None
    reference_plan_id: Optional[str] = None
    
    # Additional metadata
    meta: Dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "camera_plans"
        indexes = [
            IndexModel([("simulation_id", ASCENDING), ("_id", DESCENDING)], name="cp_sim_id_desc"),
            IndexModel([("event_id", ASCENDING)], name="cp_event_id"),
            IndexModel([("preset_name", ASCENDING)], name="cp_preset_name"),
            IndexModel([("ai_generated", ASCENDING)], name="cp_ai_generated"),
        ]
    
    model_config = {
        "extra": "allow",
        "populate_by_name": True,
    }


class AIFeedback(Document):
    """AI feedback for learning from user corrections"""
    feedback_id: Optional[str] = None
    plan_id: str  # Reference to CameraPlan
    simulation_id: str
    event_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Feedback type
    feedback_type: str  # "good", "not_good", "modify"
    
    # Original AI suggestion
    original_suggestion: Dict[str, Any] = Field(default_factory=dict)
    
    # User correction (if feedback_type == "modify")
    correction: Optional[Dict[str, Any]] = None
    
    # Context
    context: Dict[str, Any] = Field(default_factory=dict)
    
    # Learning signals
    accepted: bool = False  # True if user accepted suggestion
    should_reinforce: bool = False  # True if this pattern should be reinforced
    should_penalize: bool = False  # True if this pattern should be avoided
    
    # Reasoning
    reasoning: Optional[str] = None
    
    # Metadata
    meta: Dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "ai_feedback"
        indexes = [
            IndexModel([("plan_id", ASCENDING)], name="af_plan_id"),
            IndexModel([("simulation_id", ASCENDING), ("_id", DESCENDING)], name="af_sim_id_desc"),
            IndexModel([("feedback_type", ASCENDING)], name="af_feedback_type"),
            IndexModel([("accepted", ASCENDING)], name="af_accepted"),
        ]
    
    model_config = {
        "extra": "allow",
        "populate_by_name": True,
    }


# ============================================================
# PHASE 2: CAMERA FEEDBACK SYSTEM
# ============================================================

class CameraFeedback(Document):
    """
    Phase 2 Feature 1: Camera Feedback System
    Collects user feedback on AI camera suggestions for learning and improvement
    """
    # Core identification
    feedback_id: Optional[str] = Field(default=None, description="Unique feedback identifier")
    user_id: Optional[str] = Field(default=None, description="User who provided feedback")
    suggestion_id: str = Field(description="ID of the camera suggestion being rated")
    
    # Original suggestion context
    emotion: str = Field(description="Emotion context (e.g., 'compassion', 'anger', 'peace')")
    intensity: str = Field(description="Intensity level: 'low', 'medium', 'high'")
    suggested_angle: str = Field(description="AI-suggested camera angle")
    suggested_lens: str = Field(description="AI-suggested lens type")
    suggested_shot_type: str = Field(description="AI-suggested shot type")
    suggested_movement: str = Field(description="AI-suggested movement type")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="AI confidence score (0.0-1.0)")
    
    # User feedback
    accepted: bool = Field(default=False, description="Did user accept the suggestion?")
    rating: Optional[int] = Field(default=None, ge=1, le=5, description="User rating (1-5 stars)")
    quick_feedback: Optional[str] = Field(default=None, description="Quick feedback: 'thumbs_up', 'thumbs_down', 'neutral'")
    notes: Optional[str] = Field(default=None, description="Additional user notes/comments")
    tags: List[str] = Field(default_factory=list, description="User-added tags for categorization")
    
    # User corrections (if any)
    actual_angle: Optional[str] = Field(default=None, description="User's chosen camera angle (if different)")
    actual_lens: Optional[str] = Field(default=None, description="User's chosen lens (if different)")
    actual_shot_type: Optional[str] = Field(default=None, description="User's chosen shot type (if different)")
    actual_movement: Optional[str] = Field(default=None, description="User's chosen movement (if different)")
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When feedback was submitted")
    session_id: Optional[str] = Field(default=None, description="Session ID for grouping feedback")
    device_type: Optional[str] = Field(default=None, description="Device used: 'desktop', 'mobile', 'tablet'")
    
    # Additional context
    scene_description: Optional[str] = Field(default=None, description="Brief scene description")
    dhamma_context: Optional[str] = Field(default=None, description="Dhamma teaching context if applicable")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Settings:
        name = "camera_feedback"
        indexes = [
            # Query by user to show their feedback history
            IndexModel([("user_id", ASCENDING), ("timestamp", DESCENDING)], name="cf_user_time_desc"),
            # Filter by emotion to analyze patterns
            IndexModel([("emotion", ASCENDING), ("accepted", ASCENDING)], name="cf_emotion_accepted"),
            # Filter by rating for quality analysis
            IndexModel([("rating", DESCENDING), ("timestamp", DESCENDING)], name="cf_rating_time_desc"),
            # Find accepted suggestions for learning
            IndexModel([("accepted", ASCENDING), ("confidence", DESCENDING)], name="cf_accepted_confidence"),
            # Compound index for detailed analytics
            IndexModel([("emotion", ASCENDING), ("intensity", ASCENDING), ("accepted", ASCENDING)], name="cf_analytics"),
        ]
    
    model_config = {
        "extra": "allow",
        "populate_by_name": True,
    }


# =====================================================================
# Character State Snapshot - For Shot-by-Shot Simulation
# =====================================================================

class CharacterStateSnapshot(BaseModel):
    """
    Snapshot of character state at a specific shot in scene
    Used for shot-by-shot simulation workflow
    """
    shot_id: str = Field(..., description="Shot ID this state belongs to")
    scene_id: str = Field(..., description="Scene ID")
    actor_id: str = Field(..., description="Actor/Character ID")
    shot_number: int = Field(..., description="Shot number in scene (1-based)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When state was captured")
    
    # Character State (from MindState/CoreProfile)
    state: Dict[str, Any] = Field(
        default_factory=dict,
        description="Complete character state snapshot"
    )
    # state structure:
    # {
    #   "virtue": {"sila": 5.0, "samadhi": 4.5, "panna": 4.0},
    #   "emotion": "calm",
    #   "consciousness_state": "neutral",
    #   "active_hindrances": {},
    #   "kusala_count": 10,
    #   "akusala_count": 5
    # }
    
    # Simulation Results
    actions_taken: List[str] = Field(
        default_factory=list,
        description="Actions character performed in this shot"
    )
    dialogue_spoken: str = Field(
        default="",
        description="Dialogue character spoke in this shot"
    )
    state_changes: List[str] = Field(
        default_factory=list,
        description="State changes that occurred (for display)"
    )
    
    # Metadata
    simulation_confidence: float = Field(
        default=0.85,
        ge=0.0,
        le=1.0,
        description="Confidence in simulation results"
    )
    simulation_reasoning: str = Field(
        default="",
        description="Why simulation made these choices"
    )
    
    model_config = {
        "extra": "allow",
        "populate_by_name": True,
    }

