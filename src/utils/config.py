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
            self.logger.info(
                f"Configuration file {self.config_path} not found, using defaults"
            )
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

    # Primary and Secondary button properties
    @property
    def primary_name(self) -> str:
        """Get primary button name."""
        return self._get("primary.name", "m_x2")

    @property
    def primary_type(self) -> str:
        """Get primary button type."""
        return self._get("primary.type", "mouse_button")

    @property
    def primary_method(self) -> dict:
        """Get primary button method configuration."""
        return self._get("primary.method", {"klick": True})

    @property
    def secondary_name(self) -> str:
        """Get secondary button name."""
        return self._get("secondary.name", "m_left")

    @property
    def secondary_type(self) -> str:
        """Get secondary button type."""
        return self._get("secondary.type", "mouse_button")

    @property
    def secondary_method(self) -> dict:
        """Get secondary button method configuration."""
        return self._get("secondary.method", {"hold": 2})

    # Behavior properties
    @property
    def behavior_debounce_time(self) -> float:
        """Get debounce time for behavior settings."""
        return self._get("behavior.debounce_time", 0.5)

    # Audio properties
    @property
    def audio_sample_rate(self) -> int:
        """Get audio sample rate."""
        return self._get("audio.sample_rate", 16000)

    @property
    def audio_channels(self) -> int:
        """Get audio channel count."""
        return self._get("audio.channels", 1)

    @property
    def audio_chunk_size(self) -> int:
        """Get audio chunk size."""
        return self._get("audio.chunk_size", 1024)

    @property
    def audio_format(self) -> str:
        """Get audio format."""
        return self._get("audio.format", "int16")

    @property
    def audio_device(self) -> Optional[int]:
        """Get audio device ID."""
        return self._get("audio.device", 1)

    @property
    def audio_device_name(self) -> Optional[str]:
        """Get audio device name preference."""
        return self._get("audio.device_name", "")

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

    # System properties
    @property
    def system_volume_reduction_factor(self) -> float:
        """Get volume reduction factor."""
        return self._get("system.volume_reduction_factor", 0.15)

    @property
    def system_min_volume_percent(self) -> int:
        """Get minimum volume percentage."""
        return self._get("system.min_volume_percent", 5)

    # Transcription properties
    @property
    def transcription_language(self) -> str:
        """Get transcription language."""
        return self._get("transcription.language", "de")

    @property
    def transcription_whisper_model(self) -> str:
        """Get Whisper model size."""
        return self._get("transcription.whisper_model", "base")

    @property
    def transcription_compute_type(self) -> str:
        """Get transcription compute type."""
        return self._get("transcription.compute_type", "float32")

    # Spell check properties
    @property
    def spell_check_enabled(self) -> bool:
        """Get spell check enabled setting."""
        return self._get("spell_check.enabled", True)

    @property
    def spell_check_auto_correct(self) -> bool:
        """Get auto-correct enabled setting."""
        return self._get("spell_check.auto_correct", True)

    # Custom dictionary properties
    @property
    def custom_dictionary_enabled(self) -> bool:
        """Get custom dictionary enabled setting."""
        return self._get("custom_dictionary.enabled", True)

    @property
    def custom_dictionary_auto_add_unknown(self) -> bool:
        """Get auto-add unknown words setting."""
        return self._get("custom_dictionary.auto_add_unknown", False)

    @property
    def custom_dictionary_path(self) -> str:
        """Get custom dictionary path."""
        return self._get("custom_dictionary.path", "")

    @property
    def custom_dictionary_max_words(self) -> int:
        """Get maximum words in dictionary."""
        return self._get("custom_dictionary.max_words", 1000)

    # Debug properties
    @property
    def debug_enabled(self) -> bool:
        """Get debug mode enabled setting."""
        return self._get("debug.enabled", False)

    @property
    def debug_level(self) -> str:
        """Get debug level setting."""
        return self._get("debug.level", "INFO")

    @property
    def debug_verbose(self) -> bool:
        """Get verbose logging setting."""
        return self._get("debug.verbose", False)

    @property
    def debug_log_errors(self) -> bool:
        """Get log errors setting."""
        return self._get("debug.log_errors", True)

    # Logging properties
    @property
    def logging_enabled(self) -> bool:
        """Get logging enabled setting."""
        return self._get("logging.enabled", True)

    @property
    def logging_console_level(self) -> str:
        """Get console logging level."""
        return self._get("logging.console_level", "INFO")

    @property
    def logging_file_level(self) -> str:
        """Get file logging level."""
        return self._get("logging.file_level", "DEBUG")

    @property
    def logging_emoji_enabled(self) -> bool:
        """Get emoji logging enabled setting."""
        return self._get("logging.emoji_enabled", True)

    @property
    def logging_file_enabled(self) -> bool:
        """Get file logging enabled setting."""
        return self._get("logging.file_enabled", True)

    @property
    def logging_filename(self) -> str:
        """Get log filename."""
        return self._get("logging.log_filename", "mauscribe.log")

    @property
    def logging_suppress_external(self) -> bool:
        """Get suppress external logs setting."""
        return self._get("logging.suppress_external_logs", True)

    # Auto-update properties
    @property
    def auto_update_enabled(self) -> bool:
        """Get auto-update enabled setting."""
        return self._get("auto_update.enabled", True)

    @property
    def auto_update_check_interval(self) -> int:
        """Get auto-update check interval in seconds."""
        return self._get("auto_update.check_interval", 86400)

    @property
    def auto_update_check_on_startup(self) -> bool:
        """Get auto-update check on startup setting."""
        return self._get("auto_update.check_on_startup", True)

    @property
    def auto_update_auto_install(self) -> bool:
        """Get auto-update auto install setting."""
        return self._get("auto_update.auto_install", False)

    @property
    def auto_update_include_prereleases(self) -> bool:
        """Get auto-update include prereleases setting."""
        return self._get("auto_update.include_prereleases", False)

    # Notification properties
    @property
    def notifications_enabled(self) -> bool:
        """Get notifications enabled setting."""
        return self._get("notifications.enabled", True)

    @property
    def notifications_duration(self) -> int:
        """Get notification duration in milliseconds."""
        return self._get("notifications.duration", 5000)

    @property
    def notifications_sound(self) -> bool:
        """Get notification sound setting."""
        return self._get("notifications.sound", True)

    @property
    def notifications_toast(self) -> bool:
        """Get notification toast setting."""
        return self._get("notifications.toast", True)

    @property
    def notifications_show_startup(self) -> bool:
        """Get show startup notification setting."""
        return self._get("notifications.show_startup", True)

    @property
    def notifications_show_shutdown(self) -> bool:
        """Get show shutdown notification setting."""
        return self._get("notifications.show_shutdown", True)

    @property
    def notifications_show_recording_events(self) -> bool:
        """Get show recording events setting."""
        return self._get("notifications.show_recording_events", True)

    @property
    def notifications_show_transcription_events(self) -> bool:
        """Get show transcription events setting."""
        return self._get("notifications.show_transcription_events", True)

    @property
    def notifications_show_text_events(self) -> bool:
        """Get show text events setting."""
        return self._get("notifications.show_text_events", True)

    @property
    def notifications_show_spell_check_events(self) -> bool:
        """Get show spell check events setting."""
        return self._get("notifications.show_spell_check_events", True)

    @property
    def notifications_show_errors(self) -> bool:
        """Get show error notifications setting."""
        return self._get("notifications.show_errors", True)

    @property
    def notifications_show_warnings(self) -> bool:
        """Get show warning notifications setting."""
        return self._get("notifications.show_warnings", True)

    # Database properties
    @property
    def database_enabled(self) -> bool:
        """Get database enabled setting."""
        return self._get("database.enabled", True)

    @property
    def database_data_directory(self) -> str:
        """Get database data directory path."""
        return self._get("database.data_directory", "")

    @property
    def database_audio_format(self) -> str:
        """Get database audio format for storage."""
        return self._get("database.audio_format", "wav")

    @property
    def database_auto_save_recordings(self) -> bool:
        """Get auto-save recordings setting."""
        return self._get("database.auto_save_recordings", True)

    @property
    def database_auto_save_transcriptions(self) -> bool:
        """Get auto-save transcriptions setting."""
        return self._get("database.auto_save_transcriptions", True)

    @property
    def database_mark_as_training_data(self) -> bool:
        """Get mark as training data setting."""
        return self._get("database.mark_as_training_data", True)

    @property
    def database_retention_days(self) -> int:
        """Get retention period in days."""
        return self._get("database.retention_days", 30)

    @property
    def database_max_database_size_mb(self) -> int:
        """Get maximum database size in MB."""
        return self._get("database.max_database_size_mb", 1000)

    @property
    def database_compress_audio(self) -> bool:
        """Get audio compression setting."""
        return self._get("database.compress_audio", False)

    @property
    def database_backup_before_cleanup(self) -> bool:
        """Get backup before cleanup setting."""
        return self._get("database.backup_before_cleanup", True)

    # Legacy properties for backward compatibility
    @property
    def input_method(self) -> str:
        """Get input method configuration (legacy)."""
        return self._get("input.method", "mouse_button")

    @property
    def mouse_button_primary(self) -> str:
        """Get primary mouse button configuration (legacy)."""
        return self._get("mouse_button.primary", "m_x2")

    @property
    def mouse_button_secondary(self) -> str:
        """Get secondary mouse button configuration (legacy)."""
        return self._get("mouse_button.secondary", "m_left")

    @property
    def mouse_button_left_with_ctrl(self) -> bool:
        """Get left mouse button with Ctrl configuration (legacy)."""
        return self._get("mouse_button.left_with_ctrl", False)

    @property
    def keyboard_primary(self) -> str:
        """Get primary keyboard shortcut (legacy)."""
        return self._get("keyboard.primary", "f9")

    @property
    def keyboard_secondary(self) -> str:
        """Get secondary keyboard shortcut (legacy)."""
        return self._get("keyboard.secondary", "shift+f9")

    @property
    def custom_combinations(self) -> list[dict[str, Any]]:
        """Get custom key combinations (legacy)."""
        return self._get("custom.combinations", [])

    @property
    def behavior_add_space_after_text(self) -> bool:
        """Get behavior for adding space after text (legacy)."""
        return self._get("behavior.add_space_after_text", True)

    @property
    def behavior_auto_paste_after_transcription(self) -> bool:
        """Get auto-paste behavior setting (legacy)."""
        return self._get("behavior.auto_paste_after_transcription", True)

    @property
    def behavior_paste_double_click_window(self) -> float:
        """Get double-click window for paste functionality (legacy)."""
        return self._get("behavior.paste_double_click_window", 5.0)

    @property
    def behavior_double_click_threshold(self) -> float:
        """Get double-click threshold (legacy)."""
        return self._get("behavior.double_click_threshold", 0.5)

    @property
    def cursor_enable(self) -> bool:
        """Get cursor feedback enable setting (legacy)."""
        return self._get("cursor.enable", False)

    @property
    def cursor_recording_type(self) -> str:
        """Get cursor type during recording (legacy)."""
        return self._get("cursor.recording_type", "cross")

    @property
    def stt_model(self) -> str:
        """Get STT model size setting (legacy)."""
        return self._get("stt.model", "medium")

    @property
    def stt_language(self) -> str:
        """Get STT language setting (legacy)."""
        return self._get("stt.language", "de")

    @property
    def stt_compute_type(self) -> str:
        """Get STT compute type setting (legacy)."""
        return self._get("stt.compute_type", "float32")

    @property
    def spell_check_language(self) -> str:
        """Get spell check language setting (legacy)."""
        return self._get("spell_check.language", "de")

    @property
    def spell_check_grammar(self) -> bool:
        """Get grammar check enabled setting (legacy)."""
        return self._get("spell_check.grammar_check", True)

    @property
    def spell_check_suggest_only(self) -> bool:
        """Get suggest-only mode setting (legacy)."""
        return self._get("spell_check.suggest_only", False)

    # Input filter properties (legacy fallback)
    @property
    def input_filter_primary_mode(self) -> str:
        """Get input filter mode for primary button (legacy fallback)."""
        return self._get("input_filter.primary_mode", "single_click")

    @property
    def input_filter_secondary_mode(self) -> str:
        """Get input filter mode for secondary button (legacy fallback)."""
        return self._get("input_filter.secondary_mode", "hold")

    @property
    def input_filter_hold_duration(self) -> float:
        """Get hold duration for hold mode in seconds (legacy fallback)."""
        return self._get("input_filter.hold_duration", 0.5)

    @property
    def input_filter_double_click_window(self) -> float:
        """Get double click window in seconds (legacy fallback)."""
        return self._get("input_filter.double_click_window", 0.5)

    @property
    def input_filter_smart_delay(self) -> float:
        """Get smart delay in seconds (legacy fallback)."""
        return self._get("input_filter.smart_delay", 0.2)
