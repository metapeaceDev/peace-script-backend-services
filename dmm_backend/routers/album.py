"""
Album & Gallery Router

Handles:
- Album CRUD operations
- Video organization
- Gallery browsing
- Search and filtering

Endpoints:
- POST   /api/album/create           - Create album
- GET    /api/album/{album_id}       - Get album
- PUT    /api/album/{album_id}       - Update album
- DELETE /api/album/{album_id}       - Delete album
- GET    /api/album/list             - List albums
- POST   /api/album/{id}/add-video   - Add video to album
- DELETE /api/album/{id}/remove-video/{video_id} - Remove video
- GET    /api/album/search           - Search albums/videos
"""

from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

from documents_video import Album, GeneratedVideo
from routers.video_generation import VideoResponse

router = APIRouter(prefix="/api/album", tags=["Album & Gallery"])


# ============================================================================
# Request/Response Models
# ============================================================================

class CreateAlbumRequest(BaseModel):
    """Create album request"""
    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    project_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    is_public: bool = False


class UpdateAlbumRequest(BaseModel):
    """Update album request"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    cover_video_id: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None


class AlbumResponse(BaseModel):
    """Album response"""
    album_id: str
    project_id: Optional[str]
    name: str
    description: Optional[str]
    cover_video_id: Optional[str]
    cover_thumbnail: Optional[str] = None  # Thumbnail URL of cover video
    video_count: int
    tags: List[str]
    is_public: bool
    created_at: datetime
    updated_at: datetime


class AlbumDetailResponse(BaseModel):
    """Album with videos"""
    album_id: str
    project_id: Optional[str]
    name: str
    description: Optional[str]
    cover_video_id: Optional[str]
    videos: List[VideoResponse]
    tags: List[str]
    is_public: bool
    created_at: datetime
    updated_at: datetime


class AlbumListResponse(BaseModel):
    """List of albums"""
    albums: List[AlbumResponse]
    total: int
    page: int
    page_size: int


class AddVideoRequest(BaseModel):
    """Add video to album"""
    video_id: str


class SearchResponse(BaseModel):
    """Search results"""
    albums: List[AlbumResponse]
    videos: List[VideoResponse]
    total_albums: int
    total_videos: int


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/create", response_model=AlbumResponse, status_code=status.HTTP_201_CREATED)
async def create_album(request: CreateAlbumRequest):
    """Create new album"""
    try:
        album_id = f"album_{uuid.uuid4().hex[:12]}"
        
        album = Album(
            album_id=album_id,
            project_id=request.project_id,
            name=request.name,
            description=request.description,
            tags=request.tags,
            is_public=request.is_public
        )
        
        await album.insert()
        
        return AlbumResponse(
            album_id=album.album_id,
            project_id=album.project_id,
            name=album.name,
            description=album.description,
            cover_video_id=album.cover_video_id,
            video_count=len(album.video_ids),
            tags=album.tags,
            is_public=album.is_public,
            created_at=album.created_at,
            updated_at=album.updated_at
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create album: {str(e)}"
        )


@router.get("/list", response_model=AlbumListResponse)
async def list_albums(
    project_id: Optional[str] = None,
    tag: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """
    List albums with filtering and pagination.
    
    Filters:
    - project_id: Filter by project
    - tag: Filter by tag
    """
    try:
        # Build query
        query = {}
        if project_id:
            query["project_id"] = project_id
        if tag:
            query["tags"] = tag
        
        # Count total
        total = await Album.find(query).count()
        
        # Get page
        skip = (page - 1) * page_size
        albums = await Album.find(query).skip(skip).limit(page_size).to_list()
        
        # Build responses with cover thumbnails
        album_responses = []
        for album in albums:
            cover_thumbnail = None
            if album.cover_video_id:
                cover_video = await GeneratedVideo.find_one(GeneratedVideo.video_id == album.cover_video_id)
                if cover_video:
                    cover_thumbnail = cover_video.thumbnail_url
            
            album_responses.append(AlbumResponse(
                album_id=album.album_id,
                project_id=album.project_id,
                name=album.name,
                description=album.description,
                cover_video_id=album.cover_video_id,
                cover_thumbnail=cover_thumbnail,
                video_count=len(album.video_ids),
                tags=album.tags,
                is_public=album.is_public,
                created_at=album.created_at,
                updated_at=album.updated_at
            ))
        
        return AlbumListResponse(
            albums=album_responses,
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list albums: {str(e)}"
        )


@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1, description="Search query"),
    search_type: str = Query("all", regex="^(all|albums|videos)$")
):
    """
    Search albums and videos.
    
    Searches in:
    - Album names and descriptions
    - Video tags and descriptions
    """
    try:
        albums = []
        videos = []
        
        # Search albums
        if search_type in ["all", "albums"]:
            # Simple text search (in production, use MongoDB text indexes)
            all_albums = await Album.find().to_list()
            albums = [
                AlbumResponse(
                    album_id=a.album_id,
                    project_id=a.project_id,
                    name=a.name,
                    description=a.description,
                    cover_video_id=a.cover_video_id,
                    video_count=len(a.video_ids),
                    tags=a.tags,
                    is_public=a.is_public,
                    created_at=a.created_at,
                    updated_at=a.updated_at
                )
                for a in all_albums
                if q.lower() in a.name.lower() 
                or (a.description and q.lower() in a.description.lower())
                or any(q.lower() in tag.lower() for tag in a.tags)
            ]
        
        # Search videos
        if search_type in ["all", "videos"]:
            all_videos = await GeneratedVideo.find().to_list()
            videos = [
                VideoResponse(
                    video_id=v.video_id,
                    job_id=v.job_id,
                    project_id=v.project_id,
                    shot_id=v.shot_id,
                    file_url=v.file_url,
                    thumbnail_url=v.thumbnail_url,
                    preview_url=v.preview_url,
                    format=v.format,
                    quality=v.quality,
                    metadata=v.metadata,
                    tags=v.tags,
                    description=v.description,
                    created_at=v.created_at,
                    views=v.views,
                    downloads=v.downloads
                )
                for v in all_videos
                if any(q.lower() in tag.lower() for tag in v.tags)
                or (v.description and q.lower() in v.description.lower())
            ]
        
        return SearchResponse(
            albums=albums,
            videos=videos,
            total_albums=len(albums),
            total_videos=len(videos)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/{album_id}", response_model=AlbumDetailResponse)
async def get_album(album_id: str):
    """Get album with videos"""
    try:
        album = await Album.find_one(Album.album_id == album_id)
        
        if not album:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Album {album_id} not found"
            )
        
        # Get videos
        videos = []
        for video_id in album.video_ids:
            video = await GeneratedVideo.find_one(GeneratedVideo.video_id == video_id)
            if video:
                videos.append(VideoResponse(
                    video_id=video.video_id,
                    job_id=video.job_id,
                    project_id=video.project_id,
                    shot_id=video.shot_id,
                    file_url=video.file_url,
                    thumbnail_url=video.thumbnail_url,
                    preview_url=video.preview_url,
                    format=video.format,
                    quality=video.quality,
                    metadata=video.metadata,
                    tags=video.tags,
                    description=video.description,
                    created_at=video.created_at,
                    views=video.views,
                    downloads=video.downloads
                ))
        
        return AlbumDetailResponse(
            album_id=album.album_id,
            project_id=album.project_id,
            name=album.name,
            description=album.description,
            cover_video_id=album.cover_video_id,
            videos=videos,
            tags=album.tags,
            is_public=album.is_public,
            created_at=album.created_at,
            updated_at=album.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get album: {str(e)}"
        )


@router.put("/{album_id}", response_model=AlbumResponse)
async def update_album(album_id: str, request: UpdateAlbumRequest):
    """Update album details"""
    try:
        album = await Album.find_one(Album.album_id == album_id)
        
        if not album:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Album {album_id} not found"
            )
        
        # Update fields
        if request.name is not None:
            album.name = request.name
        if request.description is not None:
            album.description = request.description
        if request.cover_video_id is not None:
            album.cover_video_id = request.cover_video_id
        if request.tags is not None:
            album.tags = request.tags
        if request.is_public is not None:
            album.is_public = request.is_public
        
        album.updated_at = datetime.utcnow()
        await album.save()
        
        # Get cover thumbnail
        cover_thumbnail = None
        if album.cover_video_id:
            cover_video = await GeneratedVideo.find_one(GeneratedVideo.video_id == album.cover_video_id)
            if cover_video:
                cover_thumbnail = cover_video.thumbnail_url
        
        return AlbumResponse(
            album_id=album.album_id,
            project_id=album.project_id,
            name=album.name,
            description=album.description,
            cover_video_id=album.cover_video_id,
            cover_thumbnail=cover_thumbnail,
            video_count=len(album.video_ids),
            tags=album.tags,
            is_public=album.is_public,
            created_at=album.created_at,
            updated_at=album.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update album: {str(e)}"
        )


@router.delete("/{album_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_album(album_id: str):
    """Delete album (videos are not deleted)"""
    try:
        album = await Album.find_one(Album.album_id == album_id)
        
        if not album:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Album {album_id} not found"
            )
        
        await album.delete()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete album: {str(e)}"
        )


@router.post("/{album_id}/add-video", response_model=AlbumResponse)
async def add_video_to_album(album_id: str, request: AddVideoRequest):
    """Add video to album"""
    try:
        # Check album exists
        album = await Album.find_one(Album.album_id == album_id)
        if not album:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Album {album_id} not found"
            )
        
        # Check video exists
        video = await GeneratedVideo.find_one(GeneratedVideo.video_id == request.video_id)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video {request.video_id} not found"
            )
        
        # Add to album if not already there
        if request.video_id not in album.video_ids:
            album.video_ids.append(request.video_id)
            album.updated_at = datetime.utcnow()
            await album.save()
        
        # Add album to video's album_ids
        if album_id not in video.album_ids:
            video.album_ids.append(album_id)
            await video.save()
        
        return AlbumResponse(
            album_id=album.album_id,
            project_id=album.project_id,
            name=album.name,
            description=album.description,
            cover_video_id=album.cover_video_id,
            video_count=len(album.video_ids),
            tags=album.tags,
            is_public=album.is_public,
            created_at=album.created_at,
            updated_at=album.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add video to album: {str(e)}"
        )


@router.delete("/{album_id}/remove-video/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_video_from_album(album_id: str, video_id: str):
    """Remove video from album"""
    try:
        # Get album
        album = await Album.find_one(Album.album_id == album_id)
        if not album:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Album {album_id} not found"
            )
        
        # Remove from album
        if video_id in album.video_ids:
            album.video_ids.remove(video_id)
            album.updated_at = datetime.utcnow()
            await album.save()
        
        # Remove album from video
        video = await GeneratedVideo.find_one(GeneratedVideo.video_id == video_id)
        if video and album_id in video.album_ids:
            video.album_ids.remove(album_id)
            await video.save()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove video from album: {str(e)}"
        )
