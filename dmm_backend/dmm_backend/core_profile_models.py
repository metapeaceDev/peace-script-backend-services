"""
Core Profile Models - Complete Buddhist Psychology Structure

Separated from main documents.py for clarity and maintainability.
"""

from __future__ import annotations  # Enable forward references

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ============================================================
# 1. CHARACTER STATUS - Spiritual Development Level
# ============================================================

class CharacterStatus(BaseModel):
    """
    CharacterStatus: ระดับการพัฒนาทางจิตวิญญาณ
    
    Based on Buddhist path progression:
    - Puthujjana (ปุถุชน): Common worldling
    - Sekha (เสขะ): Noble disciple in training (Sotāpanna → Anāgāmī)
    - Asekha (อเสขะ): Arahant (completed training)
    """
    type: str = Field(
        default="Puthujjana",
        description="Character type: Puthujjana, Sekha, or Asekha"
    )
    stage: str = Field(
        default="Common Worldling",
        description="Detailed stage description"
    )
    path_stage: Optional[str] = Field(
        default=None,
        description="Specific path stage: Sotāpanna, Sakadāgāmī, Anāgāmī, Arahant"
    )
    fetters_broken: List[str] = Field(
        default_factory=list,
        description="List of broken samyojana (fetters)"
    )
    fetters_remaining: List[str] = Field(
        default_factory=lambda: [
            "sakkayaditthi", "vicikiccha", "silabbataparamasa",
            "kamaraga", "patigha", "ruparaga", "aruparaga",
            "mana", "uddhacca", "avijja"
        ],
        description="Remaining fetters to overcome"
    )


# ============================================================
# 2. LIFE ESSENCE - Life Force and Blueprint
# ============================================================

class SocialStanding(BaseModel):
    """Social conditions from birth kamma"""
    birth_family_status: str = "Middle-class working family"
    karmic_reputation_baseline: str = "Neutral"
    inherited_social_capital: float = Field(default=50.0, ge=0, le=100)


class InitialConditions(BaseModel):
    """Birth conditions determined by past kamma"""
    social_standing: SocialStanding = Field(default_factory=lambda: SocialStanding())
    health_baseline: float = Field(default=80.0, ge=0, le=100)
    mental_clarity_baseline: float = Field(default=70.0, ge=0, le=100)
    emotional_stability_baseline: float = Field(default=60.0, ge=0, le=100)


class LifeBlueprintVipaka(BaseModel):
    """
    LifeBlueprint_Vipaka: Birth blueprint from past kamma
    Determines the realm, initial conditions, and life trajectory
    """
    birth_bhumi: str = Field(
        default="Human Realm",
        description="Birth realm (31 planes of existence)"
    )
    initial_conditions: InitialConditions = Field(default_factory=lambda: InitialConditions())
    lifespan_potential: int = Field(default=80, description="Maximum lifespan in years")
    special_abilities: List[str] = Field(default_factory=list)


class JivitindriyaMechanics(BaseModel):
    """
    Jivitindriya: Life faculty mechanics
    Controls the life energy and depletion rate
    """
    current_jivitindriya: float = Field(default=100.0, ge=0, le=100)
    max_jivitindriya: float = Field(default=100.0, ge=0, le=100)
    depletion_rate_per_day: float = Field(default=0.05, description="% per day")
    natural_regeneration_rate: float = Field(default=0.02, description="% per day from rest")
    meditation_boost_factor: float = Field(default=1.5, description="Regeneration multiplier from meditation")


class LifeEssence(BaseModel):
    """
    LifeEssence: พลังชีวิตและพิมพ์เขียวชีวิต
    
    Contains:
    - Age (current age in years)
    - Birth Blueprint (Vipaka)
    - Jivitindriya mechanics
    
    Age progression affects:
    - Life force depletion rate
    - Spiritual development stages
    - Physical/mental capabilities
    """
    age_in_years: int = Field(default=25, ge=0, le=150, description="Current age in years")
    life_blueprint_vipaka: LifeBlueprintVipaka = Field(default_factory=lambda: LifeBlueprintVipaka())
    jivitindriya_mechanics: JivitindriyaMechanics = Field(default_factory=lambda: JivitindriyaMechanics())


# ============================================================
# 3. PSYCHOLOGICAL MATRIX - Mental Structure
# ============================================================

class LatentTendencies(BaseModel):
    """
    Container for anusaya kilesa
    7 Latent Tendencies (อนุสัย 7)
    """
    anusaya_kilesa: Dict[str, Dict[str, float]] = Field(
        default_factory=lambda: {
            "kama_raga": {"level": 6.5},
            "patigha": {"level": 8.2},
            "mana": {"level": 6.0},
            "ditthi": {"level": 3.5},
            "vicikiccha": {"level": 4.0},
            "bhava_raga": {"level": 5.0},
            "avijja": {"level": 7.5},
        }
    )


class DominantTemperament(BaseModel):
    """
    Carita: Dominant temperament types
    - Raga-carita: Lustful
    - Dosa-carita: Hateful
    - Moha-carita: Deluded
    - Saddhā-carita: Faithful
    - Buddhi-carita: Intelligent
    - Vitakka-carita: Discursive
    """
    primary_carita: str = Field(
        default="Moha-carita (Deluded Temperament)",
        description="Primary temperament type"
    )
    secondary_carita: Optional[str] = Field(
        default=None,
        description="Secondary temperament"
    )
    temperament_strength: float = Field(default=7.0, ge=0, le=10)


class MentalSufferingThreshold(BaseModel):
    """Tolerance for mental suffering (vedanā)"""
    total_threshold: float = Field(default=5.0, ge=0, le=10)
    dukkha_sukha_balance: float = Field(default=0.0, ge=-10, le=10)
    equanimity_factor: float = Field(default=3.0, ge=0, le=10)


class VedanaToleranceProfile(BaseModel):
    """Tolerance profile for different types of vedanā"""
    mental_suffering_threshold: MentalSufferingThreshold = Field(
        default_factory=lambda: MentalSufferingThreshold()
    )
    physical_pain_tolerance: float = Field(default=5.0, ge=0, le=10)
    emotional_resilience: float = Field(default=5.0, ge=0, le=10)


class SannaImprint(BaseModel):
    """Past-life perception imprint"""
    imprint_type: str = Field(description="Type: Traumatic, Blissful, Neutral")
    cue_archetype: str = Field(description="Trigger archetype")
    intensity: float = Field(default=5.0, ge=0, le=10)
    description: Optional[str] = None


class SannaMatrix(BaseModel):
    """
    Saññā Matrix: Perception patterns
    Includes past-life imprints and learned associations
    """
    PastLife_Sanna_Imprints: List[SannaImprint] = Field(
        default_factory=lambda: [
            SannaImprint(
                imprint_type="Traumatic",
                cue_archetype="Betrayal",
                intensity=7.5,
                description="Deep-rooted fear of betrayal from past life"
            )
        ]
    )
    current_perception_biases: Dict[str, float] = Field(
        default_factory=lambda: {
            "negative_bias": 6.0,
            "positive_bias": 4.0,
            "neutral_clarity": 5.0
        }
    )


class PsychologicalMatrix(BaseModel):
    """
    PsychologicalMatrix: โครงสร้างจิตใจ
    
    Contains:
    - DominantTemperament: Primary character type (Carita)
    - LatentTendencies: Anusaya kilesa levels
    - VedanaToleranceProfile: Suffering tolerance
    - SannaMatrix: Perception patterns
    """
    dominant_temperament: DominantTemperament = Field(default_factory=lambda: DominantTemperament())
    latent_tendencies: LatentTendencies = Field(default_factory=lambda: LatentTendencies())
    vedana_tolerance_profile: VedanaToleranceProfile = Field(default_factory=lambda: VedanaToleranceProfile())
    sanna_matrix: SannaMatrix = Field(default_factory=lambda: SannaMatrix())
    
    # Backward compatibility - allow uppercase keys
    model_config = {"extra": "allow", "populate_by_name": True}


# ============================================================
# 4. SPIRITUAL ASSETS - Spiritual Accumulations
# ============================================================

class KammaLedger(BaseModel):
    """
    Kamma accounting system
    Tracks wholesome and unwholesome kamma points
    """
    kusala_stock_points: int = Field(default=500, ge=0)
    akusala_stock_points: int = Field(default=1200, ge=0)
    kiriya_actions_count: int = Field(default=0, ge=0, description="Neutral actions (Arahant only)")
    pending_vipaka_seeds: List[str] = Field(default_factory=list)
    
    # ✅ Added for kamma analytics support
    dominant_pending_kamma: List[Dict[str, Any]] = Field(default_factory=list, description="Top priority pending kamma")
    kamma_log: List[Dict[str, Any]] = Field(default_factory=list, description="Complete kamma history log")


class ParamiEntry(BaseModel):
    """Single perfection (pāramī) entry"""
    level: int = Field(default=1, ge=0, le=10)
    exp: int = Field(default=0, ge=0)
    mastery_percentage: float = Field(default=0.0, ge=0, le=100)


class ParamiPortfolio(BaseModel):
    """
    10 Pāramī (Perfections) Portfolio
    """
    perfections: Dict[str, ParamiEntry] = Field(
        default_factory=lambda: {
            "dana": ParamiEntry(level=4, exp=120),
            "sila": ParamiEntry(level=5, exp=160),
            "nekkhamma": ParamiEntry(level=3, exp=90),
            "panna": ParamiEntry(level=2, exp=70),
            "viriya": ParamiEntry(level=6, exp=210),
            "khanti": ParamiEntry(level=3, exp=140),
            "sacca": ParamiEntry(level=7, exp=260),
            "adhitthana": ParamiEntry(level=4, exp=150),
            "metta": ParamiEntry(level=2, exp=80),
            "upekkha": ParamiEntry(level=1, exp=40),
        }
    )


class MasteryLevel(BaseModel):
    """Mastery level for Sati/Panna"""
    level: int = Field(default=1, ge=0, le=10)
    exp: int = Field(default=0, ge=0)
    description: Optional[str] = None


class SamadhiLevel(BaseModel):
    """Samādhi (concentration) development"""
    current_jhana: Optional[str] = Field(
        default=None,
        description="Current jhāna attainment: first, second, third, fourth, or formless"
    )
    jhana_stability: float = Field(default=0.0, ge=0, le=10)
    access_concentration_strength: float = Field(default=3.0, ge=0, le=10)


class AbhinnaCapabilities(BaseModel):
    """
    6 Abhiññā (Higher Knowledges)
    Supernormal powers from deep meditation
    """
    iddhividha: bool = Field(default=False, description="Psychic powers")
    dibbasota: bool = Field(default=False, description="Divine ear")
    cetopariya: bool = Field(default=False, description="Mind reading")
    pubbenivasanussati: bool = Field(default=False, description="Past life recall")
    dibbacakkhu: bool = Field(default=False, description="Divine eye")
    asavakkhaya: bool = Field(default=False, description="Destruction of taints (Arahant only)")


class VirtueEngine(BaseModel):
    """
    Container for all virtue and spiritual development metrics
    """
    panna_mastery: MasteryLevel = Field(
        default_factory=lambda: MasteryLevel(level=2, exp=70)
    )
    sati_mastery: MasteryLevel = Field(
        default_factory=lambda: MasteryLevel(level=3, exp=120)
    )
    parami_portfolio: ParamiPortfolio = Field(default_factory=lambda: ParamiPortfolio())
    samadhi_attainment: SamadhiLevel = Field(default_factory=lambda: SamadhiLevel())
    abhinna_capabilities: AbhinnaCapabilities = Field(default_factory=lambda: AbhinnaCapabilities())


class SpiritualAssets(BaseModel):
    """
    SpiritualAssets: สมบัติทางจิตวิญญาณ
    
    Contains:
    - KammaLedger: Kamma accounting
    - VirtueEngine: All spiritual development (Pāramī, Samādhi, Abhiññā)
    """
    kamma_ledger: KammaLedger = Field(default_factory=lambda: KammaLedger())
    virtue_engine: VirtueEngine = Field(default_factory=lambda: VirtueEngine())
    
    model_config = {"extra": "allow", "populate_by_name": True}


# ============================================================
# COMPLETE CORE PROFILE
# ============================================================

# ============================================================
# NAMA/RUPA PROFILE (Computed Summary)
# ============================================================

class NamaProfile(BaseModel):
    """
    Nama (นาม): Mental constituents summary derived from CoreProfile
    - Dominant temperament (carita)
    - Average anusaya kilesa level
    - Sati/Paññā mastery levels
    """
    dominant_temperament: str
    anusaya_levels_avg: float = Field(ge=0, le=10)
    sati_level: int = Field(ge=0, le=10)
    panna_level: int = Field(ge=0, le=10)
    notes: Optional[str] = None


class RupaProfileSimplified(BaseModel):
    """
    RupaProfileSimplified: Simplified 4-field Rupa (รูป) for backward compatibility
    
    DEPRECATED: This is the old simplified version
    New system uses RupaProfile from rupa_models.py (28 Material Forms)
    
    Fields:
    - Age, health baseline, current life force (jīvitindriya)
    - Lifespan remaining (vipāka blueprint)
    
    Use this for:
    - API backward compatibility (?detailed=false)
    - Quick views that don't need full 28-rupa detail
    """
    age: int = Field(ge=0, le=150)
    health_baseline: float = Field(ge=0, le=100)
    current_life_force: float = Field(ge=0, le=100)
    lifespan_remaining: int = Field(ge=0)
    notes: Optional[str] = None


class NamaRupaProfile(BaseModel):
    """
    NamaRupaProfile: High-level mapping of mental (Nama/นาม) and physical (Rupa/รูป) aspects
    
    Migration Strategy (Option 2: Complete Replacement):
    - Old: rupa was embedded (4 fields)
    - New: rupa_ref points to RupaProfile document (28 Material Forms)
    - Computed properties provide backward compatibility
    
    Usage:
    - For simplified view: Use computed 'rupa' property (4 fields)
    - For detailed view: Fetch from rupa_models.RupaProfile via rupa_ref
    """
    nama: NamaProfile
    rupa: RupaProfileSimplified  # Simplified view (backward compatible)
    rupa_ref: Optional[str] = Field(None, description="Reference to detailed RupaProfile._id in rupa_profiles collection")
    summary: Optional[str] = None
    
    # Metadata for migration tracking
    migration_status: str = Field(default="legacy", description="legacy, migrating, or migrated")
    detailed_rupa_available: bool = Field(default=False, description="True if detailed 28-rupa exists")

class CoreProfile(BaseModel):
    """
    CoreProfile: โครงสร้างหลักของจิตตัวแบบ (Complete Buddhist Psychology Model)
    
    4 Major Components:
    1. CharacterStatus: Spiritual development level
    2. LifeEssence: Life force and blueprint
    3. PsychologicalMatrix: Mental structure
    4. SpiritualAssets: Spiritual accumulations
    
    Based on Abhidhamma and Buddhist path progression
    """
    character_status: CharacterStatus = Field(default_factory=lambda: CharacterStatus())
    life_essence: LifeEssence = Field(default_factory=lambda: LifeEssence())
    psychological_matrix: PsychologicalMatrix = Field(default_factory=lambda: PsychologicalMatrix())
    spiritual_assets: SpiritualAssets = Field(default_factory=lambda: SpiritualAssets())
    
    # Metadata
    version: str = Field(default="14.0", description="Core Profile version")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {"extra": "allow", "populate_by_name": True}

    def get_overall_spiritual_score(self) -> float:
        """Calculate overall spiritual development score (0-100)"""
        # Factor 1: Character stage (0-40 points)
        stage_scores = {
            "Puthujjana": 0,
            "Sotāpanna": 25,
            "Sakadāgāmī": 30,
            "Anāgāmī": 35,
            "Arahant": 40
        }
        stage_score = stage_scores.get(self.character_status.type, 0)
        
        # Factor 2: Parami average (0-30 points)
        parami_avg = sum(
            p.level for p in self.spiritual_assets.virtue_engine.parami_portfolio.perfections.values()
        ) / 10
        parami_score = (parami_avg / 10) * 30
        
        # Factor 3: Kilesa reduction (0-30 points)
        anusaya = self.psychological_matrix.latent_tendencies.anusaya_kilesa
        kilesa_avg = sum(v["level"] for v in anusaya.values()) / 7
        kilesa_score = ((10 - kilesa_avg) / 10) * 30
        
        return round(stage_score + parami_score + kilesa_score, 2)

    def is_noble(self) -> bool:
        """Check if character has attained noble status"""
        return self.character_status.type in ["Sekha", "Asekha"]

    def get_broken_fetters(self) -> List[str]:
        """Get list of broken fetters"""
        return self.character_status.fetters_broken
    
    def advance_age(self, years: int = 1) -> dict:
        """
        Advance age and apply life force effects
        
        Returns summary of changes including:
        - new age
        - life force depletion
        - lifespan remaining
        - warnings if approaching death
        """
        old_age = self.life_essence.age_in_years
        self.life_essence.age_in_years += years
        
        # Calculate life force depletion (age affects depletion rate)
        age_factor = 1.0 + (self.life_essence.age_in_years / 100)  # Older = faster depletion
        depletion = self.life_essence.jivitindriya_mechanics.depletion_rate_per_day * years * 365 * age_factor
        
        old_jivita = self.life_essence.jivitindriya_mechanics.current_jivitindriya
        self.life_essence.jivitindriya_mechanics.current_jivitindriya = max(
            0, 
            old_jivita - depletion
        )
        
        lifespan_remaining = self.life_essence.life_blueprint_vipaka.lifespan_potential - self.life_essence.age_in_years
        
        return {
            "age_changed": f"{old_age} → {self.life_essence.age_in_years}",
            "life_force_depleted": f"{old_jivita:.1f}% → {self.life_essence.jivitindriya_mechanics.current_jivitindriya:.1f}%",
            "lifespan_remaining": lifespan_remaining,
            "warning": "Critical: Approaching end of life!" if lifespan_remaining < 5 else None
        }

    def break_fetter(self, fetter_name: str) -> bool:
        """Break a fetter and update status"""
        if fetter_name in self.character_status.fetters_remaining:
            self.character_status.fetters_remaining.remove(fetter_name)
            self.character_status.fetters_broken.append(fetter_name)
            self._update_character_stage()
            return True
        return False

    def _update_character_stage(self):
        """Update character stage based on broken fetters"""
        broken_count = len(self.character_status.fetters_broken)
        
        if broken_count >= 10:
            self.character_status.type = "Asekha"
            self.character_status.stage = "Arahant"
            self.character_status.path_stage = "Arahant"
        elif broken_count >= 9:
            self.character_status.type = "Sekha"
            self.character_status.stage = "Anāgāmī trajectory"
            self.character_status.path_stage = "Anāgāmī"
        elif broken_count >= 7:
            self.character_status.type = "Sekha"
            self.character_status.stage = "Sakadāgāmī trajectory"
            self.character_status.path_stage = "Sakadāgāmī"
        elif broken_count >= 3:
            self.character_status.type = "Sekha"
            self.character_status.stage = "Sotāpanna trajectory"
            self.character_status.path_stage = "Sotāpanna"

    # ------------------------------------------------------------
    # Nama/Rupa mapping (computed)
    # ------------------------------------------------------------
    def get_nama_rupa_profile(self) -> NamaRupaProfile:
        """
        Compute Nama (นาม) and Rupa (รูป) profile from existing CoreProfile data.
        - Nama derives from PsychologicalMatrix and VirtueEngine
        - Rupa derives from LifeEssence and LifeBlueprint Vipaka
        """
        # Nama (นาม)
        anusaya = self.psychological_matrix.latent_tendencies.anusaya_kilesa
        avg_kilesa = 0.0
        if anusaya:
            avg_kilesa = sum(v.get("level", 0.0) for v in anusaya.values()) / max(len(anusaya), 1)
        nama = NamaProfile(
            dominant_temperament=self.psychological_matrix.dominant_temperament.primary_carita,
            anusaya_levels_avg=round(avg_kilesa, 2),
            sati_level=self.spiritual_assets.virtue_engine.sati_mastery.level,
            panna_level=self.spiritual_assets.virtue_engine.panna_mastery.level,
            notes="Derived from PsychologicalMatrix and VirtueEngine"
        )

        # Rupa (รูป) - Simplified view for backward compatibility
        age = self.life_essence.age_in_years
        health_baseline = self.life_essence.life_blueprint_vipaka.initial_conditions.health_baseline
        current_life_force = self.life_essence.jivitindriya_mechanics.current_jivitindriya
        lifespan_remaining = self.life_essence.life_blueprint_vipaka.lifespan_potential - age
        rupa = RupaProfileSimplified(
            age=age,
            health_baseline=health_baseline,
            current_life_force=round(current_life_force, 2),
            lifespan_remaining=max(lifespan_remaining, 0),
            notes="Derived from LifeEssence (Vipaka blueprint and Jīvitindriya)"
        )

        summary = (
            "นาม (Nama): อุปนิสัยเด่น = "
            f"{nama.dominant_temperament}, อนุสัยเฉลี่ย = {nama.anusaya_levels_avg}; "
            "รูป (Rupa): อายุ = "
            f"{rupa.age}, พลังชีวิต = {rupa.current_life_force:.1f}%, สุขภาพพื้นฐาน = {rupa.health_baseline:.1f}"
        )

        return NamaRupaProfile(nama=nama, rupa=rupa, summary=summary)
