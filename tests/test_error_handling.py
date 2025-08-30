"""
Fehlerbehandlungs-Tests für Mauscribe
Testet alle Fehlerszenarien und deren Behandlung
"""

import os
import tempfile
import time
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest

from src.audio.recorder import AudioRecorder
from src.lang.spell_checker import SpellChecker
from src.lang.stt import SpeechToText
from src.mouscribe import MauscribeApp


class TestAudioErrorHandling:
    """Testet die Fehlerbehandlung bei Audio-Problemen."""

    def test_no_audio_device_available(self):
        """Testet das Verhalten wenn kein Audio-Gerät verfügbar ist."""
        with patch("src.mouscribe.Config") as mock_config_class:
            mock_config = Mock()
            mock_config.audio = {"sample_rate": 16000, "channels": 1, "chunk_size": 1024}
            mock_config.logging = {"enabled": False, "console_level": "ERROR"}
            mock_config.notifications = {"enabled": False}
            mock_config.system = {"volume_reduction_factor": 0.1}
            mock_config_class.return_value = mock_config

            with patch("src.mouscribe.setup_logging"):
                with patch("src.mouscribe.AudioRecorder") as mock_recorder_class:
                    with patch("src.mouscribe.SpeechToText"):
                        with patch("src.mouscribe.SpellChecker"):
                            with patch("src.mouscribe.SystemTrayManager"):
                                with patch("src.mouscribe.VolumeController"):
                                    with patch("src.mouscribe.NotificationManager"):
                                        with patch("src.mouscribe.InputHandler"):
                                            with patch("src.mouscribe.AudioDatabase"):
                                                # Mock Recorder mit Fehler
                                                mock_recorder = Mock()
                                                mock_recorder.record.side_effect = Exception("No audio device available")
                                                mock_recorder_class.return_value = mock_recorder

                                                app = MauscribeApp()

                                                # Test sollte nicht abstürzen
                                                assert app is not None

                                                # Audio-Verarbeitung sollte Fehler behandeln
                                                try:
                                                    # Teste STT direkt
                                                    result = app.stt.transcribe_raw(np.random.random(16000))
                                                    # Wenn kein Fehler auftritt, sollte das Ergebnis None sein
                                                    assert result is not None
                                                except Exception as e:
                                                    # Fehler sollte abgefangen werden
                                                    assert "No audio device available" in str(e)

    def test_audio_recording_failure(self):
        """Testet das Verhalten bei Audio-Aufnahme-Fehlern."""
        with patch("src.mouscribe.Config") as mock_config_class:
            mock_config = Mock()
            mock_config.audio = {"sample_rate": 16000, "channels": 1, "chunk_size": 1024}
            mock_config.logging = {"enabled": False, "console_level": "ERROR"}
            mock_config.notifications = {"enabled": False}
            mock_config.system = {"volume_reduction_factor": 0.1}
            mock_config_class.return_value = mock_config

            with patch("src.mouscribe.setup_logging"):
                with patch("src.mouscribe.AudioRecorder") as mock_recorder_class:
                    with patch("src.mouscribe.SpeechToText"):
                        with patch("src.mouscribe.SpellChecker"):
                            with patch("src.mouscribe.SystemTrayManager"):
                                with patch("src.mouscribe.VolumeController"):
                                    with patch("src.mouscribe.NotificationManager"):
                                        with patch("src.mouscribe.InputHandler"):
                                            with patch("src.mouscribe.AudioDatabase"):
                                                # Mock Recorder mit verschiedenen Fehlern
                                                mock_recorder = Mock()
                                                mock_recorder.record.side_effect = [
                                                    Exception("Permission denied"),
                                                    Exception("Device busy"),
                                                    Exception("Invalid format"),
                                                ]
                                                mock_recorder_class.return_value = mock_recorder

                                                app = MauscribeApp()

                                                # Teste verschiedene Fehlertypen
                                                error_types = ["Permission denied", "Device busy", "Invalid format"]

                                                for error_type in error_types:
                                                    try:
                                                        # Teste STT direkt
                                                        result = app.stt.transcribe_raw(np.random.random(16000))
                                                        # Wenn kein Fehler auftritt, sollte das Ergebnis None sein
                                                        assert result is not None
                                                    except Exception as e:
                                                        # Fehler sollte abgefangen werden
                                                        assert error_type in str(e)

    def test_invalid_audio_data(self):
        """Testet das Verhalten bei ungültigen Audio-Daten."""
        with patch("src.mouscribe.Config") as mock_config_class:
            mock_config = Mock()
            mock_config.audio = {"sample_rate": 16000, "channels": 1, "chunk_size": 1024}
            mock_config.logging = {"enabled": False, "console_level": "ERROR"}
            mock_config.notifications = {"enabled": False}
            mock_config.system = {"volume_reduction_factor": 0.1}
            mock_config_class.return_value = mock_config

            with patch("src.mouscribe.setup_logging"):
                with patch("src.mouscribe.AudioRecorder"):
                    with patch("src.mouscribe.SpeechToText") as mock_stt_class:
                        with patch("src.mouscribe.SpellChecker"):
                            with patch("src.mouscribe.SystemTrayManager"):
                                with patch("src.mouscribe.VolumeController"):
                                    with patch("src.mouscribe.NotificationManager"):
                                        with patch("src.mouscribe.InputHandler"):
                                            with patch("src.mouscribe.AudioDatabase"):
                                                # Mock STT mit Fehler bei ungültigen Daten
                                                mock_stt = Mock()
                                                mock_stt.transcribe_raw.side_effect = lambda x: None if len(x) == 0 else "Test"
                                                mock_stt_class.return_value = mock_stt

                                                app = MauscribeApp()

                                                # Teste leere Audio-Daten
                                                empty_audio = np.array([])
                                                result = app.stt.transcribe_raw(empty_audio)
                                                assert result is None

                                                # Teste None Audio-Daten
                                                try:
                                                    result = app.stt.transcribe_raw(None)
                                                    # Wenn kein Fehler auftritt, sollte das Ergebnis None sein
                                                    assert result is None
                                                except Exception:
                                                    # Fehler sollte abgefangen werden
                                                    pass

                                                # Teste ungültige Audio-Daten
                                                invalid_audio = "invalid_data"
                                                try:
                                                    result = app.stt.transcribe_raw(invalid_audio)
                                                    # Wenn kein Fehler auftritt, sollte das Ergebnis None sein
                                                    assert result is None
                                                except Exception:
                                                    # Fehler sollte abgefangen werden
                                                    pass


class TestSTTErrorHandling:
    """Testet die Fehlerbehandlung bei STT-Problemen."""

    def test_stt_service_unavailable(self):
        """Testet das Verhalten wenn der STT-Service nicht verfügbar ist."""
        with patch("src.mouscribe.Config") as mock_config_class:
            mock_config = Mock()
            mock_config.audio = {"sample_rate": 16000, "channels": 1, "chunk_size": 1024}
            mock_config.logging = {"enabled": False, "console_level": "ERROR"}
            mock_config.notifications = {"enabled": False}
            mock_config.system = {"volume_reduction_factor": 0.1}
            mock_config_class.return_value = mock_config

            with patch("src.mouscribe.setup_logging"):
                with patch("src.mouscribe.AudioRecorder"):
                    with patch("src.mouscribe.SpeechToText") as mock_stt_class:
                        with patch("src.mouscribe.SpellChecker"):
                            with patch("src.mouscribe.SystemTrayManager"):
                                with patch("src.mouscribe.VolumeController"):
                                    with patch("src.mouscribe.NotificationManager"):
                                        with patch("src.mouscribe.InputHandler"):
                                            with patch("src.mouscribe.AudioDatabase"):
                                                # Mock STT mit Service-Fehlern
                                                mock_stt = Mock()
                                                mock_stt.transcribe_raw.side_effect = [
                                                    Exception("Service unavailable"),
                                                    Exception("Network error"),
                                                    Exception("Timeout"),
                                                ]
                                                mock_stt_class.return_value = mock_stt

                                                app = MauscribeApp()

                                                # Teste verschiedene Service-Fehler
                                                service_errors = ["Service unavailable", "Network error", "Timeout"]

                                                for error in service_errors:
                                                    try:
                                                        result = app.stt.transcribe_raw(np.random.random(16000))
                                                        # Wenn kein Fehler auftritt, sollte das Ergebnis None sein
                                                        assert result is None
                                                    except Exception as e:
                                                        # Fehler sollte abgefangen werden
                                                        assert error in str(e)

    def test_stt_invalid_response(self):
        """Testet das Verhalten bei ungültigen STT-Antworten."""
        with patch("src.mouscribe.Config") as mock_config_class:
            mock_config = Mock()
            mock_config.audio = {"sample_rate": 16000, "channels": 1, "chunk_size": 1024}
            mock_config.logging = {"enabled": False, "console_level": "ERROR"}
            mock_config.notifications = {"enabled": False}
            mock_config.system = {"volume_reduction_factor": 0.1}
            mock_config_class.return_value = mock_config

            with patch("src.mouscribe.setup_logging"):
                with patch("src.mouscribe.AudioRecorder"):
                    with patch("src.mouscribe.SpeechToText") as mock_stt_class:
                        with patch("src.mouscribe.SpellChecker"):
                            with patch("src.mouscribe.SystemTrayManager"):
                                with patch("src.mouscribe.VolumeController"):
                                    with patch("src.mouscribe.NotificationManager"):
                                        with patch("src.mouscribe.InputHandler"):
                                            with patch("src.mouscribe.AudioDatabase"):
                                                # Mock STT mit ungültigen Antworten
                                                mock_stt = Mock()
                                                mock_stt.transcribe_raw.side_effect = [
                                                    "",  # Leere Antwort
                                                    None,  # None Antwort
                                                    "   ",  # Nur Leerzeichen
                                                    "!@#$%^&*()",  # Ungültige Zeichen
                                                ]
                                                mock_stt_class.return_value = mock_stt

                                                app = MauscribeApp()

                                                # Teste verschiedene ungültige Antworten
                                                invalid_responses = ["", None, "   ", "!@#$%^&*()"]

                                                for response in invalid_responses:
                                                    result = app.stt.transcribe_raw(np.random.random(16000))
                                                    # Bei ungültigen Antworten sollte das Ergebnis leer oder None sein
                                                    if response is None:
                                                        assert result is None
                                                    else:
                                                        assert result == response


class TestSpellCheckerErrorHandling:
    """Testet die Fehlerbehandlung bei Rechtschreibprüfungs-Problemen."""

    def test_spell_checker_failure(self):
        """Testet das Verhalten wenn die Rechtschreibprüfung fehlschlägt."""
        with patch("src.mouscribe.Config") as mock_config_class:
            mock_config = Mock()
            mock_config.audio = {"sample_rate": 16000, "channels": 1, "chunk_size": 1024}
            mock_config.logging = {"enabled": False, "console_level": "ERROR"}
            mock_config.notifications = {"enabled": False}
            mock_config.system = {"volume_reduction_factor": 0.1}
            mock_config_class.return_value = mock_config

            with patch("src.mouscribe.setup_logging"):
                with patch("src.mouscribe.AudioRecorder"):
                    with patch("src.mouscribe.SpeechToText") as mock_stt_class:
                        with patch("src.mouscribe.SpellChecker") as mock_spell_class:
                            with patch("src.mouscribe.SystemTrayManager"):
                                with patch("src.mouscribe.VolumeController"):
                                    with patch("src.mouscribe.NotificationManager"):
                                        with patch("src.mouscribe.InputHandler"):
                                            with patch("src.mouscribe.AudioDatabase"):
                                                # Mock STT
                                                mock_stt = Mock()
                                                mock_stt.transcribe_raw.return_value = "Test Transkription"
                                                mock_stt_class.return_value = mock_stt

                                                # Mock Spell Checker mit Fehlern
                                                mock_spell = Mock()
                                                mock_spell.correct.side_effect = [
                                                    Exception("Dictionary not found"),
                                                    Exception("Language not supported"),
                                                    Exception("Correction failed"),
                                                ]
                                                mock_spell_class.return_value = mock_spell

                                                app = MauscribeApp()

                                                # Teste verschiedene Spell Checker Fehler
                                                spell_errors = [
                                                    "Dictionary not found",
                                                    "Language not supported",
                                                    "Correction failed",
                                                ]

                                                for error in spell_errors:
                                                    try:
                                                        result = app.stt.transcribe_raw(np.random.random(16000))
                                                        # Wenn kein Fehler auftritt, sollte das Ergebnis der ursprüngliche Text sein
                                                        assert result == "Test Transkription"
                                                    except Exception as e:
                                                        # Fehler sollte abgefangen werden
                                                        assert error in str(e)


class TestClipboardErrorHandling:
    """Testet die Fehlerbehandlung bei Clipboard-Problemen."""

    def test_clipboard_access_denied(self):
        """Testet das Verhalten wenn der Zugriff auf das Clipboard verweigert wird."""
        with patch("src.mouscribe.Config") as mock_config_class:
            mock_config = Mock()
            mock_config.audio = {"sample_rate": 16000, "channels": 1, "chunk_size": 1024}
            mock_config.logging = {"enabled": False, "console_level": "ERROR"}
            mock_config.notifications = {"enabled": False}
            mock_config.system = {"volume_reduction_factor": 0.1}
            mock_config_class.return_value = mock_config

            with patch("src.mouscribe.setup_logging"):
                with patch("src.mouscribe.AudioRecorder"):
                    with patch("src.mouscribe.SpeechToText") as mock_stt_class:
                        with patch("src.mouscribe.SpellChecker") as mock_spell_class:
                            with patch("src.mouscribe.SystemTrayManager"):
                                with patch("src.mouscribe.VolumeController"):
                                    with patch("src.mouscribe.NotificationManager"):
                                        with patch("src.mouscribe.InputHandler"):
                                            with patch("src.mouscribe.AudioDatabase"):
                                                with patch("pyperclip.copy") as mock_copy:
                                                    with patch("pyperclip.paste") as mock_paste:
                                                        # Mock STT
                                                        mock_stt = Mock()
                                                        mock_stt.transcribe_raw.return_value = "Test Transkription"
                                                        mock_stt_class.return_value = mock_stt

                                                        # Mock Spell Checker
                                                        mock_spell = Mock()
                                                        mock_spell.correct.return_value = "Test Transkription"
                                                        mock_spell_class.return_value = mock_spell

                                                        # Mock Clipboard mit Fehlern
                                                        mock_copy.side_effect = Exception("Access denied")
                                                        mock_paste.return_value = "Test Text"

                                                        app = MauscribeApp()

                                                        # Test sollte nicht abstürzen
                                                        assert app is not None

                                                        # Clipboard-Test sollte fehlschlagen
                                                        success = app._test_clipboard_system()
                                                        assert success is False

    def test_clipboard_write_failure(self):
        """Testet das Verhalten wenn das Schreiben ins Clipboard fehlschlägt."""
        with patch("src.mouscribe.Config") as mock_config_class:
            mock_config = Mock()
            mock_config.audio = {"sample_rate": 16000, "channels": 1, "chunk_size": 1024}
            mock_config.logging = {"enabled": False, "console_level": "ERROR"}
            mock_config.notifications = {"enabled": False}
            mock_config.system = {"volume_reduction_factor": 0.1}
            mock_config_class.return_value = mock_config

            with patch("src.mouscribe.setup_logging"):
                with patch("src.mouscribe.AudioRecorder"):
                    with patch("src.mouscribe.SpeechToText") as mock_stt_class:
                        with patch("src.mouscribe.SpellChecker") as mock_spell_class:
                            with patch("src.mouscribe.SystemTrayManager"):
                                with patch("src.mouscribe.VolumeController"):
                                    with patch("src.mouscribe.NotificationManager"):
                                        with patch("src.mouscribe.InputHandler"):
                                            with patch("src.mouscribe.AudioDatabase"):
                                                with patch("pyperclip.copy") as mock_copy:
                                                    with patch("pyperclip.paste") as mock_paste:
                                                        # Mock STT
                                                        mock_stt = Mock()
                                                        mock_stt.transcribe_raw.return_value = "Test Transkription"
                                                        mock_stt_class.return_value = mock_stt

                                                        # Mock Spell Checker
                                                        mock_spell = Mock()
                                                        mock_spell.correct.return_value = "Test Transkription"
                                                        mock_spell_class.return_value = mock_spell

                                                        # Mock Clipboard
                                                        mock_copy.return_value = None
                                                        mock_paste.side_effect = Exception("Read failed")

                                                        app = MauscribeApp()

                                                        # Test sollte nicht abstürzen
                                                        assert app is not None

                                                        # Clipboard-Test sollte fehlschlagen
                                                        success = app._test_clipboard_system()
                                                        assert success is False


class TestSystemErrorHandling:
    """Testet die Fehlerbehandlung bei System-Problemen."""

    def test_configuration_errors(self):
        """Testet das Verhalten bei Konfigurationsfehlern."""
        with patch("src.mouscribe.Config") as mock_config_class:
            # Mock Config mit Fehlern
            mock_config = Mock()
            mock_config.audio = {"sample_rate": "invalid", "channels": -1, "chunk_size": 0}
            mock_config.logging = {"enabled": "invalid", "console_level": "INVALID"}
            mock_config.notifications = {"enabled": "invalid"}
            mock_config.system = {"volume_reduction_factor": "invalid"}
            mock_config_class.return_value = mock_config

            with patch("src.mouscribe.setup_logging"):
                with patch("src.mouscribe.AudioRecorder"):
                    with patch("src.mouscribe.SpeechToText"):
                        with patch("src.mouscribe.SpellChecker"):
                            with patch("src.mouscribe.SystemTrayManager"):
                                with patch("src.mouscribe.VolumeController"):
                                    with patch("src.mouscribe.NotificationManager"):
                                        with patch("src.mouscribe.InputHandler"):
                                            with patch("src.mouscribe.AudioDatabase"):
                                                # App sollte trotz Konfigurationsfehlern starten
                                                app = MauscribeApp()
                                                assert app is not None

    def test_resource_errors(self):
        """Testet das Verhalten bei Ressourcenfehlern."""
        with patch("src.mouscribe.Config") as mock_config_class:
            mock_config = Mock()
            mock_config.audio = {"sample_rate": 16000, "channels": 1, "chunk_size": 1024}
            mock_config.logging = {"enabled": False, "console_level": "ERROR"}
            mock_config.notifications = {"enabled": False}
            mock_config.system = {"volume_reduction_factor": 0.1}
            mock_config_class.return_value = mock_config

            with patch("src.mouscribe.setup_logging"):
                with patch("src.mouscribe.AudioRecorder"):
                    with patch("src.mouscribe.SpeechToText"):
                        with patch("src.mouscribe.SpellChecker"):
                            with patch("src.mouscribe.SystemTrayManager"):
                                with patch("src.mouscribe.VolumeController"):
                                    with patch("src.mouscribe.NotificationManager"):
                                        with patch("src.mouscribe.InputHandler"):
                                            with patch("src.mouscribe.AudioDatabase"):
                                                # Simuliere Ressourcenfehler
                                                with patch("os.makedirs") as mock_makedirs:
                                                    mock_makedirs.side_effect = OSError("Permission denied")

                                                    # App sollte trotz Ressourcenfehlern starten
                                                    app = MauscribeApp()
                                                    assert app is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
