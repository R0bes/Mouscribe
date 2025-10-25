# src/ui/tabs/__init__.py - Tabs package for Control Center
"""
Tabs package for Mauscribe Control Center.
Contains all tab implementations for the multi-tab interface.
"""

from .audio_tab import AudioTab
from .config_settings_tab import ConfigSettingsTab
from .logs_tab import LogsTab
from .settings_tab import SettingsTab
from .transcriptions_tab import TranscriptionsTab

__all__ = ["SettingsTab", "ConfigSettingsTab", "LogsTab", "TranscriptionsTab", "AudioTab"]
