# src/config/__init__.py - Configuration Module for Mauscribe
"""
Configuration Module für Mauscribe
Enthält die vereinheitlichte Konfigurationsverwaltung
"""

from .app_config import (
    AppConfig,
    AudioConfig,
    DatabaseConfig,
    DictionaryConfig,
    InputConfig,
    LoggingConfig,
    NotificationConfig,
    UIConfig,
    get_config,
    reload_config,
    save_config,
)

__all__ = [
    "AppConfig",
    "AudioConfig",
    "InputConfig",
    "UIConfig",
    "NotificationConfig",
    "DatabaseConfig",
    "LoggingConfig",
    "DictionaryConfig",
    "get_config",
    "reload_config",
    "save_config",
]
