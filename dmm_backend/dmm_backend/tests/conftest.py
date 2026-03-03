import sys
import os
from typing import AsyncGenerator

# 1) Set test env vars BEFORE importing app/settings
os.environ["API_KEY"] = "test_api_key"
os.environ["MONGODB_URI"] = "mongodb://localhost:27017"
os.environ["MONGODB_DB"] = "test_db"

"""Test bootstrap: set env and import paths"""
# 2) Ensure import paths: workspace root first (for `import dmm_backend.*`), then project_root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
workspace_root = os.path.abspath(os.path.join(project_root, os.pardir))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)
if project_root not in sys.path:
    sys.path.append(project_root)
# Remove current working directory entry to avoid masking package import
try:
    while '' in sys.path:
        sys.path.remove('')
except ValueError:
    pass
# Also add src/ for editable-style package layout
src_path = os.path.join(project_root, "src")
if os.path.isdir(src_path) and src_path not in sys.path:
    sys.path.insert(0, src_path)

import importlib
import pytest
import pytest_asyncio
import mongomock_motor
import motor.motor_asyncio
from httpx import AsyncClient, ASGITransport
from beanie import init_beanie

# Pre-load package modules and register legacy aliases BEFORE other imports that rely on them
documents_module = importlib.import_module("dmm_backend.documents")
sys.modules.setdefault("documents", documents_module)

config_module = importlib.import_module("dmm_backend.config")
sys.modules.setdefault("config", config_module)

db_init_module = importlib.import_module("dmm_backend.db_init")
importlib.reload(db_init_module)
sys.modules.setdefault("db_init", db_init_module)

main_module = importlib.import_module("dmm_backend.main")
sys.modules.setdefault("main", main_module)

# Prefer package-qualified imports
from dmm_backend.main import app  # enforce package import so routers resolve consistently
# Import P0 documents from documents_extra (where they actually live)
from dmm_backend.documents_extra import (
    DreamJournal,
    SimulationTimeline,
)
# Import other documents from documents
from dmm_backend.documents import (
    DigitalMindModel,
    KammaLogEntry,
    TrainingLog,
)
# Import auth User model
from dmm_backend.auth.models import User
from dmm_backend.config import settings
from dmm_backend.db_init import init_db as bootstrap_db
import dmm_backend.database as database_module

# Shared mongomock client so all db interactions hit the same in-memory store
TEST_MONGO_CLIENT = mongomock_motor.AsyncMongoMockClient()


class _SingletonAsyncMongoMockClient(mongomock_motor.AsyncMongoMockClient):
    def __new__(cls, *args, **kwargs):
        return TEST_MONGO_CLIENT


motor.motor_asyncio.AsyncIOMotorClient = _SingletonAsyncMongoMockClient

# 3) Test data for DigitalMindModel
MOCK_DMM = {
    "model_id": "test_model_001",
    "name": "Test Model",
    "status_label": "Stable",
    "overall_level": 1,
    "level_progress_percent": 50.0,
    "image_url": "http://example.com/image.png",
    "core_state": {"level_progress": 50, "level_up_threshold": 1000},
    "conscious_profile": {
        "parami_potentials": [
            {"name": "Dana", "value": 70, "exp": 0, "level": 1},
            {"name": "Sila", "value": 80, "exp": 0, "level": 1},
        ]
    },
    "kamma_profile": {
        "latent_tendencies": [
            {"name": "Lobha", "value": 20},
            {"name": "Dosa", "value": 15},
        ]
    },
    "core_profile": {
        "psychological_matrix": {
            "vedana_tolerance_profile": {
                "mental_suffering_threshold": {"total_threshold": 10}
            },
            "latent_tendencies": {
                "anusaya_kilesa": {"patigha": {"level": 5, "value": 50}}
            },
        },
        "spiritual_assets": {
            "virtue_engine": {
                "sati_mastery": {"level": 5, "exp": 0},
                "panna_mastery": {"level": 5, "exp": 0},
                "paramī_portfolio": {
                    "perfections": {
                        "khanti": {"level": 5, "exp": 0},
                        "upekkha": {"level": 5, "exp": 0},
                    }
                },
            }
        },
    },
}


# 4) Initialize Beanie and prepare data per-test on the same loop
@pytest_asyncio.fixture(scope="function", autouse=True)
async def prepare_db() -> AsyncGenerator[None, None]:
    client = TEST_MONGO_CLIENT
    db_name = settings.MONGODB_DB or settings.MONGO_DB_NAME

    for doc in (DigitalMindModel, KammaLogEntry, TrainingLog, DreamJournal, SimulationTimeline, User):
        setattr(doc, "_document_settings", None)

    await client.drop_database(db_name)
    database_module._motor_client = client
    await bootstrap_db()
    await init_beanie(
        database=client.get_database(db_name),
        document_models=[DigitalMindModel, KammaLogEntry, TrainingLog, DreamJournal, SimulationTimeline, User],
    )

    # Clean collections and insert mock
    await KammaLogEntry.delete_all()
    await TrainingLog.delete_all()
    await DreamJournal.delete_all()
    await SimulationTimeline.delete_all()
    await DigitalMindModel.delete_all()
    await User.delete_all()
    await DigitalMindModel(**MOCK_DMM).insert()

    try:
        yield
    finally:
        # Cleanup
        await KammaLogEntry.delete_all()
        await TrainingLog.delete_all()
        await DreamJournal.delete_all()
        await SimulationTimeline.delete_all()
        await DigitalMindModel.delete_all()
        await User.delete_all()
        await client.drop_database(db_name)


# 5) Clear rate limit fixture
@pytest.fixture(autouse=True)
def clear_rate_limit():
    """Clear rate limit store before each test"""
    from core.rate_limiter import rate_limit_store
    rate_limit_store.clear()
    yield
    rate_limit_store.clear()


# 6) Async HTTP client against FastAPI app without startup lifespan
@pytest_asyncio.fixture(scope="function")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.headers["X-API-KEY"] = os.environ.get("API_KEY", "test_api_key")
        yield client
