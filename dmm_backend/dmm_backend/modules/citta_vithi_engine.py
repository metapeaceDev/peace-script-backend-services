"""
🧠 Citta Vithi Engine - หัวใจของ MindOS
===========================================

จำลองกระบวนการวิถีจิต (Citta Vithi) ตามหลักอภิธรรม

วิถีจิต = ลำดับของจิตที่เกิดขึ้นเมื่อรับรู้วัตถุอารมณ์

## วิถีจิต 17 ขั้นตอน (Citta Vithi Process)

### Eye-Door Process (จักขุทวารวิถี):
1. Atīta-bhavaṅga (อดีตภวังค์) - Past life-continuum
2. Bhavaṅga-calana (ภวังค์จลนะ) - Vibrating life-continuum  
3. Bhavaṅgupaccheda (ภวังคุปัจเฉทะ) - Arrest of life-continuum
4. Pañcadvārāvajjana (ปัญจทวาราวัชชนจิต) - Five-door adverting
5. Cakkhu-viññāṇa (จักขุวิญญาณ) - Eye-consciousness
6. Sampaṭicchana (สัมปฏิจฉนะ) - Receiving
7. Santīraṇa (สันตีรณะ) - Investigating
8. Voṭṭhapana (โวฏฐปนะ) - Determining
9-15. Javana (ชวนะ) - Impulsion (7 times) **← จุดสำคัญ! kusala/akusala**
16-17. Tadārammaṇa (ตทารมณะ) - Registration (2 times)

### Mind-Door Process (มโนทวารวิถี):
Simplified for mental objects (ธรรมารมณ์)

## Key Concepts:

### Javana (ชวนะ) - The Decision Point
- เป็นจิตที่มีพลังมากที่สุด
- เกิด 7 ครั้งติดต่อกัน (เหมือนตีค้อน 7 ครั้ง)
- **จุดที่กำหนดว่าจะเป็นกุศล หรือ อกุศล**
- สร้างกรรมใหม่ (มหัคคตกรรม)

### ปัจจัยที่มีผลต่อ Javana:
1. อนุสัยกิเลส (Anusaya) - ตัวเงียบที่แฝง
2. ระดับศีล-สมาธิ-ปัญญา (Virtue Level)
3. สติ (Sati) - ตัวแทรกกั้นกิเลส
4. ลักษณะของอารมณ์ (Object Nature)
5. นิวรณ์ที่กำลังรบกวน (Active Hindrances)

## Buddhist Scriptural References:
- Abhidhammatthasaṅgaha (อภิธัมมัตถสังคหะ)
- Visuddhimagga (วิสุทธิมรรค)
- Atthasālinī (อัฏฐสาลินี)

Created: October 2025
Version: 3.0
"""

from typing import Dict, List, Optional, Literal, Tuple
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
import random


# =============================================================================
# ENUMS & TYPES
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


class JavanaQuality(str, Enum):
    """คุณภาพของชวนจิต"""
    KUSALA = "kusala"           # กุศล (ดี)
    AKUSALA = "akusala"         # อกุศล (ไม่ดี)
    KIRIYA = "kiriya"           # กิริยา (เฉยๆ - สำหรับพระอรหันต์)
    VIPAKA = "vipaka"           # วิบาก (ผลกรรม)


class CittaType(str, Enum):
    """ประเภทจิต (แบบเรียบง่าย)"""
    # Kusala (12)
    MAHA_KUSALA_SOMANASSA = "มหากุศลโสมนัสสสหคตัง"  # ใจดีร่าเริง
    MAHA_KUSALA_UPEKKHA = "มหากุศลอุเบกขาสหคตัง"     # ใจดีเฉยๆ
    
    # Akusala (12)
    LOBHA_MULA = "โลภมูลจิต"      # ใจโลภ
    DOSA_MULA = "โทสมูลจิต"       # ใจโกรธ
    MOHA_MULA = "โมหมูลจิต"       # ใจหลง
    
    # Vipaka (ผลกรรม)
    KUSALA_VIPAKA = "กุศลวิบากจิต"
    AKUSALA_VIPAKA = "อกุศลวิบากจิต"
    
    # Kiriya (กิริยา)
    KIRIYA_CITTA = "กิริยาจิต"
    
    # Process Cittas
    BHAVANGA = "ภวังค์"                      # จิตสภาวะพื้นฐาน
    PANCADVARAVAJJANA = "ปัญจทวาราวัชชนจิต"  # จิตแวบรับรู้
    CAKKHU_VINNANA = "จักขุวิญญาณ"          # จิตเห็น
    SAMPATICCHANA = "สัมปฏิจฉนะ"             # จิตรับ
    SANTIRANA = "สันตีรณะ"                    # จิตตรวจ
    VOTTHAPANA = "โวฏฐปนะ"                   # จิตตัดสิน
    TADARAMMANA = "ตทารมณะ"                  # จิตระลึก


# =============================================================================
# DATA MODELS
# =============================================================================

class SensoryInput(BaseModel):
    """Input จากประสาทสัมผัส"""
    dvara: DvaraType = Field(..., description="ทวารที่รับรู้")
    aramana_type: AramanaType = Field(..., description="ประเภทของอารมณ์")
    aramana_description: str = Field(..., description="รายละเอียดอารมณ์")
    intensity: float = Field(default=5.0, ge=0, le=10, description="ความแรง")
    natural_vedana: VedanaType = Field(..., description="เวทนาตามธรรมชาติของอารมณ์")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "dvara": "eye",
                "aramana_type": "visible_form",
                "aramana_description": "ใบหน้าสวยของนางเอก",
                "intensity": 8.5,
                "natural_vedana": "pleasant",
                "timestamp": "2025-10-22T10:30:00Z"
            }
        }


class CittaMoment(BaseModel):
    """จิตขณะหนึ่งๆ"""
    citta_type: CittaType = Field(..., description="ประเภทจิต")
    quality: Optional[JavanaQuality] = Field(None, description="คุณภาพ (สำหรับชวนจิต)")
    aramana: Optional[str] = Field(None, description="อารมณ์ที่รับรู้")
    vedana: Optional[VedanaType] = Field(None, description="เวทนา")
    hetuu: List[str] = Field(default_factory=list, description="เหตุที่มากับจิต")
    cetasikas: List[str] = Field(default_factory=list, description="เจตสิกที่เกิดร่วม")
    kamma_potency: float = Field(default=0.0, description="พลังกรรม (0-100)")
    notes: str = Field(default="", description="หมายเหตุ")


class JavanaDecision(BaseModel):
    """ผลการตัดสินใจในชวนจิต"""
    chosen_quality: JavanaQuality = Field(..., description="กุศล/อกุศล/กิริยา")
    chosen_citta_type: CittaType = Field(..., description="ประเภทจิตที่เลือก")
    probability_kusala: float = Field(..., description="โอกาสเกิดกุศล %")
    probability_akusala: float = Field(..., description="โอกาสเกิดอกุศล %")
    dominant_factors: List[str] = Field(..., description="ปัจจัยที่มีอิทธิพล")
    sati_intervened: bool = Field(default=False, description="สติเข้าแทรกหรือไม่")
    reasoning: str = Field(..., description="เหตุผลการตัดสินใจ")


class ChittaVithiSequence(BaseModel):
    """ลำดับจิตทั้งวิถี"""
    vithi_type: Literal["eye_door", "mind_door"] = Field(..., description="ประเภทวิถี")
    sensory_input: SensoryInput = Field(..., description="Input ที่เข้ามา")
    citta_moments: List[CittaMoment] = Field(..., description="ลำดับจิตทั้งหมด 17 ขณะ")
    javana_decision: JavanaDecision = Field(..., description="ผลการตัดสินใจในชวนจิต")
    total_kamma_generated: float = Field(..., description="กรรมที่สร้างรวม")
    duration_ms: float = Field(default=0.017, description="เวลาที่ใช้ (milliseconds)")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    def get_javana_moments(self) -> List[CittaMoment]:
        """ดึงชวนจิต 7 ขณะ"""
        return [c for c in self.citta_moments if "ชวนะ" in c.notes]


# =============================================================================
# JAVANA DECISION ENGINE
# =============================================================================

class JavanaDecisionEngine:
    """
    ⚖️ Javana Decision Engine
    
    ตัดสินใจว่าจะเกิดกุศลจิต หรือ อกุศลจิต ในชวนจิต
    
    Logic:
    1. ตรวจสอบว่ามีสติหรือไม่ (จาก virtue_level.panna)
    2. ถ้าไม่มีสติ → ให้อนุสัยกิเลสเป็นตัวตัดสิน
    3. Match อารมณ์กับอนุสัยที่แฝง
    4. คำนวณโอกาสกุศล/อกุศล
    5. Random weighted choice
    """
    
    def __init__(self):
        self.name = "Javana Decision Engine"
        
    def decide(
        self,
        sensory_input: SensoryInput,
        anusaya_levels: Dict[str, float],  # อนุสัยกิเลส 7 ตัว
        virtue_level: Dict[str, float],     # ศีล สมาธิ ปัญญา
        active_hindrances: Dict[str, float], # นิวรณ์ที่กำลังรบกวน
    ) -> JavanaDecision:
        """
        ตัดสินใจว่าจะเกิดกุศล หรือ อกุศล
        
        Args:
            sensory_input: อารมณ์ที่เข้ามา
            anusaya_levels: ระดับอนุสัยกิเลส (0-10)
            virtue_level: ระดับศีล สมาธิ ปัญญา (0-10)
            active_hindrances: นิวรณ์ที่กำลังรบกวน (0-10)
            
        Returns:
            JavanaDecision: ผลการตัดสินใจ
        """
        
        # 1. Check Sati (Mindfulness)
        panna_level = virtue_level.get("panna", 0)
        sati_power = panna_level * 10  # แปลงเป็น %
        sati_intervened = random.random() * 100 < sati_power
        
        # 2. Calculate base probabilities
        kusala_score = 0.0
        akusala_score = 0.0
        factors = []
        
        # Factor 1: Virtue Level (ศีล สมาธิ ปัญญา)
        sila = virtue_level.get("sila", 0)
        samadhi = virtue_level.get("samadhi", 0)
        kusala_score += (sila + samadhi + panna_level) * 3.33  # max 100
        factors.append(f"Virtue ({sila:.1f}/{samadhi:.1f}/{panna_level:.1f})")
        
        # Factor 2: Anusaya Kilesa (อนุสัยกิเลส)
        if sensory_input.natural_vedana == VedanaType.SUKHA:
            # อารมณ์น่ารัก → โลภะมีโอกาสเกิด
            kama_raga = anusaya_levels.get("kama_raga", 0)
            akusala_score += kama_raga * 10
            factors.append(f"Kāmarāga (attachment): {kama_raga:.1f}")
            
        elif sensory_input.natural_vedana == VedanaType.DUKKHA:
            # อารมณ์ไม่น่ารัก → โทสะมีโอกาสเกิด
            patigha = anusaya_levels.get("patigha", 0)
            akusala_score += patigha * 10
            factors.append(f"Paṭigha (aversion): {patigha:.1f}")
            
        # Factor 3: Active Hindrances (นิวรณ์)
        for hindrance, level in active_hindrances.items():
            if level > 0:
                akusala_score += level * 5
                factors.append(f"Hindrance-{hindrance}: {level:.1f}")
        
        # Factor 4: Avijjā (ความไม่รู้) - พื้นฐานของอกุศล
        avijja = anusaya_levels.get("avijja", 0)
        akusala_score += avijja * 5
        
        # 3. Apply Sati intervention
        if sati_intervened:
            # สติเข้าแทรก → เพิ่มโอกาสกุศล
            kusala_score *= 1.5
            akusala_score *= 0.5
            factors.append(f"✨ Sati intervened! (power: {sati_power:.1f}%)")
        
        # 4. Normalize probabilities
        total = kusala_score + akusala_score
        if total == 0:
            total = 1  # prevent division by zero
            
        prob_kusala = (kusala_score / total) * 100
        prob_akusala = (akusala_score / total) * 100
        
        # 5. Make weighted random choice
        rand = random.random() * 100
        if rand < prob_kusala:
            chosen_quality = JavanaQuality.KUSALA
            chosen_citta = CittaType.MAHA_KUSALA_SOMANASSA if sensory_input.natural_vedana == VedanaType.SUKHA else CittaType.MAHA_KUSALA_UPEKKHA
            reasoning = f"กุศลจิตเกิด (โอกาส {prob_kusala:.1f}%) - มีศีล สมาธิ ปัญญาพอ"
        else:
            chosen_quality = JavanaQuality.AKUSALA
            # เลือกอกุศลจิตตามอารมณ์
            if sensory_input.natural_vedana == VedanaType.SUKHA:
                chosen_citta = CittaType.LOBHA_MULA
                reasoning = f"อกุศลจิต (โลภ) เกิด (โอกาส {prob_akusala:.1f}%) - อารมณ์น่ารัก กระตุ้นความกำหนัด"
            elif sensory_input.natural_vedana == VedanaType.DUKKHA:
                chosen_citta = CittaType.DOSA_MULA
                reasoning = f"อกุศลจิต (โทสะ) เกิด (โอกาส {prob_akusala:.1f}%) - อารมณ์ไม่น่ารัก กระตุ้นความขัดเคือง"
            else:
                chosen_citta = CittaType.MOHA_MULA
                reasoning = f"อกุศลจิต (โมหะ) เกิด (โอกาส {prob_akusala:.1f}%) - ความหลงเป็นพื้นฐาน"
        
        return JavanaDecision(
            chosen_quality=chosen_quality,
            chosen_citta_type=chosen_citta,
            probability_kusala=prob_kusala,
            probability_akusala=prob_akusala,
            dominant_factors=factors,
            sati_intervened=sati_intervened,
            reasoning=reasoning
        )


# =============================================================================
# CITTA VITHI GENERATOR
# =============================================================================

class ChittaVithiGenerator:
    """
    🧠 Citta Vithi Generator
    
    สร้างลำดับจิต 17 ขณะ จากอารมณ์ที่เข้ามา
    
    Eye-Door Process (จักขุทวารวิถี):
    1. Atīta-bhavaṅga (ภวังค์อดีต)
    2. Bhavaṅga-calana (ภวังค์จลนะ)
    3. Bhavaṅgupaccheda (ภวังคุปัจเฉทะ)
    4. Pañcadvārāvajjana (ปัญจทวาราวัชชนจิต) **← รับรู้**
    5. Cakkhu-viññāṇa (จักขุวิญญาณ) **← เห็น**
    6. Sampaṭicchana (สัมปฏิจฉนะ) **← รับ**
    7. Santīraṇa (สันตีรณะ) **← ตรวจ**
    8. Voṭṭhapana (โวฏฐปนะ) **← ตัดสิน**
    9-15. Javana (ชวนะ) x7 **← กุศล/อกุศล เกิดที่นี่!**
    16-17. Tadārammaṇa (ตทารมณะ) x2 **← ระลึก**
    """
    
    def __init__(self):
        self.decision_engine = JavanaDecisionEngine()
        
    def generate_eye_door_vithi(
        self,
        sensory_input: SensoryInput,
        anusaya_levels: Dict[str, float],
        virtue_level: Dict[str, float],
        active_hindrances: Dict[str, float],
    ) -> ChittaVithiSequence:
        """
        สร้างจักขุทวารวิถี (Eye-Door Process)
        
        Returns:
            ChittaVithiSequence: ลำดับจิตครบ 17 ขณะ
        """
        
        citta_moments: List[CittaMoment] = []
        
        # Step 1-3: Bhavaṅga (ภวังค์) x3
        for i in range(3):
            citta_moments.append(CittaMoment(
                citta_type=CittaType.BHAVANGA,
                quality=JavanaQuality.VIPAKA,
                aramana="ภวังค์อารมณ์",
                vedana=VedanaType.UPEKKHA,
                hetuu=[],
                cetasikas=["เจตนา", "ผัสสะ", "เวทนา", "สัญญา"],
                kamma_potency=0.0,
                notes=f"ภวังค์ขณะที่ {i+1}"
            ))
        
        # Step 4: Pañcadvārāvajjana (ปัญจทวาราวัชชนจิต)
        citta_moments.append(CittaMoment(
            citta_type=CittaType.PANCADVARAVAJJANA,
            quality=JavanaQuality.KIRIYA,
            aramana=sensory_input.aramana_description,
            vedana=VedanaType.UPEKKHA,
            hetuu=[],
            cetasikas=["เจตนา", "ผัสสะ", "มนสิการ"],
            kamma_potency=0.0,
            notes="แวบรับรู้อารมณ์"
        ))
        
        # Step 5: Cakkhu-viññāṇa (จักขุวิญญาณ)
        citta_moments.append(CittaMoment(
            citta_type=CittaType.CAKKHU_VINNANA,
            quality=JavanaQuality.VIPAKA,
            aramana=sensory_input.aramana_description,
            vedana=sensory_input.natural_vedana,
            hetuu=[],
            cetasikas=["เจตนา", "ผัสสะ", "เวทนา", "สัญญา"],
            kamma_potency=0.0,
            notes="เห็นอารมณ์"
        ))
        
        # Step 6: Sampaṭicchana (สัมปฏิจฉนะ)
        citta_moments.append(CittaMoment(
            citta_type=CittaType.SAMPATICCHANA,
            quality=JavanaQuality.VIPAKA,
            aramana=sensory_input.aramana_description,
            vedana=VedanaType.UPEKKHA,
            hetuu=[],
            cetasikas=["เจตนา", "ผัสสะ", "เวทนา", "สัญญา"],
            kamma_potency=0.0,
            notes="รับอารมณ์"
        ))
        
        # Step 7: Santīraṇa (สันตีรณะ)
        citta_moments.append(CittaMoment(
            citta_type=CittaType.SANTIRANA,
            quality=JavanaQuality.VIPAKA,
            aramana=sensory_input.aramana_description,
            vedana=sensory_input.natural_vedana,
            hetuu=[],
            cetasikas=["เจตนา", "ผัสสะ", "เวทนา", "สัญญา"],
            kamma_potency=0.0,
            notes="ตรวจอารมณ์"
        ))
        
        # Step 8: Voṭṭhapana (โวฏฐปนะ)
        citta_moments.append(CittaMoment(
            citta_type=CittaType.VOTTHAPANA,
            quality=JavanaQuality.KIRIYA,
            aramana=sensory_input.aramana_description,
            vedana=VedanaType.UPEKKHA,
            hetuu=[],
            cetasikas=["เจตนา", "มนสิการ"],
            kamma_potency=0.0,
            notes="กำหนดอารมณ์ - เตรียมตัดสินใจ"
        ))
        
        # Step 9-15: Javana (ชวนะ) x7 **← จุดสำคัญ!**
        javana_decision = self.decision_engine.decide(
            sensory_input=sensory_input,
            anusaya_levels=anusaya_levels,
            virtue_level=virtue_level,
            active_hindrances=active_hindrances
        )
        
        # สร้างชวนจิต 7 ขณะ
        for i in range(7):
            if javana_decision.chosen_quality == JavanaQuality.KUSALA:
                hetuu = ["อโลภะ", "อโทสะ", "อโมหะ"]
                cetasikas = ["เจตนา", "ผัสสะ", "เวทนา", "สัญญา", "สติ", "ปัญญา", "เมตตา"]
                kamma_potency = 15.0 * sensory_input.intensity  # กุศลมีพลัง
            else:
                if javana_decision.chosen_citta_type == CittaType.LOBHA_MULA:
                    hetuu = ["โลภะ"]
                    cetasikas = ["เจตนา", "ผัสสะ", "เวทนา", "สัญญา", "ราคะ", "ตัณหา"]
                elif javana_decision.chosen_citta_type == CittaType.DOSA_MULA:
                    hetuu = ["โทสะ"]
                    cetasikas = ["เจตนา", "ผัสสะ", "เวทนา", "สัญญา", "โกรธ", "ปฏิฆะ"]
                else:
                    hetuu = ["โมหะ"]
                    cetasikas = ["เจตนา", "ผัสสะ", "เวทนา", "สัญญา", "อวิชชา"]
                kamma_potency = 10.0 * sensory_input.intensity  # อกุศลก็มีพลัง
                
            citta_moments.append(CittaMoment(
                citta_type=javana_decision.chosen_citta_type,
                quality=javana_decision.chosen_quality,
                aramana=sensory_input.aramana_description,
                vedana=sensory_input.natural_vedana,
                hetuu=hetuu,
                cetasikas=cetasikas,
                kamma_potency=kamma_potency,
                notes=f"ชวนะที่ {i+1}/7 - {javana_decision.reasoning}"
            ))
        
        # Step 16-17: Tadārammaṇa (ตทารมณะ) x2
        for i in range(2):
            citta_moments.append(CittaMoment(
                citta_type=CittaType.TADARAMMANA,
                quality=JavanaQuality.VIPAKA,
                aramana=sensory_input.aramana_description,
                vedana=sensory_input.natural_vedana,
                hetuu=[],
                cetasikas=["เจตนา", "ผัสสะ", "เวทนา", "สัญญา"],
                kamma_potency=0.0,
                notes=f"ระลึกอารมณ์ครั้งที่ {i+1}"
            ))
        
        # Calculate total kamma
        total_kamma = sum(c.kamma_potency for c in citta_moments)
        
        return ChittaVithiSequence(
            vithi_type="eye_door",
            sensory_input=sensory_input,
            citta_moments=citta_moments,
            javana_decision=javana_decision,
            total_kamma_generated=total_kamma,
            duration_ms=0.017,  # 17 milliseconds for 17 moments
            timestamp=datetime.now()
        )
    
    def generate_mind_door_vithi(
        self,
        mental_object: str,
        natural_vedana: VedanaType,
        anusaya_levels: Dict[str, float],
        virtue_level: Dict[str, float],
        active_hindrances: Dict[str, float],
    ) -> ChittaVithiSequence:
        """
        สร้างมโนทวารวิถี (Mind-Door Process)
        
        เรียบง่ายกว่า - เริ่มจากมโนทวาราวัชชนจิตเลย
        """
        # Simplified for mental objects
        sensory_input = SensoryInput(
            dvara=DvaraType.MANO,
            aramana_type=AramanaType.DHAMMĀRAMMAṆA,
            aramana_description=mental_object,
            intensity=5.0,
            natural_vedana=natural_vedana
        )
        
        # Use similar process but shorter
        return self.generate_eye_door_vithi(
            sensory_input=sensory_input,
            anusaya_levels=anusaya_levels,
            virtue_level=virtue_level,
            active_hindrances=active_hindrances
        )


# =============================================================================
# MAIN ENGINE
# =============================================================================

class ChittaVithiEngine:
    """
    🧠 Citta Vithi Engine - Main Coordinator
    
    หัวใจหลักของ MindOS ที่จำลองกระบวนการวิถีจิต
    """
    
    def __init__(self):
        self.generator = ChittaVithiGenerator()
        self.name = "Citta Vithi Engine v3.0"
        
    def process_sensory_input(
        self,
        sensory_input: SensoryInput,
        core_profile: Dict,  # CoreProfile from DigitalMindModel
    ) -> ChittaVithiSequence:
        """
        ประมวลผล sensory input → สร้างวิถีจิต
        
        Args:
            sensory_input: อารมณ์ที่เข้ามา
            core_profile: โปรไฟล์หลักของใจ (anusaya, virtue_level, etc.)
            
        Returns:
            ChittaVithiSequence: ลำดับจิตครบ 17 ขณะ พร้อมผลกรรม
        """
        
        # Extract from core_profile
        anusaya = core_profile.get("LatentTendencies", {}).get("anusaya_kilesa", {})
        anusaya_levels = {
            "kama_raga": anusaya.get("kama_raga", {}).get("level", 5),
            "patigha": anusaya.get("patigha", {}).get("level", 5),
            "avijja": anusaya.get("avijja", {}).get("level", 5),
        }
        
        virtue = core_profile.get("VirtueLevel", {})
        virtue_level = {
            "sila": virtue.get("sila", 5),
            "samadhi": virtue.get("samadhi", 5),
            "panna": virtue.get("panna", 5),
        }
        
        hindrances = core_profile.get("active_hindrances", {})
        active_hindrances = {
            k: v.get("intensity", 0) 
            for k, v in hindrances.items() 
            if v.get("isActive", False)
        }
        
        # Generate citta vithi
        if sensory_input.dvara == DvaraType.MANO:
            return self.generator.generate_mind_door_vithi(
                mental_object=sensory_input.aramana_description,
                natural_vedana=sensory_input.natural_vedana,
                anusaya_levels=anusaya_levels,
                virtue_level=virtue_level,
                active_hindrances=active_hindrances
            )
        else:
            return self.generator.generate_eye_door_vithi(
                sensory_input=sensory_input,
                anusaya_levels=anusaya_levels,
                virtue_level=virtue_level,
                active_hindrances=active_hindrances
            )
    
    def get_summary(self, vithi: ChittaVithiSequence) -> str:
        """สรุปผลของวิถีจิต"""
        javana = vithi.javana_decision
        
        summary = f"""
🧠 Citta Vithi Summary
{'='*50}
📥 Input: {vithi.sensory_input.aramana_description}
   Door: {vithi.sensory_input.dvara.value}
   Feeling: {vithi.sensory_input.natural_vedana.value}
   Intensity: {vithi.sensory_input.intensity}/10

⚖️ Decision:
   Quality: {javana.chosen_quality.value}
   Citta: {javana.chosen_citta_type.value}
   Reasoning: {javana.reasoning}
   
📊 Probabilities:
   Kusala: {javana.probability_kusala:.1f}%
   Akusala: {javana.probability_akusala:.1f}%
   
🎯 Key Factors:
   {chr(10).join(f'   - {f}' for f in javana.dominant_factors)}
   
✨ Sati: {'✅ Intervened!' if javana.sati_intervened else '❌ Not present'}

💪 Kamma Generated: {vithi.total_kamma_generated:.1f}
⏱️ Duration: {vithi.duration_ms}ms ({len(vithi.citta_moments)} moments)

🔢 Citta Sequence:
   {chr(10).join(f'   {i+1}. {c.citta_type.value}' for i, c in enumerate(vithi.citta_moments))}
"""
        return summary


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    print("🧠 Testing Citta Vithi Engine\n")
    
    # Initialize engine
    engine = ChittaVithiEngine()
    
    # Example: ภิกษุที่มีศีลสมาธิปัญญาสูง เห็นนางเอกสวย
    core_profile_monk = {
        "LatentTendencies": {
            "anusaya_kilesa": {
                "kama_raga": {"level": 2},  # ความกำหนัดต่ำ
                "patigha": {"level": 1},
                "avijja": {"level": 3},
            }
        },
        "VirtueLevel": {
            "sila": 9,
            "samadhi": 8,
            "panna": 8,
        },
        "active_hindrances": {}
    }
    
    sensory_input = SensoryInput(
        dvara=DvaraType.CAKKHU,
        aramana_type=AramanaType.RUPA,
        aramana_description="ใบหน้าสวยของนางเอก",
        intensity=8.5,
        natural_vedana=VedanaType.SUKHA
    )
    
    vithi = engine.process_sensory_input(sensory_input, core_profile_monk)
    print(engine.get_summary(vithi))
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: ปุถุชนที่มีกิเลสสูง เห็นนางเอกสวยเหมือนกัน
    core_profile_normal = {
        "LatentTendencies": {
            "anusaya_kilesa": {
                "kama_raga": {"level": 8},  # ความกำหนัดสูง
                "patigha": {"level": 5},
                "avijja": {"level": 9},
            }
        },
        "VirtueLevel": {
            "sila": 3,
            "samadhi": 2,
            "panna": 1,
        },
        "active_hindrances": {
            "kama_cchanda": {"isActive": True, "intensity": 7}
        }
    }
    
    vithi2 = engine.process_sensory_input(sensory_input, core_profile_normal)
    print(engine.get_summary(vithi2))
