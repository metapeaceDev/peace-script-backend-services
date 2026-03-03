"""
🏥 Health History Models

ระบบประวัติสุขภาพครอบคลุม (Comprehensive Health History System)
เพิ่มเติมจาก ExternalCharacter (fitness_level, health_status, scars_wounds)

Author: Peace Script Model
Date: 6 พฤศจิกายน 2568
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class HealthCondition(BaseModel):
    """
    โรค/สภาวะสุขภาพ (Health Condition)
    
    ใช้บันทึกโรคประจำตัวหรือโรคเรื้อรัง
    """
    name: str = Field(..., description="ชื่อโรค/สภาวะสุขภาพ")
    severity: str = Field(
        default="mild",
        description="ความรุนแรง: mild, moderate, severe, critical"
    )
    diagnosed_date: Optional[str] = Field(None, description="วันที่วินิจฉัย (YYYY-MM-DD)")
    status: str = Field(
        default="active",
        description="สถานะ: active, managed, cured, chronic"
    )
    notes: Optional[str] = Field(None, description="หมายเหตุเพิ่มเติม")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "โรคหัวใจ (Heart Disease)",
                "severity": "moderate",
                "diagnosed_date": "2015-01-15",
                "status": "managed",
                "notes": "จากการฝึกมวยหนักและบาดเจ็บสะสม"
            }
        }


class Injury(BaseModel):
    """
    อุบัติเหตุ/การบาดเจ็บ (Injury/Accident)
    
    บันทึกประวัติการบาดเจ็บในอดีต
    """
    type: str = Field(..., description="ประเภท: fracture, laceration, burn, sprain, etc.")
    location: str = Field(..., description="ตำแหน่งบาดเจ็บ")
    date: Optional[str] = Field(None, description="วันที่เกิดเหตุ (YYYY-MM-DD)")
    cause: Optional[str] = Field(None, description="สาเหตุ")
    treatment: Optional[str] = Field(None, description="การรักษา")
    healed: bool = Field(default=True, description="หายแล้วหรือไม่")
    permanent_effect: Optional[str] = Field(None, description="ผลกระทบถาวร (ถ้ามี)")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "fracture",
                "location": "ซี่โครงซ้าย",
                "date": "2010-05-20",
                "cause": "การต่อสู้ในสังเวียน",
                "treatment": "พักรักษา 6 สัปดาห์",
                "healed": True,
                "permanent_effect": "ปวดเมื่ออากาศเย็น"
            }
        }


class Surgery(BaseModel):
    """
    การผ่าตัด (Surgery)
    
    ประวัติการผ่าตัดทั้งหมด
    """
    procedure: str = Field(..., description="ชื่อการผ่าตัด/ขั้นตอน")
    date: Optional[str] = Field(None, description="วันที่ผ่าตัด (YYYY-MM-DD)")
    reason: str = Field(..., description="เหตุผลการผ่าตัด")
    hospital: Optional[str] = Field(None, description="โรงพยาบาล/สถานพยาบาล")
    outcome: str = Field(
        default="successful",
        description="ผลลัพธ์: successful, complicated, partial_success, failed"
    )
    notes: Optional[str] = Field(None, description="หมายเหตุเพิ่มเติม")

    class Config:
        json_schema_extra = {
            "example": {
                "procedure": "ผ่าตัดเข่าขวา (Right knee surgery)",
                "date": "2012-08-15",
                "reason": "กระดูกอ่อนสึก",
                "hospital": "โรงพยาบาลโคราช",
                "outcome": "successful",
                "notes": "ฟื้นตัวเต็มที่ใช้เวลา 1 ปี"
            }
        }


class Medication(BaseModel):
    """
    ยาที่ใช้ประจำ (Current Medication)
    
    ยาที่ตัวละครใช้อยู่ในปัจจุบัน
    """
    name: str = Field(..., description="ชื่อยา")
    dosage: str = Field(..., description="ขนาดยา (เช่น 5mg, 10ml)")
    frequency: str = Field(..., description="ความถี่ (once daily, twice daily, etc.)")
    purpose: str = Field(..., description="วัตถุประสงค์การใช้ยา")
    started_date: Optional[str] = Field(None, description="เริ่มใช้เมื่อไร (YYYY-MM-DD)")
    side_effects: List[str] = Field(default_factory=list, description="ผลข้างเคียงที่พบ")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "ยาลดความดันโลหิต",
                "dosage": "5mg",
                "frequency": "once daily",
                "purpose": "ควบคุมความดันโลหิต",
                "started_date": "2015-02-01",
                "side_effects": ["วิงเวียนเล็กน้อย"]
            }
        }


class Allergy(BaseModel):
    """
    การแพ้ (Allergy)
    
    ประวัติการแพ้ต่างๆ
    """
    allergen: str = Field(..., description="สิ่งที่แพ้")
    type: str = Field(..., description="ประเภท: food, drug, environmental, animal, etc.")
    severity: str = Field(
        default="mild",
        description="ความรุนแรง: mild, moderate, severe, anaphylactic"
    )
    symptoms: List[str] = Field(default_factory=list, description="อาการที่เกิดขึ้น")
    discovered_date: Optional[str] = Field(None, description="ค้นพบเมื่อไร (YYYY-MM-DD)")

    class Config:
        json_schema_extra = {
            "example": {
                "allergen": "penicillin",
                "type": "drug",
                "severity": "moderate",
                "symptoms": ["ผื่นคัน", "บวม"],
                "discovered_date": "2005-06-10"
            }
        }


class Disability(BaseModel):
    """
    พิการ/ความบกพร่อง (Disability)
    
    พิการหรือความบกพร่องทางร่างกายหรือจิตใจ
    """
    type: str = Field(..., description="ประเภท: physical, sensory, cognitive, mental, etc.")
    description: str = Field(..., description="รายละเอียดความพิการ")
    cause: str = Field(..., description="สาเหตุ: birth, accident, disease, aging, etc.")
    severity: str = Field(
        default="mild",
        description="ความรุนแรง: mild, moderate, severe, profound"
    )
    assistance_needed: List[str] = Field(
        default_factory=list,
        description="ความช่วยเหลือที่ต้องการ"
    )
    adaptive_equipment: List[str] = Field(
        default_factory=list,
        description="อุปกรณ์ช่วยเหลือ (wheelchair, cane, hearing aid, etc.)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "type": "sensory",
                "description": "สายตาสั้นรุนแรง",
                "cause": "birth",
                "severity": "moderate",
                "assistance_needed": ["แว่นตา"],
                "adaptive_equipment": ["แว่นตาสายตาสั้น -6.0"]
            }
        }


class MentalHealthHistory(BaseModel):
    """
    ประวัติสุขภาพจิต (Mental Health History)
    
    ประวัติด้านสุขภาพจิต
    """
    conditions: List[str] = Field(
        default_factory=list,
        description="โรค/ภาวะทางจิตเวช (depression, anxiety, PTSD, etc.)"
    )
    therapy: bool = Field(default=False, description="รับการบำบัดหรือไม่")
    medications: List[str] = Field(
        default_factory=list,
        description="ยาที่ใช้ทางจิตเวช"
    )
    support_system: Optional[str] = Field(None, description="ระบบสนับสนุน (ครอบครัว, เพื่อน, กลุ่มช่วยเหลือ)")
    notes: Optional[str] = Field(None, description="หมายเหตุเพิ่มเติม")

    class Config:
        json_schema_extra = {
            "example": {
                "conditions": [],
                "therapy": False,
                "medications": [],
                "support_system": "ครอบครัวและศิษย์",
                "notes": "มีจิตใจเข้มแข็ง มีสติสงบ"
            }
        }


class HealthHistory(BaseModel):
    """
    ประวัติสุขภาพครอบคลุม (Comprehensive Health History)
    
    เพิ่มเติมข้อมูลจาก ExternalCharacter:
    - fitness_level (ระดับสมรรถภาพโดยรวม)
    - health_status (สถานะปัจจุบัน: healthy, chronic_illness, disability)
    - scars_wounds (แผลเป็น/บาดแผลที่มองเห็น)
    
    HealthHistory เก็บข้อมูลเชิงลึกทางการแพทย์และประวัติสุขภาพ
    """
    
    # === โรคประจำตัว/โรคเรื้อรัง (Chronic Conditions) ===
    chronic_conditions: List[HealthCondition] = Field(
        default_factory=list,
        description="โรคประจำตัว/โรคเรื้อรัง"
    )
    
    # === อุบัติเหตุในอดีต (Past Injuries) ===
    past_injuries: List[Injury] = Field(
        default_factory=list,
        description="ประวัติการบาดเจ็บ/อุบัติเหตุ"
    )
    
    # === การผ่าตัด (Surgeries) ===
    surgeries: List[Surgery] = Field(
        default_factory=list,
        description="ประวัติการผ่าตัด"
    )
    
    # === ยาที่ใช้ปัจจุบัน (Current Medications) ===
    current_medications: List[Medication] = Field(
        default_factory=list,
        description="ยาที่ใช้ประจำ"
    )
    
    # === การแพ้ (Allergies) ===
    allergies: List[Allergy] = Field(
        default_factory=list,
        description="ประวัติการแพ้"
    )
    
    # === พิการ/ความบกพร่อง (Disabilities) ===
    disabilities: List[Disability] = Field(
        default_factory=list,
        description="พิการ/ความบกพร่อง"
    )
    
    # === สุขภาพจิต (Mental Health) ===
    mental_health: Optional[MentalHealthHistory] = Field(
        None,
        description="ประวัติสุขภาพจิต"
    )
    
    # === ประวัติครอบครัว (Family History) ===
    family_history: List[str] = Field(
        default_factory=list,
        description="โรคทางพันธุกรรม/ประวัติโรคในครอบครัว"
    )
    
    # === Lifestyle Factors (ปัจจัยด้านไลฟ์สไตล์) ===
    smoking: bool = Field(
        default=False,
        description="สูบบุหรี่หรือไม่"
    )
    alcohol_use: str = Field(
        default="none",
        description="การดื่มเครื่องดื่มแอลกอฮอล์: none, social, moderate, heavy"
    )
    drug_use: bool = Field(
        default=False,
        description="เสพสารเสพติดหรือไม่"
    )
    exercise_frequency: str = Field(
        default="moderate",
        description="ความถี่ในการออกกำลังกาย: none, light, moderate, high, intense"
    )
    diet_type: Optional[str] = Field(
        None,
        description="รูปแบบการกินอาหาร: normal, vegetarian, vegan, halal, kosher, etc."
    )
    
    # === หมู่เลือด (Blood Type) ===
    blood_type: Optional[str] = Field(
        None,
        description="หมู่เลือด (A+, A-, B+, B-, AB+, AB-, O+, O-)"
    )
    
    # === การฉีดวัคซีน (Vaccinations) ===
    vaccinations: List[str] = Field(
        default_factory=list,
        description="ประวัติการฉีดวัคซีน"
    )
    
    # === บันทึกทางการแพทย์ (Medical Notes) ===
    medical_notes: Optional[str] = Field(
        None,
        description="บันทึกทางการแพทย์เพิ่มเติม"
    )
    
    # === ตรวจสุขภาพครั้งล่าสุด (Last Checkup) ===
    last_checkup_date: Optional[str] = Field(
        None,
        description="วันที่ตรวจสุขภาพครั้งล่าสุด (YYYY-MM-DD)"
    )
    last_checkup_notes: Optional[str] = Field(
        None,
        description="ผลการตรวจสุขภาพ/หมายเหตุ"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "chronic_conditions": [
                    {
                        "name": "โรคหัวใจ",
                        "severity": "moderate",
                        "diagnosed_date": "2015-01-15",
                        "status": "managed",
                        "notes": "จากการฝึกมวยหนักและบาดเจ็บสะสม"
                    }
                ],
                "past_injuries": [
                    {
                        "type": "fracture",
                        "location": "ซี่โครงซ้าย",
                        "date": "2010-05-20",
                        "cause": "การต่อสู้ในสังเวียน",
                        "treatment": "พักรักษา 6 สัปดาห์",
                        "healed": True,
                        "permanent_effect": "ปวดเมื่ออากาศเย็น"
                    }
                ],
                "surgeries": [
                    {
                        "procedure": "ผ่าตัดเข่าขวา",
                        "date": "2012-08-15",
                        "reason": "กระดูกอ่อนสึก",
                        "hospital": "โรงพยาบาลโคราช",
                        "outcome": "successful",
                        "notes": "ฟื้นตัวเต็มที่ใช้เวลา 1 ปี"
                    }
                ],
                "current_medications": [
                    {
                        "name": "ยาลดความดันโลหิต",
                        "dosage": "5mg",
                        "frequency": "once daily",
                        "purpose": "ควบคุมความดันโลหิต",
                        "started_date": "2015-02-01",
                        "side_effects": ["วิงเวียนเล็กน้อย"]
                    }
                ],
                "allergies": [
                    {
                        "allergen": "penicillin",
                        "type": "drug",
                        "severity": "moderate",
                        "symptoms": ["ผื่นคัน", "บวม"],
                        "discovered_date": "2005-06-10"
                    }
                ],
                "disabilities": [],
                "mental_health": {
                    "conditions": [],
                    "therapy": False,
                    "medications": [],
                    "support_system": "ครอบครัวและศิษย์",
                    "notes": "มีจิตใจเข้มแข็ง มีสติสงบ"
                },
                "family_history": [
                    "โรคหัวใจในครอบครัว (พ่อเสียชีวิตด้วยโรคหัวใจ)",
                    "โรคความดันโลหิตสูง (แม่)"
                ],
                "smoking": False,
                "alcohol_use": "social",
                "drug_use": False,
                "exercise_frequency": "high",
                "diet_type": "normal",
                "blood_type": "O+",
                "vaccinations": ["COVID-19", "Influenza", "Tetanus"],
                "medical_notes": "ผู้ป่วยมีพื้นฐานสุขภาพแข็งแรงในวัยหนุ่ม แต่มีปัญหาจากการบาดเจ็บสะสม",
                "last_checkup_date": "2020-01-10",
                "last_checkup_notes": "ระดับคอเลสเตอรอลสูง, แนะนำลดอาหารมัน"
            }
        }
