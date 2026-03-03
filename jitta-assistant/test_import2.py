import sys
from pathlib import Path

# Add parent directory to path so we can import 'app'
# This mimics what ingest_planning_docs.py does
current_dir = Path(__file__).resolve().parent # jitta-assistant

try:
    with open("diagnostic.txt", "w") as f:
        f.write(f"CWD: {Path.cwd()}\n")
        f.write(f"sys.path: {sys.path}\n")
        try:
            import app
            f.write("Successfully imported app\n")
            from app.config import AppConfig
            f.write("Successfully imported AppConfig\n")
        except ImportError as e:
            f.write(f"ImportError: {e}\n")
        except Exception as e:
            f.write(f"Error: {e}\n")
except Exception as e:
    print(f"Failed to write diagnostic file: {e}")
