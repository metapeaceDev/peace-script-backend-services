"""
Actor Classification System - Document Models
Supports Lead/Supporting/Extra actor classification for Digital Actor workflow
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
import uuid

from beanie import Document
from pydantic import BaseModel, Field

# Import new character models (STEP 3 Enhancement)
from models.character_consciousness import Consciousness
from models.character_defilement import Defilement
from models.character_subconscious import Attachment, Taanha
from models.social_status import SocialStatus
from models.character_goals import CharacterGoals
from models.health_history import HealthHistory
from models.character_aspirations import CharacterAspirations


class ActorRoleType(str, Enum):
    """Actor role classification in narrative structure"""
    LEAD = "lead"                    # ตัวละครหลัก (Protagonist/Antagonist)
    SUPPORTING = "supporting"        # ตัวละครสมทบ
    EXTRA = "extra"                  # ตัวประกอบ
    CAMEO = "cameo"                  # รับเชิญ/ปรากฏสั้นๆ


class ActorImportance(str, Enum):
    """Actor importance level in story"""
    CRITICAL = "critical"            # สำคัญสุด (Main story driver)
    HIGH = "high"                    # สำคัญมาก (Key supporter)
    MEDIUM = "medium"                # ปานกลาง (Supporting role)
    LOW = "low"                      # น้อย (Background)


class CharacterArcType(str, Enum):
    """Character development arc pattern"""
    POSITIVE = "positive"            # เปลี่ยนแปลงไปในทางดี
    NEGATIVE = "negative"            # เปลี่ยนแปลงไปในทางเสื่อม
    FLAT = "flat"                    # ไม่มีการเปลี่ยนแปลงมาก
    TRANSFORMATION = "transformation" # การเปลี่ยนแปลงครั้งใหญ่
    COMPLEX = "complex"              # การเปลี่ยนแปลงซับซ้อน


class BudgetTier(str, Enum):
    """Production budget allocation tier"""
    A_TIER = "A"                     # งบสูงสุด (Lead actors)
    B_TIER = "B"                     # งบสูง (Main supporting)
    C_TIER = "C"                     # งบปานกลาง (Supporting)
    D_TIER = "D"                     # งบต่ำ (Extra)


class ActorRelationship(BaseModel):
    """Relationship between actors"""
    actor_id: str = Field(..., description="Target actor ID")
    relationship_type: str = Field(..., description="rival, friend, family, love_interest, mentor, etc.")
    importance: float = Field(default=5.0, ge=0, le=10, description="Relationship importance (0-10)")
    description: Optional[str] = Field(None, description="Relationship description")
    is_primary: bool = Field(default=False, description="Primary relationship flag")
    
    class Config:
        json_schema_extra = {
            "example": {
                "actor_id": "ACT-002",
                "relationship_type": "rival",
                "importance": 8.5,
                "description": "Main antagonist relationship",
                "is_primary": True
            }
        }


class NarrativeFunction(BaseModel):
    """Narrative function/role in story"""
    function_type: str = Field(..., description="mentor, obstacle, love_interest, comic_relief, etc.")
    weight: float = Field(default=5.0, ge=0, le=10, description="Function importance weight")
    description: Optional[str] = None


class InternalCharacter(BaseModel):
    """
    Internal Character Traits (Nama - นาม)
    จิตใจ/บุคลิกภาพภายใน ตามหลักธรรมถือเป็น "นาม" (mental/psychic aggregates)
    Based on psychological and emotional dimensions
    """
    # Core Personality Traits (Big Five + Thai Cultural Dimensions)
    openness: float = Field(default=5.0, ge=0, le=10, description="ความเปิดกว้าง/ความคิดสร้างสรรค์")
    conscientiousness: float = Field(default=5.0, ge=0, le=10, description="ความรับผิดชอบ/มีระเบียบ")
    extraversion: float = Field(default=5.0, ge=0, le=10, description="ความเป็นคนสังคม/พลังงาน")
    agreeableness: float = Field(default=5.0, ge=0, le=10, description="ความเป็นมิตร/ความร่วมมือ")
    neuroticism: float = Field(default=5.0, ge=0, le=10, description="ความวิตกกังวล/อารมณ์แปรปรวน")
    
    # Thai Cultural Values
    kreng_jai: float = Field(default=5.0, ge=0, le=10, description="ความเกรงใจ (Consideration/Deference)")
    bunkhun: float = Field(default=5.0, ge=0, le=10, description="บุญคุณ (Gratitude/Indebtedness)")
    nam_jai: float = Field(default=5.0, ge=0, le=10, description="น้ำใจ (Kindness/Generosity)")
    
    # Motivations & Drives
    primary_motivation: Optional[str] = Field(None, description="แรงจูงใจหลัก (revenge, love, justice, power, etc.)")
    core_values: List[str] = Field(default_factory=list, description="ค่านิยมหลัก [family, honor, freedom, etc.]")
    fears: List[str] = Field(default_factory=list, description="ความกลัวหลัก [failure, betrayal, loss, etc.]")
    desires: List[str] = Field(default_factory=list, description="ความปรารถนา [acceptance, success, love, etc.]")
    
    # Moral Alignment
    moral_alignment: Optional[str] = Field(None, description="Lawful/Neutral/Chaotic + Good/Neutral/Evil")
    ethical_compass: float = Field(default=5.0, ge=0, le=10, description="จริยธรรม (0=amoral, 10=highly ethical)")
    
    # Emotional State
    default_mood: Optional[str] = Field(None, description="อารมณ์ปกติ (optimistic, melancholic, angry, calm, etc.)")
    emotional_stability: float = Field(default=5.0, ge=0, le=10, description="ความมั่นคงทางอารมณ์")
    stress_response: Optional[str] = Field(None, description="ปฏิกิริยาต่อความเครียด (fight, flight, freeze, fawn)")
    
    # Intellectual Traits
    intelligence_type: Optional[str] = Field(None, description="analytical, creative, emotional, practical, etc.")
    wisdom_level: float = Field(default=5.0, ge=0, le=10, description="ความรอบรู้/ภูมิปัญญา")
    decision_making_style: Optional[str] = Field(None, description="rational, emotional, intuitive, impulsive")
    
    # Social Behavior
    communication_style: Optional[str] = Field(None, description="direct, indirect, assertive, passive, etc.")
    conflict_resolution: Optional[str] = Field(None, description="confrontational, avoidant, collaborative, etc.")
    trust_level: float = Field(default=5.0, ge=0, le=10, description="ความไว้วางใจผู้อื่น")
    
    # Growth & Change Potential
    adaptability: float = Field(default=5.0, ge=0, le=10, description="ความสามารถในการปรับตัว")
    learning_capacity: float = Field(default=5.0, ge=0, le=10, description="ความสามารถในการเรียนรู้")
    trauma_influence: Optional[str] = Field(None, description="บาดแผลในอดีตที่มีผลต่อปัจจุบัน")
    redemption_potential: float = Field(default=5.0, ge=0, le=10, description="ศักยภาพในการเปลี่ยนแปลง")
    
    # === NEW: Buddhist Psychology (STEP 3 Enhancement) ===
    consciousness: Optional[Consciousness] = Field(
        default=None,
        description="จิตสำนึก (Consciousness) - mindfulness, wisdom, faith, hiri, karuna, mudita (0-100)"
    )
    defilement: Optional[Defilement] = Field(
        default=None,
        description="กิเลส (Defilement) - 10 กิเลสหลัก (0-100)"
    )
    attachments: List[Attachment] = Field(
        default_factory=list,
        description="ความยึดติด (Attachments) - อุปาทาน"
    )
    taanha: Optional[Taanha] = Field(
        default=None,
        description="ตัณหา (Taanha) - wanting/unwanted desires"
    )


class ExternalCharacter(BaseModel):
    """
    External Character Traits (Rupa - รูป)
    ภายนอก/กายภาพ/การแสดงออก ตามหลักธรรมถือเป็น "รูป" (material/physical aggregates)
    Observable characteristics and behaviors
    """
    # Physical Appearance
    age: Optional[int] = Field(None, ge=0, le=150, description="อายุ (ปี)")
    age_appearance: Optional[str] = Field(default=None, description="ดูอายุ (younger, actual, older than real age)")
    gender: Optional[str] = Field(None, description="เพศ")
    ethnicity: Optional[str] = Field(default=None, description="เชื้อชาติ/สัญชาติ")
    
    height: Optional[float] = Field(None, ge=0, le=300, description="ส่วนสูง (cm)")
    weight: Optional[float] = Field(None, ge=0, le=500, description="น้ำหนัก (kg)")
    body_type: Optional[str] = Field(None, description="รูปร่าง (slim, athletic, heavyset, muscular, etc.)")
    
    # Facial Features
    face_shape: Optional[str] = Field(None, description="รูปหน้า (oval, round, square, heart, etc.)")
    eye_color: Optional[str] = Field(None, description="สีตา")
    hair_color: Optional[str] = Field(None, description="สีผม")
    hair_style: Optional[str] = Field(None, description="ทรงผม (long, short, curly, straight, etc.)")
    skin_tone: Optional[str] = Field(None, description="สีผิว (fair, tan, dark, etc.)")
    
    distinctive_features: List[str] = Field(default_factory=list, description="ลักษณะเด่น [scar, tattoo, birthmark, etc.]")
    
    # Style & Presentation
    fashion_style: Optional[str] = Field(None, description="สไตล์การแต่งกาย (casual, formal, bohemian, punk, etc.)")
    color_palette: List[str] = Field(default_factory=list, description="โทนสีที่ชอบ [black, red, earth tones, etc.]")
    accessories: List[str] = Field(default_factory=list, description="เครื่องประดับ/ของพกพา [watch, ring, bag, etc.]")
    
    # Physical Condition
    fitness_level: float = Field(default=5.0, ge=0, le=10, description="ระดับสมรรถภาพร่างกาย")
    health_status: Optional[str] = Field(None, description="สุขภาพ (healthy, chronic_illness, disability, etc.)")
    scars_wounds: List[str] = Field(default_factory=list, description="แผลเป็น/บาดแผล")
    
    # === Health History (STEP 3 Enhancement - Comprehensive Medical Records) ===
    health_history: Optional[HealthHistory] = Field(
        default=None,
        description="ประวัติสุขภาพครอบคลุม (chronic conditions, injuries, surgeries, medications, allergies, disabilities, mental health, family history, lifestyle) (STEP 3)"
    )
    
    # Movement & Body Language
    posture: Optional[str] = Field(None, description="ท่าทาง (upright, slouched, rigid, relaxed, etc.)")
    gait: Optional[str] = Field(None, description="การเดิน (confident, limping, hurried, graceful, etc.)")
    gestures: List[str] = Field(default_factory=list, description="ท่าทางมือ/การแสดงออก [fidgeting, hand-talking, etc.]")
    
    # Voice & Speech
    voice_tone: Optional[str] = Field(None, description="น้ำเสียง (deep, high-pitched, raspy, smooth, etc.)")
    speech_pattern: Optional[str] = Field(None, description="ลักษณะการพูด (fast, slow, stuttering, eloquent, etc.)")
    accent: Optional[str] = Field(None, description="สำเนียง")
    catchphrase: Optional[str] = Field(None, description="คำพูดเด่น/คำขวัญ")
    
    # Habits & Mannerisms
    nervous_habits: List[str] = Field(default_factory=list, description="กิริยาเมื่อประหม่า [nail-biting, pacing, etc.]")
    signature_gesture: Optional[str] = Field(None, description="ท่าทางเฉพาะตัว")
    quirks: List[str] = Field(default_factory=list, description="พฤติกรรมแปลกๆ ที่เป็นเอกลักษณ์")
    
    # Social Presence
    first_impression: Optional[str] = Field(None, description="ความประทับใจแรกพบ (intimidating, friendly, mysterious, etc.)")
    charisma_level: float = Field(default=5.0, ge=0, le=10, description="เสน่ห์/ความน่าดึงดูด")
    approachability: float = Field(default=5.0, ge=0, le=10, description="ความเข้าถึงง่าย")
    
    # Skills & Abilities (Observable)
    combat_skills: List[str] = Field(default_factory=list, description="ทักษะการต่อสู้ [martial arts, weapons, etc.]")
    artistic_skills: List[str] = Field(default_factory=list, description="ทักษะศิลปะ [painting, music, dance, etc.]")
    practical_skills: List[str] = Field(default_factory=list, description="ทักษะชีวิตจริง [cooking, driving, fixing, etc.]")
    supernatural_abilities: List[str] = Field(default_factory=list, description="ความสามารถพิเศษ (ถ้ามี)")
    
    # Environmental Adaptation
    preferred_environment: Optional[str] = Field(default=None, description="สภาพแวดล้อมที่ชอบ (urban, rural, mountains, sea, etc.)")
    comfort_zone: Optional[str] = Field(default=None, description="พื้นที่ที่สบายใจ (home, crowds, solitude, etc.)")
    
    # === NEW: Enhanced Physical Details (STEP 3 Enhancement) ===
    voice_characteristics: List[str] = Field(
        default_factory=list,
        description="ลักษณะเสียงแบบละเอียด [deep, warm, steady, commanding, etc.] (STEP 3)"
    )
    eye_expression: Optional[str] = Field(
        None,
        description="แววตา/นิสัยจากดวงตา (gentle but determined, sharp, cold, kind, etc.) (STEP 3)"
    )
    smile_type: Optional[str] = Field(
        None,
        description="รอยยิ้ม (warm smile, sarcastic smirk, sad smile, confident grin, etc.) (STEP 3)"
    )
    
    # === NEW: Wardrobe & Style (STEP 3.5 Enhancement) ===
    default_clothing_style: Optional[str] = Field(
        None,
        description="สไตล์การแต่งกายเริ่มต้น (casual, formal, business, sporty, etc.) (STEP 3.5)"
    )
    current_outfit_description: Optional[str] = Field(
        None,
        description="คำอธิบายชุดที่สวมใส่ในปัจจุบัน (STEP 3.5)"
    )
    wardrobe_size: Optional[str] = Field(
        None,
        description="ขนาดตู้เสื้อผ้า (minimal, moderate, extensive, luxury) (STEP 3.5)"
    )
    fashion_preferences: List[str] = Field(
        default_factory=list,
        description="ความชอบด้านแฟชั่น [minimalist, colorful, designer, vintage, etc.] (STEP 3.5)"
    )


class ActorProfile(Document):
    """
    Extended profile for Digital Actor classification
    Links to DigitalMindModel and adds narrative/production metadata
    """
    
    # === Core Identity ===
    actor_id: str = Field(
        default_factory=lambda: f"ACT-{uuid.uuid4().hex[:8].upper()}",
        description="Unique actor identifier"
    )
    model_id: str = Field(..., description="Link to DigitalMindModel")
    actor_name: str = Field(..., description="Actor/Character name")
    
    # === Classification ===
    role_type: ActorRoleType = Field(
        default=ActorRoleType.SUPPORTING,
        description="Actor role classification"
    )
    importance: ActorImportance = Field(
        default=ActorImportance.MEDIUM,
        description="Actor importance level"
    )
    
    # === Narrative Function ===
    narrative_functions: List[str] = Field(
        default_factory=list,
        description="List of narrative functions (mentor, obstacle, etc.)"
    )
    character_arc_type: CharacterArcType = Field(
        default=CharacterArcType.FLAT,
        description="Character development arc pattern"
    )
    arc_description: Optional[str] = Field(
        None,
        description="Detailed character arc description"
    )
    
    # === Screen Presence & Metrics ===
    estimated_screen_time: float = Field(
        default=0.0,
        ge=0,
        description="Estimated screen time in minutes"
    )
    scene_appearances: int = Field(
        default=0,
        ge=0,
        description="Number of scenes character appears in"
    )
    dialogue_lines_count: int = Field(
        default=0,
        ge=0,
        description="Approximate number of dialogue lines"
    )
    
    # === Story Impact ===
    plot_impact_weight: float = Field(
        default=5.0,
        ge=0,
        le=10,
        description="Impact on plot progression (0-10)"
    )
    emotional_arc_trajectory: List[float] = Field(
        default_factory=list,
        description="Emotional journey points [0-10] across story"
    )
    key_scenes: List[str] = Field(
        default_factory=list,
        description="List of key scene IDs for this actor"
    )
    
    # === Relationships ===
    relationships: List[ActorRelationship] = Field(
        default_factory=list,
        description="Relationships with other actors"
    )
    
    # === Character Development (NEW) ===
    internal_character: Optional[InternalCharacter] = Field(
        None,
        description="Internal character traits - จิตใจ/บุคลิกภาพภายใน"
    )
    external_character: Optional[ExternalCharacter] = Field(
        None,
        description="External character traits - ภายนอก/กายภาพ"
    )
    character_bio: Optional[str] = Field(
        None,
        description="Character biography/backstory - ประวัติตัวละคร"
    )
    character_summary: Optional[str] = Field(
        None,
        description="Brief character summary in 2-3 sentences"
    )
    
    # === Avatar Design Data (NEW) ===
    avatar_data: Optional[Dict] = Field(
        None,
        description="Character avatar design data from Character Avatar Designer (JSON format)"
    )
    avatar_thumbnail_url: Optional[str] = Field(
        None,
        description="URL or base64 data for avatar thumbnail image"
    )
    
    # === NEW: STEP 3 Enhancement ===
    social_status: Optional[SocialStatus] = Field(
        None,
        description="Social Status Information - ข้อมูลสถานะทางสังคม (STEP 3.1.1)"
    )
    character_goals: Optional[CharacterGoals] = Field(
        None,
        description="Character Goals - เป้าหมายตัวละคร (STEP 3.2) - objective, need, action, conflict, backstory"
    )
    aspirations: Optional[CharacterAspirations] = Field(
        None,
        description="Character Aspirations - ความปรารถนาตัวละคร (STEP 3.3) - life aspirations, hopes, ambitions, conflicts, evolution"
    )
    sleep_dreams: List[str] = Field(
        default_factory=list,
        description="Sleep Dreams - ฝันตอนหลับ (STEP 3.4) - links to DreamJournal collection (dream_journal_ids)"
    )
    
    # === Production Metadata ===
    casting_priority: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Casting priority (1=lowest, 10=highest)"
    )
    budget_allocation_tier: BudgetTier = Field(
        default=BudgetTier.C_TIER,
        description="Production budget tier"
    )
    
    # === Project Association ===
    project_id: Optional[str] = Field(
        default=None,
        description="Associated project/film ID"
    )
    project_name: Optional[str] = Field(
        None,
        description="Project/film name"
    )
    
    # === Additional Metadata ===
    tags: List[str] = Field(
        default_factory=list,
        description="Searchable tags (hero, villain, comic, etc.)"
    )
    notes: Optional[str] = Field(
        None,
        description="Additional production notes"
    )
    
    # === System Timestamps ===
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    class Settings:
        name = "actor_profiles"
        indexes = [
            "model_id",
            "project_id",
            "role_type",
            "importance",
            "actor_id"
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "actor_id": "ACT-001",
                "model_id": "peace-mind-001",
                "actor_name": "รินรดา (ตัวเอก)",
                "role_type": "lead",
                "importance": "critical",
                "narrative_functions": ["protagonist", "emotional_anchor"],
                "character_arc_type": "transformation",
                "estimated_screen_time": 85.5,
                "scene_appearances": 42,
                "dialogue_lines_count": 156,
                "plot_impact_weight": 9.5,
                "casting_priority": 10,
                "budget_allocation_tier": "A",
                "project_id": "PROJ-001"
            }
        }


class ActorStats(BaseModel):
    """Aggregated statistics for actor analysis"""
    total_actors: int
    by_role_type: Dict[str, int]
    by_importance: Dict[str, int]
    total_screen_time: float
    average_plot_impact: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_actors": 15,
                "by_role_type": {
                    "lead": 2,
                    "supporting": 5,
                    "extra": 8
                },
                "by_importance": {
                    "critical": 2,
                    "high": 3,
                    "medium": 6,
                    "low": 4
                },
                "total_screen_time": 450.5,
                "average_plot_impact": 6.2
            }
        }


class CastBreakdown(BaseModel):
    """Cast breakdown report for project"""
    project_id: str
    project_name: Optional[str] = None
    total_actors: int
    breakdown: Dict[str, List[Dict[str, Any]]]
    stats: ActorStats
    generated_at: datetime = Field(default_factory=datetime.utcnow)
