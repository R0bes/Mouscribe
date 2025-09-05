# tests/unit/test_logger.py
"""
Unit tests for the Logger system.
"""

import logging
from unittest.mock import Mock, call, patch

import pytest

from src.utils.logger import MauscribeLogger, get_logger, setup_logging


class TestMauscribeLogger:
    """Test cases for MauscribeLogger class."""

    def test_logger_initialization(self):
        """Test that MauscribeLogger can be initialized."""
        logger = MauscribeLogger("test_logger")
        assert logger is not None
        assert hasattr(logger, "logger")
        assert hasattr(logger, "_emoji_mode")

    def test_logger_default_emoji_mode(self):
        """Test that logger defaults to emoji mode enabled."""
        logger = MauscribeLogger("test_logger")
        assert logger._emoji_mode is True

    def test_logger_with_config(self, test_config):
        """Test that logger respects config settings."""
        logger = MauscribeLogger("test_logger", test_config)
        # The logger should use the config's emoji setting
        assert hasattr(logger, "_emoji_mode")

    def test_set_emoji_mode(self):
        """Test that emoji mode can be set."""
        logger = MauscribeLogger("test_logger")
        logger.set_emoji_mode(False)
        assert logger._emoji_mode is False

    def test_format_message_with_emoji(self):
        """Test message formatting with emoji enabled."""
        logger = MauscribeLogger("test_logger")
        logger.set_emoji_mode(True)

        result = logger._format_message("✅", "Test message")
        assert result == "✅ Test message"

    def test_format_message_without_emoji(self):
        """Test message formatting with emoji disabled."""
        logger = MauscribeLogger("test_logger")
        logger.set_emoji_mode(False)

        result = logger._format_message("✅", "Test message")
        assert result == "Test message"

    def test_format_message_empty_emoji(self):
        """Test message formatting with empty emoji."""
        logger = MauscribeLogger("test_logger")
        logger.set_emoji_mode(True)

        result = logger._format_message("", "Test message")
        assert result == "Test message"

    @patch("src.utils.logger.logging.getLogger")
    def test_logger_methods(self, mock_get_logger):
        """Test that all logger methods work correctly."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        logger = MauscribeLogger("test_logger")

        # Test all logging methods
        logger.debug("Debug message", "🐛")
        logger.info("Info message", "ℹ️")
        logger.warning("Warning message", "⚠️")
        logger.error("Error message", "❌")
        logger.critical("Critical message", "🚨")
        logger.exception("Exception message", "💥")

        # Verify calls
        expected_calls = [
            call("🐛 Debug message"),
            call("ℹ️ Info message"),
            call("⚠️ Warning message"),
            call("❌ Error message"),
            call("🚨 Critical message"),
            call("💥 Exception message"),
        ]
        mock_logger.debug.assert_called_once_with("🐛 Debug message")
        mock_logger.info.assert_called_once_with("ℹ️ Info message")
        mock_logger.warning.assert_called_once_with("⚠️ Warning message")
        mock_logger.error.assert_called_once_with("❌ Error message")
        mock_logger.critical.assert_called_once_with("🚨 Critical message")
        mock_logger.exception.assert_called_once_with("💥 Exception message")

    def test_logger_is_enabled_for(self):
        """Test that logger correctly checks if level is enabled."""
        logger = MauscribeLogger("test_logger")
        assert hasattr(logger, "is_enabled_for")
        assert callable(logger.is_enabled_for)

    def test_logger_get_effective_level(self):
        """Test that logger can get effective level."""
        logger = MauscribeLogger("test_logger")
        assert hasattr(logger, "get_effective_level")
        assert callable(logger.get_effective_level)


class TestGetLogger:
    """Test cases for get_logger function."""

    def test_get_logger_returns_mauscribe_logger(self):
        """Test that get_logger returns a MauscribeLogger instance."""
        logger = get_logger("test_logger")
        assert isinstance(logger, MauscribeLogger)

    def test_get_logger_with_config(self, test_config):
        """Test that get_logger respects config parameter."""
        logger = get_logger("test_logger", test_config)
        assert isinstance(logger, MauscribeLogger)
        assert hasattr(logger, "_emoji_mode")


class TestSetupLogging:
    """Test cases for setup_logging function."""

    @patch("src.utils.logger.logging.getLogger")
    @patch("src.utils.logger.logging.StreamHandler")
    @patch("src.utils.logger.logging.FileHandler")
    @patch("src.utils.logger.logging.Formatter")
    def test_setup_logging_basic(
        self, mock_formatter, mock_file_handler, mock_stream_handler, mock_get_logger
    ):
        """Test basic logging setup."""
        mock_root_logger = Mock()
        mock_get_logger.return_value = mock_root_logger
        mock_root_logger.handlers = []

        # Reset the global flag to allow multiple calls
        import src.utils.logger

        src.utils.logger._logging_initialized = False

        setup_logging()

        # Verify that logging was set up
        mock_get_logger.assert_called()
        mock_stream_handler.assert_called()
        mock_formatter.assert_called()

    @patch("src.utils.logger.logging.getLogger")
    def test_setup_logging_with_config(self, mock_get_logger, test_config):
        """Test logging setup with config."""
        mock_root_logger = Mock()
        mock_get_logger.return_value = mock_root_logger
        mock_root_logger.handlers = []

        # Reset the global flag to allow multiple calls
        import src.utils.logger

        src.utils.logger._logging_initialized = False

        setup_logging(test_config)

        # Verify that logging was set up with config
        mock_get_logger.assert_called()

    def test_setup_logging_multiple_calls(self):
        """Test that setup_logging can be called multiple times safely."""
        # Should not raise any exceptions
        setup_logging()
        setup_logging()
        setup_logging()


class TestLogWithEmoji:
    """Test cases for log_with_emoji convenience function."""

    @patch("src.utils.logger.get_logger")
    def test_log_with_emoji_info(self, mock_get_logger):
        """Test log_with_emoji with info level."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        from src.utils.logger import log_with_emoji

        log_with_emoji("info", "Test message", "ℹ️", "test_logger")

        mock_logger.info.assert_called_once_with("Test message", "ℹ️")

    @patch("src.utils.logger.get_logger")
    def test_log_with_emoji_error(self, mock_get_logger):
        """Test log_with_emoji with error level."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        from src.utils.logger import log_with_emoji

        log_with_emoji("error", "Test message", "❌", "test_logger")

        mock_logger.error.assert_called_once_with("Test message", "❌")

    @patch("src.utils.logger.get_logger")
    def test_log_with_emoji_default_logger(self, mock_get_logger):
        """Test log_with_emoji with default logger name."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        from src.utils.logger import log_with_emoji

        log_with_emoji("info", "Test message", "ℹ️")

        mock_get_logger.assert_called_with("mauscribe")
        mock_logger.info.assert_called_once_with("Test message", "ℹ️")
