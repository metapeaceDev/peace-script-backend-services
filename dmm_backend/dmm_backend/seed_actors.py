"""
Seed data for Actor Classification System
Create sample actor profiles for testing
"""

from documents_actors import (
    ActorProfile,
    ActorRoleType,
    ActorImportance,
    CharacterArcType,
    BudgetTier,
    ActorRelationship
)


# Sample Actor Profiles for "เงาแค้น" (Shadow of Vengeance) Project

SAMPLE_ACTORS = [
    # Lead Actor 1 - Protagonist
    {
        "model_id": "peace-mind-001",
        "actor_name": "รินรดา (นางเอก)",
        "role_type": ActorRoleType.LEAD,
        "importance": ActorImportance.CRITICAL,
        "narrative_functions": ["protagonist", "emotional_anchor", "hero"],
        "character_arc_type": CharacterArcType.TRANSFORMATION,
        "arc_description": "จากผู้หญิงที่เต็มไปด้วยความแค้น กลายเป็นผู้ให้อภัย",
        "estimated_screen_time": 85.5,
        "scene_appearances": 42,
        "dialogue_lines_count": 156,
        "plot_impact_weight": 9.5,
        "emotional_arc_trajectory": [3.0, 2.5, 4.0, 6.0, 7.5, 8.5, 9.0],
        "key_scenes": ["SCN001", "SCN015", "SCN028", "SCN045"],
        "relationships": [
            ActorRelationship(
                actor_id="ACT-002",
                relationship_type="rival",
                importance=9.0,
                description="คู่อริหลักของเรื่อง",
                is_primary=True
            ),
            ActorRelationship(
                actor_id="ACT-003",
                relationship_type="family",
                importance=8.5,
                description="พี่ชายที่เสียชีวิต",
                is_primary=True
            )
        ],
        "casting_priority": 10,
        "budget_allocation_tier": BudgetTier.A_TIER,
        "project_id": "PROJ-001",
        "project_name": "เงาแค้น",
        "tags": ["lead", "female", "protagonist", "hero"]
    },
    
    # Lead Actor 2 - Antagonist
    {
        "model_id": "peace-mind-002",
        "actor_name": "วิชัย (ผู้ร้าย)",
        "role_type": ActorRoleType.LEAD,
        "importance": ActorImportance.CRITICAL,
        "narrative_functions": ["antagonist", "obstacle", "villain"],
        "character_arc_type": CharacterArcType.NEGATIVE,
        "arc_description": "ตกต่ำจากอำนาจสู่ความพินาศ",
        "estimated_screen_time": 72.0,
        "scene_appearances": 38,
        "dialogue_lines_count": 128,
        "plot_impact_weight": 9.0,
        "emotional_arc_trajectory": [8.0, 8.5, 7.0, 5.5, 4.0, 2.0, 1.0],
        "key_scenes": ["SCN008", "SCN022", "SCN035", "SCN048"],
        "relationships": [
            ActorRelationship(
                actor_id="ACT-001",
                relationship_type="rival",
                importance=9.0,
                description="คู่ปรปักษ์หลัก",
                is_primary=True
            )
        ],
        "casting_priority": 10,
        "budget_allocation_tier": BudgetTier.A_TIER,
        "project_id": "PROJ-001",
        "project_name": "เงาแค้น",
        "tags": ["lead", "male", "antagonist", "villain"]
    },
    
    # Supporting Actor 1
    {
        "model_id": "peace-mind-003",
        "actor_name": "พี่ชายของรินรดา",
        "role_type": ActorRoleType.SUPPORTING,
        "importance": ActorImportance.HIGH,
        "narrative_functions": ["mentor", "emotional_support", "catalyst"],
        "character_arc_type": CharacterArcType.FLAT,
        "arc_description": "ปรากฏในฉากย้อนหลังและความทรงจำ",
        "estimated_screen_time": 28.5,
        "scene_appearances": 15,
        "dialogue_lines_count": 45,
        "plot_impact_weight": 7.5,
        "emotional_arc_trajectory": [7.0, 6.5, 0.0],
        "key_scenes": ["SCN003", "SCN009", "SCN025"],
        "relationships": [
            ActorRelationship(
                actor_id="ACT-001",
                relationship_type="family",
                importance=8.5,
                description="น้องสาว",
                is_primary=True
            )
        ],
        "casting_priority": 8,
        "budget_allocation_tier": BudgetTier.B_TIER,
        "project_id": "PROJ-001",
        "project_name": "เงาแค้น",
        "tags": ["supporting", "male", "family", "deceased"]
    },
    
    # Supporting Actor 2
    {
        "model_id": "peace-mind-004",
        "actor_name": "เพื่อนสนิท",
        "role_type": ActorRoleType.SUPPORTING,
        "importance": ActorImportance.HIGH,
        "narrative_functions": ["sidekick", "comic_relief", "support"],
        "character_arc_type": CharacterArcType.POSITIVE,
        "arc_description": "เติบโตจากผู้ช่วยเหลือกลายเป็นนักสู้",
        "estimated_screen_time": 32.0,
        "scene_appearances": 24,
        "dialogue_lines_count": 68,
        "plot_impact_weight": 6.5,
        "emotional_arc_trajectory": [5.0, 5.5, 6.0, 7.0, 7.5],
        "key_scenes": ["SCN005", "SCN018", "SCN033"],
        "relationships": [
            ActorRelationship(
                actor_id="ACT-001",
                relationship_type="friend",
                importance=7.0,
                description="เพื่อนสนิทที่ไว้ใจได้",
                is_primary=True
            )
        ],
        "casting_priority": 7,
        "budget_allocation_tier": BudgetTier.B_TIER,
        "project_id": "PROJ-001",
        "project_name": "เงาแค้น",
        "tags": ["supporting", "friend", "loyal", "comic-relief"]
    },
    
    # Supporting Actor 3
    {
        "model_id": "peace-mind-005",
        "actor_name": "นักสืบผู้ช่วย",
        "role_type": ActorRoleType.SUPPORTING,
        "importance": ActorImportance.MEDIUM,
        "narrative_functions": ["investigator", "info_source"],
        "character_arc_type": CharacterArcType.FLAT,
        "estimated_screen_time": 18.0,
        "scene_appearances": 12,
        "dialogue_lines_count": 38,
        "plot_impact_weight": 5.5,
        "key_scenes": ["SCN012", "SCN027"],
        "casting_priority": 6,
        "budget_allocation_tier": BudgetTier.C_TIER,
        "project_id": "PROJ-001",
        "project_name": "เงาแค้น",
        "tags": ["supporting", "detective", "helper"]
    },
    
    # Extra Actor 1
    {
        "model_id": "default-extra-001",
        "actor_name": "พยาน 1",
        "role_type": ActorRoleType.EXTRA,
        "importance": ActorImportance.LOW,
        "narrative_functions": ["witness"],
        "character_arc_type": CharacterArcType.FLAT,
        "estimated_screen_time": 3.5,
        "scene_appearances": 2,
        "dialogue_lines_count": 5,
        "plot_impact_weight": 2.0,
        "casting_priority": 3,
        "budget_allocation_tier": BudgetTier.D_TIER,
        "project_id": "PROJ-001",
        "project_name": "เงาแค้น",
        "tags": ["extra", "witness", "background"]
    },
    
    # Extra Actor 2
    {
        "model_id": "default-extra-002",
        "actor_name": "เจ้าของร้าน",
        "role_type": ActorRoleType.EXTRA,
        "importance": ActorImportance.LOW,
        "narrative_functions": ["merchant"],
        "character_arc_type": CharacterArcType.FLAT,
        "estimated_screen_time": 2.0,
        "scene_appearances": 1,
        "dialogue_lines_count": 3,
        "plot_impact_weight": 1.5,
        "casting_priority": 2,
        "budget_allocation_tier": BudgetTier.D_TIER,
        "project_id": "PROJ-001",
        "project_name": "เงาแค้น",
        "tags": ["extra", "merchant", "background"]
    },
    
    # Cameo
    {
        "model_id": "special-guest-001",
        "actor_name": "อดีตเจ้านาย",
        "role_type": ActorRoleType.CAMEO,
        "importance": ActorImportance.MEDIUM,
        "narrative_functions": ["flashback", "catalyst"],
        "character_arc_type": CharacterArcType.FLAT,
        "arc_description": "ปรากฏในฉากแฟลชแบ็กสำคัญ",
        "estimated_screen_time": 5.0,
        "scene_appearances": 3,
        "dialogue_lines_count": 12,
        "plot_impact_weight": 4.0,
        "key_scenes": ["SCN010"],
        "casting_priority": 5,
        "budget_allocation_tier": BudgetTier.B_TIER,
        "project_id": "PROJ-001",
        "project_name": "เงาแค้น",
        "tags": ["cameo", "flashback", "boss"]
    }
]


async def seed_actors():
    """Seed actor profiles into database"""
    from core.logging_config import get_logger
    from motor.motor_asyncio import AsyncIOMotorClient
    from beanie import init_beanie
    from config import settings
    
    logger = get_logger(__name__)
    
    logger.info("Seeding actor profiles...")
    
    try:
        # Initialize database connection if not already done
        client = AsyncIOMotorClient(settings.MONGO_URI)
        db = client[settings.MONGO_DB_NAME]
        await init_beanie(database=db, document_models=[ActorProfile])
        logger.info("Database initialized for actor seeding")
        
        # Clear existing actors for this project (optional)
        await ActorProfile.find({"project_id": "PROJ-001"}).delete()
        logger.info("Cleared existing actors for PROJ-001")
        
        # Insert sample actors
        created_count = 0
        for actor_data in SAMPLE_ACTORS:
            actor = ActorProfile(**actor_data)
            await actor.insert()
            created_count += 1
            logger.info(f"Created actor: {actor.actor_name} ({actor.actor_id})")
        
        logger.info(f"✅ Successfully seeded {created_count} actor profiles")
        
        # Print summary
        total = await ActorProfile.find_all().count()
        logger.info(f"Total actors in database: {total}")
        
        by_role = {}
        for role_type in ActorRoleType:
            count = await ActorProfile.find({"role_type": role_type}).count()
            by_role[role_type.value] = count
        
        logger.info(f"Actors by role: {by_role}")
        
        return True
        
    except Exception as e:
        import traceback
        logger.error(f"Failed to seed actors: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False
