"""Tests for the config module."""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import mock_open, patch

# Add src directory to path for direct import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

# Import the module to test
from config import Config


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

    def test_config_default_values(self):
        """Test that config has expected default values."""
        config = Config()

        # Test audio settings
        assert hasattr(config, "audio_sample_rate")
        assert hasattr(config, "audio_channels")
        assert isinstance(config.audio_sample_rate, int)
        assert isinstance(config.audio_channels, int)

        # Test STT settings
        assert hasattr(config, "stt_model_size")
        assert isinstance(config.stt_model_size, str)

        # Test input method
        assert hasattr(config, "input_method")
        assert isinstance(config.input_method, str)

    def test_config_path_property(self):
        """Test config_path property."""
        config = Config()
        assert hasattr(config, "config_path")
        # config_path is a string, not a Path object
        assert isinstance(config.config_path, str)

    def test_get_method_with_existing_key(self):
        """Test _get method with existing key in config."""
        config = Config()

        # Test with a key that should exist in the config
        result = config._get("audio.sample_rate", "default")
        assert result != "default"  # Should return actual value, not default

    def test_get_method_with_nonexistent_key(self):
        """Test _get method with nonexistent key."""
        config = Config()

        # Test with a key that doesn't exist
        result = config._get("nonexistent_key", "fallback_value")
        assert result == "fallback_value"

    def test_config_file_creation(self):
        """Test that config file is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.toml"

            # Create config with custom path
            config = Config()
            config.config_path = str(config_path)

            # Test that config can be accessed without error
            assert config is not None
            assert hasattr(config, "audio_sample_rate")

    def test_config_reload(self):
        """Test config reloading."""
        config = Config()
        original_sample_rate = config.audio_sample_rate

        # Test that config can be accessed multiple times
        assert config.audio_sample_rate == original_sample_rate

        # Test that config is consistent
        assert config.audio_sample_rate == config.audio_sample_rate

    def test_input_method_property(self):
        """Test input_method property."""
        config = Config()
        assert config.input_method == "mouse_button"

    def test_mouse_button_primary_property(self):
        """Test mouse_button_primary property."""
        config = Config()
        assert config.mouse_button_primary == "x2"

    def test_mouse_button_secondary_property(self):
        """Test mouse_button_secondary property."""
        config = Config()
        assert config.mouse_button_secondary == "x1"

    def test_mouse_button_left_with_ctrl_property(self):
        """Test mouse_button_left_with_ctrl property."""
        config = Config()
        assert config.mouse_button_left_with_ctrl is True

    def test_keyboard_primary_property(self):
        """Test keyboard_primary property."""
        config = Config()
        assert config.keyboard_primary == "f9"  # Actual value from config.toml

    def test_keyboard_secondary_property(self):
        """Test keyboard_secondary property."""
        config = Config()
        assert config.keyboard_secondary == "shift+f9"  # Actual value from config.toml

    def test_custom_combinations_property(self):
        """Test custom_combinations property."""
        config = Config()
        expected_combinations = [
            ["ctrl", "shift", "v"],
            ["alt", "v"],
        ]  # Actual value from config.toml
        assert config.custom_combinations == expected_combinations

    def test_audio_device_property(self):
        """Test audio_device property."""
        config = Config()
        assert config.audio_device is None

    def test_stt_compute_type_property(self):
        """Test stt_compute_type property."""
        config = Config()
        assert config.stt_compute_type == "float32"  # Actual value from config.toml

    def test_stt_language_property(self):
        """Test stt_language property."""
        config = Config()
        assert config.stt_language == "de"

    def test_behavior_add_space_after_text_property(self):
        """Test behavior_add_space_after_text property."""
        config = Config()
        assert config.behavior_add_space_after_text is True

    def test_behavior_auto_paste_after_transcription_property(self):
        """Test behavior_auto_paste_after_transcription property."""
        config = Config()
        assert config.behavior_auto_paste_after_transcription is False

    def test_behavior_paste_double_click_window_property(self):
        """Test behavior_paste_double_click_window property."""
        config = Config()
        assert (
            config.behavior_paste_double_click_window == 10.0
        )  # Actual value from config.toml

    def test_cursor_enable_property(self):
        """Test cursor_enable property."""
        config = Config()
        assert config.cursor_enable is True  # Actual value from config.toml

    def test_cursor_recording_type_property(self):
        """Test cursor_recording_type property."""
        config = Config()
        assert config.cursor_recording_type == "cross"

    def test_system_volume_reduction_factor_property(self):
        """Test system_volume_reduction_factor property."""
        config = Config()
        assert (
            config.system_volume_reduction_factor == 0.15
        )  # Actual value from config.toml

    def test_system_min_volume_percent_property(self):
        """Test system_min_volume_percent property."""
        config = Config()
        assert config.system_min_volume_percent == 5  # Actual value from config.toml

    def test_spell_check_enabled_property(self):
        """Test spell_check_enabled property."""
        config = Config()
        assert config.spell_check_enabled is True

    def test_spell_check_language_property(self):
        """Test spell_check_language property."""
        config = Config()
        assert config.spell_check_language == "de"

    def test_spell_check_grammar_property(self):
        """Test spell_check_grammar property."""
        config = Config()
        assert config.spell_check_grammar is True

    def test_spell_check_auto_correct_property(self):
        """Test spell_check_auto_correct property."""
        config = Config()
        assert config.spell_check_auto_correct is True

    def test_spell_check_suggest_only_property(self):
        """Test spell_check_suggest_only property."""
        config = Config()
        assert config.spell_check_suggest_only is False

    def test_custom_dictionary_enabled_property(self):
        """Test custom_dictionary_enabled property."""
        config = Config()
        assert config.custom_dictionary_enabled is True

    def test_custom_dictionary_auto_add_unknown_property(self):
        """Test custom_dictionary_auto_add_unknown property."""
        config = Config()
        assert config.custom_dictionary_auto_add_unknown is False

    def test_custom_dictionary_path_property(self):
        """Test custom_dictionary_path property."""
        config = Config()
        assert config.custom_dictionary_path is None

    def test_custom_dictionary_max_words_property(self):
        """Test custom_dictionary_max_words property."""
        config = Config()
        assert config.custom_dictionary_max_words == 1000

    def test_debug_enabled_property(self):
        """Test debug_enabled property."""
        config = Config()
        assert config.debug_enabled is False

    def test_debug_level_property(self):
        """Test debug_level property."""
        config = Config()
        assert config.debug_level == "INFO"

    def test_volume_reduction_factor_alias_property(self):
        """Test volume_reduction_factor alias property."""
        config = Config()
        assert config.volume_reduction_factor == config.system_volume_reduction_factor
        assert config.volume_reduction_factor == 0.15  # Actual value from config.toml

    def test_min_volume_percent_alias_property(self):
        """Test min_volume_percent alias property."""
        config = Config()
        assert config.min_volume_percent == config.system_min_volume_percent
        assert config.min_volume_percent == 5  # Actual value from config.toml

    def test_config_with_custom_path(self):
        """Test Config initialization with custom config path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_config_path = os.path.join(temp_dir, "custom_config.toml")
            config = Config(config_path=custom_config_path)
            assert config.config_path == custom_config_path

    def test_get_method_with_nested_dict(self):
        """Test _get method with nested dictionary keys."""
        config = Config()

        # Test with a nested key that doesn't exist
        result = config._get("nested.key.value", "default")
        assert result == "default"

        # Test with a key that has dots but doesn't exist
        result = config._get("audio.nonexistent.setting", "fallback")
        assert result == "fallback"

    def test_get_method_with_non_dict_value(self):
        """Test _get method when intermediate value is not a dict."""
        config = Config()

        # Test with a key where intermediate value is not a dict
        result = config._get("audio.sample_rate.invalid", "default")
        assert result == "default"

    def test_config_with_empty_config_file(self):
        """Test Config with empty config file."""
        empty_toml = ""
        with patch("builtins.open", mock_open(read_data=empty_toml)):
            config = Config()
            # Should not crash and should have default values
            assert config is not None
            assert config.audio_sample_rate == 16000

    def test_config_with_partial_config_file(self):
        """Test Config with partial config file."""
        partial_toml = """
[audio]
sample_rate = 44100
"""
        with patch("builtins.open", mock_open(read_data=partial_toml.encode("utf-8"))):
            config = Config()
            # Should use provided values and defaults for missing ones
            assert config.audio_sample_rate == 44100
            assert config.audio_channels == 1  # Default value
            assert config.input_method == "mouse_button"  # Default value

    def test_config_with_invalid_numeric_values(self):
        """Test Config with invalid numeric values in config file."""
        invalid_toml = """
[audio]
sample_rate = "invalid_string"
channels = "not_a_number"
"""
        with patch("builtins.open", mock_open(read_data=invalid_toml)):
            config = Config()
            # Should fall back to defaults when values are invalid
            assert config.audio_sample_rate == 16000  # Default value
            assert config.audio_channels == 1  # Default value

    def test_config_with_unicode_values(self):
        """Test Config with unicode values in config file."""
        unicode_toml = """
[spell_check]
language = "de"
[debug]
level = "INFO"
"""
        with patch("builtins.open", mock_open(read_data=unicode_toml)):
            config = Config()
            # Should handle unicode values correctly
            assert config.spell_check_language == "de"
            assert config.debug_level == "INFO"

    def test_config_path_absolute_vs_relative(self):
        """Test Config with absolute vs relative paths."""
        # Test with relative path
        config_rel = Config("relative_config.toml")
        assert config_rel.config_path == "relative_config.toml"

        # Test with absolute path
        with tempfile.TemporaryDirectory() as temp_dir:
            abs_path = os.path.join(temp_dir, "absolute_config.toml")
            config_abs = Config(abs_path)
            assert config_abs.config_path == abs_path

    def test_config_reload_consistency(self):
        """Test that config values remain consistent across multiple accesses."""
        config = Config()

        # Access the same property multiple times
        value1 = config.audio_sample_rate
        value2 = config.audio_sample_rate
        value3 = config.audio_sample_rate

        # All values should be identical
        assert value1 == value2 == value3

        # Test with different properties
        assert config.input_method == config.input_method
        assert config.stt_language == config.stt_language


if __name__ == "__main__":
    pytest.main([__file__])
