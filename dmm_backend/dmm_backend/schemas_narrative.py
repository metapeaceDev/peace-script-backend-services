"""
Pydantic Schemas for NarrativeStructure API Endpoints

This module contains request/response schemas for Peace Script narrative endpoints.
All schemas follow REST API best practices with proper validation.

Author: Peace Script Team
Date: 25 October 2025
Version: 1.0
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from beanie import PydanticObjectId

from documents_narrative import GenreEnum, CharacterRole, ProjectStatus, VisualStatus


# =============================================================================
# PROJECT SCHEMAS
# =============================================================================

class GenrePercentage(BaseModel):
    """Genre with percentage allocation"""
    type: str = Field(..., description="Genre type")
    percentage: int = Field(..., ge=0, le=100, description="Percentage allocation (0-100)")


class ProjectCreate(BaseModel):
    """Schema for creating a new project (Step 1: Project Details)"""
    project_id: str = Field(..., min_length=1, max_length=50, description="Unique project identifier")
    
    # Basic Info
    script_name: str = Field(..., min_length=1, max_length=200, description="Script name (ชื่อเรื่อง)")
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Display title (auto-generated if not provided)")
    description: Optional[str] = Field(None, max_length=2000, description="Project description")
    
    # Multi-Genre with Percentages (NEW)
    genres: List[GenrePercentage] = Field(..., description="Genres with percentage allocations (must sum to 100)")
    
    # Script Type (NEW)
    script_type: str = Field(..., description="Script type: movie/series/short_film/ad/moral_drama")
    
    # Concept & Audience (NEW)
    concept_description: Optional[str] = Field(None, max_length=2000, description="Concept description")
    target_audience: Optional[str] = Field(None, max_length=500, description="Target audience")
    
    # Tags (NEW)
    tags: List[str] = Field(default_factory=list, description="Tags (max 10)")
    
    # Structure (Step 4)
    structure: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Chapter structure (15 beats)")
    
    # Legacy Fields (for backward compatibility)
    genre: Optional[GenreEnum] = Field(None, description="Legacy single genre (deprecated, use genres instead)")
    genre_display: Optional[str] = Field(None, max_length=100, description="Legacy genre display")
    
    # Existing Fields
    studio: Optional[str] = Field(None, max_length=200, description="Production studio")
    writer: Optional[str] = Field(None, max_length=200, description="Screenwriter name")
    language: str = Field("th", min_length=2, max_length=5, description="Language code (default: th)")
    status: ProjectStatus = Field(ProjectStatus.DRAFT, description="Project status")
    
    @validator('genres')
    def validate_genres_sum(cls, v):
        """Validate that genre percentages sum to 100"""
        if not v or len(v) == 0:
            raise ValueError('At least one genre is required')
        total = sum(g.percentage for g in v)
        if total != 100:
            raise ValueError(f'Genre percentages must sum to 100, got {total}')
        return v
    
    @validator('tags')
    def validate_tags_length(cls, v):
        """Validate tags max 10"""
        if v and len(v) > 10:
            raise ValueError('Maximum 10 tags allowed')
        return v
    
    @validator('script_type')
    def validate_script_type(cls, v):
        """Validate script type"""
        valid_types = ['movie', 'series', 'short_film', 'ad', 'moral_drama']
        if v not in valid_types:
            raise ValueError(f'script_type must be one of {valid_types}')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "project_id": "proj_001",
                "script_name": "เงาแค้น",
                "genres": [
                    {"type": "drama", "percentage": 60},
                    {"type": "thriller", "percentage": 40}
                ],
                "script_type": "movie",
                "concept_description": "เรื่องราวของการแก้แค้นที่กลายเป็นการค้นหาตัวเอง",
                "target_audience": "ผู้ชมวัยทำงาน 25-40 ปี",
                "tags": ["revenge", "redemption", "family"],
                "studio": "Peace Studio",
                "writer": "สมชาย ใจดี",
                "language": "th",
                "status": "draft"
            }
        }


class ProjectUpdate(BaseModel):
    """Schema for updating a project (all fields optional)"""
    script_name: Optional[str] = Field(None, min_length=1, max_length=200)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    
    # Updated genre structure
    genres: Optional[List[GenrePercentage]] = Field(None, description="Genres with percentages")
    script_type: Optional[str] = Field(None, description="Script type")
    concept_description: Optional[str] = Field(None, max_length=2000)
    target_audience: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = Field(None, description="Tags")
    structure: Optional[List[Dict[str, Any]]] = Field(None, description="Chapter structure")
    
    # Legacy fields
    genre: Optional[GenreEnum] = Field(None, description="Legacy single genre (deprecated)")
    genre_display: Optional[str] = Field(None, max_length=100)
    
    # Other fields
    progress: Optional[float] = Field(None, ge=0.0, le=100.0)
    scenes_count: Optional[int] = Field(None, ge=0)
    characters_count: Optional[int] = Field(None, ge=0)
    studio: Optional[str] = Field(None, max_length=200)
    writer: Optional[str] = Field(None, max_length=200)
    language: Optional[str] = Field(None, min_length=2, max_length=5)
    status: Optional[ProjectStatus] = None
    imported_from: Optional[str] = None
    
    @validator('genres')
    def validate_genres_sum(cls, v):
        """Validate that genre percentages sum to 100 if provided"""
        if v:
            total = sum(g.percentage for g in v)
            if total != 100:
                raise ValueError(f'Genre percentages must sum to 100, got {total}')
        return v


class ProjectResponse(BaseModel):
    """Schema for project response"""
    id: str
    project_id: str
    script_name: str
    title: Optional[str]
    description: Optional[str]
    
    # Support both old and new genre structures
    genre: Optional[GenreEnum] = None
    genre_display: Optional[str] = None
    genres: Optional[List[GenrePercentage]] = None
    
    # New fields
    script_type: Optional[str] = None
    concept_description: Optional[str] = None
    target_audience: Optional[str] = None
    tags: Optional[List[str]] = None
    structure: Optional[List[Dict[str, Any]]] = None
    
    # Other fields
    progress: Optional[float]
    scenes_count: Optional[int]
    characters_count: Optional[int]
    studio: Optional[str]
    writer: Optional[str]
    language: str
    status: ProjectStatus
    imported_from: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# =============================================================================
# SCOPE OF STORY SCHEMAS (Step 2)
# =============================================================================

class BigIdeaSchema(BaseModel):
    """Big Idea structure"""
    prefix: str = Field(..., description="what_will_happen_if or is_the_story_of")
    content: str = Field(..., min_length=20, max_length=500, description="Big idea content")


class PremiseSchema(BaseModel):
    """Premise with Question & Answer"""
    question: str = Field(..., min_length=50, max_length=1000, description="What is this movie going to tell?")  # Increased from 10 to 50
    answer: str = Field(..., min_length=100, max_length=1000, description="Answer/Main message")  # Increased from 10 to 100


class ThemeSchema(BaseModel):
    """Theme structure"""
    teaching: str = Field(default="This tale teaches that", description="Teaching prefix")
    lesson: str = Field(..., min_length=50, max_length=300, description="The lesson/theme")  # Increased from 10 to 50


class LoglineSchema(BaseModel):
    """Logline structure"""
    premise: str = Field(..., min_length=100, max_length=500, description="Story premise")  # Increased from 10 to 100
    support_theme: str = Field(..., min_length=50, max_length=500, description="Support theme")  # Increased from 10 to 50


class TimelineSchema(BaseModel):
    """Timeline with 6 types (Peace Script v2 specification)
    
    6 Timeline Types:
    1. movie_duration: Duration in minutes (30-300)
    2. seasons: Season or TV season/episode structure
    3. date: Specific date/period/historical era
    4. social: Social context/environment
    5. economic: Economic situation
    6. environment: Physical/geographical setting
    """
    movie_duration: int = Field(
        120, 
        ge=30, 
        le=300, 
        description="Movie duration in minutes (30-300)"
    )
    seasons: str = Field(
        ..., 
        min_length=1,
        max_length=200,
        description="Season (ฤดูกาล) or TV season/episode structure (e.g., 'ฤดูร้อน', 'Season 1: 8 episodes')"
    )
    date: str = Field(
        ..., 
        min_length=1,
        max_length=200, 
        description="Date/period/historical era (e.g., 'พ.ศ. 2568', '15 มีนาคม 2568', 'World War II era')"
    )
    social: str = Field(
        ..., 
        min_length=1,
        max_length=2000, 
        description="Social context/environment (e.g., 'สังคมไทยหลังโควิด', 'Post-war society')"
    )
    economic: str = Field(
        ..., 
        min_length=1,
        max_length=2000, 
        description="Economic situation (e.g., 'ภาวะเศรษฐกิจถดถอย', 'Economic boom')"
    )
    environment: str = Field(
        ..., 
        min_length=1,
        max_length=2000, 
        description="Physical/geographical setting (e.g., 'ชนบทภาคอีสาน', 'Urban Bangkok', 'Rural village')"
    )


class SynopsisSchema(BaseModel):
    """Synopsis/Story Summary structure"""
    content: str = Field(..., min_length=1000, max_length=5000, description="Synopsis/เรื่องย่อ content")


class ScopeCreate(BaseModel):
    """Schema for creating Scope of Story (Step 2)"""
    project_id: str = Field(..., description="Parent project ID")
    big_idea: BigIdeaSchema
    premise: PremiseSchema
    theme: ThemeSchema
    logline: LoglineSchema
    timeline: TimelineSchema
    synopsis: Optional[SynopsisSchema] = None  # เรื่องย่อ (optional)
    
    class Config:
        schema_extra = {
            "example": {
                "project_id": "proj_001",
                "big_idea": {
                    "prefix": "what_will_happen_if",
                    "content": "a man discovers he can travel back in time"
                },
                "premise": {
                    "question": "What happens when you can change the past?",
                    "answer": "Every change creates a worse future"
                },
                "theme": {
                    "teaching": "This tale teaches that",
                    "lesson": "we must accept our past to move forward"
                },
                "logline": {
                    "premise": "A time traveler tries to fix his mistakes",
                    "support_theme": "but learns that changing the past destroys the future"
                },
                "timeline": {
                    "movie_duration": 120,
                    "seasons": "ฤดูหนาว",
                    "date": "พ.ศ. 2568 (ปัจจุบัน)",
                    "social": "สังคมพึ่งพาเทคโนโลยีอย่างมาก",
                    "economic": "ความเหลื่อมล้ำทางเศรษฐกิจสูง",
                    "environment": "การเปลี่ยนแปลงสภาพภูมิอากาศส่งผลต่อชีวิตประจำวัน"
                }
            }
        }


class ScopeUpdate(BaseModel):
    """Schema for updating Scope of Story"""
    big_idea: Optional[BigIdeaSchema] = None
    premise: Optional[PremiseSchema] = None
    theme: Optional[ThemeSchema] = None
    logline: Optional[LoglineSchema] = None
    timeline: Optional[TimelineSchema] = None
    synopsis: Optional[SynopsisSchema] = None  # เรื่องย่อ (optional)


class ScopeResponse(BaseModel):
    """Schema for Scope response"""
    id: str
    project_id: str
    big_idea: BigIdeaSchema
    premise: PremiseSchema
    theme: ThemeSchema
    logline: LoglineSchema
    timeline: TimelineSchema
    synopsis: Optional[SynopsisSchema] = None  # เรื่องย่อ (optional)
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# =============================================================================
# SCENE SCHEMAS
# =============================================================================

class SceneCreate(BaseModel):
    """Schema for creating a new scene"""
    project_id: str = Field(..., description="Parent project ID")
    scene_number: int = Field(..., ge=1, description="Scene number in screenplay")
    point_number: int = Field(..., ge=1, le=15, description="Story point (1-15)")
    chapter_number: int = Field(..., ge=1, le=3, description="Act number (1-3)")
    title: str = Field(..., min_length=1, max_length=200, description="Scene title")
    description: Optional[str] = Field(None, description="Scene description")
    location: Optional[str] = Field(None, max_length=200, description="Location/setting")
    time_of_day: Optional[str] = Field(None, max_length=50, description="Time of day")
    
    @validator('point_number')
    def validate_point_number(cls, v):
        if v < 1 or v > 15:
            raise ValueError('point_number must be between 1 and 15 (5 points x 3 acts)')
        return v
    
    @validator('chapter_number')
    def validate_chapter_number(cls, v):
        if v < 1 or v > 3:
            raise ValueError('chapter_number must be between 1 and 3')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "project_id": "proj_001",
                "scene_number": 1,
                "point_number": 1,
                "chapter_number": 1,
                "title": "การเผชิญหน้าครั้งแรก",
                "description": "ผู้ชายลึกลับเดินเข้ามาในร้านกาแฟ",
                "location": "ร้านกาแฟในเมือง",
                "time_of_day": "evening"
            }
        }


class SceneUpdate(BaseModel):
    """Schema for updating a scene"""
    scene_number: Optional[int] = Field(None, ge=1)
    point_number: Optional[int] = Field(None, ge=1, le=15)
    chapter_number: Optional[int] = Field(None, ge=1, le=3)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=200)
    time_of_day: Optional[str] = Field(None, max_length=50)


class SceneResponse(BaseModel):
    """Schema for scene response"""
    id: str
    project_id: str
    scene_number: int
    point_number: int
    chapter_number: int
    title: str
    description: Optional[str]
    location: Optional[str]
    time_of_day: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# =============================================================================
# CHARACTER SCHEMAS
# =============================================================================

class CharacterGoals(BaseModel):
    """Character Goals Structure (Peace Script v2 specification)
    
    5 Components of Character Goals:
    1. objective - เป้าหมายที่ชัดเจน (What they want)
    2. need - ความต้องการภายใน (What they need - may differ from want)
    3. action - การกระทำเพื่อบรรลุเป้าหมาย (What they do to achieve it)
    4. conflict - อุปสรรคที่ต้องเผชิญ (What stands in their way)
    5. backstory - ประวัติที่นำมาสู่เป้าหมายนี้ (Why they want/need it)
    
    Example:
        ```python
        goals = CharacterGoals(
            objective="แสวงหาความยุติธรรมให้ครอบครัว",
            need="ต้องการให้อดีตได้พักผ่อน ไม่ต้องถูกหลอกหลอนอีกต่อไป",
            action="สืบสวนคดีฆาตกรรมด้วยตัวเอง เสี่ยงชีวิตเพื่อหาความจริง",
            conflict="ทีมงานตำรวจไม่เชื่อ คนร้ายมีอำนาจ และอดีตของเธอเองทำให้หวั่นไหว",
            backstory="สูญเสียครอบครัวจากการฆาตกรรมเมื่อ 5 ปีก่อน คดีไม่ได้รับความยุติธรรม"
        )
        ```
    """
    objective: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="เป้าหมายที่ชัดเจน - What the character wants (external goal)"
    )
    need: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="ความต้องการภายใน - What the character needs (internal need, may differ from want)"
    )
    action: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="การกระทำเพื่อบรรลุเป้าหมาย - What the character does to achieve their goal"
    )
    conflict: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="อุปสรรคที่ต้องเผชิญ - What stands in the character's way (obstacles, antagonists)"
    )
    backstory: str = Field(
        ...,
        min_length=20,
        max_length=2000,
        description="ประวัติที่นำมาสู่เป้าหมายนี้ - Background/history that led to this goal"
    )

    class Config:
        schema_extra = {
            "example": {
                "objective": "แสวงหาความยุติธรรมให้ครอบครัว",
                "need": "ต้องการให้อดีตได้พักผ่อน ไม่ต้องถูกหลอกหลอนอีกต่อไป",
                "action": "สืบสวนคดีฆาตกรรมด้วยตัวเอง เสี่ยงชีวิตเพื่อหาความจริง",
                "conflict": "ทีมงานตำรวจไม่เชื่อ คนร้ายมีอำนาจ และอดีตของเธอเองทำให้หวั่นไหว",
                "backstory": "สูญเสียครอบครัวจากการฆาตกรรมเมื่อ 5 ปีก่อน คดีไม่ได้รับความยุติธรรม"
            }
        }


class CharacterGenerateRequest(BaseModel):
    """Schema for AI character generation request"""
    project_id: str = Field(..., description="Project ID to generate characters for")
    character_count: Optional[int] = Field(5, ge=1, le=20, description="Number of characters to generate (1-20)")
    
    class Config:
        schema_extra = {
            "example": {
                "project_id": "proj_001",
                "character_count": 5
            }
        }


class CharacterCreate(BaseModel):
    """Schema for creating a new character (Peace Script v2)
    
    Now uses structured CharacterGoals instead of separate fields.
    For backward compatibility, can accept either:
    - goals: CharacterGoals (preferred)
    - OR old fields: background, motivation, conflict (auto-converted)
    """
    project_id: str = Field(..., description="Parent project ID")
    name: str = Field(..., min_length=1, max_length=100, description="Character name")
    role: CharacterRole = Field(..., description="Character role in story")
    actor_id: Optional[str] = Field(None, description="Reference to ActorProfile (Digital Actor system)")
    age: Optional[int] = Field(None, ge=0, le=120, description="Character age")
    gender: Optional[str] = Field(None, description="Character gender (male/female/non-binary)")
    personality: Optional[str] = Field(None, description="Personality traits")
    appearance: Optional[str] = Field(None, description="Physical appearance")
    
    # NEW: Structured Character Goals (Peace Script v2)
    goals: Optional[CharacterGoals] = Field(
        None, 
        description="Character goals structure (objective, need, action, conflict, backstory)"
    )
    
    # OLD fields (deprecated, kept for backward compatibility)
    background: Optional[str] = Field(None, description="[DEPRECATED] Use goals.backstory instead")
    motivation: Optional[str] = Field(None, description="[DEPRECATED] Use goals.objective instead")
    conflict: Optional[str] = Field(None, description="[DEPRECATED] Use goals.conflict instead")
    
    arc_type: Optional[str] = Field(None, description="Character arc type")
    
    # NEW: Auto-create Actor Profile flag
    auto_create_actor: bool = Field(
        default=True,
        description="Auto-generate comprehensive Actor Profile using AI (recommended)"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "project_id": "proj_001",
                "name": "รินรดา สมพงษ์",
                "role": "protagonist",
                "age": 28,
                "gender": "female",
                "personality": "เข้มแข็ง มุ่งมั่น แต่มีอดีตที่ทรมาน",
                "appearance": "ผู้หญิงสูง ผมยาวดำ ดวงตาคม",
                "arc_type": "transformation",
                "goals": {
                    "objective": "แสวงหาความยุติธรรมให้ครอบครัวที่ถูกฆ่า",
                    "need": "ต้องการปลดปล่อยตัวเองจากความรู้สึกผิดที่ไม่สามารถช่วยพวกเขาได้",
                    "action": "สืบสวนคดีฆาตกรรมด้วยตัวเอง แม้จะต้องเสี่ยงชีวิตและผิดกฎหมาย",
                    "conflict": "ตำรวจไม่เชื่อหลักฐานของเธอ คนร้ายมีอำนาจสูง อดีตทำให้เธอหวั่นไหว",
                    "backstory": "5 ปีก่อนครอบครัวถูกฆาตกรรม คดีถูกปิดไป เธอจึงต้องหาความจริงด้วยตัวเอง"
                },
                "auto_create_actor": True
            }
        }


class CharacterUpdate(BaseModel):
    """Schema for updating a character (Peace Script v2)
    
    Now uses structured CharacterGoals instead of separate fields.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[CharacterRole] = None
    actor_id: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=120)
    gender: Optional[str] = None
    personality: Optional[str] = None
    appearance: Optional[str] = None
    
    # NEW: Structured Character Goals
    goals: Optional[CharacterGoals] = None
    
    # OLD fields (deprecated, kept for backward compatibility)
    background: Optional[str] = None
    motivation: Optional[str] = None
    conflict: Optional[str] = None
    
    arc_type: Optional[str] = None


class CharacterResponse(BaseModel):
    """Schema for character response (Peace Script v2)
    
    Returns structured CharacterGoals + old fields for backward compatibility.
    """
    id: str
    project_id: str
    name: str
    role: CharacterRole
    actor_id: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    personality: Optional[str]
    appearance: Optional[str]
    
    # NEW: Structured Character Goals
    goals: Optional[CharacterGoals] = None
    
    # OLD fields (deprecated, provided for backward compatibility)
    background: Optional[str] = None
    motivation: Optional[str] = None
    conflict: Optional[str] = None
    
    arc_type: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# =============================================================================
# SHOT SCHEMAS
# =============================================================================

class ShotCreate(BaseModel):
    """Schema for creating a new shot"""
    scene_id: str = Field(..., description="Parent scene ID")
    shot_number: int = Field(..., ge=1, description="Shot number in scene")
    shot_title: str = Field(..., min_length=1, max_length=200, description="Shot title")
    shot_description: Optional[str] = Field(None, description="Shot description")
    camera_angle: Optional[str] = Field(None, max_length=50, description="Camera angle")
    camera_movement: Optional[str] = Field(None, max_length=50, description="Camera movement")
    lens_type: Optional[str] = Field(None, max_length=50, description="Lens type")
    lighting_type: Optional[str] = Field(None, max_length=50, description="Lighting setup")
    lighting_time: Optional[str] = Field(None, max_length=50, description="Time of day for lighting")
    duration_seconds: Optional[int] = Field(None, ge=1, description="Shot duration in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "scene_id": "scene_001",
                "shot_number": 1,
                "shot_title": "Establishing Shot",
                "shot_description": "Wide shot ของร้านกาแฟจากภายนอก",
                "camera_angle": "eye-level",
                "camera_movement": "static",
                "lens_type": "wide",
                "lighting_type": "natural",
                "lighting_time": "evening",
                "duration_seconds": 5
            }
        }


class ShotUpdate(BaseModel):
    """Schema for updating a shot"""
    shot_number: Optional[int] = Field(None, ge=1)
    shot_title: Optional[str] = Field(None, min_length=1, max_length=200)
    shot_description: Optional[str] = None
    camera_angle: Optional[str] = Field(None, max_length=50)
    camera_movement: Optional[str] = Field(None, max_length=50)
    lens_type: Optional[str] = Field(None, max_length=50)
    lighting_type: Optional[str] = Field(None, max_length=50)
    lighting_time: Optional[str] = Field(None, max_length=50)
    duration_seconds: Optional[int] = Field(None, ge=1)


class ShotResponse(BaseModel):
    """Schema for shot response"""
    id: str
    scene_id: str
    shot_number: int
    shot_title: str
    shot_description: Optional[str]
    camera_angle: Optional[str]
    camera_movement: Optional[str]
    lens_type: Optional[str]
    lighting_type: Optional[str]
    lighting_time: Optional[str]
    duration_seconds: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# =============================================================================
# CHARACTER-ACTOR LINKING SCHEMAS (NEW)
# =============================================================================

class LinkActorRequest(BaseModel):
    """Schema for linking existing Actor to Character"""
    actor_id: str = Field(..., description="ActorProfile ID to link")
    
    class Config:
        schema_extra = {
            "example": {
                "actor_id": "ACT-20241110-A1B2C3"
            }
        }


class CharacterWithActorResponse(BaseModel):
    """Schema for character response with embedded actor data"""
    # Character fields
    id: str
    project_id: str
    name: str
    role: CharacterRole
    actor_id: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    personality: Optional[str]
    appearance: Optional[str]
    background: Optional[str]
    arc_type: Optional[str]
    motivation: Optional[str]
    conflict: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    # Embedded Actor (if exists)
    actor: Optional[Dict[str, Any]] = Field(
        None,
        description="Embedded ActorProfile data (if actor_id is set)"
    )
    
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BatchGenerateActorsRequest(BaseModel):
    """Schema for batch generating actors for multiple characters"""
    character_ids: List[str] = Field(
        ...,
        description="List of character IDs to generate actors for (1-50 items)"
    )
    
    @validator('character_ids')
    def validate_character_ids(cls, v):
        """Validate character_ids length"""
        if not v or len(v) == 0:
            raise ValueError('At least one character_id is required')
        if len(v) > 50:
            raise ValueError('Maximum 50 character_ids allowed')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "character_ids": [
                    "char_001",
                    "char_002",
                    "char_003"
                ]
            }
        }


class BatchGenerateActorsResponse(BaseModel):
    """Schema for batch generation response"""
    total: int = Field(..., description="Total characters requested")
    created: int = Field(..., description="Number of actors successfully created")
    skipped: int = Field(..., description="Number already had actors")
    errors: List[str] = Field(
        default_factory=list,
        description="List of error messages"
    )
    created_actor_ids: List[str] = Field(
        default_factory=list,
        description="List of created actor IDs"
    )
    skipped_character_ids: List[str] = Field(
        default_factory=list,
        description="List of character IDs that were skipped (already had actors)"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "total": 5,
                "created": 3,
                "skipped": 1,
                "errors": ["Character 'char_004' not found"],
                "created_actor_ids": ["ACT-20241110-A1B2C3", "ACT-20241110-D4E5F6"],
                "skipped_character_ids": ["char_001"]
            }
        }


# =============================================================================
# VISUAL SCHEMAS
# =============================================================================

class VisualCreate(BaseModel):
    """Schema for creating a new visual"""
    shot_id: str = Field(..., description="Parent shot MongoDB ObjectId")
    project_id: Optional[str] = Field(None, description="Parent project ID (optional)")
    image_prompt: Optional[str] = Field(None, max_length=2000, description="AI generation prompt")
    image_url: Optional[str] = Field(None, description="Generated image URL")
    video_url: Optional[str] = Field(None, description="Generated video URL")
    generation_provider: str = Field("stable-diffusion", max_length=50, description="AI provider")
    generation_params: Dict[str, Any] = Field(default_factory=dict, description="Generation parameters")
    status: VisualStatus = Field(VisualStatus.PENDING, description="Generation status")
    error_message: Optional[str] = Field(None, max_length=1000, description="Error message if failed")
    
    class Config:
        schema_extra = {
            "example": {
                "shot_id": "68fcace553611223c213415c",
                "image_prompt": "A cinematic wide shot of a haunted mansion exterior at night",
                "generation_provider": "stable-diffusion",
                "status": "pending"
            }
        }


class VisualUpdate(BaseModel):
    """Schema for updating a visual"""
    image_prompt: Optional[str] = Field(None, max_length=2000)
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    generation_provider: Optional[str] = Field(None, max_length=50)
    generation_params: Optional[Dict[str, Any]] = None
    status: Optional[VisualStatus] = None
    error_message: Optional[str] = Field(None, max_length=1000)


class VisualResponse(BaseModel):
    """Schema for visual response"""
    id: str
    shot_id: str
    project_id: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    image_prompt: Optional[str] = None
    generation_provider: str = "stable-diffusion"
    generation_params: Dict[str, Any] = {}
    status: VisualStatus
    error_message: Optional[str] = None
    generated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
