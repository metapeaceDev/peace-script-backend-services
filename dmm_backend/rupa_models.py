"""
🔸 Rupa Models (รูปธรรม - Material Forms) - Buddhist Abhidhamma Physics
Based on: ปรมัตถโชติกะ (Paramattha Jotika)

Implements the complete system of 28 Material Forms:
- 4 Mahabhuta Rupa (Great Elements): Pathavi, Apo, Tejo, Vayo
- 24 Upadaya Rupa (Derived Forms): Pasada, Gocara, Bhava, Hadaya, etc.

References:
- ปรมัตถโชติกะ ปริจเฉทที่ ๑-๒-๖ (Paramattha Jotika, Chapters 1-2-6)
- อภิธัมมัตถสังคหะ (Abhidhammatthasangaha)
"""

from typing import Dict, List, Optional, Literal
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
from beanie import Document


# =============================================================================
# ENUMS & CONSTANTS
# =============================================================================

class MahabhutaType(str, Enum):
    """4 Great Elements (มหาภูตรูป ๔)"""
    PATHAVI = "pathavi"  # Earth - Solidity
    APO = "apo"          # Water - Cohesion
    TEJO = "tejo"        # Fire - Temperature
    VAYO = "vayo"        # Wind - Motion


class UpadayaCategory(str, Enum):
    """Categories of Derived Forms (อุปาทายรูป ๒๔)"""
    PASADA = "pasada"           # 5 Sense Organs
    GOCARA = "gocara"           # 7 Sense Objects  
    BHAVA = "bhava"             # 2 Sex
    HADAYA = "hadaya"           # 1 Heart-base
    JIVITA = "jivita"           # 1 Life Faculty
    AHARA = "ahara"             # 1 Nutriment
    PARICCHEDA = "pariccheda"   # 1 Space
    VINNATTI = "vinnatti"       # 2 Intimation
    VIKARA = "vikara"           # 3 Mutability
    LAKKHANA = "lakkhana"       # 4 Characteristics


class RupaSamutthana(str, Enum):
    """4 Origins of Rupa (รูปสมุฏฐาน ๔)"""
    KAMMA = "kamma"     # Kamma-born (from past actions)
    CITTA = "citta"     # Mind-born (from present consciousness)
    UTU = "utu"         # Temperature-born (from heat/cold)
    AHARA = "ahara"     # Nutriment-born (from food)


class YoniType(str, Enum):
    """4 Birth Origins (กําเนิด ๔)"""
    OPAPATIKA = "opapatika"     # Spontaneous birth
    SAMSEDAJA = "samsedaja"     # Moisture birth
    ANDAJA = "andaja"           # Egg birth
    JALABUJA = "jalabuja"       # Womb birth


class RupaKhana(str, Enum):
    """3 Moments of Rupa (รูปขณะ ๓)"""
    UPPADA = "uppada"     # Arising
    THITI = "thiti"       # Standing/Continuity
    BHANGA = "bhanga"     # Dissolution


# =============================================================================
# MAHABHUTA RUPA (Great Elements)
# =============================================================================

class PathaviCharacteristics(BaseModel):
    """ปถวีธาตุ - Earth Element (Solidity)"""
    hardness_level: float = Field(..., ge=0, le=100, description="ความแข็ง")
    softness_level: float = Field(..., ge=0, le=100, description="ความอ่อน")
    support_function: bool = Field(True, description="หน้าที่เป็นที่ตั้ง")
    
    @validator('softness_level')
    def validate_opposing_levels(cls, v, values):
        """Softness increases as hardness decreases"""
        if 'hardness_level' in values:
            expected_softness = 100 - values['hardness_level']
            if abs(v - expected_softness) > 10:  # Allow 10% tolerance
                return expected_softness
        return v


class ApoCharacteristics(BaseModel):
    """อาโปธาตุ - Water Element (Cohesion)"""
    cohesion_level: float = Field(..., ge=0, le=100, description="ความเกาะกุม")
    fluidity_level: float = Field(..., ge=0, le=100, description="ความไหล")
    binding_function: bool = Field(True, description="หน้าที่เชื่อมโยง")
    
    @validator('fluidity_level')
    def validate_opposing_levels(cls, v, values):
        """Fluidity increases as cohesion decreases"""
        if 'cohesion_level' in values:
            expected_fluidity = 100 - values['cohesion_level']
            if abs(v - expected_fluidity) > 10:
                return expected_fluidity
        return v


class TejoCharacteristics(BaseModel):
    """เตโชธาตุ - Fire Element (Temperature)"""
    heat_level: float = Field(..., ge=-50, le=150, description="ความร้อน (°C)")
    cold_level: float = Field(..., ge=-50, le=150, description="ความเย็น (°C)")
    maturation_function: bool = Field(True, description="หน้าที่ทำให้สุก")
    tejo_types: List[str] = Field(
        default=["usumatejo"],
        description="อุสุมา, สันตัปปน, ทหน, ชิรณ, ปาจก"
    )


class VayoCharacteristics(BaseModel):
    """วาโยธาตุ - Wind Element (Motion)"""
    tension_level: float = Field(..., ge=0, le=100, description="ความตึง")
    looseness_level: float = Field(..., ge=0, le=100, description="ความหย่อน")
    distension_function: bool = Field(True, description="หน้าที่เคร่งดึง")
    movement_function: bool = Field(True, description="หน้าที่เคลื่อนไหว")
    vayo_types: List[str] = Field(
        default=["uddhangama", "adhogama"],
        description="6 types: uddhangama, adhogama, kucchittha, kotthasa, angamanganusar, assasapassasa"
    )


class MahabhutaRupa(BaseModel):
    """มหาภูตรูป ๔ - 4 Great Elements"""
    pathavi: PathaviCharacteristics
    apo: ApoCharacteristics
    tejo: TejoCharacteristics
    vayo: VayoCharacteristics
    
    # Interdependence (all 4 must exist together)
    balanced: bool = Field(True, description="All 4 elements coexist")
    dominant_element: MahabhutaType = Field(
        default=MahabhutaType.PATHAVI,
        description="Which element is most prominent"
    )


# =============================================================================
# UPADAYA RUPA (Derived Forms)
# =============================================================================

class PasadaRupa(BaseModel):
    """ปสาทรูป ๕ - 5 Sense Organs"""
    cakkhu_pasada: Optional[float] = Field(None, ge=0, le=100, description="จักขุปสาท - Eye sensitivity")
    sota_pasada: Optional[float] = Field(None, ge=0, le=100, description="โสตปสาท - Ear sensitivity")
    ghana_pasada: Optional[float] = Field(None, ge=0, le=100, description="ฆานปสาท - Nose sensitivity")
    jivha_pasada: Optional[float] = Field(None, ge=0, le=100, description="ชิวหาปสาท - Tongue sensitivity")
    kaya_pasada: Optional[float] = Field(None, ge=0, le=100, description="กายปสาท - Body sensitivity")
    
    # Locations in body (according to Abhidhamma)
    locations: Dict[str, str] = Field(default={
        "cakkhu": "eye",
        "sota": "ear",
        "ghana": "nose",
        "jivha": "tongue",
        "kaya": "entire_body"
    })


class GocaraRupa(BaseModel):
    """วิสยรูป/โคจรรูป ๗ - 7 Sense Objects"""
    rupa_aramana: Optional[List[str]] = Field(None, description="รูปารมณ์ - Colors/visible forms")
    sadda_aramana: Optional[List[str]] = Field(None, description="สัททารมณ์ - Sounds")
    gandha_aramana: Optional[List[str]] = Field(None, description="คันธารมณ์ - Smells")
    rasa_aramana: Optional[List[str]] = Field(None, description="รสารมณ์ - Tastes")
    photthabba_aramana: Optional[Dict[str, float]] = Field(
        None,
        description="โผฏฐัพพารมณ์ - Tangibles (pathavi, tejo, vayo)"
    )


class BhavaRupa(BaseModel):
    """ภาวรูป ๒ - 2 Sex Designations"""
    itthībhāva: Optional[bool] = Field(None, description="อิตถีภาวะ - Femininity")
    purisabhāva: Optional[bool] = Field(None, description="ปุริสภาวะ - Masculinity")
    gender: Optional[Literal["female", "male", "neuter"]] = "neuter"


class HadayaRupa(BaseModel):
    """หทยรูป ๑ - Heart-base (Physical basis of mind)"""
    hadaya_vatthu_present: bool = Field(True, description="หทยวัตถุ present")
    location: str = Field("heart", description="Physical location")
    citta_support: bool = Field(True, description="Supports mind-consciousness")


class JivitaRupa(BaseModel):
    """ชีวิตรูป ๑ - Life Faculty"""
    rupa_jivitindriya: float = Field(100.0, ge=0, le=100, description="รูปชีวิตินทรีย์")
    maintains_kamma_rupa: bool = Field(True, description="Maintains kamma-born rupa")
    life_span_years: Optional[int] = Field(None, description="Expected lifespan")


class AharaRupa(BaseModel):
    """อาหารรูป ๑ - Nutritive Essence"""
    kabalinkara_ahara: float = Field(0.0, ge=0, le=100, description="กพฬิการาหาร - Oja")
    nutriment_level: float = Field(0.0, ge=0, le=100, description="Current nutriment")
    last_intake: Optional[datetime] = None


class ParicchedaRupa(BaseModel):
    """ปริจเฉทรูป ๑ - Space Element"""
    akasa_dhatu: bool = Field(True, description="อากาสธาตุ - Space between kalapas")
    separates_kalapas: bool = Field(True)


class VinnattiRupa(BaseModel):
    """วิญญัตติรูป ๒ - 2 Intimations"""
    kaya_vinnatti: Optional[str] = Field(None, description="กายวิญญัติ - Bodily intimation")
    vaci_vinnatti: Optional[str] = Field(None, description="วจีวิญญัติ - Verbal intimation")


class VikaraRupa(BaseModel):
    """วิการรูป ๓ - 3 Characteristics of Pliancy"""
    lahuta: float = Field(50.0, ge=0, le=100, description="ลหุตา - Lightness")
    muduta: float = Field(50.0, ge=0, le=100, description="มุทุตา - Softness")
    kammañata: float = Field(50.0, ge=0, le=100, description="กัมมัญญตา - Wieldiness")


class LakkhanaRupa(BaseModel):
    """ลักขณรูป ๔ - 4 Characteristics"""
    upacaya: float = Field(0.0, ge=0, le=100, description="อุปจยะ - Production/Growth")
    santati: float = Field(0.0, ge=0, le=100, description="สันตติ - Continuity")
    jarata: float = Field(0.0, ge=0, le=100, description="ชรตา - Decay/Aging")
    aniccata: float = Field(0.0, ge=0, le=100, description="อนิจจตา - Impermanence")


# =============================================================================
# RUPA KALAPA (Material Groups)
# =============================================================================

class RupaKalapa(BaseModel):
    """รูปกลาป - Material Group (Minimum: 8 rupa + mahabhuta 4)"""
    kalapa_id: str
    mahabhuta: MahabhutaRupa
    upadaya_count: int = Field(..., ge=1, description="Number of derived rupa")
    pasada: Optional[PasadaRupa] = None
    gocara: Optional[GocaraRupa] = None
    bhava: Optional[BhavaRupa] = None
    hadaya: Optional[HadayaRupa] = None
    jivita: Optional[JivitaRupa] = None
    ahara: Optional[AharaRupa] = None
    pariccheda: Optional[ParicchedaRupa] = None
    vinnatti: Optional[VinnattiRupa] = None
    vikara: VikaraRupa
    lakkhana: LakkhanaRupa
    
    samutthana: RupaSamutthana = Field(..., description="Origin of this kalapa")
    moment: RupaKhana = Field(RupaKhana.UPPADA, description="Current moment")
    lifetime_kshanas: int = Field(17, description="Lifetime in mind-moments (17 for kamma-born)")


# =============================================================================
# RUPA PROFILE (Complete Material Analysis)
# =============================================================================

class RupaProfile(Document):
    """
    รูปสังขาร - Complete Rupa Profile for a being
    Linked to DigitalMindModel via model_id
    """
    model_id: str = Field(..., description="Reference to DigitalMindModel")
    
    # Birth & Origin
    yoni: YoniType = Field(..., description="Birth type")
    patisandhi_kalapas: List[RupaKalapa] = Field(
        default=[],
        description="Kalapas present at rebirth-linking"
    )
    
    # Current Rupa State (28 Material Forms)
    mahabhuta_state: MahabhutaRupa
    pasada_state: PasadaRupa
    gocara_state: GocaraRupa
    bhava_state: BhavaRupa
    hadaya_state: HadayaRupa
    jivita_state: JivitaRupa
    ahara_state: AharaRupa
    pariccheda_state: ParicchedaRupa
    vinnatti_state: VinnattiRupa
    vikara_state: VikaraRupa
    lakkhana_state: LakkhanaRupa
    
    # Kalapa Analysis
    active_kalapas: List[RupaKalapa] = Field(default=[], description="Currently existing kalapas")
    total_kalapa_count: int = 0
    
    # Samutthana Breakdown
    kamma_rupa_count: int = 0
    citta_rupa_count: int = 0
    utu_rupa_count: int = 0
    ahara_rupa_count: int = 0
    
    # Lifecycle
    age_in_moments: int = Field(0, description="Age in citta-kshanas")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "rupa_profiles"
    
    # =============================================================================
    # COMPUTED PROPERTIES (for backward compatibility with old 4-field RupaProfile)
    # =============================================================================
    
    @property
    def age(self) -> int:
        """
        Computed: Convert age_in_moments back to years
        Backward compatible with old RupaProfile.age
        """
        # Rough approximation: age_in_moments / (365 * 24 * 60 * 60 * 1000)
        # Each moment ~ 1ms, so 1 year ~ 31,536,000,000 moments
        return self.age_in_moments // (365 * 24 * 60 * 60 * 1000)
    
    @property
    def health_baseline(self) -> float:
        """
        Computed: Average of mahabhuta balance + vikara
        Backward compatible with old RupaProfile.health_baseline
        
        Formula:
        - 40%: Mahabhuta balance (all 4 elements balanced)
        - 30%: Vikara quality (lahuta, muduta, kammannata)
        - 20%: Pasada average (5 sense organs)
        - 10%: Ahara nutriment level
        """
        # Mahabhuta balance (normalize each element to 0-100)
        pathavi_balance = (self.mahabhuta_state.pathavi.hardness_level + 
                          self.mahabhuta_state.pathavi.softness_level) / 2
        apo_balance = (self.mahabhuta_state.apo.cohesion_level + 
                      self.mahabhuta_state.apo.fluidity_level) / 2
        tejo_balance = min(100, max(0, (self.mahabhuta_state.tejo.heat_level - 36) * 50))  # 36-38°C → 0-100
        vayo_balance = (self.mahabhuta_state.vayo.tension_level + 
                       self.mahabhuta_state.vayo.looseness_level) / 2
        
        mahabhuta_avg = (pathavi_balance + apo_balance + tejo_balance + vayo_balance) / 4
        
        # Vikara average
        vikara_avg = (
            self.vikara_state.lahuta +
            self.vikara_state.muduta +
            self.vikara_state.kammañata  # Correct spelling with ñ
        ) / 3
        
        # Pasada average (if any exist)
        pasada_count = 0
        pasada_sum = 0.0
        if self.pasada_state.cakkhu_pasada:
            pasada_sum += self.pasada_state.cakkhu_pasada
            pasada_count += 1
        if self.pasada_state.sota_pasada:
            pasada_sum += self.pasada_state.sota_pasada
            pasada_count += 1
        if self.pasada_state.ghana_pasada:
            pasada_sum += self.pasada_state.ghana_pasada
            pasada_count += 1
        if self.pasada_state.jivha_pasada:
            pasada_sum += self.pasada_state.jivha_pasada
            pasada_count += 1
        if self.pasada_state.kaya_pasada:
            pasada_sum += self.pasada_state.kaya_pasada
            pasada_count += 1
        
        pasada_avg = pasada_sum / pasada_count if pasada_count > 0 else 50.0
        
        # Ahara nutriment (Oja level)
        ahara_level = self.ahara_state.kabalinkara_ahara
        
        # Weighted average
        health = (
            mahabhuta_avg * 0.40 +
            vikara_avg * 0.30 +
            pasada_avg * 0.20 +
            ahara_level * 0.10
        )
        
        return min(100, max(0, health))
    
    @property
    def current_life_force(self) -> float:
        """
        Computed: Direct mapping from jivita_state
        Backward compatible with old RupaProfile.current_life_force
        
        Returns: rupa_jivitindriya (0-100)
        """
        return self.jivita_state.rupa_jivitindriya
    
    @property
    def lifespan_remaining(self) -> int:
        """
        Computed: Estimated remaining lifespan based on current age, health, and life force
        Backward compatible with old RupaProfile.lifespan_remaining
        
        Formula:
        - Base lifespan: 80 years (average human)
        - Adjusted by: health_baseline, current_life_force
        - Result: Potential remaining years
        """
        base_lifespan = 80  # Average human lifespan
        current_age = self.age
        
        # Health and life force factors (0-1 scale)
        health_factor = self.health_baseline / 100
        life_force_factor = self.current_life_force / 100
        
        # Combined vitality factor
        vitality = (health_factor + life_force_factor) / 2
        
        # Calculate potential remaining years
        potential_remaining = (base_lifespan - current_age) * vitality
        
        return max(0, int(potential_remaining))


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class CalculateRupaRequest(BaseModel):
    """Request to calculate rupa state"""
    model_id: str
    citta_state: Optional[Dict] = None
    utu_temperature: Optional[float] = None
    ahara_intake: Optional[float] = None


class RupaAnalysisResponse(BaseModel):
    """Response with complete rupa analysis"""
    model_id: str
    total_rupa_count: int
    mahabhuta_analysis: Dict[str, float]
    dominant_element: MahabhutaType
    pasada_status: Dict[str, float]
    kalapa_distribution: Dict[str, int]
    samutthana_breakdown: Dict[str, int]
    lifecycle_stage: str
    buddhist_accuracy: float = Field(..., description="Accuracy according to Abhidhamma")


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def create_suddhatthaka_kalapa(samutthana: RupaSamutthana) -> RupaKalapa:
    """
    Create basic Suddhatthaka (Pure Octad) kalapa
    Contains: 4 Mahabhuta + 4 Lakkhana (minimum 8 rupa)
    """
    return RupaKalapa(
        kalapa_id=f"suddhatthaka_{samutthana}_{datetime.utcnow().timestamp()}",
        mahabhuta=MahabhutaRupa(
            pathavi=PathaviCharacteristics(hardness_level=50, softness_level=50),
            apo=ApoCharacteristics(cohesion_level=50, fluidity_level=50),
            tejo=TejoCharacteristics(heat_level=37, cold_level=0),
            vayo=VayoCharacteristics(tension_level=50, looseness_level=50)
        ),
        upadaya_count=4,
        vikara=VikaraRupa(),
        lakkhana=LakkhanaRupa(),
        samutthana=samutthana,
        moment=RupaKhana.UPPADA
    )


def validate_rupa_28(rupa_profile: RupaProfile) -> bool:
    """Validate that all 28 rupa are properly accounted for"""
    mahabhuta_count = 4  # Always 4
    upadaya_count = (
        (5 if rupa_profile.pasada_state else 0) +  # 5 pasada
        (7 if rupa_profile.gocara_state else 0) +  # 7 gocara
        (1 if rupa_profile.bhava_state and rupa_profile.bhava_state.gender != "neuter" else 0) +  # 1-2 bhava
        (1 if rupa_profile.hadaya_state.hadaya_vatthu_present else 0) +  # 1 hadaya
        1 +  # 1 jivita (always present in living being)
        1 +  # 1 ahara (always present)
        1 +  # 1 pariccheda (always present)
        (1 if rupa_profile.vinnatti_state.kaya_vinnatti or rupa_profile.vinnatti_state.vaci_vinnatti else 0) +  # 0-2 vinnatti
        3 +  # 3 vikara (always present)
        4    # 4 lakkhana (always present)
    )
    
    total = mahabhuta_count + upadaya_count
    return total <= 28  # Can be less if some optional rupa not present
