"""
Dhamma Themes API Router
========================
API endpoints for managing Dhamma-based themes in Peace Script.

Endpoints:
- GET    /api/dhamma/themes              - List all themes with optional filters
- GET    /api/dhamma/themes/{theme_id}   - Get specific theme details
- POST   /api/dhamma/themes/validate     - Validate text against theme
- POST   /api/dhamma/themes/suggest      - Get theme suggestions based on context
- POST   /api/dhamma/themes/validate-structure - Validate 15-beat structure

Author: Peace Script Team
Date: 18 November 2025 (2568 BE)
Version: 1.0
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

from services.dhamma_theme_service import get_dhamma_theme_service


router = APIRouter(
    prefix="/api/dhamma/themes",
    tags=["Dhamma Themes"]
)


# ============================================================
# Request/Response Models
# ============================================================

class ThemeSearchRequest(BaseModel):
    """Request model for theme search"""
    category: Optional[str] = None
    subcategory: Optional[str] = None
    conflict_keyword: Optional[str] = None
    search_text: Optional[str] = None


class ThemeSuggestionRequest(BaseModel):
    """Request model for theme suggestion"""
    big_idea: Optional[str] = None
    premise: Optional[str] = None
    tags: Optional[List[str]] = None
    conflict_type: Optional[str] = None


class ValidateTextRequest(BaseModel):
    """Request model for text validation"""
    theme_id: str = Field(..., description="ID of theme to validate against")
    text: str = Field(..., description="Text content to validate")
    section: str = Field(default="general", description="Section identifier (e.g., 'beat_2')")


class BeatContent(BaseModel):
    """Model for beat content in structure validation"""
    id: int = Field(..., description="Beat number (1-15)")
    name: str = Field(..., description="Beat name (e.g., 'Opening Image')")
    content: str = Field(..., description="Beat content text")


class ValidateStructureRequest(BaseModel):
    """Request model for structure validation"""
    theme_id: str = Field(..., description="ID of theme to validate against")
    structure: List[BeatContent] = Field(..., description="List of 15 beats")


class ValidationResult(BaseModel):
    """Response model for validation results"""
    valid: bool
    theme_id: str
    theme_name: str
    section: str
    found_keywords: List[str] = []
    found_forbidden: List[str] = []
    feedback: List[str] = []
    suggestion: str = ""


class BeatValidationResult(BaseModel):
    """Response model for beat validation"""
    valid: bool
    beat_id: int
    beat_name: str
    is_critical: bool
    theme_id: str
    theme_name: str
    section: str
    found_keywords: List[str] = []
    found_forbidden: List[str] = []
    feedback: List[str] = []
    suggestion: str = ""


class StructureValidationResult(BaseModel):
    """Response model for structure validation"""
    valid: bool
    theme_id: str
    theme_name: str
    critical_beats_passed: int
    critical_beats_total: int
    beat_results: List[Dict[str, Any]]
    summary: str


# ============================================================
# Endpoints
# ============================================================

@router.get("/", response_model=List[Dict[str, Any]])
async def list_themes(
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    conflict_keyword: Optional[str] = None,
    search_text: Optional[str] = None
):
    """
    Get list of all Dhamma themes with optional filtering
    
    Query Parameters:
    - category: Filter by category (e.g., "ปัญญา/สัมมาทิฏฐิ")
    - subcategory: Filter by subcategory
    - conflict_keyword: Match against applicable_conflicts
    - search_text: General text search
    
    Returns:
        List of theme objects matching filters
    """
    try:
        service = get_dhamma_theme_service()
        
        if any([category, subcategory, conflict_keyword, search_text]):
            themes = service.search_themes(
                category=category,
                subcategory=subcategory,
                conflict_keyword=conflict_keyword,
                search_text=search_text
            )
        else:
            themes = service.get_all_themes()
        
        return themes
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading themes: {str(e)}"
        )


@router.get("/{theme_id}", response_model=Dict[str, Any])
async def get_theme(theme_id: str):
    """
    Get detailed information about a specific theme
    
    Path Parameters:
    - theme_id: Unique theme identifier (e.g., "THEME_SACCA_TRUTH")
    
    Returns:
        Complete theme object with all metadata including:
        - categories: List of all categories this theme belongs to
        - is_multi_category: Boolean indicating if theme is used in multiple contexts
    """
    try:
        service = get_dhamma_theme_service()
        theme = service.get_theme(theme_id)
        
        if not theme:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Theme '{theme_id}' not found"
            )
        
        # Add multi-category metadata
        categories = service.get_theme_categories(theme_id)
        theme['is_multi_category'] = len(categories) > 1
        theme['category_count'] = len(categories)
        
        # Add explanation if multi-category
        if theme['is_multi_category']:
            theme['multi_category_note'] = (
                f"ธรรมนี้ใช้ได้ใน {len(categories)} หมวด: {', '.join(categories)} "
                "(ตามหลักพุทธศาสนา ธรรมหนึ่งสามารถเป็นได้หลายหมวดหมู่)"
            )
        
        return theme
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving theme: {str(e)}"
        )


@router.post("/search", response_model=List[Dict[str, Any]])
async def search_themes(request: ThemeSearchRequest):
    """
    Search themes by multiple criteria (POST version for complex queries)
    
    Request Body:
        ThemeSearchRequest with filter criteria
    
    Returns:
        List of matching themes
    """
    try:
        service = get_dhamma_theme_service()
        themes = service.search_themes(
            category=request.category,
            subcategory=request.subcategory,
            conflict_keyword=request.conflict_keyword,
            search_text=request.search_text
        )
        return themes
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching themes: {str(e)}"
        )


@router.post("/suggest", response_model=List[Dict[str, Any]])
async def suggest_themes(request: ThemeSuggestionRequest):
    """
    Get AI-powered theme suggestions based on story context
    
    Request Body:
        ThemeSuggestionRequest with story context
    
    Returns:
        List of 1-3 recommended themes, ranked by relevance
    """
    try:
        service = get_dhamma_theme_service()
        suggestions = service.suggest_themes(
            big_idea=request.big_idea,
            premise=request.premise,
            tags=request.tags,
            conflict_type=request.conflict_type
        )
        return suggestions
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error suggesting themes: {str(e)}"
        )


@router.post("/validate", response_model=ValidationResult)
async def validate_text(request: ValidateTextRequest):
    """
    Validate if text content adheres to theme's Dhamma principles
    
    Request Body:
        ValidateTextRequest with theme_id, text, and section
    
    Returns:
        ValidationResult with pass/fail status and detailed feedback
    """
    try:
        service = get_dhamma_theme_service()
        result = service.validate_theme_text(
            theme_id=request.theme_id,
            text=request.text,
            section=request.section
        )
        
        # Handle error case
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )
        
        return ValidationResult(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating text: {str(e)}"
        )


@router.post("/validate-structure", response_model=StructureValidationResult)
async def validate_structure(request: ValidateStructureRequest):
    """
    Validate entire 15-beat structure against theme
    
    Request Body:
        ValidateStructureRequest with theme_id and list of 15 beats
    
    Returns:
        StructureValidationResult with overall validation + beat-by-beat feedback
    """
    try:
        service = get_dhamma_theme_service()
        
        # Convert Pydantic models to dicts
        structure_dicts = [beat.dict() for beat in request.structure]
        
        result = service.validate_structure(
            theme_id=request.theme_id,
            structure=structure_dicts
        )
        
        # Handle error case
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )
        
        return StructureValidationResult(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating structure: {str(e)}"
        )


# ============================================================
# Health Check
# ============================================================

@router.get("/health/check")
async def health_check():
    """
    Health check endpoint to verify themes are loaded
    
    Returns:
        Status information about theme service including multi-category stats
    """
    try:
        service = get_dhamma_theme_service()
        themes = service.get_all_themes()
        
        # Count multi-category themes
        multi_category_count = sum(
            1 for theme_id in service._themes.keys() 
            if service.is_multi_category_theme(theme_id)
        )
        
        return {
            "status": "healthy",
            "themes_loaded": len(themes),
            "multi_category_themes": multi_category_count,
            "service_ready": True,
            "note": f"{multi_category_count} themes are used in multiple categories (normal in Buddhism)"
        }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "themes_loaded": 0,
            "service_ready": False,
            "error": str(e)
        }


@router.get("/categories/multi")
async def get_multi_category_themes():
    """
    Get list of themes that belong to multiple categories
    
    Returns:
        List of themes with their category memberships explained
    """
    try:
        service = get_dhamma_theme_service()
        
        multi_themes = []
        for theme_id in service._themes.keys():
            categories = service.get_theme_categories(theme_id)
            if len(categories) > 1:
                theme = service.get_theme(theme_id)
                if theme:  # Add null check
                    multi_themes.append({
                        "theme_id": theme_id,
                        "thai_name": theme.get('thai_name', ''),
                        "categories": categories,
                        "category_count": len(categories),
                        "explanation": f"ใช้ได้ทั้งใน {' และ '.join(categories)}"
                    })
        
        return {
            "total": len(multi_themes),
            "themes": sorted(multi_themes, key=lambda x: x['category_count'], reverse=True)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving multi-category themes: {str(e)}"
        )
