"""
Vereinfachte Settings für Mauscribe.
"""
import os
from typing import Any, Dict

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Vereinfachte Anwendungseinstellungen."""

    # Transcription settings
    model: str = Field(default="small", description="Whisper model to use")
    language: str = Field(default="de", description="Language for transcription")
    auto_detect_language: bool = Field(default=True, description="Enable automatic language detection")

    # System settings
    volume_reduction_factor: float = Field(default=1.0, description="Volume reduction factor")

    # Notifications settings
    sound: bool = Field(default=True, description="Enable sound notifications")
    toast: bool = Field(default=True, description="Enable toast notifications")

    # Notifications settings (for compatibility with existing code)
    notifications: dict[str, Any] = Field(
        default_factory=lambda: {
            "enabled": True,
            "sound": True,
            "toast": True,
            "duration": 5000,
            "auto_insert_enabled": False,
        },
        description="Notification settings",
    )

    # UI settings
    icon_path: str = Field(default="icons/icon.png", description="Icon path")

    # Input settings
    primary_name: str = Field(default="x2", description="Primary button name")
    primary_type: str = Field(default="click", description="Primary button type")
    secondary_name: str = Field(default="left", description="Secondary button name")
    secondary_type: str = Field(default="hold", description="Secondary button type")

    # Hotword settings (for compatibility)
    hotword: dict[str, Any] = Field(default_factory=dict, description="Hotword settings")

    # Input settings (for compatibility)
    input: dict[str, Any] = Field(default_factory=dict, description="Input settings")

    # Database settings (for compatibility)
    database: dict[str, Any] = Field(default_factory=dict, description="Database settings")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Load from TOML file if it exists
        try:
            import toml

            with open("settings.toml", encoding="utf-8") as f:
                config = toml.load(f)

            # Load transcription settings
            if "transcription" in config:
                trans_config = config["transcription"]
                if "model" in trans_config:
                    self.model = str(trans_config["model"])
                if "language" in trans_config:
                    self.language = str(trans_config["language"])

            # Load system settings
            if "system" in config:
                sys_config = config["system"]
                if "volume_reduction_factor" in sys_config:
                    try:
                        self.volume_reduction_factor = float(sys_config["volume_reduction_factor"])
                    except (ValueError, TypeError):
                        self.volume_reduction_factor = 1.0  # Default fallback

            # Load notification settings
            if "notifications" in config:
                notif_config = config["notifications"]
                if "sound" in notif_config:
                    self.sound = bool(notif_config["sound"])
                if "toast" in notif_config:
                    self.toast = bool(notif_config["toast"])

                # Load notifications dict for compatibility
                self.notifications.update(notif_config)

            # Load UI settings
            if "ui" in config:
                ui_config = config["ui"]
                if "icon_path" in ui_config:
                    self.icon_path = str(ui_config["icon_path"])

            # Load input settings
            if "input" in config:
                input_config = config["input"]
                if "primary" in input_config:
                    primary_config = input_config["primary"]
                    if "name" in primary_config:
                        self.primary_name = str(primary_config["name"])
                    if "type" in primary_config:
                        self.primary_type = str(primary_config["type"])
                if "secondary" in input_config:
                    secondary_config = input_config["secondary"]
                    if "name" in secondary_config:
                        self.secondary_name = str(secondary_config["name"])
                    if "type" in secondary_config:
                        self.secondary_type = str(secondary_config["type"])

        except Exception as e:
            # Use defaults if TOML loading fails
            pass

    def get_icon_path(self) -> str:
        """Get absolute path to icon file."""
        if os.path.isabs(self.icon_path):
            return self.icon_path

        # Try different possible locations
        possible_paths = [
            self.icon_path,
            f"src/ui/{self.icon_path}",
            f"src/ui/icons/{os.path.basename(self.icon_path)}",
            "src/ui/icons/systemtray_icon.ico",
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return os.path.abspath(path)

        # Fallback to default
        return os.path.abspath("src/ui/icons/systemtray_icon.ico")


class AppSettings(Settings):
    """Application metadata settings."""

    app_name: str = Field(default="Mauscribe", description="Application name")
    version: str = Field(default="1.0.0", description="Application version")
