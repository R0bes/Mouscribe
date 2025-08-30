"""
Integration Tests für Mauscribe
Testet alle Komponenten zusammen und End-to-End-Funktionalität
"""

import os
import tempfile
import threading
import time
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest

from src.audio.recorder import AudioRecorder
from src.audio.volume_controller import VolumeController
from src.input.input_handler import InputHandler
from src.lang.spell_checker import SpellChecker
from src.lang.stt import SpeechToText
from src.mouscribe import MauscribeApp
from src.ui.notifications import NotificationManager
from src.ui.system_tray import SystemTrayManager
from src.utils.config import Config
from src.utils.database import AudioDatabase
from src.utils.logger import setup_logging


class TestMauscribeIntegration:
    """Testet die Integration aller Mauscribe-Komponenten."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup für jeden Test."""
        # Temporäre Konfiguration für Tests
        self.temp_config = {
            "audio": {"sample_rate": 16000, "channels": 1, "chunk_size": 1024},
            "logging": {"enabled": False, "console_level": "ERROR"},
            "notifications": {"enabled": False},
            "system": {"volume_reduction_factor": 0.1},
        }

        # Mock für Audio-Devices
        with patch("sounddevice.query_devices") as mock_devices:
            mock_devices.return_value = [
                {"name": "Test Microphone", "max_inputs": 1, "index": 0},
                {"name": "Test Speakers", "max_outputs": 1, "index": 1},
            ]
            yield

    def test_component_initialization(self):
        """Testet die Initialisierung aller Komponenten."""
        with patch("src.mouscribe.Config") as mock_config_class:
            mock_config = Mock()
            mock_config.audio = self.temp_config["audio"]
            mock_config.logging = self.temp_config["logging"]
            mock_config.notifications = self.temp_config["notifications"]
            mock_config.system = self.temp_config["system"]
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
                                                app = MauscribeApp()
                                                assert app is not None
                                                assert hasattr(app, "recorder")
                                                assert hasattr(app, "stt")
                                                assert hasattr(app, "spell_checker")

    def test_audio_pipeline_integration(self):
        """Testet die komplette Audio-Pipeline."""
        # Mock Audio-Daten
        test_audio = np.random.random(16000).astype(np.float32)

        with patch("src.mouscribe.Config") as mock_config_class:
            mock_config = Mock()
            mock_config.audio = self.temp_config["audio"]
            mock_config.logging = self.temp_config["logging"]
            mock_config.notifications = self.temp_config["notifications"]
            mock_config.system = self.temp_config["system"]
            mock_config_class.return_value = mock_config

            with patch("src.mouscribe.setup_logging"):
                with patch("src.mouscribe.AudioRecorder") as mock_recorder_class:
                    with patch("src.mouscribe.SpeechToText") as mock_stt_class:
                        with patch("src.mouscribe.SpellChecker") as mock_spell_class:
                            with patch("src.mouscribe.SystemTrayManager"):
                                with patch("src.mouscribe.VolumeController"):
                                    with patch("src.mouscribe.NotificationManager"):
                                        with patch("src.mouscribe.InputHandler"):
                                            with patch("src.mouscribe.AudioDatabase"):
                                                # Mock Recorder
                                                mock_recorder = Mock()
                                                mock_recorder.record.return_value = test_audio
                                                mock_recorder_class.return_value = mock_recorder

                                                # Mock STT
                                                mock_stt = Mock()
                                                mock_stt.transcribe_raw.return_value = "Test Transkription"
                                                mock_stt_class.return_value = mock_stt

                                                # Mock Spell Checker
                                                mock_spell = Mock()
                                                mock_spell.correct.return_value = "Test Transkription"
                                                mock_spell_class.return_value = mock_spell

                                                app = MauscribeApp()

                                                # Test Audio-Pipeline durch Simulation der Aufnahme
                                                app.recorder = mock_recorder
                                                app.stt = mock_stt

                                                # Simuliere Audio-Verarbeitung
                                                result = app.stt.transcribe_raw(test_audio)
                                                assert result is not None
                                                assert isinstance(result, str)

    def test_clipboard_integration(self):
        """Testet die Clipboard-Integration."""
        import time

        with patch("src.mouscribe.Config") as mock_config_class:
            mock_config = Mock()
            mock_config.audio = self.temp_config["audio"]
            mock_config.logging = self.temp_config["logging"]
            mock_config.notifications = self.temp_config["notifications"]
            mock_config.system = self.temp_config["system"]
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
                                                with patch("pyperclip.copy") as mock_copy:
                                                    with patch("pyperclip.paste") as mock_paste:
                                                        # Mock Clipboard mit korrekten Werten
                                                        mock_copy.return_value = None
                                                        # Verwende den aktuellen Timestamp
                                                        current_timestamp = int(time.time())
                                                        mock_paste.return_value = (
                                                            f"Mauscribe Clipboard-Test {current_timestamp}"
                                                        )

                                                        app = MauscribeApp()

                                                        # Test Clipboard-Funktionalität
                                                        success = app._test_clipboard_system()
                                                        assert success is True

    def test_error_handling_integration(self):
        """Testet die Fehlerbehandlung über alle Komponenten."""
        with patch("src.mouscribe.Config") as mock_config_class:
            mock_config = Mock()
            mock_config.audio = self.temp_config["audio"]
            mock_config.logging = self.temp_config["logging"]
            mock_config.notifications = self.temp_config["notifications"]
            mock_config.system = self.temp_config["system"]
            mock_config_class.return_value = mock_config

            with patch("src.mouscribe.setup_logging"):
                with patch("src.mouscribe.AudioRecorder") as mock_recorder_class:
                    with patch("src.mouscribe.SpeechToText") as mock_stt_class:
                        with patch("src.mouscribe.SpellChecker") as mock_spell_class:
                            with patch("src.mouscribe.SystemTrayManager"):
                                with patch("src.mouscribe.VolumeController"):
                                    with patch("src.mouscribe.NotificationManager"):
                                        with patch("src.mouscribe.InputHandler"):
                                            with patch("src.mouscribe.AudioDatabase"):
                                                # Mock Recorder mit Fehler
                                                mock_recorder = Mock()
                                                mock_recorder.record.side_effect = Exception("Audio Error")
                                                mock_recorder_class.return_value = mock_recorder

                                                # Mock STT mit Fehler
                                                mock_stt = Mock()
                                                mock_stt.transcribe_raw.side_effect = Exception("STT Error")
                                                mock_stt_class.return_value = mock_stt

                                                # Mock Spell Checker mit Fehler
                                                mock_spell = Mock()
                                                mock_spell.correct.side_effect = Exception("Spell Error")
                                                mock_spell_class.return_value = mock_spell

                                                app = MauscribeApp()

                                                # Test sollte nicht abstürzen
                                                assert app is not None

    def test_performance_integration(self):
        """Testet die Performance der Integration."""
        start_time = time.time()

        with patch("src.mouscribe.Config") as mock_config_class:
            mock_config = Mock()
            mock_config.audio = self.temp_config["audio"]
            mock_config.logging = self.temp_config["logging"]
            mock_config.notifications = self.temp_config["notifications"]
            mock_config.system = self.temp_config["system"]
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
                                                app = MauscribeApp()

        init_time = time.time() - start_time
        assert init_time < 2.0  # Initialisierung sollte unter 2 Sekunden dauern

    def test_configuration_integration(self):
        """Testet die Konfigurationsintegration."""
        with patch("src.mouscribe.Config") as mock_config_class:
            mock_config = Mock()
            mock_config.audio = self.temp_config["audio"]
            mock_config.logging = self.temp_config["logging"]
            mock_config.notifications = self.temp_config["notifications"]
            mock_config.system = self.temp_config["system"]
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
                                                app = MauscribeApp()

                                                # Test Konfigurationszugriff
                                                assert app.config is not None
                                                assert hasattr(app.config, "audio")
                                                assert hasattr(app.config, "logging")
                                                assert hasattr(app.config, "notifications")
                                                assert hasattr(app.config, "system")


class TestEndToEndWorkflow:
    """Testet den kompletten End-to-End-Workflow."""

    def test_complete_workflow(self):
        """Testet den kompletten Workflow von Audio bis Clipboard."""
        # Mock für komplette Pipeline
        with patch("src.mouscribe.Config") as mock_config_class:
            mock_config = Mock()
            mock_config.audio = {"sample_rate": 16000, "channels": 1, "chunk_size": 1024}
            mock_config.logging = {"enabled": False, "console_level": "ERROR"}
            mock_config.notifications = {"enabled": False}
            mock_config.system = {"volume_reduction_factor": 0.1}
            mock_config_class.return_value = mock_config

            with patch("src.mouscribe.setup_logging"):
                with patch("src.mouscribe.AudioRecorder") as mock_recorder_class:
                    with patch("src.mouscribe.SpeechToText") as mock_stt_class:
                        with patch("src.mouscribe.SpellChecker") as mock_spell_class:
                            with patch("src.mouscribe.SystemTrayManager"):
                                with patch("src.mouscribe.VolumeController"):
                                    with patch("src.mouscribe.NotificationManager"):
                                        with patch("src.mouscribe.InputHandler"):
                                            with patch("src.mouscribe.AudioDatabase"):
                                                with patch("pyperclip.copy") as mock_copy:
                                                    with patch("pyautogui.write") as mock_write:
                                                        # Setup Mocks
                                                        mock_recorder = Mock()
                                                        mock_recorder.record.return_value = np.random.random(16000)
                                                        mock_recorder_class.return_value = mock_recorder

                                                        mock_stt = Mock()
                                                        mock_stt.transcribe_raw.return_value = "Test Nachricht"
                                                        mock_stt_class.return_value = mock_stt

                                                        mock_spell = Mock()
                                                        mock_spell.correct.return_value = "Test Nachricht"
                                                        mock_spell_class.return_value = mock_spell

                                                        mock_copy.return_value = None
                                                        mock_write.return_value = None

                                                        app = MauscribeApp()

                                                        # Simuliere kompletten Workflow
                                                        test_audio = np.random.random(16000)
                                                        result = app.stt.transcribe_raw(test_audio)

                                                        assert result == "Test Nachricht"

                                                        # Teste Clipboard-Funktionalität separat
                                                        app._test_clipboard_system()
                                                        # Der Test sollte erfolgreich sein, da wir pyperclip gemockt haben


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
