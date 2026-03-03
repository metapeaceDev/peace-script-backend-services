"""
Image Gallery & Album Router

Handles Character Profile Image Albums (separate from Video Albums).
Supports connections to Shots, Storyboards, Scenes for production workflow.

Endpoints:
- POST   /api/image-gallery/create           - Create image album
- GET    /api/image-gallery/{album_id}       - Get album with images
- PUT    /api/image-gallery/{album_id}       - Update album
- DELETE /api/image-gallery/{album_id}       - Delete album
- GET    /api/image-gallery/list             - List albums
- POST   /api/image-gallery/{id}/add-image   - Add image to album
- DELETE /api/image-gallery/{id}/remove-image/{image_id} - Remove image
- GET    /api/image-gallery/search           - Search albums/images
- GET    /api/image-gallery/by-shot/{shot_id} - Get albums for shot
- GET    /api/image-gallery/by-storyboard/{storyboard_id} - Get albums for storyboard
- GET    /api/image-gallery/by-actor/{actor_id} - Get albums for actor
"""

from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

from documents_gallery import ImageAlbum
from kamma_appearance_models import GeneratedImageDocument, GeneratedImageMetadata

router = APIRouter(prefix="/api/image-gallery", tags=["Image Gallery"])


# ============================================================================
# Request/Response Models
# ============================================================================

class CreateImageAlbumRequest(BaseModel):
    """Create image album request"""
    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    
    # Associations
    actor_id: Optional[str] = None
    project_id: Optional[str] = None
    scene_id: Optional[str] = None
    shot_id: Optional[str] = None
    storyboard_id: Optional[str] = None
    
    tags: List[str] = Field(default_factory=list)
    is_system: bool = False


class UpdateImageAlbumRequest(BaseModel):
    """Update image album request"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    cover_image_id: Optional[str] = None
    tags: Optional[List[str]] = None


class ImageAlbumResponse(BaseModel):
    """Image album response"""
    album_id: str
    name: str
    description: Optional[str]
    
    # Associations
    actor_id: Optional[str]
    project_id: Optional[str]
    scene_id: Optional[str]
    shot_id: Optional[str]
    storyboard_id: Optional[str]
    
    cover_image_id: Optional[str]
    cover_thumbnail: Optional[str] = None  # Small thumbnail of cover image
    image_count: int
    tags: List[str]
    is_system: bool
    created_at: datetime
    updated_at: datetime


class ImageResponse(BaseModel):
    """Generated image response"""
    image_id: str
    model_id: str
    actor_id: Optional[str]
    style: str
    width: int
    height: int
    thumbnail_small_base64: Optional[str] = None  # 256x256 for cards
    thumbnail_medium_base64: Optional[str] = None  # 512x512 for gallery
    is_favorite: bool
    is_profile_avatar: bool
    created_at: datetime


class ImageAlbumDetailResponse(BaseModel):
    """Image album with images"""
    album_id: str
    name: str
    description: Optional[str]
    
    # Associations
    actor_id: Optional[str]
    project_id: Optional[str]
    scene_id: Optional[str]
    shot_id: Optional[str]
    storyboard_id: Optional[str]
    
    cover_image_id: Optional[str]
    images: List[ImageResponse]
    tags: List[str]
    is_system: bool
    created_at: datetime
    updated_at: datetime


class ImageAlbumListResponse(BaseModel):
    """List of image albums"""
    albums: List[ImageAlbumResponse]
    total: int
    page: int
    page_size: int


class AddImageRequest(BaseModel):
    """Add image to album"""
    image_id: str


class SearchResponse(BaseModel):
    """Search results"""
    albums: List[ImageAlbumResponse]
    images: List[ImageResponse]
    total_albums: int
    total_images: int


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/create", response_model=ImageAlbumResponse, status_code=status.HTTP_201_CREATED)
async def create_image_album(request: CreateImageAlbumRequest):
    """Create new image album"""
    try:
        album_id = f"img_album_{uuid.uuid4().hex[:12]}"
        
        album = ImageAlbum(
            album_id=album_id,
            name=request.name,
            description=request.description,
            actor_id=request.actor_id,
            project_id=request.project_id,
            scene_id=request.scene_id,
            shot_id=request.shot_id,
            storyboard_id=request.storyboard_id,
            tags=request.tags,
            is_system=request.is_system
        )
        
        await album.insert()
        
        return ImageAlbumResponse(
            album_id=album.album_id,
            name=album.name,
            description=album.description,
            actor_id=album.actor_id,
            project_id=album.project_id,
            scene_id=album.scene_id,
            shot_id=album.shot_id,
            storyboard_id=album.storyboard_id,
            cover_image_id=album.cover_image_id,
            image_count=len(album.image_ids),
            tags=album.tags,
            is_system=album.is_system,
            created_at=album.created_at,
            updated_at=album.updated_at
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create image album: {str(e)}"
        )


@router.get("/list", response_model=ImageAlbumListResponse)
async def list_image_albums(
    actor_id: Optional[str] = None,
    project_id: Optional[str] = None,
    shot_id: Optional[str] = None,
    scene_id: Optional[str] = None,
    storyboard_id: Optional[str] = None,
    tag: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """
    List image albums with filtering and pagination.
    
    Filters:
    - actor_id: Filter by actor (character albums)
    - project_id: Filter by project
    - shot_id: Filter by shot
    - scene_id: Filter by scene
    - storyboard_id: Filter by storyboard
    - tag: Filter by tag
    """
    try:
        # Build query
        query = {}
        if actor_id:
            query["actor_id"] = actor_id
        if project_id:
            query["project_id"] = project_id
        if shot_id:
            query["shot_id"] = shot_id
        if scene_id:
            query["scene_id"] = scene_id
        if storyboard_id:
            query["storyboard_id"] = storyboard_id
        if tag:
            query["tags"] = tag
        
        # Count total
        total = await ImageAlbum.find(query).count()
        
        # Get page
        skip = (page - 1) * page_size
        albums = await ImageAlbum.find(query).skip(skip).limit(page_size).to_list()
        
        # Build responses with cover thumbnails
        album_responses = []
        for album in albums:
            cover_thumbnail = None
            if album.cover_image_id:
                cover_img = await GeneratedImageDocument.find_one(
                    GeneratedImageDocument.image_id == album.cover_image_id
                )
                if cover_img:
                    cover_thumbnail = cover_img.metadata.thumbnail_small_base64
            
            album_responses.append(ImageAlbumResponse(
                album_id=album.album_id,
                name=album.name,
                description=album.description,
                actor_id=album.actor_id,
                project_id=album.project_id,
                scene_id=album.scene_id,
                shot_id=album.shot_id,
                storyboard_id=album.storyboard_id,
                cover_image_id=album.cover_image_id,
                cover_thumbnail=cover_thumbnail,
                image_count=len(album.image_ids),
                tags=album.tags,
                is_system=album.is_system,
                created_at=album.created_at,
                updated_at=album.updated_at
            ))
        
        return ImageAlbumListResponse(
            albums=album_responses,
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list image albums: {str(e)}"
        )


@router.get("/{album_id}", response_model=ImageAlbumDetailResponse)
async def get_image_album(album_id: str):
    """Get image album with images"""
    try:
        album = await ImageAlbum.find_one(ImageAlbum.album_id == album_id)
        
        if not album:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image album {album_id} not found"
            )
        
        # Get images
        images = []
        for image_id in album.image_ids:
            img_doc = await GeneratedImageDocument.find_one(GeneratedImageDocument.image_id == image_id)
            if img_doc:
                images.append(ImageResponse(
                    image_id=img_doc.image_id,
                    model_id=img_doc.model_id,
                    actor_id=img_doc.actor_id,
                    style=img_doc.metadata.style,
                    width=img_doc.metadata.width,
                    height=img_doc.metadata.height,
                    thumbnail_small_base64=img_doc.metadata.thumbnail_small_base64,
                    thumbnail_medium_base64=img_doc.metadata.thumbnail_medium_base64,
                    is_favorite=img_doc.metadata.is_favorite,
                    is_profile_avatar=img_doc.metadata.is_profile_avatar,
                    created_at=img_doc.created_at
                ))
        
        return ImageAlbumDetailResponse(
            album_id=album.album_id,
            name=album.name,
            description=album.description,
            actor_id=album.actor_id,
            project_id=album.project_id,
            scene_id=album.scene_id,
            shot_id=album.shot_id,
            storyboard_id=album.storyboard_id,
            cover_image_id=album.cover_image_id,
            images=images,
            tags=album.tags,
            is_system=album.is_system,
            created_at=album.created_at,
            updated_at=album.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get image album: {str(e)}"
        )


@router.put("/{album_id}", response_model=ImageAlbumResponse)
async def update_image_album(album_id: str, request: UpdateImageAlbumRequest):
    """Update image album details"""
    try:
        album = await ImageAlbum.find_one(ImageAlbum.album_id == album_id)
        
        if not album:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image album {album_id} not found"
            )
        
        # Update fields
        if request.name is not None:
            album.name = request.name
        if request.description is not None:
            album.description = request.description
        if request.cover_image_id is not None:
            album.cover_image_id = request.cover_image_id
        if request.tags is not None:
            album.tags = request.tags
        
        album.updated_at = datetime.utcnow()
        await album.save()
        
        # Get cover thumbnail
        cover_thumbnail = None
        if album.cover_image_id:
            cover_img = await GeneratedImageDocument.find_one(
                GeneratedImageDocument.image_id == album.cover_image_id
            )
            if cover_img:
                cover_thumbnail = cover_img.metadata.thumbnail_small_base64
        
        return ImageAlbumResponse(
            album_id=album.album_id,
            name=album.name,
            description=album.description,
            actor_id=album.actor_id,
            project_id=album.project_id,
            scene_id=album.scene_id,
            shot_id=album.shot_id,
            storyboard_id=album.storyboard_id,
            cover_image_id=album.cover_image_id,
            cover_thumbnail=cover_thumbnail,
            image_count=len(album.image_ids),
            tags=album.tags,
            is_system=album.is_system,
            created_at=album.created_at,
            updated_at=album.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update image album: {str(e)}"
        )


@router.delete("/{album_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image_album(album_id: str):
    """Delete image album (images are not deleted)"""
    try:
        album = await ImageAlbum.find_one(ImageAlbum.album_id == album_id)
        
        if not album:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image album {album_id} not found"
            )
        
        await album.delete()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete image album: {str(e)}"
        )


@router.post("/{album_id}/add-image", response_model=ImageAlbumResponse)
async def add_image_to_album(album_id: str, request: AddImageRequest):
    """Add image to album"""
    try:
        # Check album exists
        album = await ImageAlbum.find_one(ImageAlbum.album_id == album_id)
        if not album:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image album {album_id} not found"
            )
        
        # Check image exists
        image = await GeneratedImageDocument.find_one(
            GeneratedImageDocument.image_id == request.image_id
        )
        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image {request.image_id} not found"
            )
        
        # Add to album if not already there
        if request.image_id not in album.image_ids:
            album.image_ids.append(request.image_id)
            album.updated_at = datetime.utcnow()
            await album.save()
        
        return ImageAlbumResponse(
            album_id=album.album_id,
            name=album.name,
            description=album.description,
            actor_id=album.actor_id,
            project_id=album.project_id,
            scene_id=album.scene_id,
            shot_id=album.shot_id,
            storyboard_id=album.storyboard_id,
            cover_image_id=album.cover_image_id,
            image_count=len(album.image_ids),
            tags=album.tags,
            is_system=album.is_system,
            created_at=album.created_at,
            updated_at=album.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add image to album: {str(e)}"
        )


@router.delete("/{album_id}/remove-image/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_image_from_album(album_id: str, image_id: str):
    """Remove image from album"""
    try:
        # Get album
        album = await ImageAlbum.find_one(ImageAlbum.album_id == album_id)
        if not album:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image album {album_id} not found"
            )
        
        # Remove from album
        if image_id in album.image_ids:
            album.image_ids.remove(image_id)
            album.updated_at = datetime.utcnow()
            await album.save()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove image from album: {str(e)}"
        )


@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1, description="Search query"),
    search_type: str = Query("all", regex="^(all|albums|images)$")
):
    """
    Search image albums and images.
    
    Searches in:
    - Album names and descriptions
    - Image tags and metadata
    """
    try:
        albums = []
        images = []
        
        # Search albums
        if search_type in ["all", "albums"]:
            all_albums = await ImageAlbum.find().to_list()
            albums = [
                ImageAlbumResponse(
                    album_id=a.album_id,
                    name=a.name,
                    description=a.description,
                    actor_id=a.actor_id,
                    project_id=a.project_id,
                    scene_id=a.scene_id,
                    shot_id=a.shot_id,
                    storyboard_id=a.storyboard_id,
                    cover_image_id=a.cover_image_id,
                    image_count=len(a.image_ids),
                    tags=a.tags,
                    is_system=a.is_system,
                    created_at=a.created_at,
                    updated_at=a.updated_at
                )
                for a in all_albums
                if q.lower() in a.name.lower() 
                or (a.description and q.lower() in a.description.lower())
                or any(q.lower() in tag.lower() for tag in a.tags)
            ]
        
        # Search images
        if search_type in ["all", "images"]:
            all_images = await GeneratedImageDocument.find().to_list()
            images = [
                ImageResponse(
                    image_id=img.image_id,
                    model_id=img.model_id,
                    actor_id=img.actor_id,
                    style=img.metadata.style,
                    width=img.metadata.width,
                    height=img.metadata.height,
                    thumbnail_small_base64=img.metadata.thumbnail_small_base64,
                    thumbnail_medium_base64=img.metadata.thumbnail_medium_base64,
                    is_favorite=img.metadata.is_favorite,
                    is_profile_avatar=img.metadata.is_profile_avatar,
                    created_at=img.created_at
                )
                for img in all_images
                if (img.metadata.notes and q.lower() in img.metadata.notes.lower())
                or q.lower() in img.metadata.style.lower()
            ]
        
        return SearchResponse(
            albums=albums,
            images=images,
            total_albums=len(albums),
            total_images=len(images)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


# ============================================================================
# Convenience Endpoints for Navigation
# ============================================================================

@router.get("/by-shot/{shot_id}", response_model=ImageAlbumListResponse)
async def get_albums_by_shot(shot_id: str):
    """Get all image albums for a specific shot"""
    return await list_image_albums(shot_id=shot_id, page_size=100)


@router.get("/by-storyboard/{storyboard_id}", response_model=ImageAlbumListResponse)
async def get_albums_by_storyboard(storyboard_id: str):
    """Get all image albums for a specific storyboard"""
    return await list_image_albums(storyboard_id=storyboard_id, page_size=100)


@router.get("/by-actor/{actor_id}", response_model=ImageAlbumListResponse)
async def get_albums_by_actor(actor_id: str):
    """Get all image albums for a specific actor (character profile albums)"""
    return await list_image_albums(actor_id=actor_id, page_size=100)


@router.get("/by-scene/{scene_id}", response_model=ImageAlbumListResponse)
async def get_albums_by_scene(scene_id: str):
    """Get all image albums for a specific scene"""
    return await list_image_albums(scene_id=scene_id, page_size=100)
