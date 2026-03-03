from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

# --- Base Schemas ---

class MessageResponse(BaseModel):
    message: str

# --- Request Schemas (Moved from models.py) ---

class StimulusObject(BaseModel):
    type: str
    source: str
    intensity: float
    details: str

class EnvironmentModifiers(BaseModel):
    ambient_stress_level: float = 0

class ReactionRequest(BaseModel):
    model_id: str
    stimulus: StimulusObject = Field(..., alias="stimulus_object") # Frontend sends stimulus_object
    environment: Optional[EnvironmentModifiers] = Field(None, alias="environment_modifiers")

    class Config:
        populate_by_name = True
        
class CultivationRequest(BaseModel):
    cultivation_type: str


# --- Profile & Stats Schemas ---

class CharacterCardSchema(BaseModel):
    name: str
    status_label: str
    overall_level: int
    level_progress_percent: float
    image_url: str

class CoreStatsSchema(BaseModel):
    latent_tendencies: Dict[str, Any]
    summary_metrics: Dict[str, Any]

    class Config:
        extra = "allow"

class DMMProfileSchema(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    model_id: str
    name: Optional[str] = None
    status_label: Optional[str] = None
    overall_level: Optional[int] = None
    image_url: Optional[str] = None
    level_progress_percent: Optional[float] = None
    character_card: CharacterCardSchema
    core_stats: CoreStatsSchema
    training_module: Optional[Dict[str, Any]] = None
    editor_profile_for: Optional[str] = None

    class Config:
        extra = "allow"
        populate_by_name = True

# --- Log Schemas ---

class KammaLogEntrySchema(BaseModel):
    id: str = Field(..., alias="_id")
    model_id: str
    timestamp: str
    event_type: str
    description: str
    impact_level: int
    context: Dict[str, Any]

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {
            "id": str
        }

class TrainingLogSchema(BaseModel):
    id: str = Field(..., alias="_id")
    model_id: str
    date: str # Keep as string for now
    training_type: str
    details: Dict[str, Any]

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {
            "id": str
        }

# --- Simulation Schemas ---

class ReactionSimulationResponse(BaseModel):
    status: str
    log_entry: KammaLogEntrySchema
