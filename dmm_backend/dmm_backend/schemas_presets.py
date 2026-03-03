"""
Custom Preset Schemas for API
Sprint 2: Days 9-16
Created: 28 ตุลาคม 2568
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from documents_presets import (
    PresetCategory,
    PresetVisibility,
    PresetParameter,
    PresetConfig,
    PresetUsageStats,
    PresetTag
)


# --- Request Schemas --- #

class PresetParameterCreate(BaseModel):
    """Schema for creating a preset parameter"""
    name: str
    value: Any
    type: str
    description: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    options: Optional[List[str]] = None


class PresetConfigCreate(BaseModel):
    """Schema for creating preset configuration"""
    parameters: List[PresetParameterCreate] = []
    camera_settings: Optional[Dict[str, Any]] = None
    shot_settings: Optional[Dict[str, Any]] = None
    feedback_triggers: Optional[Dict[str, Any]] = None


class PresetTagCreate(BaseModel):
    """Schema for creating a tag"""
    name: str
    color: Optional[str] = None


class PresetTemplateCreate(BaseModel):
    """Schema for creating a preset template"""
    name: str
    description: str
    category: PresetCategory
    config: PresetConfigCreate
    thumbnail_url: Optional[str] = None
    preview_data: Optional[Dict[str, Any]] = None
    tags: List[PresetTagCreate] = []


class UserPresetCreate(BaseModel):
    """Schema for creating a user preset"""
    name: str
    description: Optional[str] = None
    category: PresetCategory
    visibility: PresetVisibility = PresetVisibility.PRIVATE
    config: PresetConfigCreate
    based_on_template_id: Optional[str] = None
    shared_with: List[str] = []
    thumbnail_url: Optional[str] = None
    preview_data: Optional[Dict[str, Any]] = None
    tags: List[PresetTagCreate] = []
    folder: Optional[str] = None


class UserPresetUpdate(BaseModel):
    """Schema for updating a user preset"""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[PresetCategory] = None
    visibility: Optional[PresetVisibility] = None
    config: Optional[PresetConfigCreate] = None
    shared_with: Optional[List[str]] = None
    thumbnail_url: Optional[str] = None
    preview_data: Optional[Dict[str, Any]] = None
    tags: Optional[List[PresetTagCreate]] = None
    folder: Optional[str] = None
    is_favorite: Optional[bool] = None
    rating: Optional[float] = None


class PresetCollectionCreate(BaseModel):
    """Schema for creating a preset collection"""
    name: str
    description: Optional[str] = None
    preset_ids: List[str] = []
    icon: Optional[str] = None
    color: Optional[str] = None
    parent_collection_id: Optional[str] = None


class PresetCollectionUpdate(BaseModel):
    """Schema for updating a preset collection"""
    name: Optional[str] = None
    description: Optional[str] = None
    preset_ids: Optional[List[str]] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class PresetUsageLogCreate(BaseModel):
    """Schema for logging preset usage"""
    preset_id: str
    preset_type: str
    project_id: Optional[str] = None
    scene_id: Optional[str] = None
    shot_id: Optional[str] = None
    duration_seconds: Optional[int] = None
    success: bool = True
    rating: Optional[float] = None
    feedback_text: Optional[str] = None
    modified_parameters: Optional[Dict[str, Any]] = None


class PresetShareCreate(BaseModel):
    """Schema for sharing a preset"""
    preset_id: str
    shared_with_user_id: str
    can_view: bool = True
    can_edit: bool = False
    can_reshare: bool = False
    expires_at: Optional[datetime] = None
    message: Optional[str] = None


class PresetShareUpdate(BaseModel):
    """Schema for updating a preset share"""
    can_view: Optional[bool] = None
    can_edit: Optional[bool] = None
    can_reshare: Optional[bool] = None
    accepted: Optional[bool] = None


# --- Response Schemas --- #

class PresetParameterResponse(BaseModel):
    """Response schema for preset parameter"""
    name: str
    value: Any
    type: str
    description: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    options: Optional[List[str]] = None


class PresetConfigResponse(BaseModel):
    """Response schema for preset configuration"""
    parameters: List[PresetParameterResponse] = []
    camera_settings: Optional[Dict[str, Any]] = None
    shot_settings: Optional[Dict[str, Any]] = None
    feedback_triggers: Optional[Dict[str, Any]] = None


class PresetTagResponse(BaseModel):
    """Response schema for tag"""
    name: str
    color: Optional[str] = None


class PresetUsageStatsResponse(BaseModel):
    """Response schema for usage statistics"""
    total_uses: int = 0
    successful_uses: int = 0
    failed_uses: int = 0
    average_rating: float = 0.0
    last_used: Optional[datetime] = None


class PresetTemplateResponse(BaseModel):
    """Response schema for preset template"""
    template_id: str
    name: str
    description: str
    category: PresetCategory
    visibility: PresetVisibility
    config: PresetConfigResponse
    thumbnail_url: Optional[str] = None
    preview_data: Optional[Dict[str, Any]] = None
    tags: List[PresetTagResponse] = []
    created_by: str
    created_at: datetime
    updated_at: datetime
    usage_stats: PresetUsageStatsResponse
    version: str
    is_active: bool

    class Config:
        from_attributes = True


class UserPresetResponse(BaseModel):
    """Response schema for user preset"""
    preset_id: str
    name: str
    description: Optional[str] = None
    category: PresetCategory
    visibility: PresetVisibility
    config: PresetConfigResponse
    based_on_template_id: Optional[str] = None
    is_modified: bool
    owner_id: str
    shared_with: List[str] = []
    thumbnail_url: Optional[str] = None
    preview_data: Optional[Dict[str, Any]] = None
    tags: List[PresetTagResponse] = []
    folder: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_used: Optional[datetime] = None
    usage_stats: PresetUsageStatsResponse
    is_favorite: bool
    rating: Optional[float] = None
    version: str
    is_active: bool

    class Config:
        from_attributes = True


class PresetCollectionResponse(BaseModel):
    """Response schema for preset collection"""
    collection_id: str
    name: str
    description: Optional[str] = None
    owner_id: str
    preset_ids: List[str] = []
    icon: Optional[str] = None
    color: Optional[str] = None
    parent_collection_id: Optional[str] = None
    sort_order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PresetUsageLogResponse(BaseModel):
    """Response schema for preset usage log"""
    log_id: str
    preset_id: str
    preset_type: str
    user_id: str
    project_id: Optional[str] = None
    scene_id: Optional[str] = None
    shot_id: Optional[str] = None
    used_at: datetime
    duration_seconds: Optional[int] = None
    success: bool
    rating: Optional[float] = None
    feedback_text: Optional[str] = None
    modified_parameters: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class PresetShareResponse(BaseModel):
    """Response schema for preset share"""
    share_id: str
    preset_id: str
    shared_by_user_id: str
    shared_with_user_id: str
    can_view: bool
    can_edit: bool
    can_reshare: bool
    accepted: bool
    accepted_at: Optional[datetime] = None
    shared_at: datetime
    expires_at: Optional[datetime] = None
    message: Optional[str] = None

    class Config:
        from_attributes = True


# --- List Response Schemas --- #

class PresetTemplateListResponse(BaseModel):
    """Response schema for list of preset templates"""
    templates: List[PresetTemplateResponse]
    total: int
    page: int
    page_size: int


class UserPresetListResponse(BaseModel):
    """Response schema for list of user presets"""
    presets: List[UserPresetResponse]
    total: int
    page: int
    page_size: int


class PresetCollectionListResponse(BaseModel):
    """Response schema for list of preset collections"""
    collections: List[PresetCollectionResponse]
    total: int


# --- Filter/Query Schemas --- #

class PresetFilterParams(BaseModel):
    """Query parameters for filtering presets"""
    category: Optional[PresetCategory] = None
    visibility: Optional[PresetVisibility] = None
    tags: Optional[List[str]] = None
    search: Optional[str] = None
    is_favorite: Optional[bool] = None
    folder: Optional[str] = None
    sort_by: Optional[str] = "updated_at"  # name, created_at, updated_at, usage
    sort_order: Optional[str] = "desc"  # asc, desc
    page: int = 1
    page_size: int = 20


class PresetDuplicateRequest(BaseModel):
    """Request to duplicate a preset"""
    preset_id: str
    new_name: Optional[str] = None


class PresetBatchOperationRequest(BaseModel):
    """Request for batch operations on presets"""
    preset_ids: List[str]
    operation: str  # "delete", "favorite", "unfavorite", "move_to_folder"
    folder: Optional[str] = None  # For move_to_folder operation


class PresetExportRequest(BaseModel):
    """Request to export presets"""
    preset_ids: List[str]
    format: str = "json"  # json, yaml, etc.


class PresetImportRequest(BaseModel):
    """Request to import presets"""
    data: str  # JSON or YAML string
    format: str = "json"
    override_existing: bool = False


# ============================================================================
# Additional Schemas for Router Compatibility
# ============================================================================

# Alias for backward compatibility
BatchPresetOperation = PresetBatchOperationRequest


class BatchOperationResult(BaseModel):
    """Result of batch operation"""
    success_count: int
    failed_count: int
    failed_ids: List[str] = []


class PresetExportData(BaseModel):
    """Export data container"""
    version: str
    exported_at: datetime
    presets: List[Dict[str, Any]]
    count: int


class PresetImportData(BaseModel):
    """Import data container"""
    presets: List[Dict[str, Any]]
    version: Optional[str] = "1.0"
