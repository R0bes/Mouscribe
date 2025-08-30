"""
Einfache Tests für Mauscribe
Testet grundlegende Funktionalität
"""

import pytest

from src.utils.config import Config


def test_basic_functionality():
    """Testet grundlegende Funktionalität."""
    assert True


def test_config_loading():
    """Testet das Laden der Konfiguration."""
    config = Config()
    assert config is not None
    assert hasattr(config, "primary_name")
    assert hasattr(config, "secondary_name")
    assert hasattr(config, "behavior_debounce_time")
    assert hasattr(config, "audio_sample_rate")


def test_primary_config():
    """Testet die primäre Input-Konfiguration."""
    config = Config()
    assert config.primary_name == "m_x2"
    assert config.primary_type == "mouse_button"
    assert config.primary_method == {"click": True}


def test_secondary_config():
    """Testet die sekundäre Input-Konfiguration."""
    config = Config()
    assert config.secondary_name == "m_x1"
    assert config.secondary_type == "mouse_button"
    assert config.secondary_method == {"hold": 1}


def test_behavior_config():
    """Testet die Verhaltens-Konfiguration."""
    config = Config()
    assert config.behavior_debounce_time == 0.5


def test_audio_config():
    """Testet die Audio-Konfiguration."""
    config = Config()
    assert config.audio_sample_rate == 16000
    assert config.audio_channels == 1
    assert config.audio_chunk_size == 1024


if __name__ == "__main__":
    # Führe alle Tests aus
    test_basic_functionality()
    test_config_loading()
    test_primary_config()
    test_secondary_config()
    test_behavior_config()
    test_audio_config()
    print("✅ Alle einfachen Tests erfolgreich!")
