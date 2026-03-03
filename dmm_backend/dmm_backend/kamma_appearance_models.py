"""
🔸 Kamma-Appearance Models - Physical Appearance from Kamma
Based on: Buddhist Vipāka (Kamma Results) + Rupa 28 + Abhidhamma

Implements the system to generate physical appearance from individual kamma:
- กายกรรม (Kāyakamma) → Physical health, body characteristics
- วจีกรรม (Vacīkamma) → Voice tone, speech patterns
- มโนกรรม (Manokamma) → Facial expressions, demeanor, movements

References:
- อังคุตรนิกาย (Anguttara Nikaya) AN 8.40
- มิลินทปัญหา (Milindapañha) - Kamma-born beauty/ugliness
- วิสุทธิมรรค (Visuddhimagga) IX.123 - Kamma-born materiality
- KAMMA_APPEARANCE_ANALYSIS.md (Project documentation)
"""

from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from beanie import Document

# Import Kamma enums from kamma_engine
from modules.kamma_engine import KammaCategory


# =============================================================================
# KAMMA APPEARANCE SCORE MODELS
# =============================================================================

class HealthScore(BaseModel):
    """
    สุขภาพและลักษณะร่างกายจาก กายกรรม (Physical Kamma)
    """
    # Overall Health (0-100)
    overall_health: float = Field(50.0, ge=0, le=100, description="สุขภาพโดยรวม")
    
    # Body Characteristics
    vitality_level: float = Field(50.0, ge=0, le=100, description="พลังชีวิต/ความมีชีวิตชีวา")
    body_strength: float = Field(50.0, ge=0, le=100, description="ความแข็งแรงของร่างกาย")
    skin_quality: float = Field(50.0, ge=0, le=100, description="คุณภาพผิวพรรณ")
    
    # Specific Traits (text descriptions)
    skin_tone_desc: str = Field("fair", description="สีผิว (pale/fair/tan/dark/radiant)")
    body_type_tendency: str = Field("average", description="รูปร่าง (frail/slim/average/athletic/robust)")
    health_status_desc: str = Field("healthy", description="สถานะสุขภาพ")
    
    # Fitness & Energy
    fitness_level: int = Field(5, ge=0, le=10, description="ระดับสมรรถภาพ")
    energy_level: float = Field(50.0, ge=0, le=100, description="ระดับพลังงาน")
    
    # Lifespan Impact
    lifespan_modifier: int = Field(0, ge=-50, le=50, description="ผลกระทบต่ออายุขัย (ปี)")
    
    # Influenced by Kamma
    harm_kamma_score: float = Field(0.0, description="คะแนนกรรมทำร้าย (Pāṇātipāta)")
    protection_kamma_score: float = Field(0.0, description="คะแนนกรรมคุ้มครอง (Mettā/Karuṇā)")
    generosity_score: float = Field(0.0, description="คะแนนทาน (Dāna)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "overall_health": 75.0,
                "vitality_level": 80.0,
                "body_strength": 70.0,
                "skin_quality": 75.0,
                "skin_tone_desc": "radiant, healthy glow",
                "body_type_tendency": "athletic",
                "health_status_desc": "excellent",
                "fitness_level": 8,
                "energy_level": 80.0,
                "lifespan_modifier": 15,
                "harm_kamma_score": 5.0,
                "protection_kamma_score": 85.0,
                "generosity_score": 70.0
            }
        }


class VoiceScore(BaseModel):
    """
    เสียงและการพูดจาก วจีกรรม (Verbal Kamma)
    """
    # Overall Voice Quality (0-100)
    clarity_score: float = Field(50.0, ge=0, le=100, description="ความชัดเจนของเสียง")
    pleasantness_score: float = Field(50.0, ge=0, le=100, description="ความไพเราะ")
    confidence_score: float = Field(50.0, ge=0, le=100, description="ความมั่นใจในการพูด")
    
    # Voice Characteristics (text descriptions)
    voice_tone_desc: str = Field("neutral", description="น้ำเสียง (clear/raspy/harsh/soft/warm)")
    speech_pattern_desc: str = Field("normal", description="ลักษณะการพูด (fluent/hesitant/eloquent)")
    pitch_tendency: str = Field("medium", description="ระดับเสียง (high/medium/low)")
    volume_tendency: str = Field("moderate", description="ความดัง (loud/moderate/soft)")
    
    # Speaking Quality
    articulation_quality: float = Field(50.0, ge=0, le=100, description="ความชัดเจนในการออกเสียง")
    pace_comfort: float = Field(50.0, ge=0, le=100, description="จังหวะการพูดที่สบาย")
    
    # Verbal Habits
    verbal_tics: List[str] = Field(default_factory=list, description="พฤติกรรมการพูด")
    speech_impediments: List[str] = Field(default_factory=list, description="อุปสรรคในการพูด")
    
    # Influenced by Kamma
    lying_kamma_score: float = Field(0.0, description="คะแนนกรรมโกหก (Musāvāda)")
    truthful_kamma_score: float = Field(0.0, description="คะแนนกรรมพูดจริง (Sacca)")
    harsh_speech_score: float = Field(0.0, description="คะแนนกรรมพูดหยาบ (Pharusavācā)")
    gentle_speech_score: float = Field(0.0, description="คะแนนกรรมพูดอ่อนหวาน")
    divisive_speech_score: float = Field(0.0, description="คะแนนกรรมพูดส่อเสียด (Pisuṇavācā)")
    harmonious_speech_score: float = Field(0.0, description="คะแนนกรรมพูดสร้างความสามัคคี")
    
    class Config:
        json_schema_extra = {
            "example": {
                "clarity_score": 85.0,
                "pleasantness_score": 80.0,
                "confidence_score": 75.0,
                "voice_tone_desc": "clear, resonant, warm",
                "speech_pattern_desc": "eloquent, flowing",
                "pitch_tendency": "medium-low",
                "volume_tendency": "moderate",
                "articulation_quality": 85.0,
                "pace_comfort": 80.0,
                "verbal_tics": [],
                "speech_impediments": [],
                "lying_kamma_score": 2.0,
                "truthful_kamma_score": 88.0,
                "harsh_speech_score": 5.0,
                "gentle_speech_score": 80.0
            }
        }


class DemeanorScore(BaseModel):
    """
    ท่าทาง สีหน้า และการแสดงออกจาก มโนกรรม (Mental Kamma)
    """
    # Overall Demeanor (0-100)
    approachability: float = Field(50.0, ge=0, le=100, description="ความเข้าถึงง่าย")
    charisma: float = Field(50.0, ge=0, le=100, description="เสน่ห์/ความดึงดูด")
    peacefulness: float = Field(50.0, ge=0, le=100, description="ความสงบ")
    tension_level: float = Field(50.0, ge=0, le=100, description="ความตึงเครียด (0=relaxed, 100=tense)")
    
    # Facial Expression
    default_expression: str = Field("neutral", description="สีหน้าปกติ (smile/neutral/frown/scowl)")
    eye_expression: str = Field("calm", description="สีหน้าตา (kind/calculating/warm/shifty)")
    facial_tension: str = Field("relaxed", description="ความตึงหน้า (relaxed/neutral/tense)")
    
    # Body Language
    posture_desc: str = Field("neutral", description="ท่าทาง (upright/slouched/tense/relaxed)")
    gait_desc: str = Field("normal", description="การเดิน (confident/hesitant/graceful/aggressive)")
    movement_quality: str = Field("normal", description="คุณภาพการเคลื่อนไหว (smooth/jerky/sluggish)")
    
    # Gestures & Mannerisms
    typical_gestures: List[str] = Field(default_factory=list, description="ท่าทางมือที่พบบ่อย")
    nervous_habits: List[str] = Field(default_factory=list, description="พฤติกรรมเมื่อประหม่า")
    
    # Social Presence
    first_impression: str = Field("neutral", description="ความประทับใจแรกพบ")
    aura_quality: str = Field("neutral", description="กลิ่นอาย (peaceful/hostile/warm/cold)")
    
    # Influenced by Kamma
    ill_will_score: float = Field(0.0, description="คะแนนกรรมพยาบาท (Byāpāda)")
    loving_kindness_score: float = Field(0.0, description="คะแนนกรรมเมตตา (Mettā)")
    covetousness_score: float = Field(0.0, description="คะแนนกรรมโลภะ (Abhijjhā)")
    generosity_mind_score: float = Field(0.0, description="คะแนนใจบุญ (Cāga)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "approachability": 85.0,
                "charisma": 75.0,
                "peacefulness": 80.0,
                "tension_level": 20.0,
                "default_expression": "gentle smile",
                "eye_expression": "kind, warm",
                "facial_tension": "relaxed",
                "posture_desc": "upright, open",
                "gait_desc": "confident, smooth",
                "movement_quality": "graceful",
                "typical_gestures": ["open palms", "inclusive gestures"],
                "nervous_habits": [],
                "first_impression": "peaceful, trustworthy",
                "aura_quality": "warm, peaceful",
                "ill_will_score": 5.0,
                "loving_kindness_score": 85.0,
                "covetousness_score": 10.0,
                "generosity_mind_score": 80.0
            }
        }


class KammaAppearanceProfile(BaseModel):
    """
    โปรไฟล์ลักษณะภายนอกที่เกิดจากกรรม
    Complete analysis of appearance based on individual kamma ledger
    """
    # Identity
    model_id: str = Field(..., description="Reference to DigitalMindModel")
    profile_id: str = Field(..., description="Unique profile ID")
    
    # Three Main Scores
    health_score: HealthScore = Field(..., description="สุขภาพจากกายกรรม")
    voice_score: VoiceScore = Field(..., description="เสียงจากวจีกรรม")
    demeanor_score: DemeanorScore = Field(..., description="ท่าทางจากมโนกรรม")
    
    # Overall Analysis
    overall_kamma_balance: float = Field(0.0, ge=-100, le=100, description="ดุลกรรมโดยรวม")
    kusala_percentage: float = Field(50.0, ge=0, le=100, description="เปอร์เซ็นต์กุศล")
    akusala_percentage: float = Field(50.0, ge=0, le=100, description="เปอร์เซ็นต์อกุศล")
    
    # Kamma Breakdown by Category (count)
    kamma_category_counts: Dict[str, int] = Field(default_factory=dict, description="จำนวนกรรมแต่ละประเภท")
    
    # Analysis Metadata
    total_kamma_analyzed: int = Field(0, description="จำนวนกรรมที่วิเคราะห์")
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    buddhist_accuracy: float = Field(100.0, description="ความถูกต้องตามหลักพระพุทธศาสนา")
    
    # Generation Notes
    kamma_influence_summary: str = Field("", description="สรุปอิทธิพลของกรรม")
    distinctive_features: List[str] = Field(default_factory=list, description="ลักษณะเด่นที่เกิดจากกรรม")
    
    class Config:
        json_schema_extra = {
            "example": {
                "model_id": "peace-mind-001",
                "profile_id": "kamma_appear_abc123",
                "overall_kamma_balance": 35.5,
                "kusala_percentage": 67.75,
                "akusala_percentage": 32.25,
                "total_kamma_analyzed": 45,
                "kamma_influence_summary": "High mettā and truthful speech create warm, trustworthy appearance. Past harm creates slight health reduction.",
                "distinctive_features": [
                    "Warm, genuine smile from mettā practice",
                    "Clear voice from truthful speech",
                    "Slightly pale complexion from past harm"
                ]
            }
        }


# =============================================================================
# KAMMA-TO-APPEARANCE MAPPING TABLES
# =============================================================================

class KammaAppearanceMapping:
    """
    Mapping tables for Kamma → Physical Appearance
    Based on Buddhist scriptures and Abhidhamma analysis
    """
    
    # Kāyakamma (Physical Actions) → Body/Health
    KAYAKAMMA_TO_HEALTH = {
        KammaCategory.PANATIPATA: {
            "health_impact": -15,
            "vitality_impact": -20,
            "skin_tone": "pale, sickly undertone",
            "body_type": "frail, weak",
            "lifespan_modifier": -10,
            "distinctive_features": ["sunken eyes", "thin frame", "weak constitution"]
        },
        KammaCategory.PANATIPATA_VIRATI: {
            "health_impact": 15,
            "vitality_impact": 20,
            "skin_tone": "radiant, healthy glow",
            "body_type": "strong, robust",
            "lifespan_modifier": 15,
            "distinctive_features": ["bright eyes", "strong build", "vibrant presence"]
        },
        KammaCategory.ADINNADANA: {
            "health_impact": -5,
            "material_impact": -20,
            "appearance_quality": "worn, poor maintenance",
            "distinctive_features": ["signs of poverty", "worn clothing"]
        },
        KammaCategory.ADINNADANA_VIRATI: {
            "health_impact": 5,
            "material_impact": 20,
            "appearance_quality": "well-maintained, dignified",
            "distinctive_features": ["quality items", "dignified presence"]
        },
        KammaCategory.DANA: {
            "health_impact": 10,
            "vitality_impact": 15,
            "skin_tone": "healthy, warm",
            "charisma_boost": 15,
            "distinctive_features": ["generous smile", "open demeanor"]
        },
        KammaCategory.METTA: {
            "health_impact": 12,
            "vitality_impact": 15,
            "facial_symmetry": "high symmetry",
            "skin_quality": 20,
            "distinctive_features": ["symmetrical features", "warm expression", "peaceful aura"]
        }
    }
    
    # Vacīkamma (Verbal Actions) → Voice/Speech
    VACIKAMMA_TO_VOICE = {
        KammaCategory.MUSAVADA: {
            "clarity_impact": -20,
            "confidence_impact": -15,
            "voice_tone": "uncertain, wavering",
            "speech_pattern": "hesitant, inconsistent",
            "verbal_tics": ["frequent pauses", "avoiding eye contact", "clearing throat"]
        },
        KammaCategory.MUSAVADA_VIRATI: {
            "clarity_impact": 20,
            "confidence_impact": 18,
            "voice_tone": "clear, resonant",
            "speech_pattern": "confident, consistent",
            "verbal_tics": []
        },
        KammaCategory.PHARUSAVACA: {
            "clarity_impact": 5,
            "pleasantness_impact": -25,
            "voice_tone": "sharp, abrasive",
            "speech_pattern": "clipped, aggressive",
            "pitch_tendency": "higher when stressed",
            "facial_impact": "hard lines, tense jaw"
        },
        KammaCategory.PHARUSAVACA_VIRATI: {
            "clarity_impact": 5,
            "pleasantness_impact": 25,
            "voice_tone": "soft, soothing",
            "speech_pattern": "gentle, flowing",
            "pitch_tendency": "calm, even",
            "facial_impact": "soft features, relaxed"
        },
        KammaCategory.PISUNAVACA: {
            "clarity_impact": 0,
            "pleasantness_impact": -15,
            "confidence_impact": -10,
            "social_impact": "suspicious, divisive",
            "speech_pattern": "calculating, manipulative",
            "facial_impact": "shifty eyes, calculating expression"
        },
        KammaCategory.PISUNAVACA_VIRATI: {
            "clarity_impact": 10,
            "pleasantness_impact": 15,
            "confidence_impact": 12,
            "social_impact": "trustworthy, unifying",
            "speech_pattern": "harmonious, inclusive",
            "facial_impact": "warm eyes, genuine smile"
        }
    }
    
    # Manokamma (Mental Actions) → Demeanor/Expression
    MANOKAMMA_TO_DEMEANOR = {
        KammaCategory.BYAPADA: {
            "approachability_impact": -25,
            "tension_increase": 30,
            "facial_expression": "frown, scowl",
            "eye_expression": "hostile, angry",
            "posture": "tense, aggressive",
            "gait": "aggressive, stomping",
            "gestures": ["clenched fists", "sharp movements", "pointing"],
            "aura": "hostile, intimidating"
        },
        KammaCategory.ABYAPADA: {
            "approachability_impact": 25,
            "tension_decrease": 30,
            "facial_expression": "gentle smile",
            "eye_expression": "kind, warm",
            "posture": "open, relaxed",
            "gait": "smooth, flowing",
            "gestures": ["open palms", "gentle movements", "welcoming"],
            "aura": "peaceful, approachable"
        },
        KammaCategory.METTA: {
            "approachability_impact": 28,
            "charisma_boost": 25,
            "peacefulness_boost": 30,
            "tension_decrease": 35,
            "facial_expression": "warm, genuine smile",
            "eye_expression": "compassionate, kind",
            "posture": "open, inviting",
            "gait": "graceful, flowing",
            "gestures": ["embracing gestures", "gentle touch", "supportive"],
            "aura": "loving, peaceful",
            "distinctive_features": ["laugh lines", "warm gaze", "peaceful presence"]
        },
        KammaCategory.ABHIJJHA: {
            "approachability_impact": -15,
            "tension_increase": 20,
            "facial_expression": "calculating, greedy",
            "eye_expression": "covetous, grasping",
            "posture": "leaning forward, grasping",
            "gestures": ["grasping movements", "fidgeting", "possessive"],
            "distinctive_features": ["furrowed brow", "tense expression"]
        },
        KammaCategory.ANABHIJJHA: {
            "approachability_impact": 18,
            "tension_decrease": 20,
            "facial_expression": "content, peaceful",
            "eye_expression": "clear, content",
            "posture": "upright, at ease",
            "gestures": ["open, generous movements"],
            "distinctive_features": ["clear eyes", "relaxed brow"]
        },
        KammaCategory.BHAVANA: {
            "peacefulness_boost": 35,
            "tension_decrease": 40,
            "facial_expression": "serene, mindful",
            "eye_expression": "clear, present",
            "posture": "upright, stable",
            "movement_quality": "mindful, deliberate",
            "aura": "peaceful, centered",
            "distinctive_features": ["serene expression", "mindful presence", "stable posture"]
        }
    }
    
    @classmethod
    def get_health_impact(cls, kamma_category: KammaCategory) -> Dict:
        """Get health impact from specific kamma category"""
        return cls.KAYAKAMMA_TO_HEALTH.get(kamma_category, {})
    
    @classmethod
    def get_voice_impact(cls, kamma_category: KammaCategory) -> Dict:
        """Get voice impact from specific kamma category"""
        return cls.VACIKAMMA_TO_VOICE.get(kamma_category, {})
    
    @classmethod
    def get_demeanor_impact(cls, kamma_category: KammaCategory) -> Dict:
        """Get demeanor impact from specific kamma category"""
        return cls.MANOKAMMA_TO_DEMEANOR.get(kamma_category, {})


# =============================================================================
# DOCUMENT MODEL FOR STORAGE
# =============================================================================

class KammaAppearanceDocument(Document):
    """
    MongoDB Document for storing Kamma Appearance Profiles
    """
    model_id: str = Field(description="Reference to DigitalMindModel")
    profile: KammaAppearanceProfile = Field(..., description="Complete appearance profile")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "kamma_appearance_profiles"
        indexes = ["model_id"]
    
    class Config:
        json_schema_extra = {
            "example": {
                "model_id": "peace-mind-001",
                "profile": {
                    "profile_id": "kamma_appear_abc123",
                    "overall_kamma_balance": 35.5,
                    "kusala_percentage": 67.75
                }
            }
        }


# =============================================================================
# BUDDHIST SCRIPTURAL REFERENCES
# =============================================================================

# =============================================================================
# AI GENERATED IMAGE HISTORY MODELS
# =============================================================================

class GeneratedImageMetadata(BaseModel):
    """
    Metadata สำหรับภาพที่สร้างด้วย AI
    
    NEW: Multi-resolution support for optimal performance
    - image_base64: Full resolution (512x768, 768x1024) ~500KB-1MB
    - thumbnail_medium_base64: 512x512 for gallery grid ~50-100KB
    - thumbnail_small_base64: 256x256 for actor cards ~15-30KB
    """
    # Image Data - Full Resolution
    image_base64: str = Field(..., description="Base64 encoded full resolution image")
    image_format: str = Field("png", description="Image format (png/jpg)")
    image_size_kb: float = Field(0.0, description="ขนาดไฟล์เต็มขนาด (KB)")
    
    # NEW: Thumbnails for Performance
    thumbnail_small_base64: Optional[str] = Field(
        None,
        description="256x256 thumbnail for actor cards/avatars (~15-30KB)"
    )
    thumbnail_medium_base64: Optional[str] = Field(
        None,
        description="512x512 thumbnail for gallery grid (~50-100KB)"
    )
    thumbnail_small_size_kb: Optional[float] = Field(
        None,
        description="Small thumbnail file size (KB)"
    )
    thumbnail_medium_size_kb: Optional[float] = Field(
        None,
        description="Medium thumbnail file size (KB)"
    )
    
    # Generation Parameters
    model_id: str = Field(..., description="Character model ID")
    actor_id: Optional[str] = Field(None, description="Actor ID (for character-specific images)")
    style: str = Field(..., description="Image style (realistic/anime/portrait/cinematic)")
    width: int = Field(512, description="Image width")
    height: int = Field(768, description="Image height")
    steps: int = Field(30, description="Sampling steps")
    cfg: float = Field(7.0, description="CFG scale")
    
    # Prompts
    positive_prompt: str = Field(..., description="Prompt used")
    negative_prompt: str = Field(..., description="Negative prompt used")
    seed: Optional[int] = Field(None, description="Random seed (for reproducibility)")
    
    # Generation Info
    generation_time: float = Field(0.0, description="Generation time (seconds)")
    model_used: str = Field("", description="ComfyUI model name")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When generated")
    
    # User Actions
    is_favorite: bool = Field(False, description="Marked as favorite")
    is_profile_avatar: bool = Field(False, description="Used as profile avatar")
    notes: str = Field("", description="User notes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "model_id": "peace-mind-001",
                "style": "realistic",
                "width": 512,     # ✨ OPTIMIZED: ลดจาก 768
                "height": 768,    # ✨ OPTIMIZED: ลดจาก 1024
                "steps": 25,      # ✨ OPTIMIZED: ลดจาก 35
                "cfg": 7.5,       # ✨ OPTIMIZED: ลดจาก 8.5
                "positive_prompt": "a serene Thai Buddhist monk...",
                "negative_prompt": "ugly, deformed...",
                "seed": 1234567890,
                "generation_time": 18.5,
                "model_used": "realisticVisionV60B1_v51HyperVAE",
                "is_favorite": True,
                "notes": "Perfect for profile picture"
            }
        }


class GeneratedImageDocument(Document):
    """
    MongoDB Document สำหรับเก็บประวัติภาพที่สร้างด้วย AI
    """
    # Unique ID
    image_id: str = Field(..., description="Unique image ID")
    
    # Reference
    model_id: str = Field(..., description="Character model ID")
    actor_id: Optional[str] = Field(None, description="Actor ID (for filtering character-specific images)")
    
    # Image & Metadata
    metadata: GeneratedImageMetadata = Field(..., description="Complete image metadata")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "generated_images"
        indexes = [
            "image_id",
            "model_id",
            "actor_id",  # NEW: Index for actor-specific queries
            "created_at",
            [("model_id", 1), ("created_at", -1)],  # Compound index for queries
            [("actor_id", 1), ("created_at", -1)],  # NEW: Compound index for actor-specific queries
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "image_id": "img_abc123xyz",
                "model_id": "peace-mind-001",
                "metadata": {
                    "style": "realistic",
                    "seed": 1234567890
                }
            }
        }


# =============================================================================
# BUDDHIST SCRIPTURAL REFERENCES
# =============================================================================

BUDDHIST_REFERENCES = {
    "anguttara_nikaya": {
        "citation": "Aṅguttara Nikāya (AN) 8.40",
        "quote": "Monks, kamma is intention. Having intended, one performs an action through body, speech, or mind. That kamma ripens producing its result in visible form...",
        "relevance": "Establishes that kamma produces visible results in physical form"
    },
    "milindapanha": {
        "citation": "Milindapañha - Questions of King Milinda",
        "quote": "By kamma, beings are beautiful or ugly, high or low, of good or bad complexion...",
        "relevance": "Direct statement that kamma determines physical appearance"
    },
    "visuddhimagga": {
        "citation": "Visuddhimagga IX.123",
        "quote": "Kamma-born materiality produces 9 types of groups... including the eye-decad, ear-decad, nose-decad, tongue-decad, body-decad, femininity-decad, masculinity-decad, heart-base-decad, and life-nonad.",
        "relevance": "Describes kamma-samutthāna rūpa - materiality born from kamma"
    },
    "abhidhamma": {
        "citation": "Abhidhammatthasaṅgaha - Compendium of Abhidhamma",
        "quote": "Rūpa arises from four causes: kamma, citta, utu, and āhāra",
        "relevance": "Establishes kamma as one of four origins of material form"
    }
}
