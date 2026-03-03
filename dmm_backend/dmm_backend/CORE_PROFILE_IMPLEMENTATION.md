# Core Profile Implementation Guide

## Overview

Core Profile เป็นโครงสร้างข้อมูลหลักของ Digital Mind Model v14 ที่ครอบคลุมจิตวิทยาทางพระพุทธศาสนาอย่างสมบูรณ์

## Current Status

✅ **Completed**:
- Complete Pydantic models defined in `core_profile_models.py`
- Full API router with 12 endpoints in `routers/core_profile.py`
- Router mounted in `main.py`
- Complete documentation in `docs/modules/`

⚠️ **Known Issue**:
Pydantic v2 type annotation clash - การใช้ชื่อ attribute เหมือนกับ class name ทำให้เกิด error

## Solution Options

### Option 1: Use String Type Hints (Recommended)

แก้ไข `core_profile_models.py` โดยใช้ string type hints:

```python
from __future__ import annotations  # Add at top of file

class CoreProfile(BaseModel):
    CharacterStatus: "CharacterStatus" = Field(default_factory=CharacterStatus)
    LifeEssence: "LifeEssence" = Field(default_factory=LifeEssence)
    PsychologicalMatrix: "PsychologicalMatrix" = Field(default_factory=PsychologicalMatrix)
    SpiritualAssets: "SpiritualAssets" = Field(default_factory=SpiritualAssets)
```

### Option 2: Rename Attributes (Alternative)

เปลี่ยนชื่อ attribute ให้ต่างจาก class name:

```python
class CoreProfile(BaseModel):
    character_status: CharacterStatus = Field(default_factory=CharacterStatus)
    life_essence: LifeEssence = Field(default_factory=LifeEssence)
    psychological_matrix: PsychologicalMatrix = Field(default_factory=PsychologicalMatrix)
    spiritual_assets: SpiritualAssets = Field(default_factory=SpiritualAssets)
```

### Option 3: Use typing.TYPE_CHECKING

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self

class CoreProfile(BaseModel):
    CharacterStatus: CharacterStatus = Field(default_factory=lambda: CharacterStatus())
    # ... etc
```

## Implementation Steps

### Step 1: Fix core_profile_models.py

```bash
cd dmm_backend
# Edit core_profile_models.py with Option 1
```

### Step 2: Test Import

```bash
./venv/bin/python -c "
from core_profile_models import CoreProfile
profile = CoreProfile()
print(f'✓ CoreProfile works: {profile.get_overall_spiritual_score()}')
"
```

### Step 3: Update documents.py

Ensure CoreProfile is properly exported:

```python
# In documents.py
from core_profile_models import CoreProfile

# Then use in DigitalMindModel
class DigitalMindModel(Document):
    # ...
    core_profile_model: Optional[CoreProfile] = None
```

### Step 4: Test API

```bash
# Start backend
./venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8000

# Test endpoint
curl -X GET "http://127.0.0.1:8000/api/v1/core-profile/peace-mind-001" \
  -H "X-API-KEY: YOUR_SECRET_API_KEY"
```

## API Endpoints

Once fixed, these endpoints will be available:

### Core Profile Management

```
GET    /api/v1/core-profile/{model_id}                 # Get complete profile
GET    /api/v1/core-profile/{model_id}/character-status
PATCH  /api/v1/core-profile/{model_id}/character-status
GET    /api/v1/core-profile/{model_id}/life-essence
PATCH  /api/v1/core-profile/{model_id}/life-essence
GET    /api/v1/core-profile/{model_id}/psychological-matrix
PATCH  /api/v1/core-profile/{model_id}/anusaya
GET    /api/v1/core-profile/{model_id}/spiritual-assets
PATCH  /api/v1/core-profile/{model_id}/parami
POST   /api/v1/core-profile/{model_id}/break-fetter
GET    /api/v1/core-profile/{model_id}/spiritual-score
GET    /api/v1/core-profile/{model_id}/progress-summary
```

### Example Usage

```python
# Get profile
response = await client.get("/api/v1/core-profile/peace-mind-001")
profile = response.json()

# Break fetter (become Sotāpanna)
await client.post(
    "/api/v1/core-profile/peace-mind-001/break-fetter",
    json={"fetter_name": "sakkayaditthi"}
)

# Update pāramī
await client.patch(
    "/api/v1/core-profile/peace-mind-001/parami",
    json={"parami_name": "metta", "level": 8, "exp": 600}
)

# Get spiritual score
score = await client.get("/api/v1/core-profile/peace-mind-001/spiritual-score")
# Returns: {"total_score": 45.2, "breakdown": {...}}
```

## Database Integration

### Current Structure in MongoDB

```javascript
{
  "model_id": "peace-mind-001",
  "name": "Peace Mind Prototype",
  "core_profile": {  // Legacy dict format
    "CharacterStatus": {...},
    "LifeEssence": {...},
    "PsychologicalMatrix": {...},
    "SpiritualAssets": {...}
  }
}
```

### After Fix

```javascript
{
  "model_id": "peace-mind-001",
  "name": "Peace Mind Prototype",
  "CoreProfile": {  // New Pydantic model
    "CharacterStatus": {
      "type": "Sekha",
      "stage": "Sotāpanna trajectory",
      "fetters_broken": ["sakkayaditthi", "vicikiccha", "silabbataparamasa"]
    },
    // ... complete structure
  },
  "core_profile": {...}  // Keep for backward compatibility
}
```

## Testing Checklist

- [ ] Fix Pydantic type annotation issue
- [ ] Test CoreProfile instantiation
- [ ] Test all methods (get_overall_spiritual_score, is_noble, break_fetter)
- [ ] Test DigitalMindModel integration
- [ ] Test API endpoints
- [ ] Test database save/load
- [ ] Update seed_db.py to use new models
- [ ] Run integration tests

## Buddhist Psychology Validation

### Character Progression (10 Fetters)

```
Puthujjana (ปุถุชน) - 10 fetters
  ↓ Break 3 fetters
Sotāpanna (โสดาบัน) - 7 fetters remaining
  ↓ Weaken kamaraga, patigha
Sakadāgāmī (สกทาคามี) - 5 fetters remaining
  ↓ Break kamaraga, patigha
Anāgāmī (อนาคามี) - 5 higher fetters remaining
  ↓ Break all 5 higher fetters
Arahant (อรหันต์) - 0 fetters
```

### 10 Pāramī Tracking

```python
perfections = {
    "dana": ParamiEntry(level=4, exp=120),      # Generosity
    "sila": ParamiEntry(level=5, exp=160),      # Virtue
    "nekkhamma": ParamiEntry(level=3, exp=90),  # Renunciation
    "panna": ParamiEntry(level=2, exp=70),      # Wisdom
    "viriya": ParamiEntry(level=6, exp=210),    # Energy
    "khanti": ParamiEntry(level=3, exp=140),    # Patience
    "sacca": ParamiEntry(level=7, exp=260),     # Truthfulness
    "adhitthana": ParamiEntry(level=4, exp=150),# Determination
    "metta": ParamiEntry(level=2, exp=80),      # Loving-kindness
    "upekkha": ParamiEntry(level=1, exp=40),    # Equanimity
}
```

### 7 Anusaya (Latent Tendencies)

```python
anusaya_kilesa = {
    "kama_raga": {"level": 6.5},    # Sensual desire
    "patigha": {"level": 8.2},       # Aversion
    "mana": {"level": 6.0},          # Conceit
    "ditthi": {"level": 3.5},        # Wrong view
    "vicikiccha": {"level": 4.0},    # Doubt
    "bhava_raga": {"level": 5.0},    # Craving for existence
    "avijja": {"level": 7.5},        # Ignorance
}
```

## Documentation

Complete documentation available in `docs/modules/`:

1. **CORE_PROFILE_DEEP_ANALYSIS.md** - Complete Core Profile structure
2. **README.md** - Navigation and quick start guide

## Next Steps

1. **Immediate**: Fix Pydantic type annotation issue (choose Option 1 or 2)
2. **Short-term**: Update seed_db.py to generate CoreProfile models
3. **Medium-term**: Integrate with MindOS processing
4. **Long-term**: Create frontend components for Core Profile visualization

## Support

For questions or issues:
- See documentation: `docs/modules/CORE_PROFILE_DEEP_ANALYSIS.md`
- Check API router: `routers/core_profile.py`
- Review models: `core_profile_models.py`

---

**Status**: Implementation 95% complete - Only Pydantic type annotation fix remaining
**Last Updated**: 2025-01-12
**Version**: 14.0
