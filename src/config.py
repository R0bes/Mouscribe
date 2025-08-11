# src/config.py - Configuration management for Mauscribe
"""
Configuration loading and management for Mauscribe application.
Handles TOML configuration file loading with sensible defaults.
"""

import tomllib
from pathlib import Path
from typing import Any, Dict, List, Optional


class Config:
    """Configuration manager for Mauscribe application."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration with optional custom path."""
        self.config_path = config_path or "config.toml"
        self._config_data = {}
        self._load_config()

    def _load_config(self):
        """Load configuration from TOML file with fallback defaults."""
        try:
            with open(self.config_path, "rb") as f:
                self._config_data = tomllib.load(f)
            print(f"Configuration loaded from {self.config_path}")
        except FileNotFoundError:
            print(f"Configuration file {self.config_path} not found, using defaults")
            self._config_data = {}
        except Exception as e:
            print(f"Error loading configuration: {e}, using defaults")
            self._config_data = {}

    def _get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot notation support."""
        keys = key.split(".")
        value = self._config_data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    @property
    def input_method(self) -> str:
        """Get input method configuration."""
        return self._get("input.method", "mouse_button")

    @property
    def mouse_button_primary(self) -> str:
        """Get primary mouse button configuration."""
        return self._get("mouse_button.primary", "x2")

    @property
    def mouse_button_secondary(self) -> str:
        """Get secondary mouse button configuration."""
        return self._get("mouse_button.secondary", "x1")

    @property
    def mouse_button_left_with_ctrl(self) -> bool:
        """Get left mouse button with Ctrl configuration."""
        return self._get("mouse_button.left_with_ctrl", True)

    @property
    def keyboard_primary(self) -> str:
        """Get primary keyboard shortcut."""
        return self._get("keyboard.primary", "f8")

    @property
    def keyboard_secondary(self) -> str:
        """Get secondary keyboard shortcut."""
        return self._get("keyboard.secondary", "f9")

    @property
    def custom_combinations(self) -> List[Dict[str, Any]]:
        """Get custom key combinations."""
        return self._get("custom.combinations", [])

    @property
    def audio_sample_rate(self) -> int:
        """Get audio sample rate."""
        return self._get("audio.sample_rate", 16000)

    @property
    def audio_channels(self) -> int:
        """Get audio channel count."""
        return self._get("audio.channels", 1)

    @property
    def audio_device(self) -> Optional[int]:
        """Get audio device ID."""
        return self._get("audio.device", None)

    @property
    def stt_model_size(self) -> str:
        """Get STT model size."""
        return self._get("stt.model_size", "base")

    @property
    def stt_compute_type(self) -> str:
        """Get STT compute type."""
        return self._get("stt.compute_type", "int8")

    @property
    def stt_language(self) -> str:
        """Get STT language."""
        return self._get("stt.language", "de")

    @property
    def behavior_add_space_after_text(self) -> bool:
        """Get behavior for adding space after text."""
        return self._get("behavior.add_space_after_text", True)

    @property
    def behavior_auto_paste_after_transcription(self) -> bool:
        """Get auto-paste behavior setting."""
        return self._get("behavior.auto_paste_after_transcription", False)

    @property
    def behavior_paste_double_click_window(self) -> float:
        """Get double-click window for paste functionality."""
        return self._get("behavior.paste_double_click_window", 5.0)

    @property
    def cursor_enable(self) -> bool:
        """Get cursor feedback enable setting."""
        return self._get("cursor.enable", False)

    @property
    def cursor_recording_type(self) -> str:
        """Get cursor type during recording."""
        return self._get("cursor.recording_type", "cross")

    @property
    def system_volume_reduction_factor(self) -> float:
        """Get volume reduction factor."""
        return self._get("system.volume_reduction_factor", 0.3)

    @property
    def system_min_volume_percent(self) -> int:
        """Get minimum volume percentage."""
        return self._get("system.min_volume_percent", 10)

    @property
    def spell_check_enabled(self) -> bool:
        """Get spell check enabled setting."""
        return self._get("spell_check.enabled", True)

    @property
    def spell_check_language(self) -> str:
        """Get spell check language setting."""
        return self._get("spell_check.language", "de")

    @property
    def spell_check_grammar(self) -> bool:
        """Get grammar check enabled setting."""
        return self._get("spell_check.grammar_check", True)

    @property
    def spell_check_auto_correct(self) -> bool:
        """Get auto-correct enabled setting."""
        return self._get("spell_check.auto_correct", True)

    @property
    def spell_check_suggest_only(self) -> bool:
        """Get suggest-only mode setting."""
        return self._get("spell_check.suggest_only", False)

    @property
    def custom_dictionary_enabled(self) -> bool:
        """Get custom dictionary enabled setting."""
        return self._get("custom_dictionary.enabled", True)

    @property
    def custom_dictionary_auto_add_unknown(self) -> bool:
        """Get auto-add unknown words setting."""
        return self._get("custom_dictionary.auto_add_unknown", False)

    @property
    def custom_dictionary_path(self) -> Optional[str]:
        """Get custom dictionary path setting."""
        path = self._get("custom_dictionary.path", "")
        return path if path else None

    @property
    def custom_dictionary_max_words(self) -> int:
        """Get maximum words in dictionary setting."""
        return self._get("custom_dictionary.max_words", 1000)

    @property
    def debug_enabled(self) -> bool:
        """Get debug mode setting."""
        return self._get("debug.enabled", False)

    @property
    def debug_level(self) -> str:
        """Get debug log level."""
        return self._get("debug.level", "INFO")

    @property
    def volume_reduction_factor(self) -> float:
        """Get volume reduction factor (alias for system setting)."""
        return self.system_volume_reduction_factor

    @property
    def min_volume_percent(self) -> int:
        """Get minimum volume percentage (alias for system setting)."""
        return self.system_min_volume_percent
