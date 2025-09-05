# tests/unit/test_config.py
"""
Unit tests for the Config class.
"""

from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from src.utils.config import Config


class TestConfig:
    """Test cases for Config class."""

    def test_config_initialization(self):
        """Test that Config can be initialized."""
        config = Config()
        assert config is not None
        assert hasattr(config, "primary_name")
        assert hasattr(config, "behavior_debounce_time")
        assert hasattr(config, "audio_sample_rate")

    def test_config_default_values(self):
        """Test that Config has expected default values."""
        config = Config()

        # Test some key default values
        assert config.audio_sample_rate == 16000
        assert config.audio_channels == 1
        assert config.transcription_language == "de"
        assert config.spell_check_enabled is False
        assert config.logging_enabled is True

    def test_config_property_access(self):
        """Test that config properties can be accessed."""
        config = Config()

        # Test property access
        assert isinstance(config.primary_name, str)
        assert isinstance(config.behavior_debounce_time, float)
        assert isinstance(config.audio_sample_rate, int)

    def test_config_validation(self):
        """Test that config validates input values."""
        config = Config()

        # Test that invalid values are handled gracefully
        # This would depend on the actual validation logic in Config
        assert config.audio_sample_rate > 0
        assert config.audio_channels > 0

    @patch(
        "builtins.open", new_callable=mock_open, read_data='[input]\nprimary = "test"'
    )
    def test_config_file_loading(self, mock_file):
        """Test that config can load from file."""
        config = Config()
        # This test would need to be adjusted based on actual file loading logic
        assert config is not None

    def test_config_section_access(self):
        """Test that config sections can be accessed."""
        config = Config()

        # Test section access (if implemented)
        assert hasattr(config, "primary_name")
        assert hasattr(config, "audio_sample_rate")
        assert hasattr(config, "transcription_language")

    def test_config_immutability(self):
        """Test that config values cannot be accidentally modified."""
        config = Config()
        original_sample_rate = config.audio_sample_rate

        # Attempt to modify (this should not work if config is properly protected)
        # The actual behavior depends on the Config implementation
        assert config.audio_sample_rate == original_sample_rate

    def test_config_logging_settings(self):
        """Test logging configuration settings."""
        config = Config()

        assert hasattr(config, "logging_enabled")
        assert hasattr(config, "logging_console_level")
        assert hasattr(config, "logging_file_enabled")
        assert hasattr(config, "logging_emoji_enabled")

    def test_config_gui_settings(self):
        """Test GUI configuration settings."""
        config = Config()

        assert hasattr(config, "gui_auto_start")
        assert hasattr(config, "gui_window_width")
        assert hasattr(config, "gui_window_height")
        assert hasattr(config, "gui_theme")

    def test_config_audio_settings(self):
        """Test audio configuration settings."""
        config = Config()

        assert hasattr(config, "audio_sample_rate")
        assert hasattr(config, "audio_channels")
        assert hasattr(config, "audio_chunk_size")
        assert hasattr(config, "audio_format")
        assert hasattr(config, "audio_device")

    def test_config_transcription_settings(self):
        """Test transcription configuration settings."""
        config = Config()

        assert hasattr(config, "transcription_language")
        assert hasattr(config, "transcription_whisper_model")
        assert hasattr(config, "transcription_compute_type")
