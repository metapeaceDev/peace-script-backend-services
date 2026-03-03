import motor.motor_asyncio
from typing import Optional
from beanie import init_beanie
from config import settings
from core.logging_config import get_logger
from documents import (
    DigitalMindModel,
    KammaLogEntry,
    TrainingLog,
    MindState,
    SimulationHistory,
    User  # Phase 2: Authentication
)

logger = get_logger(__name__)

# Registry for dynamically imported models (optional rebinding in routers)
REGISTERED_MODELS = {}

# Shared Motor client
_motor_client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None


def get_motor_client() -> motor.motor_asyncio.AsyncIOMotorClient:
    """Get MongoDB client with connection pooling and timeout settings."""
    global _motor_client
    if _motor_client is None:
        _motor_client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.MONGO_URI,
            maxPoolSize=50,  # Max connections in pool
            minPoolSize=10,  # Min connections to maintain
            maxIdleTimeMS=45000,  # Close idle connections after 45s
            serverSelectionTimeoutMS=5000,  # 5s timeout for server selection
            connectTimeoutMS=10000,  # 10s timeout for initial connection
            socketTimeoutMS=30000,  # 30s timeout for socket operations
            retryWrites=True,  # Auto-retry write operations
            retryReads=True,  # Auto-retry read operations
        )
        logger.info("✅ MongoDB client initialized with connection pooling")
    return _motor_client


def get_motor_db():
    client = get_motor_client()
    return client.get_database(settings.MONGO_DB_NAME)


async def close_db():
    global _motor_client
    if _motor_client is not None:
        _motor_client.close()
        _motor_client = None


async def init_db():
    """Initialize Motor and Beanie (core + P0 documents + Simulation Phase 2)."""
    logger.info("Initializing database connection (database.py)...")
    db = get_motor_db()

    # Import P0 models lazily to avoid circulars and preserve identity
    from documents_extra import DreamJournal, SimulationTimeline, CameraPlan, AIFeedback, CameraFeedback
    REGISTERED_MODELS.update({
        'DreamJournal': DreamJournal,
        'SimulationTimeline': SimulationTimeline,
        'CameraPlan': CameraPlan,
        'AIFeedback': AIFeedback,
        'CameraFeedback': CameraFeedback,  # Phase 2: Camera Feedback System
    })

    # Import Simulation Phase 2 models
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

    # Stage 1: core docs + Phase 1 Database Integration models + Phase 2 Auth
    await init_beanie(
        database=db,
        document_models=[
            DigitalMindModel,
            KammaLogEntry,
            TrainingLog,
            MindState,  # Phase 1: User mental state
            SimulationHistory,  # Phase 1: Simulation records
            User  # Phase 2: User authentication
        ]
    )
    # Stage 2: P0 docs + Camera Director models
    await init_beanie(database=db, document_models=[DreamJournal, SimulationTimeline, CameraPlan, AIFeedback, CameraFeedback])
    # Stage 3: Simulation Phase 2 docs
    await init_beanie(
        database=db,
        document_models=[Scenario, SimulationChain, SimulationCluster, TeachingStep, QATestCase, TeachingPack]
    )
    
    # Stage 4: Custom Presets docs (Sprint 2: Days 9-16)
    await init_beanie(
        database=db,
        document_models=[PresetTemplate, UserPreset, PresetCollection, PresetUsageLog, PresetShare]
    )
    
    # Stage 5: Kamma Appearance docs (AI Image Generation)
    from kamma_appearance_models import KammaAppearanceDocument, GeneratedImageDocument
    await init_beanie(
        database=db,
        document_models=[KammaAppearanceDocument, GeneratedImageDocument]
    )

    logger.info("Database and Beanie initialized successfully (database.py).")

    # Create recommended indexes (best-effort, ignore errors)
    try:
        dbi = get_motor_db()
        dj = dbi.get_collection('dream_journals')
        st = dbi.get_collection('simulation_timelines')
        # Dream journals indexes
        await dj.create_index('model_id')
        await dj.create_index('date')
        await dj.create_index('emotion_score')
        await dj.create_index('tags')
        # Simulation timelines indexes
        await st.create_index('model_id')
        await st.create_index('timeline_type')
        await st.create_index('start_time')
        
        # Simulation Phase 2 indexes
        scenarios_coll = dbi.get_collection('scenarios')
        await scenarios_coll.create_index('scenario_id', unique=True)
        await scenarios_coll.create_index('model_id')
        await scenarios_coll.create_index('status')
        await scenarios_coll.create_index('cluster_id')
        await scenarios_coll.create_index('tags')
        
        chains_coll = dbi.get_collection('simulation_chains')
        await chains_coll.create_index('chain_id', unique=True)
        await chains_coll.create_index('scenario_id')
        await chains_coll.create_index('status')
        
        clusters_coll = dbi.get_collection('simulation_clusters')
        await clusters_coll.create_index('cluster_id', unique=True)
        await clusters_coll.create_index('scenario_ids')
        
        teaching_coll = dbi.get_collection('teaching_steps')
        await teaching_coll.create_index('step_id', unique=True)
        await teaching_coll.create_index('scenario_id')
        await teaching_coll.create_index('teaching_pack_id')
        
        qa_coll = dbi.get_collection('qa_test_cases')
        await qa_coll.create_index('test_case_id', unique=True)
        await qa_coll.create_index('scenario_id')
        await qa_coll.create_index('status')
        
        # Phase 1: Database Integration indexes
        mind_states_coll = dbi.get_collection('mind_states')
        await mind_states_coll.create_index('user_id', unique=True)
        await mind_states_coll.create_index('updated_at')
        await mind_states_coll.create_index([('user_id', 1), ('updated_at', -1)])
        
        sim_history_coll = dbi.get_collection('simulation_history')
        await sim_history_coll.create_index('simulation_id', unique=True)
        await sim_history_coll.create_index('user_id')
        await sim_history_coll.create_index('scenario_id')
        await sim_history_coll.create_index('timestamp')
        await sim_history_coll.create_index('choice_type')
        await sim_history_coll.create_index([('user_id', 1), ('timestamp', -1)])
        await sim_history_coll.create_index([('scenario_id', 1), ('timestamp', -1)])
        
        # Phase 2: Camera Feedback indexes
        camera_feedback_coll = dbi.get_collection('camera_feedback')
        await camera_feedback_coll.create_index([('user_id', 1), ('timestamp', -1)])
        await camera_feedback_coll.create_index([('emotion', 1), ('accepted', 1)])
        await camera_feedback_coll.create_index([('rating', -1), ('timestamp', -1)])
        await camera_feedback_coll.create_index([('accepted', 1), ('confidence', -1)])
        await camera_feedback_coll.create_index([('emotion', 1), ('intensity', 1), ('accepted', 1)])
        
        # Custom Presets indexes (Sprint 2: Days 9-16)
        preset_templates_coll = dbi.get_collection('preset_templates')
        await preset_templates_coll.create_index('template_id', unique=True)
        await preset_templates_coll.create_index('category')
        
        user_presets_coll = dbi.get_collection('user_presets')
        await user_presets_coll.create_index('preset_id', unique=True)
        await user_presets_coll.create_index('owner_id')
        await user_presets_coll.create_index([('owner_id', 1), ('created_at', -1)])
        
        preset_usage_logs_coll = dbi.get_collection('preset_usage_logs')
        await preset_usage_logs_coll.create_index([('user_id', 1), ('used_at', -1)])
        
        logger.info("Simulation Phase 2 indexes created successfully")
        logger.info("Phase 1 Database Integration indexes created successfully")
        logger.info("Phase 2 Camera Feedback indexes created successfully")
    except Exception as idx_err:
        # Index creation is best-effort
        logger.warning(f"Index creation warning: {idx_err}")
        pass


async def ensure_p0_models_initialized():
    """Best-effort to ensure P0 collections are initialized."""
    from documents_extra import DreamJournal, SimulationTimeline, CameraPlan, AIFeedback, CameraFeedback
    try:
        DreamJournal.get_settings()
        SimulationTimeline.get_settings()
        CameraPlan.get_settings()
        AIFeedback.get_settings()
        CameraFeedback.get_settings()
        return
    except Exception:
        pass
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)
    db = client.get_database(settings.MONGO_DB_NAME)
    await init_beanie(database=db, document_models=[DreamJournal, SimulationTimeline, CameraPlan, AIFeedback, CameraFeedback])

