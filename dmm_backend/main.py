from dotenv import load_dotenv

# Load environment variables from .env file FIRST (before any imports that use env vars)
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pymongo.errors import PyMongoError
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from schemas import ReactionRequest, CultivationRequest, MessageResponse, DMMProfileSchema, ReactionSimulationResponse, KammaLogEntrySchema
from documents import DigitalMindModel, KammaLogEntry, TrainingLog
from core.services import transform_dmm_to_editor_profile, process_reaction_simulation
from core.logging_config import get_logger
from core.security import get_api_key
try:
    from db_init import init_db as _init_db
except Exception:
    from database import init_db as _init_db
try:
    from database import close_db as _close_db
except Exception:
    async def _close_db():
        return None
from config import settings  # Import settings from config
from typing import List
# Import routers with robust fallbacks and import the `router` objects directly
try:
    from dmm_backend.routers.dream_journals import router as dream_router  # type: ignore
except Exception:
    try:
        from routers.dream_journals import router as dream_router  # type: ignore
    except Exception:
        from routers.dream_journals_router import router as dream_router  # type: ignore

try:
    from dmm_backend.routers.simulation_timelines import router as timeline_router  # type: ignore
except Exception:
    from routers.simulation_timelines import router as timeline_router  # type: ignore

try:
    from dmm_backend.routers.camera_director import router as camera_router  # type: ignore
except Exception:
    from routers.camera_director import router as camera_router  # type: ignore

# Phase 2: Camera Feedback System
try:
    from dmm_backend.routers.camera_feedback import router as camera_feedback_router  # type: ignore
except Exception:
    from routers.camera_feedback import router as camera_feedback_router  # type: ignore

try:
    from dmm_backend.routers.analytics import router as analytics_router  # type: ignore
except Exception:
    from routers.analytics import router as analytics_router  # type: ignore

# Import Simulation routers
try:
    from dmm_backend.routers.scenarios import router as scenarios_router  # type: ignore
except Exception:
    from routers.scenarios import router as scenarios_router  # type: ignore

try:
    from dmm_backend.routers.simulation_events import router as simulation_events_router  # type: ignore
except Exception:
    from routers.simulation_events import router as simulation_events_router  # type: ignore

try:
    from dmm_backend.routers.simulation_chains import router as simulation_chains_router  # type: ignore
except Exception:
    from routers.simulation_chains import router as simulation_chains_router  # type: ignore

try:
    from dmm_backend.routers.simulation_clusters import router as simulation_clusters_router  # type: ignore
except Exception:
    from routers.simulation_clusters import router as simulation_clusters_router  # type: ignore

try:
    from dmm_backend.routers.teaching import router as teaching_router  # type: ignore
except Exception:
    from routers.teaching import router as teaching_router  # type: ignore

try:
    from dmm_backend.routers.qa import router as qa_router  # type: ignore
except Exception:
    from routers.qa import router as qa_router  # type: ignore

try:
    from dmm_backend.routers.kamma_analytics import router as kamma_analytics_router  # type: ignore
except Exception:
    from routers.kamma_analytics import router as kamma_analytics_router  # type: ignore

try:
    from dmm_backend.routers.core_profile import router as core_profile_router  # type: ignore
except Exception:
    from routers.core_profile import router as core_profile_router  # type: ignore

try:
    from dmm_backend.routers.actors import router as actors_router  # type: ignore
except Exception:
    from routers.actors import router as actors_router  # type: ignore

# Training router (Phase 5)
try:
    from dmm_backend.routers.training import router as training_router  # type: ignore
except Exception:
    from routers.training import router as training_router  # type: ignore

# MindState router (Phase 1: Database Integration - Mental State Tracking)
try:
    from dmm_backend.routers.mind_state import router as mind_state_router  # type: ignore
except Exception:
    from routers.mind_state import router as mind_state_router  # type: ignore

# SimulationHistory router (Phase 1: Database Integration - Simulation Tracking)
try:
    from dmm_backend.routers.simulation_history import router as simulation_history_router  # type: ignore
except Exception:
    from routers.simulation_history import router as simulation_history_router  # type: ignore

# Citta-Cetasika Engine router (Phase 5: Mind Model Integration)
try:
    from dmm_backend.routers.citta_cetasika import router as citta_cetasika_router  # type: ignore
except Exception:
    from routers.citta_cetasika import router as citta_cetasika_router  # type: ignore

# Paticcasamuppāda Engine router (Phase 5: Dependent Origination Integration)
try:
    from dmm_backend.routers.paticcasamuppada import router as paticcasamuppada_router  # type: ignore
except Exception:
    from routers.paticcasamuppada import router as paticcasamuppada_router  # type: ignore

# Rupa System router (Phase 5: 28 Material Forms - Option 2 Complete Replacement)
try:
    from dmm_backend.routers.rupa import router as rupa_router  # type: ignore
except Exception:
    from routers.rupa import router as rupa_router  # type: ignore

# Character Avatar router (Phase 5: Avatar Visualization & Animation)
try:
    from dmm_backend.routers.character_avatar import router as character_avatar_router  # type: ignore
except Exception:
    from routers.character_avatar import router as character_avatar_router  # type: ignore

# Timeline Editor router (Priority #5: Multi-track Timeline)
try:
    from dmm_backend.routers.timeline_editor_router import router as timeline_editor_router  # type: ignore
except Exception:
    from routers.timeline_editor_router import router as timeline_editor_router  # type: ignore

# Placement router (Priority #7.2: Camera & Scene Positioning)
try:
    from dmm_backend.routers.placement_router import router as placement_router  # type: ignore
except Exception:
    from routers.placement_router import router as placement_router  # type: ignore

# Extension router (Priority #7.4: Plugin Marketplace)
try:
    from dmm_backend.routers.extension_router import router as extension_router  # type: ignore
except Exception:
    from routers.extension_router import router as extension_router  # type: ignore

# AI Generation router (Week 1: Local LLM - Free)
try:
    from dmm_backend.routers.ai_generate import router as ai_router  # type: ignore
except Exception:
    from routers.ai_generate import router as ai_router  # type: ignore

# NarrativeStructure routers (Week 3: Story Development System)
try:
    from dmm_backend.routers.narrative_projects import router as narrative_projects_router  # type: ignore
except Exception:
    from routers.narrative_projects import router as narrative_projects_router  # type: ignore

try:
    from dmm_backend.routers.narrative_scopes import router as narrative_scopes_router  # type: ignore
except Exception:
    from routers.narrative_scopes import router as narrative_scopes_router  # type: ignore

try:
    from dmm_backend.routers.narrative_scenes import router as narrative_scenes_router  # type: ignore
except Exception:
    from routers.narrative_scenes import router as narrative_scenes_router  # type: ignore

try:
    from dmm_backend.routers.narrative_characters import router as narrative_characters_router  # type: ignore
except Exception:
    from routers.narrative_characters import router as narrative_characters_router  # type: ignore

try:
    from dmm_backend.routers.narrative_shots import router as narrative_shots_router  # type: ignore
except Exception:
    from routers.narrative_shots import router as narrative_shots_router  # type: ignore

try:
    from dmm_backend.routers.narrative_visuals import router as narrative_visuals_router  # type: ignore
except Exception:
    from routers.narrative_visuals import router as narrative_visuals_router  # type: ignore

# Video Generation router (Motion Editor: Video Generation & Export)
try:
    from dmm_backend.routers.video_generation import router as video_generation_router  # type: ignore
except Exception:
    from routers.video_generation import router as video_generation_router  # type: ignore

# Album router (Motion Editor: Album & Gallery System for VIDEOS)
try:
    from dmm_backend.routers.album import router as album_router  # type: ignore
except Exception:
    from routers.album import router as album_router  # type: ignore

# Image Gallery router (Character Profile Albums - Separate from Video Albums)
try:
    from dmm_backend.routers.image_gallery import router as image_gallery_router  # type: ignore
except Exception:
    from routers.image_gallery import router as image_gallery_router  # type: ignore

# Simulation Editor router (Visual Graph Editor)
try:
    from dmm_backend.routers.simulation_editor_router import router as simulation_editor_router  # type: ignore
except Exception:
    from routers.simulation_editor_router import router as simulation_editor_router  # type: ignore

# Storyboard router (Step 6: Visual Shot Planning)
try:
    from dmm_backend.routers.storyboard import router as storyboard_router  # type: ignore
except Exception:
    from routers.storyboard import router as storyboard_router  # type: ignore

# Character Creation Workflow router (Hybrid 2D→3D Approach)
try:
    from dmm_backend.routers.character_creation_workflow_router import router as workflow_router  # type: ignore
except Exception:
    from routers.character_creation_workflow_router import router as workflow_router  # type: ignore

# Rebirth Toolkit router (Optional Helper Tools for Cross-Lifetime Storytelling)
try:
    from dmm_backend.routers.rebirth_toolkit_router import router as rebirth_toolkit_router  # type: ignore
except Exception:
    from routers.rebirth_toolkit_router import router as rebirth_toolkit_router  # type: ignore

# Wardrobe System router (STEP 3.5 - Character Wardrobe & Styling)
try:
    from dmm_backend.routers.wardrobe import router as wardrobe_router  # type: ignore
except Exception:
    from routers.wardrobe import router as wardrobe_router  # type: ignore

# Dhamma Themes router (Peace Script v2: Buddhist Theme Integration)
try:
    from dmm_backend.routers.dhamma_themes import router as dhamma_themes_router  # type: ignore
except Exception:
    from routers.dhamma_themes import router as dhamma_themes_router  # type: ignore

# Admin Dashboard router (Milestone 6: Admin Dashboard)
try:
    from dmm_backend.routers.admin import router as admin_router  # type: ignore
except Exception:
    from routers.admin import router as admin_router  # type: ignore

# Product Placement router (Peace Script v1.4: Product Placement System)
try:
    from dmm_backend.routers.placement import router as product_placement_router  # type: ignore
except Exception:
    from routers.placement import router as product_placement_router  # type: ignore

# Shots router (Peace Script v2.0: LTX-style Storyboard System)
try:
    from dmm_backend.routers.shots import router as shots_router  # type: ignore
except Exception:
    from routers.shots import router as shots_router  # type: ignore

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import time
import os
import tempfile
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from core.ratelimit import limiter, add_rate_limit_middleware
from core.error_handlers import setup_error_handlers
from middleware.auth_rate_limit import AuthRateLimitMiddleware

logger = get_logger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Custom rate limit handler
async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """Handle rate limit exceeded errors"""
    return Response(
        content=f"Rate limit exceeded: {exc.detail}",
        status_code=429
    )

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)  # type: ignore[arg-type]

# Setup standardized error handlers
setup_error_handlers(app)

import asyncio

# Store start time globally
app_start_time = time.time()
metrics_update_task = None


async def update_metrics_periodically():
    """Background task to update system and database metrics."""
    import psutil
    from motor.motor_asyncio import AsyncIOMotorClient
    
    logger.info("Starting metrics update background task")
    
    while True:
        try:
            # Update system metrics
            SYSTEM_CPU_USAGE.set(psutil.cpu_percent(interval=0.1))
            SYSTEM_MEMORY_USAGE.set(psutil.virtual_memory().percent)
            disk_path = '/' if os.name != 'nt' else 'C:\\'
            SYSTEM_DISK_USAGE.set(psutil.disk_usage(disk_path).percent)
            
            # Update uptime
            uptime = time.time() - app_start_time
            APP_UPTIME_SECONDS.set(uptime)
            
            # Update database metrics
            if settings.USE_MOCK_DB:
                DB_CONNECTED.set(1)
                DB_RESPONSE_TIME.set(0)
            else:
                try:
                    client = AsyncIOMotorClient(settings.MONGO_URI)
                    db_start = time.time()
                    await client.admin.command("ping")
                    db_response_time = (time.time() - db_start) * 1000
                    
                    DB_CONNECTED.set(1)
                    DB_RESPONSE_TIME.set(db_response_time)
                    
                    db = client.get_database(settings.MONGO_DB_NAME)
                    collections = await db.list_collection_names()
                    DB_COLLECTION_COUNT.set(len(collections))
                    
                    client.close()
                except Exception as e:
                    logger.error(f"Failed to update database metrics: {e}")
                    DB_CONNECTED.set(0)
                
        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
        
        await asyncio.sleep(30)  # Update every 30 seconds


@app.on_event("startup")
async def on_startup():
    global metrics_update_task
    await _init_db()
    # Add rate limit middleware once; ignore if already started/added
    try:
        add_rate_limit_middleware(app)
    except Exception as e:
        # Starlette raises if adding middleware post-start; safe to ignore in hot-reload/dev
        logger.debug(f"Rate limit middleware add skipped: {e}")
    
    # Start metrics update background task
    metrics_update_task = asyncio.create_task(update_metrics_periodically())
    logger.info("Metrics update task started")


@app.on_event("shutdown")
async def on_shutdown():
    global metrics_update_task
    if metrics_update_task:
        metrics_update_task.cancel()
        try:
            await metrics_update_task
        except asyncio.CancelledError:
            logger.info("Metrics update task cancelled")
    await _close_db()


# --- Add CORS middleware ---
# Origins are now loaded from the .env file via the settings object
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "X-Next-After-Id",
        "X-Has-More",
        "X-Total-Count",
        "X-Page-Skip",
        "X-Page-Limit",
        "X-Returned",
        "X-Next-Skip",
    ],
)


# Comprehensive Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        
        # Basic security headers that work
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        
        # Test additional headers one by one
        response.headers["X-XSS-Protection"] = "1"
        
        # Allow Swagger UI to load resources from CDN
        if request.url.path in ["/docs", "/redoc"]:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https://fastapi.tiangolo.com"
            )
        else:
            response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        # Cache headers
        response.headers["Cache-Control"] = "no-cache"
        
        # HSTS only for HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000"
            
        return response

app.add_middleware(SecurityHeadersMiddleware)

# Add rate limiting middleware for auth endpoints (after CORS)
app.add_middleware(AuthRateLimitMiddleware)

# Mount static files for video serving
video_output_dir = os.path.join(tempfile.gettempdir(), "video_output")
if os.path.exists(video_output_dir):
    app.mount("/videos", StaticFiles(directory=video_output_dir), name="videos")
    logger.info(f"✅ Mounted static video files at /videos from {video_output_dir}")
else:
    logger.warning(f"⚠️  Video output directory not found: {video_output_dir}")

# Mount feature routers (P0)
app.include_router(dream_router)
app.include_router(timeline_router)
app.include_router(camera_router)  # Camera Director AI APIs (7 endpoints)
app.include_router(camera_feedback_router)  # Phase 2: Camera Feedback System (4 endpoints)
app.include_router(analytics_router)
app.include_router(timeline_editor_router)  # Priority #5: Multi-track Timeline Editor (15 endpoints)
app.include_router(placement_router)  # Priority #7.2: Camera & Scene Positioning (9 endpoints)
app.include_router(extension_router)  # Priority #7.4: Plugin Marketplace (8 endpoints)
app.include_router(product_placement_router)  # Peace Script v1.4: Product Placement System (21 endpoints)
app.include_router(shots_router)  # Peace Script v2.0: LTX-style Storyboard System (Shot management + AI generation)

# Mount Simulation routers (Phase 2) - routers already have prefixes configured
app.include_router(scenarios_router)
app.include_router(simulation_events_router)
app.include_router(simulation_chains_router)
app.include_router(simulation_clusters_router)
app.include_router(teaching_router)
app.include_router(qa_router)

# Mount Kamma Analytics router (Phase 3)
app.include_router(kamma_analytics_router)

# Mount Kamma-Vipāka Graph router (Phase 2: Feedback System - Kamma Graph Explorer)
from routers.kamma_graph_router import router as kamma_graph_router
app.include_router(kamma_graph_router)

# Mount Core Profile router (Complete Buddhist Psychology API)
app.include_router(core_profile_router)

# Mount Actor Classification router (Digital Actor Management)
app.include_router(actors_router, prefix="/api")

# Mount Training router (Phase 5: Training & Practice System)
app.include_router(training_router)

# Mount MindState router (Phase 1: Mental State Tracking)
app.include_router(mind_state_router)

# Mount SimulationHistory router (Phase 1: Simulation Tracking)
app.include_router(simulation_history_router)

# Mount Citta-Cetasika Engine router (Phase 5: Mind Model Integration)
app.include_router(citta_cetasika_router)

# Mount Paticcasamuppāda Engine router (Phase 5: Dependent Origination Integration)
app.include_router(paticcasamuppada_router)

# Mount Rupa System router (Phase 5: 28 Material Forms - รูป ๒๘)
app.include_router(rupa_router, prefix="/api/v1")

# Mount Character Avatar router (Phase 5: Avatar Visualization & Animation)
app.include_router(character_avatar_router, prefix="/api/character")

# Mount AI Generation router (Week 1: Local LLM - Free)
app.include_router(ai_router)

# Mount Peace Script AI Generation router (Step 2 AI)
try:
    from routers.ai_generation import router as ai_generation_router
    app.include_router(ai_generation_router)
    logger.info("✓ Peace Script AI Generation router registered")
except Exception as e:
    logger.warning(f"Peace Script AI Generation router not available: {e}")

# Mount NarrativeStructure routers (Week 3: Story Development System)
app.include_router(narrative_projects_router)
app.include_router(narrative_scopes_router)  # NEW: StoryScope CRUD
app.include_router(narrative_scenes_router)
app.include_router(narrative_characters_router)
app.include_router(narrative_shots_router)
app.include_router(narrative_visuals_router)

# Mount Simulation Editor router (Visual Graph Editor)
app.include_router(simulation_editor_router)

# Mount Storyboard router (Step 6: Visual Shot Planning)
app.include_router(storyboard_router)

# Mount Video Generation & Album routers (Motion Editor: Video System)
app.include_router(video_generation_router)  # Video generation API (5 endpoints)
app.include_router(album_router)  # Video Album & Gallery system (8 endpoints)
app.include_router(image_gallery_router)  # Image Gallery for Character/Shot Albums (11 endpoints)

# Mount Kamma Appearance router (Phase 5.2: Kamma-based Physical Appearance System)
try:
    from dmm_backend.routers.kamma_appearance_router import router as kamma_appearance_router  # type: ignore
except Exception:
    try:
        from routers.kamma_appearance_router import router as kamma_appearance_router  # type: ignore
    except Exception:
        kamma_appearance_router = None
        logger.warning("Kamma Appearance router not available")

if kamma_appearance_router:
    app.include_router(kamma_appearance_router)

# Mount Character Creation Workflow router (Hybrid 2D→3D Approach) - NEW!
app.include_router(workflow_router)  # Endpoints: /api/workflow/*

# Mount Rebirth Toolkit router (Optional Helper Tools for Cross-Lifetime Storytelling) - NEW!
app.include_router(rebirth_toolkit_router)  # Endpoints: /api/rebirth-toolkit/*
logger.info("✓ Rebirth Toolkit router registered (31 Realms + Calculator + Template)")

# Mount Wardrobe System router (STEP 3.5 - Character Wardrobe & Styling) - NEW!
app.include_router(wardrobe_router)  # Endpoints: /api/wardrobe/*
logger.info("✓ Wardrobe System router registered (Clothing, Accessories, Outfits)")

# Mount Dhamma Themes router (Peace Script v2: Buddhist Theme Integration)
app.include_router(dhamma_themes_router)  # Endpoints: /api/dhamma/themes/*
logger.info("✓ Dhamma Themes router registered (Theme Library, Validation, Suggestion - 6 endpoints)")

# Mount Admin Dashboard router (Milestone 6: Admin Dashboard)
app.include_router(admin_router)  # Endpoints: /api/admin/*
logger.info("✓ Admin Dashboard router registered (Theme Management, Analytics, Quality Check - 15 endpoints)")

# Mount Production Management router (Peace Script: Production Breakdown System)
try:
    from dmm_backend.routers.production import router as production_router  # type: ignore
except Exception:
    try:
        from routers.production import router as production_router  # type: ignore
    except Exception:
        production_router = None
        logger.warning("Production router not available")

if production_router:
    app.include_router(production_router)  # Endpoints: /api/production/*
    logger.info("✓ Production Management router registered (Breakdown Q, Scene Breakdown, Crew Sheet, Props - 17 endpoints)")

# Mount Genre Management router (Peace Script: Genre System - STEP 1)
try:
    from dmm_backend.routers.genres import router as genres_router  # type: ignore
except Exception:
    try:
        from routers.genres import router as genres_router  # type: ignore
    except Exception:
        genres_router = None
        logger.warning("Genres router not available")

if genres_router:
    app.include_router(genres_router)  # Endpoints: /api/genres/*
    logger.info("✓ Genre Management router registered (22 genres: 11 main + 11 secondary, validation, suggestions - 6 endpoints)")



# Mount Citta Vithi router (Phase 3.1: Mind Moment Processing - Consciousness Process Simulation)
try:
    from dmm_backend.routers.citta_vithi_router import router as citta_vithi_router  # type: ignore
except Exception:
    try:
        from routers.citta_vithi_router import router as citta_vithi_router  # type: ignore
    except Exception:
        citta_vithi_router = None
        logger.warning("Citta Vithi router not available")

if citta_vithi_router:
    app.include_router(citta_vithi_router)

# Mount Interactive Simulation router (Phase 3.4: Interactive Scenario-based Learning)
try:
    from dmm_backend.routers.simulation_router import router as simulation_router  # type: ignore
except Exception:
    try:
        from routers.simulation_router import router as simulation_router  # type: ignore
    except Exception:
        simulation_router = None
        logger.warning("Interactive Simulation router not available")

if simulation_router:
    app.include_router(simulation_router)

# Mount Motion Editor router (Shot Video Generation with Motion Effects)
try:
    from dmm_backend.routers.motion_editor import router as motion_editor_router  # type: ignore
except Exception:
    try:
        from routers.motion_editor import router as motion_editor_router  # type: ignore
    except Exception:
        motion_editor_router = None
        logger.warning("Motion Editor router not available")

if motion_editor_router:
    app.include_router(motion_editor_router)
    logger.info("✅ Motion Editor router registered")

# Mount FastAPI-Users Authentication routers (Phase 2: JWT Authentication)
try:
    from auth import fastapi_users, auth_backend
    from auth.schemas import UserRead, UserCreate, UserUpdate
    
    # Register auth routes
    app.include_router(
        fastapi_users.get_auth_router(auth_backend),
        prefix="/api/auth/jwt",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_register_router(UserRead, UserCreate),
        prefix="/api/auth",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_users_router(UserRead, UserUpdate),
        prefix="/api/users",
        tags=["users"],
    )
    logger.info("✅ FastAPI-Users authentication routes registered")
except Exception as e:
    logger.error(f"❌ Failed to register FastAPI-Users routes: {e}")
    # Fallback to old auth router
    try:
        from routers.auth_router import router as auth_router  # type: ignore
        app.include_router(auth_router)
        logger.warning("Using legacy authentication router")
    except Exception:
        logger.error("❌ No authentication system available")

# Mount Custom Presets router (Sprint 2: Days 9-16)
try:
    from routers.presets import router as presets_router  # type: ignore
except Exception:
    try:
        from dmm_backend.routers.presets import router as presets_router  # type: ignore
    except Exception:
        presets_router = None
        logger.warning("Custom Presets router not available")

if presets_router:
    app.include_router(presets_router)
else:
    logger.warning("⚠️ Custom Presets router not loaded")


@app.get("/", response_model=MessageResponse, tags=["General"], dependencies=[])
def read_root():
    return {"message": "Welcome to the Digital Mind Model API"}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Return 204 No Content for favicon to prevent 404 errors"""
    return Response(status_code=204)

@app.get("/health", tags=["General"])  # Simple health endpoint without auth
async def health_check():
    """Enhanced health check with comprehensive system status."""
    import psutil
    from datetime import datetime
    
    # Calculate uptime
    current_process = psutil.Process()
    uptime_seconds = time.time() - current_process.create_time()
    
    health_info = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.API_VERSION,
        "environment": {
            "debug_mode": settings.DEBUG_MODE,
            "api_title": settings.API_TITLE,
        },
        "uptime": {
            "seconds": round(uptime_seconds, 2),
            "formatted": f"{int(uptime_seconds // 3600)}h {int((uptime_seconds % 3600) // 60)}m {int(uptime_seconds % 60)}s"
        },
        "system": {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:\\').percent,
        }
    }
    
    # Database health check
    db_status = {"connected": False, "response_time_ms": None, "collections_count": 0}
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        client = AsyncIOMotorClient(settings.MONGO_URI)
        
        # Measure DB response time
        db_start = time.time()
        await client.admin.command("ping")
        db_response_time = (time.time() - db_start) * 1000  # Convert to ms
        
        db = client.get_database(settings.MONGO_DB_NAME)
        collections = await db.list_collection_names()
        
        db_status = {
            "connected": True,
            "response_time_ms": round(db_response_time, 2),
            "database_name": settings.MONGO_DB_NAME,
            "collections_count": len(collections),
            "collections": collections[:10],  # First 10 collections
        }
        
        # Get document counts for key collections
        try:
            counts = {}
            for coll_name in ["DigitalMindModel", "KammaLogEntry", "TrainingLog"][:3]:
                if coll_name in collections:
                    counts[coll_name] = await db[coll_name].count_documents({})
            db_status["document_counts"] = counts
        except Exception:
            pass
            
    except Exception as e:
        health_info["status"] = "degraded"
        db_status = {
            "connected": False,
            "error": str(e),
            "error_type": type(e).__name__
        }
    
    health_info["database"] = db_status
    
    # Determine overall health status
    if not db_status["connected"]:
        health_info["status"] = "unhealthy"
    elif health_info["system"]["cpu_percent"] > 90 or health_info["system"]["memory_percent"] > 90:
        health_info["status"] = "degraded"
    
    return health_info


@app.get("/health/system_stats", tags=["General"])
async def system_stats():
    """System stats for frontend (GPU checks etc) - Proxies to ComfyUI or returns Mock"""
    import psutil
    
    # Mock response to satisfy frontend check
    # In a real scenario, this would check NVIDIA-SMI or similar
    return {
        "system": {
            "os": os.name,
            "python_version": "3.10",
            "comfyui_version": "mock-v1"
        },
        "devices": [
            {
                "name": "Mock GPU for Dev",
                "type": "cuda",
                "index": 0,
                "vram_total": 8589934592, # 8GB
                "vram_free": 4294967296, # 4GB
                "torch_vram_total": 0,
                "torch_vram_free": 0
            }
        ]
    }


@app.get("/health/detailed", tags=["General"])
async def health_detailed():
    """Detailed health check - Alias for /health but can be expanded"""
    return await health_check()


@app.head("/health", tags=["General"])
async def health_head() -> Response:
    """Lightweight health probe for tooling that issues HEAD requests."""
    return Response(status_code=200)

@app.get("/comfyui/health", tags=["ComfyUI"])
async def check_comfyui_health():
    """Check ComfyUI server health status."""
    import httpx
    from datetime import datetime
    
    comfyui_url = "http://127.0.0.1:8188/system_stats"
    
    try:
        start_time = time.time()
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(comfyui_url)
            response_time = (time.time() - start_time) * 1000  # ms
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "online",
                    "timestamp": datetime.utcnow().isoformat(),
                    "response_time_ms": round(response_time, 2),
                    "url": comfyui_url,
                    "system_stats": data
                }
            else:
                return {
                    "status": "error",
                    "timestamp": datetime.utcnow().isoformat(),
                    "response_time_ms": round(response_time, 2),
                    "url": comfyui_url,
                    "error": f"HTTP {response.status_code}"
                }
    except httpx.TimeoutException:
        return {
            "status": "offline",
            "timestamp": datetime.utcnow().isoformat(),
            "url": comfyui_url,
            "error": "Connection timeout (3s)"
        }
    except Exception as e:
        return {
            "status": "offline",
            "timestamp": datetime.utcnow().isoformat(),
            "url": comfyui_url,
            "error": str(e),
            "error_type": type(e).__name__
        }

@app.get(
    "/models/", 
    response_model=List[DMMProfileSchema], 
    summary="Get All Model Profiles",
    description="Retrieves a list of all Digital Mind Model profiles.",
    tags=["Models"],
    dependencies=[Depends(get_api_key)]
)
async def get_all_models():
    """
    Retrieves all DMM profiles.
    - **Returns**: A list of `DMMProfileSchema` objects.
    """
    logger.info("Retrieving all model profiles")
    # Primary path: try via Beanie documents
    try:
        models = await DigitalMindModel.find_all().to_list()
        transformed_models = [
            transform_dmm_to_editor_profile(m.model_dump())
            for m in models
        ]
        logger.info(f"Successfully retrieved {len(transformed_models)} model profiles (beanie)")
        return transformed_models
    except Exception as beanie_err:
        # Fallback: fetch raw documents via motor to be more tolerant of missing fields
        logger.error(
            f"Unexpected error while retrieving all models via Beanie, falling back to raw fetch: {beanie_err}"
        )
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            client = AsyncIOMotorClient(settings.MONGO_URI)
            db = client.get_database(settings.MONGO_DB_NAME)
            coll = db.get_collection("digital_mind_models")
            raw_docs = await coll.find({}).to_list(length=200)
            transformed_models = []
            for doc in raw_docs:
                try:
                    # normalize _id
                    if "_id" in doc:
                        doc["_id"] = str(doc["_id"])  # not used by schema but keep for reference
                    transformed_models.append(transform_dmm_to_editor_profile(dict(doc)))
                except Exception:
                    # Skip documents that cannot be transformed
                    continue
            logger.info(f"Successfully retrieved {len(transformed_models)} model profiles (raw)")
            return transformed_models
        except PyMongoError as e:
            logger.error(f"Database error while retrieving all models (raw): {e}")
            raise HTTPException(status_code=500, detail="Database communication error.")
        except Exception as e:
            logger.error(f"Unexpected error while retrieving all models (raw): {e}")
            raise HTTPException(status_code=500, detail="An unexpected internal error occurred.")

@app.get(
    "/models/{model_id}/editor_profile", 
    response_model=DMMProfileSchema, 
    summary="Get Profile Data for UI Dashboard",
    description="Retrieves a processed and structured profile of the Digital Mind Model, specifically tailored for rendering in the frontend dashboard UI. This includes the character card and core stats.",
    tags=["Models"],
    dependencies=[Depends(get_api_key)]
)
async def get_editor_profile_data(model_id: str):
    """
    Retrieves and transforms the DMM data for the main dashboard view.
    - **model_id**: The unique identifier for the Digital Mind Model.
    - **Returns**: A `DMMProfileSchema` object containing the character card and core stats.
    - **Raises**: `HTTPException` with status 404 if the model is not found.
    """
    try:
        logger.info(f"Retrieving editor profile for model_id: {model_id}")
        dmm_document = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
        
        if not dmm_document:
            logger.warning(f"Editor profile request failed: DMM not found for model_id: {model_id}")
            raise HTTPException(status_code=404, detail=f"DigitalMindModel '{model_id}' not found.")
        
        # The transform function expects a dict, so we convert the Beanie doc.
        transformed_data = transform_dmm_to_editor_profile(dmm_document.model_dump())
        logger.info(f"Successfully retrieved and transformed profile for model_id: {model_id}")
        return transformed_data

    except PyMongoError as e:
        logger.error(f"Database error for model_id {model_id}: {e}")
        raise HTTPException(status_code=500, detail="Database communication error.")
    except HTTPException as he:
        # Let explicit HTTP errors (e.g., 404) propagate
        raise he
    except Exception as e:
        logger.error(f"Unexpected error for model_id {model_id}: {e}")
        raise HTTPException(status_code=500, detail="An unexpected internal error occurred.")

@app.get(
    "/models/{model_id}/full_profile", 
    response_model=DigitalMindModel, # Use the Beanie document model directly for the raw data
    response_model_by_alias=False, # Ensure PydanticObjectId is handled correctly
    summary="Get Full Raw Profile for Debugging",
    description="Retrieves the complete, raw DigitalMindModel document from the database. This is intended for debugging and development purposes.",
    tags=["Models"]
)
async def get_full_profile_data(model_id: str):
    """
    Retrieves the entire raw DMM document.
    - **model_id**: The unique identifier for the Digital Mind Model.
    - **Returns**: The raw `DigitalMindModel` document.
    - **Raises**: `HTTPException` with status 404 if the model is not found.
    """
    logger.info(f"Retrieving full profile for model_id: {model_id}")
    dmm_document = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
    
    if not dmm_document:
        logger.warning(f"Full profile request failed: DMM not found for model_id: {model_id}")
        raise HTTPException(status_code=404, detail=f"DigitalMindModel '{model_id}' not found.")
        
    logger.info(f"Successfully retrieved full profile for model_id: {model_id}")
    return dmm_document

@app.post(
    "/simulation/react", 
    response_model=ReactionSimulationResponse, 
    summary="Simulate a Reaction to a Stimulus",
    description="""
Simulates the Digital Mind Model's reaction to an external stimulus.
- **Processes**: The model's internal state is updated based on the stimulus.
- **Records**: A 'Kamma Log' entry is created to document the event.
- **Returns**: A status message and the created Kamma Log entry.
""",
    tags=["Simulation"]
)
async def simulate_character_reaction(request: ReactionRequest):
    """
    Processes a stimulus, updates the model's state, and logs the event.
    - **request**: A `ReactionRequest` object containing the model_id and stimulus details.
    - **Returns**: A `ReactionSimulationResponse` object.
    - **Raises**: `HTTPException` with status 404 if the model is not found, or 500 for other errors.
    """
    try:
        logger.info(f"Starting reaction simulation for model_id: {request.model_id}")
        # Normalize using pydantic v2 API with aliases to avoid attribute differences
        raw = request.model_dump(by_alias=True)
        model_id = raw.get("model_id") or getattr(request, "model_id", None)
        stim = raw.get("stimulus_object") or {}
        env = raw.get("environment_modifiers") or None
        # Build a lightweight object with required attributes to avoid strict re-validation edge cases
        from types import SimpleNamespace
        req_obj = SimpleNamespace(
            model_id=model_id,
            stimulus=SimpleNamespace(**(stim or {})),
            environment=SimpleNamespace(**(env or {})) if env is not None else None,
        )
        try:
            response_log_entry = await process_reaction_simulation(req_obj)  # type: ignore[arg-type]
        except Exception as svc_err:
            # Fallback: still create a minimal kamma log to avoid failing the request
            logger.error(
                f"Service error during reaction simulation for model_id {model_id}: {svc_err}. Falling back to minimal log entry."
            )
            # Ensure model exists
            dmm = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
            if not dmm:
                raise HTTPException(status_code=404, detail=f"DigitalMindModel '{model_id}' not found.")
            # Build and insert a basic log entry using provided stimulus
            stim_for_log = stim or {}
            if not model_id:
                raise HTTPException(status_code=400, detail="model_id is required")
            fallback_entry = KammaLogEntry(
                model_id=model_id,
                event_type="reaction",
                description="Reaction simulation (fallback)",
                impact_level=0,
                context={
                    "stimulus": stim_for_log,
                    "outcome": {"resulting_citta": "unknown", "is_wholesome": False, "conflict_analysis": {}},
                    "consequences": {},
                },
            )
            await fallback_entry.insert()
            response_log_entry = {
                "_id": str(getattr(fallback_entry, "id", "")),
                "model_id": model_id,
                "timestamp": fallback_entry.timestamp.isoformat() if getattr(fallback_entry, "timestamp", None) else None,
                "event_type": fallback_entry.event_type,
                "description": fallback_entry.description,
                "impact_level": fallback_entry.impact_level,
                "context": fallback_entry.context,
            }

        if response_log_entry is None:
            logger.warning(f"Reaction simulation failed: DMM not found for model_id: {request.model_id}")
            raise HTTPException(status_code=404, detail=f"DigitalMindModel '{request.model_id}' not found.")
        
        logger.info(f"Successfully completed reaction simulation for model_id: {request.model_id}")
        return {"status": "success", "log_entry": response_log_entry}

    except PyMongoError as e:
        logger.error(f"Database error during reaction simulation for model_id {request.model_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error during reaction simulation.")
    except Exception as e:
        # As a last resort, perform a minimal fallback without calling services
        try:
            raw = request.model_dump(by_alias=True)
            model_id = raw.get("model_id")
            if not model_id:
                raise HTTPException(status_code=400, detail="model_id is required")
            stim = raw.get("stimulus_object") or {}
            dmm = await DigitalMindModel.find_one(DigitalMindModel.model_id == model_id)
            if not dmm:
                raise HTTPException(status_code=404, detail=f"DigitalMindModel '{model_id}' not found.")
            fallback_entry = KammaLogEntry(
                model_id=model_id,
                event_type="reaction",
                description="Reaction simulation (final fallback)",
                impact_level=0,
                context={"stimulus": stim, "outcome": {}, "consequences": {}},
            )
            await fallback_entry.insert()
            log_entry = {
                "_id": str(getattr(fallback_entry, "id", "")),
                "model_id": model_id,
                "timestamp": fallback_entry.timestamp.isoformat() if getattr(fallback_entry, "timestamp", None) else None,
                "event_type": fallback_entry.event_type,
                "description": fallback_entry.description,
                "impact_level": fallback_entry.impact_level,
                "context": fallback_entry.context,
            }
            return {"status": "success", "log_entry": log_entry}
        except HTTPException:
            raise
        except Exception as final_err:
            logger.error(f"Unexpected error during reaction simulation for model_id {request.model_id}: {final_err}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred during reaction simulation.")

@app.get(
    "/models/{model_id}/kamma_log", 
    response_model=List[KammaLogEntrySchema], 
    summary="Get Kamma (Action) Log",
    description="Retrieves the kamma (action/reaction) history for a specific DigitalMindModel, sorted by most recent.",
    tags=["Logs"]
)
async def get_kamma_log(model_id: str):
    """
    Retrieves all kamma log entries for a given model.
    - **model_id**: The unique identifier for the Digital Mind Model.
    - **Returns**: A list of `KammaLogEntrySchema` objects.
    """
    try:
        logger.info(f"Retrieving kamma logs for model_id: {model_id}")
        logs = await KammaLogEntry.find(KammaLogEntry.model_id == model_id).sort("-timestamp").to_list()
        logger.info(f"Found {len(logs)} kamma logs for model_id: {model_id}")
        # Serialize to match KammaLogEntrySchema types (id, timestamp as strings)
        serialized = []
        for log in logs:
            serialized.append({
                "_id": str(getattr(log, "id", "")),
                "model_id": log.model_id,
                "timestamp": log.timestamp.isoformat() if hasattr(log, "timestamp") and log.timestamp else None,
                "event_type": getattr(log, "event_type", None),
                "description": getattr(log, "description", None),
                "impact_level": getattr(log, "impact_level", None),
                "context": getattr(log, "context", {}),
            })
        return serialized
    except PyMongoError as e:
        logger.error(f"Database error retrieving kamma logs for model_id {model_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error while retrieving kamma logs.")
    except Exception as e:
        logger.error(f"Unexpected error retrieving kamma logs for model_id {model_id}: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


# The TrainingLog schema is not yet defined in schemas.py, so this will be updated in a future step.
# For now, we will leave it as is.
@app.get(
    "/models/{model_id}/training_log", 
    response_model=List[TrainingLog], 
    summary="Get Training Log",
    description="Retrieves the complete training and cultivation history for a specific DigitalMindModel, showing how its parameters have evolved over time.",
    tags=["Logs"]
)
async def get_training_log(model_id: str):
    try:
        logger.info("Retrieving training logs", extra={"model_id": model_id})
        logs = await TrainingLog.find(TrainingLog.model_id == model_id).sort("-date").to_list()
        logger.info(f"Found {len(logs)} training logs", extra={"model_id": model_id, "count": len(logs)})
        return logs
    except PyMongoError as e:
        logger.error("Database error while retrieving training logs", extra={"model_id": model_id, "error": str(e)})
        raise HTTPException(status_code=500, detail="Database error while retrieving training logs.")
    except Exception as e:
        logger.error("Unexpected error while retrieving training logs", extra={"model_id": model_id, "error": str(e)})
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

@app.post("/models/{model_id}/cultivate", summary="DEPRECATED", include_in_schema=False)
async def cultivate_and_update_profile(model_id: str, request: CultivationRequest):
    logger.warning(f"Deprecated endpoint /models/{model_id}/cultivate accessed.")
    raise HTTPException(status_code=410, detail="This endpoint is deprecated and no longer functional.")


# --- Request ID middleware and metrics ---
# Prometheus metrics
REQUEST_COUNTER = Counter("http_requests_total", "Total HTTP requests", ["method", "path", "status"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "Request latency", ["method", "path"])

# System resource metrics
SYSTEM_CPU_USAGE = Gauge("system_cpu_percent", "System CPU usage percentage")
SYSTEM_MEMORY_USAGE = Gauge("system_memory_percent", "System memory usage percentage")
SYSTEM_DISK_USAGE = Gauge("system_disk_percent", "System disk usage percentage")

# Database metrics
DB_RESPONSE_TIME = Gauge("db_response_time_ms", "Database response time in milliseconds")
DB_CONNECTED = Gauge("db_connected", "Database connection status (1=connected, 0=disconnected)")
DB_COLLECTION_COUNT = Gauge("db_collection_count", "Number of database collections")

# Application metrics
APP_UPTIME_SECONDS = Gauge("app_uptime_seconds", "Application uptime in seconds")


# Duplicate security middleware removed - using SecurityHeadersMiddleware class above


@app.middleware("http")
async def add_request_id_and_metrics(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start = time.perf_counter()
    try:
        response: Response = await call_next(request)
    finally:
        duration = time.perf_counter() - start
        # Normalize path: avoid high-cardinality ids by stripping trailing object ids (basic heuristic)
        path = request.url.path
        norm_path = path
        # Record metrics
        try:
            REQUEST_LATENCY.labels(request.method, norm_path).observe(duration)
            REQUEST_COUNTER.labels(request.method, norm_path, str(getattr(response, "status_code", 500))).inc()
        except Exception:
            pass
    # Attach request id header
    if "X-Request-ID" not in response.headers:
        response.headers["X-Request-ID"] = request_id
    return response



@app.get("/metrics", include_in_schema=False)
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    import uvicorn
    # Pass app instance directly to avoid double import of main module when running as script
    uvicorn.run(app, host="0.0.0.0", port=8000)

