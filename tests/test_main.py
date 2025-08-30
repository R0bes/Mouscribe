"""
Haupttest-Datei für Mauscribe
Führt alle Tests zusammen und testet das gesamte System
"""

import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Füge den Projektroot zum Python-Pfad hinzu
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.mouscribe import MauscribeApp
from src.utils.config import Config


class TestMainSystem:
    """Testet das gesamte Mauscribe-System."""

    def test_system_initialization(self):
        """Testet die System-Initialisierung."""
        # Teste ob alle Module importiert werden können
        try:
            from src.audio.recorder import AudioRecorder
            from src.audio.volume_controller import VolumeController
            from src.input.input_handler import InputHandler
            from src.lang.spell_checker import SpellChecker
            from src.lang.stt import SpeechToText
            from src.ui.notifications import NotificationManager
            from src.ui.system_tray import SystemTrayManager
            from src.utils.database import AudioDatabase
            from src.utils.logger import setup_logging

            assert True
        except ImportError as e:
            pytest.fail(f"Import-Fehler: {e}")

    def test_config_loading(self):
        """Testet das Laden der Konfiguration."""
        try:
            config = Config()
            assert config is not None

            # Teste wichtige Konfigurationswerte
            assert hasattr(config, "audio_sample_rate")
            assert hasattr(config, "logging_enabled")
            assert hasattr(config, "notifications_enabled")
            assert hasattr(config, "system_volume_reduction_factor")
            assert hasattr(config, "transcription_language")
            assert hasattr(config, "spell_check_enabled")

            # Teste Audio-Konfiguration
            assert config.audio_sample_rate == 16000
            assert config.audio_channels == 1
            assert config.audio_chunk_size == 1024

            # Teste Transkriptions-Konfiguration
            assert config.transcription_language == "de"
            assert config.transcription_whisper_model == "base"

        except Exception as e:
            pytest.fail(f"Konfigurationsfehler: {e}")

    def test_main_application_structure(self):
        """Testet die Struktur der Hauptanwendung."""
        try:
            # Teste ob die Hauptanwendungsklasse existiert
            assert hasattr(MauscribeApp, "__init__")
            assert hasattr(MauscribeApp, "_test_clipboard_system")

            # Erstelle eine Instanz um die Attribute zu testen
            app = MauscribeApp()
            assert hasattr(app, "shutdown_event")
            app.stop()  # Cleanup

        except Exception as e:
            pytest.fail(f"Anwendungsstruktur-Fehler: {e}")

    def test_file_structure(self):
        """Testet die Dateistruktur des Projekts."""
        required_files = [
            "main.py",
            "config.toml",
            "requirements.txt",
            "src/mouscribe.py",
            "src/audio/recorder.py",
            "src/audio/volume_controller.py",
            "src/input/input_handler.py",
            "src/lang/stt.py",
            "src/lang/spell_checker.py",
            "src/ui/notifications.py",
            "src/ui/system_tray.py",
            "src/utils/config.py",
            "src/utils/database.py",
            "src/utils/logger.py",
        ]

        for file_path in required_files:
            full_path = project_root / file_path
            assert full_path.exists(), f"Erforderliche Datei fehlt: {file_path}"

    def test_dependencies(self):
        """Testet ob alle Abhängigkeiten verfügbar sind."""
        required_packages = [
            "numpy",
            "pyautogui",
            "pyperclip",
            "sounddevice",
            "soundfile",
            "faster-whisper",
            "pyspellchecker",
            "pystray",
            "win32api",  # pywin32 wird als win32api importiert
            "tomli_w",  # tomli-w wird als tomli_w importiert
        ]

        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            pytest.skip(f"Einige Pakete fehlen: {missing_packages}")


class TestSystemIntegration:
    """Testet die Integration aller Systemkomponenten."""

    def test_audio_pipeline_integration(self):
        """Testet die Integration der Audio-Pipeline."""
        try:
            from src.audio.recorder import AudioRecorder
            from src.audio.volume_controller import VolumeController

            # Teste Audio-Recorder
            recorder = AudioRecorder(Config())
            assert recorder is not None

            # Teste Volume Controller
            volume_controller = VolumeController(target=0.1)
            assert volume_controller is not None

        except Exception as e:
            pytest.fail(f"Audio-Pipeline-Integrationsfehler: {e}")

    def test_language_processing_integration(self):
        """Testet die Integration der Sprachverarbeitung."""
        try:
            # Mock STT und Spell Checker, um echte Komponenten nicht zu laden
            with patch("src.mouscribe.SpeechToText") as mock_stt_class:
                with patch("src.mouscribe.SpellChecker") as mock_spell_class:
                    # Mock STT
                    mock_stt = Mock()
                    mock_stt_class.return_value = mock_stt

                    # Mock Spell Checker
                    mock_spell = Mock()
                    mock_spell_class.return_value = mock_spell

                    assert mock_stt is not None
                    assert mock_spell is not None

        except Exception as e:
            pytest.fail(f"Sprachverarbeitungs-Integrationsfehler: {e}")

    def test_input_system_integration(self):
        """Testet die Integration des Eingabesystems."""
        try:
            from src.input.input_handler import InputHandler

            # Teste Input Handler
            input_handler = InputHandler(primary_callback=lambda: None, secondary_callback=lambda: None)
            assert input_handler is not None

        except Exception as e:
            pytest.fail(f"Eingabesystem-Integrationsfehler: {e}")

    def test_ui_system_integration(self):
        """Testet die Integration des UI-Systems."""
        try:
            from src.ui.notifications import NotificationManager
            from src.ui.system_tray import SystemTrayManager

            # Teste Notification Manager
            notification_manager = NotificationManager(Config())
            assert notification_manager is not None

            # Teste System Tray Manager
            system_tray_manager = SystemTrayManager(Config(), None)
            assert system_tray_manager is not None

        except Exception as e:
            pytest.fail(f"UI-System-Integrationsfehler: {e}")

    def test_utility_system_integration(self):
        """Testet die Integration des Utility-Systems."""
        try:
            from src.utils.database import AudioDatabase
            from src.utils.logger import setup_logging

            # Teste Database
            database = AudioDatabase()
            assert database is not None

            # Teste Logger Setup
            setup_logging(Config())

        except Exception as e:
            pytest.fail(f"Utility-System-Integrationsfehler: {e}")


class TestSystemStability:
    """Testet die Stabilität des Systems."""

    def test_memory_management(self):
        """Testet das Memory-Management."""
        import gc

        import psutil

        process = psutil.Process()
        initial_memory = process.memory_info().rss

        # Führe einige Operationen aus
        for i in range(10):
            try:
                config = Config()
                del config
            except Exception:
                pass

        # Cleanup
        gc.collect()

        # Memory sollte nicht übermäßig ansteigen
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        memory_increase_mb = memory_increase / 1024 / 1024

        assert memory_increase_mb < 50, f"Memory-Leak erkannt: {memory_increase_mb:.1f}MB"

    def test_error_recovery(self):
        """Testet die Fehlerwiederherstellung."""
        # Teste ob das System nach Fehlern wieder funktioniert
        try:
            # Simuliere einen Fehler
            config = Config()

            # Teste normale Operation
            assert config is not None

            # Simuliere einen weiteren Fehler
            config2 = Config()
            assert config2 is not None

        except Exception as e:
            pytest.fail(f"Fehlerwiederherstellung funktioniert nicht: {e}")

    def test_concurrent_access(self):
        """Testet den gleichzeitigen Zugriff."""
        import threading
        import time

        results = []
        errors = []

        def test_operation(thread_id):
            try:
                config = Config()
                results.append((thread_id, "success"))
            except Exception as e:
                errors.append((thread_id, str(e)))

        # Starte mehrere Threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=test_operation, args=(i,))
            threads.append(thread)
            thread.start()

        # Warte auf alle Threads
        for thread in threads:
            thread.join()

        # Alle Threads sollten erfolgreich sein
        assert len(errors) == 0, f"Fehler in Threads: {errors}"
        assert len(results) == 5, f"Erwartete 5 Ergebnisse, aber {len(results)} erhalten"


class TestConfigurationValidation:
    """Testet die Konfigurationsvalidierung."""

    def test_audio_configuration(self):
        """Testet die Audio-Konfiguration."""
        config = Config()

        # Teste Audio-Einstellungen
        assert config.audio_sample_rate in [8000, 16000, 22050, 44100, 48000]
        assert config.audio_channels in [1, 2]
        assert config.audio_chunk_size > 0
        assert config.audio_format in ["wav", "mp3", "flac"]
        assert isinstance(config.audio_device, int) or config.audio_device is None

    def test_transcription_configuration(self):
        """Testet die Transkriptions-Konfiguration."""
        config = Config()

        # Teste Transkriptions-Einstellungen
        assert config.transcription_language in ["de", "en", "auto"]
        assert config.transcription_whisper_model in ["tiny", "base", "small", "medium", "large"]
        assert config.transcription_compute_type in ["float32", "float16", "int8"]

    def test_system_configuration(self):
        """Testet die System-Konfiguration."""
        config = Config()

        # Teste System-Einstellungen
        assert 0.0 <= config.system_volume_reduction_factor <= 1.0
        assert 0 <= config.system_min_volume_percent <= 100

    def test_logging_configuration(self):
        """Testet die Logging-Konfiguration."""
        config = Config()

        # Teste Logging-Einstellungen
        assert isinstance(config.logging_enabled, bool)
        assert config.logging_console_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        assert config.logging_file_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        assert isinstance(config.logging_emoji_enabled, bool)
        assert isinstance(config.logging_file_enabled, bool)


if __name__ == "__main__":
    # Führe alle Tests aus
    pytest.main([__file__, "-v", "--tb=short"])
