"""Tests für die Konfigurationsfunktionalität von Mauscribe."""

import pytest

from src.utils.config import Config


class TestConfig:
    """Test-Klasse für die Konfigurationsverwaltung."""

    def test_primary_configuration(self):
        """Testet die Primary-Button-Konfiguration."""
        config = Config()

        # Teste Primary-Button-Einstellungen
        assert config.primary_name == "m_x2"
        assert config.primary_method == {"click": True}

        # Teste, dass die Werte aus der config.toml gelesen werden
        assert isinstance(config.primary_name, str)
        assert isinstance(config.primary_method, dict)

    def test_secondary_configuration(self):
        """Testet die Secondary-Button-Konfiguration."""
        config = Config()

        # Teste Secondary-Button-Einstellungen
        assert config.secondary_name == "m_left"
        assert config.secondary_method == {"hold": 2}

        # Teste, dass die Werte aus der config.toml gelesen werden
        assert isinstance(config.secondary_name, str)
        assert isinstance(config.secondary_method, dict)

    def test_behavior_configuration(self):
        """Testet die Verhaltens-Konfiguration."""
        config = Config()

        # Teste Behavior-Einstellungen
        assert config.behavior_debounce_time == 0.5
        assert isinstance(config.behavior_debounce_time, float)

    def test_audio_configuration(self):
        """Testet die Audio-Konfiguration."""
        config = Config()

        # Teste Audio-Einstellungen
        assert config.audio_sample_rate == 16000
        assert config.audio_channels == 1
        assert config.audio_chunk_size == 1024
        assert config.audio_format == "int16"
        assert config.audio_device == 1

    def test_transcription_configuration(self):
        """Testet die Transkriptions-Konfiguration."""
        config = Config()

        # Teste Transkriptions-Einstellungen
        assert config.transcription_language == "de"
        assert config.transcription_whisper_model == "base"
        assert config.transcription_compute_type == "float32"

    def test_spell_check_configuration(self):
        """Testet die Rechtschreibprüfungs-Konfiguration."""
        config = Config()

        # Teste Rechtschreibprüfungs-Einstellungen
        assert config.spell_check_enabled is True
        assert config.spell_check_auto_correct is True

    def test_debug_configuration(self):
        """Testet die Debug-Konfiguration."""
        config = Config()

        # Teste Debug-Einstellungen
        assert config.debug_enabled is True
        assert config.debug_level == "DEBUG"
        assert config.debug_verbose is True
        assert config.debug_log_errors is True

    def test_legacy_compatibility(self):
        """Testet die Rückwärtskompatibilität mit alten Konfigurationen."""
        config = Config()

        # Teste Legacy-Eigenschaften
        assert config.mouse_button_primary == "m_x2"
        assert config.mouse_button_secondary == "m_left"
        assert config.keyboard_primary == "f9"
        assert config.keyboard_secondary == "shift+f9"

    def test_config_get_method(self):
        """Testet die interne _get Methode der Konfiguration."""
        config = Config()

        # Teste, dass Standardwerte zurückgegeben werden
        assert config._get("nonexistent.key", "default") == "default"

        # Teste, dass existierende Werte korrekt gelesen werden
        assert config._get("primary.name") == "m_x2"
        assert config._get("secondary.method.hold") == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
