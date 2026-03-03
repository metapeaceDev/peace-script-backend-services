"""
🎭 Interactive Simulation Engine - ระบบจำลองสถานการณ์แบบโต้ตอบ
================================================================

สร้างสถานการณ์จำลองที่ผู้ใช้สามารถเลือกตอบสนองได้
เห็นผลทันที - กรรมเปลี่ยน, รูปกายเปลี่ยน, จิตเปลี่ยน

## Simulation Flow:

1. **Present Scenario** - แสดงสถานการณ์
   - Context setup
   - Sensory input description
   - Emotional state

2. **Offer Choices** - เสนอทางเลือก
   - Kusala option (mindful response)
   - Akusala option (reactive response)
   - Neutral option (passive response)

3. **Process Response** - ประมวลผลการตอบสนอง
   - Generate citta vithi
   - Calculate kamma
   - Update state

4. **Show Consequences** - แสดงผลที่ตามมา
   - Immediate: จิตที่เกิด, เวทนา
   - Short-term: นิวรณ์, ศีลสมาธิปัญญา
   - Long-term: กรรม, รูปกาย

5. **Repeat or End** - ทำต่อหรือจบ
   - Chain reactions
   - Cumulative effects
   - Final summary

## Scenario Types:

### 1. Temptation Scenarios (ล่อลวง)
- Marketplace: เห็นของสวย ราคาแพง
- Social media: เห็นโพสต์ที่อิจฉา
- Food: เห็นอาหารอร่อย แต่ไม่ดีต่อสุขภาพ

### 2. Conflict Scenarios (ความขัดแย้ง)
- Being insulted: ถูกด่า ถูกดูถูก
- Disagreement: มีคนไม่เห็นด้วย
- Competition: แพ้คนอื่น

### 3. Practice Scenarios (การปฏิบัติ)
- Meditation: นั่งสมาธิ จิตฟุ้งซ่าน
- Dana: มีคนขอบริจาค
- Precepts: อยากทำผิดศีล

### 4. Life Events (เหตุการณ์ชีวิต)
- Success: ได้รับรางวัล ชนะ
- Failure: สอบตก ล้มเหลว
- Loss: สูญเสียคนรัก

Created: October 2025
Version: 3.0
"""

from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import random


# =============================================================================
# ENUMS & TYPES
# =============================================================================

class ScenarioCategory(str, Enum):
    """ประเภทสถานการณ์"""
    TEMPTATION = "temptation"       # ล่อลวง
    CONFLICT = "conflict"           # ความขัดแย้ง
    PRACTICE = "practice"           # การปฏิบัติ
    LIFE_EVENT = "life_event"       # เหตุการณ์ชีวิต
    DAILY_LIFE = "daily_life"       # ชีวิตประจำวัน


class ChoiceType(str, Enum):
    """ประเภททางเลือก"""
    KUSALA = "kusala"               # กุศล - มีสติ
    AKUSALA = "akusala"             # อกุศล - ตามกิเลส
    NEUTRAL = "neutral"             # กลางๆ - เฉยๆ


class ConsequenceLevel(str, Enum):
    """ระดับผลที่ตามมา"""
    IMMEDIATE = "immediate"         # ทันที (citta, vedana)
    SHORT_TERM = "short_term"       # ระยะสั้น (hindrances, virtue)
    LONG_TERM = "long_term"         # ระยะยาว (kamma, appearance)


# =============================================================================
# DATA MODELS
# =============================================================================

class Choice(BaseModel):
    """ทางเลือกในสถานการณ์"""
    choice_id: str = Field(..., description="ID ของทางเลือก")
    choice_type: ChoiceType = Field(..., description="ประเภท kusala/akusala/neutral")
    label: str = Field(..., description="ป้ายชื่อ")
    description: str = Field(..., description="รายละเอียดการกระทำ")
    inner_dialogue: str = Field(..., description="ความคิดภายใน")
    expected_citta: str = Field(..., description="จิตที่คาดว่าจะเกิด")
    expected_kamma: float = Field(..., description="กรรมที่คาดว่าจะเกิด")
    difficulty: int = Field(default=5, ge=1, le=10, description="ความยาก 1-10")


class Scenario(BaseModel):
    """สถานการณ์จำลอง"""
    scenario_id: str = Field(..., description="ID ของสถานการณ์")
    category: ScenarioCategory = Field(..., description="ประเภทสถานการณ์")
    title: str = Field(..., description="หัวข้อ")
    description: str = Field(..., description="รายละเอียดสถานการณ์")
    
    # Sensory input
    sensory_description: str = Field(..., description="สิ่งที่รับรู้")
    dvara_type: str = Field(..., description="ทวารที่ใช้")
    vedana_nature: str = Field(..., description="เวทนาของอารมณ์")
    intensity: float = Field(default=5.0, ge=0, le=10)
    
    # Choices
    choices: List[Choice] = Field(..., description="ทางเลือกที่มี")
    
    # Context
    context_setup: Dict = Field(default_factory=dict, description="บริบทเบื้องต้น")
    learning_points: List[str] = Field(default_factory=list, description="จุดเรียนรู้")
    
    class Config:
        json_schema_extra = {
            "example": {
                "scenario_id": "market_001",
                "category": "temptation",
                "title": "ของสวยในตลาด",
                "description": "คุณเดินในตลาด เห็นของสวยมาก แต่ราคาแพงเกินงบ",
                "sensory_description": "เห็นกระเป๋าหนังสวยๆ สีชมพู",
                "dvara_type": "eye",
                "vedana_nature": "pleasant",
                "intensity": 7.5,
                "choices": [],
                "learning_points": ["Practice contentment", "Observe lobha"]
            }
        }


class SimulationResponse(BaseModel):
    """การตอบสนองของผู้ใช้"""
    choice_id: str = Field(..., description="ID ของทางเลือกที่เลือก")
    reasoning: Optional[str] = Field(None, description="เหตุผลที่เลือก")
    timestamp: datetime = Field(default_factory=datetime.now)


class ConsequenceReport(BaseModel):
    """รายงานผลที่ตามมา"""
    level: ConsequenceLevel = Field(..., description="ระดับผลกระทบ")
    description: str = Field(..., description="รายละเอียด")
    changes: Dict = Field(default_factory=dict, description="การเปลี่ยนแปลง")
    visual_indicators: List[str] = Field(default_factory=list, description="สัญลักษณ์แสดงผล")


class SimulationResult(BaseModel):
    """ผลลัพธ์ของการจำลอง"""
    scenario_id: str = Field(..., description="ID สถานการณ์")
    choice_made: Choice = Field(..., description="ทางเลือกที่เลือก")
    
    # Citta vithi result
    vithi_summary: str = Field(..., description="สรุปวิถีจิต")
    citta_generated: str = Field(..., description="จิตที่เกิด")
    kamma_generated: float = Field(..., description="กรรมที่สร้าง")
    
    # Consequences
    immediate_consequences: List[ConsequenceReport] = Field(..., description="ผลทันที")
    short_term_consequences: List[ConsequenceReport] = Field(..., description="ผลระยะสั้น")
    long_term_consequences: List[ConsequenceReport] = Field(..., description="ผลระยะยาว")
    
    # State changes
    state_before: Dict = Field(..., description="สภาวะก่อน")
    state_after: Dict = Field(..., description="สภาวะหลัง")
    
    # Learning
    wisdom_gained: str = Field(..., description="ข้อคิดที่ได้")
    practice_tip: str = Field(..., description="เคล็ดลับการปฏิบัติ")
    
    timestamp: datetime = Field(default_factory=datetime.now)


# =============================================================================
# SCENARIO TEMPLATES
# =============================================================================

SCENARIO_TEMPLATES = {
    # Temptation scenarios
    "marketplace_expensive": {
        "scenario_id": "market_001",
        "category": "temptation",
        "title": "ของสวยในตลาด - ราคาแพง",
        "description": "คุณเดินในห้างสรรพสินค้า เห็นกระเป๋าหนังสวยมากๆ แต่ราคา 50,000 บาท เกินงบที่มี คุณรู้สึกอยากได้มาก มีบัตรเครดิตในกระเป๋า",
        "sensory_description": "เห็นกระเป๋าหนังสีชมพูพาสเทล แบรนด์ดัง วางอยู่บนชั้นวางสินค้า",
        "dvara_type": "eye",
        "vedana_nature": "pleasant",
        "intensity": 8.5,
        "choices": [
            {
                "choice_id": "market_001_kusala",
                "choice_type": "kusala",
                "label": "สังเกตความอยาก แล้วเดินผ่าน",
                "description": "รู้สึกตัวว่ากำลังอยากได้ สังเกตเวทนาและความอยาก พิจารณาอนิจจัง ไม่จำเป็นต้องมี เดินผ่านไปด้วยสติ",
                "inner_dialogue": "สวยจริง แต่ฉันไม่จำเป็นต้องมี ความอยากนี้เป็นอนิจจัง ฉันมีกระเป๋าอยู่แล้ว ไม่ต้องซื้อก็ได้",
                "expected_citta": "มหากุศลจิต",
                "expected_kamma": 0,  # ไม่สร้างกรรมใหม่ แต่ต้านกิเลส
                "difficulty": 7
            },
            {
                "choice_id": "market_001_akusala",
                "choice_type": "akusala",
                "label": "ไม่ไหว ต้องซื้อ!",
                "description": "รู้สึกต้องการมากๆ คิดว่าควรมี สมน้ำสมเนื้อกับตัวเอง จ่ายด้วยบัตรเครดิต ไม่สนใจว่าเกินงบ",
                "inner_dialogue": "สวยมาก! ต้องมี! ไม่ซื้อจะเสียดายตลอดชีวิต คนอื่นก็มีกัน ทำไมฉันไม่ได้? จ่ายก่อนค่อยว่ากัน",
                "expected_citta": "โลภมูลจิต",
                "expected_kamma": 750,  # อกุศลกรรมหนัก
                "difficulty": 3
            },
            {
                "choice_id": "market_001_neutral",
                "choice_type": "neutral",
                "label": "ถ่ายรูป แล้วบอกตัวเองว่าจะซื้อทีหลัง",
                "description": "ถ่ายรูปเก็บไว้ บอกตัวเองว่าถ้ายังชอบอยู่อีก 1 เดือนค่อยกลับมาซื้อ หาข้อมูลเปรียบเทียบราคา",
                "inner_dialogue": "สวยจัง แต่อาจไม่จำเป็นตอนนี้ เก็บรูปไว้ก่อน ค่อยคิดทีหลัง ราคาอาจลดด้วย",
                "expected_citta": "อหิตุกจิต",
                "expected_kamma": 100,  # กรรมเบาๆ ยังมีความอยากแฝง
                "difficulty": 5
            }
        ],
        "context_setup": {
            "location": "ห้างสรรพสินค้าหรู",
            "time": "วันหยุดสุดสัปดาห์",
            "mood": "ผ่อนคลาย อยากช้อปปิ้ง",
            "budget_status": "งบประมาณเหลือ 20,000 บาท"
        },
        "learning_points": [
            "สังเกตความอยาก (kāma-taṇhā)",
            "ปฏิบัติสันโดษ (contentment)",
            "พิจารณาอนิจจัง (impermanence)",
            "แยกความต้องการกับความอยาก"
        ]
    },
    
    "conflict_insult": {
        "scenario_id": "conflict_001",
        "category": "conflict",
        "title": "ถูกดูถูก ต่อหน้าคนจำนวนมาก",
        "description": "ในที่ประชุม เพื่อนร่วมงานคนหนึ่งวิจารณ์งานของคุณต่อหน้าทุกคนว่า 'งานนี้ทำแย่มาก ไม่รู้คิดอะไรอยู่' เสียงดัง หน้าแข็ง",
        "sensory_description": "ได้ยินเสียงดุด่าวิจารณ์ เห็นสีหน้าโกรธ รู้สึกอับอาย ใจพล่าน",
        "dvara_type": "ear",
        "vedana_nature": "unpleasant",
        "intensity": 9.0,
        "choices": [
            {
                "choice_id": "conflict_001_kusala",
                "choice_type": "kusala",
                "label": "หายใจลึก รับฟังด้วยสติ",
                "description": "รู้สึกโกรธขึ้นมา แต่หายใจลึกๆ รับรู้อารมณ์โกรธ ไม่ตอบโต้ทันที รอให้ใจสงบก่อน แล้วค่อยคุยกันด้วยเหตุผล",
                "inner_dialogue": "โกรธจัง... แต่ถ้าตอบโต้ตอนนี้จะแย่กว่า หายใจก่อน... สังเกตความโกรธ... ค่อยคุยกันทีหลังดีกว่า",
                "expected_citta": "มหากุศลจิต (with khanti)",
                "expected_kamma": 0,  # ต้านโทสะ
                "difficulty": 9
            },
            {
                "choice_id": "conflict_001_akusala",
                "choice_type": "akusala",
                "label": "โต้กลับทันที อารมณ์เสีย",
                "description": "โกรธมาก ตอบโต้ทันที ด่ากลับว่า 'แกเองยังทำไม่ได้เลย อย่ามาสอนฉัน!' เสียงดัง หน้าแดง ทะเลาะกัน",
                "inner_dialogue": "ใครมันจะมาด่าฉัน! กล้าดีนะ! โต้กลับให้รู้ว่าฉันไม่ใช่คนง่ายๆ!",
                "expected_citta": "โทสมูลจิต",
                "expected_kamma": 850,  # อกุศลกรรมหนักมาก
                "difficulty": 2
            },
            {
                "choice_id": "conflict_001_neutral",
                "choice_type": "neutral",
                "label": "เงียบ ไม่พูดอะไร แต่ในใจโกรธมาก",
                "description": "ไม่ตอบโต้ แต่ในใจโกรธแค้นมาก กลั้นไว้ นั่งหน้าเฉย แต่ในใจด่าเต็มที่",
                "inner_dialogue": "โกรธมาก! แต่ไม่ด่ากลับ กลั้นไว้... แต่ในใจฉันจำได้ เดี๋ยวแก  รู้ว่าฉันไม่ใช่คนง่ายๆ",
                "expected_citta": "โทสมูลจิต (กดดัน)",
                "expected_kamma": 600,  # อกุศลกรรมปานกลาง แต่สะสมในใจ
                "difficulty": 4
            }
        ],
        "context_setup": {
            "location": "ห้องประชุม",
            "time": "เวลาทำงาน",
            "mood": "กำลังนำเสนองาน",
            "relationship": "เพื่อนร่วมงานที่แข่งขันกัน"
        },
        "learning_points": [
            "สังเกตความโกรธ (dosa)",
            "ปฏิบัติขันติ (patience)",
            "ปฏิบัติเมตตา (loving-kindness)",
            "แยกความโกรธกับตัวตน"
        ]
    },
    
    "meditation_wandering": {
        "scenario_id": "practice_001",
        "category": "practice",
        "title": "จิตฟุ้งซ่าน ขณะนั่งสมาธิ",
        "description": "คุณนั่งสมาธิมา 10 นาที แต่จิตฟุ้งซ่านไปเรื่อย คิดถึงงาน คิดถึงอาหาร คิดถึงเรื่องต่างๆ ไม่สามารถมีสติกับลมหายใจได้นาน",
        "sensory_description": "รู้สึกลมหายใจเข้าออก แต่ก็นึกขึ้นมาว่า 'เมื่อวานหัวหน้าว่าอะไรนะ...' แล้วก็หลงไปตามความคิด",
        "dvara_type": "mind",
        "vedana_nature": "neutral",
        "intensity": 4.0,
        "choices": [
            {
                "choice_id": "practice_001_kusala",
                "choice_type": "kusala",
                "label": "รู้ตัวว่าหลง กลับมาที่ลมหายใจอย่างอ่อนโยน",
                "description": "รู้ว่าจิตฟุ้งซ่าน ยอมรับโดยไม่ตำหนิตัวเอง พูดในใจว่า 'ฟุ้งซ่านนะ' แล้วกลับมาสังเกตลมหายใจใหม่ ทำซ้ำๆ ด้วยความอดทน",
                "inner_dialogue": "อ๋อ หลงไปแล้ว ไม่เป็นไร กลับมา... ลมหายใจเข้า... ลมหายใจออก...",
                "expected_citta": "มหากุศลจิต (with sati)",
                "expected_kamma": 0,  # พัฒนาสติ
                "difficulty": 6
            },
            {
                "choice_id": "practice_001_akusala",
                "choice_type": "akusala",
                "label": "โกรธตัวเอง เลิกนั่ง",
                "description": "รู้สึกหงุดหงิด โกรธตัวเอง คิดว่าตัวเองทำไม่ได้ ทำไมจิตฟุ้งซ่านขนาดนี้ เลิกนั่ง ลุกไปทำอย่างอื่น",
                "inner_dialogue": "ทำไมจิตฟุ้งซ่านขนาดนี้! ไม่มีสมาธิเลย! นั่งไปก็เปล่าประโยชน์ เลิก!",
                "expected_citta": "โทสมูลจิต (ต่อตัวเอง)",
                "expected_kamma": 200,  # อกุศลกรรมเบา
                "difficulty": 4
            },
            {
                "choice_id": "practice_001_neutral",
                "choice_type": "neutral",
                "label": "นั่งต่อ แต่ปล่อยให้จิตคิดไป",
                "description": "นั่งต่อไป แต่ไม่ได้พยายามกลับมา ปล่อยให้จิตคิดไปเรื่อยๆ ทำเป็นนั่งสมาธิ แต่ก็ไม่มีสติ",
                "inner_dialogue": "ก็นั่งอยู่นี่แหละ คิดไปก็ได้ อย่างน้อยก็นั่งอยู่...",
                "expected_citta": "อหิตุกจิต",
                "expected_kamma": 50,  # กรรมน้อยมาก
                "difficulty": 2
            }
        ],
        "context_setup": {
            "location": "ห้องสมาธิ",
            "time": "เช้า",
            "mood": "ตั้งใจนั่ง",
            "experience_level": "เริ่มต้น"
        },
        "learning_points": [
            "สติต้องฝึก ไม่ใช่ของที่มีทันที",
            "การรู้ว่าหลงก็คือสติ",
            "ไม่ตำหนิตัวเอง มีเมตตาต่อตัวเอง",
            "ความอดทน (viriya) สำคัญ"
        ]
    }
}


# =============================================================================
# INTERACTIVE SIMULATION ENGINE
# =============================================================================

class InteractiveSimulationEngine:
    """
    🎭 Interactive Simulation Engine
    
    จัดการสถานการณ์จำลองแบบโต้ตอบ
    
    Features:
    - Load scenario templates
    - Present choices to user
    - Process user response
    - Generate citta vithi
    - Calculate consequences
    - Update state
    - Track progress
    """
    
    def __init__(self):
        self.name = "Interactive Simulation Engine v3.0"
        self.scenarios = SCENARIO_TEMPLATES
        
    def get_scenario(self, scenario_id: str) -> Optional[Scenario]:
        """ดึงสถานการณ์ตาม ID"""
        template = self.scenarios.get(scenario_id)
        if not template:
            return None
        
        # Convert template to Scenario object
        return Scenario(**template)
    
    def list_scenarios(self, category: Optional[ScenarioCategory] = None) -> List[Dict]:
        """แสดงรายการสถานการณ์ทั้งหมด"""
        scenarios = []
        
        for sid, template in self.scenarios.items():
            if category is None or template["category"] == category:
                scenarios.append({
                    "scenario_id": sid,
                    "category": template["category"],
                    "title": template["title"],
                    "difficulty": sum(c["difficulty"] for c in template["choices"]) / len(template["choices"])
                })
        
        return scenarios
    
    async def simulate(
        self,
        scenario_id: str,
        choice_id: str,
        current_state: Dict,
        model_id: str
    ) -> SimulationResult:
        """
        รันการจำลอง
        
        Args:
            scenario_id: ID ของสถานการณ์
            choice_id: ID ของทางเลือกที่เลือก
            current_state: สภาวะจิตปัจจุบัน
            model_id: ID ของ model
            
        Returns:
            SimulationResult: ผลลัพธ์ของการจำลอง
        """
        # Get scenario
        scenario = self.get_scenario(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")
        
        # Get choice
        choice = None
        for c in scenario.choices:
            if c.choice_id == choice_id:
                choice = c
                break
        
        if not choice:
            raise ValueError(f"Choice {choice_id} not found")
        
        # Save state before
        state_before = {
            "virtue": current_state.get("VirtueLevel", {}),
            "hindrances": current_state.get("active_hindrances", {}),
            "kusala_count": current_state.get("total_kusala_count", 0),
            "akusala_count": current_state.get("total_akusala_count", 0)
        }
        
        # Generate consequences based on choice type
        immediate = self._generate_immediate_consequences(choice, scenario)
        short_term = self._generate_short_term_consequences(choice, current_state)
        long_term = self._generate_long_term_consequences(choice, current_state)
        
        # Update state (simplified - in real use, integrate with citta vithi + state updater)
        state_after = await self._apply_consequences(current_state, choice)
        
        # Generate wisdom
        wisdom, practice_tip = self._generate_learning(choice, scenario)
        
        return SimulationResult(
            scenario_id=scenario_id,
            choice_made=choice,
            vithi_summary=f"{choice.expected_citta} generated with vedana: {scenario.vedana_nature}",
            citta_generated=choice.expected_citta,
            kamma_generated=choice.expected_kamma,
            immediate_consequences=immediate,
            short_term_consequences=short_term,
            long_term_consequences=long_term,
            state_before=state_before,
            state_after=state_after,
            wisdom_gained=wisdom,
            practice_tip=practice_tip,
            timestamp=datetime.now()
        )
    
    def _generate_immediate_consequences(self, choice: Choice, scenario: Scenario) -> List[ConsequenceReport]:
        """สร้างผลทันที"""
        consequences = []
        
        if choice.choice_type == ChoiceType.KUSALA:
            consequences.append(ConsequenceReport(
                level=ConsequenceLevel.IMMEDIATE,
                description=f"กุศลจิตเกิด: {choice.expected_citta}",
                changes={"citta": choice.expected_citta, "vedana": "peace"},
                visual_indicators=["✨", "🙏", "😌"]
            ))
            consequences.append(ConsequenceReport(
                level=ConsequenceLevel.IMMEDIATE,
                description="รู้สึกสงบ มีสติ ใจเบา",
                changes={"emotion": "peaceful", "awareness": "high"},
                visual_indicators=["💚", "🕉️"]
            ))
        
        elif choice.choice_type == ChoiceType.AKUSALA:
            consequences.append(ConsequenceReport(
                level=ConsequenceLevel.IMMEDIATE,
                description=f"อกุศลจิตเกิด: {choice.expected_citta}",
                changes={"citta": choice.expected_citta, "vedana": "agitation"},
                visual_indicators=["⚠️", "😤", "😠"]
            ))
            consequences.append(ConsequenceReport(
                level=ConsequenceLevel.IMMEDIATE,
                description="รู้สึกไม่สงบ ตามกิเลส ใจหนัก",
                changes={"emotion": "agitated", "awareness": "low"},
                visual_indicators=["💔", "⚡"]
            ))
        
        else:  # NEUTRAL
            consequences.append(ConsequenceReport(
                level=ConsequenceLevel.IMMEDIATE,
                description="จิตเฉยๆ ไม่ค่อยมีสติ",
                changes={"citta": choice.expected_citta, "vedana": "neutral"},
                visual_indicators=["😐", "💤"]
            ))
        
        return consequences
    
    def _generate_short_term_consequences(self, choice: Choice, current_state: Dict) -> List[ConsequenceReport]:
        """สร้างผลระยะสั้น (นิวรณ์, ศีลสมาธิปัญญา)"""
        consequences = []
        
        if choice.choice_type == ChoiceType.KUSALA:
            consequences.append(ConsequenceReport(
                level=ConsequenceLevel.SHORT_TERM,
                description="นิวรณ์ลดลง สติเพิ่มขึ้น",
                changes={"hindrances": "decreased", "sati": "increased"},
                visual_indicators=["📉", "✅"]
            ))
            consequences.append(ConsequenceReport(
                level=ConsequenceLevel.SHORT_TERM,
                description="ศีล สมาธิ ปัญญา เพิ่มขึ้นเล็กน้อย",
                changes={"virtue": "+0.1"},
                visual_indicators=["📈", "🌟"]
            ))
        
        elif choice.choice_type == ChoiceType.AKUSALA:
            consequences.append(ConsequenceReport(
                level=ConsequenceLevel.SHORT_TERM,
                description="นิวรณ์เพิ่มขึ้น กิเลสแรงขึ้น",
                changes={"hindrances": "increased", "kilesa": "stronger"},
                visual_indicators=["📈", "⚠️"]
            ))
            consequences.append(ConsequenceReport(
                level=ConsequenceLevel.SHORT_TERM,
                description="ศีล สมาธิ ปัญญา ลดลงเล็กน้อย",
                changes={"virtue": "-0.1"},
                visual_indicators=["📉", "⚠️"]
            ))
        
        return consequences
    
    def _generate_long_term_consequences(self, choice: Choice, current_state: Dict) -> List[ConsequenceReport]:
        """สร้างผลระยะยาว (กรรม, รูปกาย)"""
        consequences = []
        
        kamma = choice.expected_kamma
        
        if kamma > 0:
            consequences.append(ConsequenceReport(
                level=ConsequenceLevel.LONG_TERM,
                description=f"กรรมเพิ่มในคิว: {kamma:.0f} potency",
                changes={"kamma_queue": f"+{kamma}"},
                visual_indicators=["📦", "⏳"]
            ))
            
            if kamma > 500:
                consequences.append(ConsequenceReport(
                    level=ConsequenceLevel.LONG_TERM,
                    description="กรรมหนัก อาจส่งผลต่อรูปกายในอนาคต",
                    changes={"appearance_risk": "high"},
                    visual_indicators=["⚠️", "👤"]
                ))
        
        elif choice.choice_type == ChoiceType.KUSALA:
            consequences.append(ConsequenceReport(
                level=ConsequenceLevel.LONG_TERM,
                description="ไม่สร้างกรรมใหม่ แต่ต้านกิเลส ป้องกันกรรมเก่า",
                changes={"kamma_prevention": "active"},
                visual_indicators=["🛡️", "✨"]
            ))
        
        return consequences
    
    async def _apply_consequences(self, current_state: Dict, choice: Choice) -> Dict:
        """ประยุกต์ผลกระทบกับ state"""
        # Simplified version - in real use, call state_updater
        
        virtue = current_state.get("VirtueLevel", {})
        
        if choice.choice_type == ChoiceType.KUSALA:
            virtue["sila"] = min(10, virtue.get("sila", 5) + 0.05)
            virtue["samadhi"] = min(10, virtue.get("samadhi", 5) + 0.08)
            virtue["panna"] = min(10, virtue.get("panna", 5) + 0.03)
            current_state["total_kusala_count"] = current_state.get("total_kusala_count", 0) + 1
        
        elif choice.choice_type == ChoiceType.AKUSALA:
            virtue["sila"] = max(0, virtue.get("sila", 5) - 0.03)
            virtue["samadhi"] = max(0, virtue.get("samadhi", 5) - 0.05)
            virtue["panna"] = max(0, virtue.get("panna", 5) - 0.02)
            current_state["total_akusala_count"] = current_state.get("total_akusala_count", 0) + 1
        
        return {
            "virtue": virtue,
            "hindrances": current_state.get("active_hindrances", {}),
            "kusala_count": current_state.get("total_kusala_count", 0),
            "akusala_count": current_state.get("total_akusala_count", 0)
        }
    
    def _generate_learning(self, choice: Choice, scenario: Scenario) -> Tuple[str, str]:
        """สร้างข้อคิดและเคล็ดลับ"""
        
        if choice.choice_type == ChoiceType.KUSALA:
            wisdom = f"เยี่ยมมาก! การมีสติและเลือกกุศลในสถานการณ์นี้ แสดงถึงการฝึกฝนที่ดี คุณต้านกิเลสได้สำเร็จ"
            practice_tip = "ฝึกให้เกิดความชำนาญในการรู้ตัวเร็ว และเลือกกุศลโดยอัตโนมัติ ด้วยการปฏิบัติบ่อยๆ"
        
        elif choice.choice_type == ChoiceType.AKUSALA:
            wisdom = f"ครั้งนี้ตามกิเลสไป แต่อย่างน้อยคุณได้เรียนรู้ว่ากิเลสนี้แรงแค่ไหน ครั้งหน้าจะมีสติมากขึ้น"
            practice_tip = f"ฝึกสังเกตอารมณ์ก่อนที่จะตอบสนอง หายใจลึกๆ 3 ครั้ง ให้เวลาสติเข้ามา - {scenario.learning_points[0]}"
        
        else:
            wisdom = "การเลือกเฉยๆ ไม่ได้ช่วยพัฒนาจิต ลองเลือกให้ชัดเจนว่ากุศลหรืออกุศล เพื่อเรียนรู้จากผล"
            practice_tip = "ฝึกให้มีสติมากขึ้น อย่าปล่อยให้จิตเป็นกลางๆ โดยไม่รู้ตัว"
        
        return wisdom, practice_tip


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    import asyncio
    
    print("🎭 Testing Interactive Simulation Engine\n")
    
    engine = InteractiveSimulationEngine()
    
    # List all scenarios
    print("="*60)
    print("Available Scenarios:")
    print("="*60)
    scenarios = engine.list_scenarios()
    for s in scenarios:
        print(f"- [{s['category']}] {s['title']} (difficulty: {s['difficulty']:.1f}/10)")
    
    # Get specific scenario
    print("\n" + "="*60)
    print("Scenario Detail: marketplace_expensive")
    print("="*60)
    
    scenario = engine.get_scenario("marketplace_expensive")
    if scenario:
        print(f"\n📖 Title: {scenario.title}")
        print(f"📝 Description: {scenario.description}")
        print(f"👁️ Sensory: {scenario.sensory_description}")
        print(f"📊 Intensity: {scenario.intensity}/10")
        print(f"\n💡 Choices:")
        for i, choice in enumerate(scenario.choices, 1):
            print(f"\n{i}. [{choice.choice_type}] {choice.label}")
            print(f"   {choice.description}")
            print(f"   💭 Inner: {choice.inner_dialogue}")
            print(f"   🎯 Expected: {choice.expected_citta}")
            print(f"   ⚖️ Kamma: {choice.expected_kamma}")
            print(f"   🎲 Difficulty: {choice.difficulty}/10")
    
    # Simulate kusala choice
    async def test_simulation():
        print("\n" + "="*60)
        print("Test Simulation: Kusala Choice")
        print("="*60)
        
        current_state = {
            "VirtueLevel": {
                "sila": 5.0,
                "samadhi": 4.5,
                "panna": 4.0
            },
            "active_hindrances": {},
            "total_kusala_count": 10,
            "total_akusala_count": 5
        }
        
        result = await engine.simulate(
            scenario_id="marketplace_expensive",
            choice_id="market_001_kusala",
            current_state=current_state,
            model_id="test-001"
        )
        
        print(f"\n✅ Choice Made: {result.choice_made.label}")
        print(f"🧠 Citta: {result.citta_generated}")
        print(f"⚖️ Kamma: {result.kamma_generated}")
        
        print(f"\n⚡ Immediate Consequences:")
        for c in result.immediate_consequences:
            print(f"  {' '.join(c.visual_indicators)} {c.description}")
        
        print(f"\n📅 Short-term Consequences:")
        for c in result.short_term_consequences:
            print(f"  {' '.join(c.visual_indicators)} {c.description}")
        
        print(f"\n🔮 Long-term Consequences:")
        for c in result.long_term_consequences:
            print(f"  {' '.join(c.visual_indicators)} {c.description}")
        
        print(f"\n💡 Wisdom: {result.wisdom_gained}")
        print(f"🎯 Practice Tip: {result.practice_tip}")
        
        print(f"\n📊 State Changes:")
        print(f"  Before: Kusala={result.state_before['kusala_count']}, Akusala={result.state_before['akusala_count']}")
        print(f"  After:  Kusala={result.state_after['kusala_count']}, Akusala={result.state_after['akusala_count']}")
        print(f"  Virtue: Sila {result.state_before['virtue']['sila']:.2f} → {result.state_after['virtue']['sila']:.2f}")
    
    asyncio.run(test_simulation())
