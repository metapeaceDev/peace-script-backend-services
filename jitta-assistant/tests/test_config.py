import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

from app.config import AppConfig, _get_bool, _get_int, _validate_path


class TestHelperFunctions:
    """Test helper functions for configuration parsing."""

    def test_get_bool_default_values(self):
        """Test _get_bool with default values."""
        assert _get_bool("NONEXISTENT_VAR", True) is True
        assert _get_bool("NONEXISTENT_VAR", False) is False

    def test_get_bool_valid_values(self):
        """Test _get_bool with valid environment values."""
        test_cases = [
            ("1", True),
            ("true", True),
            ("TRUE", True),
            ("yes", True),
            ("YES", True),
            ("y", True),
            ("Y", True),
            ("on", True),
            ("ON", True),
            ("0", False),
            ("false", False),
            ("FALSE", False),
            ("no", False),
            ("NO", False),
            ("n", False),
            ("N", False),
            ("off", False),
            ("OFF", False),
        ]

        for env_value, expected in test_cases:
            with patch.dict(os.environ, {"TEST_BOOL": env_value}):
                assert _get_bool("TEST_BOOL", False) == expected

    def test_get_bool_invalid_values(self):
        """Test _get_bool with invalid values falls back to default."""
        with patch.dict(os.environ, {"TEST_BOOL": "invalid"}):
            assert _get_bool("TEST_BOOL", True) is True
            assert _get_bool("TEST_BOOL", False) is False

    def test_get_int_default_values(self):
        """Test _get_int with default values."""
        assert _get_int("NONEXISTENT_VAR", 42) == 42

    def test_get_int_valid_values(self):
        """Test _get_int with valid values."""
        with patch.dict(os.environ, {"TEST_INT": "123"}):
            assert _get_int("TEST_INT", 0) == 123

    def test_get_int_invalid_values(self):
        """Test _get_int with invalid values falls back to default."""
        with patch.dict(os.environ, {"TEST_INT": "not_a_number"}):
            assert _get_int("TEST_INT", 42) == 42

    def test_get_int_with_constraints(self):
        """Test _get_int with min/max constraints."""
        with patch.dict(os.environ, {"TEST_INT": "0"}):
            assert _get_int("TEST_INT", 5, min_val=1, max_val=10) == 1

        with patch.dict(os.environ, {"TEST_INT": "15"}):
            assert _get_int("TEST_INT", 5, min_val=1, max_val=10) == 10

    def test_validate_path_valid(self):
        """Test _validate_path with valid paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir) / "test" / "subdir" / "file.txt"
            result = _validate_path(test_path, "test_path")
            assert result == test_path.resolve()
            assert result.parent.exists()

    def test_validate_path_invalid(self):
        """Test _validate_path with invalid paths raises ValueError."""
        invalid_path = Path("invalid-path")
        with patch("pathlib.Path.resolve", side_effect=OSError("resolve failed")):
            with pytest.raises(ValueError, match="Invalid path configuration"):
                _validate_path(invalid_path, "invalid_path")


class TestAppConfig:
    """Test AppConfig dataclass."""

    def test_default_initialization(self):
        """Test AppConfig with default values."""
        config = AppConfig()

        assert config.app_name == "Jitta"
        assert config.allow_shell_commands is False
        assert config.allow_web_access is True
        assert config.mock_llm is False
        assert config.rag_embed_device == "auto"
        assert config.rag_top_k == 4
        assert "http://" in config.fast_model_base_url
        assert "http://" in config.quality_model_base_url

    def test_environment_variable_override(self):
        """Test AppConfig with environment variables."""
        env_vars = {
            "APP_NAME": "TestApp",
            "JITTA_ALLOW_SHELL_COMMANDS": "true",
            "JITTA_ALLOW_WEB_ACCESS": "false",
            "MOCK_LLM": "true",
            "RAG_EMBED_DEVICE": "cuda",
            "RAG_TOP_K": "8",
            "FAST_LLM_BASE_URL": "http://test:8000/v1",
            "QUALITY_LLM_MODEL": "test-model",
        }

        # Clear environment first, then set test values
        with patch.dict(os.environ, {}, clear=True):
            with patch.dict(os.environ, env_vars):
                config = AppConfig()

                assert config.app_name == "TestApp"
                assert config.allow_shell_commands is True
                assert config.allow_web_access is False
                assert config.mock_llm is True
                assert config.rag_embed_device == "cuda"
                assert config.rag_top_k == 8
                assert config.fast_model_base_url == "http://test:8000/v1"
                assert config.quality_model_name == "test-model"

    def test_invalid_rag_embed_device_fallback_to_auto(self):
        """Test invalid RAG_EMBED_DEVICE falls back to auto."""
        env_vars = {
            "RAG_EMBED_DEVICE": "invalid-device",
        }

        with patch.dict(os.environ, env_vars):
            config = AppConfig()
            assert config.rag_embed_device == "auto"

    def test_path_validation(self):
        """Test path validation in __post_init__."""
        with tempfile.TemporaryDirectory() as temp_dir:
            env_vars = {
                "JITTA_ROOT_DIR": str(Path(temp_dir) / "root"),
                "JITTA_DATA_DIR": str(Path(temp_dir) / "data"),
            }

            with patch.dict(os.environ, env_vars):
                config = AppConfig()

                assert config.root_dir.exists()
                assert config.data_dir.exists()
                assert config.knowledge_dir == config.data_dir / "knowledge"
                assert config.chroma_dir == config.data_dir / "chroma"
                assert config.logs_dir == config.data_dir / "logs"

    def test_invalid_url_validation(self):
        """Test URL validation raises ValueError for invalid URLs."""
        env_vars = {
            "FAST_LLM_BASE_URL": "invalid-url",
        }

        with patch.dict(os.environ, env_vars):
            with pytest.raises(ValueError, match="Invalid FAST_LLM_BASE_URL"):
                AppConfig()

    def test_rag_top_k_constraints(self):
        """Test RAG_TOP_K constraints."""
        env_vars = {
            "RAG_TOP_K": "0",  # Below minimum
        }

        with patch.dict(os.environ, env_vars):
            config = AppConfig()
            assert config.rag_top_k == 1  # Should be clamped to minimum

        env_vars["RAG_TOP_K"] = "25"  # Above maximum
        with patch.dict(os.environ, env_vars):
            config = AppConfig()
            assert config.rag_top_k == 20  # Should be clamped to maximum

    def test_telegram_token_warning(self):
        """Test telegram token warning when not set and not in mock mode."""
        env_vars = {
            "TELEGRAM_BOT_TOKEN": "",
            "MOCK_LLM": "false",
        }

        with patch.dict(os.environ, env_vars):
            # Should not raise exception, just log warning
            config = AppConfig()
            assert config.telegram_bot_token == ""

    @pytest.mark.parametrize("rag_top_k,expected", [
        (1, 1),
        (10, 10),
        (20, 20),
    ])
    def test_rag_top_k_valid_range(self, rag_top_k, expected):
        """Test RAG_TOP_K with valid values."""
        env_vars = {
            "RAG_TOP_K": str(rag_top_k),
        }

        with patch.dict(os.environ, env_vars):
            config = AppConfig()
            assert config.rag_top_k == expected