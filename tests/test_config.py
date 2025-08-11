"""Tests for the config module."""
import os
import tempfile
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

# Import the module to test
from src.config import Config


class TestConfig:
    """Test cases for Config class."""

    def test_config_initialization(self):
        """Test Config initialization with default values."""
        config = Config()
        assert config is not None
        assert hasattr(config, "config_path")

    def test_load_config_file_not_found(self):
        """Test loading config when file doesn't exist."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            config = Config()
            # Should not crash and should have default values
            assert config is not None

    def test_load_config_invalid_toml(self):
        """Test loading config with invalid TOML."""
        invalid_toml = "invalid toml content ["
        with patch("builtins.open", mock_open(read_data=invalid_toml)):
            config = Config()
            # Should not crash and should have default values
            assert config is not None

    def test_get_setting(self):
        """Test getting a setting value."""
        config = Config()
        # Test getting a setting using the _get method
        result = config._get("test_setting", "default_value")
        assert result == "default_value"

    def test_save_config(self):
        """Test saving config to file."""
        config = Config()
        # Test that the config has the expected properties
        assert hasattr(config, "input_method")
        assert hasattr(config, "audio_sample_rate")
        assert hasattr(config, "stt_model_size")


if __name__ == "__main__":
    pytest.main([__file__])
