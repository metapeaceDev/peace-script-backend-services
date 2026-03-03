from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator


class Settings(BaseSettings):
    """
    Centralized application settings.
    Settings are loaded from the .env file.
    """
    # App settings
    API_TITLE: str = "Digital Mind API"
    API_DESCRIPTION: str = "API for simulating and interacting with a Digital Mind Model."
    API_VERSION: str = "1.4.0"
    DEBUG_MODE: bool = False
    API_KEY: str = ""  # For API security (optional, defaults to empty)

    # Database
    # Primary names
    MONGO_URI: Optional[str] = "mongodb://localhost:27017"  # Default local
    MONGO_DB_NAME: str = "digital_mind_model"

    # Backward-compatible aliases (used by some tests/scripts)
    MONGODB_URI: Optional[str] = None
    MONGODB_DB: Optional[str] = None

    # CORS
    CORS_ORIGINS: str = (
        "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:5173,http://localhost:5174,http://localhost:5178,http://localhost:8000,"
        "http://127.0.0.1:5173,http://127.0.0.1:5174,http://127.0.0.1:5178,http://127.0.0.1:4173,http://127.0.0.1:3000,"
        "http://127.0.0.1:5181,http://127.0.0.1:5182,http://localhost:5181,http://localhost:5182"
    )

    # Optional DB/index policies
    KAMMA_TTL_SECONDS: Optional[int] = None  # e.g., 2592000 (30 days)
    UNIQUE_TIMELINE_PER_MODEL: bool = False
    USE_MOCK_DB: bool = True  # Reverted to True for Immediate Testing (Real DB requires Docker)

    def get_cors_origins(self) -> List[str]:
        """
        Parses the comma-separated string of origins from the .env file into a list of strings.
        """
        if isinstance(self.CORS_ORIGINS, str):
            return [i.strip() for i in self.CORS_ORIGINS.split(',')]
        return []

    @model_validator(mode="after")
    def _apply_aliases(self):
        """Ensure alias environment variables are honored if primary ones are not provided."""
        # Promote MONGODB_URI -> MONGO_URI when the primary is missing
        if not self.MONGO_URI and self.MONGODB_URI:
            self.MONGO_URI = self.MONGODB_URI

        # Promote MONGODB_DB -> MONGO_DB_NAME only if custom provided
        if self.MONGODB_DB:
            self.MONGO_DB_NAME = self.MONGODB_DB
        return self

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra='ignore')

# Create a single, reusable instance of the settings
settings = Settings()
