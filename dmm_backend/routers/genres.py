"""
Genre Management Router

This router provides endpoints for genre definitions, validation, and suggestions.
Implements the Genre System for Peace Script (STEP 1: Genre Selection).

Author: Peace Script Team
Date: 19 November 2568
Version: 1.0
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import json
from pathlib import Path

router = APIRouter(prefix="/api/genres", tags=["genres"])

# ============================================================================
# Load Genre Definitions
# ============================================================================

def load_genre_definitions() -> Dict[str, Any]:
    """Load genre definitions from JSON file"""
    try:
        # Try relative path from backend root
        definitions_path = Path(__file__).parent.parent / "definitions" / "genres.json"
        if not definitions_path.exists():
            # Try absolute path
            definitions_path = Path("/Users/surasak.peace/Desktop/peace script model v1.4/dmm_backend/definitions/genres.json")
        
        with open(definitions_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load genre definitions: {e}")

# Load genres on module import
GENRE_DATA = load_genre_definitions()


# ============================================================================
# Response Models
# ============================================================================

class GenreDetail(BaseModel):
    """Detailed genre information"""
    id: str
    name_en: str
    name_th: str
    description_en: str
    description_th: str
    keywords: List[str]
    dhamma_themes: List[str]
    typical_percentage_range: List[int]
    examples: List[str]
    production_notes: str
    pali_reference: str
    category: str  # "main" or "secondary"


class GenreSummary(BaseModel):
    """Summary genre information for lists"""
    id: str
    name_en: str
    name_th: str
    description_th: str
    category: str
    typical_percentage_range: List[int]


class GenreListResponse(BaseModel):
    """Response for genre list endpoint"""
    total: int
    main_genres: List[GenreSummary]
    secondary_genres: List[GenreSummary]
    metadata: Dict[str, Any]


class GenrePercentage(BaseModel):
    """Genre with percentage"""
    type: str
    percentage: int = Field(..., ge=0, le=100)


class GenreValidationRequest(BaseModel):
    """Request for genre validation"""
    genres: List[GenrePercentage]
    
    @validator('genres')
    def validate_genres(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one genre is required')
        if len(v) > 5:
            raise ValueError('Maximum 5 genres allowed')
        total = sum(g.percentage for g in v)
        if total != 100:
            raise ValueError(f'Genre percentages must sum to 100, got {total}')
        return v


class GenreValidationResponse(BaseModel):
    """Response for genre validation"""
    valid: bool
    total_percentage: int
    genre_count: int
    warnings: List[str] = []
    suggestions: List[str] = []


class GenreSuggestion(BaseModel):
    """Genre suggestion with confidence"""
    type: str
    name_th: str
    percentage: int
    confidence: float = Field(..., ge=0.0, le=1.0)
    reason: str


class GenreSuggestionResponse(BaseModel):
    """Response for genre suggestion"""
    suggestions: List[GenreSuggestion]
    total_confidence: float


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/health")
async def health_check():
    """Health check endpoint for genre service"""
    return {
        "status": "healthy",
        "service": "Genre Management System",
        "version": "1.0",
        "total_genres": GENRE_DATA["metadata"]["total_genres"],
        "main_genres": GENRE_DATA["metadata"]["total_main_genres"],
        "secondary_genres": GENRE_DATA["metadata"]["total_secondary_genres"]
    }


@router.get("/", response_model=GenreListResponse)
async def list_genres(
    category: Optional[str] = Query(None, description="Filter by category: main, secondary, or all"),
    language: str = Query("th", description="Language for names: en or th")
):
    """
    List all available genres with details
    
    **Returns:**
    - Main genres (11): Drama, Comedy, Action, etc.
    - Secondary genres (11): Social, Psychological, Crime, etc.
    - Metadata: Usage notes and validation rules
    
    **Example:**
    ```
    GET /api/genres
    GET /api/genres?category=main
    GET /api/genres?category=secondary&language=en
    ```
    """
    main_genres = GENRE_DATA.get("main_genres", [])
    secondary_genres = GENRE_DATA.get("secondary_genres", [])
    
    # Convert to summary format
    main_summaries = [
        GenreSummary(
            id=g["id"],
            name_en=g["name_en"],
            name_th=g["name_th"],
            description_th=g["description_th"],
            category="main",
            typical_percentage_range=g["typical_percentage_range"]
        )
        for g in main_genres
    ]
    
    secondary_summaries = [
        GenreSummary(
            id=g["id"],
            name_en=g["name_en"],
            name_th=g["name_th"],
            description_th=g["description_th"],
            category="secondary",
            typical_percentage_range=g["typical_percentage_range"]
        )
        for g in secondary_genres
    ]
    
    # Filter by category if specified
    if category == "main":
        secondary_summaries = []
    elif category == "secondary":
        main_summaries = []
    
    return GenreListResponse(
        total=len(main_summaries) + len(secondary_summaries),
        main_genres=main_summaries,
        secondary_genres=secondary_summaries,
        metadata=GENRE_DATA.get("metadata", {})
    )


@router.get("/{genre_id}", response_model=GenreDetail)
async def get_genre(genre_id: str):
    """
    Get detailed information about a specific genre
    
    **Args:**
    - genre_id: Genre ID (e.g., "DRAMA", "THRILLER", "SOCIAL")
    
    **Returns:**
    - Complete genre details including:
      - Names (Thai/English)
      - Descriptions
      - Keywords
      - Related Dhamma themes
      - Production notes
      - Examples
      - Pali references
    
    **Example:**
    ```
    GET /api/genres/DRAMA
    GET /api/genres/SOCIAL
    ```
    """
    genre_id_upper = genre_id.upper()
    
    # Search in main genres
    for genre in GENRE_DATA.get("main_genres", []):
        if genre["id"] == genre_id_upper:
            return GenreDetail(**genre, category="main")
    
    # Search in secondary genres
    for genre in GENRE_DATA.get("secondary_genres", []):
        if genre["id"] == genre_id_upper:
            return GenreDetail(**genre, category="secondary")
    
    raise HTTPException(
        status_code=404,
        detail=f"Genre '{genre_id}' not found. Use /api/genres to see available genres."
    )


@router.post("/validate", response_model=GenreValidationResponse)
async def validate_genres(request: GenreValidationRequest):
    """
    Validate genre combination and percentages
    
    **Args:**
    - genres: List of genres with percentages
    
    **Validation Rules:**
    1. Total percentage must equal 100
    2. Minimum 1 genre, maximum 5 genres
    3. Each percentage must be 0-100
    
    **Returns:**
    - Validation result with warnings and suggestions
    
    **Example:**
    ```json
    POST /api/genres/validate
    {
      "genres": [
        {"type": "drama", "percentage": 60},
        {"type": "thriller", "percentage": 40}
      ]
    }
    ```
    """
    warnings = []
    suggestions = []
    
    # Calculate total
    total = sum(g.percentage for g in request.genres)
    
    # Check genre count
    genre_count = len(request.genres)
    if genre_count > 3:
        warnings.append(f"You have {genre_count} genres. Consider using 2-3 genres for clarity.")
    
    # Check if genres exist
    all_genre_ids = [g["id"].lower() for g in GENRE_DATA.get("main_genres", [])] + \
                    [g["id"].lower() for g in GENRE_DATA.get("secondary_genres", [])]
    
    for genre in request.genres:
        genre_type_lower = genre.type.lower()
        if genre_type_lower not in all_genre_ids:
            warnings.append(f"Genre '{genre.type}' not found in definitions. Use standard genre IDs.")
    
    # Check percentage ranges
    for genre in request.genres:
        genre_type_lower = genre.type.lower()
        
        # Find genre definition
        genre_def = None
        for g in GENRE_DATA.get("main_genres", []) + GENRE_DATA.get("secondary_genres", []):
            if g["id"].lower() == genre_type_lower:
                genre_def = g
                break
        
        if genre_def:
            min_pct, max_pct = genre_def["typical_percentage_range"]
            if genre.percentage < min_pct or genre.percentage > max_pct:
                warnings.append(
                    f"{genre_def['name_th']} typically uses {min_pct}-{max_pct}%, "
                    f"but you have {genre.percentage}%"
                )
    
    # Suggestions
    if genre_count == 1:
        suggestions.append("Consider adding a secondary genre to add depth to your story")
    
    if total == 100 and len(warnings) == 0:
        suggestions.append("Great! Your genre combination looks balanced.")
    
    return GenreValidationResponse(
        valid=(total == 100),
        total_percentage=total,
        genre_count=genre_count,
        warnings=warnings,
        suggestions=suggestions
    )


@router.get("/suggest/auto", response_model=GenreSuggestionResponse)
async def suggest_genres(
    concept: str = Query(..., description="Story concept description"),
    target_count: int = Query(2, ge=1, le=5, description="Number of genres to suggest")
):
    """
    Suggest genres based on story concept (AI-powered)
    
    **Args:**
    - concept: Brief description of story concept
    - target_count: How many genres to suggest (1-5)
    
    **Returns:**
    - Genre suggestions with confidence scores
    - Suggested percentages
    - Reasoning for each suggestion
    
    **Example:**
    ```
    GET /api/genres/suggest/auto?concept=เรื่องราวของการแก้แค้น&target_count=2
    ```
    
    **Note:** This is a basic keyword-based implementation.
    Future versions will use Ollama LLM for smarter suggestions.
    """
    # Simple keyword-based matching (can be upgraded to use Ollama later)
    suggestions = []
    concept_lower = concept.lower()
    
    # Keyword mappings (simplified)
    keyword_map = {
        "แก้แค้น": [("THRILLER", 50, "เรื่องมีการแก้แค้น → ระทึกขวัญ"), 
                    ("DRAMA", 40, "มีความขัดแย้งทางอารมณ์")],
        "ตลก": [("COMEDY", 70, "เน้นความตลก"), 
                ("DRAMA", 30, "มีองค์ประกอบดราม่า")],
        "รัก": [("ROMANCE", 60, "เรื่องความรัก"), 
               ("DRAMA", 40, "มีความลึกซึ้งทางอารมณ์")],
        "ผี": [("HORROR", 70, "เรื่องสยองขวัญ"), 
               ("THRILLER", 30, "มีความระทึก")],
        "ต่อสู้": [("ACTION", 60, "มีฉากแอ็กชัน"), 
                  ("DRAMA", 40, "มีความขัดแย้ง")],
        "สังคม": [("SOCIAL", 40, "มีประเด็นสังคม"), 
                  ("DRAMA", 60, "ดราม่าสังคม")],
        "อาชญากรรม": [("CRIME", 50, "เกี่ยวกับอาชญากรรม"), 
                       ("THRILLER", 50, "มีความระทึก")],
    }
    
    # Match keywords
    matched_genres = {}
    for keyword, genre_list in keyword_map.items():
        if keyword in concept_lower:
            for genre_id, pct, reason in genre_list:
                if genre_id not in matched_genres:
                    matched_genres[genre_id] = {"percentage": pct, "confidence": 0.7, "reason": reason}
    
    # Default suggestion if no matches
    if not matched_genres:
        matched_genres = {
            "DRAMA": {"percentage": 60, "confidence": 0.5, "reason": "แนวดราม่าเป็นแนวพื้นฐานที่ครอบคลุมเรื่องราวหลากหลาย"},
            "THRILLER": {"percentage": 40, "confidence": 0.4, "reason": "เพิ่มความน่าสนใจด้วยแนวระทึกขวัญ"}
        }
    
    # Normalize to target_count
    genre_items = list(matched_genres.items())[:target_count]
    total_pct = sum(item[1]["percentage"] for item in genre_items)
    
    # Adjust percentages to sum to 100
    for genre_id, data in genre_items:
        # Find genre name
        genre_name = genre_id
        for g in GENRE_DATA.get("main_genres", []) + GENRE_DATA.get("secondary_genres", []):
            if g["id"] == genre_id:
                genre_name = g["name_th"]
                break
        
        adjusted_pct = int((data["percentage"] / total_pct) * 100)
        suggestions.append(
            GenreSuggestion(
                type=genre_id.lower(),
                name_th=genre_name,
                percentage=adjusted_pct,
                confidence=data["confidence"],
                reason=data["reason"]
            )
        )
    
    # Ensure percentages sum to 100
    if suggestions:
        total_suggested = sum(s.percentage for s in suggestions)
        if total_suggested != 100:
            suggestions[0].percentage += (100 - total_suggested)
    
    avg_confidence = sum(s.confidence for s in suggestions) / len(suggestions) if suggestions else 0.0
    
    return GenreSuggestionResponse(
        suggestions=suggestions,
        total_confidence=avg_confidence
    )


@router.get("/templates/presets")
async def get_genre_templates():
    """
    Get pre-defined genre combination templates
    
    **Returns:**
    - Common genre templates for quick selection
    
    **Example:**
    ```
    GET /api/genres/templates/presets
    ```
    """
    templates = [
        {
            "id": "pure_drama",
            "name_th": "ดราม่าล้วน",
            "name_en": "Pure Drama",
            "genres": [{"type": "drama", "percentage": 100}],
            "description": "เรื่องราวที่เน้นความลึกซึ้งทางอารมณ์และตัวละคร"
        },
        {
            "id": "action_drama",
            "name_th": "แอ็กชันดราม่า",
            "name_en": "Action Drama",
            "genres": [
                {"type": "action", "percentage": 60},
                {"type": "drama", "percentage": 40}
            ],
            "description": "แอ็กชันเข้มข้นผสมกับความลึกซึ้งทางอารมณ์"
        },
        {
            "id": "thriller_mystery",
            "name_th": "ระทึกขวัญปริศนา",
            "name_en": "Thriller Mystery",
            "genres": [
                {"type": "thriller", "percentage": 50},
                {"type": "mystery", "percentage": 50}
            ],
            "description": "ความระทึกผสมกับการไขปริศนา"
        },
        {
            "id": "romantic_comedy",
            "name_th": "รอมคอม",
            "name_en": "Romantic Comedy",
            "genres": [
                {"type": "romance", "percentage": 50},
                {"type": "comedy", "percentage": 50}
            ],
            "description": "ความรักผสมกับความตลกขบขัน"
        },
        {
            "id": "horror_thriller",
            "name_th": "สยองขวัญระทึกขวัญ",
            "name_en": "Horror Thriller",
            "genres": [
                {"type": "horror", "percentage": 60},
                {"type": "thriller", "percentage": 40}
            ],
            "description": "ความน่ากลัวผสมกับความระทึก"
        },
        {
            "id": "social_drama",
            "name_th": "ดราม่าสังคม",
            "name_en": "Social Drama",
            "genres": [
                {"type": "drama", "percentage": 60},
                {"type": "social", "percentage": 40}
            ],
            "description": "ดราม่าที่มีประเด็นสังคม"
        },
        {
            "id": "crime_thriller",
            "name_th": "อาชญากรรมระทึกขวัญ",
            "name_en": "Crime Thriller",
            "genres": [
                {"type": "crime", "percentage": 50},
                {"type": "thriller", "percentage": 50}
            ],
            "description": "เรื่องอาชญากรรมที่ระทึกขวัญ"
        },
        {
            "id": "action_adventure",
            "name_th": "แอ็กชันผจญภัย",
            "name_en": "Action Adventure",
            "genres": [
                {"type": "action", "percentage": 50},
                {"type": "adventure", "percentage": 50}
            ],
            "description": "แอ็กชันผสมกับการผจญภัย"
        },
        {
            "id": "psychological_thriller",
            "name_th": "จิตวิทยาระทึกขวัญ",
            "name_en": "Psychological Thriller",
            "genres": [
                {"type": "thriller", "percentage": 50},
                {"type": "psychological", "percentage": 30},
                {"type": "drama", "percentage": 20}
            ],
            "description": "ความระทึกที่เล่นกับจิตใจ"
        },
        {
            "id": "scifi_action",
            "name_th": "ไซไฟแอ็กชัน",
            "name_en": "Sci-Fi Action",
            "genres": [
                {"type": "scifi", "percentage": 60},
                {"type": "action", "percentage": 40}
            ],
            "description": "วิทยาศาสตร์ผสมกับแอ็กชัน"
        }
    ]
    
    return {
        "total": len(templates),
        "templates": templates
    }
