import motor.motor_asyncio
from beanie import init_beanie
from config import settings
from core.logging_config import get_logger
from documents import DigitalMindModel, KammaLogEntry, TrainingLog, MindState, SimulationHistory, CittaMomentRecord
from auth.models import User  # Import User จาก auth.models โดยตรง

logger = get_logger(__name__)

# Expose registered models for routers to rebind class identity if needed
REGISTERED_MODELS = {}


async def init_db():
    """Initialize Mongo connection and register all Beanie documents, including P0 models and Phase 2 Simulation models."""
    logger.info("Initializing database connection (db_init.py)...")
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)
    database = client.get_database(settings.MONGO_DB_NAME)

    # Import P0 models lazily
    from documents_extra import DreamJournal, SimulationTimeline, CameraPlan, AIFeedback, CameraFeedback
    REGISTERED_MODELS.update({
        'DreamJournal': DreamJournal,
        'SimulationTimeline': SimulationTimeline,
        'CameraPlan': CameraPlan,
        'AIFeedback': AIFeedback,
        'CameraFeedback': CameraFeedback,  # Phase 2: Camera Feedback System
    })

    # Import Simulation Phase 2 models (only Document classes, not BaseModel)
    from documents_simulation import (
        Scenario,
        SimulationChain,
        SimulationCluster,
        TeachingStep,
        QATestCase,
        TeachingPack
    )
    REGISTERED_MODELS.update({
        'Scenario': Scenario,
        'SimulationChain': SimulationChain,
        'SimulationCluster': SimulationCluster,
        'TeachingStep': TeachingStep,
        'QATestCase': QATestCase,
        'TeachingPack': TeachingPack,
    })

    # Import Actor Classification models
    from documents_actors import ActorProfile
    REGISTERED_MODELS.update({
        'ActorProfile': ActorProfile,
    })

    # Import Rupa (Material Form) models - Option 2: Complete 28 Material Forms
    from rupa_models import RupaProfile
    REGISTERED_MODELS.update({
        'RupaProfile': RupaProfile,
    })

    # Import NarrativeStructure models (Peace Script Integration - Week 1)
    from documents_narrative import (
        Project,
        StoryScope,
        Character,
        Scene,
        Shot,
        Visual
    )
    REGISTERED_MODELS.update({
        'Project': Project,
        'StoryScope': StoryScope,
        'Character': Character,
        'Scene': Scene,
        'Shot': Shot,
        'Visual': Visual,
    })

    # Import Production models (Peace Script: Production Breakdown System)
    from documents_production import (
        ProductionQueue,
        SceneBreakdown,
        CrewSheet,
        PropsInventory,
        SceneSetDetails
    )
    REGISTERED_MODELS.update({
        'ProductionQueue': ProductionQueue,
        'SceneBreakdown': SceneBreakdown,
        'CrewSheet': CrewSheet,
        'PropsInventory': PropsInventory,
        'SceneSetDetails': SceneSetDetails,
    })

    # Import Simulation Editor Graph models
    from documents_graph import ScenarioGraph
    REGISTERED_MODELS.update({
        'ScenarioGraph': ScenarioGraph,
    })

    # Import Storyboard models (Step 6: Visual Shot Planning)
    from documents_storyboard import Storyboard
    REGISTERED_MODELS.update({
        'Storyboard': Storyboard,
    })

    # Import Custom Presets models (Sprint 2: Days 9-16)
    from documents_presets import (
        PresetTemplate,
        UserPreset,
        PresetCollection,
        PresetUsageLog,
        PresetShare
    )
    REGISTERED_MODELS.update({
        'PresetTemplate': PresetTemplate,
        'UserPreset': UserPreset,
        'PresetCollection': PresetCollection,
        'PresetUsageLog': PresetUsageLog,
        'PresetShare': PresetShare,
    })

    # Import Kamma Appearance models
    from kamma_appearance_models import KammaAppearanceDocument, GeneratedImageDocument
    REGISTERED_MODELS.update({
        'KammaAppearanceDocument': KammaAppearanceDocument,
        'GeneratedImageDocument': GeneratedImageDocument,
    })

    # Import Product Placement models (Peace Script v1.4: Product Placement System)
    from documents_placement import Brand, Product, ProductPlacement
    REGISTERED_MODELS.update({
        'Brand': Brand,
        'Product': Product,
        'ProductPlacement': ProductPlacement,
    })

    # Import Video Generation & Album models (Motion Editor: Video System)
    from documents_video import VideoGenerationJob, GeneratedVideo, Album, ExportTask
    REGISTERED_MODELS.update({
        'VideoGenerationJob': VideoGenerationJob,
        'GeneratedVideo': GeneratedVideo,
        'Album': Album,
        'ExportTask': ExportTask,
    })

    # Import Image Gallery models (Character Profile Albums - Separate from Video Albums)
    from documents_gallery import ImageAlbum
    REGISTERED_MODELS.update({
        'ImageAlbum': ImageAlbum,
    })

    # Import Image Gallery models (Character Profile Albums)
    from documents_gallery import ImageAlbum
    REGISTERED_MODELS.update({
        'ImageAlbum': ImageAlbum,
    })

    # Initialize all documents in one call to avoid Beanie version conflicts
    all_documents = [
        # Core documents
        DigitalMindModel, KammaLogEntry, TrainingLog,
        # Phase 1: Mind State Tracking
        MindState, SimulationHistory,
        # Citta-Cetasika System
        CittaMomentRecord,
        # Phase 2: User Authentication
        User,
        # P0 documents
        DreamJournal, SimulationTimeline, CameraPlan, AIFeedback, CameraFeedback,
        # Simulation Phase 2 documents (Document classes only)
        Scenario,
        SimulationChain,
        SimulationCluster,
        TeachingStep,
        QATestCase,
        TeachingPack,
        # Actor Classification documents
        ActorProfile,
        # Rupa (Material Form) documents
        RupaProfile,
        # NarrativeStructure documents (Peace Script Integration - Week 1)
        Project,
        StoryScope,
        Character,
        Scene,
        Shot,
        Visual,
        # Simulation Editor Graph documents
        ScenarioGraph,
        # Storyboard documents (Step 6: Visual Shot Planning)
        Storyboard,
        # Production Breakdown documents (Peace Script: Production Planning System)
        ProductionQueue,
        SceneBreakdown,
        CrewSheet,
        PropsInventory,
        SceneSetDetails,
        # Custom Presets documents (Sprint 2: Days 9-16)
        PresetTemplate,
        UserPreset,
        PresetCollection,
        PresetUsageLog,
        PresetShare,
        # Kamma Appearance documents
        KammaAppearanceDocument,
        GeneratedImageDocument,
        # Product Placement documents (Peace Script v1.4: Product Placement System)
        Brand,
        Product,
        ProductPlacement,
        # Video Generation & Album documents (Motion Editor: Video System)
        VideoGenerationJob,
        GeneratedVideo,
        Album,
        ExportTask,
        # Image Gallery documents
        ImageAlbum,
    ]
    
    await init_beanie(database=database, document_models=all_documents)

    # Post-check
    try:
        # Core collections
        logger.info("Core collections: DigitalMindModel, KammaLogEntry, TrainingLog")
        
        # Phase 2 collections
        user_settings = User.get_settings()
        mind_settings = MindState.get_settings()
        sim_settings = SimulationHistory.get_settings()
        logger.info("Phase 2 collections ready: User=%s MindState=%s SimulationHistory=%s", 
                   getattr(user_settings, 'name', None),
                   getattr(mind_settings, 'name', None),
                   getattr(sim_settings, 'name', None))
        
        # P0 collections
        dj = DreamJournal.get_settings()
        st = SimulationTimeline.get_settings()
        logger.info("P0 collections ready: DJ=%s ST=%s", getattr(dj, 'name', None), getattr(st, 'name', None))
        
        # Simulation Phase 2 collections
        sc = Scenario.get_settings()
        logger.info("Simulation Phase 2 collections ready: Scenario=%s", getattr(sc, 'name', None))
        
        # Rupa collection
        rupa = RupaProfile.get_settings()
        logger.info("Rupa collection ready: RupaProfile=%s", getattr(rupa, 'name', None))
        
        # NarrativeStructure collections (Peace Script Integration - Week 1)
        project_settings = Project.get_settings()
        scope_settings = StoryScope.get_settings()
        character_settings = Character.get_settings()
        scene_settings = Scene.get_settings()
        shot_settings = Shot.get_settings()
        visual_settings = Visual.get_settings()
        logger.info("NarrativeStructure collections ready: Project=%s StoryScope=%s Character=%s Scene=%s Shot=%s Visual=%s",
                   getattr(project_settings, 'name', None),
                   getattr(scope_settings, 'name', None),
                   getattr(character_settings, 'name', None),
                   getattr(scene_settings, 'name', None),
                   getattr(shot_settings, 'name', None),
                   getattr(visual_settings, 'name', None))
        
        # Production collections (Peace Script: Production Breakdown System)
        queue_settings = ProductionQueue.get_settings()
        breakdown_settings = SceneBreakdown.get_settings()
        crew_settings = CrewSheet.get_settings()
        props_settings = PropsInventory.get_settings()
        set_settings = SceneSetDetails.get_settings()
        logger.info("Production collections ready: Queue=%s Breakdown=%s Crew=%s Props=%s Sets=%s",
                   getattr(queue_settings, 'name', None),
                   getattr(breakdown_settings, 'name', None),
                   getattr(crew_settings, 'name', None),
                   getattr(props_settings, 'name', None),
                   getattr(set_settings, 'name', None))
        
        # Custom Presets collections (Sprint 2: Days 9-16)
        preset_template_settings = PresetTemplate.get_settings()
        user_preset_settings = UserPreset.get_settings()
        preset_collection_settings = PresetCollection.get_settings()
        logger.info("Custom Presets collections ready: PresetTemplate=%s UserPreset=%s PresetCollection=%s",
                   getattr(preset_template_settings, 'name', None),
                   getattr(user_preset_settings, 'name', None),
                   getattr(preset_collection_settings, 'name', None))
    except Exception as e:
        logger.error("Collection check failed: %s", repr(e))

    # Optional indexes: TTL for logs and unique constraint on (model_id, simulation_id)
    try:
        # TTL on kamma_logs.timestamp if enabled
        ttl_seconds = getattr(settings, 'KAMMA_TTL_SECONDS', None)
        if ttl_seconds is not None:
            await database.command({
                'collMod': 'kamma_logs',
                'index': {
                    'keyPattern': {'timestamp': 1},
                    'expireAfterSeconds': int(ttl_seconds)
                }
            })
    except Exception:
        # Silently continue if not supported or missing
        pass

    try:
        # Unique index on simulation_timelines (model_id, simulation_id) if enabled
        if getattr(settings, 'UNIQUE_TIMELINE_PER_MODEL', False):
            await database['simulation_timelines'].create_index(
                [('model_id', 1), ('simulation_id', 1)], unique=True, name='uniq_model_sim'
            )
    except Exception:
        pass

    # Custom Presets indexes (Sprint 2: Days 9-16)
    try:
        preset_templates_coll = database['preset_templates']
        await preset_templates_coll.create_index('template_id', unique=True)
        await preset_templates_coll.create_index('category')
        await preset_templates_coll.create_index('visibility')
        await preset_templates_coll.create_index('created_at')
        
        user_presets_coll = database['user_presets']
        await user_presets_coll.create_index('preset_id', unique=True)
        await user_presets_coll.create_index('owner_id')
        await user_presets_coll.create_index('category')
        await user_presets_coll.create_index('visibility')
        await user_presets_coll.create_index('is_favorite')
        await user_presets_coll.create_index([('owner_id', 1), ('created_at', -1)])
        
        preset_collections_coll = database['preset_collections']
        await preset_collections_coll.create_index('collection_id', unique=True)
        await preset_collections_coll.create_index('owner_id')
        await preset_collections_coll.create_index('parent_collection_id')
        
        preset_usage_logs_coll = database['preset_usage_logs']
        await preset_usage_logs_coll.create_index('log_id', unique=True)
        await preset_usage_logs_coll.create_index('preset_id')
        await preset_usage_logs_coll.create_index('user_id')
        await preset_usage_logs_coll.create_index([('user_id', 1), ('used_at', -1)])
        await preset_usage_logs_coll.create_index([('preset_id', 1), ('used_at', -1)])
        
        preset_shares_coll = database['preset_shares']
        await preset_shares_coll.create_index('share_id', unique=True)
        await preset_shares_coll.create_index('preset_id')
        await preset_shares_coll.create_index('shared_with_user_id')
        await preset_shares_coll.create_index([('shared_with_user_id', 1), ('shared_at', -1)])
        
        logger.info("Custom Presets indexes created successfully")
    except Exception as idx_err:
        logger.warning(f"Custom Presets index creation warning: {idx_err}")
        pass

    # Image Gallery indexes (Character Profile Albums - Separate from Video Albums)
    try:
        image_albums_coll = database['image_albums']
        await image_albums_coll.create_index('album_id', unique=True)
        await image_albums_coll.create_index('actor_id')
        await image_albums_coll.create_index('project_id')
        await image_albums_coll.create_index('scene_id')
        await image_albums_coll.create_index('shot_id')
        await image_albums_coll.create_index('storyboard_id')
        await image_albums_coll.create_index('created_at')
        await image_albums_coll.create_index([('actor_id', 1), ('created_at', -1)])
        await image_albums_coll.create_index([('shot_id', 1), ('created_at', -1)])
        await image_albums_coll.create_index([('storyboard_id', 1), ('created_at', -1)])
        
        logger.info("Image Gallery indexes created successfully")
    except Exception as idx_err:
        logger.warning(f"Image Gallery index creation warning: {idx_err}")
        pass

    logger.info("Database and Beanie initialized successfully (db_init.py).")
