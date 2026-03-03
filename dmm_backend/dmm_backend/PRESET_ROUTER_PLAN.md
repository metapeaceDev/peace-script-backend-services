# Custom Presets Router - Implementation Plan
**Date**: 28 ตุลาคม 2568

---

## 🏗️ Architecture Overview

### File Structure
```
routers/presets.py (main router - ~750 lines)
utils/preset_helpers.py (helper functions - ✅ มีแล้ว)
documents_presets.py (models - ✅ มีแล้ว)
schemas_presets.py (schemas - ✅ มีแล้ว)
```

---

## 📝 Implementation Plan (6 Parts)

### Part 1: Imports & Setup (Lines 1-70)
**Content**:
- Import statements (FastAPI, Beanie, typing)
- Import helpers (preset_helpers)
- Import models (documents_presets)
- Import schemas (schemas_presets)
- Router initialization
- Helper functions (get_current_user_id, check_preset_access)

**Estimated Lines**: 70

---

### Part 2: Preset Templates Endpoints (Lines 71-180)
**Endpoints** (3):
1. `GET /api/presets/templates` - List templates
2. `GET /api/presets/templates/{template_id}` - Get template detail
3. `POST /api/presets/templates` - Create template (admin)

**Features**:
- Pagination
- Filtering (category, search)
- Serialization using helpers

**Estimated Lines**: 110

---

### Part 3: User Presets Core CRUD (Lines 181-350)
**Endpoints** (5):
1. `GET /api/presets/user` - List user presets
2. `GET /api/presets/user/{preset_id}` - Get preset detail
3. `POST /api/presets/user` - Create preset
4. `PUT /api/presets/user/{preset_id}` - Update preset
5. `DELETE /api/presets/user/{preset_id}` - Delete preset

**Features**:
- Complex filtering (category, visibility, favorite, folder)
- Sorting (name, date, usage)
- Pagination
- Soft delete

**Estimated Lines**: 170

---

### Part 4: User Presets Extended Operations (Lines 351-450)
**Endpoints** (3):
1. `POST /api/presets/user/{preset_id}/duplicate` - Duplicate preset
2. `POST /api/presets/user/{preset_id}/favorite` - Toggle favorite
3. `POST /api/presets/user/batch` - Batch operations

**Features**:
- Preset duplication
- Favorite toggle
- Batch delete/favorite/move

**Estimated Lines**: 100

---

### Part 5: Collections, Usage & Analytics (Lines 451-600)
**Endpoints** (7):
1. `GET /api/presets/collections` - List collections
2. `POST /api/presets/collections` - Create collection
3. `PUT /api/presets/collections/{collection_id}` - Update collection
4. `DELETE /api/presets/collections/{collection_id}` - Delete collection
5. `POST /api/presets/usage` - Log usage
6. `GET /api/presets/usage/stats` - Usage statistics
7. Analytics aggregation

**Features**:
- Collection management
- Usage logging with stats updates
- Analytics calculations

**Estimated Lines**: 150

---

### Part 6: Sharing & Import/Export (Lines 601-750)
**Endpoints** (5):
1. `POST /api/presets/share` - Share preset
2. `GET /api/presets/shared-with-me` - Get shared presets
3. `PUT /api/presets/share/{share_id}` - Update share
4. `DELETE /api/presets/share/{share_id}` - Revoke share
5. `POST /api/presets/export` - Export presets
6. `POST /api/presets/import` - Import presets

**Features**:
- Sharing with permissions
- Accept/revoke sharing
- JSON export/import

**Estimated Lines**: 150

---

## ✅ Implementation Checklist

### Pre-requisites
- [x] Helper utilities created (`utils/preset_helpers.py`)
- [x] Models defined (`documents_presets.py`)
- [x] Schemas defined (`schemas_presets.py`)
- [x] Database integration (`db_init.py`, `database.py`)
- [x] Seed data available (`seed_presets.py`)

### Implementation Order
1. [ ] Part 1: Imports & Setup
2. [ ] Part 2: Preset Templates Endpoints
3. [ ] Part 3: User Presets Core CRUD
4. [ ] Part 4: User Presets Extended Operations
5. [ ] Part 5: Collections, Usage & Analytics
6. [ ] Part 6: Sharing & Import/Export

### Testing After Each Part
- [ ] Syntax validation (Pylance)
- [ ] Import checks
- [ ] API endpoint testing (curl)
- [ ] Response validation

---

## 🔧 Key Technical Decisions

### 1. Serialization Strategy
```python
# Use helper functions from utils/preset_helpers.py
from utils.preset_helpers import to_response, to_response_list

# Instead of:
PresetTemplateResponse.model_validate(template.model_dump())

# Use:
to_response(template, PresetTemplateResponse)
```

### 2. Error Handling Pattern
```python
try:
    # Operation
except DocumentNotFound:
    raise HTTPException(status_code=404, detail="Not found")
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
```

### 3. Authentication Placeholder
```python
def get_current_user_id() -> str:
    """Placeholder - will integrate with actual auth"""
    return "user_001"
```

### 4. Query Building Pattern
```python
query = Model.find(Model.field == value)
if filter_param:
    query = query.find(Model.other_field == filter_param)
# Chain filters before execution
results = await query.to_list()
```

---

## 📊 Endpoint Summary

| Group | Endpoints | Lines |
|-------|-----------|-------|
| Templates | 3 | 110 |
| User Presets Core | 5 | 170 |
| User Presets Extended | 3 | 100 |
| Collections | 4 | 80 |
| Usage & Analytics | 2 | 70 |
| Sharing | 4 | 70 |
| Import/Export | 2 | 80 |
| **Total** | **23** | **~750** |

---

## 🎯 Success Criteria

### Code Quality
- ✅ All imports valid
- ✅ No syntax errors
- ✅ Type hints complete
- ✅ Docstrings for all endpoints

### Functionality
- ✅ All 23 endpoints working
- ✅ Proper error handling
- ✅ Correct serialization
- ✅ Database operations succeed

### Performance
- ✅ Efficient queries (use indexes)
- ✅ Pagination implemented
- ✅ No N+1 queries

---

**Ready to implement**: Yes ✅
**Estimated time**: 60-90 minutes
**Parts to create**: 6
