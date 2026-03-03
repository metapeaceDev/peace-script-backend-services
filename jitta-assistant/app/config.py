from dataclasses import dataclass
import os
from pathlib import Path
from typing import Optional

from .logger import get_logger


logger = get_logger(__name__)


def _get_bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    val_lower = val.strip().lower()
    if val_lower in {"1", "true", "yes", "y", "on"}:
        return True
    elif val_lower in {"0", "false", "no", "n", "off"}:
        return False
    else:
        logger.warning(f"Invalid boolean value for {name}: {val}, using default {default}")
        return default


def _get_int(name: str, default: int, min_val: Optional[int] = None, max_val: Optional[int] = None) -> int:
    val = os.getenv(name)
    if val is None:
        return default
    try:
        int_val = int(val)
        if min_val is not None and int_val < min_val:
            logger.warning(f"Value for {name} too small: {int_val}, using {min_val}")
            return min_val
        if max_val is not None and int_val > max_val:
            logger.warning(f"Value for {name} too large: {int_val}, using {max_val}")
            return max_val
        return int_val
    except ValueError:
        logger.warning(f"Invalid integer value for {name}: {val}, using default {default}")
        return default


def _validate_path(path: Path, name: str) -> Path:
    """Validate and resolve path, creating parent directories if needed."""
    try:
        resolved = path.resolve()
        resolved.parent.mkdir(parents=True, exist_ok=True)
        return resolved
    except Exception as e:
        logger.error(f"Invalid path for {name}: {path}, error: {e}")
        raise ValueError(f"Invalid path configuration for {name}")


@dataclass
class AppConfig:
    """Application configuration loaded from environment variables."""

    def __post_init__(self):
        """Initialize configuration from environment variables."""
        # Application settings
        self.app_name = os.getenv("APP_NAME", "Jitta")
        self.root_dir = Path(os.getenv("JITTA_ROOT_DIR", os.getcwd()))
        self.data_dir = Path(os.getenv("JITTA_DATA_DIR", str(Path.cwd() / "data")))
        self.allow_shell_commands = _get_bool("JITTA_ALLOW_SHELL_COMMANDS", False)
        self.allow_web_access = _get_bool("JITTA_ALLOW_WEB_ACCESS", True)

        # Telegram settings
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.admin_chat_id = os.getenv("TELEGRAM_ADMIN_CHAT_ID", "")

        # LLM settings
        self.fast_model_base_url = os.getenv("FAST_LLM_BASE_URL", "http://127.0.0.1:8001/v1")
        self.fast_model_name = os.getenv("FAST_LLM_MODEL", "qwen3.5-14b-instruct")
        self.fast_model_api_key = os.getenv("FAST_LLM_API_KEY", "")

        self.quality_model_base_url = os.getenv("QUALITY_LLM_BASE_URL", "http://127.0.0.1:8002/v1")
        self.quality_model_name = os.getenv("QUALITY_LLM_MODEL", "qwen3.5-32b-instruct")
        self.quality_model_api_key = os.getenv("QUALITY_LLM_API_KEY", "")

        # RAG settings
        self.rag_embed_model = os.getenv(
            "RAG_EMBED_MODEL",
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        )
        self.rag_embed_device = os.getenv("RAG_EMBED_DEVICE", "auto").strip().lower()
        if self.rag_embed_device not in {"auto", "cpu", "cuda", "mps"}:
            logger.warning(
                f"Invalid RAG_EMBED_DEVICE: {self.rag_embed_device}, using auto"
            )
            self.rag_embed_device = "auto"
        self.rag_top_k = _get_int("RAG_TOP_K", 4, min_val=1, max_val=20)

        # Development settings
        self.mock_llm = _get_bool("MOCK_LLM", False)

        # Validate configuration after initialization
        # Validate paths
        self.root_dir = _validate_path(self.root_dir, "root_dir")
        self.data_dir = _validate_path(self.data_dir, "data_dir")
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Validate required settings
        if not self.telegram_bot_token and not self.mock_llm:
            logger.warning("TELEGRAM_BOT_TOKEN not set - Telegram bot will not work")

        # Validate URLs
        if not self.fast_model_base_url.startswith(("http://", "https://")):
            raise ValueError(f"Invalid FAST_LLM_BASE_URL: {self.fast_model_base_url}")
        if not self.quality_model_base_url.startswith(("http://", "https://")):
            raise ValueError(f"Invalid QUALITY_LLM_BASE_URL: {self.quality_model_base_url}")

        # Log configuration summary
        logger.info(f"Configuration loaded for {self.app_name}")
        logger.info(f"Root directory: {self.root_dir}")
        logger.info(f"Data directory: {self.data_dir}")
        logger.info(f"Mock mode: {self.mock_llm}")
        logger.info(f"Shell commands allowed: {self.allow_shell_commands}")
        logger.info(f"Web access allowed: {self.allow_web_access}")

    @property
    def knowledge_dir(self) -> Path:
        return self.data_dir / "knowledge"

    @property
    def chroma_dir(self) -> Path:
        return self.data_dir / "chroma"

    @property
    def logs_dir(self) -> Path:
        return self.data_dir / "logs"
