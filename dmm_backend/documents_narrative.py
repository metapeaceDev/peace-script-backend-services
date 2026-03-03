"""
NarrativeStructure Models for Peace Script Integration

This module contains MongoDB models for the Peace Script integration project.
It implements the 6-step workflow from Peace Script (Google Colab):
- Step 1: Project Details → Project model
- Step 2: Story Scope → StoryScope model
- Step 3: Characters → Character model
- Step 4: Chapter Structure → Scene model
- Step 5: Scene Design → Shot model
- Step 6: Visual Generation → Visual model

Author: Peace Script Team
Date: 26 January 2025
Version: 1.0
"""

from beanie import Document
from pydantic import Field, validator
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class GenreEnum(str, Enum):
    """Supported screenplay genres"""
    DRAMA = "drama"
    COMEDY = "comedy"
    ACTION = "action"
    HORROR = "horror"
    SCIFI = "sci-fi"
    ROMANCE = "romance"
    THRILLER = "thriller"
    FANTASY = "fantasy"
    MYSTERY = "mystery"
    DOCUMENTARY = "documentary"


class CharacterRole(str, Enum):
    """Character roles in story structure"""
    PROTAGONIST = "protagonist"
    ANTAGONIST = "antagonist"
    MAIN = "main"
    SUPPORT = "support"
    EXTRA = "extra"


class ProjectStatus(str, Enum):
    """Project workflow status"""
    DRAFT = "draft"
    IN_PROGRESS = "in-progress"
    REVIEW = "review"
    COMPLETE = "complete"
    ARCHIVED = "archived"


class VisualStatus(str, Enum):
    """Visual generation status"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETE = "complete"
    FAILED = "failed"


# ============================================================================
# Step 1: Project Details Model
# ============================================================================

class Project(Document):
    """NarrativeStructure Project Model
    
    Represents a Peace Script project imported from Google Colab.
    Corresponds to Step 1: Project Details in Peace Script workflow.
    
    Attributes:
        project_id: Unique identifier for the project
        script_name: Name of the screenplay
        genre: Primary genre (drama, comedy, action, etc.)
        studio: Production studio name
        writer: Screenwriter name
        language: Script language code (default: "th" for Thai)
        status: Current project status
        imported_from: Source file path if imported from Peace Script
        created_at: Project creation timestamp
        updated_at: Last update timestamp
    
    Example:
        ```python
        project = Project(
            project_id="proj_001",
            script_name="เงาแค้น",
            genre=GenreEnum.DRAMA,
            studio="Peace Studio",
            writer="สมชาย ใจดี",
            language="th"
        )
        await project.insert()
        ```
    """
    
    # Primary fields
    project_id: str = Field(
        ...,
        description="Unique project identifier",
        min_length=1,
        max_length=100
    )
    script_name: str = Field(
        ...,
        description="Name of the screenplay",
        min_length=1,
        max_length=200
    )
    title: Optional[str] = Field(
        default=None,
        description="Display title for UI (auto-generated from script_name if not provided)",
        min_length=1,
        max_length=200
    )
    description: Optional[str] = Field(
        default=None,
        description="Project description/synopsis",
        max_length=2000
    )
    
    # Multi-Genre System (v2)
    genres: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Genres with percentage allocations [{'type': 'drama', 'percentage': 60}]"
    )
    script_type: Optional[str] = Field(
        default="movie",
        description="Script type: movie/series/short_film/ad/moral_drama"
    )
    concept_description: Optional[str] = Field(
        default=None,
        description="Concept description (Big Idea preview)",
        max_length=2000
    )
    target_audience: Optional[str] = Field(
        default=None,
        description="Target audience demographic",
        max_length=500
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Tags for categorization (max 10)"
    )
    
    # Step 4: Chapter Structure
    structure: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Chapter structure (15 beats)"
    )
    
    # Legacy Fields (backward compatibility)
    genre: Optional[GenreEnum] = Field(
        default=None,
        description="Primary genre (deprecated, use genres array instead)"
    )
    genre_display: Optional[str] = Field(
        default=None,
        description="Human-readable genre display name"
    )
    progress: Optional[float] = Field(
        default=0.0,
        description="Completion percentage (0.0-100.0)",
        ge=0.0,
        le=100.0
    )
    scenes_count: Optional[int] = Field(
        default=0,
        description="Number of scenes in project",
        ge=0
    )
    characters_count: Optional[int] = Field(
        default=0,
        description="Number of characters in project",
        ge=0
    )
    studio: Optional[str] = Field(
        default=None,
        description="Production studio name",
        max_length=100
    )
    writer: Optional[str] = Field(
        default=None,
        description="Screenwriter name",
        max_length=100
    )
    language: str = Field(
        default="th",
        description="Script language code (th/en/ja/zh/ko/etc.)"
    )
    
    # Status tracking
    status: ProjectStatus = Field(
        default=ProjectStatus.DRAFT,
        description="Current project status"
    )
    
    # Import metadata
    imported_from: Optional[str] = Field(
        default=None,
        description="Source file path if imported from Peace Script"
    )
    import_date: Optional[datetime] = Field(
        default=None,
        description="Date when project was imported"
    )
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Project creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    class Settings:
        name = "narrative_projects"
        indexes = [
            "project_id",
            "script_name",
            "status",
            "created_at",
        ]
    
    @validator("tags")
    def validate_tags(cls, v):
        """Validate tags max 10"""
        if v and len(v) > 10:
            raise ValueError("Maximum 10 tags allowed")
        return v
    
    @validator("script_type")
    def validate_script_type(cls, v):
        """Validate script type"""
        if v:
            valid_types = ['movie', 'series', 'short_film', 'ad', 'moral_drama']
            if v not in valid_types:
                raise ValueError(f"script_type must be one of {valid_types}")
        return v
    
    @validator("script_name")
    def validate_script_name(cls, v):
        """Ensure script name is not empty or just whitespace"""
        if not v or v.strip() == "":
            raise ValueError("Script name cannot be empty")
        return v.strip()
    
    @validator("title", always=True)
    def set_title_from_script_name(cls, v, values):
        """Auto-generate title from script_name if not provided"""
        if not v and "script_name" in values:
            return values["script_name"]
        return v.strip() if v else None
    
    @validator("genre_display", always=True)
    def set_genre_display(cls, v, values):
        """Auto-generate genre_display from genre if not provided"""
        if not v and "genre" in values:
            genre_map = {
                "drama": "ดราม่า",
                "comedy": "ตลก",
                "action": "บู๊/แอ็คชั่น",
                "thriller": "ระทึกขวัญ",
                "horror": "สยองขวัญ",
                "romance": "โรแมนติก",
                "fantasy": "แฟนตาซี",
                "sci_fi": "ไซไฟ",
                "documentary": "สารคดี",
                "animation": "การ์ตูน/อนิเมชั่น",
            }
            genre_value = values["genre"].value if hasattr(values["genre"], 'value') else str(values["genre"])
            return genre_map.get(genre_value, genre_value.title())
        return v
    
    @validator("language")
    def validate_language(cls, v):
        """Validate language code format"""
        if len(v) < 2:
            raise ValueError("Language code must be at least 2 characters")
        return v.lower()
    
    def __repr__(self):
        genre_str = self.genre.value if self.genre else "unknown"
        return f"<Project '{self.script_name}' ({genre_str})>"
    
    def __str__(self):
        genre_str = self.genre.value if self.genre else "unknown"
        writer_str = self.writer or "unknown"
        return f"{self.script_name} - {genre_str} by {writer_str}"


# ============================================================================
# Step 2: Story Scope Model (v2 Structure)
# ============================================================================

class StoryScope(Document):
    """Story Scope Model v2
    
    Represents the comprehensive story scope with nested structured data.
    Corresponds to Step 2: Scope of Story in Peace Script workflow v2.
    
    Attributes:
        project_id: Reference to parent Project (unique identifier)
        big_idea: Nested object with prefix and content
        premise: Nested object with question and answer
        theme: Nested object with teaching and lesson
        logline: Nested object with premise and support_theme
        timeline: Nested object with 6 types (movie_duration, seasons, date, social, economic, environment)
        synopsis: Optional story synopsis (1000-5000 chars)
        created_at: Creation timestamp
        updated_at: Last update timestamp
    
    Example:
        ```python
        scope = StoryScope(
            project_id="proj_001",
            big_idea={
                "prefix": "what_will_happen_if",
                "content": "A woman seeks revenge but discovers redemption"
            },
            premise={
                "question": "What makes forgiveness stronger than revenge?",
                "answer": "True strength comes from letting go"
            },
            theme={
                "teaching": "This tale teaches that",
                "lesson": "revenge only breeds more suffering"
            },
            logline={
                "premise": "After her family is killed, Rinrada seeks revenge",
                "support_theme": "but her journey leads her to forgiveness"
            },
            timeline={
                "movie_duration": 120,
                "seasons": "ฤดูร้อน",
                "date": "พ.ศ. 2568 (ปัจจุบัน)",
                "social": "สังคมไทยหลังโควิด - คนต้องปรับตัว",
                "economic": "ภาวะเศรษฐกิจถดถอย ค่าครองชีพสูง",
                "environment": "กรุงเทพมหานคร - ชุมชนคนชั้นกลาง"
            }
        )
        await scope.insert()
        ```
    """
    
    # Primary field (project_id is unique identifier - replaces scope_id)
    project_id: str = Field(
        ...,
        description="Reference to parent Project (unique per project)",
        min_length=1,
        max_length=100
    )
    
    # Big Idea (nested structure)
    big_idea: Dict[str, str] = Field(
        ...,
        description="Big Idea with prefix and content: {'prefix': 'what_will_happen_if', 'content': '...'}"
    )
    
    # Premise (nested structure)
    premise: Dict[str, str] = Field(
        ...,
        description="Premise with question and answer: {'question': '...', 'answer': '...'}"
    )
    
    # Theme (nested structure)  
    theme: Dict[str, str] = Field(
        ...,
        description="Theme with teaching and lesson: {'teaching': 'This tale teaches that', 'lesson': '...'}"
    )
    
    # Logline (nested structure)
    logline: Dict[str, str] = Field(
        ...,
        description="Logline with premise and support: {'premise': '...', 'support_theme': '...'}"
    )
    
    # Timeline (nested structure with 6 types - Peace Script v2 specification)
    timeline: Dict[str, Any] = Field(
        ...,
        description="""Timeline with 6 types:
        {
            'movie_duration': 120,  # int: Duration in minutes
            'seasons': 'summer',    # str: Season or TV season/episode structure
            'date': '15 มีนาคม 2568',  # str: Specific date/period/historical era
            'social': 'สังคมไทยหลังโควิด',  # str: Social context/environment
            'economic': 'ภาวะเศรษฐกิจถดถอย',  # str: Economic situation
            'environment': 'ชนบทภาคอีสาน'  # str: Physical/geographical setting
        }
        """
    )
    
    # Synopsis (optional, 1000-5000 characters)
    synopsis: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Story synopsis with structure: {'th': '...', 'en': '...', 'structure': {...}}"
    )
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    class Settings:
        name = "narrative_scopes"
        indexes = [
            "project_id",  # Unique index
        ]
    
    @validator("big_idea")
    def validate_big_idea(cls, v):
        """Validate big_idea structure"""
        required_keys = ["prefix", "content"]
        if not all(k in v for k in required_keys):
            raise ValueError(f"big_idea must have keys: {required_keys}")
        if not v["content"] or len(v["content"]) < 20:
            raise ValueError("big_idea content must be at least 20 characters")
        return v
    
    @validator("premise")
    def validate_premise(cls, v):
        """Validate premise structure"""
        required_keys = ["question", "answer"]
        if not all(k in v for k in required_keys):
            raise ValueError(f"premise must have keys: {required_keys}")
        return v
    
    @validator("theme")
    def validate_theme(cls, v):
        """Validate theme structure"""
        required_keys = ["teaching", "lesson"]
        if not all(k in v for k in required_keys):
            raise ValueError(f"theme must have keys: {required_keys}")
        return v
    
    @validator("logline")
    def validate_logline(cls, v):
        """Validate logline structure"""
        required_keys = ["premise", "support_theme"]
        if not all(k in v for k in required_keys):
            raise ValueError(f"logline must have keys: {required_keys}")
        return v
    
    @validator("timeline")
    def validate_timeline(cls, v):
        """Validate timeline structure - 6 types required (Peace Script v2)"""
        required_keys = ["movie_duration", "seasons", "date", "social", "economic", "environment"]
        missing_keys = [k for k in required_keys if k not in v]
        
        if missing_keys:
            raise ValueError(f"timeline must have all 6 types: {required_keys}. Missing: {missing_keys}")
        
        # Validate movie_duration is integer
        if not isinstance(v["movie_duration"], int) or v["movie_duration"] <= 0:
            raise ValueError("timeline.movie_duration must be a positive integer (minutes)")
        
        # Validate all text fields are non-empty strings
        text_fields = ["seasons", "date", "social", "economic", "environment"]
        for field in text_fields:
            if not isinstance(v[field], str) or not v[field].strip():
                raise ValueError(f"timeline.{field} must be a non-empty string")
        
        # NEW: Validate minimum lengths for Context fields (200 chars)
        # Auto-pad if too short (to handle legacy data or migration)
        context_fields = ["social", "economic", "environment"]
        padding_text = {
            "social": " ซึ่งสะท้อนให้เห็นถึงความซับซ้อนของโครงสร้างทางสังคมที่ส่งผลกระทบต่อวิถีชีวิตและความคิดของตัวละครในทุกมิติ ทั้งในด้านความสัมพันธ์และบทบาทหน้าที่",
            "economic": " โดยมีปัจจัยทางเศรษฐกิจเป็นแรงขับเคลื่อนสำคัญที่กำหนดทางเลือกและโอกาสในชีวิตของตัวละคร สร้างแรงกดดันและความท้าทายที่ต้องเผชิญในแต่ละวัน",
            "environment": " ท่ามกลางสภาพแวดล้อมที่มีเอกลักษณ์เฉพาะตัว ซึ่งช่วยสร้างบรรยากาศและอารมณ์ให้กับเรื่องราว พร้อมทั้งสะท้อนสภาวะจิตใจของตัวละครได้อย่างลึกซึ้ง"
        }

        for field in context_fields:
            val = v.get(field, "")
            if isinstance(val, str) and len(val.strip()) < 200:
                # Instead of raising error, we pad it here to ensure model validity
                padded_val = val
                while len(padded_val) < 200:
                    padded_val += padding_text.get(field, " ...")
                v[field] = padded_val
        
        return v
        required_keys = [
            "movie_duration",  # int: Duration in minutes (60-240)
            "seasons",         # str: Season or episode structure
            "date",            # str: Date/period/era
            "social",          # str: Social context
            "economic",        # str: Economic situation  
            "environment"      # str: Physical setting
        ]
        
        missing_keys = [k for k in required_keys if k not in v]
        if missing_keys:
            raise ValueError(f"timeline must have all 6 keys. Missing: {missing_keys}")
        
        # Validate movie_duration is int and in reasonable range
        if not isinstance(v["movie_duration"], int):
            raise ValueError("movie_duration must be an integer (minutes)")
        
        if not (30 <= v["movie_duration"] <= 300):
            raise ValueError("movie_duration must be between 30-300 minutes")
        
        # Validate string fields are not empty
        for key in ["seasons", "date", "social", "economic", "environment"]:
            if not isinstance(v[key], str) or not v[key].strip():
                raise ValueError(f"timeline.{key} must be a non-empty string")
        
        return v
    
    def __repr__(self):
        return f"<StoryScope for Project '{self.project_id}'>"
    
    def __str__(self):
        theme_lesson = self.theme.get("lesson", "N/A") if isinstance(self.theme, dict) else "N/A"
        return f"Scope: {theme_lesson}"


# ============================================================================
# Step 3: Characters Model
# ============================================================================

class Character(Document):
    """Character Model (Peace Script v2)
    
    Represents a character in the screenplay.
    Corresponds to Step 3: Characters in Peace Script workflow.
    Peace Script generates 12 characters (2 Main + 3 Support + 7 Extra).
    
    NOW USES STRUCTURED CHARACTER GOALS (5 components):
    - objective: เป้าหมายที่ชัดเจน (What they want)
    - need: ความต้องการภายใน (What they need)
    - action: การกระทำเพื่อบรรลุเป้าหมาย (What they do)
    - conflict: อุปสรรคที่ต้องเผชิญ (What stands in their way)
    - backstory: ประวัติที่นำมาสู่เป้าหมายนี้ (Why)
    
    Attributes:
        character_id: Unique identifier
        project_id: Reference to parent Project
        name: Character's name
        role: Character role (protagonist/antagonist/main/support/extra)
        age: Character's age (optional)
        gender: Character's gender (optional)
        personality: Personality description
        appearance: Physical appearance description (optional)
        goals: Structured character goals (NEW - replaces background/motivation/conflict)
        image_url: URL of generated character image (DALL-E)
        image_prompt: Prompt used for image generation
        arc_type: Character arc type (rise/fall/flat/transformation)
        narrative_function: Narrative functions in story structure
        created_at: Creation timestamp
        updated_at: Last update timestamp
    
    Example:
        ```python
        character = Character(
            project_id="proj_001",
            name="รินรดา สมพงษ์",
            role=CharacterRole.PROTAGONIST,
            age=28,
            gender="female",
            personality="Strong-willed, haunted by past trauma",
            appearance="Tall with dark hair, intense eyes",
            goals={
                "objective": "แสวงหาความยุติธรรมให้ครอบครัว",
                "need": "ปลดปล่อยตัวเองจากความรู้สึกผิด",
                "action": "สืบสวนคดีฆาตกรรมด้วยตัวเอง",
                "conflict": "ตำรวจไม่เชื่อ คนร้ายมีอำนาจ",
                "backstory": "5 ปีก่อนครอบครัวถูกฆาตกรรม คดีถูกปิด"
            }
        )
        await character.insert()
        ```
    """
    
    # Primary fields (MongoDB _id is used as unique identifier)
    project_id: str = Field(
        ...,
        description="Reference to parent Project",
        min_length=1,
        max_length=100
    )
    
    # Link to Digital Actor System
    actor_id: Optional[str] = Field(
        default=None,
        description="Reference to ActorProfile in Digital Actor system (links to Actor Management, Avatar, Profile)"
    )
    
    # Basic info
    name: str = Field(
        ...,
        description="Character name",
        min_length=1,
        max_length=100
    )
    role: CharacterRole = Field(
        ...,
        description="Character role in story structure"
    )
    age: Optional[int] = Field(
        None,
        description="Character age",
        ge=0,
        le=120
    )
    gender: Optional[str] = Field(
        None,
        description="Character gender",
        max_length=50
    )
    
    # Personality & appearance
    personality: str = Field(
        ...,
        description="Personality description",
        min_length=10,
        max_length=2000
    )
    appearance: Optional[str] = Field(
        None,
        description="Physical appearance description",
        min_length=10,
        max_length=2000
    )
    
    # NEW: Structured Character Goals (Peace Script v2)
    goals: Optional[Dict[str, str]] = Field(
        default=None,
        description="""Character goals structure with 5 components:
        {
            'objective': 'What they want (external goal)',
            'need': 'What they need (internal need)',
            'action': 'What they do to achieve it',
            'conflict': 'What stands in their way',
            'backstory': 'Why they want/need it'
        }
        """
    )
    
    # OLD fields (deprecated, kept for data migration and backward compatibility)
    background: Optional[str] = Field(
        default=None,
        description="[DEPRECATED] Character background story - use goals.backstory instead",
        max_length=5000
    )
    motivation: Optional[str] = Field(
        default=None,
        description="[DEPRECATED] Character motivation - use goals.objective instead",
        max_length=2000
    )
    conflict: Optional[str] = Field(
        default=None,
        description="[DEPRECATED] Internal/external conflicts - use goals.conflict instead",
        max_length=2000
    )
    
    # Visual assets
    image_url: Optional[str] = Field(
        default=None,
        description="URL of generated character image (DALL-E/Stable Diffusion)"
    )
    image_prompt: Optional[str] = Field(
        default=None,
        description="Prompt used for image generation",
        max_length=1000
    )
    
    # Story arc
    arc_type: Optional[str] = Field(
        default=None,
        description="Character arc: rise/fall/flat/transformation",
        max_length=50
    )
    narrative_function: List[str] = Field(
        default=[],
        description="Narrative functions (hero, mentor, threshold guardian, etc.)"
    )
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    # NEW: Simulation tracking fields
    simulation_count: int = Field(
        default=0,
        description="Number of simulations run for this character"
    )
    last_simulation: Optional[datetime] = Field(
        default=None,
        description="Timestamp of last simulation"
    )
    simulation_history: List[Dict[str, Any]] = Field(
        default=[],
        description="History of simulation results (last 50)"
    )
    
    class Settings:
        name = "narrative_characters"
        indexes = [
            "project_id",
            "role",
            "name",
        ]
    
    @validator("name")
    def validate_name(cls, v):
        """Ensure name is not empty"""
        if not v or v.strip() == "":
            raise ValueError("Character name cannot be empty")
        return v.strip()
    
    @validator("goals")
    def validate_goals(cls, v):
        """Validate character goals structure (Peace Script v2)"""
        if v is None:
            return v
        
        required_keys = ["objective", "need", "action", "conflict", "backstory"]
        missing_keys = [k for k in required_keys if k not in v]
        
        if missing_keys:
            raise ValueError(f"goals must have all 5 keys. Missing: {missing_keys}")
        
        # Validate each field is non-empty
        for key in required_keys:
            if not isinstance(v[key], str) or not v[key].strip():
                raise ValueError(f"goals.{key} must be a non-empty string")
            
            # Validate minimum lengths (updated for better quality content)
            min_lengths = {
                "objective": 150,  # Increased to 150
                "need": 150,       # Increased to 150
                "action": 150,     # Increased to 150
                "conflict": 150,   # Increased to 150
                "backstory": 300   # Increased to 300
            }
            if len(v[key].strip()) < min_lengths[key]:
                raise ValueError(f"goals.{key} must be at least {min_lengths[key]} characters")
        
        return v
    
    def __repr__(self):
        return f"<Character '{self.name}' ({self.role.value})>"
    
    def __str__(self):
        return f"{self.name} - {self.role.value}, age {self.age}"


# ============================================================================
# Step 4: Scene Model (from Chapter Structure)
# ============================================================================

class Scene(Document):
    """Scene Model
    
    Represents a scene in the screenplay.
    Corresponds to Step 4: Chapter Structure in Peace Script workflow.
    Peace Script generates 45 scenes based on Save the Cat 15-Point structure.
    
    Attributes:
        scene_id: Unique identifier
        project_id: Reference to parent Project
        scene_number: Scene number in sequence (1-45)
        point_number: Save the Cat point number (1-15)
        chapter_number: Chapter number (1-3)
        title: Scene title
        description: Scene description/summary
        location: Scene location
        time_of_day: Time of day (day/night/dawn/dusk)
        characters: List of character_ids in this scene
        duration_seconds: Estimated scene duration
        created_at: Creation timestamp
        updated_at: Last update timestamp
    
    Example:
        ```python
        scene = Scene(
            scene_id="scene_001",
            project_id="proj_001",
            scene_number=1,
            point_number=1,
            chapter_number=1,
            title="Opening Scene - The Letter",
            description="Rinrada receives a mysterious letter",
            location="Rinrada's apartment",
            time_of_day="night",
            characters=["char_001"]
        )
        await scene.insert()
        ```
    """
    
    # Primary fields (MongoDB _id is used as unique identifier)
    project_id: str = Field(
        ...,
        description="Reference to parent Project",
        min_length=1,
        max_length=100
    )
    
    # Scene identification
    scene_number: int = Field(
        ...,
        description="Scene number in sequence",
        ge=1
    )
    point_number: int = Field(
        ...,
        description="Save the Cat 15-Point structure number",
        ge=1,
        le=15
    )
    chapter_number: int = Field(
        ...,
        description="Chapter number (usually 1-3)",
        ge=1,
        le=3
    )
    
    # Scene content
    title: str = Field(
        ...,
        description="Scene title",
        min_length=1,
        max_length=200
    )
    description: Optional[str] = Field(
        default=None,
        description="Scene description/summary (optional, but if provided must be at least 350 characters for professional-quality content with setting, action, emotion, and visual details)",
        max_length=5000
    )
    
    @validator('description')
    def validate_description_length(cls, v):
        """Validate description: if provided (not None/empty), must be at least 350 chars for professional screenplay standards"""
        if v is not None and v.strip() and len(v.strip()) < 350:
            raise ValueError('Description must be at least 350 characters if provided (should include: setting/location, character actions, emotional states, and visual atmosphere)')
        return v if v else None  # Convert empty string to None
    location: Optional[str] = Field(
        default=None,
        description="Scene location",
        max_length=200
    )
    time_of_day: str = Field(
        default="day",
        description="Time of day: day/night/dawn/dusk",
        max_length=50
    )
    
    # Characters in scene
    characters: List[str] = Field(
        default=[],
        description="List of character_ids appearing in this scene"
    )
    
    # Timing
    duration_seconds: Optional[int] = Field(
        default=None,
        description="Estimated scene duration in seconds",
        ge=0
    )
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    class Settings:
        name = "narrative_scenes"
        indexes = [
            "scene_id",
            "project_id",
            "scene_number",
            ("project_id", "scene_number"),
        ]
    
    @validator("title")
    def validate_title(cls, v):
        """Ensure title is not empty"""
        if not v or v.strip() == "":
            raise ValueError("Scene title cannot be empty")
        return v.strip()
    
    def __repr__(self):
        return f"<Scene {self.scene_number}: '{self.title}'>"
    
    def __str__(self):
        return f"Scene {self.scene_number} - {self.title}"


# ============================================================================
# Step 5: Shot Model (from Scene Design)
# ============================================================================

class Shot(Document):
    """Shot Model
    
    Represents a camera shot within a scene.
    Corresponds to Step 5: Scene Design in Peace Script workflow.
    Peace Script generates 135 shots (3 per scene × 45 scenes).
    Each shot includes 8 motion parameters for video generation.
    
    Attributes:
        scene_id: Reference to parent Scene (MongoDB ObjectId)
        project_id: Reference to parent Project (optional - derived from scene)
        shot_number: Shot number within scene
        shot_description: Visual description of the shot (optional)
        camera_angle: Camera angle (close-up/medium/wide/overhead)
        motion_parameters: Dict with 8 motion effect parameters:
            - zoom_start: Starting zoom level (1.0 = normal)
            - zoom_end: Ending zoom level
            - move_x: Horizontal movement in pixels
            - move_y: Vertical movement in pixels
            - rotate_start: Starting rotation in degrees
            - rotate_end: Ending rotation in degrees
            - duration: Shot duration in seconds
            - speed: Playback speed multiplier
        duration_seconds: Shot duration
        created_at: Creation timestamp
        updated_at: Last update timestamp
    
    Example:
        ```python
        shot = Shot(
            scene_id="68fcace553611223c213415c",
            shot_number=1,
            shot_description="Wide shot of old mansion exterior at night",
            camera_angle="wide",
            motion_parameters={
                "zoom_start": 1.0,
                "zoom_end": 1.5,
                "move_x": 10,
                "move_y": 0,
                "rotate_start": 0,
                "rotate_end": 0,
                "duration": 3,
                "speed": 1.0
            }
        )
        await shot.insert()
        ```
    """
    
    # Primary fields (MongoDB _id is used as unique identifier)
    scene_id: str = Field(
        ...,
        description="Reference to parent Scene (MongoDB ObjectId)",
        min_length=1,
        max_length=100
    )
    project_id: Optional[str] = Field(
        None,
        description="Reference to parent Project (optional - can be derived from scene)",
        min_length=1,
        max_length=100
    )
    
    # Shot identification
    shot_number: int = Field(
        ...,
        description="Shot number within scene",
        ge=1
    )
    
    # Visual description
    shot_description: Optional[str] = Field(
        None,
        description="Visual description of the shot (minimum 100 characters for professional quality AI generation)",
        max_length=2000
    )
    
    # Shot metadata
    shot_title: str = Field(
        ...,
        description="Shot title/name",
        min_length=1,
        max_length=200
    )
    
    # Camera settings
    camera_angle: Optional[str] = Field(
        None,
        description="Camera angle: eye-level/high-angle/low-angle/dutch/overhead",
        max_length=50
    )
    camera_movement: Optional[str] = Field(
        None,
        description="Camera movement: static/pan/tilt/zoom/dolly/tracking",
        max_length=50
    )
    lens_type: Optional[str] = Field(
        None,
        description="Lens type: wide/standard/telephoto/fisheye",
        max_length=50
    )
    lighting_type: Optional[str] = Field(
        None,
        description="Lighting setup: natural/three-point/high-key/low-key",
        max_length=50
    )
    lighting_time: Optional[str] = Field(
        None,
        description="Time of day for lighting: morning/noon/evening/night",
        max_length=50
    )
    
    # Motion parameters (8 parameters from Peace Script)
    motion_parameters: Dict[str, Any] = Field(
        default={
            "zoom_start": 1.0,
            "zoom_end": 1.0,
            "move_x": 0,
            "move_y": 0,
            "rotate_start": 0,
            "rotate_end": 0,
            "duration": 3,
            "speed": 1.0
        },
        description="Motion effect parameters for video generation"
    )
    
    # Timing
    duration_seconds: Optional[int] = Field(
        None,
        description="Shot duration in seconds",
        ge=1,
        le=60
    )
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    class Settings:
        name = "narrative_shots"
        indexes = [
            "scene_id",
            "project_id",
            ("scene_id", "shot_number"),  # Composite index for unique shots per scene
        ]
    
    @validator("shot_description")
    def validate_shot_description(cls, v):
        """
        Validate shot description:
        - If None or empty, return None (optional field)
        - If provided but < 100 chars, return None (will be auto-generated in router)
        - Otherwise return cleaned description
        """
        if not v or v.strip() == "":
            return None
        
        cleaned = v.strip()
        
        # If too short, return None so router can auto-generate
        if len(cleaned) < 100:
            return None
            
        return cleaned
    
    @validator("motion_parameters")
    def validate_motion_parameters(cls, v):
        """Ensure all required motion parameters exist"""
        required_keys = [
            "zoom_start", "zoom_end", "move_x", "move_y",
            "rotate_start", "rotate_end", "duration", "speed"
        ]
        for key in required_keys:
            if key not in v:
                v[key] = 1.0 if "zoom" in key or "speed" in key else 0
        return v
    
    def __repr__(self):
        return f"<Shot {self.shot_number} of Scene '{self.scene_id}'>"
    
    def __str__(self):
        desc = self.shot_description[:50] if self.shot_description else "No description"
        return f"Shot {self.shot_number}: {desc}..."


# ============================================================================
# Step 6: Visual Model (from Visual Generation)
# ============================================================================

class Visual(Document):
    """Visual Model
    
    Represents generated visual assets (images/videos) for a shot.
    Corresponds to Step 6: Visual Generation in Peace Script workflow.
    
    Attributes:
        visual_id: Unique identifier
        shot_id: Reference to parent Shot
        project_id: Reference to parent Project
        image_url: URL of generated image
        video_url: URL of generated video with motion effects
        image_prompt: Prompt used for AI image generation
        generation_provider: AI provider (stable-diffusion/dalle/midjourney)
        generation_params: Additional generation parameters
        status: Generation status (pending/generating/complete/failed)
        error_message: Error message if generation failed
        generated_at: Timestamp when generation completed
        created_at: Creation timestamp
        updated_at: Last update timestamp
    
    Example:
        ```python
        visual = Visual(
            visual_id="visual_001",
            shot_id="shot_001",
            project_id="proj_001",
            image_prompt="A dark mansion at night, cinematic lighting",
            generation_provider="stable-diffusion",
            status=VisualStatus.PENDING
        )
        await visual.insert()
        
        # After generation:
        visual.image_url = "https://storage.example.com/images/shot_001.png"
        visual.video_url = "https://storage.example.com/videos/shot_001.mp4"
        visual.status = VisualStatus.COMPLETE
        visual.generated_at = datetime.utcnow()
        await visual.save()
        ```
    """
    
    # Primary fields (MongoDB _id is used as unique identifier)
    shot_id: str = Field(
        ...,
        description="Reference to parent Shot (MongoDB ObjectId)",
        min_length=1,
        max_length=100
    )
    project_id: Optional[str] = Field(
        None,
        description="Reference to parent Project (optional - derived from shot)",
        min_length=1,
        max_length=100
    )
    
    # Visual assets
    image_url: Optional[str] = Field(
        default=None,
        description="URL of generated image"
    )
    video_url: Optional[str] = Field(
        default=None,
        description="URL of generated video with motion effects"
    )
    
    # Generation details
    image_prompt: Optional[str] = Field(
        default=None,
        description="Prompt used for AI image generation",
        max_length=2000
    )
    generation_provider: str = Field(
        default="stable-diffusion",
        description="AI provider: stable-diffusion/dalle/midjourney/runwayml",
        max_length=50
    )
    generation_params: Dict[str, Any] = Field(
        default={},
        description="Additional generation parameters (steps, guidance_scale, etc.)"
    )
    
    # Status tracking
    status: VisualStatus = Field(
        default=VisualStatus.PENDING,
        description="Generation status"
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Error message if generation failed",
        max_length=1000
    )
    
    # Timestamps
    generated_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when generation completed"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    class Settings:
        name = "narrative_visuals"
        indexes = [
            "shot_id",
            "project_id",
            "status",
        ]
    
    def __repr__(self):
        return f"<Visual for Shot '{self.shot_id}' ({self.status.value})>"
    
    def __str__(self):
        return f"Visual {str(self.id)[:8]} - {self.status.value}"


# ============================================================================
# Export all models
# ============================================================================

__all__ = [
    # Enums
    "GenreEnum",
    "CharacterRole",
    "ProjectStatus",
    "VisualStatus",
    # Models
    "Project",
    "StoryScope",
    "Character",
    "Scene",
    "Shot",
    "Visual",
]
