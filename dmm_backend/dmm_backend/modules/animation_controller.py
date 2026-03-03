"""
🎭 3D Animation Controller - Three.js Integration
Controls character animations based on DemeanorScore

Features:
- Convert DemeanorScore → animation parameters
- Gesture mapping from kamma
- Posture control (upright, slouched, tense)
- Facial expression animation
- Movement speed and style
- Buddhist-accurate body language

Dependencies:
- Frontend: Three.js, React Three Fiber
- Backend: Animation parameter generation
"""

from typing import Optional, Dict, List, Literal, Tuple
from datetime import datetime
from pydantic import BaseModel, Field

from kamma_appearance_models import DemeanorScore, KammaAppearanceProfile
from core.logging_config import get_logger

logger = get_logger(__name__)


# =============================================================================
# ANIMATION PARAMETERS
# =============================================================================

class AnimationParameters(BaseModel):
    """3D Animation parameters derived from DemeanorScore"""
    
    # Posture & stance
    posture_type: Literal["upright", "slouched", "tense", "relaxed"] = Field(..., description="Overall posture")
    spine_curvature: float = Field(..., ge=-1.0, le=1.0, description="-1 (slouched) to 1 (erect)")
    shoulder_tension: float = Field(..., ge=0.0, le=1.0, description="Shoulder tension level")
    hip_angle: float = Field(..., ge=0.0, le=45.0, description="Hip tilt angle in degrees")
    
    # Movement characteristics
    movement_speed: float = Field(..., ge=0.5, le=2.0, description="Movement speed multiplier")
    movement_fluidity: float = Field(..., ge=0.0, le=1.0, description="Motion smoothness")
    gesture_frequency: float = Field(..., ge=0.0, le=1.0, description="How often gestures occur")
    gesture_amplitude: float = Field(..., ge=0.0, le=1.0, description="Size of gestures")
    
    # Facial expressions
    facial_expression: str = Field(..., description="Primary facial expression")
    smile_intensity: float = Field(..., ge=0.0, le=1.0, description="Smile strength")
    eye_openness: float = Field(..., ge=0.0, le=1.0, description="Eye openness")
    brow_position: float = Field(..., ge=-1.0, le=1.0, description="-1 (frown) to 1 (raised)")
    
    # Gaze behavior
    gaze_steadiness: float = Field(..., ge=0.0, le=1.0, description="Eye contact stability")
    gaze_warmth: float = Field(..., ge=0.0, le=1.0, description="Warmth in gaze")
    
    # Energy & presence
    energy_level: float = Field(..., ge=0.0, le=1.0, description="Overall energy")
    presence_strength: float = Field(..., ge=0.0, le=1.0, description="Charismatic presence")
    
    # Buddhist influence markers
    metta_radiance: float = Field(..., ge=0.0, le=1.0, description="Visible mettā in body language")
    meditation_calmness: float = Field(..., ge=0.0, le=1.0, description="Meditative stillness")
    confidence_marker: float = Field(..., ge=0.0, le=1.0, description="Confident posture")
    
    # Idle animations
    idle_animation: str = Field(..., description="Main idle animation")
    idle_variation: float = Field(..., ge=0.0, le=1.0, description="Variation in idle")
    breathing_depth: float = Field(..., ge=0.0, le=1.0, description="Breathing animation depth")
    
    class Config:
        json_schema_extra = {
            "example": {
                "posture_type": "upright",
                "spine_curvature": 0.8,
                "shoulder_tension": 0.2,
                "movement_speed": 1.0,
                "movement_fluidity": 0.9,
                "facial_expression": "gentle smile",
                "smile_intensity": 0.7,
                "gaze_steadiness": 0.85,
                "metta_radiance": 0.9,
                "meditation_calmness": 0.8,
                "idle_animation": "standing_peaceful"
            }
        }


class GestureDefinition(BaseModel):
    """Definition of a single gesture"""
    name: str = Field(..., description="Gesture name")
    type: Literal["hand", "head", "body", "combined"] = Field(..., description="Gesture type")
    duration: float = Field(..., ge=0.5, le=5.0, description="Duration in seconds")
    triggers: List[str] = Field(..., description="When to trigger (metta, greeting, etc.)")
    intensity: float = Field(..., ge=0.0, le=1.0, description="Gesture intensity")
    description: str = Field(..., description="Human-readable description")


# =============================================================================
# GESTURE LIBRARY
# =============================================================================

class GestureLibrary:
    """
    Library of gestures mapped to kamma states
    
    Buddhist Body Language Principles:
    - Mettā → Open, welcoming gestures
    - Meditation → Still, composed posture
    - Confidence → Upright, stable stance
    - Tension → Tight, closed gestures
    - Ill-will → Sharp, aggressive movements
    """
    
    # Mettā-based gestures
    METTA_GESTURES = [
        GestureDefinition(
            name="anjali_mudra",
            type="hand",
            duration=2.0,
            triggers=["greeting", "respect", "gratitude"],
            intensity=0.8,
            description="Palms together in respectful greeting (wai)"
        ),
        GestureDefinition(
            name="open_palm_offering",
            type="hand",
            duration=1.5,
            triggers=["giving", "compassion"],
            intensity=0.7,
            description="Open palm gesture showing generosity"
        ),
        GestureDefinition(
            name="gentle_nod",
            type="head",
            duration=1.0,
            triggers=["agreement", "understanding"],
            intensity=0.5,
            description="Gentle head nod showing understanding"
        ),
        GestureDefinition(
            name="warm_smile",
            type="combined",
            duration=2.0,
            triggers=["happiness", "friendliness"],
            intensity=0.8,
            description="Warm, genuine smile with eye crinkles"
        )
    ]
    
    # Meditation/Peace gestures
    MEDITATION_GESTURES = [
        GestureDefinition(
            name="dhyana_mudra",
            type="hand",
            duration=3.0,
            triggers=["meditation", "contemplation"],
            intensity=0.9,
            description="Meditation hand position (dhyana mudra)"
        ),
        GestureDefinition(
            name="still_presence",
            type="body",
            duration=5.0,
            triggers=["peace", "mindfulness"],
            intensity=1.0,
            description="Completely still, mindful presence"
        ),
        GestureDefinition(
            name="slow_breath",
            type="body",
            duration=4.0,
            triggers=["calm", "centered"],
            intensity=0.7,
            description="Slow, deep breathing rhythm"
        )
    ]
    
    # Confidence gestures
    CONFIDENCE_GESTURES = [
        GestureDefinition(
            name="upright_stance",
            type="body",
            duration=2.0,
            triggers=["confidence", "authority"],
            intensity=0.8,
            description="Erect posture with shoulders back"
        ),
        GestureDefinition(
            name="steady_gaze",
            type="head",
            duration=3.0,
            triggers=["conviction", "certainty"],
            intensity=0.9,
            description="Steady, direct eye contact"
        ),
        GestureDefinition(
            name="assertive_gesture",
            type="hand",
            duration=1.2,
            triggers=["emphasis", "leadership"],
            intensity=0.7,
            description="Assertive hand gesture for emphasis"
        )
    ]
    
    # Tension/Ill-will gestures
    TENSION_GESTURES = [
        GestureDefinition(
            name="tense_shoulders",
            type="body",
            duration=2.0,
            triggers=["stress", "anxiety"],
            intensity=0.8,
            description="Raised, tense shoulders"
        ),
        GestureDefinition(
            name="clenched_fists",
            type="hand",
            duration=1.5,
            triggers=["anger", "frustration"],
            intensity=0.9,
            description="Hands clenched into fists"
        ),
        GestureDefinition(
            name="sharp_turn",
            type="body",
            duration=0.8,
            triggers=["avoidance", "rejection"],
            intensity=0.7,
            description="Quick, sharp body turn away"
        )
    ]


# =============================================================================
# ANIMATION PARAMETER MAPPER
# =============================================================================

class AnimationParameterMapper:
    """
    Maps DemeanorScore to animation parameters
    
    Buddhist Body Language Mappings:
    - High mettā → Open posture, gentle movements, warm smile
    - High meditation → Still, composed, minimal gestures
    - High confidence → Upright posture, steady gaze
    - High tension → Tight movements, tense shoulders
    - High ill-will → Sharp gestures, aggressive posture
    """
    
    def __init__(self):
        self.gesture_lib = GestureLibrary()
    
    def map_demeanor_score(self, demeanor: DemeanorScore) -> AnimationParameters:
        """
        Convert DemeanorScore → AnimationParameters
        
        Algorithm:
        1. Determine posture from confidence/tension
        2. Calculate movement characteristics
        3. Set facial expression from emotional state
        4. Apply Buddhist influence modifiers
        5. Select appropriate idle animation
        """
        logger.info("Mapping DemeanorScore to animation parameters")
        
        # 1. Posture
        posture_type, spine_curvature = self._calculate_posture(demeanor)
        shoulder_tension = demeanor.tension_level / 100.0
        hip_angle = self._calculate_hip_angle(demeanor)
        
        # 2. Movement
        movement_speed = self._calculate_movement_speed(demeanor)
        movement_fluidity = self._calculate_fluidity(demeanor)
        gesture_freq = self._calculate_gesture_frequency(demeanor)
        gesture_amp = self._calculate_gesture_amplitude(demeanor)
        
        # 3. Facial expression
        facial_expr = self._determine_facial_expression(demeanor)
        smile_intensity = self._calculate_smile(demeanor)
        eye_openness = self._calculate_eye_openness(demeanor)
        brow_position = self._calculate_brow_position(demeanor)
        
        # 4. Gaze
        gaze_steadiness = self._calculate_gaze_steadiness(demeanor)
        gaze_warmth = demeanor.loving_kindness_score / 100.0
        
        # 5. Energy & presence
        energy = demeanor.overall_demeanor / 100.0
        presence = demeanor.charisma_modifier / 10.0  # 0-10 → 0-1
        
        # 6. Buddhist markers
        metta_radiance = demeanor.loving_kindness_score / 100.0
        meditation_calm = demeanor.peacefulness / 100.0
        confidence_marker = demeanor.confidence_level / 100.0
        
        # 7. Idle animation
        idle_anim = self._select_idle_animation(demeanor)
        idle_var = self._calculate_idle_variation(demeanor)
        breathing_depth = self._calculate_breathing_depth(demeanor)
        
        params = AnimationParameters(
            posture_type=posture_type,
            spine_curvature=spine_curvature,
            shoulder_tension=shoulder_tension,
            hip_angle=hip_angle,
            movement_speed=movement_speed,
            movement_fluidity=movement_fluidity,
            gesture_frequency=gesture_freq,
            gesture_amplitude=gesture_amp,
            facial_expression=facial_expr,
            smile_intensity=smile_intensity,
            eye_openness=eye_openness,
            brow_position=brow_position,
            gaze_steadiness=gaze_steadiness,
            gaze_warmth=gaze_warmth,
            energy_level=energy,
            presence_strength=presence,
            metta_radiance=metta_radiance,
            meditation_calmness=meditation_calm,
            confidence_marker=confidence_marker,
            idle_animation=idle_anim,
            idle_variation=idle_var,
            breathing_depth=breathing_depth
        )
        
        logger.info(f"Mapped parameters: posture={posture_type}, expression={facial_expr}")
        
        return params
    
    def _calculate_posture(self, demeanor: DemeanorScore) -> Tuple[str, float]:
        """Calculate posture type and spine curvature"""
        confidence = demeanor.confidence_level
        tension = demeanor.tension_level
        peace = demeanor.peacefulness
        
        # High confidence, low tension → upright
        if confidence >= 70 and tension <= 30:
            return "upright", 0.8
        
        # High peace, low tension → relaxed
        elif peace >= 70 and tension <= 30:
            return "relaxed", 0.6
        
        # High tension → tense
        elif tension >= 60:
            return "tense", 0.4
        
        # Low confidence → slouched
        elif confidence <= 40:
            return "slouched", -0.3
        
        # Default: neutral
        else:
            return "upright", 0.5
    
    def _calculate_hip_angle(self, demeanor: DemeanorScore) -> float:
        """Calculate hip tilt angle"""
        # Confident, upright posture → small hip angle
        if demeanor.confidence_level >= 70:
            return 5.0
        # Slouched → larger hip angle
        elif demeanor.confidence_level <= 40:
            return 20.0
        else:
            return 10.0
    
    def _calculate_movement_speed(self, demeanor: DemeanorScore) -> float:
        """Calculate movement speed multiplier"""
        energy = demeanor.overall_demeanor
        peace = demeanor.peacefulness
        
        # High energy, low peace → fast movements
        if energy >= 70 and peace <= 50:
            return 1.3
        
        # High peace → slow, mindful movements
        elif peace >= 70:
            return 0.8
        
        # Default: normal speed
        else:
            return 1.0
    
    def _calculate_fluidity(self, demeanor: DemeanorScore) -> float:
        """Calculate movement fluidity (smoothness)"""
        peace = demeanor.peacefulness
        tension = demeanor.tension_level
        
        # High peace, low tension → very fluid
        if peace >= 70 and tension <= 30:
            return 0.9
        
        # High tension → jerky, less fluid
        elif tension >= 60:
            return 0.3
        
        else:
            return 0.6
    
    def _calculate_gesture_frequency(self, demeanor: DemeanorScore) -> float:
        """Calculate how often gestures occur"""
        metta = demeanor.loving_kindness_score
        confidence = demeanor.confidence_level
        
        # High mettā → frequent warm gestures
        if metta >= 70:
            return 0.8
        
        # Low confidence → few gestures
        elif confidence <= 40:
            return 0.3
        
        else:
            return 0.5
    
    def _calculate_gesture_amplitude(self, demeanor: DemeanorScore) -> float:
        """Calculate size of gestures"""
        confidence = demeanor.confidence_level
        
        # High confidence → larger gestures
        if confidence >= 70:
            return 0.8
        
        # Low confidence → small gestures
        elif confidence <= 40:
            return 0.3
        
        else:
            return 0.5
    
    def _determine_facial_expression(self, demeanor: DemeanorScore) -> str:
        """Determine primary facial expression"""
        metta = demeanor.loving_kindness_score
        peace = demeanor.peacefulness
        tension = demeanor.tension_level
        ill_will = demeanor.ill_will_score
        
        # High mettā → warm smile
        if metta >= 80:
            return "warm smile"
        
        # High peace → serene
        elif peace >= 80:
            return "serene calm"
        
        # High tension → tense/worried
        elif tension >= 60:
            return "tense concern"
        
        # High ill-will → stern/harsh
        elif ill_will >= 60:
            return "stern gaze"
        
        # Moderate → neutral pleasant
        else:
            return "neutral pleasant"
    
    def _calculate_smile(self, demeanor: DemeanorScore) -> float:
        """Calculate smile intensity"""
        metta = demeanor.loving_kindness_score
        
        return min(1.0, metta / 100.0)
    
    def _calculate_eye_openness(self, demeanor: DemeanorScore) -> float:
        """Calculate eye openness"""
        energy = demeanor.overall_demeanor
        peace = demeanor.peacefulness
        
        # High energy → wide eyes
        if energy >= 70:
            return 0.9
        
        # High peace → slightly closed (meditative)
        elif peace >= 80:
            return 0.6
        
        else:
            return 0.75
    
    def _calculate_brow_position(self, demeanor: DemeanorScore) -> float:
        """Calculate eyebrow position"""
        tension = demeanor.tension_level
        metta = demeanor.loving_kindness_score
        
        # High tension → furrowed brow
        if tension >= 60:
            return -0.6
        
        # High mettā → slightly raised (friendly)
        elif metta >= 70:
            return 0.3
        
        else:
            return 0.0
    
    def _calculate_gaze_steadiness(self, demeanor: DemeanorScore) -> float:
        """Calculate eye contact stability"""
        confidence = demeanor.confidence_level
        peace = demeanor.peacefulness
        
        # High confidence + peace → very steady
        if confidence >= 70 and peace >= 60:
            return 0.9
        
        # Low confidence → avoidant gaze
        elif confidence <= 40:
            return 0.3
        
        else:
            return 0.6
    
    def _select_idle_animation(self, demeanor: DemeanorScore) -> str:
        """Select appropriate idle animation"""
        peace = demeanor.peacefulness
        metta = demeanor.loving_kindness_score
        tension = demeanor.tension_level
        
        # High peace + mettā → peaceful standing
        if peace >= 70 and metta >= 70:
            return "standing_peaceful"
        
        # High meditation → meditative pose
        elif peace >= 80:
            return "standing_meditative"
        
        # High tension → shifting weight
        elif tension >= 60:
            return "standing_tense"
        
        # Default → neutral standing
        else:
            return "standing_neutral"
    
    def _calculate_idle_variation(self, demeanor: DemeanorScore) -> float:
        """Calculate variation in idle animation"""
        peace = demeanor.peacefulness
        
        # High peace → less variation (stillness)
        if peace >= 80:
            return 0.2
        
        # Low peace → more variation (fidgeting)
        elif peace <= 40:
            return 0.8
        
        else:
            return 0.5
    
    def _calculate_breathing_depth(self, demeanor: DemeanorScore) -> float:
        """Calculate breathing animation depth"""
        peace = demeanor.peacefulness
        
        # High peace → deep, visible breathing
        if peace >= 70:
            return 0.8
        
        else:
            return 0.5
    
    def select_gestures(
        self,
        demeanor: DemeanorScore,
        trigger: str,
        max_gestures: int = 3
    ) -> List[GestureDefinition]:
        """
        Select appropriate gestures for given trigger
        
        Args:
            demeanor: Character's demeanor score
            trigger: Event trigger (greeting, meditation, etc.)
            max_gestures: Maximum number of gestures to return
            
        Returns:
            List of appropriate gestures
        """
        selected = []
        
        # High mettā → mettā gestures
        if demeanor.loving_kindness_score >= 70:
            candidates = [g for g in self.gesture_lib.METTA_GESTURES if trigger in g.triggers]
            selected.extend(candidates[:max_gestures])
        
        # High peace → meditation gestures
        if demeanor.peacefulness >= 70 and len(selected) < max_gestures:
            candidates = [g for g in self.gesture_lib.MEDITATION_GESTURES if trigger in g.triggers]
            selected.extend(candidates[:max_gestures - len(selected)])
        
        # High confidence → confidence gestures
        if demeanor.confidence_level >= 70 and len(selected) < max_gestures:
            candidates = [g for g in self.gesture_lib.CONFIDENCE_GESTURES if trigger in g.triggers]
            selected.extend(candidates[:max_gestures - len(selected)])
        
        # High tension/ill-will → tension gestures
        if (demeanor.tension_level >= 60 or demeanor.ill_will_score >= 60) and len(selected) < max_gestures:
            candidates = [g for g in self.gesture_lib.TENSION_GESTURES if trigger in g.triggers]
            selected.extend(candidates[:max_gestures - len(selected)])
        
        return selected[:max_gestures]


# =============================================================================
# ANIMATION CONTROLLER
# =============================================================================

class AnimationController:
    """
    Main controller for 3D character animations
    Coordinates between backend kamma data and frontend Three.js
    """
    
    def __init__(self):
        self.mapper = AnimationParameterMapper()
    
    def get_animation_config(
        self,
        demeanor: DemeanorScore,
        context: str = "idle"
    ) -> Dict:
        """
        Get complete animation configuration for frontend
        
        Args:
            demeanor: Character's demeanor score
            context: Animation context (idle/greeting/meditation/etc.)
            
        Returns:
            Dict with all animation parameters and gesture sequences
        """
        logger.info(f"Generating animation config for context: {context}")
        
        # Get base parameters
        params = self.mapper.map_demeanor_score(demeanor)
        
        # Get context-appropriate gestures
        gestures = self.mapper.select_gestures(demeanor, trigger=context)
        
        # Build config
        config = {
            "parameters": params.dict(),
            "gestures": [g.dict() for g in gestures],
            "context": context,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return config
    
    def get_animation_description(self, demeanor: DemeanorScore) -> str:
        """
        Get human-readable animation description
        """
        params = self.mapper.map_demeanor_score(demeanor)
        
        parts = []
        
        # Posture
        parts.append(f"{params.posture_type.capitalize()} posture")
        
        # Movement
        if params.movement_fluidity >= 0.8:
            parts.append("fluid, graceful movements")
        elif params.movement_fluidity <= 0.4:
            parts.append("tense, jerky movements")
        
        # Expression
        parts.append(f"{params.facial_expression}")
        
        # Buddhist influence
        if params.metta_radiance >= 0.8:
            parts.append("radiating mettā")
        if params.meditation_calmness >= 0.8:
            parts.append("deep meditative calm")
        
        return ". ".join(parts) + "."


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_animation_parameters(demeanor: DemeanorScore) -> AnimationParameters:
    """
    Convenience function to get animation parameters
    
    Example:
        >>> params = get_animation_parameters(demeanor_score)
        >>> print(params.posture_type)
        'upright'
    """
    mapper = AnimationParameterMapper()
    return mapper.map_demeanor_score(demeanor)


def get_animation_description(demeanor: DemeanorScore) -> str:
    """
    Get human-readable animation description
    
    Example:
        >>> desc = get_animation_description(demeanor_score)
        >>> print(desc)
        "Upright posture. Fluid, graceful movements. Warm smile. Radiating mettā."
    """
    controller = AnimationController()
    return controller.get_animation_description(demeanor)
