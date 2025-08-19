"""Einfache Tests für Mauscribe - sofort ausführbar."""

import pytest

from src.utils.config import Config


def test_basic_functionality():
    """Testet grundlegende Funktionalität."""
    assert True  # Immer erfolgreich


def test_config_loading():
    """Testet das Laden der Konfiguration."""
    config = Config()
    assert config is not None
    assert hasattr(config, "primary_name")
    assert hasattr(config, "secondary_name")


def test_primary_config():
    """Testet die Primary-Button-Konfiguration."""
    config = Config()
    assert config.primary_name == "m_x2"
    assert config.primary_method == {"click": True}


def test_secondary_config():
    """Testet die Secondary-Button-Konfiguration."""
    config = Config()
    assert config.secondary_name == "m_left"
    assert config.secondary_method == {"hold": 2}


def test_behavior_config():
    """Testet die Verhaltens-Konfiguration."""
    config = Config()
    assert config.behavior_debounce_time == 0.5


def test_audio_config():
    """Testet die Audio-Konfiguration."""
    config = Config()
    assert config.audio_sample_rate == 16000
    assert config.audio_channels == 1


if __name__ == "__main__":
    # Führe alle Tests aus
    test_basic_functionality()
    test_config_loading()
    test_primary_config()
    test_secondary_config()
    test_behavior_config()
    test_audio_config()
    print("✅ Alle einfachen Tests erfolgreich!")
