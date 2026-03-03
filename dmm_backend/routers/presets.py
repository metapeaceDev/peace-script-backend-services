"""
Custom Presets Router
=====================
RESTful API endpoints for managing camera director presets.

Features:
- Preset Templates (system-defined presets)
- User Presets (custom user presets)
- Collections (organize presets)
- Usage Logging & Analytics
- Sharing & Collaboration
- Import/Export

Total Endpoints: 23
"""

from fastapi import APIRouter, HTTPException, Query, status, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from beanie import PydanticObjectId
from beanie.operators import In, And, Or
import logging

logger = logging.getLogger(__name__)

# Import authentication
from dependencies.auth import get_current_user, get_optional_user, get_admin_user
from documents import User

# Import helper utilities
from utils.preset_helpers import to_response, to_response_list, serialize_document
from utils.preset_validators import PresetValidator

# Import models
from documents_presets import (
    PresetTemplate,
    UserPreset,
    PresetCollection,
    PresetUsageLog,
    PresetShare,
    PresetCategory,
    PresetVisibility,
)

# Import schemas
from schemas_presets import (
    # Template schemas
    PresetTemplateResponse,
    PresetTemplateCreate,
    PresetTemplateListResponse,
    
    # User preset schemas
    UserPresetResponse,
    UserPresetCreate,
    UserPresetUpdate,
    UserPresetListResponse,
    
    # Collection schemas
    PresetCollectionResponse,
    PresetCollectionCreate,
    PresetCollectionUpdate,
    
    # Usage schemas
    PresetUsageLogCreate,
    PresetUsageStatsResponse,
    
    # Share schemas
    PresetShareResponse,
    PresetShareCreate,
    PresetShareUpdate,
    
    # Batch & utility schemas
    BatchPresetOperation,
    BatchOperationResult,
    PresetExportData,
    PresetImportData,
)


# Initialize router
router = APIRouter(
    prefix="/api/presets",
    tags=["Custom Presets"],
)

# Initialize logger
logger = logging.getLogger(__name__)


# ============================================================================
# Helper Functions
# ============================================================================

# NOTE: Authentication is now handled via FastAPI Depends
# Use: current_user: User = Depends(get_current_user)
# Access user ID via: str(current_user.id)


async def check_preset_access(preset_id: str, user_id: str) -> UserPreset:
    """
    Check if user has access to a preset.
    
    Args:
        preset_id: Preset ID to check
        user_id: User ID requesting access
        
    Returns:
        UserPreset: The preset if accessible
        
    Raises:
        HTTPException: 400 if invalid ID, 404 if not found, 403 if no access
    """
    try:
        # Validate preset_id format
        try:
            obj_id = PydanticObjectId(preset_id)
        except Exception as e:
            logger.warning(f"Invalid preset ID format: {preset_id}, error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid preset ID format"
            )
        
        preset = await UserPreset.get(obj_id)
        if not preset:
            logger.warning(f"Preset not found: {preset_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Preset not found"
            )
        
        # Check ownership or sharing
        if preset.user_id != user_id:
            # Check if shared with user
            share = await PresetShare.find_one(
                PresetShare.preset_id == preset_id,
                PresetShare.shared_with_user_id == user_id,
                PresetShare.status == "active"
            )
            if not share:
                logger.warning(f"Access denied for user {user_id} to preset {preset_id}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
        
        return preset
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking preset access: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify preset access"
        )


async def check_collection_access(collection_id: str, user_id: str) -> PresetCollection:
    """
    Check if user has access to a collection.
    
    Args:
        collection_id: Collection ID to check
        user_id: User ID requesting access
        
    Returns:
        PresetCollection: The collection if accessible
        
    Raises:
        HTTPException: 400 if invalid ID, 404 if not found
    """
    try:
        # Validate collection_id format
        try:
            obj_id = PydanticObjectId(collection_id)
        except Exception as e:
            logger.warning(f"Invalid collection ID format: {collection_id}, error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid collection ID format"
            )
        
        collection = await PresetCollection.get(obj_id)
        if not collection or collection.user_id != user_id:
            logger.warning(f"Collection not found or access denied: {collection_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection not found"
            )
        return collection
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking collection access: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify collection access"
        )


# ============================================================================
# Part 1 Complete - Ready for Part 2
# ============================================================================


# ============================================================================
# PART 2: Preset Templates Endpoints
# ============================================================================

@router.get("/templates", response_model=PresetTemplateListResponse)
async def get_preset_templates(
    category: Optional[PresetCategory] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """
    Get all preset templates with filtering.
    
    Query Parameters:
    - category: Filter by category
    - search: Search in name and description
    - page: Page number (default: 1)
    - limit: Items per page (default: 20, max: 100)
    
    Returns:
        PresetTemplateListResponse with templates list and pagination
    """
    try:
        # Build query
        query = PresetTemplate.find(PresetTemplate.is_active == True)
        
        # Apply filters
        if category:
            query = query.find(PresetTemplate.category == category)
        
        if search:
            # Search in name or description
            query = query.find(
                Or(
                    PresetTemplate.name.regex(search, "i"),
                    PresetTemplate.description.regex(search, "i")
                )
            )
        
        # Get total count
        total = await query.count()
        
        # Apply pagination
        skip = (page - 1) * limit
        templates = await query.skip(skip).limit(limit).to_list()
        
        # Convert to response
        return PresetTemplateListResponse(
            templates=to_response_list(templates, PresetTemplateResponse),
            total=total,
            page=page,
            page_size=limit
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch templates: {str(e)}"
        )


@router.get("/templates/{template_id}", response_model=PresetTemplateResponse)
async def get_preset_template(template_id: str):
    """
    Get a specific preset template by ID.
    
    Path Parameters:
    - template_id: Template ID (string identifier, not ObjectId)
    
    Returns:
        PresetTemplateResponse with template details
    
    Raises:
        404: Template not found
    """
    try:
        # Find by template_id field (string), not _id (ObjectId)
        template = await PresetTemplate.find_one(
            PresetTemplate.template_id == template_id,
            PresetTemplate.is_active == True
        )
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        return to_response(template, PresetTemplateResponse)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch template: {str(e)}"
        )


@router.post("/templates", response_model=PresetTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_preset_template(
    template_data: PresetTemplateCreate,
    admin_user: User = Depends(get_admin_user)
):
    """
    Create a new preset template (Admin only).
    ✅ IMPLEMENTED: Admin authentication with JWT required
    
    Request Body:
    - template_data: PresetTemplateCreate schema
    
    Security:
    - Requires: Bearer token with admin role
    
    Returns:
        PresetTemplateResponse with created template
    
    Raises:
        401: Unauthorized (invalid/missing token)
        403: Forbidden (not admin)
        400: Invalid data
    """
    try:
        # ✅ Admin authorization - handled by get_admin_user dependency
        logger.info(
            f"Admin {admin_user.email} creating preset template: {template_data.name}",
            extra={"admin_id": str(admin_user.id), "template_name": template_data.name}
        )
        
        # Create template
        template = PresetTemplate(
            **template_data.model_dump(),
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        await template.insert()
        
        return to_response(template, PresetTemplateResponse)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create template: {str(e)}"
        )


# ============================================================================
# Part 2 Complete - Templates Endpoints Working
# ============================================================================


# ============================================================================
# PART 3: User Presets Core CRUD
# ============================================================================

@router.get("/user", response_model=UserPresetListResponse)
async def get_user_presets(
    category: Optional[PresetCategory] = None,
    visibility: Optional[PresetVisibility] = None,
    is_favorite: Optional[bool] = None,
    folder_id: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = Query("updated_at", regex="^(name|created_at|updated_at|usage_count)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's custom presets with advanced filtering and sorting.
    
    Query Parameters:
    - category: Filter by category
    - visibility: Filter by visibility (private, team, organization, public)
    - is_favorite: Filter favorites only
    - folder_id: Filter by collection/folder
    - search: Search in name and description
    - sort_by: Sort field (name, created_at, updated_at, usage_count)
    - sort_order: Sort order (asc, desc)
    - page: Page number
    - limit: Items per page
    
    Returns:
        UserPresetListResponse with presets list and pagination
    """
    try:
        user_id = str(current_user.id)
        
        # Build query
        query = UserPreset.find(UserPreset.user_id == user_id)
        
        # Apply filters
        if category:
            query = query.find(UserPreset.category == category)
        
        if visibility:
            query = query.find(UserPreset.visibility == visibility)
        
        if is_favorite is not None:
            query = query.find(UserPreset.is_favorite == is_favorite)
        
        if folder_id:
            query = query.find(UserPreset.folder_id == folder_id)
        
        if search:
            query = query.find(
                Or(
                    UserPreset.name.regex(search, "i"),
                    UserPreset.description.regex(search, "i")
                )
            )
        
        # Get total count
        total = await query.count()
        
        # Apply sorting
        sort_direction = 1 if sort_order == "asc" else -1
        query = query.sort((sort_by, sort_direction))
        
        # Apply pagination
        skip = (page - 1) * limit
        presets = await query.skip(skip).limit(limit).to_list()
        
        # Convert to response
        return UserPresetListResponse(
            presets=to_response_list(presets, UserPresetResponse),
            total=total,
            page=page,
            page_size=limit
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch presets: {str(e)}"
        )


@router.get("/user/{preset_id}", response_model=UserPresetResponse)
async def get_user_preset(preset_id: str, current_user: User = Depends(get_current_user)):
    """
    Get detailed information about a specific user preset.
    
    Path Parameters:
    - preset_id: Preset ID
    
    Returns:
        UserPresetResponse with full preset details
    
    Raises:
        400: Invalid preset ID format
        404: Preset not found or no access
        500: Server error
    """
    try:
        user_id = str(current_user.id)
        logger.info(f"User {user_id} requesting preset {preset_id}")
        
        preset = await check_preset_access(preset_id, user_id)
        
        logger.info(f"Successfully retrieved preset {preset_id} for user {user_id}")
        return to_response(preset, UserPresetResponse)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch preset {preset_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch preset"
        )


@router.post("/user", response_model=UserPresetResponse, status_code=status.HTTP_201_CREATED)
async def create_user_preset(preset_data: UserPresetCreate, current_user: User = Depends(get_current_user)):
    """
    Create a new custom user preset.
    
    Request Body:
    - preset_data: UserPresetCreate schema with config and parameters
    
    Returns:
        UserPresetResponse with created preset
    
    Raises:
        400: Invalid preset data or validation error
        500: Server error
    """
    try:
        user_id = str(current_user.id)
        logger.info(f"User {user_id} creating new preset: {preset_data.name}")
        
        # ✅ Comprehensive validation using PresetValidator
        PresetValidator.validate_preset_create(
            name=preset_data.name,
            category=preset_data.category,
            config=preset_data.config,
            description=preset_data.description,
            visibility=preset_data.visibility
        )
        
        logger.info(f"Validation passed for preset: {preset_data.name}")
        
        # Create preset with user ownership
        preset = UserPreset(
            **preset_data.model_dump(),
            user_id=user_id,
            is_favorite=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        await preset.insert()
        
        logger.info(f"Successfully created preset {preset.id} for user {user_id}")
        return to_response(preset, UserPresetResponse)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create preset: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create preset"
        )


@router.put("/user/{preset_id}", response_model=UserPresetResponse)
async def update_user_preset(preset_id: str, preset_data: UserPresetUpdate, current_user: User = Depends(get_current_user)):
    """
    Update an existing user preset.
    
    Path Parameters:
    - preset_id: Preset ID to update
    
    Request Body:
    - preset_data: UserPresetUpdate schema with updated fields
    
    Returns:
        UserPresetResponse with updated preset
    
    Raises:
        400: Invalid preset ID or data
        403: No edit permission
        404: Preset not found
        500: Server error
    """
    try:
        user_id = str(current_user.id)
        logger.info(f"User {user_id} updating preset {preset_id}")
        
        preset = await check_preset_access(preset_id, user_id)
        
        # Check if user owns the preset
        if preset.user_id != user_id:
            logger.warning(f"User {user_id} attempted to edit preset {preset_id} without ownership")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only preset owner can edit"
            )
        
        # ✅ Validate updates using PresetValidator
        update_data = preset_data.model_dump(exclude_unset=True)
        PresetValidator.validate_preset_update(update_data)
        
        logger.info(f"Validation passed for preset update: {preset_id}")
        
        # Update fields
        for field, value in update_data.items():
            setattr(preset, field, value)
        
        preset.updated_at = datetime.now()
        await preset.save()
        
        logger.info(f"Successfully updated preset {preset_id}")
        return to_response(preset, UserPresetResponse)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update preset {preset_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preset"
        )


@router.delete("/user/{preset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_preset(preset_id: str, current_user: User = Depends(get_current_user)):
    """
    Delete a user preset.
    
    Path Parameters:
    - preset_id: Preset ID to delete
    
    Returns:
        204 No Content on success
    
    Raises:
        400: Invalid preset ID
        403: No delete permission
        404: Preset not found
        500: Server error
    """
    try:
        user_id = str(current_user.id)
        logger.info(f"User {user_id} deleting preset {preset_id}")
        
        preset = await check_preset_access(preset_id, user_id)
        
        # Check if user owns the preset
        if preset.user_id != user_id:
            logger.warning(f"User {user_id} attempted to delete preset {preset_id} without ownership")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only preset owner can delete"
            )
        
        await preset.delete()
        
        logger.info(f"Successfully deleted preset {preset_id}")
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete preset {preset_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete preset"
        )


# ============================================================================
# Part 3 Complete - User Presets CRUD Working
# ============================================================================


# ============================================================================
# PART 4: User Presets Extended Operations
# ============================================================================

@router.post("/user/{preset_id}/duplicate", response_model=UserPresetResponse, status_code=status.HTTP_201_CREATED)
async def duplicate_user_preset(preset_id: str, new_name: Optional[str] = None, current_user: User = Depends(get_current_user)):
    """
    Duplicate an existing preset.
    
    Path Parameters:
    - preset_id: Preset ID to duplicate
    
    Query Parameters:
    - new_name: Optional new name for duplicated preset
    
    Returns:
        UserPresetResponse with new duplicated preset
    
    Raises:
        404: Preset not found or no access
    """
    try:
        user_id = str(current_user.id)
        original_preset = await check_preset_access(preset_id, user_id)
        
        # Create duplicate
        preset_dict = serialize_document(original_preset)
        preset_dict.pop('_id', None)
        preset_dict.pop('id', None)
        
        # Update metadata
        preset_dict['name'] = new_name or f"{original_preset.name} (Copy)"
        preset_dict['user_id'] = user_id
        preset_dict['is_favorite'] = False
        preset_dict['created_at'] = datetime.now()
        preset_dict['updated_at'] = datetime.now()
        
        # Reset usage stats if present
        if 'usage_stats' in preset_dict:
            preset_dict['usage_stats']['usage_count'] = 0
            preset_dict['usage_stats']['last_used'] = None
        
        new_preset = UserPreset(**preset_dict)
        await new_preset.insert()
        
        return to_response(new_preset, UserPresetResponse)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to duplicate preset: {str(e)}"
        )


@router.post("/user/{preset_id}/favorite", response_model=UserPresetResponse)
async def toggle_preset_favorite(preset_id: str, current_user: User = Depends(get_current_user)):
    """
    Toggle favorite status of a preset.
    
    Path Parameters:
    - preset_id: Preset ID to toggle favorite
    
    Returns:
        UserPresetResponse with updated favorite status
    
    Raises:
        404: Preset not found or no access
    """
    try:
        user_id = str(current_user.id)
        preset = await check_preset_access(preset_id, user_id)
        
        # Toggle favorite
        preset.is_favorite = not preset.is_favorite
        preset.updated_at = datetime.now()
        await preset.save()
        
        return to_response(preset, UserPresetResponse)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle favorite: {str(e)}"
        )


@router.post("/user/batch", response_model=BatchOperationResult)
async def batch_preset_operations(operation: BatchPresetOperation, current_user: User = Depends(get_current_user)):
    """
    Perform batch operations on multiple presets.
    
    Request Body:
    - operation: BatchPresetOperation with action and preset IDs
    
    Supported actions:
    - delete: Delete multiple presets
    - favorite: Mark multiple presets as favorite
    - unfavorite: Remove favorite from multiple presets
    - move: Move presets to a folder/collection
    
    Returns:
        BatchOperationResult with success/failure counts
    """
    try:
        user_id = str(current_user.id)
        success_count = 0
        failed_ids = []
        
        for preset_id in operation.preset_ids:
            try:
                preset = await check_preset_access(preset_id, user_id)
                
                # Check ownership for modifying operations
                if preset.user_id != user_id:
                    failed_ids.append(preset_id)
                    continue
                
                # Perform action
                if operation.action == "delete":
                    await preset.delete()
                    success_count += 1
                    
                elif operation.action == "favorite":
                    preset.is_favorite = True
                    preset.updated_at = datetime.now()
                    await preset.save()
                    success_count += 1
                    
                elif operation.action == "unfavorite":
                    preset.is_favorite = False
                    preset.updated_at = datetime.now()
                    await preset.save()
                    success_count += 1
                    
                elif operation.action == "move":
                    if not operation.target_folder_id:
                        failed_ids.append(preset_id)
                        continue
                    preset.folder_id = operation.target_folder_id
                    preset.updated_at = datetime.now()
                    await preset.save()
                    success_count += 1
                    
                else:
                    failed_ids.append(preset_id)
                    
            except Exception:
                failed_ids.append(preset_id)
        
        return BatchOperationResult(
            success_count=success_count,
            failed_count=len(failed_ids),
            failed_ids=failed_ids
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch operation failed: {str(e)}"
        )


# ============================================================================
# Part 4 Complete - Extended Operations Working
# ============================================================================


# ============================================================================
# PART 5: Collections, Usage & Analytics
# ============================================================================

@router.get("/collections", response_model=List[PresetCollectionResponse])
async def get_preset_collections(current_user: User = Depends(get_current_user)):
    """
    Get all preset collections/folders for the current user.
    
    Returns:
        List[PresetCollectionResponse] with user's collections
    """
    try:
        user_id = str(current_user.id)
        
        collections = await PresetCollection.find(
            PresetCollection.user_id == user_id
        ).sort("sort_order").to_list()
        
        return to_response_list(collections, PresetCollectionResponse)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch collections: {str(e)}"
        )


@router.post("/collections", response_model=PresetCollectionResponse, status_code=status.HTTP_201_CREATED)
async def create_preset_collection(collection_data: PresetCollectionCreate, current_user: User = Depends(get_current_user)):
    """
    Create a new preset collection/folder.
    
    Request Body:
    - collection_data: PresetCollectionCreate schema
    
    Returns:
        PresetCollectionResponse with created collection
    """
    try:
        user_id = str(current_user.id)
        
        # Get max sort_order
        existing = await PresetCollection.find(
            PresetCollection.user_id == user_id
        ).sort("-sort_order").limit(1).to_list()
        
        sort_order = (existing[0].sort_order + 1) if existing else 0
        
        collection = PresetCollection(
            **collection_data.model_dump(),
            user_id=user_id,
            sort_order=sort_order,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        await collection.insert()
        
        return to_response(collection, PresetCollectionResponse)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create collection: {str(e)}"
        )


@router.put("/collections/{collection_id}", response_model=PresetCollectionResponse)
async def update_preset_collection(collection_id: str, collection_data: PresetCollectionUpdate, current_user: User = Depends(get_current_user)):
    """
    Update a preset collection.
    
    Path Parameters:
    - collection_id: Collection ID to update
    
    Request Body:
    - collection_data: PresetCollectionUpdate schema
    
    Returns:
        PresetCollectionResponse with updated collection
    """
    try:
        user_id = str(current_user.id)
        collection = await check_collection_access(collection_id, user_id)
        
        # Update fields
        update_data = collection_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(collection, field, value)
        
        collection.updated_at = datetime.now()
        await collection.save()
        
        return to_response(collection, PresetCollectionResponse)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update collection: {str(e)}"
        )


@router.delete("/collections/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_preset_collection(collection_id: str, current_user: User = Depends(get_current_user)):
    """
    Delete a preset collection.
    Note: Presets in the collection will not be deleted, just unassigned.
    
    Path Parameters:
    - collection_id: Collection ID to delete
    
    Returns:
        204 No Content on success
    """
    try:
        user_id = str(current_user.id)
        collection = await check_collection_access(collection_id, user_id)
        
        # Unassign presets from this collection
        presets = await UserPreset.find(
            UserPreset.folder_id == collection_id
        ).to_list()
        
        for preset in presets:
            preset.folder_id = None
            await preset.save()
        
        await collection.delete()
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete collection: {str(e)}"
        )


@router.post("/usage", status_code=status.HTTP_201_CREATED)
async def log_preset_usage(usage_data: PresetUsageLogCreate, current_user: User = Depends(get_current_user)):
    """
    Log preset usage for analytics.
    
    Request Body:
    - usage_data: PresetUsageLogCreate with preset_id, scene_id, etc.
    
    Returns:
        201 Created on success
    """
    try:
        user_id = str(current_user.id)
        
        # Create usage log
        usage_log = PresetUsageLog(
            **usage_data.model_dump(),
            user_id=user_id,
            used_at=datetime.now()
        )
        
        await usage_log.insert()
        
        # Update preset usage stats
        preset = await UserPreset.get(PydanticObjectId(usage_data.preset_id))
        if preset:
            if not preset.usage_stats:
                from documents_presets import PresetUsageStats
                preset.usage_stats = PresetUsageStats(
                    usage_count=0,
                    last_used=None,
                    avg_rating=0.0
                )
            
            preset.usage_stats.usage_count += 1
            preset.usage_stats.last_used = datetime.now()
            await preset.save()
        
        return {"message": "Usage logged successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log usage: {str(e)}"
        )


@router.get("/usage/stats", response_model=PresetUsageStatsResponse)
async def get_preset_usage_stats(
    preset_id: Optional[str] = None,
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user)
):
    """
    Get usage statistics for presets.
    
    Query Parameters:
    - preset_id: Optional specific preset ID
    - days: Number of days to analyze (default: 30, max: 365)
    
    Returns:
        PresetUsageStatsResponse with aggregated statistics
    """
    try:
        user_id = str(current_user.id)
        
        # Calculate date range
        from_date = datetime.now() - timedelta(days=days)
        
        # Build query
        query = PresetUsageLog.find(
            PresetUsageLog.user_id == user_id,
            PresetUsageLog.used_at >= from_date
        )
        
        if preset_id:
            query = query.find(PresetUsageLog.preset_id == preset_id)
        
        # Get logs
        logs = await query.to_list()
        
        # Aggregate stats
        total_uses = len(logs)
        unique_presets = len(set(log.preset_id for log in logs))
        
        # Most used presets
        preset_counts = {}
        for log in logs:
            preset_counts[log.preset_id] = preset_counts.get(log.preset_id, 0) + 1
        
        most_used = sorted(preset_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return PresetUsageStatsResponse(
            total_uses=total_uses,
            unique_presets=unique_presets,
            most_used_presets=[{"preset_id": pid, "count": count} for pid, count in most_used],
            date_range_days=days
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get usage stats: {str(e)}"
        )


# ============================================================================
# Part 5 Complete - Collections & Analytics Working
# ============================================================================


# ============================================================================
# PART 6: Sharing & Import/Export
# ============================================================================

@router.post("/share", response_model=PresetShareResponse, status_code=status.HTTP_201_CREATED)
async def share_preset(share_data: PresetShareCreate, current_user: User = Depends(get_current_user)):
    """
    Share a preset with another user or team.
    
    Request Body:
    - share_data: PresetShareCreate with preset_id, shared_with_user_id, permissions
    
    Returns:
        PresetShareResponse with share details
    """
    try:
        user_id = str(current_user.id)
        
        # Check if user owns the preset
        preset = await check_preset_access(share_data.preset_id, user_id)
        if preset.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only preset owner can share"
            )
        
        # Check if already shared
        existing = await PresetShare.find_one(
            PresetShare.preset_id == share_data.preset_id,
            PresetShare.shared_with_user_id == share_data.shared_with_user_id
        )
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Preset already shared with this user"
            )
        
        # Create share
        share = PresetShare(
            **share_data.model_dump(),
            shared_by_user_id=user_id,
            status="pending",
            shared_at=datetime.now()
        )
        
        await share.insert()
        
        return to_response(share, PresetShareResponse)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to share preset: {str(e)}"
        )


@router.get("/shared-with-me", response_model=List[PresetShareResponse])
async def get_shared_presets(status_filter: Optional[str] = Query(None, regex="^(pending|active|revoked)$"), current_user: User = Depends(get_current_user)):
    """
    Get presets shared with the current user.
    
    Query Parameters:
    - status_filter: Filter by share status (pending, active, revoked)
    
    Returns:
        List[PresetShareResponse] with shared presets
    """
    try:
        user_id = str(current_user.id)
        
        query = PresetShare.find(PresetShare.shared_with_user_id == user_id)
        
        if status_filter:
            query = query.find(PresetShare.status == status_filter)
        
        shares = await query.sort("-shared_at").to_list()
        
        return to_response_list(shares, PresetShareResponse)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch shared presets: {str(e)}"
        )


@router.put("/share/{share_id}", response_model=PresetShareResponse)
async def update_preset_share(share_id: str, share_data: PresetShareUpdate, current_user: User = Depends(get_current_user)):
    """
    Update share permissions or accept/reject share.
    
    Path Parameters:
    - share_id: Share ID to update
    
    Request Body:
    - share_data: PresetShareUpdate with updated fields
    
    Returns:
        PresetShareResponse with updated share
    """
    try:
        user_id = str(current_user.id)
        
        share = await PresetShare.get(PydanticObjectId(share_id))
        if not share:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Share not found"
            )
        
        # Check if user is owner or recipient
        if share.shared_by_user_id != user_id and share.shared_with_user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Update fields
        update_data = share_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(share, field, value)
        
        await share.save()
        
        return to_response(share, PresetShareResponse)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update share: {str(e)}"
        )


@router.delete("/share/{share_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_preset_share(share_id: str, current_user: User = Depends(get_current_user)):
    """
    Revoke a preset share.
    
    Path Parameters:
    - share_id: Share ID to revoke
    
    Returns:
        204 No Content on success
    """
    try:
        user_id = str(current_user.id)
        
        share = await PresetShare.get(PydanticObjectId(share_id))
        if not share:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Share not found"
            )
        
        # Only owner can revoke
        if share.shared_by_user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only share owner can revoke"
            )
        
        share.status = "revoked"
        await share.save()
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke share: {str(e)}"
        )


@router.post("/export")
async def export_presets(preset_ids: Optional[List[str]] = None, current_user: User = Depends(get_current_user)):
    """
    Export presets to JSON format.
    
    Request Body:
    - preset_ids: Optional list of preset IDs to export (if empty, exports all)
    
    Returns:
        PresetExportData with presets in JSON format
    """
    try:
        user_id = str(current_user.id)
        
        # Get presets to export
        if preset_ids:
            presets = []
            for pid in preset_ids:
                preset = await check_preset_access(pid, user_id)
                presets.append(preset)
        else:
            presets = await UserPreset.find(UserPreset.user_id == user_id).to_list()
        
        # Serialize presets
        export_data = []
        for preset in presets:
            preset_dict = serialize_document(preset)
            # Remove internal fields
            preset_dict.pop('_id', None)
            preset_dict.pop('id', None)
            preset_dict.pop('user_id', None)
            export_data.append(preset_dict)
        
        return PresetExportData(
            version="1.0",
            exported_at=datetime.now(),
            presets=export_data,
            count=len(export_data)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export presets: {str(e)}"
        )


@router.post("/import")
async def import_presets(import_data: PresetImportData, current_user: User = Depends(get_current_user)):
    """
    Import presets from JSON format.
    
    Request Body:
    - import_data: PresetImportData with presets array
    
    Returns:
        Import summary with success/failure counts
    """
    try:
        user_id = str(current_user.id)
        
        success_count = 0
        failed_count = 0
        errors = []
        
        for preset_data in import_data.presets:
            try:
                # Add user ownership
                preset_data['user_id'] = user_id
                preset_data['created_at'] = datetime.now()
                preset_data['updated_at'] = datetime.now()
                preset_data['is_favorite'] = False
                
                # Reset usage stats
                if 'usage_stats' in preset_data:
                    preset_data['usage_stats']['usage_count'] = 0
                    preset_data['usage_stats']['last_used'] = None
                
                preset = UserPreset(**preset_data)
                await preset.insert()
                success_count += 1
                
            except Exception as e:
                failed_count += 1
                errors.append(f"Failed to import preset: {str(e)}")
        
        return {
            "success_count": success_count,
            "failed_count": failed_count,
            "errors": errors if errors else None,
            "message": f"Imported {success_count} presets successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {str(e)}"
        )


# ============================================================================
# Part 6 Complete - ALL 23 ENDPOINTS IMPLEMENTED! 🎉
# ============================================================================
