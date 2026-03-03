"""
Rebirth Toolkit Router
=======================
API endpoints for Rebirth Toolkit features.

Optional helper tools for cross-lifetime character creation.
NOT a full automatic Samsara Cycle.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict
from pydantic import BaseModel, Field

from modules.rebirth_toolkit import (
    THIRTY_ONE_REALMS,
    get_realm_by_id,
    get_realms_by_category,
    RealmCategory,
    RebirthCalculator,
    RebirthTemplate,
    RebirthTemplateGenerator,
)


router = APIRouter(
    prefix="/api/rebirth-toolkit",
    tags=["Rebirth Toolkit"],
    responses={404: {"description": "Not found"}},
)


# ========================================
# REQUEST/RESPONSE MODELS
# ========================================

class RealmResponse(BaseModel):
    """Response model for realm data"""
    id: int
    name_en: str
    name_th: str
    name_pali: str
    category: str
    category_name_th: str
    lifespan_years: int
    suffering_level: int
    happiness_level: int
    description_th: str
    description_en: str
    buddhist_reference: str
    kamma_score_range: Dict[str, float]


class CreateTemplateRequest(BaseModel):
    """Request model for creating rebirth template"""
    previous_character_id: str = Field(..., description="Previous character ID")
    enable_memories: bool = Field(default=False, description="Enable past life memories?")
    karmic_debt: float = Field(default=0.0, ge=0, le=100, description="Karmic debt 0-100")
    educational_mode: bool = Field(default=False, description="Educational mode?")


# ========================================
# ENDPOINTS: 31 REALMS REFERENCE
# ========================================

@router.get("/realms", response_model=List[RealmResponse])
async def get_all_realms():
    """
    Get all 31 realms of existence
    
    Educational reference for Buddhist cosmology.
    """
    return [
        RealmResponse(
            id=realm.id,
            name_en=realm.name_en,
            name_th=realm.name_th,
            name_pali=realm.name_pali,
            category=realm.category.value,
            category_name_th=realm.category_name_th,
            lifespan_years=realm.lifespan_years,
            suffering_level=realm.suffering_level,
            happiness_level=realm.happiness_level,
            description_th=realm.description_th,
            description_en=realm.description_en,
            buddhist_reference=realm.buddhist_reference,
            kamma_score_range={
                "min": realm.min_kamma_score,
                "max": realm.max_kamma_score
            }
        )
        for realm in THIRTY_ONE_REALMS
    ]


@router.get("/realms/{realm_id}", response_model=RealmResponse)
async def get_realm_detail(realm_id: int):
    """
    Get detailed information about specific realm
    
    Args:
        realm_id: Realm ID (1-31)
    """
    realm = get_realm_by_id(realm_id)
    
    if not realm:
        raise HTTPException(status_code=404, detail=f"Realm {realm_id} not found")
    
    return RealmResponse(
        id=realm.id,
        name_en=realm.name_en,
        name_th=realm.name_th,
        name_pali=realm.name_pali,
        category=realm.category.value,
        category_name_th=realm.category_name_th,
        lifespan_years=realm.lifespan_years,
        suffering_level=realm.suffering_level,
        happiness_level=realm.happiness_level,
        description_th=realm.description_th,
        description_en=realm.description_en,
        buddhist_reference=realm.buddhist_reference,
        kamma_score_range={
            "min": realm.min_kamma_score,
            "max": realm.max_kamma_score
        }
    )


@router.get("/realms/category/{category}")
async def get_realms_by_category_endpoint(category: str):
    """
    Get all realms in a category
    
    Categories:
    - apaya_bhumi: Suffering Realms (1-4)
    - kama_sugati: Happy Sensual Realms (5-12)
    - rupa_brahma: Fine-Material Realms (13-28)
    - arupa_brahma: Formless Realms (29-31)
    """
    try:
        realm_category = RealmCategory(category)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {[c.value for c in RealmCategory]}"
        )
    
    realms = get_realms_by_category(realm_category)
    
    return {
        "category": category,
        "count": len(realms),
        "realms": [
            {
                "id": realm.id,
                "name_th": realm.name_th,
                "name_en": realm.name_en,
                "suffering_level": realm.suffering_level,
                "happiness_level": realm.happiness_level,
            }
            for realm in realms
        ]
    }


# ========================================
# ENDPOINTS: REBIRTH CALCULATOR
# ========================================

@router.post("/calculate-kamma")
async def calculate_kamma_score(kamma_ledger: Dict):
    """
    Calculate total kamma score from kamma ledger
    
    Request body:
    {
        "dana": {"count": 10, "average_intensity": 50},
        "metta": {"count": 5},
        "panatipata": {"count": 2, "severity": 1.5},
        ...
    }
    
    Returns kamma score breakdown
    """
    calculator = RebirthCalculator()
    result = calculator.calculate_kamma_score(kamma_ledger)
    
    return {
        "success": True,
        "kamma_analysis": result,
        "disclaimer": "⚠️ นี่เป็นการคำนวณเพื่อการศึกษาเท่านั้น"
    }


@router.get("/suggest-realm/{character_id}")
async def suggest_rebirth_realm(
    character_id: str,
    top_n: int = Query(default=5, ge=1, le=10)
):
    """
    Suggest probable rebirth realms based on character's kamma
    
    ⚠️ ADVISORY ONLY - Creator makes final decision
    
    Args:
        character_id: Character ID to analyze
        top_n: Number of top suggestions (1-10)
    
    Returns:
        Top N realm suggestions with probability
        
    Implementation: Ready for MongoDB integration
    Uses mock data until Character/Kamma documents are linked
    """
    if not character_id:
        raise HTTPException(status_code=400, detail="Character ID required")
    
    # Future MongoDB integration (when Character model has kamma_ledger):
    # try:
    #     from documents_character import Character
    #     character = await Character.find_one({"character_id": character_id})
    #     if not character:
    #         raise HTTPException(status_code=404, detail="Character not found")
    #     kamma_ledger = character.kamma_ledger or {}
    # except Exception as e:
    #     # Fallback to mock data if not integrated yet
    #     kamma_ledger = None
    
    # Mock kamma ledger for testing (replace with MongoDB query above)
    mock_kamma = {
        "dana": {"count": 5, "average_intensity": 70},
        "sila": {"count": 3},
        "samadhi": {"count": 2},
        "metta": {"count": 4}
    }
    
    # Calculate suggestions
    calculator = RebirthCalculator()
    suggestions = calculator.suggest_rebirth_realms(
        mock_kamma,
        top_n=top_n
    )
    
    return {
        "success": True,
        "character_id": character_id,
        "character_name": f"Mock Character {character_id}",
        "current_life_summary": {
            "realm": "มนุษย์ (Manussā)",
            "age": 30,
            "kamma_summary": "Mock kamma for testing"
        },
        "rebirth_suggestions": suggestions,
        "disclaimer": "⚠️ นี่เป็นคำแนะนำเท่านั้น Creator ตัดสินใจเองได้เสมอ",
        "note": "Peace Script ไม่มีระบบตายเกิดอัตโนมัติ นี่เป็นเครื่องมือช่วยเท่านั้น",
        "warning": "⚠️ Mock data - connect to MongoDB for real character data"
    }


@router.get("/explain-kamma/{character_id}")
async def explain_kamma_impact(
    character_id: str
):
    """
    Explain how character's kamma impacts rebirth
    
    Educational feature to understand Buddhist cosmology
    
    Implementation: Ready for MongoDB integration
    Uses mock data until Character/Kamma documents are linked
    """
    if not character_id:
        raise HTTPException(status_code=400, detail="Character ID required")
    
    # Future MongoDB integration:
    # try:
    #     from documents_character import Character
    #     character = await Character.find_one({"character_id": character_id})
    #     if not character:
    #         raise HTTPException(status_code=404, detail="Character not found")
    #     kamma_ledger = character.kamma_ledger or {}
    # except Exception:
    #     kamma_ledger = None
    
    # Mock kamma ledger for testing (replace with MongoDB query above)
    mock_kamma = {
        "dana": {"count": 5},
        "sila": {"count": 3},
        "samadhi": {"count": 2}
    }
    
    # Get explanation
    calculator = RebirthCalculator()
    explanation = calculator.explain_kamma_impact(mock_kamma)
    
    return {
        "success": True,
        "character_id": character_id,
        "character_name": f"Mock Character {character_id}",
        "kamma_explanation": explanation,
        "educational_note": "ข้อมูลนี้ใช้สำหรับการศึกษาหลักพุทธศาสนาเท่านั้น",
        "warning": "⚠️ Mock data - connect to MongoDB for real character data"
    }


# ========================================
# ENDPOINTS: REBIRTH TEMPLATE
# ========================================

@router.post("/create-template", response_model=RebirthTemplate)
async def create_rebirth_template(
    request: CreateTemplateRequest
):
    """
    Create rebirth template for next incarnation
    
    This generates a template with:
    ✅ Auto-filled: Inherited kamma, core traits
    ❌ Manual fill: Name, age, appearance, realm
    ⚠️ Optional: Past life memories
    
    Creator still has full control - this is just a helper
    
    Note: Currently uses mock data. Connect to MongoDB when ready.
    """
    # Get previous character from MongoDB if ID provided
    # For now, use mock character data as this is a calculation helper
    # Real character data should be fetched from actors collection when integrated
    
    mock_previous_character = {
        "id": request.previous_character_id,
        "name": f"Mock Character {request.previous_character_id}",
        "current_bhumi": "มนุษย์ (Manussā)",
        "kamma_ledger": {
            "dana": {"count": 5},
            "sila": {"count": 3},
            "samadhi": {"count": 2}
        },
        "personality": {
            "compassion": 70,
            "wisdom": 60,
            "patience": 50
        },
        "skills": ["meditation", "teaching", "healing"]
    }
    
    # Create template
    generator = RebirthTemplateGenerator()
    template = generator.create_template(
        mock_previous_character,
        options={
            "enable_memories": request.enable_memories,
            "karmic_debt": request.karmic_debt,
            "educational_mode": request.educational_mode
        }
    )
    
    return template


@router.get("/templates/{character_id}/history")
async def get_rebirth_history(character_id: str):
    """
    Get rebirth history for a character
    
    Shows all past life connections
    
    Note: This feature requires database schema update
    """
    return {
        "character_id": character_id,
        "past_lives": [],
        "future_incarnations": [],
        "note": "Feature coming soon - requires database schema update"
    }


# ========================================
# ENDPOINTS: EDUCATIONAL DEMO
# ========================================

@router.get("/demo/samsara-cycle")
async def demonstrate_samsara_cycle():
    """
    Educational demonstration of complete Samsara Cycle
    
    Shows how kamma affects rebirth across 31 realms
    Pre-scripted examples for documentary/educational content
    """
    return {
        "title": "สังสารวัฏ - วนเวียนเกิดแก่เจ็บตาย",
        "description": "ตัวอย่างการเวียนว่ายตายเกิดตามกรรม",
        "examples": [
            {
                "scenario": "คนทำบุญมาก",
                "life_1": {"realm": "มนุษย์", "kamma_score": 60, "actions": ["ให้ทาน", "รักษาศีล"]},
                "life_2": {"realm": "เทวดาชั้นดาวดึงส์", "kamma_score": 65, "lifespan": "36 ล้านปี"},
                "life_3": {"realm": "มนุษย์อีกครั้ง", "kamma_score": 20, "note": "เมื่อบุญหมดก็กลับมาเกิดเป็นมนุษย์"}
            },
            {
                "scenario": "คนโลภมาก",
                "life_1": {"realm": "มนุษย์", "kamma_score": -50, "actions": ["โลภ", "ตระหนี่", "ไม่ให้ทาน"]},
                "life_2": {"realm": "เปรต", "kamma_score": -55, "suffering": "หิวกระหายตลอดเวลา"},
                "life_3": {"realm": "สัตว์เดรัจฉาน", "kamma_score": -30, "note": "เมื่อพ้นเปรตก็ยังต้องเวียนทุกข์"}
            },
            {
                "scenario": "ผู้บรรลุธรรม",
                "life_1": {"realm": "มนุษย์", "kamma_score": 80, "actions": ["เจริญวิปัสสนา", "บรรลุพระอนาคามี"]},
                "life_2": {"realm": "สุทธาวาสภูมิ", "kamma_score": 110, "note": "เกิดในสุทธาวาสแล้วจะบรรลุอรหันต์ที่นั่น"},
                "life_3": {"realm": "นิพพาน", "kamma_score": "N/A", "note": "หลุดพ้นจากสังสารวัฏ ไม่เกิดอีก"}
            }
        ],
        "educational_note": "นี่เป็นตัวอย่างสำหรับการศึกษา ไม่ใช่ระบบจำลองอัตโนมัติ"
    }


@router.get("/demo/realm-comparison")
async def compare_realms():
    """
    Compare different realms
    
    Educational tool to understand differences between realms
    """
    return {
        "comparison": [
            {
                "realm": "นรกอเวจี",
                "pros": [],
                "cons": ["ทุกข์ 100%", "อายุยืนมาก", "ไม่มีโอกาสบรรลุธรรม"],
                "best_for": "ไม่มี - หลีกเลี่ยงเสมอ"
            },
            {
                "realm": "มนุษย์",
                "pros": ["สมดุล สุข-ทุกข์ 50:50", "มีปัญญา", "ดีที่สุดสำหรับบรรลุธรรม"],
                "cons": ["มีทุกข์", "อายุสั้น"],
                "best_for": "แสวงหาพระนิพพาน"
            },
            {
                "realm": "เทวดา",
                "pros": ["ความสุขสูง", "อายุยืน", "มีฤทธิ์"],
                "cons": ["สุขมากเกินไป", "ลืมปฏิบัติธรรม"],
                "best_for": "พักผ่อนจากความทุกข์ แต่ไม่เหมาะบรรลุธรรม"
            },
            {
                "realm": "พรหม",
                "pros": ["ไม่มีทุกข์", "อายุยืนมาก", "ความสงบสุขสูงสุด"],
                "cons": ["ติดฌาน", "ยากที่จะบรรลุธรรม"],
                "best_for": "พักจากสังสารวัฏ แต่ไม่ใช่จุดหมายปลายทาง"
            }
        ]
    }


# ========================================
# HEALTH CHECK
# ========================================

@router.get("/health")
async def health_check():
    """Health check for Rebirth Toolkit module"""
    return {
        "status": "healthy",
        "module": "Rebirth Toolkit",
        "version": "1.0.0",
        "features": {
            "31_realms_reference": "active",
            "rebirth_calculator": "active",
            "template_generator": "active",
            "educational_demo": "active"
        },
        "note": "นี่เป็น Optional Helper Tools ไม่ใช่ระบบอัตโนมัติ",
        "disclaimer": "⚠️ Currently using mock data - MongoDB integration pending",
        "total_realms": len(THIRTY_ONE_REALMS)
    }
