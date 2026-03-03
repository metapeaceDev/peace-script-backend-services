import logging
import tempfile
from pathlib import Path
from unittest.mock import patch

from app.logger import setup_logging, get_logger


class TestSetupLogging:
    """Test logging setup functionality."""

    def test_setup_logging_default(self):
        """Test setup_logging with default parameters."""
        setup_logging()

        logger = logging.getLogger()
        assert logger.level == logging.INFO
        assert len(logger.handlers) >= 1  # At least console handler

        # Check console handler
        console_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
        assert len(console_handlers) == 1

    def test_setup_logging_with_file(self):
        """Test setup_logging with file output."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            setup_logging(log_file=log_file)

            logger = logging.getLogger()
            assert len(logger.handlers) >= 2  # Console + file handlers

            # Check file handler
            file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
            assert len(file_handlers) == 1
            assert file_handlers[0].baseFilename == str(log_file)

    def test_setup_logging_without_console(self):
        """Test setup_logging without console output."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            setup_logging(console=False, log_file=log_file)

            logger = logging.getLogger()
            console_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
            assert len(console_handlers) == 0

            file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
            assert len(file_handlers) == 1

    def test_setup_logging_different_levels(self):
        """Test setup_logging with different log levels."""
        test_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        for level in test_levels:
            setup_logging(level=level)
            logger = logging.getLogger()
            expected_level = getattr(logging, level.upper())
            assert logger.level == expected_level

    def test_setup_logging_invalid_level(self):
        """Test setup_logging with invalid level defaults to INFO."""
        setup_logging(level="INVALID")
        logger = logging.getLogger()
        assert logger.level == logging.INFO

    def test_setup_logging_creates_log_directory(self):
        """Test that setup_logging creates parent directories for log file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "subdir" / "nested" / "test.log"
            setup_logging(log_file=log_file)

            assert log_file.parent.exists()
            assert log_file.parent.is_dir()

    def test_setup_logging_formatter(self):
        """Test that handlers have correct formatter."""
        setup_logging()

        logger = logging.getLogger()
        for handler in logger.handlers:
            assert handler.formatter is not None
            # Test formatter format
            record = logging.LogRecord(
                name="test", level=logging.INFO, pathname="", lineno=0,
                msg="test message", args=(), exc_info=None
            )
            formatted = handler.formatter.format(record)
            assert "INFO" in formatted
            assert "test" in formatted
            assert "test message" in formatted


class TestGetLogger:
    """Test get_logger functionality."""

    def test_get_logger_returns_logger_instance(self):
        """Test that get_logger returns a Logger instance."""
        logger = get_logger("test_logger")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"

    def test_get_logger_same_name_returns_same_instance(self):
        """Test that get_logger returns the same instance for same name."""
        logger1 = get_logger("test_logger")
        logger2 = get_logger("test_logger")
        assert logger1 is logger2

    def test_get_logger_different_names_different_instances(self):
        """Test that get_logger returns different instances for different names."""
        logger1 = get_logger("logger1")
        logger2 = get_logger("logger2")
        assert logger1 is not logger2
        assert logger1.name != logger2.name

    def test_get_logger_inherits_configuration(self):
        """Test that loggers inherit the root logger configuration."""
        setup_logging(level="DEBUG")

        logger = get_logger("test_logger")
        # Child loggers should inherit level from root if not explicitly set
        assert logger.getEffectiveLevel() == logging.DEBUG

    def test_get_logger_can_log(self):
        """Test that returned logger can actually log messages."""
        with patch('sys.stdout') as mock_stdout:
            setup_logging()
            logger = get_logger("test_logger")

            logger.info("Test message")
            # Verify that logging calls were made (exact output format may vary)
            mock_stdout.write.assert_called()

    def test_get_logger_with_file_output(self):
        """Test logger with file output."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            setup_logging(log_file=log_file)

            logger = get_logger("test_logger")
            logger.info("Test file message")

            # Check that file was created and contains the message
            assert log_file.exists()
            content = log_file.read_text(encoding="utf-8")
            assert "Test file message" in content
            assert "INFO" in content
            assert "test_logger" in content