# src/config.py - Configuration management for Mauscribe
"""
Configuration loading and management for Mauscribe application.
Handles TOML configuration file loading with sensible defaults.
"""

import tomllib
from typing import Any, Dict, List, Optional

from .logger import get_logger


class Config:
    """Configuration manager for Mauscribe application."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration with optional custom path."""
        self.logger = get_logger(self.__class__.__name__)
        self.config_path = config_path or "config.toml"
        self.logger.debug(f"self.config_path loaded from {self.config_path}")
        self._config_data: dict[str, Any] = {}
        self._load_config()

    def _load_config(self):
        """Load configuration from TOML file with fallback defaults."""
        try:
            with open(self.config_path, "rb") as f:
                self._config_data = tomllib.load(f)
            self.logger.debug(f"Configuration loaded from {self.config_path}")
        except FileNotFoundError:
            self.logger.info(f"Configuration file {self.config_path} not found, using defaults")
            self._config_data = {}
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}, using defaults")
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
    def custom_combinations(self) -> list[dict[str, Any]]:
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
    def audio_device_name(self) -> Optional[str]:
        """Get audio device name preference."""
        return self._get("audio.device_name", None)

    @property
    def audio_auto_select_device(self) -> bool:
        """Get whether to automatically select the best audio device."""
        return self._get("audio.auto_select_device", True)

    @property
    def audio_test_device_on_startup(self) -> bool:
        """Get whether to test audio device on startup."""
        return self._get("audio.test_device_on_startup", True)

    @property
    def audio_fallback_to_default(self) -> bool:
        """Get whether to fallback to default device if selected device fails."""
        return self._get("audio.fallback_to_default", True)

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
        """Get volume reduction factor."""
        return self._get("system.volume_reduction_factor", 0.15)

    @property
    def min_volume_percent(self) -> int:
        """Get minimum volume percentage."""
        return self._get("system.min_volume_percent", 5)

    @property
    def recording_timeout_seconds(self) -> int:
        """Get recording timeout in seconds."""
        return self._get("recording.timeout_seconds", 60)

    @property
    def auto_update_enabled(self) -> bool:
        """Get auto-update enabled setting."""
        return self._get("auto_update.enabled", True)

    @property
    def auto_update_check_interval(self) -> Optional[int]:
        """Get auto-update check interval in seconds."""
        return self._get("auto_update.check_interval", 86400)  # 24 hours

    @property
    def auto_update_check_on_startup(self) -> bool:
        """Get check for updates on startup setting."""
        return self._get("auto_update.check_on_startup", True)

    @property
    def auto_update_auto_install(self) -> bool:
        """Get auto-install updates setting."""
        return self._get("auto_update.auto_install", False)

    @property
    def auto_update_include_prereleases(self) -> bool:
        """Get include pre-releases setting."""
        return self._get("auto_update.include_prereleases", False)

    # Windows notification settings
    @property
    def notifications_enabled(self) -> bool:
        """Get whether Windows notifications are enabled."""
        return self._get("notifications.enabled", True)

    @property
    def notifications_duration(self) -> int:
        """Get notification display duration in milliseconds."""
        return self._get("notifications.duration", 5000)

    @property
    def notifications_sound(self) -> bool:
        """Get whether notification sounds are enabled."""
        return self._get("notifications.sound", True)

    @property
    def notifications_toast(self) -> bool:
        """Get whether toast notifications are enabled."""
        return self._get("notifications.toast", True)

    @property
    def notifications_show_startup(self) -> bool:
        """Get whether to show startup notification."""
        return self._get("notifications.show_startup", True)

    @property
    def notifications_show_shutdown(self) -> bool:
        """Get whether to show shutdown notification."""
        return self._get("notifications.show_shutdown", True)

    @property
    def notifications_show_recording_events(self) -> bool:
        """Get whether to show recording start/stop notifications."""
        return self._get("notifications.show_recording_events", True)

    @property
    def notifications_show_transcription_events(self) -> bool:
        """Get whether to show transcription complete notifications."""
        return self._get("notifications.show_transcription_events", True)

    @property
    def notifications_show_text_events(self) -> bool:
        """Get whether to show text paste notifications."""
        return self._get("notifications.show_text_events", True)

    @property
    def notifications_show_spell_check_events(self) -> bool:
        """Get whether to show spell check complete notifications."""
        return self._get("notifications.show_spell_check_events", True)

    @property
    def notifications_show_errors(self) -> bool:
        """Get whether to show error notifications."""
        return self._get("notifications.show_errors", True)

    @property
    def notifications_show_warnings(self) -> bool:
        """Get whether to show warning notifications."""
        return self._get("notifications.show_warnings", True)

    # Database properties
    @property
    def database_enabled(self) -> bool:
        """Get database enabled setting."""
        return self._get("database.enabled", True)

    @property
    def data_directory(self) -> str:
        """Get data directory path."""
        return self._get("database.data_directory", "")

    @property
    def audio_format(self) -> str:
        """Get audio format for storage."""
        return self._get("database.audio_format", "wav")

    @property
    def auto_save_recordings(self) -> bool:
        """Get auto-save recordings setting."""
        return self._get("database.auto_save_recordings", True)

    @property
    def auto_save_transcriptions(self) -> bool:
        """Get auto-save transcriptions setting."""
        return self._get("database.auto_save_transcriptions", True)

    @property
    def mark_as_training_data(self) -> bool:
        """Get mark as training data setting."""
        return self._get("database.mark_as_training_data", True)

    @property
    def retention_days(self) -> int:
        """Get retention period in days."""
        return self._get("database.retention_days", 30)

    @property
    def max_database_size_mb(self) -> int:
        """Get maximum database size in MB."""
        return self._get("database.max_database_size_mb", 1000)

    @property
    def compress_audio(self) -> bool:
        """Get audio compression setting."""
        return self._get("database.compress_audio", False)

    @property
    def backup_before_cleanup(self) -> bool:
        """Get backup before cleanup setting."""
        return self._get("database.backup_before_cleanup", True)

    # Behavior properties
    @property
    def auto_paste_after_transcription(self) -> bool:
        """Get auto-paste after transcription setting."""
        return self._get("behavior.auto_paste_after_transcription", True)

    # Input filter properties
    @property
    def input_filter_primary_mode(self) -> str:
        """Get input filter mode for primary button."""
        return self._get("input_filter.primary_mode", "single_click")

    @property
    def input_filter_secondary_mode(self) -> str:
        """Get input filter mode for secondary button."""
        return self._get("input_filter.secondary_mode", "hold")

    @property
    def input_filter_hold_duration(self) -> float:
        """Get hold duration for hold mode in seconds."""
        return self._get("input_filter.hold_duration", 0.5)

    @property
    def input_filter_double_click_window(self) -> float:
        """Get double click window in seconds."""
        return self._get("input_filter.double_click_window", 0.5)

    @property
    def input_filter_smart_delay(self) -> float:
        """Get smart delay in seconds."""
        return self._get("input_filter.smart_delay", 0.2)

    # STT properties
    @property
    def stt_model(self) -> str:
        """Get STT model size setting."""
        return self._get("stt.model", "medium")
