"""
Basic tests for Mauscribe
"""
import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_imports():
    """Test that main modules can be imported"""
    try:
        from src.utils.settings import Settings
        from src.utils.logger import get_logger
        from src.audio.recorder import Recorder
        from src.audio.transcriptor import Transcriptor
        from src.ui.notifications import Toaster
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")

def test_settings_loading():
    """Test that settings can be loaded"""
    try:
        from src.utils.settings import Settings
        settings = Settings()
        assert settings is not None
        assert hasattr(settings, 'primary_name')
        assert hasattr(settings, 'secondary_name')
    except Exception as e:
        pytest.fail(f"Settings loading failed: {e}")

def test_logger_creation():
    """Test that logger can be created"""
    try:
        from src.utils.logger import get_logger
        logger = get_logger("test")
        assert logger is not None
    except Exception as e:
        pytest.fail(f"Logger creation failed: {e}")

def test_notification_system():
    """Test that notification system can be initialized"""
    try:
        from src.ui.notifications import Toaster
        toaster = Toaster(enabled=False)  # Disabled for testing
        assert toaster is not None
        assert toaster.enabled == False
    except Exception as e:
        pytest.fail(f"Notification system initialization failed: {e}")

def test_audio_components():
    """Test that audio components can be initialized"""
    try:
        from src.audio.recorder import Recorder
        from src.audio.transcriptor import Transcriptor
        
        # Test recorder initialization
        recorder = Recorder()
        assert recorder is not None
        
        # Test transcriptor initialization
        transcriptor = Transcriptor()
        assert transcriptor is not None
        
    except Exception as e:
        pytest.fail(f"Audio components initialization failed: {e}")

if __name__ == "__main__":
    pytest.main([__file__])
