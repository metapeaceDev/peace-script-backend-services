"""
Image Gallery & Album Models

Separates "Character Profile Albums" (Images) from "Shot Albums" (Videos).
This allows for a clean separation of concerns as requested.

Models:
- ImageAlbum: Collection of GeneratedImageDocument
"""

from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional, List

class ImageAlbum(Document):
    """
    Image Album / Character Gallery
    
    Stores collections of images (GeneratedImageDocument).
    Distinct from 'Album' in documents_video.py which stores videos.
    
    Attributes:
        album_id: Unique album identifier
        name: Album name (e.g., "Concept Art", "Portraits")
        description: Optional description
        actor_id: Linked Actor ID (if this is a specific character's gallery)
        project_id: Linked Project ID (optional)
        image_ids: List of GeneratedImageDocument IDs
        cover_image_id: ID of the image to use as cover
        tags: Searchable tags
        is_system: If True, this is a system-generated album (e.g., "All Photos")
    """
    
    album_id: str = Field(unique=True, index=True)
    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    
    # Associations
    actor_id: Optional[str] = Field(default=None, description="Owner Actor ID (for Character Albums)")
    project_id: Optional[str] = Field(default=None, description="Associated Project ID")
    
    # Narrative Associations (for Shot/Production Albums)
    scene_id: Optional[str] = Field(default=None, description="Associated Scene ID")
    shot_id: Optional[str] = Field(default=None, description="Associated Shot ID")
    storyboard_id: Optional[str] = Field(default=None, description="Associated Storyboard ID")
    
    # Content
    image_ids: List[str] = Field(default_factory=list, description="List of GeneratedImageDocument IDs")
    cover_image_id: Optional[str] = None
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    is_system: bool = Field(default=False, description="System album flag")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "image_albums"
        indexes = [
            "album_id",
            "actor_id",
            "project_id",
            "scene_id",
            "shot_id",
            "storyboard_id",
            "created_at",
            "tags"
        ]
