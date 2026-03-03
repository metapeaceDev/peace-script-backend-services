"""
Extension Router - Plugin Marketplace & Extension Management
Priority #7.4 - Plugin registry, Install/Uninstall, Marketplace

Features:
- Extension marketplace browsing
- Search and category filtering
- Install/Uninstall extensions
- Enable/Disable extensions
- Extension settings management
- Dependency checking

Endpoints:
- GET /api/v1/extensions/marketplace - Browse marketplace
- GET /api/v1/extensions/installed - List installed extensions
- POST /api/v1/extensions/{id}/install - Install extension
- DELETE /api/v1/extensions/{id}/uninstall - Uninstall extension
- PATCH /api/v1/extensions/{id}/toggle - Enable/Disable extension
- PATCH /api/v1/extensions/{id}/settings - Update settings
- GET /api/v1/extensions/categories - List categories
- GET /api/v1/extensions/search - Search extensions
"""

from typing import List, Dict, Optional, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field, HttpUrl

from core.security import get_api_key
from core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/api/v1/extensions",
    tags=["Extensions"],
    dependencies=[Depends(get_api_key)],
)


# ===== Pydantic Models =====

class ExtensionBase(BaseModel):
    """Base extension model"""
    id: str = Field(..., description="Unique extension ID")
    name: str = Field(..., description="Extension name")
    description: str = Field(..., description="Extension description")
    version: str = Field(..., description="Extension version (semver)")
    author: str = Field(..., description="Extension author")
    category: str = Field(..., description="Extension category")
    icon_url: Optional[str] = Field(None, description="Icon URL")
    tags: List[str] = Field(default_factory=list, description="Search tags")


class MarketplaceExtension(ExtensionBase):
    """Extension in marketplace"""
    downloads: int = Field(0, description="Download count")
    rating: float = Field(0.0, ge=0.0, le=5.0, description="Average rating (0-5)")
    price: float = Field(0.0, ge=0.0, description="Price (0 = free)")
    size_mb: float = Field(0.0, description="Extension size in MB")
    homepage_url: Optional[str] = Field(None, description="Homepage URL")
    repository_url: Optional[str] = Field(None, description="Repository URL")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class InstalledExtension(ExtensionBase):
    """Installed extension"""
    enabled: bool = Field(True, description="Extension enabled status")
    installed_at: datetime = Field(default_factory=datetime.utcnow)
    settings: Dict[str, Any] = Field(default_factory=dict, description="Extension settings")
    dependencies: List[str] = Field(default_factory=list, description="Required dependencies")


class InstallRequest(BaseModel):
    """Request to install extension"""
    extension_id: str = Field(..., description="Extension ID to install")
    enable_immediately: bool = Field(True, description="Enable after install")


class SettingsUpdateRequest(BaseModel):
    """Request to update extension settings"""
    settings: Dict[str, Any] = Field(..., description="New settings")


# ===== Mock Data (Replace with database in production) =====

# Marketplace extensions
marketplace_extensions: List[MarketplaceExtension] = [
    MarketplaceExtension(
        id="ext-visual-debugger",
        name="Visual Debugger",
        description="Real-time kamma chain visualization with interactive graph explorer",
        version="1.2.0",
        author="Peace Script Team",
        category="Visualization",
        icon_url="https://example.com/icons/debugger.png",
        tags=["kamma", "debug", "visualization", "graph"],
        downloads=1250,
        rating=4.8,
        price=0.0,
        size_mb=2.5,
        homepage_url="https://peacescript.dev/extensions/visual-debugger",
        repository_url="https://github.com/peacescript/visual-debugger",
    ),
    MarketplaceExtension(
        id="ext-ai-narrator",
        name="AI Narrator",
        description="Automatic story narration using local LLM integration",
        version="2.0.1",
        author="Narrative Systems",
        category="AI",
        icon_url="https://example.com/icons/narrator.png",
        tags=["ai", "narration", "story", "llm"],
        downloads=890,
        rating=4.5,
        price=9.99,
        size_mb=15.3,
    ),
    MarketplaceExtension(
        id="ext-blender-export",
        name="Blender Export Pro",
        description="Export characters and animations directly to Blender with rigging",
        version="3.1.0",
        author="3D Tools Inc",
        category="Export",
        icon_url="https://example.com/icons/blender.png",
        tags=["blender", "export", "3d", "animation"],
        downloads=2100,
        rating=4.9,
        price=14.99,
        size_mb=8.7,
    ),
    MarketplaceExtension(
        id="ext-unity-bridge",
        name="Unity Bridge",
        description="Real-time Unity integration for game development workflows",
        version="1.5.2",
        author="Game Dev Tools",
        category="Export",
        icon_url="https://example.com/icons/unity.png",
        tags=["unity", "game", "export", "real-time"],
        downloads=1560,
        rating=4.6,
        price=19.99,
        size_mb=12.4,
    ),
    MarketplaceExtension(
        id="ext-csv-analytics",
        name="CSV Analytics Exporter",
        description="Export detailed analytics and kamma data to CSV/Excel formats",
        version="1.0.5",
        author="Data Tools",
        category="Export",
        icon_url="https://example.com/icons/csv.png",
        tags=["csv", "excel", "analytics", "export"],
        downloads=780,
        rating=4.2,
        price=0.0,
        size_mb=1.2,
    ),
    MarketplaceExtension(
        id="ext-character-importer",
        name="Character Importer",
        description="Import characters from VRoid, DAZ3D, and other 3D platforms",
        version="2.3.0",
        author="Import Wizard",
        category="Import",
        icon_url="https://example.com/icons/import.png",
        tags=["import", "vroid", "daz3d", "character"],
        downloads=1420,
        rating=4.7,
        price=12.99,
        size_mb=6.8,
    ),
    MarketplaceExtension(
        id="ext-motion-capture",
        name="Motion Capture Sync",
        description="Sync with motion capture systems for realistic character animation",
        version="1.8.0",
        author="Animation Pro",
        category="Import",
        icon_url="https://example.com/icons/mocap.png",
        tags=["mocap", "animation", "import", "real-time"],
        downloads=650,
        rating=4.4,
        price=29.99,
        size_mb=18.5,
    ),
    MarketplaceExtension(
        id="ext-theme-pack-neon",
        name="Neon Theme Pack",
        description="Cyberpunk-inspired neon UI theme with custom visualizations",
        version="1.1.0",
        author="UI Themes",
        category="Themes",
        icon_url="https://example.com/icons/neon.png",
        tags=["theme", "ui", "neon", "cyberpunk"],
        downloads=3200,
        rating=4.9,
        price=4.99,
        size_mb=3.5,
    ),
]

# Installed extensions storage
installed_extensions: Dict[str, InstalledExtension] = {}


# ===== Endpoints =====

@router.get("/marketplace", response_model=List[MarketplaceExtension])
async def get_marketplace(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search query"),
    sort: str = Query("downloads", description="Sort by: downloads, rating, name, updated_at"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """
    Browse extension marketplace
    
    Returns list of available extensions with filtering and sorting
    """
    try:
        # Filter by category
        extensions = marketplace_extensions
        if category:
            extensions = [e for e in extensions if e.category.lower() == category.lower()]
        
        # Search by name, description, tags
        if search:
            search_lower = search.lower()
            extensions = [
                e for e in extensions
                if (search_lower in e.name.lower() or
                    search_lower in e.description.lower() or
                    any(search_lower in tag.lower() for tag in e.tags))
            ]
        
        # Sort
        if sort == "downloads":
            extensions.sort(key=lambda e: e.downloads, reverse=True)
        elif sort == "rating":
            extensions.sort(key=lambda e: e.rating, reverse=True)
        elif sort == "name":
            extensions.sort(key=lambda e: e.name.lower())
        elif sort == "updated_at":
            extensions.sort(key=lambda e: e.updated_at, reverse=True)
        
        # Pagination
        return extensions[skip:skip + limit]
        
    except Exception as e:
        logger.error(f"Error getting marketplace: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/installed", response_model=List[InstalledExtension])
async def get_installed():
    """
    List all installed extensions
    
    Returns list of installed extensions with settings and status
    """
    try:
        return list(installed_extensions.values())
    except Exception as e:
        logger.error(f"Error getting installed extensions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/install", response_model=InstalledExtension)
async def install_extension(request: InstallRequest):
    """
    Install extension from marketplace
    
    Downloads and installs the extension
    """
    try:
        # Find extension in marketplace
        marketplace_ext = next(
            (e for e in marketplace_extensions if e.id == request.extension_id),
            None
        )
        
        if not marketplace_ext:
            raise HTTPException(status_code=404, detail=f"Extension not found: {request.extension_id}")
        
        # Check if already installed
        if request.extension_id in installed_extensions:
            raise HTTPException(status_code=400, detail="Extension already installed")
        
        # Create installed extension
        installed_ext = InstalledExtension(
            id=marketplace_ext.id,
            name=marketplace_ext.name,
            description=marketplace_ext.description,
            version=marketplace_ext.version,
            author=marketplace_ext.author,
            category=marketplace_ext.category,
            icon_url=marketplace_ext.icon_url,
            tags=marketplace_ext.tags,
            enabled=request.enable_immediately,
            installed_at=datetime.utcnow(),
            settings={},
            dependencies=[],
        )
        
        installed_extensions[request.extension_id] = installed_ext
        logger.info(f"Installed extension: {request.extension_id}")
        
        return installed_ext
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error installing extension: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{extension_id}/uninstall")
async def uninstall_extension(extension_id: str):
    """
    Uninstall extension
    
    Removes extension and its settings
    """
    if extension_id not in installed_extensions:
        raise HTTPException(status_code=404, detail=f"Extension not installed: {extension_id}")
    
    try:
        del installed_extensions[extension_id]
        logger.info(f"Uninstalled extension: {extension_id}")
        
        return {"success": True, "message": f"Extension {extension_id} uninstalled"}
        
    except Exception as e:
        logger.error(f"Error uninstalling extension: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{extension_id}/toggle", response_model=InstalledExtension)
async def toggle_extension(extension_id: str):
    """
    Enable or disable extension
    
    Toggles the enabled status
    """
    if extension_id not in installed_extensions:
        raise HTTPException(status_code=404, detail=f"Extension not installed: {extension_id}")
    
    try:
        extension = installed_extensions[extension_id]
        extension.enabled = not extension.enabled
        
        logger.info(f"Toggled extension {extension_id}: enabled={extension.enabled}")
        
        return extension
        
    except Exception as e:
        logger.error(f"Error toggling extension: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{extension_id}/settings", response_model=InstalledExtension)
async def update_settings(extension_id: str, request: SettingsUpdateRequest):
    """
    Update extension settings
    
    Updates configuration for installed extension
    """
    if extension_id not in installed_extensions:
        raise HTTPException(status_code=404, detail=f"Extension not installed: {extension_id}")
    
    try:
        extension = installed_extensions[extension_id]
        extension.settings.update(request.settings)
        
        logger.info(f"Updated settings for extension: {extension_id}")
        
        return extension
        
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def get_categories():
    """
    List all extension categories
    
    Returns unique categories with counts
    """
    try:
        categories: Dict[str, int] = {}
        for ext in marketplace_extensions:
            categories[ext.category] = categories.get(ext.category, 0) + 1
        
        return {
            "categories": [
                {"name": cat, "count": count}
                for cat, count in sorted(categories.items())
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_extensions(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50),
):
    """
    Search extensions by query
    
    Searches name, description, tags, and author
    """
    try:
        query_lower = q.lower()
        
        results = [
            e for e in marketplace_extensions
            if (query_lower in e.name.lower() or
                query_lower in e.description.lower() or
                query_lower in e.author.lower() or
                any(query_lower in tag.lower() for tag in e.tags))
        ]
        
        # Sort by relevance (name match first, then description, then tags)
        def relevance_score(ext: MarketplaceExtension) -> int:
            score = 0
            if query_lower in ext.name.lower():
                score += 100
            if query_lower in ext.description.lower():
                score += 50
            if any(query_lower in tag.lower() for tag in ext.tags):
                score += 25
            score += ext.downloads // 100  # Popularity boost
            return score
        
        results.sort(key=relevance_score, reverse=True)
        
        return {
            "query": q,
            "total": len(results),
            "results": results[:limit]
        }
        
    except Exception as e:
        logger.error(f"Error searching extensions: {e}")
        raise HTTPException(status_code=500, detail=str(e))
