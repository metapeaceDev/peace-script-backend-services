"""
Social Status Model (ข้อมูลสถานะทางสังคม)
Character Background Information

Based on STEP 3.1.1 - Social Status Information
ข้อมูลพื้นฐานและสถานะทางสังคมของตัวละคร
"""

from pydantic import BaseModel, Field
from typing import Optional


class SocialStatus(BaseModel):
    """
    Social Status (ข้อมูลสถานะทางสังคม)
    
    ข้อมูลพื้นฐานและสถานะทางสังคมของตัวละคร
    Based on STEP 3.1.1 - Social Status Information
    """
    
    last_name: Optional[str] = Field(
        None,
        description="นามสกุล (e.g., 'Wichan Mahaphrom')"
    )
    
    nickname: Optional[str] = Field(
        None,
        description="ชื่อเล่น (e.g., 'Wich')"
    )
    
    alias: Optional[str] = Field(
        None,
        description="นามแฝง/ฉายา (e.g., 'Korat Boxing Teacher Mud Arahat')"
    )
    
    date_of_birth: Optional[str] = Field(
        None,
        description="วันเกิด (YYYY-MM-DD format) (e.g., '1965-03-12')"
    )
    
    address: Optional[str] = Field(
        None,
        description="ที่อยู่ (e.g., 'Pak Chong District, Nakhon Ratchasima Province')"
    )
    
    relationship_status: Optional[str] = Field(
        None,
        description="สถานะความสัมพันธ์ (e.g., 'Married, father of Koi')"
    )
    
    nationality: Optional[str] = Field(
        None,
        description="สัญชาติ (e.g., 'Thai')"
    )
    
    religion: Optional[str] = Field(
        None,
        description="ศาสนา (e.g., 'Buddhist')"
    )
    
    blood_type: Optional[str] = Field(
        None,
        description="หมู่เลือด (e.g., 'O', 'A', 'B', 'AB')"
    )
    
    education: Optional[str] = Field(
        None,
        description="การศึกษา (e.g., 'Lower secondary (M.3) + Boxing training from ancient boxing master')"
    )
    
    financial_status: Optional[str] = Field(
        None,
        description="สถานะทางการเงิน (e.g., 'Enough to eat but medical expenses burden')"
    )
    
    occupation: Optional[str] = Field(
        None,
        description="อาชีพ (e.g., 'Boxing teacher and former boxer')"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "last_name": "Wichan Mahaphrom",
                "nickname": "Wich",
                "alias": "Korat Boxing Teacher 'Mud Arahat'",
                "date_of_birth": "1965-03-12",
                "address": "A house in the countryside, Pak Chong District, Nakhon Ratchasima Province",
                "relationship_status": "Married, Koi's father, respected in boxing circle",
                "nationality": "Thai",
                "religion": "Buddhist",
                "blood_type": "O",
                "education": "Lower secondary (M.3) in rural school + Boxing training from ancient boxing master",
                "financial_status": "Enough to eat, but faced financial problems from medical expenses in later years",
                "occupation": "Boxing teacher and boxer who made a name in the past"
            }
        }
    
    def get_age(self) -> Optional[int]:
        """Calculate age from date of birth (if provided)"""
        if not self.date_of_birth:
            return None
        
        from datetime import datetime
        try:
            birth_date = datetime.strptime(self.date_of_birth, "%Y-%m-%d")
            today = datetime.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            return age
        except:
            return None
    
    def get_full_identity(self) -> str:
        """Get full identity string"""
        parts = []
        
        if self.last_name:
            parts.append(self.last_name)
        if self.nickname:
            parts.append(f"({self.nickname})")
        if self.alias:
            parts.append(f"a.k.a. {self.alias}")
        
        return " ".join(parts) if parts else "Unknown"
    
    def is_complete(self) -> bool:
        """Check if all critical fields are filled"""
        critical_fields = [
            self.last_name,
            self.date_of_birth,
            self.occupation
        ]
        return all(field is not None for field in critical_fields)


# Example: Koi's Father (Wichan Mahaphrom)
EXAMPLE_KOIS_FATHER_SOCIAL_STATUS = SocialStatus(
    last_name="Wichan Mahaphrom",
    nickname="Wich",
    alias="Korat Boxing Teacher 'Mud Arahat'",
    date_of_birth="1965-03-12",
    address="A house in the countryside, Pak Chong District, Nakhon Ratchasima Province",
    relationship_status="Married, Koi's father, mother's husband, respected in boxing circle",
    nationality="Thai",
    religion="Buddhist",
    blood_type="O",
    education="Graduated from lower secondary school (M.3) in a rural school, but received boxing training from an ancient boxing teacher",
    financial_status="Had enough to eat, but faced financial problems from medical expenses in later years",
    occupation="Boxing teacher and boxer who made a name in the past"
)
