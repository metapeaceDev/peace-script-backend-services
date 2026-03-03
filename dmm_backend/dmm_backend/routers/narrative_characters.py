"""
NarrativeStructure Character Router

This module implements CRUD operations for screenplay characters.
Characters are essential elements that drive the narrative forward.

Author: Peace Script Team
Date: 25 October 2025
Version: 1.1 - Added AI Character Generation
"""

from fastapi import APIRouter, HTTPException, status, Query, Response
from beanie import PydanticObjectId
from typing import List, Optional, Any
from datetime import datetime
import uuid
import sys
import asyncio
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from documents_narrative import Character, Project, StoryScope, CharacterRole
from documents_actors import ActorProfile, ActorRoleType, ActorImportance, CharacterArcType, BudgetTier
from schemas_narrative import (
    CharacterCreate, CharacterUpdate, CharacterResponse, CharacterGenerateRequest,
    LinkActorRequest, CharacterWithActorResponse, BatchGenerateActorsRequest, BatchGenerateActorsResponse
)
from core.logging_config import get_logger

logger = get_logger(__name__)

# Import AI parser after logger is defined
try:
    from services.ai_character_parser import ai_parser
    HAS_AI_PARSER = True
except ImportError as e:
    logger.warning(f"AI Character Parser not available: {e}")
    HAS_AI_PARSER = False
    ai_parser = None

logger = get_logger(__name__)

router = APIRouter(
    prefix="/api/narrative/characters",
    tags=["narrative-characters"]
)


# =============================================================================
# HELPER FUNCTIONS: Character → Actor Mapping
# =============================================================================

def map_character_role(role: CharacterRole) -> tuple[ActorRoleType, ActorImportance]:
    """
    Map Peace Script CharacterRole to Actor System role & importance
    
    Args:
        role: CharacterRole from Peace Script (protagonist/antagonist/main/support/extra)
        
    Returns:
        Tuple of (ActorRoleType, ActorImportance)
        
    Example:
        >>> role_type, importance = map_character_role(CharacterRole.PROTAGONIST)
        >>> role_type
        ActorRoleType.LEAD
        >>> importance
        ActorImportance.CRITICAL
    """
    mapping = {
        CharacterRole.PROTAGONIST: (ActorRoleType.LEAD, ActorImportance.CRITICAL),
        CharacterRole.ANTAGONIST: (ActorRoleType.LEAD, ActorImportance.CRITICAL),
        CharacterRole.MAIN: (ActorRoleType.SUPPORTING, ActorImportance.HIGH),
        CharacterRole.SUPPORT: (ActorRoleType.SUPPORTING, ActorImportance.MEDIUM),
        CharacterRole.EXTRA: (ActorRoleType.EXTRA, ActorImportance.LOW),
    }
    return mapping.get(role, (ActorRoleType.SUPPORTING, ActorImportance.MEDIUM))


def map_arc_type(arc_type: Optional[str]) -> Optional[CharacterArcType]:
    """
    Map Peace Script arc_type string to Actor System CharacterArcType enum
    
    Args:
        arc_type: Character arc type string from Peace Script
        
    Returns:
        CharacterArcType enum or None
    """
    if not arc_type:
        return None
    
    arc_type_lower = arc_type.lower()
    mapping = {
        "rise": CharacterArcType.POSITIVE,
        "positive": CharacterArcType.POSITIVE,
        "fall": CharacterArcType.NEGATIVE,
        "negative": CharacterArcType.NEGATIVE,
        "flat": CharacterArcType.FLAT,
        "transformation": CharacterArcType.TRANSFORMATION,
        "complex": CharacterArcType.COMPLEX,
    }
    return mapping.get(arc_type_lower, CharacterArcType.FLAT)


def calculate_casting_priority(role: CharacterRole) -> float:
    """
    Calculate casting priority (1-10) based on character role
    
    Args:
        role: CharacterRole
        
    Returns:
        Casting priority (1.0-10.0)
    """
    priority_map = {
        CharacterRole.PROTAGONIST: 10.0,
        CharacterRole.ANTAGONIST: 9.5,
        CharacterRole.MAIN: 7.0,
        CharacterRole.SUPPORT: 4.0,
        CharacterRole.EXTRA: 1.0,
    }
    return priority_map.get(role, 5.0)


def calculate_budget_tier(role: CharacterRole) -> BudgetTier:
    """
    Calculate budget allocation tier based on character role
    
    Args:
        role: CharacterRole
        
    Returns:
        BudgetTier (A/B/C/D)
    """
    tier_map = {
        CharacterRole.PROTAGONIST: BudgetTier.A_TIER,
        CharacterRole.ANTAGONIST: BudgetTier.A_TIER,
        CharacterRole.MAIN: BudgetTier.B_TIER,
        CharacterRole.SUPPORT: BudgetTier.C_TIER,
        CharacterRole.EXTRA: BudgetTier.D_TIER,
    }
    return tier_map.get(role, BudgetTier.C_TIER)


def calculate_plot_impact(role: CharacterRole) -> float:
    """
    Calculate plot impact weight (0-10) based on character role
    
    Args:
        role: CharacterRole
        
    Returns:
        Plot impact weight (0.0-10.0)
    """
    impact_map = {
        CharacterRole.PROTAGONIST: 10.0,
        CharacterRole.ANTAGONIST: 9.0,
        CharacterRole.MAIN: 6.0,
        CharacterRole.SUPPORT: 3.0,
        CharacterRole.EXTRA: 0.5,
    }
    return impact_map.get(role, 5.0)


def get_narrative_functions(role: CharacterRole) -> List[str]:
    """
    Get narrative functions based on character role
    
    Args:
        role: CharacterRole
        
    Returns:
        List of narrative function strings
    """
    function_map = {
        CharacterRole.PROTAGONIST: ["hero", "protagonist", "main_driver"],
        CharacterRole.ANTAGONIST: ["villain", "antagonist", "obstacle"],
        CharacterRole.MAIN: ["supporter", "ally", "key_character"],
        CharacterRole.SUPPORT: ["helper", "background_character"],
        CharacterRole.EXTRA: ["crowd", "background"],
    }
    return function_map.get(role, ["supporting"])


async def create_actor_from_character(character: Character) -> ActorProfile:
    """
    Create comprehensive ActorProfile from Peace Script Character using AI
    
    This function transforms a simple 12-field Character into a full 100+ field
    ActorProfile by using AI to parse Thai text descriptions into structured data.
    
    Args:
        character: Character document from Peace Script
        
    Returns:
        ActorProfile document (already inserted into database)
        
    Process:
        1. Generate unique actor_id
        2. Parse personality text → InternalCharacter (40+ fields)
        3. Parse appearance text → ExternalCharacter (35+ fields)
        4. Map role → ActorRoleType + ActorImportance
        5. Calculate casting priority, budget tier, plot impact
        6. Create and insert ActorProfile
        
    Example:
        >>> character = await Character.find_one({"name": "รินรดา"})
        >>> actor = await create_actor_from_character(character)
        >>> actor.internal_character.conscientiousness
        8.5  # Parsed from "มุ่งมั่น" in personality
    """
    logger.info(f"Creating Actor from Character: {character.name}")
    
    # 1. Generate unique actor_id
    actor_id = f"ACT-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    
    # 2. Parse personality with AI (if available)
    internal_character = None
    if ai_parser and character.personality and len(character.personality) >= 10:
        try:
            logger.info(f"Parsing personality for {character.name}")
            internal_character = await ai_parser.parse_personality_to_internal(
                personality_text=character.personality,
                motivation_text=character.motivation,
                conflict_text=character.conflict
            )
            logger.info(f"Successfully parsed InternalCharacter for {character.name}")
        except Exception as e:
            logger.error(f"Failed to parse personality: {e}")
            # Will use None, ActorProfile handles defaults
    
    # 3. Parse appearance with AI (if available)
    external_character = None
    if ai_parser and character.appearance and len(character.appearance) >= 10:
        try:
            logger.info(f"Parsing appearance for {character.name}")
            external_character = await ai_parser.parse_appearance_to_external(
                appearance_text=character.appearance,
                gender=character.gender,
                age=character.age
            )
            logger.info(f"Successfully parsed ExternalCharacter for {character.name}")
        except Exception as e:
            logger.error(f"Failed to parse appearance: {e}")
            # Will use None, ActorProfile handles defaults
    
    # 4. Map role to Actor system
    role_type, importance = map_character_role(character.role)
    arc_type = map_arc_type(character.arc_type)
    
    # 5. Calculate metrics
    casting_priority = calculate_casting_priority(character.role)
    budget_tier = calculate_budget_tier(character.role)
    plot_impact = calculate_plot_impact(character.role)
    narrative_functions = get_narrative_functions(character.role)
    
    # 6. Create ActorProfile
    # 🎨 Generate placeholder avatar URL based on name (128px for cards)
    name_encoded = character.name.replace(" ", "+")
    placeholder_avatar = f"https://ui-avatars.com/api/?name={name_encoded}&size=128&background=random&color=fff&bold=true"
    
    actor = ActorProfile(
        actor_id=actor_id,
        model_id="peace-mind-001",  # Default Digital Mind Model
        actor_name=character.name,
        
        # Role & Classification
        role_type=role_type,
        importance=importance,
        character_arc_type=arc_type or CharacterArcType.FLAT,
        arc_description=character.arc_type,  # Store original arc_type text
        narrative_functions=narrative_functions,
        
        # Character Data (parsed by AI)
        internal_character=internal_character,
        external_character=external_character,
        
        # Bio & Visuals
        character_bio=character.background,
        character_summary=f"{character.name} - {character.role.value}",
        avatar_thumbnail_url=placeholder_avatar,  # 🎨 Placeholder avatar with character name
        avatar_data=None,  # Will be set later via Avatar Designer
        
        # Project Association
        project_id=character.project_id,
        project_name=None,  # Will be fetched if needed
        
        # Social/Goals/Aspirations (will be enhanced later)
        social_status=None,
        character_goals=None,
        aspirations=None,
        
        # Production Metrics
        casting_priority=int(casting_priority),
        budget_allocation_tier=budget_tier,
        plot_impact_weight=plot_impact,
        
        # Additional
        notes=f"Auto-generated from Peace Script Character '{character.name}'",
        tags=[character.role.value, "peace-script"],
        
        # Timestamps
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Insert into database
    await actor.insert()
    logger.info(f"Created ActorProfile {actor_id} for Character {character.name}")
    
    return actor


# =============================================================================
# CREATE
# =============================================================================

@router.post("/", response_model=CharacterWithActorResponse, status_code=status.HTTP_201_CREATED)
async def create_character(character_data: CharacterCreate):
    """
    สร้างตัวละครใหม่ (Create new character)
    
    **NEW**: Auto-generate comprehensive Actor Profile using AI (default: ON)
    
    Process:
    1. Create Character (12 fields from Peace Script)
    2. If auto_create_actor=True (default):
       - Parse personality text → InternalCharacter (40+ fields)
       - Parse appearance text → ExternalCharacter (35+ fields)
       - Generate comprehensive ActorProfile (100+ fields)
       - Link Character ↔ Actor via actor_id
    
    **Parameters:**
    - **project_id**: Project ID (required)
    - **name**: Character name (required)
    - **role**: Character role (protagonist/antagonist/main/support/extra)
    - **personality**: Personality description in Thai (for AI parsing)
    - **appearance**: Appearance description in Thai (for AI parsing)
    - **auto_create_actor**: Auto-generate Actor Profile (default: True)
    
    **Returns:**
    - Character data + embedded Actor data (if auto-created)
    """
    logger.info(f"Creating character: {character_data.name} (auto_create_actor={character_data.auto_create_actor})")
    
    # Verify project exists
    project = await Project.find_one({"project_id": character_data.project_id})
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{character_data.project_id}' not found"
        )
    
    # Check if character with same name already exists in project
    existing = await Character.find_one({
        "project_id": character_data.project_id,
        "name": character_data.name
    })
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Character '{character_data.name}' already exists in project '{character_data.project_id}'"
        )
    
    # Extract auto_create_actor flag (not stored in Character)
    auto_create_actor = character_data.auto_create_actor
    
    # ✨ NEW: Handle Character Goals migration (Peace Script v2)
    # Convert old fields → goals structure if goals not provided
    data_dict = character_data.model_dump(exclude={"auto_create_actor"})
    
    if not data_dict.get("goals") and any([
        data_dict.get("background"),
        data_dict.get("motivation"),
        data_dict.get("conflict")
    ]):
        # Build goals from old fields
        logger.info(f"Migrating old fields → goals structure for: {character_data.name}")
        data_dict["goals"] = {
            "objective": data_dict.get("motivation") or "ยังไม่ระบุเป้าหมาย",
            "need": "ความต้องการภายในยังไม่ระบุ",  # Inferred later
            "action": "การกระทำยังไม่ระบุ",  # Inferred later
            "conflict": data_dict.get("conflict") or "ยังไม่ระบุอุปสรรค",
            "backstory": data_dict.get("background") or "ยังไม่มีประวัติ"
        }
    
    # Convert CharacterGoals object → dict if needed
    if data_dict.get("goals") and not isinstance(data_dict["goals"], dict):
        data_dict["goals"] = data_dict["goals"].model_dump()
    
    # Create new character
    character = Character(
        **data_dict,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    await character.insert()
    logger.info(f"Character created: {character.name} (id={character.id})")
    
    # ✨ NEW: Auto-create Actor Profile if requested
    actor = None
    if auto_create_actor:
        try:
            logger.info(f"Auto-creating Actor for Character: {character.name}")
            actor = await create_actor_from_character(character)
            
            # Link Character → Actor
            character.actor_id = actor.actor_id
            await character.save()
            logger.info(f"Linked Character {character.name} → Actor {actor.actor_id}")
            
        except Exception as e:
            logger.error(f"Failed to auto-create Actor: {e}")
            # Continue without Actor (non-blocking error)
            # Character still created successfully
    
    # ✨ AUTO-INCREMENT: Update project characters_count
    try:
        characters_count = await Character.find({"project_id": character_data.project_id}).count()
        project.characters_count = characters_count
        project.updated_at = datetime.utcnow()
        await project.save()
    except Exception as e:
        logger.warning(f"Failed to update characters_count: {e}")
    
    # Build response with embedded actor (if exists)
    response = CharacterWithActorResponse(
        id=str(character.id),
        **character.model_dump(exclude={"id"}),
        actor=actor.model_dump(mode='json') if actor else None
    )
    
    return response


# =============================================================================
# READ
# =============================================================================

@router.get("/", response_model=List[CharacterResponse])
async def list_characters(
    project_id: str = Query(..., description="รหัสโปรเจ็ค (required)"),
    skip: int = Query(0, ge=0, description="จำนวนรายการที่จะข้าม"),
    limit: int = Query(100, ge=1, le=500, description="จำนวนรายการสูงสุด"),
    role: Optional[str] = Query(None, description="กรองตามบทบาท"),
    gender: Optional[str] = Query(None, description="กรองตามเพศ"),
    age_min: Optional[int] = Query(None, ge=0, description="อายุขั้นต่ำ"),
    age_max: Optional[int] = Query(None, le=120, description="อายุสูงสุด")
):
    """
    แสดงรายการตัวละครทั้งหมดของโปรเจ็ค
    
    รองรับการกรอง:
    - **project_id**: รหัสโปรเจ็ค (required)
    - **role**: บทบาท (protagonist, antagonist, supporting, etc.)
    - **gender**: เพศ
    - **age_min**: อายุขั้นต่ำ
    - **age_max**: อายุสูงสุด
    """
    query: dict[str, Any] = {"project_id": project_id}
    
    if role:
        query["role"] = role
    
    if gender:
        query["gender"] = gender
    
    if age_min is not None or age_max is not None:
        age_query = {}
        if age_min is not None:
            age_query["$gte"] = age_min
        if age_max is not None:
            age_query["$lte"] = age_max
        if age_query:
            query["age"] = age_query
    
    characters = await Character.find(query).skip(skip).limit(limit).to_list()
    
    return [
        CharacterResponse(
            id=str(c.id),
            **c.model_dump(exclude={"id"})
        )
        for c in characters
    ]


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "narrative-characters",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(character_id: str):
    """
    ดึงข้อมูลตัวละครตาม MongoDB _id
    
    - **character_id**: MongoDB ObjectId ของตัวละคร
    """
    try:
        character = await Character.get(character_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character '{character_id}' not found"
        )
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character '{character_id}' not found"
        )
    
    return CharacterResponse(
        id=str(character.id),
        **character.model_dump(exclude={"id"})
    )


# =============================================================================
# UPDATE
# =============================================================================

@router.put("/{character_id}", response_model=CharacterResponse)
async def update_character(
    character_id: str,
    character_data: CharacterUpdate
):
    """
    อัปเดตข้อมูลตัวละคร
    
    - **character_id**: MongoDB ObjectId ของตัวละคร
    - อัปเดตเฉพาะฟิลด์ที่ส่งมาเท่านั้น
    """
    try:
        character = await Character.get(character_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character '{character_id}' not found"
        )
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character '{character_id}' not found"
        )
    
    # Update only provided fields
    update_data = character_data.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    update_data["updated_at"] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(character, field, value)
    
    await character.save()
    
    return CharacterResponse(
        id=str(character.id),
        **character.model_dump(exclude={"id"})
    )


# =============================================================================
# DELETE
# =============================================================================

@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character(character_id: str):
    """
    ลบตัวละคร
    
    - **character_id**: MongoDB ObjectId ของตัวละคร
    - ⚠️ คำเตือน: จะลบข้อมูลตัวละครทั้งหมด
    """
    try:
        character = await Character.get(character_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character '{character_id}' not found"
        )
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character '{character_id}' not found"
        )
    
    # Store project_id before deletion
    project_id = character.project_id
    
    await character.delete()
    
    # ✨ AUTO-DECREMENT: Update project characters_count
    try:
        project = await Project.find_one({"project_id": project_id})
        if project:
            characters_count = await Character.find({"project_id": project_id}).count()
            project.characters_count = characters_count
            project.updated_at = datetime.utcnow()
            await project.save()
    except Exception as e:
        print(f"Warning: Failed to update characters_count after deletion: {e}")
    
    return None


# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================

@router.get("/by-project/{project_id}/summary")
async def get_characters_summary(project_id: str):
    """
    สรุปข้อมูลตัวละครของโปรเจ็ค
    
    Returns:
    - จำนวนตัวละครแยกตามบทบาท
    - จำนวนตัวละครแยกตามเพศ
    - อายุเฉลี่ย
    """
    characters = await Character.find({"project_id": project_id}).to_list()
    
    if not characters:
        return {
            "project_id": project_id,
            "total_characters": 0,
            "by_role": {},
            "by_gender": {},
            "average_age": 0
        }
    
    # Count by role
    by_role = {}
    for char in characters:
        role = char.role
        by_role[role] = by_role.get(role, 0) + 1
    
    # Count by gender
    by_gender = {}
    for char in characters:
        gender = char.gender
        by_gender[gender] = by_gender.get(gender, 0) + 1
    
    # Calculate average age
    total_age = sum(char.age for char in characters if char.age is not None)
    average_age = round(total_age / len(characters), 1) if characters else 0
    
    return {
        "project_id": project_id,
        "total_characters": len(characters),
        "by_role": by_role,
        "by_gender": by_gender,
        "average_age": average_age
    }


# =============================================================================
# AI GENERATION ENDPOINT
# =============================================================================

@router.options("/generate-from-scope")
async def options_generate_from_scope(response: Response):
    """Handle CORS preflight request"""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return {"status": "ok"}

@router.post("/generate-from-scope", response_model=List[CharacterResponse])
async def generate_characters_from_scope(
    request: CharacterGenerateRequest,
    response: Response  # 🔥 ADD: Response object for CORS headers
):
    """
    🤖 สร้างตัวละครอัตโนมัติจาก StoryScope (Step 1-2)
    """
    try:
        # 🔥 FIX: Add CORS headers explicitly
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        
        # 1. Verify project exists
        project = await Project.find_one({"project_id": request.project_id})
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project '{request.project_id}' not found"
            )
        
        # 2. Get StoryScope data
        scope = await StoryScope.find_one({"project_id": request.project_id})
        if not scope:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"StoryScope not found for project '{request.project_id}'. Please complete Step 1-2 first."
            )
        
        # 3. Generate characters based on scope data with count
        from routers.ai_generation import generate_characters_from_scope as ai_gen_characters
        
        character_count = request.character_count or 5
        logger.info(f"🤖 Generating {character_count} characters for project '{request.project_id}'")
        
        # 🗑️ Delete existing characters for this project first (clean slate)
        await Character.find({"project_id": request.project_id}).delete()
        logger.info(f"🗑️ Deleted existing characters from project '{request.project_id}'")
        
        generated_data = await ai_gen_characters(scope, project, character_count)
        
        # 4. Create Character and ActorProfile records
        created_characters = []
        actor_generation_tasks = []
        
        for char_data in generated_data:
            try:
                # 🔍 Check if character with same name already exists
                existing = await Character.find_one({
                    "project_id": request.project_id,
                    "name": char_data["name"]
                })
                
                if existing:
                    logger.warning(f"⚠️ Character '{char_data['name']}' already exists, skipping")
                    created_characters.append(existing)
                    continue
                
                # 🔧 FIX: Validate and ensure ALL goals fields meet minimum length requirements
                goals_data = char_data.get("goals", {})
                if goals_data and isinstance(goals_data, dict):
                    field_requirements = {
                        "objective": { "min_length": 150, "padding": " เพื่อให้บรรลุเป้าหมายสูงสุดในชีวิตและพิสูจน์ความสามารถของตนเองให้เป็นที่ยอมรับ ท่ามกลางความท้าทายที่ต้องเผชิญ" },
                        "need": { "min_length": 150, "padding": " และต้องการการยอมรับจากผู้อื่นอย่างแท้จริง รวมถึงความเข้าใจในตัวตนที่แท้จริงของตนเอง เพื่อเติมเต็มสิ่งที่ขาดหายไปในจิตใจ" },
                        "action": { "min_length": 150, "padding": " โดยพยายามอย่างเต็มที่ทุกวันเพื่อก้าวข้ามขีดจำกัดของตนเอง และเรียนรู้จากความผิดพลาดในอดีตเพื่อสร้างอนาคตที่ดีกว่าเดิม" },
                        "conflict": { "min_length": 150, "padding": " และต้องเผชิญกับอุปสรรคมากมายที่เข้ามาทดสอบจิตใจอย่างต่อเนื่อง ทั้งจากปัจจัยภายนอกและความขัดแย้งภายในใจที่ยากจะก้าวผ่าน" },
                        "backstory": { "min_length": 300, "padding": " - มีประสบการณ์ชีวิตที่หลากหลายและเติบโตมาในสภาพแวดล้อมที่มีอิทธิพลต่อบุคลิกภาพ ซึ่งหล่อหลอมให้กลายเป็นคนที่มีมุมมองต่อโลกในแบบที่เป็นอยู่ และเป็นแรงผลักดันสำคัญในการดำเนินชีวิตเพื่อตามหาความหมายที่แท้จริง" }
                    }
                    
                    for field_name, requirements in field_requirements.items():
                        field_value = goals_data.get(field_name, "")
                        min_len = requirements["min_length"]
                        
                        if len(field_value) < min_len:
                            padding_text = requirements["padding"]
                            padded_value = field_value
                            while len(padded_value) < min_len:
                                padded_value += padding_text
                            goals_data[field_name] = padded_value

                # 🔧 FIX: Validate Personality and Appearance length
                personality = char_data.get("personality", "")
                if len(personality) < 10:
                    personality += " เป็นคนที่มีความมุ่งมั่นและตั้งใจจริงในการทำทุกสิ่ง"
                
                appearance = char_data.get("appearance", "")
                if appearance and len(appearance) < 10:
                    appearance += " รูปร่างสมส่วน แต่งกายดูดีมีสไตล์"

                # Create Character with auto-generated Actor Profile
                character = Character(
                    project_id=request.project_id,
                    actor_id=None,
                    name=char_data["name"],
                    role=char_data["role"],
                    age=char_data.get("age"),
                    gender=char_data.get("gender"),
                    personality=personality,
                    appearance=appearance,
                    goals=goals_data if goals_data else None,
                    # Legacy fields
                    background=char_data.get("background"),
                    arc_type=char_data.get("arc_name"),
                    motivation=char_data.get("motivation"),
                    conflict=char_data.get("conflict")
                )
                await character.insert()
                logger.info(f"✅ Created character: {character.name}")
                
                # 🎭 Prepare async task for Actor Profile creation
                async def generate_actor_task(char_obj):
                    try:
                        logger.info(f"🎭 Auto-creating Actor Profile for: {char_obj.name}")
                        actor = await create_actor_from_character(char_obj)
                        char_obj.actor_id = actor.actor_id
                        await char_obj.save()
                        logger.info(f"✅ Linked Character '{char_obj.name}' → Actor '{actor.actor_id}'")
                    except Exception as e:
                        logger.error(f"⚠️ Failed to auto-create Actor for '{char_obj.name}': {e}")
                
                actor_generation_tasks.append(generate_actor_task(character))
                created_characters.append(character)
                
            except Exception as e:
                logger.error(f"❌ Failed to create character '{char_data.get('name', 'Unknown')}': {e}")
                # Continue to next character instead of failing entire request

        # 🚀 Execute all actor generation tasks in parallel
        if actor_generation_tasks:
            logger.info(f"🚀 Starting parallel generation of {len(actor_generation_tasks)} actors...")
            await asyncio.gather(*actor_generation_tasks)
            logger.info("✅ Parallel actor generation complete")
        
        # Convert to response model
        response_list = [
            CharacterResponse(
                id=str(c.id),
                **c.model_dump(exclude={"id"})
            )
            for c in created_characters
        ]
        
        return response_list

    except Exception as e:
        logger.error(f"🔥 CRITICAL ERROR in generate_characters_from_scope: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(e)}"
        )


# =============================================================================
# CHARACTER ↔ ACTOR INTEGRATION ENDPOINTS
# =============================================================================

@router.post("/{character_id}/generate-actor", response_model=CharacterWithActorResponse)
async def generate_actor_for_character(character_id: str):
    """
    🎭 สร้าง Actor Profile จาก Character ที่มีอยู่
    
    Manually trigger Actor generation for an existing Character.
    Useful when Character was created with auto_create_actor=False.
    
    Args:
        character_id: Character ID to generate Actor for
    
    Returns:
        CharacterWithActorResponse with embedded actor data
    
    Raises:
        404: Character not found
        409: Actor already linked to this Character
    
    Example:
        POST /api/narrative/characters/char_123/generate-actor
        → Creates ActorProfile from character data
        → Links character.actor_id → actor.actor_id
        → Returns Character with embedded actor
    """
    try:
        character = await Character.get(PydanticObjectId(character_id))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character '{character_id}' not found"
        )
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character '{character_id}' not found"
        )
    
    # Check if Actor already linked
    if character.actor_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Actor '{character.actor_id}' already linked to this Character. Use sync-to-actor to update."
        )
    
    # Generate Actor from Character
    logger.info(f"Generating Actor for Character '{character.name}' ({character_id})")
    
    try:
        actor = await create_actor_from_character(character)
        
        # Link Character → Actor
        character.actor_id = actor.actor_id
        await character.save()
        
        logger.info(f"✅ Actor '{actor.actor_id}' generated and linked to Character '{character_id}'")
        
        return CharacterWithActorResponse(
            id=str(character.id),
            **character.model_dump(exclude={"id"}),
            actor=actor.model_dump(mode='json') if actor else None
        )
    except Exception as e:
        logger.error(f"Failed to generate Actor for Character '{character_id}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate Actor: {str(e)}"
        )


@router.post("/{character_id}/link-actor", response_model=CharacterResponse)
async def link_existing_actor(character_id: str, request: LinkActorRequest):
    """
    🔗 เชื่อมโยง Actor ที่มีอยู่แล้วกับ Character
    
    Link an existing ActorProfile to a Character.
    Useful for manually connecting Peace Script Characters to Digital Actors.
    
    Args:
        character_id: Character ID
        request: LinkActorRequest containing actor_id
    
    Returns:
        Updated CharacterResponse
    
    Raises:
        404: Character or Actor not found
        409: Character already linked to another Actor
    
    Example:
        POST /api/narrative/characters/char_123/link-actor
        {
            "actor_id": "ACT-20241110-A1B2C3"
        }
    """
    # Verify Character exists
    try:
        character = await Character.get(PydanticObjectId(character_id))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character '{character_id}' not found"
        )
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character '{character_id}' not found"
        )
    
    # Check if already linked
    if character.actor_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Character already linked to Actor '{character.actor_id}'. Unlink first."
        )
    
    # Verify Actor exists
    actor = await ActorProfile.find_one({"actor_id": request.actor_id})
    if not actor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Actor '{request.actor_id}' not found"
        )
    
    # Link Character → Actor
    character.actor_id = request.actor_id
    await character.save()
    
    logger.info(f"✅ Linked Character '{character.name}' → Actor '{request.actor_id}'")
    
    return CharacterResponse(
        id=str(character.id),
        **character.model_dump(exclude={"id"})
    )


@router.delete("/{character_id}/link-actor", response_model=CharacterResponse)
async def unlink_actor(character_id: str):
    """
    🔓 ยกเลิกการเชื่อมโยง Actor จาก Character
    
    Unlink Actor from Character.
    Does NOT delete the ActorProfile, only removes the link.
    
    Args:
        character_id: Character ID
    
    Returns:
        Updated CharacterResponse with actor_id=None
    
    Raises:
        404: Character not found
        409: No Actor linked to this Character
    
    Example:
        DELETE /api/narrative/characters/char_123/link-actor
        → Sets character.actor_id = None
    """
    try:
        character = await Character.get(PydanticObjectId(character_id))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character '{character_id}' not found"
        )
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character '{character_id}' not found"
        )
    
    # Check if Actor is linked
    if not character.actor_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No Actor linked to this Character"
        )
    
    # Store actor_id for logging
    old_actor_id = character.actor_id
    
    # Unlink
    character.actor_id = None
    await character.save()
    
    logger.info(f"✅ Unlinked Actor '{old_actor_id}' from Character '{character.name}'")
    
    return CharacterResponse(
        id=str(character.id),
        **character.model_dump(exclude={"id"})
    )


@router.post("/{character_id}/sync-to-actor", response_model=CharacterWithActorResponse)
async def sync_character_to_actor(character_id: str):
    """
    🔄 ซิงค์ข้อมูล Character ไปยัง Actor ที่เชื่อมโยงอยู่
    
    Re-sync Character data to linked ActorProfile.
    Useful when Character data has been updated and needs to be reflected in Actor.
    
    Process:
    1. Get Character and linked Actor
    2. Re-parse personality → InternalCharacter
    3. Re-parse appearance → ExternalCharacter
    4. Update Actor fields from Character
    5. Save updated Actor
    
    Args:
        character_id: Character ID
    
    Returns:
        CharacterWithActorResponse with updated embedded actor data
    
    Raises:
        404: Character not found or no Actor linked
        500: Sync failed
    
    Example:
        POST /api/narrative/characters/char_123/sync-to-actor
        → Re-parses character.personality/appearance with AI
        → Updates linked ActorProfile
    """
    try:
        character = await Character.get(PydanticObjectId(character_id))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character '{character_id}' not found"
        )
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character '{character_id}' not found"
        )
    
    # Check if Actor is linked
    if not character.actor_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Actor linked to this Character. Use generate-actor first."
        )
    
    # Get linked Actor
    actor = await ActorProfile.find_one({"actor_id": character.actor_id})
    if not actor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Linked Actor '{character.actor_id}' not found in database"
        )
    
    logger.info(f"Syncing Character '{character.name}' → Actor '{character.actor_id}'")
    
    try:
        # Re-parse personality
        internal_character = None
        if ai_parser and character.personality and len(character.personality.strip()) >= 10:
            try:
                internal_character = await ai_parser.parse_personality_to_internal(
                    personality_text=character.personality,
                    motivation_text=character.motivation or None,
                    conflict_text=character.conflict or None
                )
                logger.info(f"✅ Re-parsed personality for '{character.name}'")
            except Exception as e:
                logger.warning(f"Failed to re-parse personality: {e}")
        
        # Re-parse appearance
        external_character = None
        if ai_parser and character.appearance and len(character.appearance.strip()) >= 10:
            try:
                external_character = await ai_parser.parse_appearance_to_external(
                    appearance_text=character.appearance,
                    gender=character.gender or None,
                    age=character.age or None
                )
                logger.info(f"✅ Re-parsed appearance for '{character.name}'")
            except Exception as e:
                logger.warning(f"Failed to re-parse appearance: {e}")
        
        # Update Actor fields
        actor.actor_name = character.name
        actor.character_bio = character.background or actor.character_bio
        
        if internal_character:
            actor.internal_character = internal_character
        if external_character:
            actor.external_character = external_character
        
        # Update role mapping
        role_type, importance = map_character_role(character.role)
        actor.role_type = role_type
        actor.importance = importance
        
        # Update arc type
        if character.arc_type:
            arc_type_enum = map_arc_type(character.arc_type)
            if arc_type_enum:
                actor.character_arc_type = arc_type_enum
        
        # Update metrics
        actor.casting_priority = int(calculate_casting_priority(character.role))
        actor.budget_allocation_tier = calculate_budget_tier(character.role)
        actor.plot_impact_weight = calculate_plot_impact(character.role)
        actor.narrative_functions = get_narrative_functions(character.role)
        
        # Update metadata
        actor.notes = f"Synced from Character '{character.name}' at {datetime.utcnow().isoformat()}"
        
        # Save updated Actor
        await actor.save()
        
        logger.info(f"✅ Synced Character '{character_id}' → Actor '{character.actor_id}'")
        
        return CharacterWithActorResponse(
            id=str(character.id),
            **character.model_dump(exclude={"id"}),
            actor=actor.model_dump(mode='json') if actor else None
        )
        
    except Exception as e:
        logger.error(f"Failed to sync Character → Actor: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync: {str(e)}"
        )


@router.get("/{character_id}/actor", response_model=dict)
async def get_linked_actor(character_id: str):
    """
    🎭 ดึงข้อมูล Actor ที่เชื่อมโยงกับ Character
    
    Get full ActorProfile data for a Character's linked Actor.
    
    Args:
        character_id: Character ID
    
    Returns:
        Full ActorProfile data (100+ fields)
    
    Raises:
        404: Character not found or no Actor linked
    
    Example:
        GET /api/narrative/characters/char_123/actor
        → Returns full ActorProfile with internal/external character data
    """
    try:
        character = await Character.get(PydanticObjectId(character_id))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character '{character_id}' not found"
        )
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character '{character_id}' not found"
        )
    
    # Check if Actor is linked
    if not character.actor_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Actor linked to this Character"
        )
    
    # Get linked Actor
    actor = await ActorProfile.find_one({"actor_id": character.actor_id})
    if not actor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Linked Actor '{character.actor_id}' not found in database"
        )
    
    return actor.model_dump(mode='json')


@router.post("/projects/{project_id}/generate-actors", response_model=BatchGenerateActorsResponse)
async def batch_generate_actors(project_id: str, request: BatchGenerateActorsRequest):
    """
    🎬 สร้าง Actor Profiles แบบเป็นกลุ่มสำหรับโปรเจ็ค
    
    Batch generate ActorProfiles for multiple Characters in a project.
    Useful for generating all actors at once after creating characters.
    
    Process:
    1. Validate project exists
    2. Get all specified Characters
    3. For each Character without actor_id:
       - Call create_actor_from_character()
       - Link character.actor_id → actor.actor_id
    4. Track results (created, skipped, errors)
    
    Args:
        project_id: Project ID
        request: BatchGenerateActorsRequest with character_ids list (1-50)
    
    Returns:
        BatchGenerateActorsResponse with summary
    
    Raises:
        404: Project not found
        422: Invalid character_ids (must be 1-50 items)
    
    Example:
        POST /api/narrative/characters/projects/proj_001/generate-actors
        {
            "character_ids": ["char_1", "char_2", "char_3"]
        }
        
        Response:
        {
            "total": 3,
            "created": 2,
            "skipped": 1,
            "errors": [],
            "created_actor_ids": ["ACT-...", "ACT-..."],
            "skipped_character_ids": ["char_1"]  // Already had actor
        }
    """
    # Validate project exists
    project = await Project.find_one({"project_id": project_id})
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found"
        )
    
    logger.info(f"Batch generating Actors for project '{project_id}' ({len(request.character_ids)} characters)")
    
    created_actor_ids = []
    skipped_character_ids = []
    errors = []
    
    for character_id in request.character_ids:
        try:
            # Get Character
            try:
                character = await Character.get(PydanticObjectId(character_id))
            except Exception:
                errors.append(f"Character '{character_id}' not found")
                continue
            
            if not character:
                errors.append(f"Character '{character_id}' not found")
                continue
            
            # Verify Character belongs to this project
            if character.project_id != project_id:
                errors.append(f"Character '{character_id}' does not belong to project '{project_id}'")
                continue
            
            # Skip if Actor already linked
            if character.actor_id:
                logger.info(f"⏭️ Skipping Character '{character.name}' - already linked to Actor '{character.actor_id}'")
                skipped_character_ids.append(character_id)
                continue
            
            # Generate Actor
            logger.info(f"Generating Actor for Character '{character.name}' ({character_id})")
            actor = await create_actor_from_character(character)
            
            # Link Character → Actor
            character.actor_id = actor.actor_id
            await character.save()
            
            created_actor_ids.append(actor.actor_id)
            logger.info(f"✅ Created Actor '{actor.actor_id}' for Character '{character.name}'")
            
        except Exception as e:
            error_msg = f"Failed to generate Actor for '{character_id}': {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
    
    # Summary
    total = len(request.character_ids)
    created = len(created_actor_ids)
    skipped = len(skipped_character_ids)
    
    logger.info(f"✅ Batch generation complete: {created} created, {skipped} skipped, {len(errors)} errors")
    
    return BatchGenerateActorsResponse(
        total=total,
        created=created,
        skipped=skipped,
        errors=errors,
        created_actor_ids=created_actor_ids,
        skipped_character_ids=skipped_character_ids
    )
