"""
🧠 Citta Vithi Router - REST API Endpoints
===========================================

REST API สำหรับ Citta Vithi Engine

Endpoints:
- POST /api/citta-vithi/process - ประมวลผล sensory input → สร้างวิถีจิต
- GET /api/citta-vithi/simulate/{model_id} - จำลองสถานการณ์
- GET /api/citta-vithi/history/{model_id} - ประวัติวิถีจิตที่เกิด
- GET /api/citta-vithi/statistics/{model_id} - สถิติกุศล/อกุศล
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import random

from modules.citta_vithi_engine import (
    ChittaVithiEngine,
    SensoryInput,
    DvaraType,
    AramanaType,
    VedanaType,
    ChittaVithiSequence,
)

# Import database documents
from documents import VithiRecord


router = APIRouter(
    prefix="/api/citta-vithi",
    tags=["Citta Vithi (วิถีจิต)"]
)

# Initialize engine
engine = ChittaVithiEngine()


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class ProcessVithiRequest(BaseModel):
    """Request สำหรับประมวลผล sensory input"""
    dvara: DvaraType = Field(..., description="ทวารที่รับรู้")
    aramana_description: str = Field(..., description="รายละเอียดอารมณ์")
    intensity: float = Field(default=5.0, ge=0, le=10, description="ความแรง")
    natural_vedana: VedanaType = Field(..., description="เวทนาของอารมณ์")
    core_profile: Dict = Field(..., description="CoreProfile ของ model")
    
    class Config:
        json_schema_extra = {
            "example": {
                "dvara": "eye",
                "aramana_description": "ใบหน้าสวยของนางเอก",
                "intensity": 8.5,
                "natural_vedana": "pleasant",
                "core_profile": {
                    "LatentTendencies": {
                        "anusaya_kilesa": {
                            "kama_raga": {"level": 5},
                            "patigha": {"level": 5},
                            "avijja": {"level": 7}
                        }
                    },
                    "VirtueLevel": {
                        "sila": 5,
                        "samadhi": 5,
                        "panna": 5
                    },
                    "active_hindrances": {}
                }
            }
        }


class SimulateScenarioRequest(BaseModel):
    """Request สำหรับจำลองสถานการณ์"""
    scenario_type: str = Field(..., description="ประเภทสถานการณ์")
    model_id: str = Field(..., description="ID ของ model")
    
    class Config:
        json_schema_extra = {
            "example": {
                "scenario_type": "marketplace_temptation",
                "model_id": "507f1f77bcf86cd799439011"
            }
        }


class VithiStatistics(BaseModel):
    """สถิติวิถีจิต"""
    model_id: str
    total_vithis: int = Field(..., description="จำนวนวิถีจิตทั้งหมด")
    kusala_count: int = Field(..., description="จำนวนกุศล")
    akusala_count: int = Field(..., description="จำนวนอกุศล")
    kusala_percentage: float = Field(..., description="% กุศล")
    akusala_percentage: float = Field(..., description="% อกุศล")
    total_kamma_generated: float = Field(..., description="กรรมที่สร้างรวม")
    average_kusala_probability: float = Field(..., description="โอกาสกุศลเฉลี่ย")
    sati_intervention_rate: float = Field(..., description="% ที่สติเข้าแทรก")
    most_common_citta: str = Field(..., description="จิตที่เกิดบ่อยที่สุด")
    dominant_factors: List[str] = Field(..., description="ปัจจัยหลักที่มีอิทธิพล")


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.post("/process", response_model=ChittaVithiSequence)
async def process_sensory_input(request: ProcessVithiRequest):
    """
    🧠 ประมวลผล Sensory Input → สร้างวิถีจิต
    
    รับ input จากประสาทสัมผัส → สร้างลำดับจิต 17 ขณะ
    
    Returns:
        ChittaVithiSequence: ลำดับจิตครบ 17 ขณะ พร้อมผลกรรม
    """
    try:
        # Map aramana type from dvara
        aramana_type_map = {
            DvaraType.CAKKHU: AramanaType.RUPA,
            DvaraType.SOTA: AramanaType.SADDA,
            DvaraType.GHANA: AramanaType.GANDHA,
            DvaraType.JIVHA: AramanaType.RASA,
            DvaraType.KAYA: AramanaType.PHOTTHABBA,
            DvaraType.MANO: AramanaType.DHAMMĀRAMMAṆA,
        }
        
        sensory_input = SensoryInput(
            dvara=request.dvara,
            aramana_type=aramana_type_map[request.dvara],
            aramana_description=request.aramana_description,
            intensity=request.intensity,
            natural_vedana=request.natural_vedana
        )
        
        vithi = engine.process_sensory_input(
            sensory_input=sensory_input,
            core_profile=request.core_profile
        )
        
        return vithi
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing vithi: {str(e)}")


@router.post("/simulate")
async def simulate_scenario(request: SimulateScenarioRequest):
    """
    🎭 จำลองสถานการณ์
    
    สร้างสถานการณ์จำลอง → ประมวลผลวิถีจิต → แสดงผล
    
    Scenarios:
    - marketplace_temptation (ตลาดของสวย)
    - conflict_situation (ถูกดุ)
    - meditation_session (นั่งสมาธิ)
    - beautiful_sunset (พระอาทิตย์ตกสวย)
    """
    
    # Predefined scenarios
    scenarios = {
        "marketplace_temptation": {
            "dvara": DvaraType.CAKKHU,
            "aramana": "เห็นของสวยๆ ในตลาด ราคาแพง",
            "intensity": 7.5,
            "vedana": VedanaType.SUKHA,
            "description": "เดินในตลาด เห็นของสวยๆ แต่ราคาแพง ใจจะยั้งได้หรือไม่?"
        },
        "conflict_situation": {
            "dvara": DvaraType.SOTA,
            "aramana": "ได้ยินคนว่าหนักๆ",
            "intensity": 8.0,
            "vedana": VedanaType.DUKKHA,
            "description": "ถูกคนว่าหนักๆ ต่อหน้าคนจำนวนมาก จะโกรธหรือไม่?"
        },
        "meditation_session": {
            "dvara": DvaraType.MANO,
            "aramana": "ลมหายใจเข้าออก สงบ",
            "intensity": 6.0,
            "vedana": VedanaType.UPEKKHA,
            "description": "นั่งสมาธิ สงบใจ เฝ้าลมหายใจ"
        },
        "beautiful_sunset": {
            "dvara": DvaraType.CAKKHU,
            "aramana": "พระอาทิตย์ตกสวยมาก",
            "intensity": 7.0,
            "vedana": VedanaType.SUKHA,
            "description": "เห็นพระอาทิตย์ตกสวยมาก จะติดความชอบหรือไม่?"
        }
    }
    
    if request.scenario_type not in scenarios:
        raise HTTPException(
            status_code=400, 
            detail=f"Unknown scenario. Available: {list(scenarios.keys())}"
        )
    
    scenario = scenarios[request.scenario_type]
    
    # For demo, use example core_profile
    # In production, load from database using model_id
    core_profile = {
        "LatentTendencies": {
            "anusaya_kilesa": {
                "kama_raga": {"level": 6},
                "patigha": {"level": 5},
                "avijja": {"level": 7}
            }
        },
        "VirtueLevel": {
            "sila": 5,
            "samadhi": 4,
            "panna": 4
        },
        "active_hindrances": {}
    }
    
    # Process vithi
    sensory_input = SensoryInput(
        dvara=scenario["dvara"],
        aramana_type=AramanaType.RUPA if scenario["dvara"] == DvaraType.CAKKHU else AramanaType.SADDA,
        aramana_description=scenario["aramana"],
        intensity=scenario["intensity"],
        natural_vedana=scenario["vedana"]
    )
    
    vithi = engine.process_sensory_input(sensory_input, core_profile)
    
    return {
        "scenario": {
            "type": request.scenario_type,
            "description": scenario["description"],
            "input": scenario["aramana"]
        },
        "vithi_result": vithi,
        "summary": engine.get_summary(vithi)
    }


@router.get("/history/{model_id}")
async def get_vithi_history(
    model_id: str,
    limit: int = Query(default=20, ge=1, le=100, description="จำนวนวิถีจิตที่จะดึง"),
    days: int = Query(default=7, ge=1, le=365, description="ช่วงเวลา (วัน)")
):
    """
    📜 ดึงประวัติวิถีจิต
    
    ดึงประวัติวิถีจิตที่เกิดในช่วงเวลาที่กำหนด
    
    Note: ต้องบันทึก vithi ลง MongoDB ก่อน
    """
    # Calculate time range
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)
    
    # Query VithiRecord from MongoDB
    from pymongo import DESCENDING
    vithi_records = await VithiRecord.find({
        "model_id": model_id,
        "timestamp": {"$gte": start_time, "$lte": end_time}
    }).sort([("timestamp", DESCENDING)]).to_list()
    
    # Convert to response format
    vithis = []
    for record in vithi_records:
        vithis.append({
            "vithi_type": record.vithi_type,
            "javana_quality": record.javana_quality,
            "kamma_potency": record.kamma_potency,
            "total_moments": record.total_moments,
            "duration_ms": record.duration_ms,
            "timestamp": record.timestamp.isoformat()
        })
    
    return {
        "model_id": model_id,
        "period": f"Last {days} days",
        "total_vithis": len(vithis),
        "vithis": vithis
    }


@router.get("/statistics/{model_id}", response_model=VithiStatistics)
async def get_vithi_statistics(
    model_id: str,
    days: int = Query(default=30, ge=1, le=365, description="ช่วงเวลา (วัน)")
):
    """
    📊 สถิติวิถีจิต
    
    คำนวณสถิติการเกิดกุศล/อกุศล ในช่วงเวลาที่กำหนด
    """
    # Calculate time range
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)
    
    # Query VithiRecord from MongoDB
    from pymongo import DESCENDING
    vithi_records = await VithiRecord.find({
        "model_id": model_id,
        "timestamp": {"$gte": start_time, "$lte": end_time}
    }).to_list()
    
    # Calculate statistics
    total_vithis = len(vithi_records)
    
    if total_vithis == 0:
        return VithiStatistics(
            model_id=model_id,
            total_vithis=0,
            kusala_count=0,
            akusala_count=0,
            kusala_percentage=0.0,
            akusala_percentage=0.0,
            total_kamma_generated=0.0,
            average_kusala_probability=0.0,
            sati_intervention_rate=0.0,
            most_common_citta="N/A",
            dominant_factors=[],
        )
    
    # Count by quality
    kusala_count = sum(1 for v in vithi_records if v.javana_quality == "kusala")
    akusala_count = sum(1 for v in vithi_records if v.javana_quality == "akusala")
    kiriya_count = sum(1 for v in vithi_records if v.javana_quality == "kiriya")
    
    # Calculate percentages
    kusala_percentage = (kusala_count / total_vithis) * 100.0
    akusala_percentage = (akusala_count / total_vithis) * 100.0
    
    # Total kamma (sum potency of kusala + akusala)
    total_kamma = sum(v.kamma_potency for v in vithi_records if v.javana_quality in ["kusala", "akusala"])
    
    # Average kusala probability
    average_kusala_probability = kusala_percentage / 100.0
    
    # Sati intervention rate (estimated from kiriya moments)
    sati_intervention_rate = (kiriya_count / total_vithis) * 100.0 if kiriya_count > 0 else 0.0
    
    # Most common vithi type
    vithi_type_counts: Dict[str, int] = {}
    for v in vithi_records:
        vithi_type_counts[v.vithi_type] = vithi_type_counts.get(v.vithi_type, 0) + 1
    
    most_common_citta = max(vithi_type_counts, key=lambda k: vithi_type_counts[k]) if vithi_type_counts else "N/A"
    
    # Dominant factors (top 3 vithi types)
    sorted_types = sorted(vithi_type_counts.items(), key=lambda x: x[1], reverse=True)
    dominant_factors = [vtype for vtype, _ in sorted_types[:3]]
    
    return VithiStatistics(
        model_id=model_id,
        total_vithis=total_vithis,
        kusala_count=kusala_count,
        akusala_count=akusala_count,
        kusala_percentage=round(kusala_percentage, 2),
        akusala_percentage=round(akusala_percentage, 2),
        total_kamma_generated=round(total_kamma, 2),
        average_kusala_probability=round(average_kusala_probability, 3),
        sati_intervention_rate=round(sati_intervention_rate, 2),
        most_common_citta=most_common_citta,
        dominant_factors=dominant_factors,
    )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "engine": engine.name,
        "version": "3.0.0",
        "features": [
            "process_sensory_input",
            "simulate_scenario", 
            "vithi_history",
            "vithi_statistics"
        ],
        "total_endpoints": 5
    }
