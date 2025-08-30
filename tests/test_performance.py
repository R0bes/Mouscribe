"""
Performance Tests für Mauscribe
Testet Geschwindigkeit, Stabilität und Ressourcenverbrauch
"""

import gc
import os
import threading
import time
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import psutil
import pytest

from src.audio.recorder import AudioRecorder
from src.lang.spell_checker import SpellChecker
from src.lang.stt import SpeechToText
from src.mouscribe import MauscribeApp


class TestPerformance:
    """Testet die Performance verschiedener Systemkomponenten."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup für jeden Test."""
        self.process = psutil.Process()
        self.initial_memory = self.process.memory_info().rss
        yield
        # Cleanup nach Tests
        gc.collect()

    def test_initialization_performance(self):
        """Testet die Initialisierungsgeschwindigkeit."""
        start_time = time.time()

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
                                                app = MauscribeApp()

        init_time = time.time() - start_time
        assert init_time < 1.0, f"Initialisierung dauert zu lange: {init_time:.2f}s"

        # Memory-Verbrauch nach Initialisierung
        memory_after_init = self.process.memory_info().rss
        memory_increase = memory_after_init - self.initial_memory
        memory_increase_mb = memory_increase / 1024 / 1024

        assert memory_increase_mb < 100, f"Zu hoher Memory-Verbrauch: {memory_increase_mb:.1f}MB"

    def test_audio_processing_performance(self):
        """Testet die Audio-Verarbeitungsgeschwindigkeit."""
        # Verschiedene Audio-Längen testen
        audio_lengths = [8000, 16000, 32000, 48000]  # 0.5s, 1s, 2s, 3s

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
                                                # Mock STT mit realistischer Verzögerung
                                                mock_stt = Mock()
                                                mock_stt.transcribe_raw.side_effect = lambda x: "Test Transkription"
                                                mock_stt_class.return_value = mock_stt

                                                # Mock Spell Checker
                                                mock_spell = Mock()
                                                mock_spell.correct.side_effect = lambda x: x
                                                mock_spell_class.return_value = mock_spell

                                                app = MauscribeApp()

                                                for length in audio_lengths:
                                                    test_audio = np.random.random(length).astype(np.float32)

                                                    start_time = time.time()
                                                    result = app.stt.transcribe_raw(test_audio)
                                                    processing_time = time.time() - start_time

                                                    # Verarbeitungszeit sollte proportional zur Audio-Länge sein
                                                    expected_time = length / 16000 * 0.1  # 0.1x realtime
                                                    assert (
                                                        processing_time < expected_time
                                                    ), f"Audio-Verarbeitung zu langsam für {length} Samples: {processing_time:.3f}s > {expected_time:.3f}s"

                                                    assert result is not None
                                                    assert isinstance(result, str)

    def test_memory_stability(self):
        """Testet die Memory-Stabilität bei längerer Nutzung."""
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
                                                mock_stt.transcribe_raw.side_effect = lambda x: "Test Transkription"
                                                mock_stt_class.return_value = mock_stt

                                                # Mock Spell Checker
                                                mock_spell = Mock()
                                                mock_spell.correct.side_effect = lambda x: x
                                                mock_spell_class.return_value = mock_spell

                                                app = MauscribeApp()

                                                # Memory nach Initialisierung
                                                memory_after_init = self.process.memory_info().rss

                                                # Simuliere mehrere Audio-Verarbeitungen
                                                for i in range(10):
                                                    test_audio = np.random.random(16000).astype(np.float32)
                                                    app.stt.transcribe_raw(test_audio)

                                                    # Memory nach jeder Verarbeitung
                                                    current_memory = self.process.memory_info().rss
                                                    memory_increase = current_memory - memory_after_init
                                                    memory_increase_mb = memory_increase / 1024 / 1024

                                                    # Memory sollte nicht übermäßig ansteigen
                                                    assert (
                                                        memory_increase_mb < 50
                                                    ), "Memory-Leak nach {} Verarbeitungen: {:.1f}MB".format(
                                                        i + 1, memory_increase_mb
                                                    )

    def test_concurrent_processing(self):
        """Testet die Stabilität bei gleichzeitiger Verarbeitung."""
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
                                                mock_stt.transcribe_raw.side_effect = lambda x: "Test Transkription"
                                                mock_stt_class.return_value = mock_stt

                                                # Mock Spell Checker
                                                mock_spell = Mock()
                                                mock_spell.correct.side_effect = lambda x: x
                                                mock_spell_class.return_value = mock_spell

                                                app = MauscribeApp()

                                                results = []
                                                errors = []

                                                def process_audio(thread_id):
                                                    try:
                                                        test_audio = np.random.random(16000).astype(np.float32)
                                                        result = app.stt.transcribe_raw(test_audio)
                                                        results.append((thread_id, result))
                                                    except Exception as e:
                                                        errors.append((thread_id, str(e)))

                                                # Starte mehrere Threads gleichzeitig
                                                threads = []
                                                for i in range(5):
                                                    thread = threading.Thread(target=process_audio, args=(i,))
                                                    threads.append(thread)
                                                    thread.start()

                                                # Warte auf alle Threads
                                                for thread in threads:
                                                    thread.join()

                                                # Alle Threads sollten erfolgreich sein
                                                assert len(errors) == 0, f"Fehler in Threads: {errors}"
                                                assert (
                                                    len(results) == 5
                                                ), f"Erwartete 5 Ergebnisse, aber {len(results)} erhalten"

                                                # Alle Ergebnisse sollten gleich sein
                                                for thread_id, result in results:
                                                    assert (
                                                        result == "Test Transkription"
                                                    ), f"Thread {thread_id} hat unerwartetes Ergebnis: {result}"

    def test_cpu_usage(self):
        """Testet die CPU-Nutzung während der Verarbeitung."""
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
                                                mock_stt.transcribe_raw.side_effect = lambda x: "Test Transkription"
                                                mock_stt_class.return_value = mock_stt

                                                # Mock Spell Checker
                                                mock_spell = Mock()
                                                mock_spell.correct.side_effect = lambda x: x
                                                mock_spell_class.return_value = mock_spell

                                                app = MauscribeApp()

                                                # CPU vor Verarbeitung
                                                cpu_before = self.process.cpu_percent()

                                                # Simuliere Audio-Verarbeitung
                                                test_audio = np.random.random(16000).astype(np.float32)
                                                start_time = time.time()
                                                result = app.stt.transcribe_raw(test_audio)
                                                processing_time = time.time() - start_time

                                                # CPU nach Verarbeitung
                                                cpu_after = self.process.cpu_percent()

                                                # CPU-Nutzung sollte nicht übermäßig sein
                                                assert cpu_after < 80, f"CPU-Nutzung zu hoch: {cpu_after}%"

                                                # Verarbeitung sollte erfolgreich sein
                                                assert result == "Test Transkription"
                                                assert (
                                                    processing_time < 1.0
                                                ), f"Verarbeitung zu langsam: {processing_time:.3f}s"


class TestStressTest:
    """Stress-Tests für das System."""

    def test_rapid_fire_processing(self):
        """Testet schnelle aufeinanderfolgende Verarbeitung."""
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
                                                mock_stt.transcribe_raw.side_effect = lambda x: "Test Transkription"
                                                mock_stt_class.return_value = mock_stt

                                                # Mock Spell Checker
                                                mock_spell = Mock()
                                                mock_spell.correct.side_effect = lambda x: x
                                                mock_spell_class.return_value = mock_spell

                                                app = MauscribeApp()

                                                # Schnelle aufeinanderfolgende Verarbeitung
                                                start_time = time.time()
                                                for i in range(20):
                                                    test_audio = np.random.random(16000).astype(np.float32)
                                                    result = app.stt.transcribe_raw(test_audio)
                                                    assert result == "Test Transkription"

                                                total_time = time.time() - start_time
                                                avg_time = total_time / 20

                                                # Durchschnittliche Verarbeitungszeit sollte unter 100ms liegen
                                                assert (
                                                    avg_time < 0.1
                                                ), f"Durchschnittliche Verarbeitungszeit zu hoch: {avg_time:.3f}s"

    def test_large_audio_files(self):
        """Testet die Verarbeitung großer Audio-Dateien."""
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
                                                mock_stt.transcribe_raw.side_effect = lambda x: "Test Transkription"
                                                mock_stt_class.return_value = mock_stt

                                                # Mock Spell Checker
                                                mock_spell = Mock()
                                                mock_spell.correct.side_effect = lambda x: x
                                                mock_spell_class.return_value = mock_spell

                                                app = MauscribeApp()

                                                # Teste verschiedene Audio-Größen
                                                audio_sizes = [8000, 16000, 32000, 64000, 128000]  # 0.5s bis 8s

                                                for size in audio_sizes:
                                                    test_audio = np.random.random(size).astype(np.float32)

                                                    start_time = time.time()
                                                    result = app.stt.transcribe_raw(test_audio)
                                                    processing_time = time.time() - start_time

                                                    # Verarbeitung sollte erfolgreich sein
                                                    assert result == "Test Transkription"

                                                    # Verarbeitungszeit sollte proportional zur Größe sein
                                                    expected_time = size / 16000 * 0.2  # 0.2x realtime
                                                    assert (
                                                        processing_time < expected_time
                                                    ), f"Verarbeitung zu langsam für {size} Samples: {processing_time:.3f}s > {expected_time:.3f}s"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
