"""
🔄 Real-time State Updater - อัปเดต MindState แบบ Real-time
=============================================================

อัปเดต MindState หลังจากแต่ละ Citta Vithi เกิด
ติดตามการเปลี่ยนแปลงของจิต, กรรม, นิวรณ์, และรูปกาย

## Core Responsibilities:

1. **Update Consciousness State** - อัปเดตสภาวะจิต
   - Current active citta
   - Bhavanga state vs active processing
   - Dominant cetasikas

2. **Update Active Hindrances** - อัปเดตนิวรณ์ที่กำลังรบกวน
   - Increase if akusala citta
   - Decrease if kusala citta
   - Auto-decay over time

3. **Update Kamma Queue** - อัปเดตคิวกรรม
   - Add new kamma from javana
   - Track kamma potency
   - Trigger maturation when ready

4. **Update Virtue Level** - อัปเดตระดับศีล สมาธิ ปัญญา
   - Increase from kusala practice
   - Decrease from akusala actions
   - Gradual changes only

5. **Trigger Appearance Updates** - กระตุ้นการอัปเดตรูปกาย
   - When kamma threshold crossed
   - When virtue level changes significantly
   - Real-time physical manifestation

## Buddhist Scriptural References:
- Abhidhammatthasaṅgaha (อภิธัมมัตถสังคหะ)
- Paṭṭhāna (ปัฏฐาน - Conditional Relations)
- Vīthimutta (วีถิมุตตะ - Cognitive Process)

Created: October 2025
Version: 3.0
"""

from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from enum import Enum
import asyncio


# =============================================================================
# ENUMS & TYPES
# =============================================================================

class ConsciousnessState(str, Enum):
    """สภาวะของจิต"""
    BHAVANGA = "bhavanga"               # ภวังค์ - จิตสภาวะพื้นฐาน
    ACTIVE_PROCESSING = "processing"    # กำลังประมวลผลอารมณ์
    JAVANA_ACTIVE = "javana_active"     # ชวนจิตกำลังทำงาน
    POST_VITHI = "post_vithi"           # หลังจบวิถีจิต
    SLEEPING = "sleeping"               # นอนหลับ
    MEDITATION = "meditation"           # กำลังฌาน


class HindranceType(str, Enum):
    """นิวรณ์ 5"""
    KAMA_CCHANDA = "sensual_desire"     # กามฉันทะ
    BYAPADA = "ill_will"                # พยาบาท
    THINA_MIDDHA = "sloth_torpor"       # ถีนมิทธะ
    UDDHACCA_KUKKUCCA = "restlessness"  # อุทธัจจกุกกุจจะ
    VICIKICCHA = "doubt"                # วิจิกิจฉา


class KammaMaturityLevel(str, Enum):
    """ระดับความสุกของกรรม"""
    SEED = "seed"               # เมล็ด - เพิ่งสร้าง
    GERMINATING = "germinating" # กำลังงอก
    GROWING = "growing"         # กำลังเติบโต
    MATURE = "mature"           # สุกแล้ว พร้อมให้ผล
    FRUITING = "fruiting"       # กำลังให้ผล
    EXHAUSTED = "exhausted"     # หมดฤทธิ์แล้ว


# =============================================================================
# DATA MODELS
# =============================================================================

class ActiveHindrance(BaseModel):
    """นิวรณ์ที่กำลังรบกวน"""
    type: HindranceType = Field(..., description="ประเภทนิวรณ์")
    intensity: float = Field(default=0.0, ge=0, le=10, description="ความเข้ม")
    is_active: bool = Field(default=False, description="กำลังรบกวนหรือไม่")
    last_activated: Optional[datetime] = Field(None, description="เวลาที่ปรากฏล่าสุด")
    activation_count: int = Field(default=0, description="จำนวนครั้งที่ปรากฏ")
    decay_rate: float = Field(default=0.1, description="อัตราการลดลงต่อชั่วโมง")


class KammaQueueEntry(BaseModel):
    """รายการกรรมในคิว"""
    kamma_id: str = Field(..., description="ID ของกรรม")
    citta_type: str = Field(..., description="ประเภทจิตที่สร้าง")
    quality: str = Field(..., description="กุศล/อกุศล")
    potency: float = Field(..., description="พลังของกรรม")
    created_at: datetime = Field(default_factory=datetime.now)
    maturity_level: KammaMaturityLevel = Field(default=KammaMaturityLevel.SEED)
    progress: float = Field(default=0.0, ge=0, le=100, description="ความคืบหน้า %")
    estimated_fruition: Optional[datetime] = Field(None, description="เวลาที่คาดว่าจะให้ผล")
    context: Dict = Field(default_factory=dict, description="บริบทของกรรม")


class MindStateSnapshot(BaseModel):
    """สแนปช็อตของสภาวะจิต ณ จุดหนึ่ง"""
    timestamp: datetime = Field(default_factory=datetime.now)
    consciousness_state: ConsciousnessState = Field(..., description="สภาวะจิต")
    last_citta_type: Optional[str] = Field(None, description="จิตขณะล่าสุด")
    last_javana_quality: Optional[str] = Field(None, description="คุณภาพชวนจิตล่าสุด")
    active_hindrances: Dict[str, float] = Field(default_factory=dict, description="นิวรณ์ที่กำลังรบกวน")
    virtue_level: Dict[str, float] = Field(default_factory=dict, description="ระดับศีล สมาธิ ปัญญา")
    total_kusala_count: int = Field(default=0, description="จำนวนกุศลจิตที่เกิด")
    total_akusala_count: int = Field(default=0, description="จำนวนอกุศลจิตที่เกิด")
    kamma_queue_size: int = Field(default=0, description="ขนาดคิวกรรม")


class StateUpdateResult(BaseModel):
    """ผลการอัปเดต state"""
    success: bool = Field(..., description="สำเร็จหรือไม่")
    changes: List[str] = Field(default_factory=list, description="รายการการเปลี่ยนแปลง")
    triggered_events: List[str] = Field(default_factory=list, description="เหตุการณ์ที่ถูกกระตุ้น")
    warnings: List[str] = Field(default_factory=list, description="คำเตือน")
    new_state: Optional[MindStateSnapshot] = Field(None, description="สภาวะใหม่")


# =============================================================================
# REAL-TIME STATE UPDATER
# =============================================================================

class RealTimeStateUpdater:
    """
    🔄 Real-time State Updater
    
    อัปเดต MindState แบบ real-time หลังแต่ละ citta vithi
    
    Features:
    - Update consciousness state
    - Track active hindrances with auto-decay
    - Manage kamma queue with maturation
    - Update virtue levels gradually
    - Trigger appearance updates on thresholds
    """
    
    def __init__(self):
        self.name = "Real-time State Updater v3.0"
        
        # Thresholds for triggering appearance updates
        self.KAMMA_THRESHOLD = 1000.0  # พลังกรรมสะสม
        self.VIRTUE_CHANGE_THRESHOLD = 0.5  # การเปลี่ยนแปลงศีล สมาธิ ปัญญา
        
        # Maturation settings
        self.KAMMA_MATURATION_TIME = timedelta(hours=24)  # เวลาที่กรรมสุก
        self.HINDRANCE_DECAY_RATE = 0.1  # อัตราการลดลงของนิวรณ์ต่อชั่วโมง
        
    async def update_after_vithi(
        self,
        vithi_result: Dict,  # ChittaVithiSequence
        current_state: Dict,  # MindState from CoreProfile
        model_id: str
    ) -> StateUpdateResult:
        """
        อัปเดต state หลังจาก citta vithi เกิด
        
        Args:
            vithi_result: ผลจาก citta vithi (ChittaVithiSequence)
            current_state: สภาวะจิตปัจจุบัน (MindState)
            model_id: ID ของ model
            
        Returns:
            StateUpdateResult: ผลการอัปเดต
        """
        changes = []
        triggered_events = []
        warnings = []
        
        # Extract info from vithi
        javana_decision = vithi_result.get("javana_decision", {})
        chosen_quality = javana_decision.get("chosen_quality")
        chosen_citta = javana_decision.get("chosen_citta_type")
        total_kamma = vithi_result.get("total_kamma_generated", 0)
        
        # 1. Update consciousness state
        new_consciousness_state = await self._update_consciousness_state(
            current_state, vithi_result
        )
        changes.append(f"Consciousness state: {new_consciousness_state}")
        
        # 2. Update active hindrances
        hindrance_changes = await self._update_active_hindrances(
            current_state, chosen_quality, chosen_citta
        )
        if hindrance_changes:
            changes.extend(hindrance_changes)
        
        # 3. Update kamma queue
        kamma_added = await self._update_kamma_queue(
            current_state, vithi_result, model_id
        )
        if kamma_added:
            changes.append(f"Kamma added: {total_kamma:.1f} potency")
        
        # 4. Update virtue level (gradual)
        virtue_changes = await self._update_virtue_level(
            current_state, chosen_quality, total_kamma
        )
        if virtue_changes:
            # Convert numeric changes to strings
            virtue_change_strs = [
                f"Sila: {virtue_changes[0]:+.3f}",
                f"Samadhi: {virtue_changes[1]:+.3f}",
                f"Panna: {virtue_changes[2]:+.3f}"
            ]
            changes.extend(virtue_change_strs)
            
            # Check if significant change
            if any(abs(change) > self.VIRTUE_CHANGE_THRESHOLD for change in virtue_changes):
                triggered_events.append("virtue_level_significant_change")
        
        # 5. Update counters
        if chosen_quality == "kusala":
            current_state["total_kusala_count"] = current_state.get("total_kusala_count", 0) + 1
            changes.append(f"Kusala count: {current_state['total_kusala_count']}")
        elif chosen_quality == "akusala":
            current_state["total_akusala_count"] = current_state.get("total_akusala_count", 0) + 1
            changes.append(f"Akusala count: {current_state['total_akusala_count']}")
        
        # 6. Check appearance update threshold
        total_kamma_accumulated = sum(
            k.get("potency", 0) 
            for k in current_state.get("kamma_queue", [])
        )
        
        if total_kamma_accumulated > self.KAMMA_THRESHOLD:
            triggered_events.append("appearance_update_threshold_reached")
            changes.append(f"Appearance update triggered (kamma: {total_kamma_accumulated:.1f})")
        
        # 7. Update last citta moment
        current_state["last_citta_type"] = chosen_citta
        current_state["last_javana_quality"] = chosen_quality
        current_state["last_vithi_timestamp"] = datetime.now().isoformat()
        
        # Create snapshot
        new_snapshot = MindStateSnapshot(
            timestamp=datetime.now(),
            consciousness_state=new_consciousness_state,
            last_citta_type=chosen_citta,
            last_javana_quality=chosen_quality,
            active_hindrances={
                k: v.get("intensity", 0)
                for k, v in current_state.get("active_hindrances", {}).items()
                if v.get("is_active", False)
            },
            virtue_level=current_state.get("VirtueLevel", {}),
            total_kusala_count=current_state.get("total_kusala_count", 0),
            total_akusala_count=current_state.get("total_akusala_count", 0),
            kamma_queue_size=len(current_state.get("kamma_queue", []))
        )
        
        return StateUpdateResult(
            success=True,
            changes=changes,
            triggered_events=triggered_events,
            warnings=warnings,
            new_state=new_snapshot
        )
    
    async def _update_consciousness_state(
        self,
        current_state: Dict,
        vithi_result: Dict
    ) -> ConsciousnessState:
        """อัปเดตสภาวะจิต"""
        # After vithi completes, return to bhavanga
        return ConsciousnessState.BHAVANGA
    
    async def _update_active_hindrances(
        self,
        current_state: Dict,
        javana_quality: str,
        citta_type: str
    ) -> List[str]:
        """อัปเดตนิวรณ์ที่กำลังรบกวน"""
        changes = []
        
        hindrances = current_state.get("active_hindrances", {})
        
        if javana_quality == "akusala":
            # Akusala citta increases relevant hindrance
            if "โลภ" in citta_type:
                # Lobha increases kāmacchanda
                hindrance = hindrances.setdefault("kama_cchanda", {
                    "type": "sensual_desire",
                    "intensity": 0,
                    "is_active": False,
                    "activation_count": 0
                })
                hindrance["intensity"] = min(10, hindrance.get("intensity", 0) + 0.5)
                hindrance["is_active"] = True
                hindrance["last_activated"] = datetime.now().isoformat()
                hindrance["activation_count"] = hindrance.get("activation_count", 0) + 1
                changes.append(f"Kāmacchanda increased to {hindrance['intensity']:.1f}")
                
            elif "โทสะ" in citta_type:
                # Dosa increases byāpāda
                hindrance = hindrances.setdefault("byapada", {
                    "type": "ill_will",
                    "intensity": 0,
                    "is_active": False,
                    "activation_count": 0
                })
                hindrance["intensity"] = min(10, hindrance.get("intensity", 0) + 0.5)
                hindrance["is_active"] = True
                hindrance["last_activated"] = datetime.now().isoformat()
                hindrance["activation_count"] = hindrance.get("activation_count", 0) + 1
                changes.append(f"Byāpāda increased to {hindrance['intensity']:.1f}")
                
            elif "โมหะ" in citta_type:
                # Moha increases vicikicchā
                hindrance = hindrances.setdefault("vicikiccha", {
                    "type": "doubt",
                    "intensity": 0,
                    "is_active": False,
                    "activation_count": 0
                })
                hindrance["intensity"] = min(10, hindrance.get("intensity", 0) + 0.3)
                hindrance["is_active"] = True
                hindrance["last_activated"] = datetime.now().isoformat()
                hindrance["activation_count"] = hindrance.get("activation_count", 0) + 1
                changes.append(f"Vicikicchā increased to {hindrance['intensity']:.1f}")
        
        elif javana_quality == "kusala":
            # Kusala citta decreases all hindrances
            for h_name, h_data in hindrances.items():
                if h_data.get("is_active", False):
                    old_intensity = h_data.get("intensity", 0)
                    new_intensity = max(0, old_intensity - 0.3)
                    h_data["intensity"] = new_intensity
                    
                    if new_intensity < 1.0:
                        h_data["is_active"] = False
                        changes.append(f"{h_name} deactivated")
                    else:
                        changes.append(f"{h_name} decreased to {new_intensity:.1f}")
        
        return changes
    
    async def _update_kamma_queue(
        self,
        current_state: Dict,
        vithi_result: Dict,
        model_id: str
    ) -> bool:
        """อัปเดตคิวกรรม"""
        kamma_queue = current_state.setdefault("kamma_queue", [])
        
        javana_decision = vithi_result.get("javana_decision", {})
        total_kamma = vithi_result.get("total_kamma_generated", 0)
        
        # Only add if kamma is significant
        if total_kamma > 10:
            entry = {
                "kamma_id": f"{model_id}_{datetime.now().timestamp()}",
                "citta_type": javana_decision.get("chosen_citta_type", "unknown"),
                "quality": javana_decision.get("chosen_quality", "unknown"),
                "potency": total_kamma,
                "created_at": datetime.now().isoformat(),
                "maturity_level": "seed",
                "progress": 0.0,
                "estimated_fruition": (datetime.now() + self.KAMMA_MATURATION_TIME).isoformat(),
                "context": {
                    "sensory_input": vithi_result.get("sensory_input", {}).get("aramana_description", ""),
                    "reasoning": javana_decision.get("reasoning", "")
                }
            }
            
            kamma_queue.append(entry)
            return True
        
        return False
    
    async def _update_virtue_level(
        self,
        current_state: Dict,
        javana_quality: str,
        kamma_potency: float
    ) -> List[float]:
        """อัปเดตระดับศีล สมาธิ ปัญญา (ค่อยๆ เปลี่ยน)"""
        virtue = current_state.get("VirtueLevel", {})
        changes = []
        
        # Calculate change amount (very small, gradual)
        change_amount = (kamma_potency / 1000) * 0.1  # max 0.1 per vithi
        
        if javana_quality == "kusala":
            # Kusala increases virtue (slightly)
            old_sila = virtue.get("sila", 5)
            old_samadhi = virtue.get("samadhi", 5)
            old_panna = virtue.get("panna", 5)
            
            virtue["sila"] = min(10, old_sila + change_amount * 0.5)
            virtue["samadhi"] = min(10, old_samadhi + change_amount * 0.7)
            virtue["panna"] = min(10, old_panna + change_amount * 0.3)
            
            changes.append(virtue["sila"] - old_sila)
            changes.append(virtue["samadhi"] - old_samadhi)
            changes.append(virtue["panna"] - old_panna)
            
        elif javana_quality == "akusala":
            # Akusala decreases virtue (slightly)
            old_sila = virtue.get("sila", 5)
            old_samadhi = virtue.get("samadhi", 5)
            old_panna = virtue.get("panna", 5)
            
            virtue["sila"] = max(0, old_sila - change_amount * 0.3)
            virtue["samadhi"] = max(0, old_samadhi - change_amount * 0.5)
            virtue["panna"] = max(0, old_panna - change_amount * 0.2)
            
            changes.append(virtue["sila"] - old_sila)
            changes.append(virtue["samadhi"] - old_samadhi)
            changes.append(virtue["panna"] - old_panna)
        
        return changes
    
    async def decay_hindrances(self, current_state: Dict, hours_elapsed: float) -> List[str]:
        """
        Auto-decay hindrances over time
        
        Args:
            current_state: สภาวะจิตปัจจุบัน
            hours_elapsed: จำนวนชั่วโมงที่ผ่านไป
            
        Returns:
            List[str]: รายการการเปลี่ยนแปลง
        """
        changes = []
        hindrances = current_state.get("active_hindrances", {})
        
        for h_name, h_data in hindrances.items():
            if h_data.get("is_active", False):
                decay_amount = self.HINDRANCE_DECAY_RATE * hours_elapsed
                old_intensity = h_data.get("intensity", 0)
                new_intensity = max(0, old_intensity - decay_amount)
                h_data["intensity"] = new_intensity
                
                if new_intensity < 1.0:
                    h_data["is_active"] = False
                    changes.append(f"{h_name} naturally decayed and deactivated")
                elif new_intensity < old_intensity:
                    changes.append(f"{h_name} decayed to {new_intensity:.1f}")
        
        return changes
    
    async def mature_kamma(self, current_state: Dict) -> List[Dict]:
        """
        Mature kamma in queue (progress towards fruition)
        
        Returns:
            List[Dict]: รายการกรรมที่สุกแล้ว
        """
        kamma_queue = current_state.get("kamma_queue", [])
        matured_kamma = []
        
        for entry in kamma_queue:
            # Calculate progress
            created = datetime.fromisoformat(entry.get("created_at"))
            elapsed = datetime.now() - created
            total_time = self.KAMMA_MATURATION_TIME.total_seconds()
            progress = (elapsed.total_seconds() / total_time) * 100
            
            entry["progress"] = min(100, progress)
            
            # Update maturity level
            if progress >= 100:
                entry["maturity_level"] = "mature"
                matured_kamma.append(entry)
            elif progress >= 75:
                entry["maturity_level"] = "growing"
            elif progress >= 25:
                entry["maturity_level"] = "germinating"
            else:
                entry["maturity_level"] = "seed"
        
        return matured_kamma


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    import asyncio
    
    print("🔄 Testing Real-time State Updater\n")
    
    updater = RealTimeStateUpdater()
    
    # Mock current state
    current_state = {
        "consciousness_state": "bhavanga",
        "active_hindrances": {
            "kama_cchanda": {
                "type": "sensual_desire",
                "intensity": 3.0,
                "is_active": True,
                "activation_count": 5
            }
        },
        "VirtueLevel": {
            "sila": 5.0,
            "samadhi": 4.0,
            "panna": 4.0
        },
        "total_kusala_count": 10,
        "total_akusala_count": 15,
        "kamma_queue": []
    }
    
    # Mock vithi result (akusala - lobha)
    vithi_result = {
        "javana_decision": {
            "chosen_quality": "akusala",
            "chosen_citta_type": "โลภมูลจิต",
            "reasoning": "Sensual desire activated"
        },
        "total_kamma_generated": 595.0,
        "sensory_input": {
            "aramana_description": "เห็นของสวยในตลาด"
        }
    }
    
    # Test update
    async def test_update():
        print("="*60)
        print("Test 1: Update after Akusala Vithi (Lobha)")
        print("="*60)
        
        result = await updater.update_after_vithi(
            vithi_result,
            current_state,
            "test-model-001"
        )
        
        print(f"\n✅ Success: {result.success}")
        print(f"\n📝 Changes ({len(result.changes)}):")
        for change in result.changes:
            print(f"  - {change}")
        
        if result.triggered_events:
            print(f"\n🎯 Triggered Events:")
            for event in result.triggered_events:
                print(f"  - {event}")
        
        print(f"\n📊 New State Snapshot:")
        print(f"  Consciousness: {result.new_state.consciousness_state}")
        print(f"  Last Citta: {result.new_state.last_citta_type}")
        print(f"  Kusala Count: {result.new_state.total_kusala_count}")
        print(f"  Akusala Count: {result.new_state.total_akusala_count}")
        print(f"  Active Hindrances: {result.new_state.active_hindrances}")
        print(f"  Virtue Level: {result.new_state.virtue_level}")
        print(f"  Kamma Queue Size: {result.new_state.kamma_queue_size}")
        
        # Test decay
        print("\n" + "="*60)
        print("Test 2: Natural Decay of Hindrances (1 hour)")
        print("="*60)
        
        decay_changes = await updater.decay_hindrances(current_state, hours_elapsed=1.0)
        print(f"\n📝 Decay Changes:")
        for change in decay_changes:
            print(f"  - {change}")
    
    asyncio.run(test_update())
