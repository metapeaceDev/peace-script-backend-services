"""
🌟 Character Aspirations Model (ระบบความปรารถนาตัวละคร)

Complete Aspirations System for Character Development
- Life Aspirations (ความปรารถนาในชีวิต): aspirations, hopes, ambitions, wishes
- Aspiration Types: 15 types covering all aspects
- Aspiration Lifecycle: tracking from creation to achievement
- Buddhist Psychology Integration: Taanha, Attachment, Defilement
- Narrative Integration: Goals, Conflicts, Character Arc

NOTE: This is different from DreamJournal (ฝันตอนหลับ / sleep dreams)
      CharacterAspirations = life goals/wishes (ความปรารถนา)
      DreamJournal = sleep dreams (ฝันตอนหลับ)

Author: Peace Script Model
Date: 6 พฤศจิกายน 2568 (Renamed from CharacterDreams)
"""

from datetime import datetime
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class AspirationType(str, Enum):
    """
    ประเภทความปรารถนา (Aspiration Types)
    
    แบ่งเป็น 3 หมวดหลัก:
    1. Life Aspirations (ความปรารถนาในชีวิต)
    2. Dreams/Nightmares (reference only - actual sleep dreams in DreamJournal)
    3. Other Types (จินตนาการ, ฝันเพ้อฝัน)
    """
    
    # === Life Aspirations (ความปรารถนาในชีวิต) ===
    ASPIRATION = "aspiration"        # ความทะเยอทะยาน - long-term ambition
    AMBITION = "ambition"            # ความใฝ่ฝัน - strong desire for achievement
    HOPE = "hope"                    # ความหวัง - expectation for good outcome
    WISH = "wish"                    # ความปรารถนา - desire for something specific
    GOAL = "goal"                    # เป้าหมาย - specific objective to achieve
    
    # === Sleep Dreams Reference (ใช้ DreamJournal แทน) ===
    NIGHTMARE = "nightmare"          # ฝันร้าย - disturbing dream (use DreamJournal)
    WISHFUL = "wishful"              # ฝันสมหวัง - wish-fulfillment dream
    RECURRING = "recurring"          # ฝันซ้ำ - recurring dream pattern
    LUCID = "lucid"                  # ฝันรู้ตัว - conscious dreaming
    PROPHETIC = "prophetic"          # ฝันเป็นนิมิต - prophetic/precognitive dream
    SYMBOLIC = "symbolic"            # ฝันสัญลักษณ์ - symbolic dream
    
    # === Other Types ===
    FANTASY = "fantasy"              # จินตนาการ - imaginative fantasy
    DAYDREAM = "daydream"            # ฝันกลางวัน - daydreaming
    IMPOSSIBLE = "impossible"        # ฝันเพ้อฝัน - unrealistic aspiration
    SPIRITUAL = "spiritual"          # ปณิธานทางจิตวิญญาณ - spiritual vision


class AspirationTimeline(str, Enum):
    """
    เส้นเวลาความปรารถนา (Aspiration Timeline)
    
    กำหนดระยะเวลาที่ต้องการบรรลุความปรารถนา
    """
    IMMEDIATE = "immediate"         # ทันที - 0-1 เดือน
    SHORT_TERM = "short_term"       # ระยะสั้น - 1-12 เดือน
    MID_TERM = "mid_term"           # ระยะกลาง - 1-5 ปี
    LONG_TERM = "long_term"         # ระยะยาว - 5+ ปี
    LIFETIME = "lifetime"           # ตลอดชีวิต - entire lifetime
    ETERNAL = "eternal"             # นิรันดร์ - beyond this life (Buddhist concept)


class AspirationStatus(str, Enum):
    """
    สถานะความปรารถนา (Aspiration Status)
    
    ติดตามสถานะปัจจุบันของความปรารถนา
    """
    DORMANT = "dormant"             # ยังไม่เริ่ม/หลับใหล - not yet started
    ACTIVE = "active"               # กำลังทำ - actively pursuing
    IN_PROGRESS = "in_progress"     # กำลังดำเนินการ - making progress
    ACHIEVED = "achieved"           # สำเร็จแล้ว - successfully achieved
    ABANDONED = "abandoned"         # ละทิ้งแล้ว - given up
    TRANSFORMED = "transformed"     # เปลี่ยนรูปแล้ว - evolved into something else
    IMPOSSIBLE = "impossible"       # เป็นไปไม่ได้ - realized as impossible
    CONFLICTED = "conflicted"       # ขัดแย้ง - conflicting with other aspirations
    ON_HOLD = "on_hold"             # พักไว้ก่อน - temporarily paused


class AspirationSource(str, Enum):
    """
    แหล่งที่มาของความปรารถนา (Aspiration Source)
    
    ความปรารถนาเกิดจากอะไร - มาจากส่วนไหนของจิตใจ
    """
    
    # === Buddhist Psychology ===
    TAANHA_LOBHA = "taanha_lobha"         # ตัณหาจากโลภะ - craving from greed
    TAANHA_DOSA = "taanha_dosa"           # ตัณหาจากโทสะ - craving from anger
    ATTACHMENT_HOPE = "attachment_hope"   # อุปาทานจากความหวัง - attachment to hope
    ATTACHMENT_LOVE = "attachment_love"   # อุปาทานจากความรัก - attachment to love
    ATTACHMENT_DUTY = "attachment_duty"   # อุปาทานจากหน้าที่ - attachment to duty
    CONSCIOUSNESS = "consciousness"        # จิตสำนึก - conscious awareness
    DEFILEMENT = "defilement"             # กิเลส - mental defilement
    
    # === Character Psychology ===
    DESIRE = "desire"                     # ความปรารถนา - basic desire
    FEAR = "fear"                         # ความกลัว - fear-based aspiration
    TRAUMA = "trauma"                     # บาดแผลใจ - from past trauma
    AMBITION = "ambition"                 # ความทะเยอทะยาน - personal ambition
    MOTIVATION = "motivation"             # แรงจูงใจ - motivation
    
    # === External Sources ===
    SOCIAL_PRESSURE = "social_pressure"   # แรงกดดันสังคม - societal expectation
    FAMILY = "family"                     # ครอบครัว - family influence
    CULTURE = "culture"                   # วัฒนธรรม - cultural norm
    RELIGION = "religion"                 # ศาสนา - religious teaching
    KARMA = "karma"                       # กรรม - karmic influence
    
    # === Other ===
    INNATE = "innate"                     # ติดตัวมา - innate tendency
    LEARNED = "learned"                   # เรียนรู้มา - learned behavior
    UNKNOWN = "unknown"                   # ไม่ทราบที่มา - unknown origin


class LifeAspiration(BaseModel):
    """
    ความปรารถนาในชีวิต (Life Aspiration)
    
    ความปรารถนา ความหวัง ความใฝ่ฝัน ที่ตัวละครต้องการบรรลุในชีวิต
    ไม่ใช่ความฝันตอนหลับ (sleep dreams) แต่เป็นเป้าหมายชีวิต (life goals)
    
    Examples:
    - "อยากเห็นลูกสำเร็จในชีวิต"
    - "อยากร่ำรวย มีเงินเก็บ"
    - "อยากเป็นแชมป์มวยโลก"
    - "อยากสอนมวยให้คนรุ่นหลัง"
    """
    
    aspiration_id: str = Field(
        default_factory=lambda: f"ASP-{uuid.uuid4().hex[:8].upper()}",
        description="รหัสความปรารถนา (unique identifier)"
    )
    
    type: AspirationType = Field(
        ...,
        description="ประเภทความปรารถนา (aspiration, hope, ambition, wish, goal, etc.)"
    )
    
    description: str = Field(
        ...,
        description="รายละเอียดความปรารถนา - อธิบายอย่างละเอียด"
    )
    
    intensity: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="ความรุนแรง/ความต้องการ (0-100) - แรงแค่ไหน"
    )
    
    timeline: AspirationTimeline = Field(
        default=AspirationTimeline.LONG_TERM,
        description="เส้นเวลาที่ต้องการบรรลุ (immediate, short_term, mid_term, long_term, lifetime, eternal)"
    )
    
    status: AspirationStatus = Field(
        default=AspirationStatus.ACTIVE,
        description="สถานะปัจจุบัน (active, achieved, abandoned, etc.)"
    )
    
    source: AspirationSource = Field(
        default=AspirationSource.DESIRE,
        description="แหล่งที่มา (taanha, attachment, desire, fear, etc.)"
    )
    
    priority: int = Field(
        default=5,
        ge=1,
        le=10,
        description="ลำดับความสำคัญ (1-10, 10 = สูงสุด)"
    )
    
    related_to: List[str] = Field(
        default_factory=list,
        description="เกี่ยวข้องกับ (character_id, goal_id, event_id, etc.)"
    )
    
    obstacles: List[str] = Field(
        default_factory=list,
        description="อุปสรรค/สิ่งที่ขัดขวาง - what prevents achievement"
    )
    
    progress: float = Field(
        default=0.0,
        ge=0,
        le=100,
        description="ความคืบหน้า (0-100%) - how much achieved so far"
    )
    
    created_date: Optional[str] = Field(
        None,
        description="วันที่เกิดความปรารถนา (YYYY-MM-DD or datetime)"
    )
    
    achieved_date: Optional[str] = Field(
        None,
        description="วันที่บรรลุ (YYYY-MM-DD or datetime)"
    )
    
    abandoned_date: Optional[str] = Field(
        None,
        description="วันที่ละทิ้ง (YYYY-MM-DD or datetime)"
    )
    
    notes: Optional[str] = Field(
        None,
        description="บันทึกเพิ่มเติม - additional notes"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "aspiration_id": "ASP-A1B2C3D4",
                "type": "hope",
                "description": "อยากเห็นลูกสำเร็จในชีวิต มีงานดี มีครอบครัวที่อบอุ่น",
                "intensity": 95.0,
                "timeline": "lifetime",
                "status": "active",
                "source": "attachment_love",
                "priority": 10,
                "related_to": ["child_character_id"],
                "obstacles": ["heart_disease", "financial_problems", "social_inequality"],
                "progress": 30.0,
                "created_date": "2010-01-01",
                "notes": "ความปรารถนาหลักในชีวิต ยอมเสียสละทุกอย่างเพื่อลูก"
            }
        }


class AspirationConflict(BaseModel):
    """
    ความขัดแย้งของความปรารถนา (Aspiration Conflict)
    
    เมื่อความปรารถนาหนึ่งขัดกับความปรารถนาอื่น หรือขัดกับความเป็นจริง
    
    Types:
    - internal: ขัดแย้งภายใน (2 ความปรารถนาขัดกัน)
    - external: ขัดกับความเป็นจริง
    - temporal: ขัดกันเรื่องเวลา (ทำ 2 อย่างพร้อมกันไม่ได้)
    - resource: ขัดกันเรื่องทรัพยากร (เงิน, เวลา, พลังงาน)
    """
    
    aspiration_a_id: str = Field(..., description="ความปรารถนาที่ 1 (aspiration_id)")
    aspiration_b_id: str = Field(..., description="ความปรารถนาที่ 2 (aspiration_id or 'reality')")
    
    conflict_type: str = Field(
        ...,
        description="ประเภทความขัดแย้ง: internal, external, temporal, resource"
    )
    
    description: str = Field(
        ...,
        description="รายละเอียดความขัดแย้ง - what is the conflict"
    )
    
    severity: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="ความรุนแรงของความขัดแย้ง (0-100)"
    )
    
    resolution_strategy: Optional[str] = Field(
        None,
        description="กลยุทธ์แก้ปัญหา: compromise, sacrifice, delay, transform, acceptance"
    )
    
    resolution_description: Optional[str] = Field(
        None,
        description="รายละเอียดการแก้ปัญหา"
    )
    
    is_resolved: bool = Field(
        default=False,
        description="แก้ปัญหาแล้วหรือยัง"
    )
    
    notes: Optional[str] = Field(
        None,
        description="บันทึกเพิ่มเติม"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "aspiration_a_id": "ASP-TEACH-MUAY",
                "aspiration_b_id": "ASP-CHILD-NOT-FIGHTER",
                "conflict_type": "internal",
                "description": "อยากสอนมวย แต่ไม่อยากให้ลูกเป็นมวย (ภูมิใจในมวย vs กลัวลูกลำบาก)",
                "severity": 70.0,
                "resolution_strategy": "compromise",
                "resolution_description": "สอนมวยเป็นวิชา แต่ไม่บังคับให้เป็นอาชีพ",
                "is_resolved": True,
                "notes": "ได้ข้อสรุปแล้ว ให้ลูกเลือกเองว่าจะเป็นอะไร"
            }
        }


class CharacterAspirations(BaseModel):
    """
    Character Aspirations System (ระบบความปรารถนาตัวละคร)
    
    รวมความปรารถนาทั้งหมดของตัวละคร
    
    IMPORTANT DISTINCTION:
    - CharacterAspirations = Life goals/wishes (ความปรารถนาในชีวิต) - THIS CLASS
    - DreamJournal = Sleep dreams (ฝันตอนหลับ) - SEPARATE SYSTEM
    
    Integration Points:
    - CharacterGoals.need → life_aspirations (ความต้องการ → ความปรารถนา)
    - Taanha.wanting → life_aspirations (ตัณหา → ความปรารถนา)
    - Attachment (hope) → life_aspirations (อุปาทาน → ความปรารถนา)
    - InternalCharacter.fears → nightmare themes (ความกลัว → referenced in DreamJournal)
    - DreamJournal → sleep dreams (ความฝันตอนหลับ - separate collection)
    
    Based on: Character Dreams Comprehensive Analysis (6 Nov 2568)
    Renamed: CharacterDreams → CharacterAspirations (6 Nov 2568)
    """
    
    # === Life Aspirations (ความปรารถนาในชีวิต) ===
    life_aspirations: List[LifeAspiration] = Field(
        default_factory=list,
        description="""
        ความปรารถนาในชีวิต (aspirations, hopes, ambitions, wishes, goals)
        
        ไม่ใช่ความฝันตอนหลับ แต่เป็นเป้าหมายชีวิต สิ่งที่อยากให้เกิดขึ้น
        
        Examples:
        - "อยากเห็นลูกสำเร็จ"
        - "อยากร่ำรวย"
        - "อยากสอนมวยให้คนรุ่นหลัง"
        """
    )
    
    # === Sleep Dreams Integration (ฝันตอนหลับ) ===
    dream_journal_ids: List[str] = Field(
        default_factory=list,
        description="""
        ลิงก์ไปยัง DreamJournal documents (ความฝันตอนหลับ)
        
        เชื่อมโยงกับ DreamJournal collection ที่เก็บฝันตอนหลับ
        ซึ่งแยกออกจากความปรารถนาในชีวิต (life aspirations)
        """
    )
    
    recurring_themes: List[str] = Field(
        default_factory=list,
        description="""
        ธีมที่เกิดซ้ำในความฝันตอนหลับ (recurring dream patterns)
        
        Reference จาก DreamJournal - ความฝันที่เกิดซ้ำบ่อยๆ 
        มักบ่งบอกถึงปัญหาที่ยังไม่ได้แก้ หรือความกลัวที่ฝังลึก
        
        Examples:
        - "ฝันว่าลูกล้มเหลว"
        - "ฝันว่าไม่มีเงินรักษาตัว"
        - "ฝันว่าหมดแรงช่วยเหลือไม่ได้"
        """
    )
    
    nightmare_sources: List[str] = Field(
        default_factory=list,
        description="""
        แหล่งที่มาของฝันร้าย (nightmare sources from DreamJournal)
        
        มักมาจาก fears ใน InternalCharacter
        
        Examples:
        - "child_failure" → ฝันว่าลูกล้มเหลว
        - "financial_ruin" → ฝันว่าหมดตัว
        - "death" → ฝันว่าตาย
        """
    )
    
    # === Aspiration Conflicts ===
    aspiration_conflicts: List[AspirationConflict] = Field(
        default_factory=list,
        description="ความขัดแย้งระหว่างความปรารถนา (aspirations that conflict with each other)"
    )
    
    # === Tracking & Statistics ===
    total_aspirations_achieved: int = Field(
        default=0,
        description="จำนวนความปรารถนาที่บรรลุแล้ว (achieved count)"
    )
    
    total_aspirations_abandoned: int = Field(
        default=0,
        description="จำนวนความปรารถนาที่ละทิ้งแล้ว (abandoned count)"
    )
    
    total_aspirations_transformed: int = Field(
        default=0,
        description="จำนวนความปรารถนาที่เปลี่ยนรูปแล้ว (transformed count)"
    )
    
    # === Evolution & History ===
    aspiration_evolution: Optional[str] = Field(
        None,
        description="""
        การเปลี่ยนแปลงของความปรารถนาตามเวลา (aspiration evolution over time)
        
        ความปรารถนาเปลี่ยนไปตามช่วงวัย ประสบการณ์ เหตุการณ์
        
        Example:
        "วัยหนุ่ม: ปรารถนาเป็นแชมป์มวย
         วัยกลางคน: ปรารถนาสอนมวย
         วัยปลาย: ปรารถนาเห็นลูกสำเร็จ"
        """
    )
    
    achievement_history: List[dict] = Field(
        default_factory=list,
        description="""
        ประวัติความปรารถนาที่บรรลุแล้ว (achievement history)
        
        [{"aspiration_id": "...", "achieved_date": "...", "description": "..."}]
        """
    )
    
    # === Meta Information ===
    notes: Optional[str] = Field(
        None,
        description="บันทึกเพิ่มเติมเกี่ยวกับความปรารถนา"
    )
    
    last_updated: Optional[str] = Field(
        None,
        description="วันที่อัพเดทครั้งล่าสุด (YYYY-MM-DD or datetime)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "life_aspirations": [
                    {
                        "aspiration_id": "ASP-CHILD-SUCCESS",
                        "type": "hope",
                        "description": "อยากเห็นลูกสำเร็จในชีวิต มีงานดี มีครอบครัวที่อบอุ่น",
                        "intensity": 95.0,
                        "timeline": "lifetime",
                        "status": "active",
                        "source": "attachment_love",
                        "priority": 10,
                        "related_to": ["koi_character_id"],
                        "obstacles": ["heart_disease", "financial_problems"],
                        "progress": 30.0
                    }
                ],
                "recurring_themes": [
                    "ฝันว่าลูกล้มเหลว",
                    "ฝันว่าไม่มีเงินรักษาตัว"
                ],
                "nightmare_sources": ["child_failure", "financial_ruin"],
                "aspiration_conflicts": [
                    {
                        "aspiration_a_id": "ASP-TEACH-MUAY",
                        "aspiration_b_id": "ASP-CHILD-NOT-FIGHTER",
                        "conflict_type": "internal",
                        "description": "อยากสอนมวย แต่ไม่อยากให้ลูกเป็นมวย",
                        "severity": 70.0
                    }
                ],
                "total_aspirations_achieved": 2,
                "total_aspirations_abandoned": 1,
                "aspiration_evolution": "วัยหนุ่ม: ปรารถนาเป็นแชมป์มวย → วัยปลาย: ปรารถนาเห็นลูกสำเร็จ"
            }
        }
    
    # === Helper Methods ===
    
    def get_active_aspirations(self) -> List[LifeAspiration]:
        """Get all active life aspirations"""
        return [a for a in self.life_aspirations if a.status == AspirationStatus.ACTIVE]
    
    def get_high_priority_aspirations(self, min_priority: int = 8) -> List[LifeAspiration]:
        """Get high priority aspirations (priority >= min_priority)"""
        return [a for a in self.life_aspirations if a.priority >= min_priority]
    
    def get_aspirations_by_timeline(self, timeline: AspirationTimeline) -> List[LifeAspiration]:
        """Get aspirations by specific timeline"""
        return [a for a in self.life_aspirations if a.timeline == timeline]
    
    def get_aspirations_by_source(self, source: AspirationSource) -> List[LifeAspiration]:
        """Get aspirations from specific source"""
        return [a for a in self.life_aspirations if a.source == source]
    
    def get_aspirations_by_type(self, aspiration_type: AspirationType) -> List[LifeAspiration]:
        """Get aspirations of specific type"""
        return [a for a in self.life_aspirations if a.type == aspiration_type]
    
    def calculate_achievement_rate(self) -> float:
        """
        Calculate percentage of achieved aspirations
        
        Returns:
            float: Achievement rate (0-100%)
        """
        total = len(self.life_aspirations)
        if total == 0:
            return 0.0
        return (self.total_aspirations_achieved / total) * 100
    
    def calculate_average_progress(self) -> float:
        """
        Calculate average progress across all active aspirations
        
        Returns:
            float: Average progress (0-100%)
        """
        active = self.get_active_aspirations()
        if not active:
            return 0.0
        return sum(a.progress for a in active) / len(active)
    
    def get_most_important_aspiration(self) -> Optional[LifeAspiration]:
        """
        Get the aspiration with highest priority
        
        Returns:
            LifeAspiration or None
        """
        active = self.get_active_aspirations()
        if not active:
            return None
        return max(active, key=lambda a: a.priority)
    
    def get_conflicted_aspirations(self) -> List[LifeAspiration]:
        """Get all aspirations with conflicted status"""
        return [a for a in self.life_aspirations if a.status == AspirationStatus.CONFLICTED]
    
    def get_unresolved_conflicts(self) -> List[AspirationConflict]:
        """Get all conflicts that haven't been resolved"""
        return [c for c in self.aspiration_conflicts if not c.is_resolved]
    
    def get_aspirations_summary(self) -> dict:
        """
        Get summary statistics of aspirations
        
        Returns:
            dict: Summary with counts and percentages
        """
        total = len(self.life_aspirations)
        active = len(self.get_active_aspirations())
        
        return {
            "total_aspirations": total,
            "active_aspirations": active,
            "achieved_aspirations": self.total_aspirations_achieved,
            "abandoned_aspirations": self.total_aspirations_abandoned,
            "transformed_aspirations": self.total_aspirations_transformed,
            "achievement_rate": self.calculate_achievement_rate(),
            "average_progress": self.calculate_average_progress(),
            "total_conflicts": len(self.aspiration_conflicts),
            "unresolved_conflicts": len(self.get_unresolved_conflicts()),
            "recurring_nightmares": len(self.recurring_themes)
        }


# === Example: Koi's Father (Wichan Mahaphrom) ===
EXAMPLE_KOIS_FATHER_ASPIRATIONS = CharacterAspirations(
    life_aspirations=[
        LifeAspiration(
            aspiration_id="ASP-CHILD-SUCCESS",
            type=AspirationType.HOPE,
            description="อยากเห็นลูกสำเร็จในชีวิต มีงานดี มีครอบครัวที่อบอุ่น",
            intensity=95.0,
            timeline=AspirationTimeline.LIFETIME,
            status=AspirationStatus.ACTIVE,
            source=AspirationSource.ATTACHMENT_LOVE,
            priority=10,
            related_to=["koi_character_id"],
            obstacles=["heart_disease", "financial_problems", "social_inequality"],
            progress=30.0,
            created_date="2010-01-01",
            notes="ความปรารถนาหลักในชีวิต ยอมเสียสละทุกอย่างเพื่อลูก"
        ),
        LifeAspiration(
            aspiration_id="ASP-HEALTH-RECOVERY",
            type=AspirationType.WISH,
            description="อยากหายจากโรคหัวใจ กลับมาแข็งแรงเหมือนเดิม",
            intensity=85.0,
            timeline=AspirationTimeline.SHORT_TERM,
            status=AspirationStatus.CONFLICTED,
            source=AspirationSource.DESIRE,
            priority=9,
            obstacles=["chronic_heart_disease", "expensive_treatment", "age_factor"],
            progress=15.0,
            created_date="2015-02-01",
            notes="รู้ว่าเป็นไปไม่ได้ แต่ก็ยังหวัง"
        )
    ],
    recurring_themes=[
        "ฝันว่าลูกล้มเหลว",
        "ฝันว่าไม่มีเงินรักษาตัว",
        "ฝันว่าหมดแรงช่วยเหลือไม่ได้"
    ],
    nightmare_sources=["child_failure", "financial_ruin", "death"],
    aspiration_conflicts=[
        AspirationConflict(
            aspiration_a_id="ASP-TEACH-MUAY",
            aspiration_b_id="ASP-CHILD-NOT-FIGHTER",
            conflict_type="internal",
            description="อยากสอนมวย แต่ไม่อยากให้ลูกเป็นมวย (ภูมิใจในมวย vs กลัวลูกลำบาก)",
            severity=70.0,
            resolution_strategy="compromise",
            resolution_description="สอนมวยเป็นวิชา แต่ไม่บังคับให้เป็นอาชีพ",
            is_resolved=True
        )
    ],
    total_aspirations_achieved=2,
    total_aspirations_abandoned=1,
    aspiration_evolution="""
    วัยหนุ่ม (20-30): ปรารถนาเป็นแชมป์มวย ร่ำรวย มีชื่อเสียง
    วัยกลางคน (30-45): ปรารถนาสอนมวย สืบทอดศิลปะ มีครอบครัวที่ดี
    วัยปลาย (45+): ปรารถนาเห็นลูกสำเร็จ หายจากโรค ครอบครัวมีความสุข
    
    การเปลี่ยนแปลง: จากความปรารถนาเกี่ยวกับตัวเอง → ความปรารถนาเกี่ยวกับลูก
    """,
    notes="ความปรารถนาเปลี่ยนไปตามช่วงวัย จากปรารถนาเพื่อตัวเอง เป็นปรารถนาเพื่อลูก"
)
