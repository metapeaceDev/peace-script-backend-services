# Ensure workspace root is importable when running pytest from dmm_backend/
import os
import sys
from pathlib import Path

# Insert workspace root (parent of this directory) at the beginning of sys.path
_THIS_DIR = Path(__file__).resolve().parent
_WORKSPACE = _THIS_DIR.parent
if str(_WORKSPACE) not in sys.path:
    sys.path.insert(0, str(_WORKSPACE))

# Also ensure project dir itself is importable by name
if str(_THIS_DIR) not in sys.path:
    sys.path.append(str(_THIS_DIR))

# Minimal env defaults for tests
os.environ.setdefault("API_KEY", "test_api_key")
os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")
os.environ.setdefault("MONGODB_DB", "test_db")

# Import authentication fixtures for all tests
pytest_plugins = ["tests.fixtures.auth_fixtures"]
