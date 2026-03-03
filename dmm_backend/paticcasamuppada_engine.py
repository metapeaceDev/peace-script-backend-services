"""
Paticcasamuppāda Engine
========================
Simulates the Buddhist principle of Dependent Origination (ปฏิจจสมุปบาท) - 
the cycle of cause and effect that perpetuates suffering and rebirth.

The 12 Links (Nidānas):
1. Avijjā (อวิชชา) - Ignorance
2. Saṅkhāra (สังขาร) - Formations/Volitional activities
3. Viññāṇa (วิญญาณ) - Consciousness
4. Nāma-rūpa (นามรูป) - Mind-body
5. Saḷāyatana (สฬายตนะ) - Six sense bases
6. Phassa (ผัสสะ) - Contact
7. Vedanā (เวทนา) - Feeling
8. Taṇhā (ตัณหา) - Craving
9. Upādāna (อุปาทาน) - Clinging
10. Bhava (ภพ) - Becoming
11. Jāti (ชาติ) - Birth
12. Jarā-maraṇa (ชรามรณะ) - Aging-death

Critical Cycle: Vedanā → Taṇhā → Upādāna → Bhava
This is where the wheel turns - feelings lead to craving, craving to clinging,
clinging to kamma that creates future becoming.

Breaking Points by Path Stage:
- Sotāpanna: Weakens sakkāya-diṭṭhi (self-view) - reduces clinging to "I"
- Sakadāgāmī: Weakens kāma-rāga (sensual desire) - reduces sensual craving
- Anāgāmī: Eliminates kāma-rāga completely - no more sensual becoming
- Arahant: Eliminates all ignorance - breaks the cycle entirely

References:
- Visuddhimagga Chapter XVII: Paṭiccasamuppāda
- Saṃyutta Nikāya 12: Nidāna Saṃyutta
- docs/PATICCASAMUPPADA_ANALYSIS.md
"""

from enum import Enum
from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field, validator
from datetime import datetime

from citta_cetasika_models import (
    CittaMoment, Cetasika, Vedana, 
    CetasikaCategory, CittaType
)
from kamma_engine import KammaEngine, KammaRecord, KammaType, KammaStrength


# ============================================================================
# ENUMS: 12 Links and States
# ============================================================================

class NidanaLink(str, Enum):
    """12 Links of Dependent Origination"""
    AVIJJA = "avijjā"  # 1. Ignorance
    SANKHARA = "saṅkhāra"  # 2. Formations
    VINNANA = "viññāṇa"  # 3. Consciousness
    NAMA_RUPA = "nāma-rūpa"  # 4. Mind-body
    SALAYATANA = "saḷāyatana"  # 5. Six sense bases
    PHASSA = "phassa"  # 6. Contact
    VEDANA = "vedanā"  # 7. Feeling
    TANHA = "taṇhā"  # 8. Craving
    UPADANA = "upādāna"  # 9. Clinging
    BHAVA = "bhava"  # 10. Becoming
    JATI = "jāti"  # 11. Birth
    JARA_MARANA = "jarā-maraṇa"  # 12. Aging-death


class TanhaType(str, Enum):
    """3 types of craving"""
    KAMA_TANHA = "kāma-taṇhā"  # Craving for sensual pleasures
    BHAVA_TANHA = "bhava-taṇhā"  # Craving for existence/becoming
    VIBHAVA_TANHA = "vibhava-taṇhā"  # Craving for non-existence/annihilation


class UpādānaType(str, Enum):
    """4 types of clinging"""
    KAMUPADANA = "kāmūpādāna"  # Clinging to sensual pleasures
    DITTHUPADANA = "diṭṭhūpādāna"  # Clinging to views
    SILABBATUPADANA = "sīlabbatūpādāna"  # Clinging to rites and rituals
    ATTAVADUPADANA = "attavādūpādāna"  # Clinging to self-doctrine


class BhavaType(str, Enum):
    """3 realms of existence"""
    KAMA_BHAVA = "kāma-bhava"  # Sensual realm
    RUPA_BHAVA = "rūpa-bhava"  # Form realm (jhāna)
    ARUPA_BHAVA = "arūpa-bhava"  # Formless realm (arūpa jhāna)


class CycleState(str, Enum):
    """State of the cycle"""
    ACTIVE = "active"  # Cycle is running
    INTERRUPTED = "interrupted"  # Temporarily stopped (e.g., mindfulness)
    BROKEN = "broken"  # Permanently broken (e.g., path attainment)


# ============================================================================
# LINK STATE MODELS
# ============================================================================

class LinkState(BaseModel):
    """
    State of one link in the 12-link chain.
    
    Each link has:
    - Intensity: How strong this link is (0.0 = absent, 1.0 = maximum)
    - Active: Whether this link is currently active
    - Conditions: Supporting conditions that strengthen/weaken the link
    """
    link: NidanaLink = Field(..., description="Which link this is")
    intensity: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Strength of this link"
    )
    active: bool = Field(default=True, description="Whether link is active")
    conditions: Dict[str, Any] = Field(
        default_factory=dict,
        description="Supporting/obstructing conditions"
    )
    last_updated: datetime = Field(
        default_factory=datetime.now,
        description="When this link was last modified"
    )
    
    def strengthen(self, amount: float = 0.1):
        """Increase link intensity"""
        self.intensity = min(1.0, self.intensity + amount)
        self.last_updated = datetime.now()
    
    def weaken(self, amount: float = 0.1):
        """Decrease link intensity"""
        self.intensity = max(0.0, self.intensity - amount)
        self.last_updated = datetime.now()
        if self.intensity == 0.0:
            self.active = False
    
    def deactivate(self):
        """Deactivate this link"""
        self.active = False
        self.intensity = 0.0
        self.last_updated = datetime.now()


# ============================================================================
# VEDANĀ → TAṆHĀ → UPĀDĀNA → BHAVA CYCLE
# ============================================================================

class VedanaTanhaCycle(BaseModel):
    """
    The critical cycle: Feeling → Craving → Clinging → Becoming.
    
    This is where suffering perpetuates:
    1. Pleasant feeling → craving for more → clinging to pleasure → kamma for sensual rebirth
    2. Unpleasant feeling → craving to escape → clinging to existence → kamma for future becoming
    3. Neutral feeling → ignorance → habitual craving → subtle clinging → continued existence
    
    Breaking this cycle is the key to liberation.
    """
    vedana_type: Vedana = Field(..., description="Type of feeling")
    vedana_intensity: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Strength of feeling"
    )
    
    # Taṇhā arises from Vedanā
    tanha_type: Optional[TanhaType] = Field(
        None,
        description="Type of craving that arises"
    )
    tanha_intensity: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Strength of craving"
    )
    
    # Upādāna arises from Taṇhā
    upadana_type: Optional[UpādānaType] = Field(
        None,
        description="Type of clinging that arises"
    )
    upadana_intensity: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Strength of clinging"
    )
    
    # Bhava arises from Upādāna
    bhava_type: Optional[BhavaType] = Field(
        None,
        description="Type of becoming that arises"
    )
    bhava_intensity: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Strength of becoming (kamma potency)"
    )
    
    # Mindfulness can interrupt
    mindfulness_present: bool = Field(
        default=False,
        description="Is mindfulness (sati) present?"
    )
    
    wisdom_present: bool = Field(
        default=False,
        description="Is wisdom (paññā) present?"
    )
    
    @validator("tanha_intensity", always=True)
    def calculate_tanha(cls, v, values):
        """Auto-calculate craving intensity from feeling"""
        if v > 0:
            return v
        
        vedana_intensity = values.get("vedana_intensity", 0.5)
        mindfulness = values.get("mindfulness_present", False)
        wisdom = values.get("wisdom_present", False)
        
        # Base: craving arises proportional to feeling intensity
        base_tanha = vedana_intensity * 0.8
        
        # Mindfulness reduces craving
        if mindfulness:
            base_tanha *= 0.5
        
        # Wisdom further reduces
        if wisdom:
            base_tanha *= 0.3
        
        return base_tanha
    
    @validator("upadana_intensity", always=True)
    def calculate_upadana(cls, v, values):
        """Auto-calculate clinging from craving"""
        if v > 0:
            return v
        
        tanha_intensity = values.get("tanha_intensity", 0.0)
        mindfulness = values.get("mindfulness_present", False)
        
        # Clinging arises if craving is strong
        if tanha_intensity < 0.3:
            return 0.0
        
        base_upadana = tanha_intensity * 0.9
        
        if mindfulness:
            base_upadana *= 0.6
        
        return base_upadana
    
    @validator("bhava_intensity", always=True)
    def calculate_bhava(cls, v, values):
        """Auto-calculate becoming (kamma potency) from clinging"""
        if v > 0:
            return v
        
        upadana_intensity = values.get("upadana_intensity", 0.0)
        wisdom = values.get("wisdom_present", False)
        
        # Becoming (kamma creation) arises from clinging
        if upadana_intensity < 0.3:
            return 0.0
        
        base_bhava = upadana_intensity * 0.85
        
        # Wisdom prevents kamma creation
        if wisdom:
            base_bhava *= 0.4
        
        return base_bhava
    
    @property
    def is_cycle_active(self) -> bool:
        """Check if the full cycle is running"""
        return (
            self.tanha_intensity > 0.2 and
            self.upadana_intensity > 0.2 and
            self.bhava_intensity > 0.2
        )
    
    @property
    def is_cycle_broken(self) -> bool:
        """Check if cycle is broken by mindfulness/wisdom"""
        return self.mindfulness_present or self.wisdom_present


# ============================================================================
# FULL 12-LINK CHAIN STATE
# ============================================================================

class PaticcasamuppadaState(BaseModel):
    """
    Complete state of all 12 links.
    
    Represents the current state of the dependent origination cycle
    for a character at a given moment.
    """
    character_id: str = Field(..., description="Character ID")
    
    # All 12 links
    links: Dict[NidanaLink, LinkState] = Field(
        default_factory=dict,
        description="State of each link"
    )
    
    # Current cycle
    current_cycle: Optional[VedanaTanhaCycle] = Field(
        None,
        description="Active Vedanā→Taṇhā→Upādāna→Bhava cycle"
    )
    
    # Overall state
    cycle_state: CycleState = Field(
        default=CycleState.ACTIVE,
        description="Overall cycle state"
    )
    
    # Path stage (affects breaking points)
    path_stage: Optional[str] = Field(
        None,
        description="Sotāpanna/Sakadāgāmī/Anāgāmī/Arahant"
    )
    
    # History
    cycles_completed: int = Field(
        default=0,
        description="Number of full cycles completed"
    )
    
    cycles_broken: int = Field(
        default=0,
        description="Number of cycles broken by mindfulness/wisdom"
    )
    
    def initialize_links(self):
        """Initialize all 12 links with default state"""
        for nidana in NidanaLink:
            if nidana not in self.links:
                self.links[nidana] = LinkState(link=nidana)
    
    def get_link(self, link: NidanaLink) -> LinkState:
        """Get state of a specific link"""
        if link not in self.links:
            self.links[link] = LinkState(link=link)
        return self.links[link]
    
    def strengthen_link(self, link: NidanaLink, amount: float = 0.1):
        """Strengthen a specific link"""
        link_state = self.get_link(link)
        link_state.strengthen(amount)
    
    def weaken_link(self, link: NidanaLink, amount: float = 0.1):
        """Weaken a specific link"""
        link_state = self.get_link(link)
        link_state.weaken(amount)
    
    def deactivate_link(self, link: NidanaLink):
        """Deactivate a specific link"""
        link_state = self.get_link(link)
        link_state.deactivate()
    
    @property
    def avijja_intensity(self) -> float:
        """Get ignorance level"""
        return self.get_link(NidanaLink.AVIJJA).intensity
    
    @property
    def tanha_intensity(self) -> float:
        """Get craving level"""
        return self.get_link(NidanaLink.TANHA).intensity


# ============================================================================
# PATICCASAMUPPĀDA ENGINE
# ============================================================================

class PaticcasamuppadaEngine:
    """
    Main engine for simulating Dependent Origination.
    
    Processes:
    1. Monitors citta moments for feelings (vedanā)
    2. Simulates arising of craving (taṇhā) from feelings
    3. Simulates arising of clinging (upādāna) from craving
    4. Simulates arising of becoming (bhava) from clinging
    5. Creates kamma records via Kamma Engine
    6. Applies breaking points based on path stage
    
    Usage:
        engine = PaticcasamuppadaEngine(character_id="CHAR001")
        
        # Process a citta moment with feeling
        engine.process_citta_moment(citta_moment)
        
        # Check cycle state
        state = engine.get_state()
        print(f"Cycle active: {state.current_cycle.is_cycle_active}")
        
        # Apply path attainment breaking points
        engine.apply_path_breaking(path_stage="sotapanna")
    """
    
    def __init__(
        self,
        character_id: str,
        kamma_engine: Optional[KammaEngine] = None
    ):
        self.character_id = character_id
        self.state = PaticcasamuppadaState(character_id=character_id)
        self.state.initialize_links()
        
        # Integrate with Kamma Engine
        self.kamma_engine = kamma_engine or KammaEngine(character_id)
    
    def process_citta_moment(
        self,
        citta_moment: CittaMoment,
        character_state: Optional[Dict[str, Any]] = None
    ) -> Optional[VedanaTanhaCycle]:
        """
        Process a citta moment through the 12 links.
        
        Args:
            citta_moment: The citta moment to process
            character_state: Current character state (path stage, mindfulness level, etc.)
            
        Returns:
            VedanaTanhaCycle if cycle was activated, None otherwise
        """
        character_state = character_state or {}
        
        # 1. Extract Vedanā (feeling) from citta moment
        vedana = citta_moment.citta.vedana
        vedana_intensity = self._calculate_vedana_intensity(citta_moment)
        
        # Update Link 7: Vedanā
        self.state.strengthen_link(NidanaLink.VEDANA, vedana_intensity * 0.1)
        
        # 2. Check for mindfulness/wisdom
        mindfulness_present = self._check_mindfulness(citta_moment, character_state)
        wisdom_present = self._check_wisdom(citta_moment, character_state)
        
        # 3. Create Vedanā→Taṇhā→Upādāna→Bhava cycle
        cycle = VedanaTanhaCycle(
            vedana_type=vedana,
            vedana_intensity=vedana_intensity,
            mindfulness_present=mindfulness_present,
            wisdom_present=wisdom_present
        )
        
        # 4. Determine Taṇhā type based on Vedanā
        cycle.tanha_type = self._determine_tanha_type(vedana, character_state)
        
        # 5. Determine Upādāna type based on Taṇhā
        if cycle.tanha_intensity > 0.3:
            cycle.upadana_type = self._determine_upadana_type(
                cycle.tanha_type,
                character_state
            )
        
        # 6. Determine Bhava type based on Upādāna
        if cycle.upadana_intensity > 0.3:
            cycle.bhava_type = self._determine_bhava_type(
                cycle.upadana_type,
                character_state
            )
        
        # 7. Update links
        if cycle.tanha_intensity > 0:
            self.state.strengthen_link(NidanaLink.TANHA, cycle.tanha_intensity * 0.1)
        
        if cycle.upadana_intensity > 0:
            self.state.strengthen_link(NidanaLink.UPADANA, cycle.upadana_intensity * 0.1)
        
        if cycle.bhava_intensity > 0:
            self.state.strengthen_link(NidanaLink.BHAVA, cycle.bhava_intensity * 0.1)
        
        # 8. Create Kamma if cycle is active
        if cycle.is_cycle_active and not cycle.is_cycle_broken:
            self._create_kamma_from_cycle(citta_moment, cycle)
            self.state.cycles_completed += 1
        elif cycle.is_cycle_broken:
            self.state.cycles_broken += 1
        
        # 9. Store current cycle
        self.state.current_cycle = cycle
        
        return cycle
    
    def _calculate_vedana_intensity(self, citta_moment: CittaMoment) -> float:
        """Calculate intensity of feeling from citta moment"""
        vedana = citta_moment.citta.vedana
        
        # Pleasant/unpleasant feelings are stronger
        if vedana in [Vedana.SUKHA, Vedana.SOMANASSA]:
            return 0.7
        elif vedana in [Vedana.DUKKHA, Vedana.DOMANASSA]:
            return 0.75  # Unpleasant slightly stronger (aversion)
        else:  # Upekkhā
            return 0.3  # Neutral feeling is weaker
    
    def _check_mindfulness(
        self,
        citta_moment: CittaMoment,
        character_state: Dict[str, Any]
    ) -> bool:
        """Check if mindfulness (sati) is present"""
        # Check for Sati cetasika
        sati_present = citta_moment.cetasikas.has_cetasika("SATI01")
        
        # Check character's mindfulness level
        mindfulness_level = character_state.get("mindfulness_level", 0.0)
        
        return sati_present or mindfulness_level > 0.6
    
    def _check_wisdom(
        self,
        citta_moment: CittaMoment,
        character_state: Dict[str, Any]
    ) -> bool:
        """Check if wisdom (paññā) is present"""
        # Check for Paññā cetasika
        panna_present = citta_moment.cetasikas.has_cetasika("PANNA01")
        
        # Check if citta has wisdom
        wisdom_present = citta_moment.citta.has_panna
        
        return panna_present or wisdom_present
    
    def _determine_tanha_type(
        self,
        vedana: Vedana,
        character_state: Dict[str, Any]
    ) -> TanhaType:
        """Determine type of craving based on feeling"""
        # Pleasant feeling → craving for sensual pleasure
        if vedana in [Vedana.SUKHA, Vedana.SOMANASSA]:
            return TanhaType.KAMA_TANHA
        
        # Unpleasant feeling → craving for existence/escape
        elif vedana in [Vedana.DUKKHA, Vedana.DOMANASSA]:
            # Check if character has strong self-view
            self_view = character_state.get("self_view_intensity", 0.5)
            if self_view > 0.7:
                return TanhaType.BHAVA_TANHA  # Craving for becoming
            else:
                return TanhaType.VIBHAVA_TANHA  # Craving for non-existence
        
        # Neutral feeling → habitual craving
        else:
            return TanhaType.BHAVA_TANHA
    
    def _determine_upadana_type(
        self,
        tanha_type: TanhaType,
        character_state: Dict[str, Any]
    ) -> UpādānaType:
        """Determine type of clinging based on craving"""
        if tanha_type == TanhaType.KAMA_TANHA:
            return UpādānaType.KAMUPADANA  # Clinging to sensual pleasures
        
        elif tanha_type == TanhaType.BHAVA_TANHA:
            # Check for wrong views
            has_wrong_view = character_state.get("has_wrong_view", False)
            if has_wrong_view:
                return UpādānaType.DITTHUPADANA  # Clinging to views
            else:
                return UpādānaType.ATTAVADUPADANA  # Clinging to self
        
        else:  # VIBHAVA_TANHA
            return UpādānaType.DITTHUPADANA  # Clinging to annihilation view
    
    def _determine_bhava_type(
        self,
        upadana_type: UpādānaType,
        character_state: Dict[str, Any]
    ) -> BhavaType:
        """Determine type of becoming based on clinging"""
        if upadana_type == UpādānaType.KAMUPADANA:
            return BhavaType.KAMA_BHAVA  # Sensual realm rebirth
        
        # Check jhāna attainment
        jhana_level = character_state.get("jhana_level", 0)
        
        if jhana_level >= 1 and jhana_level <= 4:
            return BhavaType.RUPA_BHAVA  # Form realm rebirth
        elif jhana_level >= 5:
            return BhavaType.ARUPA_BHAVA  # Formless realm rebirth
        
        return BhavaType.KAMA_BHAVA  # Default: sensual realm
    
    def _create_kamma_from_cycle(
        self,
        citta_moment: CittaMoment,
        cycle: VedanaTanhaCycle
    ):
        """Create kamma record from completed cycle"""
        # Only create kamma if citta creates kamma
        if not citta_moment.creates_kamma:
            return
        
        # Determine strength based on cycle intensity
        avg_intensity = (
            cycle.tanha_intensity +
            cycle.upadana_intensity +
            cycle.bhava_intensity
        ) / 3
        
        if avg_intensity > 0.8:
            strength = KammaStrength.GARUKA  # Weighty
        elif avg_intensity > 0.6:
            strength = KammaStrength.ACINNA  # Habitual
        else:
            strength = KammaStrength.KATATTA  # Reserve
        
        # Record kamma
        self.kamma_engine.record_kamma_from_citta_moment(
            citta_moment,
            strength=strength,
            notes=f"Created via Vedanā→Taṇhā→Upādāna→Bhava cycle ({cycle.vedana_type.value} feeling)"
        )
    
    def apply_path_breaking(self, path_stage: str):
        """
        Apply breaking points based on path attainment.
        
        Each path stage breaks certain links:
        - Sotāpanna: Weakens Upādāna (attavāda) significantly
        - Sakadāgāmī: Weakens Taṇhā (kāma-rāga) significantly
        - Anāgāmī: Eliminates Taṇhā (kāma-rāga) completely
        - Arahant: Eliminates Avijjā completely - breaks entire cycle
        """
        self.state.path_stage = path_stage
        
        if path_stage == "sotapanna":
            # Stream-enterer: Breaks 3 fetters
            # - Sakkāya-diṭṭhi: Reduces clinging to self
            self.state.weaken_link(NidanaLink.UPADANA, 0.4)
            
            # - Vicikicchā: No more doubt in Triple Gem
            self.state.weaken_link(NidanaLink.AVIJJA, 0.2)
            
            # - Sīlabbata-parāmāsa: No clinging to rites
            # (affects Upādāna of type Sīlabbatūpādāna)
            
            self.state.cycle_state = CycleState.INTERRUPTED
        
        elif path_stage == "sakadagami":
            # Once-returner: Weakens sensual desire and aversion
            self.state.weaken_link(NidanaLink.TANHA, 0.4)
            self.state.weaken_link(NidanaLink.UPADANA, 0.5)
            self.state.cycle_state = CycleState.INTERRUPTED
        
        elif path_stage == "anagami":
            # Non-returner: Eliminates sensual desire completely
            # No more Kāma-taṇhā
            self.state.deactivate_link(NidanaLink.TANHA)
            self.state.weaken_link(NidanaLink.UPADANA, 0.7)
            self.state.cycle_state = CycleState.INTERRUPTED
        
        elif path_stage == "arahant":
            # Arahant: Eliminates all ignorance
            self.state.deactivate_link(NidanaLink.AVIJJA)
            self.state.deactivate_link(NidanaLink.TANHA)
            self.state.deactivate_link(NidanaLink.UPADANA)
            self.state.deactivate_link(NidanaLink.BHAVA)
            
            # Cycle is permanently broken
            self.state.cycle_state = CycleState.BROKEN
    
    def simulate_rebirth(self, kamma_record: KammaRecord) -> Dict[str, Any]:
        """
        Simulate rebirth (Jāti) based on ripening kamma.
        
        Link 10 (Bhava) → Link 11 (Jāti) → Link 12 (Jarā-maraṇa)
        
        Args:
            kamma_record: The kamma that causes rebirth
            
        Returns:
            Rebirth conditions dict
        """
        # Strengthen Links 10, 11, 12
        self.state.strengthen_link(NidanaLink.BHAVA, 0.5)
        self.state.strengthen_link(NidanaLink.JATI, 1.0)
        self.state.strengthen_link(NidanaLink.JARA_MARANA, 0.8)
        
        # Determine rebirth realm based on kamma type
        rebirth_conditions = {
            "timestamp": datetime.now(),
            "kamma_source": kamma_record.source_citta_name,
            "kamma_type": kamma_record.kamma_type.value,
        }
        
        if kamma_record.kamma_type == KammaType.KUSALA:
            # Good rebirth
            if kamma_record.potency > 0.8:
                rebirth_conditions["realm"] = "deva"  # Heavenly realm
                rebirth_conditions["happiness_level"] = "very_high"
            else:
                rebirth_conditions["realm"] = "human"  # Human realm
                rebirth_conditions["happiness_level"] = "moderate"
        else:
            # Bad rebirth
            if kamma_record.potency > 0.7:
                rebirth_conditions["realm"] = "hell"  # Hell realm
                rebirth_conditions["happiness_level"] = "extreme_suffering"
            elif kamma_record.potency > 0.5:
                rebirth_conditions["realm"] = "peta"  # Hungry ghost
                rebirth_conditions["happiness_level"] = "high_suffering"
            else:
                rebirth_conditions["realm"] = "animal"  # Animal realm
                rebirth_conditions["happiness_level"] = "moderate_suffering"
        
        return rebirth_conditions
    
    def get_state(self) -> PaticcasamuppadaState:
        """Get current state of all 12 links"""
        return self.state
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the cycle"""
        return {
            "character_id": self.character_id,
            "cycle_state": self.state.cycle_state.value,
            "path_stage": self.state.path_stage,
            "cycles_completed": self.state.cycles_completed,
            "cycles_broken": self.state.cycles_broken,
            "avijja_intensity": self.state.avijja_intensity,
            "tanha_intensity": self.state.tanha_intensity,
            "current_cycle_active": (
                self.state.current_cycle.is_cycle_active
                if self.state.current_cycle else False
            ),
            "link_states": {
                link.value: {
                    "intensity": state.intensity,
                    "active": state.active
                }
                for link, state in self.state.links.items()
            }
        }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_integrated_engine(character_id: str) -> Tuple[KammaEngine, PaticcasamuppadaEngine]:
    """
    Create integrated Kamma and Paticcasamuppāda engines.
    
    Returns:
        Tuple of (KammaEngine, PaticcasamuppadaEngine)
    """
    kamma_engine = KammaEngine(character_id)
    ps_engine = PaticcasamuppadaEngine(character_id, kamma_engine)
    return kamma_engine, ps_engine


def analyze_breaking_points(path_stage: str) -> Dict[str, Any]:
    """
    Analyze which links are broken at each path stage.
    
    Returns detailed information about what each path attainment breaks.
    """
    breaking_points = {
        "puthujjana": {
            "broken_links": [],
            "weakened_links": [],
            "cycle_state": "fully_active",
            "description": "Ordinary person - all 12 links active"
        },
        "sotapanna": {
            "broken_links": [],
            "weakened_links": [
                NidanaLink.AVIJJA,
                NidanaLink.UPADANA
            ],
            "cycle_state": "interrupted",
            "description": "Stream-enterer - Sakkāya-diṭṭhi broken, clinging weakened",
            "fetters_broken": ["sakkaya_ditthi", "vicikiccha", "silabbata_paramasa"]
        },
        "sakadagami": {
            "broken_links": [],
            "weakened_links": [
                NidanaLink.AVIJJA,
                NidanaLink.TANHA,
                NidanaLink.UPADANA
            ],
            "cycle_state": "interrupted",
            "description": "Once-returner - Sensual desire/aversion weakened",
            "fetters_weakened": ["kama_raga", "patigha"]
        },
        "anagami": {
            "broken_links": [NidanaLink.TANHA],
            "weakened_links": [
                NidanaLink.AVIJJA,
                NidanaLink.UPADANA
            ],
            "cycle_state": "interrupted",
            "description": "Non-returner - Sensual craving eliminated",
            "fetters_broken": ["kama_raga", "patigha"]
        },
        "arahant": {
            "broken_links": [
                NidanaLink.AVIJJA,
                NidanaLink.TANHA,
                NidanaLink.UPADANA,
                NidanaLink.BHAVA
            ],
            "weakened_links": [],
            "cycle_state": "permanently_broken",
            "description": "Arahant - All ignorance eliminated, cycle broken",
            "fetters_broken": ["all_10_fetters"]
        }
    }
    
    return breaking_points.get(path_stage, breaking_points["puthujjana"])


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Enums
    "NidanaLink",
    "TanhaType",
    "UpādānaType",
    "BhavaType",
    "CycleState",
    
    # Models
    "LinkState",
    "VedanaTanhaCycle",
    "PaticcasamuppadaState",
    
    # Main engine
    "PaticcasamuppadaEngine",
    
    # Helpers
    "create_integrated_engine",
    "analyze_breaking_points",
]
