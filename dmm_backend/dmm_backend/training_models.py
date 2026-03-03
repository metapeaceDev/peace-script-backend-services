"""
📝 Training System Models for Digital Mind Model v1.4

Pydantic models for Training Log system - tracks spiritual practice sessions,
results, and character development modifications.
"""

from datetime import datetime
from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field


# ============================================================================
# TRAINING RESULT MODELS
# ============================================================================

class TrainingMetrics(BaseModel):
    """Metrics captured during a training session"""
    exp_gained: Optional[int] = Field(None, description="Experience points gained")
    quality_score: Optional[float] = Field(None, ge=0, le=10, description="Quality of practice (0-10)")
    concentration_level: Optional[float] = Field(None, ge=0, le=10, description="Samādhi level achieved")
    mindfulness_level: Optional[float] = Field(None, ge=0, le=10, description="Sati level maintained")
    vedana_tolerance_change: Optional[float] = Field(None, description="Change in suffering tolerance")
    patigha_reduction: Optional[float] = Field(None, description="Reduction in aversion")
    reason: Optional[str] = Field(None, description="Reason for partial success/failure")
    
    # Type-specific metrics
    dana_exp_gained: Optional[int] = None
    sila_exp_gained: Optional[int] = None
    khanti_exp_gained: Optional[int] = None
    sati_exp_gained: Optional[int] = None
    panna_insight: Optional[int] = None
    metta_exp_gained: Optional[int] = None
    
    class Config:
        extra = "allow"  # Allow additional custom metrics


class TrainingModification(BaseModel):
    """A single modification made to character as result of training"""
    target: str = Field(..., description="Path to modified field (e.g., 'Barami.dana', 'Anusaya.patigha')")
    old_value: Optional[float] = Field(None, description="Value before modification")
    new_value: Optional[float] = Field(None, description="Value after modification")
    delta: str = Field(..., description="Human-readable change description (e.g., '+1 level', '-0.5')")
    exp_change: Optional[str] = Field(None, description="Experience change if applicable")


class TrainingResultDetails(BaseModel):
    """Detailed results of a training session"""
    status: Literal["success", "partial", "fail"] = Field(..., description="Overall result status")
    metrics: TrainingMetrics = Field(..., description="Captured metrics")
    notes: Optional[str] = Field(None, description="Practitioner's notes or observations")


# ============================================================================
# TRAINING SESSION MODELS
# ============================================================================

class TrainingSession(BaseModel):
    """A single training/practice session"""
    id: str = Field(..., description="Unique session ID (e.g., 'train-001')")
    model_id: str = Field(..., description="ID of the model/character")
    training_type: str = Field(..., description="Type of training (e.g., 'GENEROSITY', 'MEDITATION')")
    date: str = Field(..., description="Date of training (YYYY-MM-DD)")
    duration_minutes: int = Field(..., ge=0, description="Duration in minutes")
    result: Literal["Successful", "Partially Successful", "Failed"] = Field(..., description="Training result")
    result_details: TrainingResultDetails = Field(..., description="Detailed results")
    modifications: List[TrainingModification] = Field(default=[], description="Character modifications made")
    completed_at: datetime = Field(..., description="Timestamp when training completed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "train-001",
                "model_id": "peace-mind-001",
                "training_type": "GENEROSITY",
                "date": "2024-05-01",
                "duration_minutes": 30,
                "result": "Successful",
                "result_details": {
                    "status": "success",
                    "metrics": {
                        "dana_exp_gained": 25,
                        "quality_score": 8.5
                    },
                    "notes": "Practiced giving without expectation"
                },
                "modifications": [
                    {
                        "target": "Barami.dana",
                        "old_value": 4,
                        "new_value": 5,
                        "delta": "+1 level"
                    }
                ],
                "completed_at": "2024-05-01T08:30:00Z"
            }
        }


class TrainingLog(BaseModel):
    """Collection of training sessions for a model"""
    model_id: str
    training_sessions: List[TrainingSession] = []
    total_sessions: int = 0
    success_rate: float = Field(0.0, ge=0, le=100, description="Success rate percentage")
    total_exp_gained: int = 0
    total_kusala_earned: int = 0
    total_akusala_earned: int = 0
    last_training_date: Optional[str] = None
    streak_days: int = 0
    average_session_duration: int = 0


# ============================================================================
# API REQUEST/RESPONSE MODELS
# ============================================================================

class StartTrainingRequest(BaseModel):
    """Request to start a new training session"""
    model_id: str = Field(..., description="ID of the model to train")
    training_type: str = Field(..., description="Type of training")
    duration_minutes: int = Field(30, ge=5, le=480, description="Planned duration (5-480 minutes)")
    notes: Optional[str] = Field(None, max_length=500, description="Optional notes or intentions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "model_id": "peace-mind-001",
                "training_type": "MEDITATION",
                "duration_minutes": 60,
                "notes": "Morning vipassana session"
            }
        }


class StartTrainingResponse(BaseModel):
    """Response after starting training session"""
    success: bool
    session_id: str
    message: str
    estimated_completion: datetime


class CompleteTrainingRequest(BaseModel):
    """Request to complete/finish a training session"""
    session_id: str = Field(..., description="Training session ID")
    result: Literal["Successful", "Partially Successful", "Failed"] = Field(..., description="Training outcome")
    metrics: TrainingMetrics = Field(..., description="Captured metrics")
    notes: Optional[str] = Field(None, max_length=1000, description="Session notes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "train-003",
                "result": "Successful",
                "metrics": {
                    "sati_exp_gained": 30,
                    "concentration_level": 8.0,
                    "quality_score": 8.5
                },
                "notes": "Deep concentration achieved"
            }
        }


class CompleteTrainingResponse(BaseModel):
    """Response after completing training"""
    success: bool
    modifications: List[TrainingModification]
    updated_profile: Dict = Field(default={}, description="Relevant profile updates")
    message: str


class TrainingStatsResponse(BaseModel):
    """Training statistics for a model"""
    model_id: str
    total_sessions: int
    success_rate: float
    total_exp_gained: int
    total_kusala_earned: int
    total_akusala_earned: int
    streak_days: int
    average_duration: int
    most_practiced_type: Optional[str] = None
    recent_trend: Optional[str] = None  # "improving", "stable", "declining"


# ============================================================================
# TRAINING TYPE DEFINITIONS
# ============================================================================

TRAINING_TYPES = {
    "GENEROSITY": {
        "name": "Dana (Generosity)",
        "target_parami": "dana",
        "base_exp": 20,
        "typical_duration": 30,
        "description": "Practice of giving without expectation"
    },
    "ETHICS_TRAINING": {
        "name": "Sila (Virtue)",
        "target_parami": "sila",
        "base_exp": 15,
        "typical_duration": 20,
        "description": "Maintaining precepts and ethical conduct"
    },
    "RENUNCIATION": {
        "name": "Nekkhamma (Renunciation)",
        "target_parami": "nekkhamma",
        "base_exp": 25,
        "typical_duration": 60,
        "description": "Letting go of sensual attachments"
    },
    "WISDOM_STUDY": {
        "name": "Pañña (Wisdom)",
        "target_parami": "panna",
        "base_exp": 30,
        "typical_duration": 90,
        "description": "Study and contemplation of Dhamma"
    },
    "ENERGY_CULTIVATION": {
        "name": "Viriya (Energy)",
        "target_parami": "viriya",
        "base_exp": 18,
        "typical_duration": 45,
        "description": "Cultivation of right effort"
    },
    "PATIENCE": {
        "name": "Khanti (Patience)",
        "target_parami": "khanti",
        "base_exp": 22,
        "typical_duration": 40,
        "description": "Endurance with difficult situations"
    },
    "TRUTHFULNESS": {
        "name": "Sacca (Truthfulness)",
        "target_parami": "sacca",
        "base_exp": 20,
        "typical_duration": 15,
        "description": "Practice of honest speech and action"
    },
    "DETERMINATION": {
        "name": "Adhiṭṭhāna (Determination)",
        "target_parami": "adhitthana",
        "base_exp": 20,
        "typical_duration": 30,
        "description": "Unwavering resolve in practice"
    },
    "LOVING_KINDNESS": {
        "name": "Mettā (Loving-kindness)",
        "target_parami": "metta",
        "base_exp": 25,
        "typical_duration": 40,
        "description": "Cultivation of universal goodwill"
    },
    "EQUANIMITY": {
        "name": "Upekkhā (Equanimity)",
        "target_parami": "upekkha",
        "base_exp": 28,
        "typical_duration": 50,
        "description": "Balanced mind in all situations"
    },
    "MEDITATION": {
        "name": "Samādhi & Vipassanā",
        "target_parami": "panna",  # Primarily wisdom
        "base_exp": 30,
        "typical_duration": 60,
        "description": "Concentration and insight meditation",
        "affects": ["sati_mastery", "panna_mastery", "anusaya"]
    }
}


def get_training_type_info(training_type: str) -> Optional[Dict]:
    """Get information about a training type"""
    return TRAINING_TYPES.get(training_type)


def calculate_exp_gain(
    training_type: str,
    quality_score: float,
    duration_minutes: int
) -> int:
    """
    Calculate experience gain based on training quality and duration.
    
    Formula: base_exp * (quality_score / 10) * (duration / typical_duration)
    """
    info = get_training_type_info(training_type)
    if not info:
        return 0
    
    base_exp = info["base_exp"]
    typical_duration = info["typical_duration"]
    
    quality_multiplier = quality_score / 10.0
    duration_multiplier = min(duration_minutes / typical_duration, 2.0)  # Cap at 2x
    
    exp_gained = int(base_exp * quality_multiplier * duration_multiplier)
    
    return max(exp_gained, 1)  # Minimum 1 exp
