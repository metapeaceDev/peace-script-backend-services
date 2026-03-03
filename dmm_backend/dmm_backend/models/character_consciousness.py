"""
Consciousness Model (จิต - จิตสำนึก)
Buddhist Psychology - Consciousness Factors

Based on STEP 3.1.1 - Internal Main Topics - Consciousness
ความระลึกรู้และความเข้าใจในธรรม (0-100)
"""

from pydantic import BaseModel, Field
from typing import Optional


class Consciousness(BaseModel):
    """
    Consciousness (จิต) - Mental/Spiritual Awareness
    
    ระดับจิตสำนึกตามหลักจิตวิทยาพุทธ
    ค่าคะแนน 0-100 (0 = ไม่มีเลย, 100 = สมบูรณ์แบบ)
    
    Based on STEP 3.1.1 Character Design
    """
    
    mindfulness: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="สติ (Mindfulness) - ความระลึกรู้, ความสงบ, ความตั้งมั่น"
    )
    
    wisdom: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="ปัญญา (Wisdom/Right View) - ความเข้าใจอนิจจัง, ความเห็นถูก, ความรู้แจ้ง"
    )
    
    faith: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="ศรัทธา (Faith) - ความเชื่อในความดี, ความเชื่อในธรรม, ความมั่นใจในทางที่ถูก"
    )
    
    hiri: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="หิริ (Hiri/Shame of sin) - ความละอายต่อบาป, ความละอายใจที่จะทำชั่ว"
    )
    
    karuna: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="กรุณา (Karuna/Compassion) - ความเมตตา, ความรู้ความทุกข์ของผู้อื่น, ความอยากช่วยเหลือ"
    )
    
    mudita: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="มุทิตา (Mudita/Joy in happiness) - ความยินดีในความสุขของผู้อื่น, ความเบิกบานใจ"
    )
    
    # Optional: Additional Notes
    notes: Optional[str] = Field(
        None,
        description="บันทึกเพิ่มเติมเกี่ยวกับจิตสำนึกของตัวละคร"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "mindfulness": 90.0,
                "wisdom": 85.0,
                "faith": 80.0,
                "hiri": 90.0,
                "karuna": 95.0,
                "mudita": 80.0,
                "notes": "มีความสงบและเข้าใจธรรมจากประสบการณ์ชีวิต สอนลูกด้วยแนวคิดธรรม"
            }
        }
    
    def get_consciousness_level(self) -> str:
        """
        Calculate overall consciousness level
        Returns: 'very_low' | 'low' | 'medium' | 'high' | 'very_high'
        """
        avg = (self.mindfulness + self.wisdom + self.faith + 
               self.hiri + self.karuna + self.mudita) / 6
        
        if avg >= 80:
            return "very_high"
        elif avg >= 60:
            return "high"
        elif avg >= 40:
            return "medium"
        elif avg >= 20:
            return "low"
        else:
            return "very_low"
    
    def get_spiritual_qualities(self) -> dict:
        """Get breakdown of spiritual qualities"""
        return {
            "mindfulness": self.mindfulness,
            "wisdom": self.wisdom,
            "faith": self.faith,
            "hiri": self.hiri,
            "karuna": self.karuna,
            "mudita": self.mudita,
            "average": (self.mindfulness + self.wisdom + self.faith + 
                       self.hiri + self.karuna + self.mudita) / 6,
            "level": self.get_consciousness_level()
        }
    
    def get_dominant_qualities(self, threshold: float = 70.0) -> list:
        """Get list of dominant consciousness qualities (above threshold)"""
        qualities = []
        
        if self.mindfulness >= threshold:
            qualities.append(("mindfulness", self.mindfulness))
        if self.wisdom >= threshold:
            qualities.append(("wisdom", self.wisdom))
        if self.faith >= threshold:
            qualities.append(("faith", self.faith))
        if self.hiri >= threshold:
            qualities.append(("hiri", self.hiri))
        if self.karuna >= threshold:
            qualities.append(("karuna", self.karuna))
        if self.mudita >= threshold:
            qualities.append(("mudita", self.mudita))
        
        # Sort by value descending
        qualities.sort(key=lambda x: x[1], reverse=True)
        
        return qualities


# Example: Koi's Father (Wichan Mahaphrom)
EXAMPLE_KOIS_FATHER_CONSCIOUSNESS = Consciousness(
    mindfulness=90.0,   # มีความสงบและเข้าใจธรรมจากชีวิต
    wisdom=85.0,        # เข้าใจอนิจจัง สอนลูกด้วยธรรม
    faith=80.0,         # เชื่อในความดีและการใช้ชีวิตแบบเรียบง่าย
    hiri=90.0,          # ไม่เคยทำความชั่ว
    karuna=95.0,        # รักและดูแลครอบครัวและศิษย์เสมอ
    mudita=80.0,        # มีความสุขกับความสำเร็จของลูกและผู้อื่น
    notes="พ่อของคอย - มีจิตสำนึกสูง เข้าใจธรรมะในระดับลึก ใช้ชีวิตด้วยความเรียบง่ายและเมตตา"
)
