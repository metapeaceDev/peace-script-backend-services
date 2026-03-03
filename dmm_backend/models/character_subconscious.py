"""
Subconscious Model (จิตใต้สำนึก)
Buddhist Psychology - Subconscious Factors

Based on STEP 3.1.1 - Subconscious
ความยึดติด (Attachment) และตัณหา (Taanha)
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class AttachmentType(str, Enum):
    """Types of attachment"""
    LOVE = "love"              # ความรัก
    DUTY = "duty"              # หน้าที่
    FEAR = "fear"              # ความกลัว
    HOPE = "hope"              # ความหวัง
    PRIDE = "pride"            # ความภูมิใจ
    POSSESSION = "possession"  # ความเป็นเจ้าของ
    IDENTITY = "identity"      # อัตลักษณ์
    BELIEF = "belief"          # ความเชื่อ
    MEMORY = "memory"          # ความทรงจำ
    OTHER = "other"            # อื่นๆ


class TaanhaCategory(str, Enum):
    """Categories of Taanha (craving)"""
    FORM = "form"              # รูป - External/Material desires
    EMOTION = "emotion"        # รส - Emotional/Feeling desires
    MIXED = "mixed"            # ผสมทั้งสองอย่าง


class Attachment(BaseModel):
    """
    Attachment (อุปาทาน) - Clinging/Attachment
    
    ความยึดติดที่มีต่อสิ่งต่างๆ
    Based on STEP 3.1.1 - Subconscious
    """
    
    description: str = Field(
        ...,
        description="รายละเอียดของความยึดติด (e.g., 'ความหวังที่จะสร้างชีวิตที่ดีให้ลูก')"
    )
    
    type: AttachmentType = Field(
        ...,
        description="ประเภทของความยึดติด"
    )
    
    intensity: float = Field(
        default=5.0,
        ge=0,
        le=10,
        description="ความรุนแรงของความยึดติด (0 = น้อยมาก, 10 = รุนแรงมาก)"
    )
    
    source: Optional[str] = Field(
        None,
        description="ที่มาของความยึดติด (e.g., 'จากความรักลูก', 'จากประสบการณ์ในอดีต')"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "description": "ความหวังที่จะสร้างชีวิตที่ดีให้ลูก",
                "type": "hope",
                "intensity": 9.5,
                "source": "จากความรักและความปรารถนาดีต่อลูก"
            }
        }


class Taanha(BaseModel):
    """
    Taanha (ตัณหา) - Craving/Desire
    
    ความทะยานอยาก แบ่งเป็น 2 ประเภท:
    1. Wanting (สิ่งที่อยากได้/อยากให้เกิด)
    2. Unwanted (สิ่งที่ไม่อยากให้เกิด/อยากหลีกเลี่ยง)
    
    Based on STEP 3.1.1 - Subconscious
    """
    
    category: TaanhaCategory = Field(
        ...,
        description="ประเภทของตัณหา - form (รูป) | emotion (รส) | mixed"
    )
    
    wanting: List[str] = Field(
        default_factory=list,
        description="สิ่งที่อยากได้/อยากให้เกิด"
    )
    
    unwanted: List[str] = Field(
        default_factory=list,
        description="สิ่งที่ไม่อยากให้เกิด/อยากหลีกเลี่ยง"
    )
    
    notes: Optional[str] = Field(
        None,
        description="บันทึกเพิ่มเติมเกี่ยวกับตัณหา"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "category": "mixed",
                "wanting": [
                    "เห็นลูกสำเร็จในชีวิต",
                    "ให้ครอบครัวมีความสุข",
                    "ได้เห็นลูกแต่งงาน"
                ],
                "unwanted": [
                    "ลูกต้องทุกข์เหมือนตน",
                    "เห็นครอบครัวเจ็บปวด",
                    "ลูกต้องล้มเหลว"
                ],
                "notes": "ตัณหาหลักมาจากความรักและความห่วงใยครอบครัว"
            }
        }
    
    def get_wanting_count(self) -> int:
        """Count of wanting items"""
        return len(self.wanting)
    
    def get_unwanted_count(self) -> int:
        """Count of unwanted items"""
        return len(self.unwanted)
    
    def get_total_desires(self) -> int:
        """Total count of all desires"""
        return len(self.wanting) + len(self.unwanted)


# Example: Koi's Father (Wichan Mahaphrom)
EXAMPLE_KOIS_FATHER_ATTACHMENTS = [
    Attachment(
        description="ความหวังที่จะสร้างชีวิตที่ดีให้ลูก",
        type=AttachmentType.HOPE,
        intensity=9.5,
        source="จากความรักและความปรารถนาดีต่อลูก"
    ),
    Attachment(
        description="ภาระหน้าที่ในฐานะครูมวย",
        type=AttachmentType.DUTY,
        intensity=8.0,
        source="จากความรับผิดชอบต่อลูกศิษย์และประเพณีมวยโบราณ"
    )
]

EXAMPLE_KOIS_FATHER_TAANHA = Taanha(
    category=TaanhaCategory.MIXED,
    wanting=[
        "เห็นลูกสำเร็จในชีวิต",
        "ให้ครอบครัวมีความสุข",
        "ได้เห็นลูกแต่งงานและมีครอบครัว",
        "ส่งต่อภูมิปัญญามวยโบราณ"
    ],
    unwanted=[
        "ลูกต้องทุกข์เหมือนตน",
        "เห็นครอบครัวเจ็บปวด",
        "ลูกต้องล้มเหลวในชีวิต",
        "ครอบครัวต้องเผชิญปัญหาทางการเงิน"
    ],
    notes="ตัณหาหลักมาจากความรักและความห่วงใยครอบครัว แม้ว่าตัวเองจะป่วยหนักก็ยังคงห่วงใยลูก"
)
