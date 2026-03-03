from datetime import datetime
from typing import Any, Dict, List, Optional

from beanie import Document
from pydantic import BaseModel, Field
from pydantic import model_validator

# Import Core Profile models from dedicated module
from core_profile_models import CoreProfile

# --- Re-usable Pydantic Models for nesting --- #

class StimulusObject(BaseModel):
    type: str
    source: str
    intensity: float
    details: str

class ConflictAnalysis(BaseModel):
    initial_kilesa_force: float
    final_kilesa_force: float
    parami_force: float
    sati_intervened: bool
    panna_intervened: bool

class ReactionOutcome(BaseModel):
    resulting_citta: str
    is_wholesome: bool
    conflict_analysis: ConflictAnalysis

class ProfileChange(BaseModel):
    target: str
    change: str

class Consequence(BaseModel):
    new_kamma_id: Optional[str] = None
    profile_changes: List[ProfileChange]

# --- Beanie Document Models --- #

class DigitalMindModel(Document):
    model_id: str
    name: str
    status_label: str
    overall_level: int
    level_progress_percent: float = 0.0
    image_url: str
    avatar_image_id: Optional[str] = Field(default=None, description="ID of generated image set as profile avatar")
    core_state: Dict[str, Any]
    conscious_profile: Dict[str, Any]
    kamma_profile: Dict[str, Any]
    
    # Core Profile (NEW: Full Pydantic model support)
    core_profile_obj: Optional[CoreProfile] = Field(default=None, alias="CoreProfile")
    core_profile: Optional[Dict[str, Any]] = Field(default=None)  # Legacy dict format
    
    # System metadata
    version: str = Field(default="14.0")
    SystemStatus: str = Field(default="Active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "digital_mind_models"

    # Allow unknown fields (e.g., core_profile) in test/seed payloads
    model_config = {"extra": "allow", "populate_by_name": True}

    @model_validator(mode="before")
    @classmethod
    def _ensure_defaults(cls, data):
        if isinstance(data, dict):
            data.setdefault("level_progress_percent", 0.0)
            
            # Auto-convert dict core_profile to CoreProfile model
            if "core_profile" in data and not data.get("core_profile_obj"):
                try:
                    from core_profile_models import CoreProfile as CP
                    data["core_profile_obj"] = CP(**data["core_profile"])
                except Exception:
                    pass  # Keep dict format if conversion fails
                    
            # Sync CoreProfile to dict format for backward compatibility
            if data.get("core_profile_obj") and not data.get("core_profile"):
                data["core_profile"] = data["core_profile_obj"].model_dump()
                
        return data
    
    def get_core_profile(self) -> CoreProfile:
        """Get CoreProfile as Pydantic object, creating default if not exists"""
        # If we have Pydantic object, return it
        if self.core_profile_obj:
            return self.core_profile_obj
        
        # Try to create from dict
        if self.core_profile:
            try:
                from core_profile_models import CoreProfile as CP
                self.core_profile_obj = CP(**self.core_profile)
                return self.core_profile_obj
            except Exception as e:
                print(f"Warning: Failed to convert core_profile dict to object: {e} - documents.py:102")
        
        # Create default CoreProfile
        from core_profile_models import CoreProfile as CP
        self.core_profile_obj = CP()
        return self.core_profile_obj
    
    def update_core_profile(self, updates: Dict[str, Any]):
        """Update CoreProfile and sync to dict format"""
        profile = self.get_core_profile()
        
        # Apply updates to Pydantic model
        for key, value in updates.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        # Sync to dict format
        self.core_profile = profile.model_dump()
        self.core_profile_obj = profile
        self.updated_at = datetime.utcnow()
    
    def get_spiritual_score(self) -> float:
        """Get overall spiritual development score"""
        profile = self.get_core_profile()
        return profile.get_overall_spiritual_score()
    
    def is_noble_being(self) -> bool:
        """Check if model has attained noble status"""
        profile = self.get_core_profile()
        return profile.is_noble()
    
    async def break_fetter(self, fetter_name: str) -> bool:
        """Break a fetter and save"""
        profile = self.get_core_profile()
        if profile.break_fetter(fetter_name):
            self.update_core_profile({})  # Sync changes
            await self.save()
            return True
        return False

class KammaLogEntry(Document):
    model_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_type: str
    description: str
    impact_level: int
    context: Dict[str, Any]

    class Settings:
        name = "kamma_logs"

class TrainingLog(Document):
    model_id: str
    training_type: str
    date: datetime = Field(default_factory=datetime.utcnow)
    details: Dict[str, Any]

    class Settings:
        name = "training_logs"


# ============================================================================
# Phase 2: Authentication & User Management (Added: 22 Oct 2568)
# ============================================================================
# Authentication - User Model (FastAPI-Users Integration)
# ============================================================================

# User model is now in auth/models.py for FastAPI-Users compatibility
# Import it here for backward compatibility
from auth.models import User

# ============================================================================
# Phase 1: Database Integration Models (Added: 22 Oct 2568)
# ============================================================================

class MindState(Document):
    """
    User's Mental and Spiritual State
    Tracks the moment-to-moment state of a user's mind for simulation purposes
    """
    user_id: str = Field(..., description="User identifier")
    
    # Virtue Levels (Sīla, Samādhi, Paññā)
    sila: float = Field(default=5.0, ge=0, le=10, description="Moral conduct level")
    samadhi: float = Field(default=4.0, ge=0, le=10, description="Concentration level")
    panna: float = Field(default=4.0, ge=0, le=10, description="Wisdom level")
    sati_strength: float = Field(default=5.0, ge=0, le=10, description="Mindfulness strength")
    
    # Anusaya (Latent Tendencies) - 7 types
    current_anusaya: Dict[str, float] = Field(
        default_factory=lambda: {
            "lobha": 3.0,      # Greed
            "dosa": 2.5,       # Aversion
            "moha": 3.5,       # Delusion
            "mana": 2.0,       # Conceit
            "ditthi": 2.0,     # Wrong view
            "vicikiccha": 2.5, # Doubt
            "thina": 3.0       # Sloth
        },
        description="Current levels of latent tendencies"
    )
    
    # Daily Counters
    kusala_count_today: int = Field(default=0, description="Wholesome actions today")
    akusala_count_today: int = Field(default=0, description="Unwholesome actions today")
    kusala_count_total: int = Field(default=0, description="Total wholesome actions")
    akusala_count_total: int = Field(default=0, description="Total unwholesome actions")
    
    # Active State
    active_hindrances: Dict[str, float] = Field(
        default_factory=dict,
        description="Currently active mental hindrances (Nīvaraṇa)"
    )
    current_bhumi: str = Field(
        default="puthujjana",
        description="Current spiritual stage (puthujjana, sotapanna, etc.)"
    )
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_simulation_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp of last simulation"
    )
    
    class Settings:
        name = "mind_states"
        indexes = [
            "user_id",
            "updated_at",
            [("user_id", 1), ("updated_at", -1)]  # Compound index
        ]
    
    def reset_daily_counters(self):
        """Reset daily counters (call at midnight)"""
        self.kusala_count_today = 0
        self.akusala_count_today = 0
        self.updated_at = datetime.utcnow()
    
    def get_virtue_level(self) -> Dict[str, float]:
        """Get virtue levels as dict"""
        return {
            "sila": self.sila,
            "samadhi": self.samadhi,
            "panna": self.panna
        }
    
    def to_simulation_state(self) -> Dict[str, Any]:
        """Convert to format expected by simulation engine"""
        return {
            "user_id": self.user_id,
            "sila": self.sila,
            "samadhi": self.samadhi,
            "panna": self.panna,
            "sati_strength": self.sati_strength,
            "current_anusaya": self.current_anusaya,
            "kusala_count_today": self.kusala_count_today,
            "akusala_count_today": self.akusala_count_today,
            "VirtueLevel": self.get_virtue_level(),
            "total_kusala_count": self.kusala_count_total,
            "total_akusala_count": self.akusala_count_total,
            "active_hindrances": self.active_hindrances
        }


class SimulationHistory(Document):
    """
    Complete Record of User's Simulation Sessions
    Stores all simulation attempts with choices, results, and learning
    """
    simulation_id: str = Field(..., description="Unique simulation identifier")
    user_id: str = Field(..., description="User who ran simulation")
    scenario_id: str = Field(..., description="Scenario used")
    
    # Choice Information
    choice_index: int = Field(..., ge=0, description="Index of choice selected (0-2)")
    choice_id: str = Field(..., description="Choice ID from scenario")
    choice_type: str = Field(..., description="kusala, akusala, or neutral")
    choice_label: str = Field(..., description="Short description of choice")
    
    # Simulation Results
    citta_generated: str = Field(..., description="Type of consciousness that arose")
    kamma_generated: float = Field(default=0.0, description="Karma potency generated")
    sati_intervened: bool = Field(default=False, description="Did mindfulness intervene")
    
    # State Changes
    state_before: Dict[str, Any] = Field(
        default_factory=dict,
        description="Mental state before simulation"
    )
    state_after: Dict[str, Any] = Field(
        default_factory=dict,
        description="Mental state after simulation"
    )
    state_changes: List[str] = Field(
        default_factory=list,
        description="List of changes that occurred"
    )
    
    # Consequences (stored as simple descriptions)
    immediate_consequences: str = Field(default="", description="Immediate effect")
    short_term_consequences: str = Field(default="", description="Short-term effect")
    long_term_consequences: str = Field(default="", description="Long-term effect")
    
    # Learning & Wisdom
    wisdom_gained: str = Field(default="", description="Wisdom message for user")
    practice_tip: str = Field(default="", description="Practice suggestion")
    scriptural_reference: Optional[str] = Field(
        default=None,
        description="Reference to Buddhist scripture"
    )
    
    # User Reflection
    user_reflection: Optional[str] = Field(
        default=None,
        description="User's own reflection on their choice"
    )
    
    # Quality Metrics
    difficulty_level: float = Field(default=5.0, ge=0, le=10)
    user_satisfaction: Optional[int] = Field(
        default=None,
        ge=1,
        le=5,
        description="User rating (1-5 stars)"
    )
    
    # Timestamps
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When simulation occurred"
    )
    
    class Settings:
        name = "simulation_history"
        indexes = [
            "user_id",
            "scenario_id",
            "timestamp",
            "choice_type",
            [("user_id", 1), ("timestamp", -1)],  # User's history chronologically
            [("scenario_id", 1), ("timestamp", -1)]  # Scenario popularity
        ]
    
    def is_kusala_choice(self) -> bool:
        """Check if this was a wholesome choice"""
        return self.choice_type == "kusala"
    
    def is_akusala_choice(self) -> bool:
        """Check if this was an unwholesome choice"""
        return self.choice_type == "akusala"
    
    def get_choice_quality_score(self) -> float:
        """Calculate quality score (0-10) based on choice type"""
        if self.is_kusala_choice():
            return 8.0 + (self.difficulty_level / 5.0)  # 8-10 range
        elif self.is_akusala_choice():
            return 2.0 - (self.difficulty_level / 10.0)  # 1-2 range
        else:
            return 5.0  # Neutral


class CittaMomentRecord(Document):
    """
    Record of a single citta (consciousness) moment
    Used for tracking mental state evolution in characters
    """
    model_id: str = Field(..., description="Character ID")
    citta_type: str = Field(..., description="Type of consciousness (e.g., lobha-mula-citta-1)")
    category: str = Field(..., description="Category: Kusala/Akusala/Abyakata")
    root: Optional[str] = Field(None, description="Root: lobha/dosa/moha or alobha/adosa/amoha")
    
    # Vedanā (feeling)
    feeling: str = Field(..., description="Vedanā: sukha/dukkha/upekkha")
    intensity: float = Field(5.0, ge=0, le=10, description="Intensity (0-10)")
    
    # Cetasikas (mental factors)
    cetasikas: List[str] = Field(default_factory=list, description="List of accompanying cetasikas")
    
    # Context
    prompted: bool = Field(False, description="Whether prompted by conditions")
    accompanied_by_knowledge: bool = Field(False, description="With wisdom (ñāṇa-sampayutta)")
    duration_ms: int = Field(17, description="Duration in milliseconds (typically 17ms)")
    
    # Metadata
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When this moment arose")
    
    # Kamma tracking
    is_javana: bool = Field(False, description="Whether this is a javana (impulsion) moment")
    kamma_created: bool = Field(False, description="Whether kamma was created")
    kamma_log_id: Optional[str] = Field(None, description="Reference to KammaLogEntry if created")
    
    class Settings:
        name = "citta_moment_records"
        indexes = [
            "model_id",
            "timestamp",
            "category",
            "citta_type",
            [("model_id", 1), ("timestamp", -1)],  # Character history
            [("category", 1), ("timestamp", -1)]  # By category
        ]


class VithiRecord(Document):
    """
    Record of a cognitive process (citta-vīthi)
    Tracks the full sequence of consciousness moments
    """
    model_id: str = Field(..., description="Character ID")
    vithi_type: str = Field(..., description="Type of vithi process")
    
    # Process stages
    atita_bhavanga_count: int = Field(default=1, description="Past life-continuum moments")
    bhavanga_calana: bool = Field(default=True, description="Vibration of life-continuum")
    bhavanga_upaccheda: bool = Field(default=True, description="Arrest of life-continuum")
    
    # Main sequence
    pancadvaravajjana: Optional[Dict[str, Any]] = Field(None, description="Five-door adverting")
    cakkhu_vinnana: Optional[Dict[str, Any]] = Field(None, description="Eye consciousness")
    sampaticchana: Optional[Dict[str, Any]] = Field(None, description="Receiving")
    santirana: Optional[Dict[str, Any]] = Field(None, description="Investigating")
    votthapana: Optional[Dict[str, Any]] = Field(None, description="Determining")
    javana_sequence: List[Dict[str, Any]] = Field(default_factory=list, description="Impulsion moments (7)")
    tadalambana_sequence: List[Dict[str, Any]] = Field(default_factory=list, description="Registration moments (2)")
    
    # Results
    javana_quality: str = Field(..., description="Quality: kusala/akusala/kiriya")
    kamma_potency: float = Field(0.0, description="Kamma potency (0-10)")
    object_clarity: float = Field(5.0, description="Object clarity (0-10)")
    
    # Duration
    total_moments: int = Field(..., description="Total citta moments in vithi")
    duration_ms: int = Field(..., description="Total duration in milliseconds")
    
    # Context
    sensory_input: Optional[Dict[str, Any]] = Field(None, description="Initial sensory input")
    resulting_state: Optional[Dict[str, Any]] = Field(None, description="Mind state after vithi")
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When vithi occurred")
    
    class Settings:
        name = "vithi_records"
        indexes = [
            "model_id",
            "timestamp",
            "javana_quality",
            [("model_id", 1), ("timestamp", -1)],
            [("javana_quality", 1), ("timestamp", -1)]
        ]


class MindState(Document):
    """
    User's mental and spiritual state
    Tracks Sīla, Samādhi, Paññā levels and Anusaya (latent tendencies)
    Based on Theravada Buddhist psychology
    """
    user_id: str = Field(..., description="User identifier")
    
    # Three Training Pillars (Sīla, Samādhi, Paññā)
    sila: float = Field(default=5.0, ge=0, le=10, description="Virtue/Morality level (0-10)")
    samadhi: float = Field(default=4.0, ge=0, le=10, description="Concentration/Mental discipline (0-10)")
    panna: float = Field(default=4.0, ge=0, le=10, description="Wisdom/Insight (0-10)")
    sati_strength: float = Field(default=5.0, ge=0, le=10, description="Mindfulness strength (0-10)")
    
    # Anusaya - Latent Tendencies (7 types)
    current_anusaya: Dict[str, float] = Field(
        default_factory=dict,
        description="Latent tendencies: lobha, dosa, moha, mana, ditthi, vicikiccha, uddhacca"
    )
    # Example: {"lobha": 3.0, "dosa": 2.5, "moha": 3.5, "mana": 2.0, ...}
    
    # Daily Kusala/Akusala Counters
    kusala_count_today: int = Field(default=0, description="Wholesome actions count today")
    akusala_count_today: int = Field(default=0, description="Unwholesome actions count today")
    kusala_count_total: int = Field(default=0, description="Total wholesome actions")
    akusala_count_total: int = Field(default=0, description="Total unwholesome actions")
    
    # Five Hindrances (Nīvaraṇa) - Active State
    active_hindrances: Dict[str, float] = Field(
        default_factory=dict,
        description="Active hindrances: kamacchanda, byapada, thina-middha, uddhacca-kukkucca, vicikiccha"
    )
    
    # Spiritual Development Level
    current_bhumi: str = Field(
        default="puthujjana",
        description="Current spiritual stage: puthujjana, sotapanna, sakadagami, anagami, arahant"
    )
    
    # Progress Tracking
    days_of_practice: int = Field(default=0, description="Days of continuous practice")
    meditation_minutes_total: int = Field(default=0, description="Total meditation time in minutes")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Record creation time")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update time")
    last_simulation_at: Optional[datetime] = Field(None, description="Last simulation timestamp")
    last_reset_at: Optional[datetime] = Field(None, description="Last daily counter reset")
    
    class Settings:
        name = "mind_states"
        indexes = [
            "user_id",
            "updated_at",
            "current_bhumi",
            [("user_id", 1), ("updated_at", -1)]
        ]


class SimulationHistory(Document):
    """
    Complete record of simulation sessions
    Tracks choices, state changes, consequences, and learning outcomes
    """
    simulation_id: str = Field(..., description="Unique simulation session ID")
    user_id: str = Field(..., description="User identifier")
    scenario_id: str = Field(..., description="Scenario identifier")
    
    # Choice Information
    choice_index: int = Field(..., description="Index of chosen option")
    choice_id: str = Field(..., description="Unique choice identifier")
    choice_type: str = Field(..., description="Choice classification: kusala, akusala, neutral")
    choice_label: str = Field(..., description="Display label of the choice")
    choice_description: Optional[str] = Field(None, description="Full choice description")
    
    # Mental Process (Citta-Vīthi)
    citta_generated: str = Field(..., description="Type of consciousness generated")
    citta_quality: str = Field(..., description="Quality: kusala/akusala/kiriya")
    kamma_generated: float = Field(default=0.0, description="Kamma potency generated (0-10)")
    
    # Mindfulness Intervention
    sati_intervened: bool = Field(default=False, description="Did Sati intervene?")
    sati_strength_at_choice: float = Field(default=5.0, description="Sati strength at decision time")
    panna_intervened: bool = Field(default=False, description="Did Paññā provide insight?")
    
    # State Before and After
    state_before: Dict[str, Any] = Field(..., description="Mind state snapshot before choice")
    state_after: Dict[str, Any] = Field(..., description="Mind state snapshot after choice")
    state_changes: List[str] = Field(default_factory=list, description="List of specific changes")
    
    # Consequences (Three Time Frames)
    immediate_consequences: List[str] = Field(default_factory=list, description="Immediate results of the choice")
    short_term_consequences: List[str] = Field(default_factory=list, description="Short-term implications")
    long_term_consequences: List[str] = Field(default_factory=list, description="Long-term karmic effects")
    
    # Learning and Reflection
    wisdom_gained: str = Field(..., description="Dhamma insight gained")
    practice_tip: str = Field(..., description="Practice recommendation")
    pali_term_explained: Optional[str] = Field(None, description="Relevant Pali term explanation")
    
    # User Engagement
    user_reflection: Optional[str] = Field(None, description="User's own reflection (optional)")
    user_rating: Optional[int] = Field(None, ge=1, le=5, description="User rating of simulation (1-5)")
    
    # Anusaya Changes
    anusaya_before: Dict[str, float] = Field(default_factory=dict, description="Anusaya before")
    anusaya_after: Dict[str, float] = Field(default_factory=dict, description="Anusaya after")
    anusaya_changes: Dict[str, float] = Field(default_factory=dict, description="Anusaya delta")
    
    # Metadata
    duration_seconds: Optional[int] = Field(None, description="Time taken to make choice")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Simulation timestamp")
    
    class Settings:
        name = "simulation_history"
        indexes = [
            "user_id",
            "scenario_id",
            "simulation_id",
            "timestamp",
            "choice_type",
            [("user_id", 1), ("timestamp", -1)],
            [("scenario_id", 1), ("timestamp", -1)],
            [("choice_type", 1), ("timestamp", -1)]
        ]
