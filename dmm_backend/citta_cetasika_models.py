"""
Citta-Cetasika Models
=====================
Core models for 89 Cittas (consciousness types) and 52 Cetasikas (mental factors).
This module provides the foundation for Buddhist psychology simulation in character development.

Buddhist Framework:
- 89 Cittas: Types of consciousness that arise and cease moment by moment
- 52 Cetasikas: Mental factors that accompany consciousness
- Citta Moment (Cittakkhaṇa): A single moment of consciousness with its accompanying cetasikas

Key Concepts:
1. Each Citta arises with specific Cetasikas (e.g., Lobha-mūla-citta arises with Lobha cetasika)
2. Cetasikas determine the ethical quality (kusala/akusala/abyākata) of the Citta
3. Kamma is created by Kusala/Akusala cittas and their cetasikas
4. Vipāka (result) cittas deliver karmic results

References:
- definitions/cittas.json: 89 Citta definitions
- definitions/cetasikas.json: 52 Cetasika definitions
- docs/USER_GUIDE_CETASIKA.md: Detailed guide
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime


# ============================================================================
# ENUMS: Buddhist Classifications
# ============================================================================

class CittaCategory(str, Enum):
    """6 main categories of consciousness (89 Cittas)"""
    AKUSALA = "akusala"  # 12 unwholesome cittas
    AHETUKA = "ahetuka"  # 18 rootless cittas
    KAMA_SOBHANA = "kama_sobhana"  # 24 sense-sphere beautiful cittas
    RUPAVACARA = "rupavacara"  # 15 form-sphere jhāna cittas
    ARUPAVACARA = "arupavacara"  # 12 formless-sphere jhāna cittas
    LOKUTTARA = "lokuttara"  # 8 supramundane cittas (or 40 detailed)


class CittaType(str, Enum):
    """3 functional types of Citta"""
    KUSALA = "kusala"  # Wholesome (creates good kamma)
    AKUSALA = "akusala"  # Unwholesome (creates bad kamma)
    VIPAKA = "vipaka"  # Resultant (delivers kamma results)
    KIRIYA = "kiriya"  # Functional (Arahant's cittas - no kamma)
    ABYAKATA = "abyakata"  # Indeterminate (neutral)


class CetasikaCategory(str, Enum):
    """3 main categories of mental factors (52 Cetasikas)"""
    ANNASAMAN = "aññasamāna"  # 13 universal/particular (7 universal + 6 particular)
    AKUSALA = "akusala"  # 14 unwholesome
    SOBHANA = "sobhaṇa"  # 25 beautiful


class CetasikaSubCategory(str, Enum):
    """Detailed subcategories of Cetasikas"""
    # Aññasamāna (13)
    UNIVERSAL = "sabbacittasādhāraṇa"  # 7 universal (arise with ALL cittas)
    PARTICULAR = "pakiṇṇaka"  # 6 particular (arise with some cittas)
    
    # Akusala (14)
    MOHA = "moha_group"  # 4 delusion-based
    LOBHA = "lobha_group"  # 3 greed-based
    DOSA = "dosa_group"  # 4 hatred-based
    THINA_MIDDHA = "thīna_middha"  # 2 sloth-torpor
    VICIKICCHA = "vicikicchā"  # 1 doubt
    
    # Sobhaṇa (25)
    SOBHANA_UNIVERSAL = "sobhaṇa_sādhāraṇa"  # 19 universal beautiful
    VIRATI = "virati"  # 3 abstinences
    APPAMANNA = "appamaññā"  # 2 boundless states
    PANNA = "paññā"  # 1 wisdom


class Vedana(str, Enum):
    """5 types of feeling that accompany cittas"""
    SUKHA = "sukha"  # Pleasant bodily feeling
    DUKKHA = "dukkha"  # Painful bodily feeling
    SOMANASSA = "somanassa"  # Pleasant mental feeling (joy)
    DOMANASSA = "domanassa"  # Unpleasant mental feeling (grief)
    UPEKKHA = "upekkhā"  # Neutral feeling (equanimity)


class Hetu(str, Enum):
    """6 roots that can accompany cittas"""
    # Unwholesome roots
    LOBHA = "lobha"  # Greed
    DOSA = "dosa"  # Hatred
    MOHA = "moha"  # Delusion
    
    # Wholesome roots
    ALOBHA = "alobha"  # Non-greed (generosity)
    ADOSA = "adosa"  # Non-hatred (loving-kindness)
    AMOHA = "amoha"  # Non-delusion (wisdom)


class Sankhara(str, Enum):
    """Prompted vs unprompted"""
    ASANKHARIKA = "asaṅkhārika"  # Unprompted (spontaneous)
    SASANKHARIKA = "sasaṅkhārika"  # Prompted (induced)


# ============================================================================
# CETASIKA MODELS
# ============================================================================

class Cetasika(BaseModel):
    """
    Cetasika (Mental Factor)
    
    Mental factors that arise together with consciousness (citta).
    52 Cetasikas are classified into:
    - 13 Aññasamāna (7 universal + 6 particular)
    - 14 Akusala (unwholesome)
    - 25 Sobhaṇa (beautiful)
    
    Attributes:
        id: Unique identifier (e.g., "CETASIKA001")
        name_pali: Pali name (e.g., "Phassa")
        name_thai: Thai name (e.g., "ผัสสะ")
        name_english: English name (e.g., "Contact")
        category: Main category (aññasamāna/akusala/sobhaṇa)
        subcategory: Detailed subcategory
        description: What this cetasika does
        function: Technical function in mind process
        ethical_quality: kusala/akusala/abyākata (wholesome/unwholesome/neutral)
        intensity: Strength level 0.0-1.0 (for simulation)
    """
    id: str = Field(..., description="Unique ID from cetasikas.json")
    name_pali: str = Field(..., description="Pali name")
    name_thai: str = Field(..., description="Thai name")
    name_english: Optional[str] = Field(None, description="English name")
    
    category: CetasikaCategory = Field(..., description="Main category")
    subcategory: CetasikaSubCategory = Field(..., description="Subcategory")
    
    description: str = Field(..., description="What this cetasika does")
    function: str = Field(..., description="Technical function")
    
    ethical_quality: CittaType = Field(
        ..., 
        description="Ethical nature: kusala/akusala/abyākata"
    )
    
    # For simulation/gameplay
    intensity: float = Field(
        default=1.0, 
        ge=0.0, 
        le=1.0,
        description="Intensity of this cetasika in current moment"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "CETASIKA001",
                "name_pali": "Phassa",
                "name_thai": "ผัสสะ",
                "name_english": "Contact",
                "category": "aññasamāna",
                "subcategory": "sabbacittasādhāraṇa",
                "description": "Contact between sense organ, object, and consciousness",
                "function": "Touches the object",
                "ethical_quality": "abyākata",
                "intensity": 1.0
            }
        }


class CetasikaManifold(BaseModel):
    """
    Collection of Cetasikas arising together in one citta moment.
    
    Buddhist principle: Cetasikas arise in specific combinations:
    - 7 Universal Cetasikas arise with EVERY citta
    - Other cetasikas arise based on citta type
    - Akusala cetasikas cannot arise with Sobhaṇa cetasikas
    
    Examples:
    - Lobha-mūla-citta: 7 universal + Moha + Lobha + (possibly Diṭṭhi)
    - Mahā-kusala-citta: 7 universal + 19 Sobhaṇa universal + (possibly Paññā)
    """
    universal_7: List[Cetasika] = Field(
        ..., 
        min_length=7, 
        max_length=7,
        description="7 universal cetasikas (Phassa, Vedanā, Saññā, Cetanā, Ekaggatā, Jīvitindriya, Manasikāra)"
    )
    
    particular: List[Cetasika] = Field(
        default_factory=list,
        description="Additional cetasikas based on citta type"
    )
    
    @validator("universal_7")
    def validate_universal(cls, v):
        if len(v) != 7:
            raise ValueError("Must have exactly 7 universal cetasikas")
        universal_ids = {"CETASIKA001", "CETASIKA002", "CETASIKA003", 
                        "CETASIKA004", "CETASIKA005", "CETASIKA006", "CETASIKA007"}
        actual_ids = {c.id for c in v}
        if actual_ids != universal_ids:
            raise ValueError(f"Universal cetasikas must be {universal_ids}")
        return v
    
    @property
    def all_cetasikas(self) -> List[Cetasika]:
        """Get all cetasikas in this manifold"""
        return self.universal_7 + self.particular
    
    @property
    def total_count(self) -> int:
        """Total number of cetasikas"""
        return len(self.all_cetasikas)
    
    def has_cetasika(self, cetasika_id: str) -> bool:
        """Check if specific cetasika is present"""
        return any(c.id == cetasika_id for c in self.all_cetasikas)
    
    def get_cetasika_by_id(self, cetasika_id: str) -> Optional[Cetasika]:
        """Get specific cetasika by ID"""
        for c in self.all_cetasikas:
            if c.id == cetasika_id:
                return c
        return None


# ============================================================================
# CITTA MODELS
# ============================================================================

class Citta(BaseModel):
    """
    Citta (Consciousness)
    
    One of 89 types of consciousness according to Abhidhamma.
    Each citta arises with specific cetasikas and has distinct characteristics.
    
    Classification:
    - Category: 6 main groups (akusala, ahetuka, kāma-sobhana, rūpāvacara, arūpāvacara, lokuttara)
    - Type: kusala/akusala/vipāka/kiriyā
    - Roots: Number and type of hetu (0-3)
    - Feeling: sukha/dukkha/somanassa/domanassa/upekkhā
    
    Attributes:
        id: Unique identifier (e.g., "LOBHA01")
        name_pali: Full Pali name
        name_thai: Thai name
        category: Main category
        citta_type: kusala/akusala/vipāka/kiriyā
        hetus: List of roots (lobha/dosa/moha/alobha/adosa/amoha)
        vedana: Accompanying feeling
        sankhara: Prompted or unprompted
        cetasika_ids: IDs of cetasikas that arise with this citta
        sanna_module: Perceptual interpretation (from cittas.json)
    """
    id: str = Field(..., description="Unique ID from cittas.json")
    name_pali: str = Field(..., description="Full Pali name")
    name_thai: str = Field(..., description="Thai name")
    name_english: Optional[str] = Field(None, description="English name")
    
    category: CittaCategory = Field(..., description="Main category")
    citta_type: CittaType = Field(..., description="Functional type")
    
    hetus: List[Hetu] = Field(
        default_factory=list,
        description="Roots accompanying this citta (0-3)"
    )
    
    vedana: Vedana = Field(..., description="Feeling accompanying this citta")
    sankhara: Optional[Sankhara] = Field(None, description="Prompted or unprompted")
    
    # Cetasika combination
    cetasika_ids: List[str] = Field(
        ..., 
        description="IDs of cetasikas that arise with this citta"
    )
    
    # From cittas.json
    sanna_module: str = Field(
        ..., 
        description="Perceptual interpretation of objects"
    )
    
    # Additional properties
    has_panna: bool = Field(
        default=False, 
        description="Whether accompanied by wisdom (ñāṇa)"
    )
    
    has_ditthi: bool = Field(
        default=False, 
        description="Whether accompanied by wrong view"
    )
    
    @validator("hetus")
    def validate_hetus(cls, v):
        if len(v) > 3:
            raise ValueError("Citta cannot have more than 3 hetus")
        # Cannot have both wholesome and unwholesome roots
        unwholesome = {Hetu.LOBHA, Hetu.DOSA, Hetu.MOHA}
        wholesome = {Hetu.ALOBHA, Hetu.ADOSA, Hetu.AMOHA}
        has_unwholesome = any(h in unwholesome for h in v)
        has_wholesome = any(h in wholesome for h in v)
        if has_unwholesome and has_wholesome:
            raise ValueError("Cannot have both wholesome and unwholesome hetus")
        return v
    
    @property
    def is_ahetuka(self) -> bool:
        """Check if this is a rootless citta"""
        return len(self.hetus) == 0
    
    @property
    def is_dvihetuka(self) -> bool:
        """Check if this citta has 2 roots"""
        return len(self.hetus) == 2
    
    @property
    def is_tihetuka(self) -> bool:
        """Check if this citta has 3 roots"""
        return len(self.hetus) == 3
    
    @property
    def creates_kamma(self) -> bool:
        """Check if this citta creates kamma"""
        return self.citta_type in [CittaType.KUSALA, CittaType.AKUSALA]
    
    @property
    def is_kamavacara(self) -> bool:
        """Check if this is a sense-sphere citta"""
        return self.category in [
            CittaCategory.AKUSALA, 
            CittaCategory.AHETUKA, 
            CittaCategory.KAMA_SOBHANA
        ]
    
    @property
    def is_jhana(self) -> bool:
        """Check if this is a jhāna citta"""
        return self.category in [CittaCategory.RUPAVACARA, CittaCategory.ARUPAVACARA]
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "LOBHA01",
                "name_pali": "Lobha-mūla-citta somanassa-sahagataṃ diṭṭhigata-sampayuttaṃ asaṅkhārikaṃ",
                "name_thai": "โลภมูลจิต โสมนัสสสหคตัง ทิฏฐิคตสัมปยุตตัง อสังขาริกัง",
                "category": "akusala",
                "citta_type": "akusala",
                "hetus": ["lobha", "moha"],
                "vedana": "somanassa",
                "sankhara": "asaṅkhārika",
                "cetasika_ids": ["CETASIKA001-007", "MOHA01", "LOBHA01", "DITTHI01"],
                "sanna_module": "ตีความอารมณ์ที่น่าพอใจว่าเป็น 'ของเรา' ด้วยความเห็นผิด และเกิดขึ้นเอง",
                "has_panna": False,
                "has_ditthi": True
            }
        }


# ============================================================================
# CITTA MOMENT (จิตขณะ)
# ============================================================================

class CittaMoment(BaseModel):
    """
    Cittakkhaṇa (Citta Moment)
    
    A single moment of consciousness consisting of:
    - 1 Citta (consciousness type)
    - Multiple Cetasikas (mental factors) that arise together
    
    This is the fundamental unit of mental experience in Abhidhamma.
    Each citta moment arises, exists briefly, and ceases instantly.
    
    In simulation:
    - Citta moments arise in response to objects (ārammaṇa)
    - Sequence of citta moments forms a mind process (citta vīthi)
    - Kusala/Akusala citta moments create kamma
    - Vipāka citta moments deliver karmic results
    
    Attributes:
        timestamp: When this citta moment arose
        citta: The consciousness type
        cetasikas: Mental factors arising with this citta
        arammana: Object of consciousness
        door: Sense door (eye/ear/nose/tongue/body/mind)
        kamma_potency: Strength of kamma created (if kusala/akusala)
    """
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When this citta moment arose"
    )
    
    citta: Citta = Field(..., description="The consciousness type")
    
    cetasikas: CetasikaManifold = Field(
        ..., 
        description="Mental factors arising with this citta"
    )
    
    arammana: Optional[str] = Field(
        None, 
        description="Object of consciousness (rūpa, sadda, gandha, rasa, phoṭṭhabba, dhamma)"
    )
    
    door: Optional[str] = Field(
        None,
        description="Sense door: cakkhu/sota/ghāna/jivhā/kāya/mano"
    )
    
    kamma_potency: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Strength of kamma created by this moment (if kusala/akusala)"
    )
    
    @validator("kamma_potency", always=True)
    def set_kamma_potency(cls, v, values):
        """Auto-calculate kamma potency if not set"""
        if v is not None:
            return v
        
        citta = values.get("citta")
        if citta and citta.creates_kamma:
            # Base potency on roots and wisdom
            base = 0.3
            if citta.is_tihetuka:
                base = 0.7
            elif citta.is_dvihetuka:
                base = 0.5
            
            # Boost if has wisdom
            if citta.has_panna:
                base += 0.2
            
            # Reduce if prompted
            if citta.sankhara == Sankhara.SASANKHARIKA:
                base *= 0.8
            
            return min(base, 1.0)
        
        return 0.0  # No kamma for vipāka/kiriyā cittas
    
    @property
    def is_kusala_moment(self) -> bool:
        """Check if this is a wholesome moment"""
        return self.citta.citta_type == CittaType.KUSALA
    
    @property
    def is_akusala_moment(self) -> bool:
        """Check if this is an unwholesome moment"""
        return self.citta.citta_type == CittaType.AKUSALA
    
    @property
    def is_vipaka_moment(self) -> bool:
        """Check if this is a resultant moment"""
        return self.citta.citta_type == CittaType.VIPAKA
    
    @property
    def creates_kamma(self) -> bool:
        """Check if this moment creates kamma"""
        return self.citta.creates_kamma and self.kamma_potency > 0
    
    def get_akusala_cetasikas(self) -> List[Cetasika]:
        """Get all unwholesome cetasikas in this moment"""
        return [
            c for c in self.cetasikas.all_cetasikas 
            if c.category == CetasikaCategory.AKUSALA
        ]
    
    def get_sobhana_cetasikas(self) -> List[Cetasika]:
        """Get all beautiful cetasikas in this moment"""
        return [
            c for c in self.cetasikas.all_cetasikas 
            if c.category == CetasikaCategory.SOBHANA
        ]


# ============================================================================
# CITTA VITHI (Mind Process/Cognitive Series)
# ============================================================================

class CittaVithi(BaseModel):
    """
    Citta Vīthi (Mind Process / Cognitive Series)
    
    A sequence of citta moments that forms one complete cognitive process.
    
    Standard door process (for strong objects):
    1. Bhavaṅga (Life-continuum)
    2. Bhavaṅga-calana (Vibrating life-continuum)
    3. Bhavaṅga-upaccheda (Arrest life-continuum)
    4. Pañca-dvārāvajjana (Five-door adverting)
    5. Cakkhuviññāṇa etc. (Eye-consciousness etc.)
    6. Sampaṭicchana (Receiving)
    7. Santīraṇa (Investigating)
    8. Voṭṭhapana (Determining)
    9. Javana (Impulsion) x 7
    10. Tadārammaṇa (Retention) x 2
    11. Back to Bhavaṅga
    
    The Javana stage (9) is where kamma is created (if kusala/akusala).
    
    Attributes:
        vithi_id: Unique identifier
        moments: Sequence of citta moments
        door: Sense door used
        object_strength: Strength of object (determines process length)
        javana_count: Number of Javana moments (usually 7, or 5-6 for weaker objects)
    """
    vithi_id: str = Field(..., description="Unique identifier")
    
    moments: List[CittaMoment] = Field(
        default_factory=list,
        description="Sequence of citta moments in this process"
    )
    
    door: str = Field(
        ...,
        description="Sense door: pañca-dvāra or mano-dvāra"
    )
    
    object_strength: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Strength of object: weak/moderate/strong/very strong"
    )
    
    javana_count: int = Field(
        default=7,
        ge=5,
        le=7,
        description="Number of Javana moments (5-7)"
    )
    
    @property
    def total_moments(self) -> int:
        """Total number of citta moments in this process"""
        return len(self.moments)
    
    @property
    def javana_moments(self) -> List[CittaMoment]:
        """Get Javana moments (where kamma is created)"""
        # Javana moments are the ones that create kamma
        return [m for m in self.moments if m.creates_kamma]
    
    @property
    def total_kamma_created(self) -> float:
        """Total kamma potency created in this process"""
        return sum(m.kamma_potency for m in self.javana_moments if m.kamma_potency)
    
    def add_moment(self, moment: CittaMoment):
        """Add a citta moment to this process"""
        self.moments.append(moment)


# ============================================================================
# MAPPING FUNCTIONS: Anusaya ↔ Cetasika, Pāramī ↔ Cetasika
# ============================================================================

class AnusayaCetasikaMap:
    """
    Mapping between Anusaya (latent tendencies) and Akusala Cetasikas.
    
    7 Anusaya → 14 Akusala Cetasikas:
    - Kāma-rāga-anusaya → Lobha cetasikas (3)
    - Paṭigha-anusaya → Dosa cetasikas (4)
    - Diṭṭhi-anusaya → Diṭṭhi cetasika (1)
    - Māna-anusaya → Māna cetasika (1)
    - Vicikicchā-anusaya → Vicikicchā cetasika (1)
    - Bhava-rāga-anusaya → Lobha cetasikas (3)
    - Avijjā-anusaya → Moha cetasikas (4)
    """
    
    # Anusaya → Cetasika ID mappings
    MAPPINGS = {
        "kama_raga": ["LOBHA01", "LOBHA02", "LOBHA03"],  # Lobha, Abhijjhā, Rāga
        "patigha": ["DOSA01", "DOSA02", "DOSA03", "DOSA04"],  # Dosa, Paṭigha, Issā, Macchariya
        "ditthi": ["DITTHI01"],  # Diṭṭhi
        "mana": ["MANA01"],  # Māna
        "vicikiccha": ["VICIKICCHA01"],  # Vicikicchā
        "bhava_raga": ["LOBHA01", "LOBHA02", "LOBHA03"],  # Same as kāma-rāga
        "avijja": ["MOHA01", "MOHA02", "MOHA03", "MOHA04"]  # Moha, Ahirika, Anottappa, Uddhacca
    }
    
    @classmethod
    def get_cetasikas_for_anusaya(cls, anusaya_name: str) -> List[str]:
        """Get cetasika IDs for a given anusaya"""
        return cls.MAPPINGS.get(anusaya_name, [])
    
    @classmethod
    def get_anusaya_for_cetasika(cls, cetasika_id: str) -> List[str]:
        """Get anusaya names that include this cetasika"""
        return [
            anusaya for anusaya, cetasikas in cls.MAPPINGS.items()
            if cetasika_id in cetasikas
        ]


class ParamiCetasikaMap:
    """
    Mapping between Pāramī (perfections) and Sobhaṇa Cetasikas.
    
    10 Pāramī → 25 Sobhaṇa Cetasikas:
    - Dāna → Alobha (generosity)
    - Sīla → Virati cetasikas (3 abstinences)
    - Nekkhamma → Alobha (renunciation)
    - Paññā → Paññā cetasika + Amoha
    - Viriya → Viriya cetasika
    - Khanti → Adosa (patience)
    - Sacca → Sacca cetasika (truthfulness)
    - Adhiṭṭhāna → Adhimokkha (determination)
    - Mettā → Adosa + Karuṇā cetasika
    - Upekkhā → Tatramajjhattatā (equanimity)
    """
    
    # Pāramī → Cetasika ID mappings
    MAPPINGS = {
        "dana": ["ALOBHA01"],  # Generosity
        "sila": ["VIRATI01", "VIRATI02", "VIRATI03"],  # 3 Abstinences
        "nekkhamma": ["ALOBHA01"],  # Renunciation (also alobha)
        "panna": ["PANNA01", "AMOHA01"],  # Wisdom
        "viriya": ["VIRIYA01"],  # Energy
        "khanti": ["ADOSA01"],  # Patience (non-hatred)
        "sacca": ["SACCA01"],  # Truthfulness
        "adhitthana": ["ADHIMOKKHA01"],  # Determination
        "metta": ["ADOSA01", "KARUNA01"],  # Loving-kindness
        "upekkha": ["TATRAMAJJHATTATA01"]  # Equanimity
    }
    
    @classmethod
    def get_cetasikas_for_parami(cls, parami_name: str) -> List[str]:
        """Get cetasika IDs for a given pāramī"""
        return cls.MAPPINGS.get(parami_name, [])
    
    @classmethod
    def get_parami_for_cetasika(cls, cetasika_id: str) -> List[str]:
        """Get pāramī names that include this cetasika"""
        return [
            parami for parami, cetasikas in cls.MAPPINGS.items()
            if cetasika_id in cetasikas
        ]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def load_cittas_from_json() -> Dict[str, Any]:
    """Load cittas from definitions/cittas.json"""
    import json
    from pathlib import Path
    
    cittas_path = Path(__file__).parent.parent / "definitions" / "cittas.json"
    with open(cittas_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_cetasikas_from_json() -> Dict[str, Any]:
    """Load cetasikas from definitions/cetasikas.json"""
    import json
    from pathlib import Path
    
    cetasikas_path = Path(__file__).parent.parent / "definitions" / "cetasikas.json"
    with open(cetasikas_path, "r", encoding="utf-8") as f:
        return json.load(f)


def create_citta_from_json(citta_id: str, citta_data: Dict[str, Any]) -> Citta:
    """
    Create a Citta model from JSON data.
    
    Parses cittas.json format and creates fully-populated Citta object.
    
    Args:
        citta_id: Unique ID (e.g., "CITTA001")
        citta_data: Dict from cittas.json
        
    Returns:
        Citta object with all fields populated
    """
    try:
        # Extract core fields with fallbacks
        name_pali = citta_data.get("name_pali", "Unknown")
        name_thai = citta_data.get("name_thai", "ไม่ทราบ")
        name_english = citta_data.get("name_english")
        
        # Parse category (required)
        category_str = citta_data.get("category", "ahetuka").lower()
        category = CittaCategory(category_str)
        
        # Parse type (required)
        type_str = citta_data.get("type", "abyakata").lower()
        citta_type = CittaType(type_str)
        
        # Parse feeling (vedana)
        feeling_str = citta_data.get("feeling", "upekkhā").lower()
        feeling = Vedana(feeling_str)
        
        # Parse roots (hetu) - can be list or empty
        roots_data = citta_data.get("roots", [])
        roots = [Hetu(r.lower()) for r in roots_data] if roots_data else []
        
        # Parse sankhara (prompted/unprompted)
        sankhara_str = citta_data.get("sankhara")
        sankhara = Sankhara(sankhara_str.lower()) if sankhara_str else None
        
        # Parse associated cetasikas (IDs)
        cetasika_ids = citta_data.get("cetasikas", [])
        
        # Additional metadata
        description = citta_data.get("description", "")
        function = citta_data.get("function", "")
        door_types = citta_data.get("door_types", [])
        object_types = citta_data.get("object_types", [])
        
        # Create Citta object
        return Citta(
            id=citta_id,
            name_pali=name_pali,
            name_thai=name_thai,
            name_english=name_english,
            category=category,
            type=citta_type,
            feeling=feeling,
            roots=roots,
            sankhara=sankhara,
            cetasika_ids=cetasika_ids,
            description=description,
            function=function,
            door_types=door_types,
            object_types=object_types
        )
    
    except (KeyError, ValueError, AttributeError) as e:
        # Return minimal valid Citta on parse error
        print(f"Warning: Failed to parse citta {citta_id}: {e}")
        return Citta(
            id=citta_id,
            name_pali=citta_data.get("name_pali", "Unknown"),
            name_thai=citta_data.get("name_thai", "ไม่ทราบ"),
            category=CittaCategory.AHETUKA,
            type=CittaType.ABYAKATA,
            feeling=Vedana.UPEKKHA,
            roots=[],
            cetasika_ids=[]
        )


def create_cetasika_from_json(cetasika_id: str, cetasika_data: Dict[str, Any]) -> Cetasika:
    """
    Create a Cetasika model from JSON data.
    
    Parses cetasikas.json format and creates fully-populated Cetasika object.
    
    Args:
        cetasika_id: Unique ID (e.g., "CETASIKA001")
        cetasika_data: Dict from cetasikas.json
        
    Returns:
        Cetasika object with all fields populated
    """
    try:
        # Extract core fields with fallbacks
        name_pali = cetasika_data.get("name_pali", "Unknown")
        name_thai = cetasika_data.get("name_thai", "ไม่ทราบ")
        name_english = cetasika_data.get("name_english")
        
        # Parse category (required)
        category_str = cetasika_data.get("category", "aññasamāna").lower()
        # Normalize category string
        if "annasaman" in category_str or "aññasamāna" in category_str:
            category_str = "aññasamāna"
        elif "sobhana" in category_str or "sobhaṇa" in category_str:
            category_str = "sobhaṇa"
        category = CetasikaCategory(category_str)
        
        # Parse subcategory (required)
        subcategory_str = cetasika_data.get("subcategory", "sabbacittasādhāraṇa").lower()
        # Normalize subcategory string
        if "universal" in subcategory_str or "sabbacittasādhāraṇa" in subcategory_str:
            subcategory_str = "sabbacittasādhāraṇa"
        elif "particular" in subcategory_str or "pakiṇṇaka" in subcategory_str:
            subcategory_str = "pakiṇṇaka"
        elif "moha" in subcategory_str:
            subcategory_str = "moha_group"
        elif "lobha" in subcategory_str:
            subcategory_str = "lobha_group"
        elif "dosa" in subcategory_str:
            subcategory_str = "dosa_group"
        elif "thina" in subcategory_str or "middha" in subcategory_str:
            subcategory_str = "thīna_middha"
        elif "vicikiccha" in subcategory_str or "vicikicchā" in subcategory_str:
            subcategory_str = "vicikicchā"
        elif "sobhana_universal" in subcategory_str or "sobhaṇa_sādhāraṇa" in subcategory_str:
            subcategory_str = "sobhaṇa_sādhāraṇa"
        elif "virati" in subcategory_str:
            subcategory_str = "virati"
        elif "appamanna" in subcategory_str or "appamaññā" in subcategory_str:
            subcategory_str = "appamaññā"
        elif "panna" in subcategory_str or "paññā" in subcategory_str:
            subcategory_str = "paññā"
        
        subcategory = CetasikaSubCategory(subcategory_str)
        
        # Parse ethical quality
        ethical_str = cetasika_data.get("ethical_quality", "abyakata").lower()
        ethical_quality = CittaType(ethical_str)
        
        # Additional metadata
        description = cetasika_data.get("description", "")
        function = cetasika_data.get("function", "")
        
        # Intensity (for simulation)
        intensity = cetasika_data.get("intensity", 1.0)
        
        # Create Cetasika object
        return Cetasika(
            id=cetasika_id,
            name_pali=name_pali,
            name_thai=name_thai,
            name_english=name_english,
            category=category,
            subcategory=subcategory,
            description=description,
            function=function,
            ethical_quality=ethical_quality,
            intensity=intensity
        )
    
    except (KeyError, ValueError, AttributeError) as e:
        # Return minimal valid Cetasika on parse error
        print(f"Warning: Failed to parse cetasika {cetasika_id}: {e}")
        return Cetasika(
            id=cetasika_id,
            name_pali=cetasika_data.get("name_pali", "Unknown"),
            name_thai=cetasika_data.get("name_thai", "ไม่ทราบ"),
            category=CetasikaCategory.ANNASAMAN,
            subcategory=CetasikaSubCategory.UNIVERSAL,
            description="",
            function="",
            ethical_quality=CittaType.ABYAKATA,
            intensity=1.0
        )


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Enums
    "CittaCategory",
    "CittaType",
    "CetasikaCategory",
    "CetasikaSubCategory",
    "Vedana",
    "Hetu",
    "Sankhara",
    
    # Models
    "Cetasika",
    "CetasikaManifold",
    "Citta",
    "CittaMoment",
    "CittaVithi",
    
    # Mapping classes
    "AnusayaCetasikaMap",
    "ParamiCetasikaMap",
    
    # Helper functions
    "load_cittas_from_json",
    "load_cetasikas_from_json",
    "create_citta_from_json",
    "create_cetasika_from_json",
]
