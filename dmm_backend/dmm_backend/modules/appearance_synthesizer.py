"""
🔸 Appearance Synthesizer Module
Synthesizes final ExternalCharacter from KammaAppearanceProfile + Rupa

This module:
1. Takes KammaAppearanceProfile (from analyzer)
2. Generates Rupa modifications based on kamma
3. Maps to ExternalCharacter fields
4. Creates complete physical appearance profile

Buddhist Foundation:
- Kamma-samutthāna rūpa (กรรมสมุฏฐานรูป) - Fixed traits from birth kamma
- Citta-samutthāna rūpa (จิตตสมุฏฐานรูป) - Dynamic expressions
- Integration with 28 Rupa system
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from kamma_appearance_models import KammaAppearanceProfile, HealthScore, VoiceScore, DemeanorScore
from documents_actors import ExternalCharacter
from rupa_models import (
    RupaProfile,
    MahabhutaRupa,
    PathaviCharacteristics,
    ApoCharacteristics,
    TejoCharacteristics,
    VayoCharacteristics,
    PasadaRupa,
    BhavaRupa,
    HadayaRupa,
    JivitaRupa,
    AharaRupa,
    ParicchedaRupa,
    VinnattiRupa,
    VikaraRupa,
    LakkhanaRupa,
    RupaSamutthana,
    YoniType
)
from core.logging_config import get_logger

logger = get_logger(__name__)


# =============================================================================
# RUPA APPEARANCE GENERATOR
# =============================================================================

class RupaAppearanceGenerator:
    """
    Generates Rupa (material form) based on Kamma
    Modifies Mahabhuta elements according to kamma influence
    """
    
    def generate_kamma_rupa(
        self,
        kamma_profile: KammaAppearanceProfile,
        base_genetics: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate Rupa with Kamma modifications
        
        Args:
            kamma_profile: KammaAppearanceProfile from analyzer
            base_genetics: Optional base genetic traits
            
        Returns:
            Dict with modified Rupa components
        """
        logger.info(f"Generating kamma-based rupa for model: {kamma_profile.model_id}")
        
        # Create base Mahabhuta
        mahabhuta = self._create_kamma_mahabhuta(kamma_profile.health_score)
        
        # Create Pasada (sense organs) - affected by health
        pasada = self._create_pasada_from_health(kamma_profile.health_score)
        
        # Create Vinnatti (bodily/verbal expression) - affected by voice & demeanor
        vinnatti = self._create_vinnatti_from_scores(
            kamma_profile.voice_score,
            kamma_profile.demeanor_score
        )
        
        # Create Vikara (pliancy) - affected by demeanor
        vikara = self._create_vikara_from_demeanor(kamma_profile.demeanor_score)
        
        # Create Lakkhana (aging characteristics) - affected by health
        lakkhana = self._create_lakkhana_from_health(kamma_profile.health_score)
        
        # Jivita (life faculty) - affected by health
        jivita = self._create_jivita_from_health(kamma_profile.health_score)
        
        return {
            "mahabhuta": mahabhuta,
            "pasada": pasada,
            "vinnatti": vinnatti,
            "vikara": vikara,
            "lakkhana": lakkhana,
            "jivita": jivita,
            "kamma_influence_notes": kamma_profile.kamma_influence_summary
        }
    
    def _create_kamma_mahabhuta(self, health: HealthScore) -> MahabhutaRupa:
        """
        Create Mahabhuta (4 great elements) modified by kamma
        
        Mappings:
        - Pathavi (Earth/Hardness): Body strength
        - Apo (Water/Cohesion): Skin quality
        - Tejo (Fire/Heat): Vitality/Energy
        - Vayo (Wind/Motion): Fitness/Movement
        """
        # Pathavi - affected by body strength
        pathavi_hardness = 30 + (health.body_strength * 0.4)  # 30-70 range
        pathavi_softness = 100 - pathavi_hardness
        
        # Apo - affected by skin quality
        apo_cohesion = 30 + (health.skin_quality * 0.4)  # 30-70 range
        apo_fluidity = 100 - apo_cohesion
        
        # Tejo - affected by vitality
        # Normal body temp: 36-38°C, vitality affects this
        base_temp = 37.0
        vitality_modifier = (health.vitality_level - 50) / 50 * 1.5  # ±1.5°C
        tejo_heat = base_temp + vitality_modifier
        
        # Vayo - affected by fitness/energy
        vayo_tension = 50 - (health.energy_level * 0.3)  # Less energy = more tension
        vayo_looseness = 100 - vayo_tension
        
        return MahabhutaRupa(
            pathavi=PathaviCharacteristics(
                hardness_level=pathavi_hardness,
                softness_level=pathavi_softness
            ),
            apo=ApoCharacteristics(
                cohesion_level=apo_cohesion,
                fluidity_level=apo_fluidity
            ),
            tejo=TejoCharacteristics(
                heat_level=tejo_heat,
                cold_level=37.0 - tejo_heat if tejo_heat < 37.0 else 0,
                tejo_types=["usumatejo", "santappana"]  # Body heat + maturation
            ),
            vayo=VayoCharacteristics(
                tension_level=vayo_tension,
                looseness_level=vayo_looseness,
                vayo_types=["uddhangama", "adhogama", "assasapassasa"]  # Up/down/breath
            )
        )
    
    def _create_pasada_from_health(self, health: HealthScore) -> PasadaRupa:
        """Create sense organs based on health"""
        # All 5 sense organs affected by overall health
        base_sensitivity = 50 + (health.overall_health - 50) * 0.5
        
        return PasadaRupa(
            cakkhu_pasada=base_sensitivity,  # Eye
            sota_pasada=base_sensitivity,    # Ear
            ghana_pasada=base_sensitivity,   # Nose
            jivha_pasada=base_sensitivity,   # Tongue
            kaya_pasada=base_sensitivity     # Body
        )
    
    def _create_vinnatti_from_scores(self, voice: VoiceScore, demeanor: DemeanorScore) -> VinnattiRupa:
        """Create intimations (bodily/verbal expression)"""
        # Kaya Vinnatti - bodily expression from demeanor
        kaya_desc = f"{demeanor.posture_desc}, {demeanor.gait_desc}"
        if demeanor.typical_gestures:
            kaya_desc += f", gestures: {', '.join(demeanor.typical_gestures[:2])}"
        
        # Vaci Vinnatti - verbal expression from voice
        vaci_desc = f"{voice.voice_tone_desc}, {voice.speech_pattern_desc}"
        
        return VinnattiRupa(
            kaya_vinnatti=kaya_desc,
            vaci_vinnatti=vaci_desc
        )
    
    def _create_vikara_from_demeanor(self, demeanor: DemeanorScore) -> VikaraRupa:
        """
        Create Vikara (lightness, softness, wieldiness) from demeanor
        
        - Lahuta (Lightness): Inversely related to tension
        - Muduta (Softness): Related to approachability
        - Kammañata (Wieldiness): Related to movement quality
        """
        lahuta = 100 - demeanor.tension_level  # Less tension = more lightness
        muduta = demeanor.approachability  # More approachable = softer
        
        # Kammañata from movement quality description
        movement_quality_map = {
            "graceful": 80,
            "mindful": 75,
            "smooth": 70,
            "normal": 50,
            "jerky": 30,
            "sluggish": 25,
            "tense": 20
        }
        kammañata = movement_quality_map.get(demeanor.movement_quality.split(",")[0].strip(), 50)
        
        return VikaraRupa(
            lahuta=lahuta,
            muduta=muduta,
            kammañata=kammañata
        )
    
    def _create_lakkhana_from_health(self, health: HealthScore) -> LakkhanaRupa:
        """
        Create Lakkhana (characteristics) from health
        
        - Upacaya (Growth): Related to vitality
        - Santati (Continuity): Related to overall health
        - Jarata (Aging): Inversely related to vitality
        - Aniccata (Impermanence): Always present at moderate level
        """
        upacaya = health.vitality_level * 0.8  # Growth potential
        santati = health.overall_health * 0.9  # Continuity
        jarata = 100 - health.vitality_level  # Aging inversely related to vitality
        aniccata = 50.0  # Always present
        
        return LakkhanaRupa(
            upacaya=upacaya,
            santati=santati,
            jarata=jarata,
            aniccata=aniccata
        )
    
    def _create_jivita_from_health(self, health: HealthScore) -> JivitaRupa:
        """Create Jivita (life faculty) from health"""
        life_force = health.overall_health
        
        # Estimate lifespan (base 80 years + modifier)
        base_lifespan = 80
        lifespan = base_lifespan + health.lifespan_modifier
        
        return JivitaRupa(
            rupa_jivitindriya=life_force,
            life_span_years=max(0, lifespan)
        )


# =============================================================================
# APPEARANCE SYNTHESIZER
# =============================================================================

class AppearanceSynthesizer:
    """
    Synthesizes final ExternalCharacter profile
    Combines Kamma analysis + Rupa generation → ExternalCharacter
    """
    
    def __init__(self):
        self.rupa_generator = RupaAppearanceGenerator()
    
    def synthesize_appearance(
        self,
        model_id: str,
        kamma_profile: KammaAppearanceProfile,
        base_template: Optional[Dict] = None
    ) -> ExternalCharacter:
        """
        Main synthesis function
        
        Args:
            model_id: DigitalMindModel ID
            kamma_profile: KammaAppearanceProfile from analyzer
            base_template: Optional base template for genetic traits
            
        Returns:
            Complete ExternalCharacter with kamma-based appearance
        """
        logger.info(f"Synthesizing appearance for model: {model_id}")
        
        # Generate Rupa
        rupa_data = self.rupa_generator.generate_kamma_rupa(kamma_profile, base_template)
        
        # Map to ExternalCharacter
        external = self._map_to_external_character(
            model_id,
            kamma_profile,
            rupa_data,
            base_template
        )
        
        logger.info(f"Synthesis complete for {model_id}")
        
        return external
    
    def _map_to_external_character(
        self,
        model_id: str,
        profile: KammaAppearanceProfile,
        rupa: Dict[str, Any],
        template: Optional[Dict]
    ) -> ExternalCharacter:
        """
        Map KammaAppearanceProfile + Rupa → ExternalCharacter
        """
        health = profile.health_score
        voice = profile.voice_score
        demeanor = profile.demeanor_score
        
        # Physical Appearance
        age = template.get("age") if template else None
        age_appearance = self._determine_age_appearance(health, age)
        gender = template.get("gender") if template else None
        ethnicity = template.get("ethnicity") if template else None
        
        height = self._calculate_height(health, template)
        weight = self._calculate_weight(health, template)
        body_type = health.body_type_tendency
        
        # Facial Features
        face_shape = template.get("face_shape") if template else self._default_face_shape(demeanor)
        eye_color = template.get("eye_color") if template else "brown"
        hair_color = template.get("hair_color") if template else "black"
        hair_style = template.get("hair_style") if template else "medium length"
        skin_tone = health.skin_tone_desc
        
        distinctive_features = profile.distinctive_features.copy()
        
        # Style & Presentation
        fashion_style = self._determine_fashion_style(health, demeanor)
        color_palette = self._determine_color_palette(demeanor)
        accessories = template.get("accessories", []) if template else []
        
        # Physical Condition
        fitness_level = health.fitness_level
        health_status = health.health_status_desc
        scars_wounds = template.get("scars_wounds", []) if template else []
        
        # Movement & Body Language
        posture = demeanor.posture_desc
        gait = demeanor.gait_desc
        gestures = demeanor.typical_gestures
        
        # Voice & Speech
        voice_tone = voice.voice_tone_desc
        speech_pattern = voice.speech_pattern_desc
        accent = template.get("accent") if template else None
        catchphrase = template.get("catchphrase") if template else None
        
        # Habits & Mannerisms
        nervous_habits = demeanor.nervous_habits
        signature_gesture = gestures[0] if gestures else None
        quirks = template.get("quirks", []) if template else []
        
        # Social Presence
        first_impression = demeanor.first_impression
        charisma_level = demeanor.charisma / 10.0  # Convert to 0-10 scale
        approachability = demeanor.approachability / 10.0
        
        # Skills (from template if available)
        combat_skills = template.get("combat_skills", []) if template else []
        artistic_skills = template.get("artistic_skills", []) if template else []
        practical_skills = template.get("practical_skills", []) if template else []
        supernatural_abilities = template.get("supernatural_abilities", []) if template else []
        
        # Environment
        preferred_environment = template.get("preferred_environment") if template else None
        comfort_zone = template.get("comfort_zone") if template else None
        
        return ExternalCharacter(
            age=age,
            age_appearance=age_appearance,
            gender=gender,
            ethnicity=ethnicity,
            height=height,
            weight=weight,
            body_type=body_type,
            face_shape=face_shape,
            eye_color=eye_color,
            hair_color=hair_color,
            hair_style=hair_style,
            skin_tone=skin_tone,
            distinctive_features=distinctive_features,
            fashion_style=fashion_style,
            color_palette=color_palette,
            accessories=accessories,
            fitness_level=fitness_level,
            health_status=health_status,
            scars_wounds=scars_wounds,
            posture=posture,
            gait=gait,
            gestures=gestures,
            voice_tone=voice_tone,
            speech_pattern=speech_pattern,
            accent=accent,
            catchphrase=catchphrase,
            nervous_habits=nervous_habits,
            signature_gesture=signature_gesture,
            quirks=quirks,
            first_impression=first_impression,
            charisma_level=charisma_level,
            approachability=approachability,
            combat_skills=combat_skills,
            artistic_skills=artistic_skills,
            practical_skills=practical_skills,
            supernatural_abilities=supernatural_abilities,
            preferred_environment=preferred_environment,
            comfort_zone=comfort_zone
        )
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _determine_age_appearance(self, health: HealthScore, actual_age: Optional[int]) -> str:
        """Determine if character looks younger/older than actual age"""
        if not actual_age:
            return "unknown"
        
        vitality = health.vitality_level
        
        if vitality >= 75:
            return "younger than actual age"
        elif vitality <= 30:
            return "older than actual age"
        else:
            return "actual age"
    
    def _calculate_height(self, health: HealthScore, template: Optional[Dict]) -> Optional[float]:
        """Calculate height based on health and genetics"""
        if template and "height" in template:
            base_height = template["height"]
        else:
            # Default average height
            base_height = 170.0  # cm
        
        # Health affects height slightly (±5cm)
        health_modifier = (health.overall_health - 50) / 50 * 5
        
        return round(base_height + health_modifier, 1)
    
    def _calculate_weight(self, health: HealthScore, template: Optional[Dict]) -> Optional[float]:
        """Calculate weight based on health and body type"""
        if template and "weight" in template:
            base_weight = template["weight"]
        else:
            # Default average weight
            base_weight = 65.0  # kg
        
        # Body strength affects weight
        strength_modifier = (health.body_strength - 50) / 50 * 10
        
        return round(base_weight + strength_modifier, 1)
    
    def _default_face_shape(self, demeanor: DemeanorScore) -> str:
        """Determine default face shape based on demeanor"""
        if demeanor.tension_level >= 70:
            return "angular, sharp"
        elif demeanor.approachability >= 75:
            return "round, soft"
        else:
            return "oval"
    
    def _determine_fashion_style(self, health: HealthScore, demeanor: DemeanorScore) -> Optional[str]:
        """Determine fashion style from health and demeanor"""
        if health.overall_health >= 70 and demeanor.charisma >= 70:
            return "well-maintained, confident"
        elif health.overall_health <= 35:
            return "simple, practical"
        elif demeanor.peacefulness >= 75:
            return "simple, comfortable, mindful"
        else:
            return "casual, everyday"
    
    def _determine_color_palette(self, demeanor: DemeanorScore) -> List[str]:
        """Determine color preferences from demeanor"""
        colors = []
        
        if demeanor.peacefulness >= 75:
            colors.extend(["white", "beige", "earth tones"])
        elif demeanor.tension_level >= 70:
            colors.extend(["dark colors", "black", "grey"])
        elif demeanor.charisma >= 75:
            colors.extend(["warm colors", "vibrant tones"])
        else:
            colors.extend(["neutral colors"])
        
        return colors


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def synthesize_from_model(
    profile_dict: Dict[str, Any],
    base_template: Optional[Dict] = None
) -> ExternalCharacter:
    """
    Complete pipeline: DigitalMindModel → ExternalCharacter
    
    Args:
        profile_dict: Complete DigitalMindModel profile dictionary
        base_template: Optional genetic/cultural baseline
        
    Returns:
        Complete ExternalCharacter with kamma-based appearance
        
    Example:
        >>> profile = get_digital_mind_model("peace-mind-001")
        >>> external = synthesize_from_model(profile)
        >>> print(external.skin_tone)
        'radiant, healthy glow'
    """
    from modules.kamma_appearance_analyzer import analyze_model_appearance
    
    # Step 1: Analyze kamma
    kamma_profile = analyze_model_appearance(profile_dict)
    
    # Step 2: Synthesize appearance
    synthesizer = AppearanceSynthesizer()
    external = synthesizer.synthesize_appearance(
        model_id=profile_dict.get("model_id", "unknown"),
        kamma_profile=kamma_profile,
        base_template=base_template
    )
    
    return external
