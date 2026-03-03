"""
Kamma Engine
============
Simulates Buddhist karmic mechanics - creation, storage, ripening, and delivery of kamma results.

Core Principles:
1. **Cetanā is Kamma**: Volition (cetanā cetasika) in kusala/akusala cittas creates kamma
2. **Kamma Ripens as Vipāka**: Good/bad actions ripen as pleasant/unpleasant results
3. **Four Types of Kamma by Timing**:
   - Diṭṭhadhamma-vedanīya: Ripens in this life
   - Upapajja-vedanīya: Ripens in next life
   - Aparāpariya-vedanīya: Ripens in future lives
   - Ahosi: Becomes ineffective (never ripens)

4. **Four Types of Kamma by Function**:
   - Janaka (Reproductive): Causes rebirth
   - Upatthambhaka (Supportive): Supports existing results
   - Upapīḷaka (Obstructive): Blocks other kamma from ripening
   - Upaghātaka (Destructive): Destroys weak kamma

5. **Five Niyāmas (Natural Laws)**:
   - Utu-niyāma: Physical laws
   - Bīja-niyāma: Biological laws  
   - Citta-niyāma: Mental laws
   - **Kamma-niyāma**: Moral causation (this engine)
   - Dhamma-niyāma: Buddhist natural laws

References:
- Abhidhammatthasaṅgaha Chapter 5: Vīthimuttasaṅgaha
- Visuddhimagga Chapter XVII: Description of Consciousness and Matter
- docs/PATICCASAMUPPADA_ANALYSIS.md: Link 10 (Bhava) → Link 11 (Jāti)
"""

from enum import Enum
from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field, validator
from datetime import datetime, timedelta
from uuid import uuid4

from citta_cetasika_models import (
    CittaMoment, Citta, CittaType, CittaCategory,
    Hetu, Vedana
)


# ============================================================================
# ENUMS: Kamma Classifications
# ============================================================================

class KammaType(str, Enum):
    """Ethical type of kamma"""
    KUSALA = "kusala"  # Wholesome - produces pleasant results
    AKUSALA = "akusala"  # Unwholesome - produces unpleasant results


class KammaTiming(str, Enum):
    """When kamma will ripen (4 types by timing)"""
    DITTHADHAMMA_VEDANIYA = "diṭṭhadhamma_vedanīya"  # This life (strongest/weakest)
    UPAPAJJA_VEDANIYA = "upapajja_vedanīya"  # Next life only
    APARA_PARIYA_VEDANIYA = "aparāpariya_vedanīya"  # Future lives (2+)
    AHOSI = "ahosi"  # Ineffective - never ripens


class KammaFunction(str, Enum):
    """Function of kamma (4 types by function)"""
    JANAKA = "janaka"  # Reproductive - causes rebirth, major life events
    UPATTHAMBHAKA = "upatthambhaka"  # Supportive - sustains results
    UPAPILAKA = "upapīḷaka"  # Obstructive - blocks other kamma
    UPAGHĀTAKA = "upaghātaka"  # Destructive - destroys weak kamma


class KammaStrength(str, Enum):
    """Strength/weight of kamma (determines priority)"""
    GARUKA = "garuka"  # Weighty - very strong (e.g., killing parent, jhāna, path attainment)
    ASANNA = "āsanna"  # Proximate - near death moment (death-proximate kamma)
    ACINNA = "āciṇṇa"  # Habitual - repeated frequently
    KATATTA = "kaṭattā"  # Reserve - weak, fills gaps


class RipeningCondition(str, Enum):
    """Conditions that trigger kamma ripening"""
    TIME_BASED = "time"  # Based on timing (this life, next life, future)
    SUPPORT_BASED = "support"  # Needs supporting conditions
    OBSTRUCTION_BASED = "obstruction"  # Can be blocked by other kamma
    DESTRUCTION_BASED = "destruction"  # Can be destroyed by powerful opposite kamma


class VipakaType(str, Enum):
    """Type of result delivered"""
    REBIRTH_LINKING = "paṭisandhi"  # Rebirth-linking consciousness
    BHAVANGA = "bhavaṅga"  # Life-continuum (during life)
    SENSE_RESULT = "sense_vipāka"  # Pleasant/unpleasant sense experiences
    MENTAL_RESULT = "mental_vipāka"  # Mental pleasure/pain
    LIFE_SPAN = "āyu"  # Length of life
    BODY_QUALITY = "vaṇṇa"  # Physical beauty/ugliness
    HEALTH = "ārogya"  # Health/illness
    WEALTH = "bhoga"  # Wealth/poverty
    WISDOM = "paññā"  # Intelligence/dullness


# ============================================================================
# KAMMA RECORD MODELS
# ============================================================================

class KammaRecord(BaseModel):
    """
    Record of one kamma created by a citta moment.
    
    When a kusala or akusala citta moment arises during Javana stage,
    the strong volition (cetanā) creates kamma that will ripen as vipāka.
    
    Attributes:
        kamma_id: Unique identifier
        created_at: Timestamp of creation
        citta_moment: The citta moment that created this kamma
        kamma_type: kusala or akusala
        potency: Strength 0.0-1.0
        timing: When it will ripen
        function: What role it plays
        strength: Priority weight
        ripening_conditions: Conditions needed for ripening
        has_ripened: Whether already delivered
        ripened_at: When it ripened (if has_ripened=True)
        vipaka_type: Type of result delivered
    """
    kamma_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique ID")
    
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="When this kamma was created"
    )
    
    # Source citta moment (optional - for analysis)
    source_citta_id: Optional[str] = Field(
        None,
        description="ID of citta that created this kamma"
    )
    
    source_citta_name: str = Field(
        ...,
        description="Name of citta (e.g., KUSALA01, LOBHA03)"
    )
    
    # Kamma properties
    kamma_type: KammaType = Field(..., description="kusala or akusala")
    
    potency: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Strength of this kamma (from citta moment)"
    )
    
    timing: KammaTiming = Field(
        ...,
        description="When this kamma will ripen"
    )
    
    function: KammaFunction = Field(
        default=KammaFunction.JANAKA,
        description="Function of this kamma"
    )
    
    strength: KammaStrength = Field(
        default=KammaStrength.KATATTA,
        description="Weight/priority of this kamma"
    )
    
    # Ripening details
    ripening_conditions: Dict[str, Any] = Field(
        default_factory=dict,
        description="Conditions required for ripening"
    )
    
    has_ripened: bool = Field(
        default=False,
        description="Whether this kamma has already ripened"
    )
    
    ripened_at: Optional[datetime] = Field(
        None,
        description="When this kamma ripened"
    )
    
    vipaka_type: Optional[VipakaType] = Field(
        None,
        description="Type of result delivered when ripened"
    )
    
    # Metadata
    notes: Optional[str] = Field(
        None,
        description="Additional notes (e.g., 'Created during generous donation')"
    )
    
    @validator("timing", always=True)
    def determine_timing(cls, v, values):
        """Auto-determine timing if not set, based on strength and potency"""
        if v is not None:
            return v
        
        strength = values.get("strength", KammaStrength.KATATTA)
        potency = values.get("potency", 0.5)
        
        # Garuka kamma usually ripens next life (causes rebirth)
        if strength == KammaStrength.GARUKA:
            return KammaTiming.UPAPAJJA_VEDANIYA
        
        # Very strong kamma may ripen this life
        if potency > 0.8:
            return KammaTiming.DITTHADHAMMA_VEDANIYA
        
        # Habitual kamma ripens in future lives
        if strength == KammaStrength.ACINNA:
            return KammaTiming.APARA_PARIYA_VEDANIYA
        
        # Default: ripens in future lives
        return KammaTiming.APARA_PARIYA_VEDANIYA
    
    @property
    def is_ripe_for_delivery(self) -> bool:
        """Check if this kamma is ready to ripen"""
        if self.has_ripened:
            return False
        
        # Check timing conditions
        # (In full implementation, check actual game time/rebirth count)
        return True
    
    @property
    def priority_score(self) -> float:
        """Calculate priority for ripening (higher = ripens first)"""
        base_score = self.potency
        
        # Strength multipliers
        if self.strength == KammaStrength.GARUKA:
            base_score *= 10.0
        elif self.strength == KammaStrength.ASANNA:
            base_score *= 5.0
        elif self.strength == KammaStrength.ACINNA:
            base_score *= 2.0
        
        return base_score
    
    def mark_ripened(self, vipaka_type: VipakaType):
        """Mark this kamma as ripened"""
        self.has_ripened = True
        self.ripened_at = datetime.now()
        self.vipaka_type = vipaka_type


# ============================================================================
# KAMMA STORAGE
# ============================================================================

class KammaStorage(BaseModel):
    """
    Stores all kamma records for a character.
    
    Organized by:
    - Type (kusala/akusala)
    - Timing (this life / next life / future lives)
    - Ripening status (active / ripened / ineffective)
    
    This is analogous to the "kamma ledger" in SpiritualAssets,
    but with full Buddhist mechanics.
    """
    character_id: str = Field(..., description="Character ID")
    
    # Active kamma (not yet ripened)
    active_kusala: List[KammaRecord] = Field(
        default_factory=list,
        description="Wholesome kamma waiting to ripen"
    )
    
    active_akusala: List[KammaRecord] = Field(
        default_factory=list,
        description="Unwholesome kamma waiting to ripen"
    )
    
    # Ripened kamma (historical)
    ripened_kusala: List[KammaRecord] = Field(
        default_factory=list,
        description="Wholesome kamma that has ripened"
    )
    
    ripened_akusala: List[KammaRecord] = Field(
        default_factory=list,
        description="Unwholesome kamma that has ripened"
    )
    
    # Ineffective kamma (ahosi - never ripens)
    ineffective: List[KammaRecord] = Field(
        default_factory=list,
        description="Kamma that became ineffective"
    )
    
    # Statistics
    total_kusala_created: int = Field(default=0)
    total_akusala_created: int = Field(default=0)
    total_kusala_ripened: int = Field(default=0)
    total_akusala_ripened: int = Field(default=0)
    
    def add_kamma(self, kamma: KammaRecord):
        """Add new kamma to storage"""
        if kamma.timing == KammaTiming.AHOSI:
            self.ineffective.append(kamma)
        elif kamma.kamma_type == KammaType.KUSALA:
            self.active_kusala.append(kamma)
            self.total_kusala_created += 1
        else:
            self.active_akusala.append(kamma)
            self.total_akusala_created += 1
    
    def get_ready_to_ripen(self, limit: int = 10) -> List[KammaRecord]:
        """
        Get kamma records ready to ripen, sorted by priority.
        
        Args:
            limit: Maximum number to return
            
        Returns:
            List of kamma records, highest priority first
        """
        # Combine active kusala and akusala
        candidates = self.active_kusala + self.active_akusala
        
        # Filter ready
        ready = [k for k in candidates if k.is_ripe_for_delivery]
        
        # Sort by priority (highest first)
        ready.sort(key=lambda k: k.priority_score, reverse=True)
        
        return ready[:limit]
    
    def mark_ripened(self, kamma: KammaRecord, vipaka_type: VipakaType):
        """Move kamma from active to ripened"""
        kamma.mark_ripened(vipaka_type)
        
        # Move to ripened list
        if kamma.kamma_type == KammaType.KUSALA:
            if kamma in self.active_kusala:
                self.active_kusala.remove(kamma)
            self.ripened_kusala.append(kamma)
            self.total_kusala_ripened += 1
        else:
            if kamma in self.active_akusala:
                self.active_akusala.remove(kamma)
            self.ripened_akusala.append(kamma)
            self.total_akusala_ripened += 1
    
    def make_ineffective(self, kamma: KammaRecord, reason: str):
        """Move kamma to ineffective (ahosi)"""
        kamma.timing = KammaTiming.AHOSI
        kamma.notes = f"Made ineffective: {reason}"
        
        if kamma in self.active_kusala:
            self.active_kusala.remove(kamma)
        elif kamma in self.active_akusala:
            self.active_akusala.remove(kamma)
        
        self.ineffective.append(kamma)
    
    @property
    def kusala_akusala_ratio(self) -> float:
        """Ratio of wholesome to unwholesome kamma"""
        total_akusala = self.total_akusala_created
        if total_akusala == 0:
            return float('inf') if self.total_kusala_created > 0 else 1.0
        return self.total_kusala_created / total_akusala
    
    @property
    def active_kamma_count(self) -> int:
        """Total active kamma waiting to ripen"""
        return len(self.active_kusala) + len(self.active_akusala)


# ============================================================================
# RIPENING CALCULATOR
# ============================================================================

class RipeningCalculator:
    """
    Determines when and how kamma ripens.
    
    Considers:
    - Timing: This life / next life / future lives
    - Strength: Garuka > Āsanna > Āciṇṇa > Kaṭattā
    - Supporting/Obstructing kamma
    - Character's current state (path stage, mental state)
    - External conditions (rebirth, near-death, meditation)
    """
    
    @staticmethod
    def calculate_ripening_probability(
        kamma: KammaRecord,
        current_conditions: Dict[str, Any]
    ) -> float:
        """
        Calculate probability that kamma will ripen in current conditions.
        
        Args:
            kamma: The kamma record
            current_conditions: Dict with:
                - life_stage: "in_life" | "near_death" | "rebirth_linking"
                - mental_state: "normal" | "jhana" | "path_moment"
                - supporting_factors: List of supporting conditions
                - obstructing_factors: List of obstructing conditions
                
        Returns:
            Probability 0.0-1.0
        """
        base_prob = kamma.potency
        
        # 1. Strength modifiers
        if kamma.strength == KammaStrength.GARUKA:
            base_prob *= 2.0  # Weighty kamma very likely to ripen
        elif kamma.strength == KammaStrength.ASANNA:
            # Death-proximate kamma only ripens near death
            if current_conditions.get("life_stage") == "near_death":
                base_prob *= 5.0
            else:
                base_prob *= 0.1
        elif kamma.strength == KammaStrength.ACINNA:
            base_prob *= 1.5  # Habitual kamma ripens steadily
        
        # 2. Timing constraints
        life_stage = current_conditions.get("life_stage", "in_life")
        
        if kamma.timing == KammaTiming.DITTHADHAMMA_VEDANIYA:
            # Must ripen in this life
            if life_stage == "in_life":
                base_prob *= 2.0
            else:
                return 0.0  # Cannot ripen after death
        
        elif kamma.timing == KammaTiming.UPAPAJJA_VEDANIYA:
            # Must ripen in next life only
            if life_stage == "rebirth_linking":
                base_prob *= 3.0
            else:
                return 0.0  # Cannot ripen in current life or later
        
        # 3. Supporting/Obstructing factors
        supporting = len(current_conditions.get("supporting_factors", []))
        obstructing = len(current_conditions.get("obstructing_factors", []))
        
        base_prob *= (1.0 + supporting * 0.1)
        base_prob /= (1.0 + obstructing * 0.2)
        
        # 4. Special conditions
        mental_state = current_conditions.get("mental_state", "normal")
        
        if mental_state == "jhana" and kamma.kamma_type == KammaType.KUSALA:
            # Wholesome kamma more likely to ripen in jhāna
            base_prob *= 1.3
        
        if mental_state == "path_moment":
            # Some kamma becomes ineffective at path attainment
            # (e.g., kamma for lower realms destroyed by Stream-entry)
            if kamma.kamma_type == KammaType.AKUSALA:
                # Strong akusala kamma may be destroyed
                if kamma.strength == KammaStrength.GARUKA:
                    return 0.0  # Destroyed by path
        
        return min(base_prob, 1.0)
    
    @staticmethod
    def can_obstruct(obstructor: KammaRecord, target: KammaRecord) -> bool:
        """
        Check if obstructor kamma can block target kamma from ripening.
        
        Rules:
        - Upapīḷaka function can obstruct
        - Must be stronger or equal strength
        - Opposite type (kusala vs akusala)
        """
        if obstructor.function != KammaFunction.UPAPILAKA:
            return False
        
        # Check strength hierarchy
        strength_order = {
            KammaStrength.GARUKA: 4,
            KammaStrength.ASANNA: 3,
            KammaStrength.ACINNA: 2,
            KammaStrength.KATATTA: 1
        }
        
        obstructor_level = strength_order[obstructor.strength]
        target_level = strength_order[target.strength]
        
        if obstructor_level < target_level:
            return False  # Cannot obstruct stronger kamma
        
        # Typically opposite types obstruct each other
        if obstructor.kamma_type != target.kamma_type:
            return True
        
        return False
    
    @staticmethod
    def can_destroy(destroyer: KammaRecord, target: KammaRecord) -> bool:
        """
        Check if destroyer kamma can permanently destroy target kamma.
        
        Rules:
        - Upaghātaka function can destroy
        - Must be much stronger (2+ levels)
        - Opposite type
        """
        if destroyer.function != KammaFunction.UPAGHĀTAKA:
            return False
        
        strength_order = {
            KammaStrength.GARUKA: 4,
            KammaStrength.ASANNA: 3,
            KammaStrength.ACINNA: 2,
            KammaStrength.KATATTA: 1
        }
        
        destroyer_level = strength_order[destroyer.strength]
        target_level = strength_order[target.strength]
        
        if destroyer_level - target_level < 2:
            return False  # Need 2+ level difference
        
        if destroyer.kamma_type == target.kamma_type:
            return False  # Same type doesn't destroy
        
        return True


# ============================================================================
# VIPAKA DELIVERER
# ============================================================================

class VipakaDeliverer:
    """
    Delivers karmic results (vipāka) when kamma ripens.
    
    Creates appropriate vipāka cittas based on:
    - Kamma type (kusala → pleasant vipāka, akusala → unpleasant vipāka)
    - Vipāka type (sense/mental/rebirth/life conditions)
    - Character's current state
    """
    
    @staticmethod
    def create_vipaka_citta(
        kamma: KammaRecord,
        vipaka_type: VipakaType
    ) -> Citta:
        """
        Create a vipāka citta based on ripening kamma.
        
        Args:
            kamma: The kamma record that's ripening
            vipaka_type: Type of result to deliver
            
        Returns:
            A Vipāka citta (consciousness)
        """
        # Determine pleasant vs unpleasant
        if kamma.kamma_type == KammaType.KUSALA:
            # Wholesome kamma → pleasant result
            if vipaka_type == VipakaType.SENSE_RESULT:
                # Pleasant sense experience
                # Map to appropriate sense vipāka citta
                # e.g., AHETU08-15 (kusala vipāka ahetuka)
                citta_id = "AHETU08"  # Eye-consciousness (pleasant)
                vedana = Vedana.SUKHA
            
            elif vipaka_type == VipakaType.MENTAL_RESULT:
                # Pleasant mental feeling
                # Map to mahā-vipāka with somanassa
                citta_id = "VIPAKA01"  # Mahā-vipāka with joy
                vedana = Vedana.SOMANASSA
            
            elif vipaka_type == VipakaType.REBIRTH_LINKING:
                # Good rebirth
                citta_id = "VIPAKA01"  # Mahā-vipāka (human/deva)
                vedana = Vedana.SOMANASSA
            
            else:
                # Default pleasant vipāka
                citta_id = "VIPAKA01"
                vedana = Vedana.SOMANASSA
        
        else:
            # Unwholesome kamma → unpleasant result
            if vipaka_type == VipakaType.SENSE_RESULT:
                # Unpleasant sense experience
                citta_id = "AHETU01"  # Eye-consciousness (unpleasant)
                vedana = Vedana.DUKKHA
            
            elif vipaka_type == VipakaType.MENTAL_RESULT:
                # Unpleasant mental feeling
                citta_id = "AHETU07"  # Investigating (unpleasant)
                vedana = Vedana.DOMANASSA
            
            elif vipaka_type == VipakaType.REBIRTH_LINKING:
                # Bad rebirth
                citta_id = "AHETU07"  # Akusala vipāka (animal/peta/hell)
                vedana = Vedana.DOMANASSA
            
            else:
                # Default unpleasant vipāka
                citta_id = "AHETU07"
                vedana = Vedana.DOMANASSA
        
        # Create vipāka citta
        # (In full implementation, load from cittas.json)
        vipaka_citta = Citta(
            id=citta_id,
            name_pali=f"Vipāka of {kamma.source_citta_name}",
            name_thai=f"วิบากจิตของ {kamma.source_citta_name}",
            category=CittaCategory.AHETUKA,  # Or KAMA_SOBHANA for mahā-vipāka
            citta_type=CittaType.VIPAKA,
            hetus=[],  # Vipāka cittas are rootless (or have wholesome roots if mahā-vipāka)
            vedana=vedana,
            cetasika_ids=[],  # To be filled
            sanna_module=f"ผลของกรรม {kamma.kamma_type.value}"
        )
        
        return vipaka_citta
    
    @staticmethod
    def apply_vipaka_effects(
        vipaka_citta: Citta,
        character_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply vipāka effects to character state.
        
        Args:
            vipaka_citta: The vipāka citta being delivered
            character_state: Current character state to modify
            
        Returns:
            Updated character state
        """
        # Modify character based on vipāka
        if vipaka_citta.vedana in [Vedana.SUKHA, Vedana.SOMANASSA]:
            # Pleasant result
            character_state["happiness"] = character_state.get("happiness", 50) + 10
            character_state["mental_state"] = "pleasant"
        
        else:
            # Unpleasant result
            character_state["happiness"] = character_state.get("happiness", 50) - 10
            character_state["mental_state"] = "unpleasant"
        
        return character_state


# ============================================================================
# MAIN KAMMA ENGINE
# ============================================================================

class KammaEngine:
    """
    Main engine for kamma mechanics.
    
    Coordinates:
    - KammaStorage: Stores kamma records
    - RipeningCalculator: Determines when kamma ripens
    - VipakaDeliverer: Delivers karmic results
    
    Usage:
        engine = KammaEngine(character_id="CHAR001")
        
        # Create kamma from citta moment
        engine.record_kamma_from_citta_moment(citta_moment)
        
        # Check for ripening
        engine.process_ripening(current_conditions)
        
        # Get statistics
        stats = engine.get_statistics()
    """
    
    def __init__(self, character_id: str):
        self.character_id = character_id
        self.storage = KammaStorage(character_id=character_id)
    
    def record_kamma_from_citta_moment(
        self,
        citta_moment: CittaMoment,
        strength: KammaStrength = KammaStrength.KATATTA,
        function: KammaFunction = KammaFunction.JANAKA,
        notes: Optional[str] = None
    ) -> Optional[KammaRecord]:
        """
        Record kamma created by a citta moment.
        
        Args:
            citta_moment: The citta moment (from Javana stage)
            strength: Weight of this kamma
            function: Function of this kamma
            notes: Optional notes
            
        Returns:
            KammaRecord if kamma was created, None otherwise
        """
        # Only kusala and akusala cittas create kamma
        if not citta_moment.creates_kamma:
            return None
        
        # Determine kamma type
        if citta_moment.is_kusala_moment:
            kamma_type = KammaType.KUSALA
        else:
            kamma_type = KammaType.AKUSALA
        
        # Create kamma record
        kamma = KammaRecord(
            source_citta_id=citta_moment.citta.id,
            source_citta_name=citta_moment.citta.name_thai,
            kamma_type=kamma_type,
            potency=citta_moment.kamma_potency,
            strength=strength,
            function=function,
            notes=notes
            # timing will be auto-determined by validator
        )
        
        # Store
        self.storage.add_kamma(kamma)
        
        return kamma
    
    def process_ripening(
        self,
        current_conditions: Dict[str, Any],
        max_ripen: int = 5
    ) -> List[Tuple[KammaRecord, Citta]]:
        """
        Process kamma ripening and deliver vipāka.
        
        Args:
            current_conditions: Current conditions (life stage, mental state, etc.)
            max_ripen: Maximum number of kamma to ripen in this cycle
            
        Returns:
            List of (KammaRecord, Vipāka Citta) tuples
        """
        results = []
        
        # Get ready kamma
        ready_kamma = self.storage.get_ready_to_ripen(limit=max_ripen * 2)
        
        # Calculate ripening probabilities
        candidates = []
        for kamma in ready_kamma:
            prob = RipeningCalculator.calculate_ripening_probability(
                kamma, current_conditions
            )
            if prob > 0:
                candidates.append((kamma, prob))
        
        # Sort by probability
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Ripen top candidates
        import random
        for kamma, prob in candidates[:max_ripen]:
            # Roll for ripening
            if random.random() < prob:
                # Determine vipāka type
                vipaka_type = self._determine_vipaka_type(kamma, current_conditions)
                
                # Create vipāka citta
                vipaka_citta = VipakaDeliverer.create_vipaka_citta(kamma, vipaka_type)
                
                # Mark as ripened
                self.storage.mark_ripened(kamma, vipaka_type)
                
                results.append((kamma, vipaka_citta))
        
        return results
    
    def _determine_vipaka_type(
        self,
        kamma: KammaRecord,
        current_conditions: Dict[str, Any]
    ) -> VipakaType:
        """Determine what type of vipāka to deliver"""
        life_stage = current_conditions.get("life_stage", "in_life")
        
        if life_stage == "rebirth_linking":
            return VipakaType.REBIRTH_LINKING
        
        # Based on kamma strength
        if kamma.strength == KammaStrength.GARUKA:
            return VipakaType.REBIRTH_LINKING
        
        # Default to sense/mental results
        import random
        return random.choice([
            VipakaType.SENSE_RESULT,
            VipakaType.MENTAL_RESULT
        ])
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get kamma statistics for character"""
        return {
            "character_id": self.character_id,
            "total_kusala_created": self.storage.total_kusala_created,
            "total_akusala_created": self.storage.total_akusala_created,
            "total_kusala_ripened": self.storage.total_kusala_ripened,
            "total_akusala_ripened": self.storage.total_akusala_ripened,
            "active_kamma_count": self.storage.active_kamma_count,
            "kusala_akusala_ratio": self.storage.kusala_akusala_ratio,
            "active_kusala": len(self.storage.active_kusala),
            "active_akusala": len(self.storage.active_akusala)
        }


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Enums
    "KammaType",
    "KammaTiming",
    "KammaFunction",
    "KammaStrength",
    "RipeningCondition",
    "VipakaType",
    
    # Models
    "KammaRecord",
    "KammaStorage",
    
    # Components
    "RipeningCalculator",
    "VipakaDeliverer",
    
    # Main engine
    "KammaEngine",
]
