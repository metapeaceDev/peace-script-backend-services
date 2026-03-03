import sys
from pathlib import Path
print(f"CWD: {Path.cwd()}")
print(f"sys.path: {sys.path}")
try:
    import app
    print("Successfully imported app")
    from app.config import AppConfig
    print("Successfully imported AppConfig")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
