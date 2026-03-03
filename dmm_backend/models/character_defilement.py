"""
Defilement Model (กิเลส - Mental Defilements)
Buddhist Psychology - Ten Mental Defilements

Based on STEP 3.1.1 - Defilement (Value 0-100)
กิเลสที่เป็นมลทินของจิต (0-100)
"""

from pydantic import BaseModel, Field
from typing import Optional


class Defilement(BaseModel):
    """
    Defilement (กิเลส) - Mental Defilements/Impurities
    
    ระดับกิเลสต่างๆ ตามหลักจิตวิทยาพุทธ
    ค่าคะแนน 0-100 (0 = ไม่มีเลย, 100 = รุนแรงมาก)
    
    Based on STEP 3.1.1 Character Design
    ยิ่งคะแนนสูง = กิเลสยิ่งรุนแรง
    """
    
    lobha: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="โลภะ (Lobha/Greed) - ความโลภ, ความทะยานอยาก, ความอยากได้"
    )
    
    dosa: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="โทสะ (Dosa/Anger) - ความโกรธ, ความขุ่นเคือง, ความเกลียดชัง"
    )
    
    moha: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="โมหะ (Moha/Delusion) - ความหลง, ความงมงาย, ความไม่รู้"
    )
    
    mana: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="มานะ (Mana/Arrogance) - ความถือตัว, ความทะนง, ความภูมิใจเกินควร"
    )
    
    ditthi: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="ทิฏฐิ (Ditthi/Wrong View) - ความยึดมั่นผิด, ความคิดดื้อด้าน, ความเห็นผิด"
    )
    
    vicikiccha: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="วิจิกิจฉา (Vicikiccha/Doubt) - ความสงสัยลังเล, ความไม่แน่ใจ"
    )
    
    thina: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="ถีนะ (Thina/Sloth) - ความซบเซา, ความท้อแท้, ความหดหู่"
    )
    
    uddhacca: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="อุทธัจจะ (Uddhacca/Restlessness) - ความฟุ้งซ่าน, ความกระวนกระวาย, จิตไม่สงบ"
    )
    
    ahirika: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="อหิริกะ (Ahirika/Shamelessness) - ความไม่ละอาย, ความไม่เกรงกลัวต่อบาป"
    )
    
    anottappa: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="อโนตตัปปะ (Anottappa/Fearlessness of evil) - ความไม่กลัวบาป, ความไม่เกรงกลัวต่อผลของกรรม"
    )
    
    # Optional: Additional Notes
    notes: Optional[str] = Field(
        None,
        description="บันทึกเพิ่มเติมเกี่ยวกับกิเลสของตัวละคร"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "lobha": 20.0,
                "dosa": 30.0,
                "moha": 50.0,
                "mana": 40.0,
                "ditthi": 45.0,
                "vicikiccha": 20.0,
                "thina": 35.0,
                "uddhacca": 20.0,
                "ahirika": 10.0,
                "anottappa": 10.0,
                "notes": "มีกิเลสต่ำในด้านความโลภและความโกรธ แต่มีความหลงในเรื่องการแบกภาระคนเดียว"
            }
        }
    
    def get_defilement_level(self) -> str:
        """
        Calculate overall defilement level
        Returns: 'very_low' | 'low' | 'medium' | 'high' | 'very_high'
        """
        avg = (self.lobha + self.dosa + self.moha + self.mana + self.ditthi + 
               self.vicikiccha + self.thina + self.uddhacca + self.ahirika + self.anottappa) / 10
        
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
    
    def get_defilement_breakdown(self) -> dict:
        """Get breakdown of all defilements"""
        return {
            "lobha": self.lobha,
            "dosa": self.dosa,
            "moha": self.moha,
            "mana": self.mana,
            "ditthi": self.ditthi,
            "vicikiccha": self.vicikiccha,
            "thina": self.thina,
            "uddhacca": self.uddhacca,
            "ahirika": self.ahirika,
            "anottappa": self.anottappa,
            "average": (self.lobha + self.dosa + self.moha + self.mana + self.ditthi + 
                       self.vicikiccha + self.thina + self.uddhacca + self.ahirika + self.anottappa) / 10,
            "level": self.get_defilement_level()
        }
    
    def get_dominant_defilements(self, threshold: float = 60.0) -> list:
        """Get list of dominant defilements (above threshold)"""
        defilements = []
        
        if self.lobha >= threshold:
            defilements.append(("lobha", self.lobha))
        if self.dosa >= threshold:
            defilements.append(("dosa", self.dosa))
        if self.moha >= threshold:
            defilements.append(("moha", self.moha))
        if self.mana >= threshold:
            defilements.append(("mana", self.mana))
        if self.ditthi >= threshold:
            defilements.append(("ditthi", self.ditthi))
        if self.vicikiccha >= threshold:
            defilements.append(("vicikiccha", self.vicikiccha))
        if self.thina >= threshold:
            defilements.append(("thina", self.thina))
        if self.uddhacca >= threshold:
            defilements.append(("uddhacca", self.uddhacca))
        if self.ahirika >= threshold:
            defilements.append(("ahirika", self.ahirika))
        if self.anottappa >= threshold:
            defilements.append(("anottappa", self.anottappa))
        
        # Sort by value descending
        defilements.sort(key=lambda x: x[1], reverse=True)
        
        return defilements
    
    def get_primary_defilement(self) -> tuple:
        """Get the most dominant defilement"""
        all_defilements = [
            ("lobha", self.lobha),
            ("dosa", self.dosa),
            ("moha", self.moha),
            ("mana", self.mana),
            ("ditthi", self.ditthi),
            ("vicikiccha", self.vicikiccha),
            ("thina", self.thina),
            ("uddhacca", self.uddhacca),
            ("ahirika", self.ahirika),
            ("anottappa", self.anottappa)
        ]
        
        return max(all_defilements, key=lambda x: x[1])
    
    def is_virtuous(self, threshold: float = 30.0) -> bool:
        """
        Check if character is generally virtuous (all defilements below threshold)
        """
        avg = (self.lobha + self.dosa + self.moha + self.mana + self.ditthi + 
               self.vicikiccha + self.thina + self.uddhacca + self.ahirika + self.anottappa) / 10
        return avg < threshold


# Example: Koi's Father (Wichan Mahaphrom)
EXAMPLE_KOIS_FATHER_DEFILEMENT = Defilement(
    lobha=20.0,         # แทบไม่มีความโลภ ยอมเสียสละเพื่อครอบครัว
    dosa=30.0,          # โกรธน้อย แต่จะโกรธเมื่อคนรักถูกทำร้าย
    moha=50.0,          # หลงคิดว่าแบกภาระคนเดียวจะช่วยครอบครัว
    mana=40.0,          # ภูมิใจที่เป็นครูมวย แต่ไม่โอ้อวด
    ditthi=45.0,        # ยึดติดกับหน้าที่จนลืมดูแลสุขภาพตัวเอง
    vicikiccha=20.0,    # เข้าใจชีวิตในระดับสงบ
    thina=35.0,         # เคยท้อแท้เมื่อครอบครัวประสบปัญหา
    uddhacca=20.0,      # ควบคุมจิตได้ดี
    ahirika=10.0,       # แทบไม่มี
    anottappa=10.0,     # แทบไม่มี
    notes="พ่อของคอย - มีกิเลสต่ำโดยรวม โดยเฉพาะความโลภและความโกรธ แต่มีความหลงในเรื่องการรับภาระคนเดียว"
)
