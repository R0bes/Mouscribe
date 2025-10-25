# src/config/recording_modes.py - Recording Mode Configuration
"""
Configuration for Mauscribe recording modes:
- Normal mode: Audio files deleted after transcription
- Enhanced mode: Audio files + transcriptions saved permanently
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class RecordingMode(Enum):
    """Recording modes available in Mauscribe."""

    NORMAL = "normal"
    ENHANCED = "enhanced"


@dataclass
class NormalModeConfig:
    """Configuration for normal recording mode."""

    auto_cleanup: bool = True
    cleanup_after_n_recordings: int = 10
    cleanup_on_exit: bool = True
    max_temp_recordings: int = 50
    cleanup_interval_minutes: int = 30


@dataclass
class EnhancedModeConfig:
    """Configuration for enhanced recording mode."""

    save_audio_files: bool = True
    save_audio_data_in_db: bool = False  # Store audio data directly in database
    max_file_size_mb: int = 100
    compression_enabled: bool = True
    backup_enabled: bool = True
    backup_interval_hours: int = 24


@dataclass
class TrainingDataConfig:
    """Configuration for training data collection."""

    auto_mark_high_confidence: bool = True
    min_confidence_threshold: float = 0.8
    min_duration_seconds: float = 1.0
    max_duration_seconds: float = 300.0
    quality_scoring_enabled: bool = True
    speaker_identification_enabled: bool = False


@dataclass
class RecordingConfig:
    """Main recording configuration."""

    mode: RecordingMode = RecordingMode.NORMAL
    session_id: Optional[str] = None
    normal_config: NormalModeConfig = None
    enhanced_config: EnhancedModeConfig = None
    training_config: TrainingDataConfig = None

    def __post_init__(self):
        if self.normal_config is None:
            self.normal_config = NormalModeConfig()
        if self.enhanced_config is None:
            self.enhanced_config = EnhancedModeConfig()
        if self.training_config is None:
            self.training_config = TrainingDataConfig()

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "mode": self.mode.value,
            "session_id": self.session_id,
            "normal_config": {
                "auto_cleanup": self.normal_config.auto_cleanup,
                "cleanup_after_n_recordings": self.normal_config.cleanup_after_n_recordings,
                "cleanup_on_exit": self.normal_config.cleanup_on_exit,
                "max_temp_recordings": self.normal_config.max_temp_recordings,
                "cleanup_interval_minutes": self.normal_config.cleanup_interval_minutes,
            },
            "enhanced_config": {
                "save_audio_files": self.enhanced_config.save_audio_files,
                "save_audio_data_in_db": self.enhanced_config.save_audio_data_in_db,
                "max_file_size_mb": self.enhanced_config.max_file_size_mb,
                "compression_enabled": self.enhanced_config.compression_enabled,
                "backup_enabled": self.enhanced_config.backup_enabled,
                "backup_interval_hours": self.enhanced_config.backup_interval_hours,
            },
            "training_config": {
                "auto_mark_high_confidence": self.training_config.auto_mark_high_confidence,
                "min_confidence_threshold": self.training_config.min_confidence_threshold,
                "min_duration_seconds": self.training_config.min_duration_seconds,
                "max_duration_seconds": self.training_config.max_duration_seconds,
                "quality_scoring_enabled": self.training_config.quality_scoring_enabled,
                "speaker_identification_enabled": self.training_config.speaker_identification_enabled,
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RecordingConfig":
        """Create config from dictionary."""
        mode = RecordingMode(data.get("mode", "normal"))

        normal_data = data.get("normal_config", {})
        normal_config = NormalModeConfig(
            auto_cleanup=normal_data.get("auto_cleanup", True),
            cleanup_after_n_recordings=normal_data.get("cleanup_after_n_recordings", 10),
            cleanup_on_exit=normal_data.get("cleanup_on_exit", True),
            max_temp_recordings=normal_data.get("max_temp_recordings", 50),
            cleanup_interval_minutes=normal_data.get("cleanup_interval_minutes", 30),
        )

        enhanced_data = data.get("enhanced_config", {})
        enhanced_config = EnhancedModeConfig(
            save_audio_files=enhanced_data.get("save_audio_files", True),
            save_audio_data_in_db=enhanced_data.get("save_audio_data_in_db", False),
            max_file_size_mb=enhanced_data.get("max_file_size_mb", 100),
            compression_enabled=enhanced_data.get("compression_enabled", True),
            backup_enabled=enhanced_data.get("backup_enabled", True),
            backup_interval_hours=enhanced_data.get("backup_interval_hours", 24),
        )

        training_data = data.get("training_config", {})
        training_config = TrainingDataConfig(
            auto_mark_high_confidence=training_data.get("auto_mark_high_confidence", True),
            min_confidence_threshold=training_data.get("min_confidence_threshold", 0.8),
            min_duration_seconds=training_data.get("min_duration_seconds", 1.0),
            max_duration_seconds=training_data.get("max_duration_seconds", 300.0),
            quality_scoring_enabled=training_data.get("quality_scoring_enabled", True),
            speaker_identification_enabled=training_data.get("speaker_identification_enabled", False),
        )

        return cls(
            mode=mode,
            session_id=data.get("session_id"),
            normal_config=normal_config,
            enhanced_config=enhanced_config,
            training_config=training_config,
        )


# Default configurations
DEFAULT_NORMAL_CONFIG = RecordingConfig(
    mode=RecordingMode.NORMAL,
    normal_config=NormalModeConfig(),
    enhanced_config=EnhancedModeConfig(),
    training_config=TrainingDataConfig(),
)

DEFAULT_ENHANCED_CONFIG = RecordingConfig(
    mode=RecordingMode.ENHANCED,
    normal_config=NormalModeConfig(),
    enhanced_config=EnhancedModeConfig(
        save_audio_files=True, save_audio_data_in_db=False, compression_enabled=True, backup_enabled=True
    ),
    training_config=TrainingDataConfig(
        auto_mark_high_confidence=True, min_confidence_threshold=0.7, quality_scoring_enabled=True
    ),
)

# Training-focused configuration
TRAINING_CONFIG = RecordingConfig(
    mode=RecordingMode.ENHANCED,
    normal_config=NormalModeConfig(),
    enhanced_config=EnhancedModeConfig(
        save_audio_files=True,
        save_audio_data_in_db=True,  # Store in DB for easy access
        compression_enabled=False,  # No compression for training
        backup_enabled=True,
    ),
    training_config=TrainingDataConfig(
        auto_mark_high_confidence=True,
        min_confidence_threshold=0.6,  # Lower threshold for more data
        min_duration_seconds=0.5,  # Include shorter recordings
        max_duration_seconds=600.0,  # Allow longer recordings
        quality_scoring_enabled=True,
        speaker_identification_enabled=True,
    ),
)
