# src/config.py - Configuration management for Mauscribe
"""
Simplified configuration management for Mauscribe application.
Handles TOML configuration file loading with clean, unified structure.
"""

import tomllib
from typing import Any, Dict, Optional

from .logger import get_logger


class Config:
    """Configuration manager for Mauscribe application."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration with optional custom path."""
        self.logger = get_logger(self.__class__.__name__)
        self.config_path = config_path or "config.toml"
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

    # Input properties
    @property
    def primary_name(self) -> str:
        """Get primary button name."""
        return self._get("input.primary.name", "m_x2")

    @property
    def primary_type(self) -> str:
        """Get primary button type."""
        return self._get("input.primary.type", "mouse_button")

    @property
    def primary_method(self) -> dict:
        """Get primary button method configuration."""
        return self._get("input.primary.method", {"click": True})

    @property
    def secondary_name(self) -> str:
        """Get secondary button name."""
        return self._get("input.secondary.name", "m_x1")

    @property
    def secondary_type(self) -> str:
        """Get secondary button type."""
        return self._get("input.secondary.type", "mouse_button")

    @property
    def secondary_method(self) -> dict:
        """Get secondary button method configuration."""
        return self._get("input.secondary.method", {"hold": 1})

    # Behavior properties
    @property
    def behavior_debounce_time(self) -> float:
        """Get debounce time for behavior settings."""
        return self._get("behavior.debounce_time", 0.5)

    @property
    def behavior_auto_paste_after_transcription(self) -> bool:
        """Get auto-paste after transcription setting."""
        return self._get("behavior.auto_paste_after_transcription", True)

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
        return self._get("audio.format", "wav")

    @property
    def audio_device(self) -> Optional[int]:
        """Get audio device ID."""
        return self._get("audio.device", 1)

    @property
    def audio_auto_select_device(self) -> bool:
        """Get whether to automatically select the best audio device."""
        return self._get("audio.auto_select_device", True)

    @property
    def audio_test_device_on_startup(self) -> bool:
        """Get whether to test audio device on startup."""
        return self._get("audio.test_device_on_startup", True)

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

    # Dictionary properties
    @property
    def dictionary_enabled(self) -> bool:
        """Get dictionary enabled setting."""
        return self._get("dictionary.enabled", True)

    @property
    def dictionary_auto_add_unknown(self) -> bool:
        """Get auto-add unknown words setting."""
        return self._get("dictionary.auto_add_unknown", False)

    @property
    def dictionary_path(self) -> str:
        """Get dictionary path."""
        return self._get("dictionary.path", "")

    @property
    def dictionary_max_words(self) -> int:
        """Get maximum words in dictionary."""
        return self._get("dictionary.max_words", 1000)

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
        """Get emoji logging enabled."""
        return self._get("logging.emoji_enabled", True)

    @property
    def logging_file_enabled(self) -> bool:
        """Get file logging enabled."""
        return self._get("logging.file_enabled", True)

    @property
    def logging_filename(self) -> str:
        """Get log filename."""
        return self._get("logging.filename", "mauscribe.log")

    @property
    def logging_suppress_external(self) -> bool:
        """Get suppress external logs setting."""
        return self._get("logging.suppress_external_logs", True)

    # Update properties
    @property
    def updates_enabled(self) -> bool:
        """Get updates enabled setting."""
        return self._get("updates.enabled", True)

    @property
    def updates_check_interval(self) -> int:
        """Get updates check interval in seconds."""
        return self._get("updates.check_interval", 86400)

    @property
    def updates_check_on_startup(self) -> bool:
        """Get updates check on startup setting."""
        return self._get("updates.check_on_startup", True)

    @property
    def updates_auto_install(self) -> bool:
        """Get updates auto install setting."""
        return self._get("updates.auto_install", False)

    @property
    def updates_include_prereleases(self) -> bool:
        """Get updates include prereleases setting."""
        return self._get("updates.include_prereleases", False)

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
    def notifications_show_all(self) -> bool:
        """Get show all notifications setting."""
        return self._get("notifications.show_all", True)

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
    def database_max_size_mb(self) -> int:
        """Get maximum database size in MB."""
        return self._get("database.max_size_mb", 1000)

    @property
    def database_compress_audio(self) -> bool:
        """Get audio compression setting."""
        return self._get("database.compress_audio", False)

    @property
    def database_backup_before_cleanup(self) -> bool:
        """Get backup before cleanup setting."""
        return self._get("database.backup_before_cleanup", True)

    # Legacy compatibility properties (for backward compatibility)
    @property
    def stt_language(self) -> str:
        """Legacy property for transcription language."""
        return self.transcription_language

    @property
    def stt_model(self) -> str:
        """Legacy property for transcription model."""
        return self.transcription_whisper_model

    @property
    def stt_compute_type(self) -> str:
        """Legacy property for transcription compute type."""
        return self.transcription_compute_type

    @property
    def custom_dictionary_enabled(self) -> bool:
        """Legacy property for dictionary enabled."""
        return self.dictionary_enabled

    @property
    def custom_dictionary_auto_add_unknown(self) -> bool:
        """Legacy property for dictionary auto add unknown."""
        return self.dictionary_auto_add_unknown

    @property
    def custom_dictionary_path(self) -> str:
        """Legacy property for dictionary path."""
        return self.dictionary_path

    @property
    def custom_dictionary_max_words(self) -> int:
        """Legacy property for dictionary max words."""
        return self.dictionary_max_words

    @property
    def auto_update_enabled(self) -> bool:
        """Legacy property for updates enabled."""
        return self.updates_enabled

    @property
    def auto_update_check_interval(self) -> int:
        """Legacy property for updates check interval."""
        return self.updates_check_interval

    @property
    def auto_update_check_on_startup(self) -> bool:
        """Legacy property for updates check on startup."""
        return self.updates_check_on_startup

    @property
    def auto_update_auto_install(self) -> bool:
        """Legacy property for updates auto install."""
        return self.updates_auto_install

    @property
    def auto_update_include_prereleases(self) -> bool:
        """Legacy property for updates include prereleases."""
        return self.updates_include_prereleases
