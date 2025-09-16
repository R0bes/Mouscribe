# src/utils/settings.py - Settings management for Mauscribe
"""
Settings management for Mauscribe using Pydantic for validation and type safety.
Each module can define its own settings class that only loads relevant fields.
"""
from typing import Optional, Literal, Any, Dict

from pydantic import Field
from pydantic_settings import BaseSettings


class ModuleSettings(BaseSettings):
    """Base class for module-specific settings that loads from TOML."""
    
    model_config = {
        "env_file": "settings.toml",
        "env_file_encoding": "utf-8",
        "extra": "ignore",  # Ignore extra fields from TOML file
        "validate_assignment": True,
        "use_enum_values": True
    }


class Settings(ModuleSettings):
    """Main settings class for Mauscribe - only loads what it needs."""
    
    # Primary and secondary button names
    primary_name: str = Field(default="x2", description="Primary button name")
    secondary_name: str = Field(default="x1", description="Secondary button name")
    
    # Notifications settings
    notifications: Dict[str, Any] = Field(default_factory=lambda: {"show_all": True}, description="Notification settings")
    
    # Audio settings
    audio: Dict[str, Any] = Field(default_factory=dict, description="Audio settings")
    
    # Transcription settings
    transcription: Dict[str, Any] = Field(default_factory=dict, description="Transcription settings")
    
    # Database settings
    database: Dict[str, Any] = Field(default_factory=dict, description="Database settings")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load from TOML file if it exists
        try:
            import toml
            with open("settings.toml", "r", encoding="utf-8") as f:
                config = toml.load(f)
                
            # Map TOML structure to our fields
            if "input" in config:
                if "primary" in config["input"]:
                    self.primary_name = config["input"]["primary"].get("name", "x2")
                if "secondary" in config["input"]:
                    self.secondary_name = config["input"]["secondary"].get("name", "x1")
            
            if "notifications" in config:
                self.notifications = config["notifications"]
            
            if "audio" in config:
                self.audio = config["audio"]
                
            if "transcription" in config:
                self.transcription = config["transcription"]
                
            if "database" in config:
                self.database = config["database"]
                
        except Exception as e:
            # Use defaults if TOML loading fails
            pass
    
    @classmethod
    def create_default_config(cls, config_path: str = "settings.toml") -> None:
        """Create a default configuration file if it doesn't exist."""
        import toml
        from pathlib import Path
        
        if Path(config_path).exists():
            return
            
        default_config = {
            "app": {
                "app_name": "Mauscribe",
                "version": "1.0.0"
            },
            "input": {
                "primary": {"name": "x2", "type": "click"},
                "secondary": {"name": "x1", "type": "click"}
            },
            "audio": {
                "sample_rate": 16000,
                "channels": 1,
                "chunk_size": 1024,
                "format": "wav",
                "audio_device": 1,
                "auto_select_device": True,
                "test_device_on_startup": True
            },
            "system": {
                "volume_reduction_factor": 0.6,
                "min_volume_percent": 10,
                "volume_controller_enabled": True
            },
            "transcription": {
                "language": "de",
                "whisper_model": "base",
                "compute_type": "float32",
                "compute_device": "cpu"
            },
            "logging": {
                "enabled": True,
                "console_level": "INFO",
                "file_level": "DEBUG",
                "file_enabled": True,
                "filename": "mauscribe.log",
                "suppress_external_logs": True
            },
            "dictionary": {
                "enabled": True,
                "auto_add_unknown": False,
                "path": "",
                "max_words": 1000
            },
            "notifications": {
                "enabled": True,
                "duration": 5000,
                "sound": True,
                "toast": True,
                "show_info": True,
                "show_success": True,
                "show_warning": True,
                "show_error": True,
                "show_recording": True,
                "show_transcription": True,
                "show_paste": True,
                "show_spell_check": True,
                "auto_insert_enabled": False
            },
            "database": {
                "enabled": True,
                "data_directory": "",
                "audio_format": "wav",
                "auto_save_recordings": True,
                "auto_save_transcriptions": True,
                "mark_as_training_data": True,
                "retention_days": 30,
                "max_size_mb": 1000,
                "compress_audio": False,
                "backup_before_cleanup": True
            }
        }
        
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                toml.dump(default_config, f)
            print(f"✅ Standard-Konfiguration erstellt: {config_path}")
        except Exception as e:
            print(f"❌ Fehler beim Erstellen der Standard-Konfiguration: {e}")