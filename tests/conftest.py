# tests/conftest.py
"""
Pytest configuration and shared fixtures for Mauscribe tests.
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.config import Config
from src.utils.logger import setup_logging


@pytest.fixture(scope="session")
def test_config():
    """Provide a test configuration."""
    config = Config()

    # Note: Config properties are read-only, so we can't override them
    # The config will use the actual config.toml file or defaults
    return config


@pytest.fixture(scope="session")
def temp_dir():
    """Provide a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture(scope="function")
def mock_audio_file(temp_dir):
    """Provide a mock audio file path."""
    audio_file = Path(temp_dir) / "test_audio.wav"
    # Create a minimal WAV file header
    with open(audio_file, "wb") as f:
        f.write(b"RIFF")
        f.write((36).to_bytes(4, "little"))  # File size
        f.write(b"WAVE")
        f.write(b"fmt ")
        f.write((16).to_bytes(4, "little"))  # Chunk size
        f.write((1).to_bytes(2, "little"))  # Audio format (PCM)
        f.write((1).to_bytes(2, "little"))  # Channels
        f.write((16000).to_bytes(4, "little"))  # Sample rate
        f.write((32000).to_bytes(4, "little"))  # Byte rate
        f.write((2).to_bytes(2, "little"))  # Block align
        f.write((16).to_bytes(2, "little"))  # Bits per sample
        f.write(b"data")
        f.write((0).to_bytes(4, "little"))  # Data size

    yield audio_file


@pytest.fixture(scope="function")
def mock_logger():
    """Provide a mock logger for testing."""
    with patch("src.utils.logger.get_logger") as mock_get_logger:
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        yield mock_logger


@pytest.fixture(scope="function")
def mock_system_tray():
    """Provide a mock system tray manager."""
    with patch("src.ui.system_tray.SystemTrayManager") as mock_tray:
        mock_tray_instance = Mock()
        mock_tray.return_value = mock_tray_instance
        mock_tray_instance.is_available.return_value = True
        yield mock_tray_instance


@pytest.fixture(scope="function")
def mock_notification_manager():
    """Provide a mock notification manager."""
    with patch("src.ui.notifications.NotificationManager") as mock_notif:
        mock_notif_instance = Mock()
        mock_notif.return_value = mock_notif_instance
        yield mock_notif_instance


@pytest.fixture(scope="function")
def mock_gui_manager():
    """Provide a mock GUI manager."""
    with patch("src.ui.gui.manager.GUIManager") as mock_gui:
        mock_gui_instance = Mock()
        mock_gui.return_value = mock_gui_instance
        yield mock_gui_instance


@pytest.fixture(scope="function")
def mock_input_handler():
    """Provide a mock input handler."""
    with patch("src.input.input_handler.InputHandler") as mock_input:
        mock_input_instance = Mock()
        mock_input.return_value = mock_input_instance
        yield mock_input_instance


@pytest.fixture(scope="function")
def mock_audio_recorder():
    """Provide a mock audio recorder."""
    with patch("src.audio.recorder.AudioRecorder") as mock_recorder:
        mock_recorder_instance = Mock()
        mock_recorder.return_value = mock_recorder_instance
        yield mock_recorder_instance


@pytest.fixture(scope="function")
def mock_speech_to_text():
    """Provide a mock speech-to-text engine."""
    with patch("src.lang.stt.SpeechToText") as mock_stt:
        mock_stt_instance = Mock()
        mock_stt.return_value = mock_stt_instance
        mock_stt_instance.transcribe.return_value = "Test transcription"
        yield mock_stt_instance


@pytest.fixture(scope="function")
def mock_spell_checker():
    """Provide a mock spell checker."""
    with patch("src.lang.spell_checker.SpellChecker") as mock_spell:
        mock_spell_instance = Mock()
        mock_spell.return_value = mock_spell_instance
        mock_spell_instance.correct.return_value = "corrected text"
        yield mock_spell_instance


@pytest.fixture(scope="function")
def mock_volume_controller():
    """Provide a mock volume controller."""
    with patch("src.audio.volume_controller.VolumeController") as mock_volume:
        mock_volume_instance = Mock()
        mock_volume.return_value = mock_volume_instance
        yield mock_volume_instance


@pytest.fixture(scope="function")
def mock_database():
    """Provide a mock audio database."""
    with patch("src.utils.database.AudioDatabase") as mock_db:
        mock_db_instance = Mock()
        mock_db.return_value = mock_db_instance
        yield mock_db_instance


@pytest.fixture(scope="function")
def mock_transcription_queue():
    """Provide a mock transcription queue."""
    with patch("src.core.simple_queue.SimpleTranscriptionQueue") as mock_queue:
        mock_queue_instance = Mock()
        mock_queue.return_value = mock_queue_instance
        yield mock_queue_instance


@pytest.fixture(scope="function")
def mock_singleton():
    """Provide a mock system-wide singleton."""
    with patch("src.utils.singleton.SystemWideSingleton") as mock_singleton:
        mock_singleton_instance = Mock()
        mock_singleton.return_value = mock_singleton_instance
        mock_singleton_instance.acquire.return_value = True
        mock_singleton_instance.is_running.return_value = False
        yield mock_singleton_instance


def pytest_configure(config):
    """Configure pytest for Mauscribe tests."""
    # Disable logging during tests
    setup_logging()

    # Add custom markers
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "audio: mark test as requiring audio hardware")
    config.addinivalue_line("markers", "gui: mark test as requiring GUI")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers."""
    for item in items:
        # Add unit marker to tests in unit/ directory
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        # Add integration marker to tests in integration/ directory
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
