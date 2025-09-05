# tests/utils.py
"""
Test utilities for Mauscribe tests.
"""

import json
import tempfile
import wave
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np


def create_temp_audio_file(
    duration: float = 1.0, sample_rate: int = 16000, channels: int = 1
) -> Path:
    """Create a temporary WAV file for testing.

    Args:
        duration: Duration in seconds
        sample_rate: Sample rate in Hz
        channels: Number of channels

    Returns:
        Path to the temporary audio file
    """
    temp_dir = Path(tempfile.mkdtemp())
    audio_file = temp_dir / "test_audio.wav"

    # Generate test audio data (sine wave)
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio_data = np.sin(2 * np.pi * 440 * t)  # 440 Hz sine wave

    # Convert to 16-bit PCM
    audio_data = (audio_data * 32767).astype(np.int16)

    # Write WAV file
    with wave.open(str(audio_file), "wb") as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())

    return audio_file


def create_temp_config_file(config_data: Dict[str, Any]) -> Path:
    """Create a temporary TOML config file for testing.

    Args:
        config_data: Configuration data as dictionary

    Returns:
        Path to the temporary config file
    """
    temp_dir = Path(tempfile.mkdtemp())
    config_file = temp_dir / "test_config.toml"

    # Convert dict to TOML format (simplified)
    toml_content = ""
    for section, values in config_data.items():
        toml_content += f"[{section}]\n"
        for key, value in values.items():
            if isinstance(value, str):
                toml_content += f'{key} = "{value}"\n'
            elif isinstance(value, bool):
                toml_content += f"{key} = {str(value).lower()}\n"
            else:
                toml_content += f"{key} = {value}\n"
        toml_content += "\n"

    config_file.write_text(toml_content)
    return config_file


def create_temp_dictionary_file(words: list) -> Path:
    """Create a temporary dictionary file for testing.

    Args:
        words: List of words to include in dictionary

    Returns:
        Path to the temporary dictionary file
    """
    temp_dir = Path(tempfile.mkdtemp())
    dict_file = temp_dir / "test_dictionary.json"

    dictionary_data = {
        "words": words,
        "metadata": {
            "created": "2024-01-01T00:00:00Z",
            "version": "1.0.0",
            "language": "de",
        },
    }

    dict_file.write_text(json.dumps(dictionary_data, indent=2))
    return dict_file


def create_temp_database_file() -> Path:
    """Create a temporary SQLite database file for testing.

    Returns:
        Path to the temporary database file
    """
    temp_dir = Path(tempfile.mkdtemp())
    db_file = temp_dir / "test_database.db"

    # Create empty database file
    db_file.touch()
    return db_file


def assert_audio_file_valid(audio_file: Path) -> None:
    """Assert that an audio file is valid.

    Args:
        audio_file: Path to the audio file to validate
    """
    assert audio_file.exists(), f"Audio file {audio_file} does not exist"
    assert audio_file.stat().st_size > 0, f"Audio file {audio_file} is empty"

    # Try to open as WAV file
    try:
        with wave.open(str(audio_file), "rb") as wav_file:
            assert wav_file.getnchannels() > 0, "Invalid number of channels"
            assert wav_file.getframerate() > 0, "Invalid sample rate"
            assert wav_file.getnframes() > 0, "No audio frames"
    except Exception as e:
        raise AssertionError(f"Audio file {audio_file} is not a valid WAV file: {e}")


def assert_config_file_valid(config_file: Path) -> None:
    """Assert that a config file is valid.

    Args:
        config_file: Path to the config file to validate
    """
    assert config_file.exists(), f"Config file {config_file} does not exist"
    assert config_file.stat().st_size > 0, f"Config file {config_file} is empty"

    # Try to read as text
    content = config_file.read_text()
    assert len(content.strip()) > 0, "Config file is empty or contains only whitespace"


def assert_dictionary_file_valid(dict_file: Path) -> None:
    """Assert that a dictionary file is valid.

    Args:
        dict_file: Path to the dictionary file to validate
    """
    assert dict_file.exists(), f"Dictionary file {dict_file} does not exist"
    assert dict_file.stat().st_size > 0, f"Dictionary file {dict_file} is empty"

    # Try to parse as JSON
    try:
        data = json.loads(dict_file.read_text())
        assert isinstance(data, dict), "Dictionary file is not a valid JSON object"
        assert "words" in data, "Dictionary file missing 'words' key"
        assert isinstance(data["words"], list), "Dictionary words must be a list"
    except json.JSONDecodeError as e:
        raise AssertionError(f"Dictionary file {dict_file} is not valid JSON: {e}")


def assert_database_file_valid(db_file: Path) -> None:
    """Assert that a database file is valid.

    Args:
        db_file: Path to the database file to validate
    """
    assert db_file.exists(), f"Database file {db_file} does not exist"
    assert db_file.stat().st_size >= 0, f"Database file {db_file} has invalid size"


def cleanup_temp_files(*files: Path) -> None:
    """Clean up temporary files and directories.

    Args:
        *files: Variable number of file paths to clean up
    """
    for file_path in files:
        try:
            if file_path.exists():
                if file_path.is_file():
                    file_path.unlink()
                elif file_path.is_dir():
                    import shutil

                    shutil.rmtree(file_path)
        except Exception as e:
            print(f"Warning: Could not clean up {file_path}: {e}")


class MockAudioDevice:
    """Mock audio device for testing."""

    def __init__(
        self, name: str = "Test Device", channels: int = 2, sample_rate: int = 16000
    ):
        self.name = name
        self.channels = channels
        self.sample_rate = sample_rate
        self.is_active = False

    def start_recording(self):
        """Start recording simulation."""
        self.is_active = True

    def stop_recording(self):
        """Stop recording simulation."""
        self.is_active = False

    def get_audio_data(self, duration: float = 1.0) -> np.ndarray:
        """Get mock audio data."""
        samples = int(self.sample_rate * duration)
        return np.random.rand(samples, self.channels).astype(np.float32)


class MockTranscriptionResult:
    """Mock transcription result for testing."""

    def __init__(
        self,
        text: str = "Test transcription",
        confidence: float = 0.95,
        language: str = "de",
    ):
        self.text = text
        self.confidence = confidence
        self.language = language
        self.segments = [{"text": text, "start": 0.0, "end": 1.0}]

    def __str__(self) -> str:
        return self.text
