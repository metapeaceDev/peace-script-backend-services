"""
👁️ Sensory Input Processor - ระบบประมวลผล Input จากทวาร 6
===========================================================

ประมวลผล input จากประสาทสัมผัส 6 ทวาร พร้อมวิเคราะห์และจัดประเภทอารมณ์

## ทวาร 6 ประการ (Dvāra - Sense Doors):

1. **จักขุทวาร** (Cakkhu-dvāra) - Eye Door
   - อารมณ์: รูป (Rūpa - Visible Form)
   - ตัวอย่าง: สี, รูปร่าง, ความสว่าง

2. **โสตทวาร** (Sota-dvāra) - Ear Door
   - อารมณ์: เสียง (Sadda - Sound)
   - ตัวอย่าง: ดนตรี, เสียงคน, เสียงธรรมชาติ

3. **ฆานทวาร** (Ghāna-dvāra) - Nose Door
   - อารมณ์: กลิ่น (Gandha - Smell)
   - ตัวอย่าง: กลิ่นหอม, กลิ่นเหม็น, กลิ่นกลาง

4. **ชิวหาทวาร** (Jivhā-dvāra) - Tongue Door
   - อารมณ์: รส (Rasa - Taste)
   - ตัวอย่าง: หวาน, เค็ม, เปรี้ยว, ขม, เผ็ด, จืด

5. **กายทวาร** (Kāya-dvāra) - Body Door
   - อารมณ์: โผฏฐัพพะ (Phoṭṭhabba - Touch)
   - ตัวอย่าง: อ่อน, แข็ง, ร้อน, เย็น, ปวด, สบาย

6. **มโนทวาร** (Mano-dvāra) - Mind Door
   - อารมณ์: ธรรมารมณ์ (Dhammārammaṇa - Mental Object)
   - ตัวอย่าง: ความคิด, ความทรงจำ, จินตนาการ

## Buddhist Scriptural References:
- Dhammasaṅgaṇī (ธัมมสังคณี)
- Vibhaṅga (วิภังค์)
- Abhidhammatthasaṅgaha (อภิธัมมัตถสังคหะ)

Created: October 2025
Version: 3.0
"""

from typing import Dict, List, Optional, Literal, Tuple
from enum import Enum
from pydantic import BaseModel, Field, validator
from datetime import datetime


# =============================================================================
# ENUMS & TYPES (Re-use from citta_vithi_engine)
# =============================================================================

class DvaraType(str, Enum):
    """ทวาร - ประตูรับรู้ 6 ทาง"""
    CAKKHU = "eye"          # จักขุ (ตา)
    SOTA = "ear"            # โสตะ (หู)
    GHANA = "nose"          # ฆานะ (จมูก)
    JIVHA = "tongue"        # ชิวหา (ลิ้น)
    KAYA = "body"           # กายะ (กาย)
    MANO = "mind"           # มโน (ใจ)


class AramanaType(str, Enum):
    """อารมณ์ - วัตถุที่กระทบ"""
    RUPA = "visible_form"       # รูป (ที่ตาเห็น)
    SADDA = "sound"             # เสียง (ที่หูได้ยิน)
    GANDHA = "smell"            # กลิ่น (ที่จมูกดม)
    RASA = "taste"              # รส (ที่ลิ้นลิ้ม)
    PHOTTHABBA = "touch"        # สัมผัส (ที่กายต้อง)
    DHAMMĀRAMMAṆA = "mental"    # ธรรมารมณ์ (ที่ใจคิด)


class VedanaType(str, Enum):
    """เวทนา - ความรู้สึก 3 แบบ"""
    SUKHA = "pleasant"      # สุข
    DUKKHA = "unpleasant"   # ทุกข์
    UPEKKHA = "neutral"     # อุเบกขา


class AramanaQuality(str, Enum):
    """คุณภาพของอารมณ์"""
    ATTRACTIVE = "attractive"       # น่ารัก (iṭṭha)
    REPULSIVE = "repulsive"         # ไม่น่ารัก (aniṭṭha)
    NEUTRAL = "neutral"             # กลางๆ (majjhatta)
    BEAUTIFUL = "beautiful"         # สวยงาม
    UGLY = "ugly"                   # น่าเกลียด
    PLEASANT_SOUND = "pleasant_sound"
    UNPLEASANT_SOUND = "unpleasant_sound"
    FRAGRANT = "fragrant"           # หอม
    FOUL = "foul"                   # เหม็น
    DELICIOUS = "delicious"         # อร่อย
    DISGUSTING = "disgusting"       # น่าขยะแขยง
    SOFT = "soft"                   # นุ่ม
    ROUGH = "rough"                 # หยาบ
    PAINFUL = "painful"             # เจ็บปวด
    COMFORTABLE = "comfortable"     # สบาย


class InputContext(str, Enum):
    """บริบทของ input"""
    DAILY_LIFE = "daily_life"
    MEDITATION = "meditation"
    CONFLICT = "conflict"
    TEMPTATION = "temptation"
    SOCIAL = "social"
    SOLITUDE = "solitude"
    WORK = "work"
    LEISURE = "leisure"
    RELIGIOUS = "religious"


# =============================================================================
# DATA MODELS
# =============================================================================

class RawSensoryInput(BaseModel):
    """Input ดิบจากภายนอก (ก่อนประมวลผล)"""
    description: str = Field(..., description="รายละเอียด input")
    source: Optional[str] = Field(None, description="แหล่งที่มา")
    context: InputContext = Field(default=InputContext.DAILY_LIFE, description="บริบท")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "description": "เห็นดอกไม้สวยบนโต๊ะ",
                "source": "visual_environment",
                "context": "daily_life"
            }
        }


class ProcessedSensoryInput(BaseModel):
    """Input ที่ประมวลผลแล้ว พร้อมส่งเข้า Citta Vithi"""
    # Basic info
    dvara: DvaraType = Field(..., description="ทวารที่รับรู้")
    aramana_type: AramanaType = Field(..., description="ประเภทของอารมณ์")
    aramana_description: str = Field(..., description="รายละเอียดอารมณ์")
    
    # Characteristics
    quality: AramanaQuality = Field(..., description="คุณภาพของอารมณ์")
    intensity: float = Field(default=5.0, ge=0, le=10, description="ความแรง")
    natural_vedana: VedanaType = Field(..., description="เวทนาตามธรรมชาติของอารมณ์")
    
    # Context
    context: InputContext = Field(default=InputContext.DAILY_LIFE)
    trigger_factors: List[str] = Field(default_factory=list, description="ปัจจัยกระตุ้น")
    
    # Processing metadata
    raw_input: Optional[str] = Field(None, description="Input ดิบ")
    processing_notes: str = Field(default="", description="หมายเหตุการประมวลผล")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "dvara": "eye",
                "aramana_type": "visible_form",
                "aramana_description": "ดอกไม้สวยสีชมพู",
                "quality": "beautiful",
                "intensity": 7.5,
                "natural_vedana": "pleasant",
                "context": "daily_life",
                "trigger_factors": ["visual_beauty", "natural_object"],
                "processing_notes": "Classified as beautiful visible form"
            }
        }


class InputValidationResult(BaseModel):
    """ผลการตรวจสอบ input"""
    is_valid: bool = Field(..., description="ถูกต้องหรือไม่")
    errors: List[str] = Field(default_factory=list, description="รายการ error")
    warnings: List[str] = Field(default_factory=list, description="รายการ warning")
    suggestions: List[str] = Field(default_factory=list, description="คำแนะนำ")


class InputClassification(BaseModel):
    """การจัดประเภท input"""
    primary_category: str = Field(..., description="หมวดหมู่หลัก")
    sub_categories: List[str] = Field(default_factory=list, description="หมวดหมู่ย่อย")
    buddhist_analysis: Dict = Field(default_factory=dict, description="วิเคราะห์ตามพุทธศาสตร์")
    potential_reactions: List[str] = Field(default_factory=list, description="ปฏิกิริยาที่อาจเกิด")


# =============================================================================
# SENSORY INPUT PROCESSOR
# =============================================================================

class SensoryInputProcessor:
    """
    👁️ Sensory Input Processor
    
    ประมวลผล input จากทวาร 6 → วิเคราะห์ → จัดประเภท → เตรียมส่งเข้า Citta Vithi
    
    Features:
    - Auto-detect sense door from description
    - Classify aramana quality (attractive/repulsive/neutral)
    - Determine natural vedana (pleasant/unpleasant/neutral)
    - Add Buddhist analysis
    - Validate input
    """
    
    def __init__(self):
        self.name = "Sensory Input Processor v3.0"
        
        # Keywords for auto-detection
        self.eye_keywords = ["เห็น", "มอง", "ดู", "สี", "สว", "ง่าม", "สว่าง", "มืด", "วิว", "ภาพ", "รูป"]
        self.ear_keywords = ["ได้ยิน", "ฟัง", "เสียง", "ดัง", "เงียบ", "ดนตรี", "เพลง", "พูด", "ตะโกน"]
        self.nose_keywords = ["ดม", "กลิ่น", "หอม", "เหม็น", "สูด"]
        self.tongue_keywords = ["ลิ้ม", "ชิม", "รส", "หวาน", "เค็ม", "เปรี้ยว", "ขม", "เผ็ด", "จืด", "อร่อย"]
        self.body_keywords = ["สัมผัส", "แตะ", "จับ", "นุ่ม", "แข็ง", "ร้อน", "เย็น", "ปวด", "เจ็บ", "สบาย", "นวด"]
        self.mind_keywords = ["คิด", "ระลึก", "จำ", "จินตนาการ", "ฝัน", "ครุ่นคิด", "ความทรงจำ", "ความคิด"]
        
        # Quality keywords
        self.attractive_keywords = ["สวย", "สวยงาม", "ดี", "น่ารัก", "สวยเลิศ", "งดงาม", "วิเศษ"]
        self.repulsive_keywords = ["น่าเกลียด", "แย่", "น่ารังเกียจ", "น่าขยะแขยง", "เลวร้าย"]
        self.beautiful_keywords = ["สวย", "งาม", "สวยงาม", "งดงาม"]
        self.ugly_keywords = ["น่าเกลียด", "อัปลักษณ์", "น่ารังเกียจ"]
        
    def process(self, raw_input: RawSensoryInput) -> ProcessedSensoryInput:
        """
        ประมวลผล raw input → processed input
        
        Args:
            raw_input: Input ดิบจากภายนอก
            
        Returns:
            ProcessedSensoryInput: Input ที่ประมวลผลแล้ว
        """
        description = raw_input.description.lower()
        
        # 1. Detect sense door
        dvara = self._detect_dvara(description)
        
        # 2. Map to aramana type
        aramana_type = self._map_aramana_type(dvara)
        
        # 3. Classify quality
        quality = self._classify_quality(description, dvara)
        
        # 4. Determine vedana
        vedana = self._determine_vedana(quality, description)
        
        # 5. Calculate intensity
        intensity = self._calculate_intensity(description, quality)
        
        # 6. Extract trigger factors
        trigger_factors = self._extract_trigger_factors(description, dvara, quality)
        
        # 7. Generate processing notes
        notes = self._generate_processing_notes(dvara, quality, vedana)
        
        return ProcessedSensoryInput(
            dvara=dvara,
            aramana_type=aramana_type,
            aramana_description=raw_input.description,
            quality=quality,
            intensity=intensity,
            natural_vedana=vedana,
            context=raw_input.context,
            trigger_factors=trigger_factors,
            raw_input=raw_input.description,
            processing_notes=notes,
            timestamp=raw_input.timestamp
        )
    
    def _detect_dvara(self, description: str) -> DvaraType:
        """ตรวจจับทวารจากคำอธิบาย"""
        # Count keyword matches
        scores = {
            DvaraType.CAKKHU: sum(1 for kw in self.eye_keywords if kw in description),
            DvaraType.SOTA: sum(1 for kw in self.ear_keywords if kw in description),
            DvaraType.GHANA: sum(1 for kw in self.nose_keywords if kw in description),
            DvaraType.JIVHA: sum(1 for kw in self.tongue_keywords if kw in description),
            DvaraType.KAYA: sum(1 for kw in self.body_keywords if kw in description),
            DvaraType.MANO: sum(1 for kw in self.mind_keywords if kw in description),
        }
        
        # Get highest score
        max_score = max(scores.values())
        if max_score == 0:
            # Default to eye if no match
            return DvaraType.CAKKHU
        
        # Return dvara with highest score
        for dvara, score in scores.items():
            if score == max_score:
                return dvara
        
        return DvaraType.CAKKHU  # fallback
    
    def _map_aramana_type(self, dvara: DvaraType) -> AramanaType:
        """แปลงทวาร → ประเภทอารมณ์"""
        mapping = {
            DvaraType.CAKKHU: AramanaType.RUPA,
            DvaraType.SOTA: AramanaType.SADDA,
            DvaraType.GHANA: AramanaType.GANDHA,
            DvaraType.JIVHA: AramanaType.RASA,
            DvaraType.KAYA: AramanaType.PHOTTHABBA,
            DvaraType.MANO: AramanaType.DHAMMĀRAMMAṆA,
        }
        return mapping[dvara]
    
    def _classify_quality(self, description: str, dvara: DvaraType) -> AramanaQuality:
        """จัดประเภทคุณภาพของอารมณ์"""
        
        # Eye door
        if dvara == DvaraType.CAKKHU:
            if any(kw in description for kw in self.beautiful_keywords):
                return AramanaQuality.BEAUTIFUL
            elif any(kw in description for kw in self.ugly_keywords):
                return AramanaQuality.UGLY
            elif any(kw in description for kw in self.attractive_keywords):
                return AramanaQuality.ATTRACTIVE
            elif any(kw in description for kw in self.repulsive_keywords):
                return AramanaQuality.REPULSIVE
            else:
                return AramanaQuality.NEUTRAL
        
        # Ear door
        elif dvara == DvaraType.SOTA:
            if any(kw in description for kw in ["ไพเราะ", "เพราะ", "ชัดเจน"]):
                return AramanaQuality.PLEASANT_SOUND
            elif any(kw in description for kw in ["แหลม", "ดัง", "รำคาญ", "หยาบคาย"]):
                return AramanaQuality.UNPLEASANT_SOUND
            else:
                return AramanaQuality.NEUTRAL
        
        # Nose door
        elif dvara == DvaraType.GHANA:
            if any(kw in description for kw in ["หอม", "กลิ่นดี"]):
                return AramanaQuality.FRAGRANT
            elif any(kw in description for kw in ["เหม็น", "กลิ่นเน่า", "กลิ่นไม่ดี"]):
                return AramanaQuality.FOUL
            else:
                return AramanaQuality.NEUTRAL
        
        # Tongue door
        elif dvara == DvaraType.JIVHA:
            if any(kw in description for kw in ["อร่อย", "รสชาติดี", "หวาน"]):
                return AramanaQuality.DELICIOUS
            elif any(kw in description for kw in ["เน่า", "เสีย", "รสชาติแย่"]):
                return AramanaQuality.DISGUSTING
            else:
                return AramanaQuality.NEUTRAL
        
        # Body door
        elif dvara == DvaraType.KAYA:
            if any(kw in description for kw in ["นุ่ม", "สบาย", "เย็นสบาย"]):
                return AramanaQuality.SOFT
            elif any(kw in description for kw in ["หยาบ", "แข็ง", "หยาบกระด้าง"]):
                return AramanaQuality.ROUGH
            elif any(kw in description for kw in ["ปวด", "เจ็บ", "ร้อน"]):
                return AramanaQuality.PAINFUL
            elif any(kw in description for kw in ["สบาย", "เย็น"]):
                return AramanaQuality.COMFORTABLE
            else:
                return AramanaQuality.NEUTRAL
        
        # Mind door
        else:
            if any(kw in description for kw in self.attractive_keywords):
                return AramanaQuality.ATTRACTIVE
            elif any(kw in description for kw in self.repulsive_keywords):
                return AramanaQuality.REPULSIVE
            else:
                return AramanaQuality.NEUTRAL
    
    def _determine_vedana(self, quality: AramanaQuality, description: str) -> VedanaType:
        """กำหนดเวทนาตามธรรมชาติของอารมณ์"""
        
        # Pleasant qualities
        pleasant_qualities = [
            AramanaQuality.BEAUTIFUL,
            AramanaQuality.ATTRACTIVE,
            AramanaQuality.PLEASANT_SOUND,
            AramanaQuality.FRAGRANT,
            AramanaQuality.DELICIOUS,
            AramanaQuality.SOFT,
            AramanaQuality.COMFORTABLE
        ]
        
        # Unpleasant qualities
        unpleasant_qualities = [
            AramanaQuality.UGLY,
            AramanaQuality.REPULSIVE,
            AramanaQuality.UNPLEASANT_SOUND,
            AramanaQuality.FOUL,
            AramanaQuality.DISGUSTING,
            AramanaQuality.ROUGH,
            AramanaQuality.PAINFUL
        ]
        
        if quality in pleasant_qualities:
            return VedanaType.SUKHA
        elif quality in unpleasant_qualities:
            return VedanaType.DUKKHA
        else:
            return VedanaType.UPEKKHA
    
    def _calculate_intensity(self, description: str, quality: AramanaQuality) -> float:
        """คำนวณความแรงของอารมณ์"""
        intensity = 5.0  # default
        
        # Intensity keywords
        very_strong = ["มาก", "สุด", "มหาศาล", "ล้นหลาม", "เข้มข้น", "แรง"]
        strong = ["เยอะ", "พอสมควร", "ค่อนข้าง"]
        weak = ["นิดหน่อย", "เล็กน้อย", "ไม่มาก", "อ่อน"]
        
        for kw in very_strong:
            if kw in description:
                intensity += 3.0
                break
        
        for kw in strong:
            if kw in description:
                intensity += 1.5
                break
        
        for kw in weak:
            if kw in description:
                intensity -= 2.0
                break
        
        # Clamp to 0-10
        return max(0.0, min(10.0, intensity))
    
    def _extract_trigger_factors(self, description: str, dvara: DvaraType, quality: AramanaQuality) -> List[str]:
        """สกัดปัจจัยกระตุ้น"""
        factors = []
        
        # Add dvara as factor
        factors.append(f"dvara_{dvara.value}")
        
        # Add quality as factor
        factors.append(f"quality_{quality.value}")
        
        # Context-specific factors
        if any(kw in description for kw in ["นางเอก", "คน", "ผู้หญิง", "ผู้ชาย"]):
            factors.append("human_object")
        
        if any(kw in description for kw in ["ธรรมชาติ", "ดอกไม้", "ต้นไม้", "ทะเล"]):
            factors.append("natural_object")
        
        if any(kw in description for kw in ["ของ", "สินค้า", "ซื้อ"]):
            factors.append("material_object")
        
        if any(kw in description for kw in ["กิน", "อาหาร", "เครื่องดื่ม"]):
            factors.append("food_related")
        
        return factors
    
    def _generate_processing_notes(self, dvara: DvaraType, quality: AramanaQuality, vedana: VedanaType) -> str:
        """สร้างหมายเหตุการประมวลผล"""
        return f"Processed via {dvara.value} door, classified as {quality.value}, natural vedana: {vedana.value}"
    
    def validate(self, input_data: ProcessedSensoryInput) -> InputValidationResult:
        """ตรวจสอบความถูกต้องของ input"""
        errors = []
        warnings = []
        suggestions = []
        
        # Check intensity range
        if not (0 <= input_data.intensity <= 10):
            errors.append(f"Intensity {input_data.intensity} out of range [0, 10]")
        
        # Check dvara-aramana consistency
        expected_aramana = self._map_aramana_type(input_data.dvara)
        if input_data.aramana_type != expected_aramana:
            warnings.append(f"Aramana type {input_data.aramana_type} may not match dvara {input_data.dvara}")
        
        # Check vedana-quality consistency
        if input_data.quality == AramanaQuality.BEAUTIFUL and input_data.natural_vedana == VedanaType.DUKKHA:
            warnings.append("Beautiful quality typically produces pleasant vedana, not unpleasant")
        
        # Suggestions
        if input_data.intensity > 8:
            suggestions.append("High intensity may trigger strong kilesa. Consider mindfulness practice.")
        
        if input_data.quality in [AramanaQuality.BEAUTIFUL, AramanaQuality.ATTRACTIVE]:
            suggestions.append("Attractive object may activate kāmarāga (sensual desire). Watch for lobha.")
        
        is_valid = len(errors) == 0
        
        return InputValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
    
    def classify(self, input_data: ProcessedSensoryInput) -> InputClassification:
        """จัดประเภท input พร้อมวิเคราะห์ตามพุทธศาสตร์"""
        
        # Primary category
        primary = f"{input_data.dvara.value}_{input_data.quality.value}"
        
        # Sub-categories
        sub_cats = [
            input_data.aramana_type.value,
            input_data.natural_vedana.value,
            input_data.context.value
        ]
        
        # Buddhist analysis
        buddhist_analysis = {
            "dvara": input_data.dvara.value,
            "aramana": input_data.aramana_type.value,
            "vedana": input_data.natural_vedana.value,
            "quality": input_data.quality.value,
            "potential_kilesa": self._analyze_potential_kilesa(input_data),
            "recommended_practice": self._recommend_practice(input_data)
        }
        
        # Potential reactions
        reactions = self._predict_reactions(input_data)
        
        return InputClassification(
            primary_category=primary,
            sub_categories=sub_cats,
            buddhist_analysis=buddhist_analysis,
            potential_reactions=reactions
        )
    
    def _analyze_potential_kilesa(self, input_data: ProcessedSensoryInput) -> List[str]:
        """วิเคราะห์กิเลสที่อาจเกิด"""
        kilesas = []
        
        if input_data.natural_vedana == VedanaType.SUKHA:
            if input_data.quality in [AramanaQuality.BEAUTIFUL, AramanaQuality.ATTRACTIVE]:
                kilesas.append("lobha (โลภ - greed)")
                kilesas.append("kama_raga (กามราคะ - sensual desire)")
        
        if input_data.natural_vedana == VedanaType.DUKKHA:
            kilesas.append("dosa (โทสะ - aversion)")
            kilesas.append("patigha (ปฏิฆะ - anger)")
        
        if input_data.natural_vedana == VedanaType.UPEKKHA:
            kilesas.append("moha (โมหะ - delusion)")
            kilesas.append("avijja (อวิชชา - ignorance)")
        
        return kilesas
    
    def _recommend_practice(self, input_data: ProcessedSensoryInput) -> str:
        """แนะนำการปฏิบัติ"""
        if input_data.natural_vedana == VedanaType.SUKHA:
            return "Practice asubha (อสุภะ - contemplation of unattractiveness) or aniccānupassanā (อนิจจานุปัสสนา - reflection on impermanence)"
        
        elif input_data.natural_vedana == VedanaType.DUKKHA:
            return "Practice mettā (เมตตา - loving-kindness) or khanti (ขันติ - patience)"
        
        else:
            return "Practice sati (สติ - mindfulness) and sampajañña (สัมปชัญญะ - clear comprehension)"
    
    def _predict_reactions(self, input_data: ProcessedSensoryInput) -> List[str]:
        """ทำนายปฏิกิริยาที่อาจเกิด"""
        reactions = []
        
        if input_data.intensity > 7:
            reactions.append("strong_emotional_response")
        
        if input_data.quality in [AramanaQuality.BEAUTIFUL, AramanaQuality.ATTRACTIVE]:
            reactions.append("attachment_tendency")
            reactions.append("desire_to_possess")
        
        if input_data.quality in [AramanaQuality.UGLY, AramanaQuality.REPULSIVE]:
            reactions.append("aversion_tendency")
            reactions.append("desire_to_avoid")
        
        if input_data.dvara == DvaraType.MANO:
            reactions.append("mental_proliferation")
            reactions.append("thought_chain")
        
        return reactions


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    print("👁️ Testing Sensory Input Processor\n")
    
    processor = SensoryInputProcessor()
    
    # Test case 1: Eye door - beautiful object
    raw1 = RawSensoryInput(
        description="เห็นดอกไม้สวยมากๆ บานสะพรั่ง สีชมพูสดใส",
        source="garden",
        context=InputContext.DAILY_LIFE
    )
    
    processed1 = processor.process(raw1)
    print("="*60)
    print("Test 1: Beautiful flower")
    print("="*60)
    print(f"Dvara: {processed1.dvara.value}")
    print(f"Aramana: {processed1.aramana_type.value}")
    print(f"Quality: {processed1.quality.value}")
    print(f"Vedana: {processed1.natural_vedana.value}")
    print(f"Intensity: {processed1.intensity}/10")
    print(f"Trigger factors: {processed1.trigger_factors}")
    print(f"Notes: {processed1.processing_notes}")
    
    validation1 = processor.validate(processed1)
    print(f"\nValidation: {'✅ Valid' if validation1.is_valid else '❌ Invalid'}")
    if validation1.warnings:
        print(f"Warnings: {validation1.warnings}")
    if validation1.suggestions:
        print(f"Suggestions: {validation1.suggestions}")
    
    classification1 = processor.classify(processed1)
    print(f"\nBuddhist Analysis:")
    print(f"  Potential kilesa: {classification1.buddhist_analysis['potential_kilesa']}")
    print(f"  Recommended practice: {classification1.buddhist_analysis['recommended_practice']}")
    print(f"  Predicted reactions: {classification1.potential_reactions}")
    
    # Test case 2: Ear door - unpleasant sound
    print("\n" + "="*60)
    print("Test 2: Loud annoying sound")
    print("="*60)
    
    raw2 = RawSensoryInput(
        description="ได้ยินเสียงดังมาก รำคาญ แหลมหู",
        source="traffic",
        context=InputContext.DAILY_LIFE
    )
    
    processed2 = processor.process(raw2)
    print(f"Dvara: {processed2.dvara.value}")
    print(f"Aramana: {processed2.aramana_type.value}")
    print(f"Quality: {processed2.quality.value}")
    print(f"Vedana: {processed2.natural_vedana.value}")
    print(f"Intensity: {processed2.intensity}/10")
    
    classification2 = processor.classify(processed2)
    print(f"\nBuddhist Analysis:")
    print(f"  Potential kilesa: {classification2.buddhist_analysis['potential_kilesa']}")
    print(f"  Recommended practice: {classification2.buddhist_analysis['recommended_practice']}")
    
    # Test case 3: Mind door - memory
    print("\n" + "="*60)
    print("Test 3: Pleasant memory")
    print("="*60)
    
    raw3 = RawSensoryInput(
        description="ระลึกถึงความทรงจำดีๆ ในอดีต รู้สึกอบอุ่นใจ",
        source="meditation",
        context=InputContext.MEDITATION
    )
    
    processed3 = processor.process(raw3)
    print(f"Dvara: {processed3.dvara.value}")
    print(f"Aramana: {processed3.aramana_type.value}")
    print(f"Quality: {processed3.quality.value}")
    print(f"Vedana: {processed3.natural_vedana.value}")
    print(f"Intensity: {processed3.intensity}/10")
