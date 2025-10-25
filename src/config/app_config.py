# src/config/app_config.py - Unified Application Configuration
"""
Unified application configuration for Mauscribe.
Consolidates all settings classes into a single, consistent configuration system.
"""

import logging
import os
from typing import Any, Dict, List, Optional

import toml
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class AudioConfig(BaseModel):
    """Audio configuration settings."""

    # Model settings
    model: str = Field(default="medium", description="Whisper model size")
    language: str = Field(default="de", description="Transcription language")
    auto_detect_language: bool = Field(default=False, description="Auto-detect language")

    # Recording settings
    sample_rate: int = Field(default=16000, description="Audio sample rate")
    channels: int = Field(default=1, description="Number of audio channels")
    chunk_size: int = Field(default=1024, description="Audio chunk size")

    # Volume control
    volume_reduction_factor: float = Field(default=0.3, description="Volume reduction factor")
    min_volume: int = Field(default=10, description="Minimum volume level")

    # Audio processing settings only


class InputConfig(BaseModel):
    """Input configuration settings."""

    enabled: bool = Field(default=True, description="Enable input handling")

    # Mouse settings
    primary_button: str = Field(default="left", description="Primary mouse button")
    secondary_button: str = Field(default="right", description="Secondary mouse button")
    insert_combination: str = Field(default="left+x2", description="Insert combination")

    # Keyboard settings
    recording_key: str = Field(default="space", description="Recording key")
    insert_key: str = Field(default="ctrl+v", description="Insert key combination")

    # Timing settings
    hold_threshold: float = Field(default=0.5, description="Hold threshold in seconds")
    double_click_threshold: float = Field(default=0.3, description="Double click threshold")


class NotificationTypeConfig(BaseModel):
    """Configuration for a specific notification type."""

    toast: bool = Field(default=True, description="Show toast notification")
    sound: bool = Field(default=True, description="Play sound notification")


class NotificationConfig(BaseModel):
    """Granular notification configuration settings."""

    # Recording notifications
    recording_start: NotificationTypeConfig = Field(default_factory=lambda: NotificationTypeConfig(toast=False, sound=False))
    recording_stop: NotificationTypeConfig = Field(default_factory=lambda: NotificationTypeConfig(toast=False, sound=False))
    recording_error: NotificationTypeConfig = Field(default_factory=lambda: NotificationTypeConfig(toast=True, sound=True))

    # Transcription notifications
    transcription_success: NotificationTypeConfig = Field(
        default_factory=lambda: NotificationTypeConfig(toast=False, sound=False)
    )
    transcription_error: NotificationTypeConfig = Field(default_factory=lambda: NotificationTypeConfig(toast=True, sound=True))
    transcription_empty: NotificationTypeConfig = Field(
        default_factory=lambda: NotificationTypeConfig(toast=False, sound=False)
    )

    # Text insertion notifications
    text_inserted: NotificationTypeConfig = Field(default_factory=lambda: NotificationTypeConfig(toast=False, sound=False))
    text_insert_error: NotificationTypeConfig = Field(default_factory=lambda: NotificationTypeConfig(toast=True, sound=True))

    # System notifications
    app_start: NotificationTypeConfig = Field(default_factory=lambda: NotificationTypeConfig(toast=False, sound=False))
    app_shutdown: NotificationTypeConfig = Field(default_factory=lambda: NotificationTypeConfig(toast=False, sound=False))

    # Input notifications
    input_primary: NotificationTypeConfig = Field(default_factory=lambda: NotificationTypeConfig(toast=False, sound=False))
    input_secondary: NotificationTypeConfig = Field(default_factory=lambda: NotificationTypeConfig(toast=False, sound=False))
    input_combination: NotificationTypeConfig = Field(default_factory=lambda: NotificationTypeConfig(toast=False, sound=False))

    # Global settings
    toast_duration: int = Field(default=2000, description="Toast notification duration in ms")
    toast_position: str = Field(default="top-right", description="Toast position")


class UIConfig(BaseModel):
    """UI configuration settings."""

    # System tray
    tray_enabled: bool = Field(default=True, description="Enable system tray")
    tray_icon: str = Field(default="systemtray_icon.ico", description="Tray icon file")

    # Notifications
    notifications: NotificationConfig = Field(default_factory=NotificationConfig)

    # Widgets (currently disabled)
    widgets_enabled: bool = Field(default=False, description="Enable overlay widgets")

    # Theme
    theme: str = Field(default="default", description="UI theme")
    dark_mode: bool = Field(default=False, description="Enable dark mode")


class DatabaseConfig(BaseModel):
    """Database configuration settings."""

    enabled: bool = Field(default=True, description="Enable database")
    path: str = Field(default="data/audio_database.db", description="Database file path")
    max_size_mb: int = Field(default=100, description="Maximum database size in MB")
    compression_enabled: bool = Field(default=True, description="Enable audio compression")

    # Auto-save settings
    auto_save_recordings: bool = Field(default=True, description="Auto-save audio recordings")
    auto_save_transcriptions: bool = Field(default=True, description="Auto-save transcriptions")
    mark_as_training_data: bool = Field(default=False, description="Mark transcriptions as training data")
    audio_format: str = Field(default="wav", description="Audio format for storage")

    # Backup settings
    backup_enabled: bool = Field(default=True, description="Enable automatic backups")
    backup_interval_hours: int = Field(default=24, description="Backup interval in hours")
    max_backups: int = Field(default=7, description="Maximum number of backups")


class LoggingConfig(BaseModel):
    """Logging configuration settings."""

    level: str = Field(default="INFO", description="Logging level")
    file_enabled: bool = Field(default=True, description="Enable file logging")
    console_enabled: bool = Field(default=True, description="Enable console logging")
    max_file_size_mb: int = Field(default=10, description="Maximum log file size in MB")
    max_files: int = Field(default=5, description="Maximum number of log files")

    # Log file paths
    main_log: str = Field(default="logs/mauscribe.log", description="Main log file")
    error_log: str = Field(default="logs/mauscribe_errors.log", description="Error log file")
    performance_log: str = Field(default="logs/mauscribe_performance.log", description="Performance log file")


class DictionaryConfig(BaseModel):
    """Dictionary configuration settings."""

    enabled: bool = Field(default=True, description="Enable custom dictionary")
    path: str = Field(default="data/custom_dictionary.json", description="Dictionary file path")
    auto_save: bool = Field(default=True, description="Auto-save dictionary changes")
    max_entries: int = Field(default=1000, description="Maximum dictionary entries")


class AppConfig(BaseModel):
    """
    Main application configuration.
    Consolidates all configuration sections into a single, unified system.
    """

    # Application metadata
    app_name: str = Field(default="Mauscribe", description="Application name")
    version: str = Field(default="2.0.0", description="Application version")

    # Legacy compatibility fields
    model: str = Field(default="small", description="Whisper model size (legacy)")
    language: str = Field(default="de", description="Transcription language (legacy)")
    primary_name: str = Field(default="x2", description="Primary button name (legacy)")
    primary_type: str = Field(default="click", description="Primary button type (legacy)")
    secondary_name: str = Field(default="left", description="Secondary button name (legacy)")
    secondary_type: str = Field(default="hold", description="Secondary button type (legacy)")
    volume_reduction_factor: float = Field(default=0.3, description="Volume reduction factor (legacy)")
    sound: bool = Field(default=True, description="Sound notifications (legacy)")
    toast: bool = Field(default=True, description="Toast notifications (legacy)")

    # Legacy dict fields for compatibility
    input: dict[str, Any] = Field(default_factory=dict, description="Input settings (legacy)")

    # Configuration sections
    audio: AudioConfig = Field(default_factory=AudioConfig)
    input_config: InputConfig = Field(default_factory=InputConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    dictionary: DictionaryConfig = Field(default_factory=DictionaryConfig)

    class Config:
        env_file = "settings.toml"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @classmethod
    def load_from_file(cls, config_path: str = "settings.toml") -> "AppConfig":
        """
        Load configuration from TOML file.

        Args:
            config_path: Path to configuration file

        Returns:
            AppConfig instance
        """
        try:
            if os.path.exists(config_path):
                with open(config_path, encoding="utf-8") as f:
                    config_data = toml.load(f)
                logger.info(f"✅ Konfiguration geladen: {config_path}")
                return cls(**config_data)
            else:
                logger.warning(f"⚠️ Konfigurationsdatei nicht gefunden: {config_path}")
                logger.info("🔄 Verwende Standard-Konfiguration")
                # Erstelle Standard-Konfiguration und speichere sie
                default_config = cls()
                if default_config.save_to_file(config_path):
                    logger.info(f"💾 Standard-Konfiguration gespeichert: {config_path}")
                return default_config
        except Exception as e:
            logger.error(f"❌ Fehler beim Laden der Konfiguration: {e}")
            logger.info("🔄 Verwende Standard-Konfiguration")
            # Erstelle Standard-Konfiguration und speichere sie
            default_config = cls()
            if default_config.save_to_file(config_path):
                logger.info(f"💾 Standard-Konfiguration gespeichert: {config_path}")
            return default_config

    def save_to_file(self, config_path: str = "settings.toml") -> bool:
        """
        Save configuration to TOML file.

        Args:
            config_path: Path to configuration file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists (only if config_path has a directory)
            config_dir = os.path.dirname(config_path)
            if config_dir:
                os.makedirs(config_dir, exist_ok=True)

            # Convert to dict and save
            config_dict = self.dict()
            with open(config_path, "w", encoding="utf-8") as f:
                toml.dump(config_dict, f)

            logger.info(f"✅ Konfiguration gespeichert: {config_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Fehler beim Speichern der Konfiguration: {e}")
            return False

    def update_and_save(self, key_path: str, value: Any, config_path: str = "settings.toml") -> bool:
        """
        Update a specific configuration value and save it to file.

        Args:
            key_path: Dot-separated path to the configuration key (e.g., "audio.model")
            value: New value to set
            config_path: Path to configuration file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Update the configuration object
            self._set_nested_value(key_path, value)

            # Load existing config file
            if os.path.exists(config_path):
                with open(config_path, encoding="utf-8") as f:
                    existing_config = toml.load(f)
            else:
                existing_config = {}

            # Update the specific value in the existing config
            self._set_nested_dict_value(existing_config, key_path, value)

            # Save back to file
            with open(config_path, "w", encoding="utf-8") as f:
                toml.dump(existing_config, f)

            logger.info(f"✅ Konfigurationswert aktualisiert: {key_path} = {value}")
            return True
        except Exception as e:
            logger.error(f"❌ Fehler beim Aktualisieren des Konfigurationswerts {key_path}: {e}")
            return False

    def _set_nested_value(self, key_path: str, value: Any) -> None:
        """Set a nested value in the configuration object."""
        keys = key_path.split(".")
        obj = self

        # Navigate to the parent object
        for key in keys[:-1]:
            if hasattr(obj, key):
                obj = getattr(obj, key)
            else:
                raise AttributeError(f"Configuration key not found: {key}")

        # Set the final value
        final_key = keys[-1]
        if hasattr(obj, final_key):
            setattr(obj, final_key, value)
        else:
            raise AttributeError(f"Configuration key not found: {final_key}")

    def _set_nested_dict_value(self, config_dict: dict, key_path: str, value: Any) -> None:
        """Set a nested value in a dictionary."""
        keys = key_path.split(".")
        obj = config_dict

        # Navigate to the parent object
        for key in keys[:-1]:
            if key not in obj:
                obj[key] = {}
            obj = obj[key]

        # Set the final value
        final_key = keys[-1]
        obj[final_key] = value

    def get_section(self, section_name: str) -> Optional[BaseModel]:
        """
        Get a configuration section.

        Args:
            section_name: Name of the section

        Returns:
            Configuration section or None
        """
        return getattr(self, section_name, None)

    def update_section(self, section_name: str, **kwargs) -> bool:
        """
        Update a configuration section.

        Args:
            section_name: Name of the section
            **kwargs: Section updates

        Returns:
            True if successful, False otherwise
        """
        try:
            section = getattr(self, section_name, None)
            if section:
                for key, value in kwargs.items():
                    if hasattr(section, key):
                        setattr(section, key, value)
                logger.info(f"✅ Konfigurationssektion aktualisiert: {section_name}")
                return True
            else:
                logger.error(f"❌ Unbekannte Konfigurationssektion: {section_name}")
                return False
        except Exception as e:
            logger.error(f"❌ Fehler beim Aktualisieren der Konfiguration: {e}")
            return False

    def validate_config(self) -> list[str]:
        """
        Validate configuration and return any issues.

        Returns:
            List of validation issues
        """
        issues = []

        try:
            # Validate audio settings
            if self.audio.model not in ["tiny", "base", "small", "medium", "large"]:
                issues.append(f"Invalid audio model: {self.audio.model}")

            if self.audio.sample_rate <= 0:
                issues.append(f"Invalid sample rate: {self.audio.sample_rate}")

            # Validate input settings
            if self.input.hold_threshold <= 0:
                issues.append(f"Invalid hold threshold: {self.input.hold_threshold}")

            # Validate database settings
            if self.database.max_size_mb <= 0:
                issues.append(f"Invalid database max size: {self.database.max_size_mb}")

            # Validate logging settings
            if self.logging.level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
                issues.append(f"Invalid logging level: {self.logging.level}")

        except Exception as e:
            issues.append(f"Configuration validation error: {e}")

        return issues

    def get_summary(self) -> dict[str, Any]:
        """
        Get configuration summary.

        Returns:
            Configuration summary dictionary
        """
        return {
            "app_name": self.app_name,
            "version": self.version,
            "audio": {
                "model": self.audio.model,
                "language": self.audio.language,
            },
            "input": {
                "enabled": self.input.enabled,
                "primary_button": self.input.primary_button,
                "secondary_button": self.input.secondary_button,
            },
            "ui": {
                "tray_enabled": self.ui.tray_enabled,
                "notifications_enabled": self.ui.notifications_enabled,
                "widgets_enabled": self.ui.widgets_enabled,
            },
            "database": {
                "enabled": self.database.enabled,
                "path": self.database.path,
                "max_size_mb": self.database.max_size_mb,
            },
            "logging": {
                "level": self.logging.level,
                "file_enabled": self.logging.file_enabled,
                "console_enabled": self.logging.console_enabled,
            },
        }


# Global configuration instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = AppConfig.load_from_file()
    return _config


def reload_config() -> AppConfig:
    """Reload configuration from file."""
    global _config
    _config = AppConfig.load_from_file()
    return _config


def save_config() -> bool:
    """Save current configuration to file."""
    global _config
    if _config:
        return _config.save_to_file()
    return False
