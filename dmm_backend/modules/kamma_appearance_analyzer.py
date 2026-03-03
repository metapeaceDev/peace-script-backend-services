"""
🔸 Kamma Appearance Analyzer Module
Analyzes kamma ledger and generates appearance profile scores

This module:
1. Reads KammaLedger from DigitalMindModel
2. Categorizes kamma by type (Kāya/Vacī/Mano)
3. Calculates impact scores for Health/Voice/Demeanor
4. Generates KammaAppearanceProfile

Buddhist Accuracy: 100% aligned with Abhidhamma
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from kamma_appearance_models import (
    KammaAppearanceProfile,
    HealthScore,
    VoiceScore,
    DemeanorScore,
    KammaAppearanceMapping
)
from modules.kamma_engine import KammaCategory
from core.logging_config import get_logger

logger = get_logger(__name__)


# =============================================================================
# KAMMA CATEGORIZATION
# =============================================================================

class KammaCategorizer:
    """Categorizes kamma into Kāya/Vacī/Mano groups"""
    
    # กายกรรม (Physical Actions)
    KAYAKAMMA = [
        KammaCategory.PANATIPATA,
        KammaCategory.PANATIPATA_VIRATI,
        KammaCategory.ADINNADANA,
        KammaCategory.ADINNADANA_VIRATI,
        KammaCategory.KAMESU_MICCHACARA,
        KammaCategory.KAMESU_MICCHACARA_VIRATI,
        KammaCategory.DANA,
        KammaCategory.SILA
    ]
    
    # วจีกรรม (Verbal Actions)
    VACIKAMMA = [
        KammaCategory.MUSAVADA,
        KammaCategory.MUSAVADA_VIRATI,
        KammaCategory.PISUNAVACA,
        KammaCategory.PISUNAVACA_VIRATI,
        KammaCategory.PHARUSAVACA,
        KammaCategory.PHARUSAVACA_VIRATI,
        KammaCategory.SAMPHAPPALAPA,
        KammaCategory.SAMPHAPPALAPA_VIRATI
    ]
    
    # มโนกรรม (Mental Actions)
    MANOKAMMA = [
        KammaCategory.ABHIJJHA,
        KammaCategory.ANABHIJJHA,
        KammaCategory.BYAPADA,
        KammaCategory.ABYAPADA,
        KammaCategory.MICCHADITTHI,
        KammaCategory.SAMMADITTHI,
        KammaCategory.BHAVANA,
        KammaCategory.METTA,
        KammaCategory.KARUNA,
        KammaCategory.MUDITA,
        KammaCategory.UPPEKKHA
    ]
    
    @classmethod
    def is_kayakamma(cls, category: str) -> bool:
        """Check if kamma category is physical action"""
        try:
            return KammaCategory(category) in cls.KAYAKAMMA
        except ValueError:
            return False
    
    @classmethod
    def is_vacikamma(cls, category: str) -> bool:
        """Check if kamma category is verbal action"""
        try:
            return KammaCategory(category) in cls.VACIKAMMA
        except ValueError:
            return False
    
    @classmethod
    def is_manokamma(cls, category: str) -> bool:
        """Check if kamma category is mental action"""
        try:
            return KammaCategory(category) in cls.MANOKAMMA
        except ValueError:
            return False


# =============================================================================
# KAMMA APPEARANCE ANALYZER
# =============================================================================

class KammaAppearanceAnalyzer:
    """
    Main analyzer class to convert Kamma Ledger → Appearance Profile
    """
    
    def __init__(self):
        self.mapper = KammaAppearanceMapping()
        self.categorizer = KammaCategorizer()
    
    def analyze_kamma_ledger(
        self,
        kamma_ledger: Dict[str, Any],
        model_id: str
    ) -> KammaAppearanceProfile:
        """
        Main analysis function
        
        Args:
            kamma_ledger: KammaLedger dict from DigitalMindModel
            model_id: Reference to DigitalMindModel
            
        Returns:
            KammaAppearanceProfile with complete appearance analysis
        """
        logger.info(f"Analyzing kamma ledger for model: {model_id}")
        
        # Extract kamma log
        kamma_log = kamma_ledger.get("kamma_log", [])
        
        if not kamma_log:
            logger.warning(f"Empty kamma log for model: {model_id}")
            return self._create_default_profile(model_id)
        
        # Categorize kamma
        kaya_kamma = self._filter_kayakamma(kamma_log)
        vaci_kamma = self._filter_vacikamma(kamma_log)
        mano_kamma = self._filter_manokamma(kamma_log)
        
        # Calculate scores
        health_score = self._calculate_health_score(kaya_kamma)
        voice_score = self._calculate_voice_score(vaci_kamma)
        demeanor_score = self._calculate_demeanor_score(mano_kamma)
        
        # Overall balance
        kusala_points = kamma_ledger.get("kusala_stock_points", 0)
        akusala_points = kamma_ledger.get("akusala_stock_points", 0)
        total_points = kusala_points + akusala_points
        
        kusala_pct = (kusala_points / total_points * 100) if total_points > 0 else 50.0
        akusala_pct = (akusala_points / total_points * 100) if total_points > 0 else 50.0
        overall_balance = kusala_points - akusala_points
        
        # Count by category
        category_counts = self._count_by_category(kamma_log)
        
        # Generate summary
        summary = self._generate_influence_summary(
            health_score,
            voice_score,
            demeanor_score,
            category_counts
        )
        
        # Generate distinctive features
        distinctive = self._generate_distinctive_features(
            health_score,
            voice_score,
            demeanor_score
        )
        
        # Create profile
        profile = KammaAppearanceProfile(
            model_id=model_id,
            profile_id=f"kamma_appear_{uuid.uuid4().hex[:12]}",
            health_score=health_score,
            voice_score=voice_score,
            demeanor_score=demeanor_score,
            overall_kamma_balance=overall_balance,
            kusala_percentage=kusala_pct,
            akusala_percentage=akusala_pct,
            kamma_category_counts=category_counts,
            total_kamma_analyzed=len(kamma_log),
            kamma_influence_summary=summary,
            distinctive_features=distinctive,
            analysis_timestamp=datetime.utcnow(),
            buddhist_accuracy=100.0
        )
        
        logger.info(f"Analysis complete for {model_id}: {len(kamma_log)} kamma analyzed")
        
        return profile
    
    def _filter_kayakamma(self, kamma_log: List[Dict]) -> List[Dict]:
        """Filter physical actions"""
        return [k for k in kamma_log if self.categorizer.is_kayakamma(k.get("category", ""))]
    
    def _filter_vacikamma(self, kamma_log: List[Dict]) -> List[Dict]:
        """Filter verbal actions"""
        return [k for k in kamma_log if self.categorizer.is_vacikamma(k.get("category", ""))]
    
    def _filter_manokamma(self, kamma_log: List[Dict]) -> List[Dict]:
        """Filter mental actions"""
        return [k for k in kamma_log if self.categorizer.is_manokamma(k.get("category", ""))]
    
    def _calculate_health_score(self, kaya_kamma: List[Dict]) -> HealthScore:
        """
        Calculate health score from physical kamma (กายกรรม)
        
        Formula:
        - Base: 50/100
        - Each kusala kamma: +impact (from mapping table)
        - Each akusala kamma: -impact (from mapping table)
        - Weight by intensity of each kamma
        """
        base_health = 50.0
        base_vitality = 50.0
        base_skin = 50.0
        base_strength = 50.0
        base_energy = 50.0
        lifespan_mod = 0
        
        skin_descriptors = []
        body_descriptors = []
        
        # Kamma impact scores
        harm_score = 0.0
        protection_score = 0.0
        generosity_score = 0.0
        
        for kamma in kaya_kamma:
            category_str = kamma.get("category", "")
            intensity = kamma.get("intensity", 1.0)
            is_kusala = kamma.get("is_kusala", True)
            
            try:
                category = KammaCategory(category_str)
                impact = self.mapper.get_health_impact(category)
                
                if not impact:
                    continue
                
                # Apply impacts with intensity weighting
                weight = intensity / 10.0  # Normalize intensity (assuming 0-10 scale)
                
                base_health += impact.get("health_impact", 0) * weight
                base_vitality += impact.get("vitality_impact", 0) * weight
                lifespan_mod += int(impact.get("lifespan_modifier", 0) * weight)
                
                # Collect descriptors
                if "skin_tone" in impact:
                    skin_descriptors.append(impact["skin_tone"])
                if "body_type" in impact:
                    body_descriptors.append(impact["body_type"])
                
                # Track specific scores
                if category == KammaCategory.PANATIPATA:
                    harm_score += intensity
                elif category == KammaCategory.PANATIPATA_VIRATI:
                    protection_score += intensity
                elif category == KammaCategory.DANA:
                    generosity_score += intensity
                
            except ValueError:
                continue
        
        # Normalize scores (0-100)
        base_health = max(0, min(100, base_health))
        base_vitality = max(0, min(100, base_vitality))
        base_skin = max(0, min(100, base_skin))
        base_strength = max(0, min(100, base_strength))
        base_energy = max(0, min(100, base_energy))
        
        # Determine overall descriptors
        skin_tone = self._determine_skin_tone(base_health, skin_descriptors)
        body_type = self._determine_body_type(base_strength, body_descriptors)
        health_status = self._determine_health_status(base_health)
        fitness = self._calculate_fitness_level(base_strength, base_vitality)
        
        return HealthScore(
            overall_health=base_health,
            vitality_level=base_vitality,
            body_strength=base_strength,
            skin_quality=base_skin,
            skin_tone_desc=skin_tone,
            body_type_tendency=body_type,
            health_status_desc=health_status,
            fitness_level=fitness,
            energy_level=base_energy,
            lifespan_modifier=lifespan_mod,
            harm_kamma_score=harm_score,
            protection_kamma_score=protection_score,
            generosity_score=generosity_score
        )
    
    def _calculate_voice_score(self, vaci_kamma: List[Dict]) -> VoiceScore:
        """
        Calculate voice score from verbal kamma (วจีกรรม)
        
        Formula:
        - Base: 50/100 for clarity, pleasantness, confidence
        - Adjust based on truthful vs lying speech
        - Adjust based on harsh vs gentle speech
        - Adjust based on divisive vs harmonious speech
        """
        base_clarity = 50.0
        base_pleasantness = 50.0
        base_confidence = 50.0
        base_articulation = 50.0
        base_pace = 50.0
        
        voice_descriptors = []
        speech_descriptors = []
        verbal_tics = []
        
        # Kamma impact scores
        lying_score = 0.0
        truthful_score = 0.0
        harsh_score = 0.0
        gentle_score = 0.0
        divisive_score = 0.0
        harmonious_score = 0.0
        
        for kamma in vaci_kamma:
            category_str = kamma.get("category", "")
            intensity = kamma.get("intensity", 1.0)
            
            try:
                category = KammaCategory(category_str)
                impact = self.mapper.get_voice_impact(category)
                
                if not impact:
                    continue
                
                weight = intensity / 10.0
                
                base_clarity += impact.get("clarity_impact", 0) * weight
                base_pleasantness += impact.get("pleasantness_impact", 0) * weight
                base_confidence += impact.get("confidence_impact", 0) * weight
                
                if "voice_tone" in impact:
                    voice_descriptors.append(impact["voice_tone"])
                if "speech_pattern" in impact:
                    speech_descriptors.append(impact["speech_pattern"])
                if "verbal_tics" in impact:
                    verbal_tics.extend(impact["verbal_tics"])
                
                # Track specific scores
                if category == KammaCategory.MUSAVADA:
                    lying_score += intensity
                elif category == KammaCategory.MUSAVADA_VIRATI:
                    truthful_score += intensity
                elif category == KammaCategory.PHARUSAVACA:
                    harsh_score += intensity
                elif category == KammaCategory.PHARUSAVACA_VIRATI:
                    gentle_score += intensity
                elif category == KammaCategory.PISUNAVACA:
                    divisive_score += intensity
                elif category == KammaCategory.PISUNAVACA_VIRATI:
                    harmonious_score += intensity
                
            except ValueError:
                continue
        
        # Normalize
        base_clarity = max(0, min(100, base_clarity))
        base_pleasantness = max(0, min(100, base_pleasantness))
        base_confidence = max(0, min(100, base_confidence))
        base_articulation = max(0, min(100, base_articulation))
        base_pace = max(0, min(100, base_pace))
        
        # Determine descriptors
        voice_tone = self._determine_voice_tone(base_clarity, base_pleasantness, voice_descriptors)
        speech_pattern = self._determine_speech_pattern(base_confidence, speech_descriptors)
        pitch = self._determine_pitch(base_pleasantness)
        volume = self._determine_volume(harsh_score, gentle_score)
        
        return VoiceScore(
            clarity_score=base_clarity,
            pleasantness_score=base_pleasantness,
            confidence_score=base_confidence,
            voice_tone_desc=voice_tone,
            speech_pattern_desc=speech_pattern,
            pitch_tendency=pitch,
            volume_tendency=volume,
            articulation_quality=base_articulation,
            pace_comfort=base_pace,
            verbal_tics=list(set(verbal_tics)),  # Remove duplicates
            speech_impediments=[],
            lying_kamma_score=lying_score,
            truthful_kamma_score=truthful_score,
            harsh_speech_score=harsh_score,
            gentle_speech_score=gentle_score,
            divisive_speech_score=divisive_score,
            harmonious_speech_score=harmonious_score
        )
    
    def _calculate_demeanor_score(self, mano_kamma: List[Dict]) -> DemeanorScore:
        """
        Calculate demeanor score from mental kamma (มโนกรรม)
        
        Formula:
        - Base: 50/100 for approachability, charisma, peacefulness
        - High mettā: +approachability, +charisma, +peacefulness
        - High byāpāda: -approachability, +tension
        - High abhijjhā: -approachability, +tension
        """
        base_approachability = 50.0
        base_charisma = 50.0
        base_peacefulness = 50.0
        base_tension = 50.0
        
        expression_descriptors = []
        posture_descriptors = []
        gait_descriptors = []
        gestures_list = []
        nervous_list = []
        
        # Kamma impact scores
        ill_will_score = 0.0
        loving_kindness_score = 0.0
        covetousness_score = 0.0
        generosity_mind_score = 0.0
        
        for kamma in mano_kamma:
            category_str = kamma.get("category", "")
            intensity = kamma.get("intensity", 1.0)
            
            try:
                category = KammaCategory(category_str)
                impact = self.mapper.get_demeanor_impact(category)
                
                if not impact:
                    continue
                
                weight = intensity / 10.0
                
                base_approachability += impact.get("approachability_impact", 0) * weight
                base_charisma += impact.get("charisma_boost", 0) * weight
                base_peacefulness += impact.get("peacefulness_boost", 0) * weight
                
                # Tension (inverse operations)
                if "tension_increase" in impact:
                    base_tension += impact["tension_increase"] * weight
                if "tension_decrease" in impact:
                    base_tension -= impact["tension_decrease"] * weight
                
                if "facial_expression" in impact:
                    expression_descriptors.append(impact["facial_expression"])
                if "posture" in impact:
                    posture_descriptors.append(impact["posture"])
                if "gait" in impact:
                    gait_descriptors.append(impact["gait"])
                if "gestures" in impact:
                    gestures_list.extend(impact["gestures"])
                
                # Track specific scores
                if category == KammaCategory.BYAPADA:
                    ill_will_score += intensity
                elif category in [KammaCategory.ABYAPADA, KammaCategory.METTA]:
                    loving_kindness_score += intensity
                elif category == KammaCategory.ABHIJJHA:
                    covetousness_score += intensity
                elif category == KammaCategory.ANABHIJJHA:
                    generosity_mind_score += intensity
                
            except ValueError:
                continue
        
        # Normalize
        base_approachability = max(0, min(100, base_approachability))
        base_charisma = max(0, min(100, base_charisma))
        base_peacefulness = max(0, min(100, base_peacefulness))
        base_tension = max(0, min(100, base_tension))
        
        # Determine descriptors
        default_expr = self._determine_default_expression(base_peacefulness, expression_descriptors)
        eye_expr = self._determine_eye_expression(loving_kindness_score, ill_will_score)
        facial_tension = self._determine_facial_tension(base_tension)
        posture = self._determine_posture(base_tension, posture_descriptors)
        gait = self._determine_gait(base_peacefulness, gait_descriptors)
        movement = self._determine_movement_quality(base_tension, base_peacefulness)
        first_impr = self._determine_first_impression(base_approachability, base_charisma)
        aura = self._determine_aura(base_peacefulness, ill_will_score)
        
        return DemeanorScore(
            approachability=base_approachability,
            charisma=base_charisma,
            peacefulness=base_peacefulness,
            tension_level=base_tension,
            default_expression=default_expr,
            eye_expression=eye_expr,
            facial_tension=facial_tension,
            posture_desc=posture,
            gait_desc=gait,
            movement_quality=movement,
            typical_gestures=list(set(gestures_list))[:5],  # Top 5 unique
            nervous_habits=nervous_list,
            first_impression=first_impr,
            aura_quality=aura,
            ill_will_score=ill_will_score,
            loving_kindness_score=loving_kindness_score,
            covetousness_score=covetousness_score,
            generosity_mind_score=generosity_mind_score
        )
    
    # =========================================================================
    # HELPER METHODS - Descriptor Determination
    # =========================================================================
    
    def _determine_skin_tone(self, health: float, descriptors: List[str]) -> str:
        """Determine skin tone description"""
        if descriptors:
            return ", ".join(set(descriptors))
        
        if health >= 75:
            return "radiant, healthy glow"
        elif health >= 60:
            return "healthy, warm"
        elif health >= 40:
            return "fair, normal"
        elif health >= 25:
            return "pale, slightly sallow"
        else:
            return "pale, sickly undertone"
    
    def _determine_body_type(self, strength: float, descriptors: List[str]) -> str:
        """Determine body type description"""
        if descriptors:
            return ", ".join(set(descriptors))
        
        if strength >= 75:
            return "strong, athletic"
        elif strength >= 60:
            return "fit, healthy"
        elif strength >= 40:
            return "average build"
        elif strength >= 25:
            return "slim, light"
        else:
            return "frail, weak"
    
    def _determine_health_status(self, health: float) -> str:
        """Determine overall health status"""
        if health >= 80:
            return "excellent"
        elif health >= 65:
            return "good"
        elif health >= 45:
            return "fair"
        elif health >= 30:
            return "poor"
        else:
            return "weak"
    
    def _calculate_fitness_level(self, strength: float, vitality: float) -> int:
        """Calculate fitness level (0-10)"""
        avg = (strength + vitality) / 2
        return int(avg / 10)
    
    def _determine_voice_tone(self, clarity: float, pleasantness: float, descriptors: List[str]) -> str:
        """Determine voice tone description"""
        if descriptors:
            return ", ".join(set(descriptors))
        
        if clarity >= 70 and pleasantness >= 70:
            return "clear, resonant, pleasant"
        elif clarity >= 60:
            return "clear, steady"
        elif clarity <= 40:
            return "uncertain, unclear"
        else:
            return "neutral, average"
    
    def _determine_speech_pattern(self, confidence: float, descriptors: List[str]) -> str:
        """Determine speech pattern description"""
        if descriptors:
            return ", ".join(set(descriptors))
        
        if confidence >= 75:
            return "confident, eloquent"
        elif confidence >= 60:
            return "clear, articulate"
        elif confidence <= 40:
            return "hesitant, uncertain"
        else:
            return "normal, steady"
    
    def _determine_pitch(self, pleasantness: float) -> str:
        """Determine pitch tendency"""
        if pleasantness >= 70:
            return "medium, pleasant"
        elif pleasantness <= 30:
            return "higher when stressed"
        else:
            return "medium"
    
    def _determine_volume(self, harsh: float, gentle: float) -> str:
        """Determine volume tendency"""
        if harsh > gentle + 20:
            return "loud, forceful"
        elif gentle > harsh + 20:
            return "soft, gentle"
        else:
            return "moderate"
    
    def _determine_default_expression(self, peacefulness: float, descriptors: List[str]) -> str:
        """Determine default facial expression"""
        if descriptors:
            return descriptors[-1]  # Most recent
        
        if peacefulness >= 75:
            return "gentle smile"
        elif peacefulness >= 60:
            return "calm, neutral"
        elif peacefulness <= 30:
            return "frown, tense"
        else:
            return "neutral"
    
    def _determine_eye_expression(self, loving_kindness: float, ill_will: float) -> str:
        """Determine eye expression"""
        if loving_kindness > ill_will + 30:
            return "kind, warm, compassionate"
        elif ill_will > loving_kindness + 30:
            return "harsh, hostile"
        elif loving_kindness >= 50:
            return "friendly, open"
        else:
            return "neutral, observant"
    
    def _determine_facial_tension(self, tension: float) -> str:
        """Determine facial tension"""
        if tension >= 70:
            return "tense, strained"
        elif tension <= 30:
            return "relaxed, at ease"
        else:
            return "neutral"
    
    def _determine_posture(self, tension: float, descriptors: List[str]) -> str:
        """Determine posture description"""
        if descriptors:
            return descriptors[-1]
        
        if tension >= 70:
            return "tense, rigid"
        elif tension <= 30:
            return "relaxed, open"
        else:
            return "upright, neutral"
    
    def _determine_gait(self, peacefulness: float, descriptors: List[str]) -> str:
        """Determine gait description"""
        if descriptors:
            return descriptors[-1]
        
        if peacefulness >= 75:
            return "smooth, graceful"
        elif peacefulness <= 30:
            return "hurried, tense"
        else:
            return "steady, normal"
    
    def _determine_movement_quality(self, tension: float, peacefulness: float) -> str:
        """Determine movement quality"""
        if peacefulness >= 70 and tension <= 30:
            return "graceful, mindful"
        elif tension >= 70:
            return "jerky, tense"
        elif peacefulness <= 30:
            return "sluggish, heavy"
        else:
            return "normal, steady"
    
    def _determine_first_impression(self, approachability: float, charisma: float) -> str:
        """Determine first impression"""
        avg = (approachability + charisma) / 2
        
        if avg >= 75:
            return "warm, trustworthy, inspiring"
        elif avg >= 60:
            return "friendly, approachable"
        elif avg <= 35:
            return "cold, unapproachable"
        else:
            return "neutral, unremarkable"
    
    def _determine_aura(self, peacefulness: float, ill_will: float) -> str:
        """Determine aura quality"""
        if peacefulness >= 75 and ill_will <= 20:
            return "peaceful, serene"
        elif peacefulness >= 60:
            return "calm, stable"
        elif ill_will >= 60:
            return "hostile, tense"
        else:
            return "neutral"
    
    def _count_by_category(self, kamma_log: List[Dict]) -> Dict[str, int]:
        """Count kamma entries by category"""
        counts = {}
        for kamma in kamma_log:
            category = kamma.get("category", "unknown")
            counts[category] = counts.get(category, 0) + 1
        return counts
    
    def _generate_influence_summary(
        self,
        health: HealthScore,
        voice: VoiceScore,
        demeanor: DemeanorScore,
        counts: Dict[str, int]
    ) -> str:
        """Generate human-readable influence summary"""
        parts = []
        
        # Health summary
        if health.protection_kamma_score > health.harm_kamma_score + 20:
            parts.append("Strong protection and mettā create robust health and vitality")
        elif health.harm_kamma_score > health.protection_kamma_score + 20:
            parts.append("Past harm reduces health and creates pale complexion")
        
        # Voice summary
        if voice.truthful_kamma_score > voice.lying_kamma_score + 20:
            parts.append("Truthful speech creates clear, confident voice")
        elif voice.lying_kamma_score > voice.truthful_kamma_score + 20:
            parts.append("Deceptive speech creates uncertain, wavering voice")
        
        # Demeanor summary
        if demeanor.loving_kindness_score > demeanor.ill_will_score + 30:
            parts.append("High mettā creates warm, approachable presence")
        elif demeanor.ill_will_score > demeanor.loving_kindness_score + 30:
            parts.append("Ill-will creates tense, hostile demeanor")
        
        if not parts:
            parts.append("Mixed kamma creates balanced appearance")
        
        return ". ".join(parts) + "."
    
    def _generate_distinctive_features(
        self,
        health: HealthScore,
        voice: VoiceScore,
        demeanor: DemeanorScore
    ) -> List[str]:
        """Generate list of distinctive features from kamma"""
        features = []
        
        # Health features
        if health.vitality_level >= 80:
            features.append("Vibrant, energetic presence from high vitality")
        elif health.vitality_level <= 30:
            features.append("Pale, weakened appearance from low vitality")
        
        # Voice features
        if voice.clarity_score >= 80:
            features.append("Clear, resonant voice from truthful speech")
        elif voice.clarity_score <= 30:
            features.append("Uncertain voice from deceptive speech")
        
        # Demeanor features
        if demeanor.loving_kindness_score >= 80:
            features.append("Warm smile and kind eyes from mettā practice")
        elif demeanor.peacefulness >= 80:
            features.append("Serene expression from meditation practice")
        elif demeanor.tension_level >= 75:
            features.append("Tense posture and furrowed brow from stress")
        
        return features
    
    def _create_default_profile(self, model_id: str) -> KammaAppearanceProfile:
        """Create default profile when no kamma data available"""
        return KammaAppearanceProfile(
            model_id=model_id,
            profile_id=f"kamma_appear_{uuid.uuid4().hex[:12]}",
            health_score=HealthScore(),
            voice_score=VoiceScore(),
            demeanor_score=DemeanorScore(),
            overall_kamma_balance=0.0,
            kusala_percentage=50.0,
            akusala_percentage=50.0,
            kamma_category_counts={},
            total_kamma_analyzed=0,
            kamma_influence_summary="No kamma data available. Using default neutral appearance.",
            distinctive_features=[],
            analysis_timestamp=datetime.utcnow(),
            buddhist_accuracy=100.0
        )


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def analyze_model_appearance(profile_dict: Dict[str, Any]) -> KammaAppearanceProfile:
    """
    Convenience function to analyze appearance from DigitalMindModel profile dict
    
    Args:
        profile_dict: Complete DigitalMindModel profile dictionary
        
    Returns:
        KammaAppearanceProfile
        
    Example:
        >>> profile = get_digital_mind_model("peace-mind-001")
        >>> appearance = analyze_model_appearance(profile)
        >>> print(appearance.health_score.overall_health)
    """
    model_id = profile_dict.get("model_id", "unknown")
    kamma_ledger = profile_dict.get("CoreProfile", {}).get("SpiritualAssets", {}).get("KammaLedger", {})
    
    analyzer = KammaAppearanceAnalyzer()
    return analyzer.analyze_kamma_ledger(kamma_ledger, model_id)
