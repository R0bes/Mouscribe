# src/main.py - Main application entry point for Mauscribe
"""
Mauscribe - Voice-to-Text Tool
Main application logic and core functionality
"""
import signal
import sys
import threading
import time
from typing import Any

import numpy as np
import pyautogui
import pyperclip

from .audio.recorder import AudioRecorder
from .audio.volume_controller import VolumeController
from .input.input_handler import InputHandler
from .lang.spell_checker import SpellChecker
from .lang.stt import SpeechToText
from .ui.notifications import NotificationManager
from .ui.system_tray import SystemTrayManager
from .utils.config import Config
from .utils.database import AudioDatabase
from .utils.logger import get_logger, setup_logging


class MauscribeApp:
    """Main application class for Mauscribe voice-to-text tool."""

    def __init__(self) -> None:
        """Initialize Mauscribe application."""
        # Initialize config first
        self.config = Config()

        # Setup logging with config
        setup_logging(self.config)

        # Create logger instance
        self.logger = get_logger(self.__class__.__name__, self.config)
        self.logger.info("🚀 Starte Mauscribe...")

        self.logger.info("🔧 Initialisiere Komponenten...")
        self.recorder = AudioRecorder(self.config)
        self.stt = SpeechToText()  # SpeechToText nimmt keinen Config-Parameter
        self.spell_checker = (
            SpellChecker()
        )  # SpellChecker nimmt keinen Config-Parameter
        self.system_tray_manager = SystemTrayManager(self.config, self)
        self._volume_controller = VolumeController(target=0.1)
        self.notification_manager = NotificationManager(self.config)
        self.input_handler = InputHandler(
            pk_callback=self._on_primary_key_pressed,
            sk_callback=self._on_secondary_key_pressed,
        )

        # Initialize database
        self.audio_database = AudioDatabase()
        self.logger.info("✅ Alle Komponenten initialisiert")

        # Initialize recording state variables
        self._is_recording = False
        self._last_recording_timestamp: float = 0.0
        self._last_recording_stop_timestamp: float = 0.0
        self._last_click_time: float = 0.0
        self._click_debounce_ms = 500  # 500ms for double-click detection
        self._secondary_button_start_time: float = 0.0
        self._secondary_button_is_pressed = False
        self._secondary_button_long_press_threshold = 1.5  # 1.5 seconds

        self.shutdown_event = threading.Event()

        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()

    def _on_primary_key_pressed(self, pressed: bool) -> None:
        if pressed:
            if not self._is_recording:
                self.start_recording()
            else:
                self.stop_recording()

    def _on_secondary_key_pressed(self, pressed: bool) -> None:
        if pressed:
            self._paste_text()

    def _paste_text(self, _: bool = False) -> None:
        """Paste transcribed text to current cursor position."""
        try:
            text = pyperclip.paste()
            if text and text.strip():
                pyautogui.write(text)
                self.logger.info(f"📋 Text eingefügt: {text[:50]}...")
                self.notification_manager.show_text_pasted(text)
            else:
                self.logger.warning("⚠️  Kein Text in der Zwischenablage zum Einfügen")
                self.notification_manager.show_warning(
                    "Kein Text in der Zwischenablage zum Einfügen", "Text einfügen"
                )
        except Exception as e:
            self.logger.error(f"❌ Text konnte nicht eingefügt werden: {e}")
            self.notification_manager.show_error(
                f"Text konnte nicht eingefügt werden: {e}", "Text einfügen"
            )

    def start_recording(self) -> None:
        """Start voice recording and transcription."""
        if self._is_recording:
            self.logger.warning("⚠️  Aufnahme läuft bereits")
            self.notification_manager.show_warning("Aufnahme läuft bereits", "Aufnahme")
            return

        self.logger.info("🎙️  Starte Sprachaufnahme...")
        self._is_recording = True

        # Set volume to 10%
        self._volume_controller.reduce_volume()

        # Start the recorder
        try:
            self.logger.debug("🎵 Starte Audio-Recorder...")
            self.recorder.start_recording()
            self.logger.info("✅ Audio-Recorder erfolgreich gestartet")

            # Show notification
            self.notification_manager.show_recording_started()

            # Update system tray icon
            self.system_tray_manager.update_recording_state(True)

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Starten des Audio-Recorders: {e}")
            self._is_recording = False
            self.notification_manager.show_error(
                f"Fehler beim Starten der Aufnahme: {e}", "Aufnahme"
            )
            return

    def stop_recording(self) -> None:
        """Stop voice recording and process audio."""
        if not self._is_recording:
            self.logger.warning("⚠️  Keine Aufnahme aktiv")
            self.notification_manager.show_warning("Keine Aufnahme aktiv", "Aufnahme")
            return

        self.logger.info("🛑 Stoppe Sprachaufnahme...")
        self._is_recording = False
        self._last_recording_stop_timestamp = time.time()

        # Stelle Lautstärke sicher wieder her
        self._volume_controller.restore_volume()

        # Stop the recorder
        try:
            # Get audio data & stopping
            audio_data = self.recorder.stop_recording()
            self.logger.info("🎵 Audio-Recorder gestoppt")

            # Process audio data immediately if available
            if audio_data is not None and len(audio_data) <= 0:
                self.logger.warning("❌ Keine Audioaufnahme verfügbar")
                self.notification_manager.show_warning(
                    "Keine Audioaufnahme", "Aufnahme"
                )

            # Transcribe audio (ohne Spellchecking für schnelle Rückgabe)
            duration = len(audio_data) / self.recorder.sample_rate_hz
            self.logger.info(
                f"🔊 Audio verarbeitet: {len(audio_data):,} Samples, {duration:.2f}s"
            )

            self.logger.info("🎯 Starte Sprach-zu-Text Transkription...")
            raw_text = self.stt.transcribe_raw(audio_data)

            self.notification_manager.show_transcription_complete(raw_text, duration)

            # Save audio recording to database if enabled
            recording_id = None
            if (
                self.config.database_enabled
                and self.config.database_auto_save_recordings
            ):
                try:
                    self.logger.info("💾 Speichere Audio-Aufnahme in Datenbank...")
                    recording_id = self.audio_database.save_audio_recording(
                        audio_data=audio_data,
                        sample_rate=self.recorder.sample_rate_hz,
                        channels=self.recorder.num_channels,
                        duration=duration,
                        audio_format=self.config.audio_format,
                    )
                    self.logger.info(
                        f"✅ Audio-Aufnahme gespeichert (ID: {recording_id})"
                    )
                except Exception as e:
                    self.logger.warning(
                        f"⚠️  Konnte Audio-Aufnahme nicht speichern: {e}"
                    )

                if raw_text and raw_text.strip():
                    self.logger.info("✨ Transkription erfolgreich abgeschlossen!")
                    self.logger.info(f"📝 Roher Text: '{raw_text}'")

                    # Save transcription to database if enabled
                    transcription_id = None
                    if (
                        self.config.database_enabled
                        and self.config.database_auto_save_transcriptions
                        and recording_id
                    ):
                        try:
                            transcription_id = self.audio_database.save_transcription(
                                audio_recording_id=recording_id,
                                raw_text=raw_text,
                                language=self.config.stt_language,
                            )
                            self.logger.info(
                                f"✅ Transkription in Datenbank gespeichert (ID: {transcription_id})"
                            )

                            # Mark as training data if enabled
                            if self.config.database_mark_as_training_data:
                                self.audio_database.save_training_data(
                                    transcription_id=transcription_id,
                                    is_valid_for_training=True,
                                )
                                self.logger.info("🏷️  Als Trainingsdaten markiert")
                        except Exception as e:
                            self.logger.warning(
                                f"⚠️  Konnte Transkription nicht speichern: {e}"
                            )
                    else:
                        self.logger.debug(
                            "💾 Transkriptions-Speicherung deaktiviert oder keine Aufnahme-ID verfügbar"
                        )

                    # Show transcription complete notification
                    duration = len(audio_data) / self.recorder.sample_rate_hz
                    self.notification_manager.show_transcription_complete(
                        raw_text, duration
                    )

                    # Sofort rohe Transkription in Clipboard kopieren
                    self.logger.info("📋 Kopiere Text in Zwischenablage...")
                    pyperclip.copy(raw_text)
                    self.logger.info("✅ Text erfolgreich in Zwischenablage kopiert!")
                    self.logger.info(f"🎤 Transkribiert: '{raw_text}'")

                    # Automatisches Einfügen falls aktiviert
                    # if self.config.behavior_auto_paste_after_transcription:
                    #    self.logger.info("🔄 Automatisches Einfügen aktiviert - füge Text ein...")
                    #    time.sleep(0.2)  # Kurze Pause für bessere Stabilität
                    #    self._paste_text()
                    #    self.logger.info("✅ Text automatisch eingefügt!")

                    # Im Hintergrund Spellchecking machen
                    # self.logger.info(f"🔄 Starte Hintergrund-Spellchecking...")
                    # self._spellcheck_background(raw_text, audio_data)
                else:
                    self.logger.warning("❌ Keine Sprache erkannt")
                    self.notification_manager.show_warning(
                        "Keine Sprache erkannt", "Transkription"
                    )

        except Exception as e:
            self.logger.error(f"Failed to stop recorder: {e}")
            self.notification_manager.show_error(
                f"Fehler beim Stoppen der Aufnahme: {e}", "Aufnahme"
            )

        # Update system tray icon
        self.system_tray_manager.update_recording_state(False)

    def _spellcheck_background(self, raw_text: str, audio_data: np.ndarray) -> None:
        """Mache Spellchecking im Hintergrund und aktualisiere Clipboard wenn nötig."""

        def spellcheck_worker():
            try:
                self.logger.info("🔄 Starte Hintergrund-Spellchecking...")

                self.logger.info(f"📝 Analysiere Text: '{raw_text}'")
                self.logger.info("🔍 Starte Rechtschreibprüfung...")

                # Spell check and correct
                corrected_text = self.spell_checker.check_text(raw_text)
                self.logger.info(f"📖 Korrigierter Text: {corrected_text}")

                self.logger.info("✨ Rechtschreibprüfung abgeschlossen!")
                self.logger.info(f"📖 Ursprünglicher Text: '{raw_text}'")
                self.logger.info(f"✅ Korrigierter Text: '{corrected_text}'")

                # Nur aktualisieren wenn sich was geändert hat
                if corrected_text != raw_text:
                    self.logger.info(
                        "🔄 Text korrigiert - aktualisiere Zwischenablage..."
                    )
                    pyperclip.copy(corrected_text)
                    self.logger.info(
                        "📋 Zwischenablage mit korrigiertem Text aktualisiert!"
                    )
                    self.logger.info(f"🎯 Korrektur: '{raw_text}' → '{corrected_text}'")

                    # Show notification
                    self.notification_manager.show_spell_check_complete(
                        raw_text, corrected_text
                    )
                else:
                    self.logger.info(
                        "✅ Keine Korrekturen nötig - Text ist bereits korrekt"
                    )
                    self.logger.info("📋 Zwischenablage bleibt unverändert")

                    # Show notification
                    self.notification_manager.show_spell_check_complete(
                        raw_text, corrected_text
                    )

                self.logger.info(
                    "🏁 Hintergrund-Spellchecking erfolgreich abgeschlossen"
                )

            except Exception as spell_error:
                self.logger.warning(f"❌ Spellchecking fehlgeschlagen: {spell_error}")
                self.logger.warning("⚠️  Verwende ursprünglichen Text ohne Korrekturen")

        self.logger.info("🚀 Starte Spellchecking-Thread im Hintergrund...")
        # Starte Spellchecking im Hintergrund
        spellcheck_thread = threading.Thread(target=spellcheck_worker)
        spellcheck_thread.daemon = True
        spellcheck_thread.start()
        self.logger.info(
            f"✅ Spellchecking-Thread gestartet (Thread-ID: {spellcheck_thread.ident})"
        )

    def run(self) -> None:
        """Start the Mauscribe application."""
        self.logger.info("🚀 Starte Mauscribe-Anwendung...")

        # Setup system tray
        self.system_tray_manager.setup()

        self.logger.info("🔄 Initialisiere System Tray...")

        # Run system tray in a separate thread so we can monitor shutdown
        tray_thread = threading.Thread(target=self._run_system_tray)
        tray_thread.daemon = True
        tray_thread.start()
        self.logger.info("✅ System Tray läuft im Hintergrund")

        if self.config.notifications_show_startup:
            self.notification_manager.show_info(
                "Mauscribe erfolgreich gestartet", "Anwendung"
            )

        self.logger.info("🎯 Mauscribe Steuerung:")
        self.logger.info(
            f"\t🐭 {self.config.mouse_button_primary} (press): Aufnahme starten/stoppen"
        )
        self.logger.info(
            f"\t🐭 {self.config.mouse_button_secondary} (hold): Text einfügen"
        )
        self.logger.info("🎮 Bereit für Eingaben!")

        while not self.shutdown_event.is_set():
            time.sleep(0.1)
        self.logger.info("🔄 Shutdown-Signal empfangen - beende System Tray...")

    def _run_system_tray(self) -> None:
        """Run system tray in a separate thread."""
        if not self.system_tray_manager.is_available():
            self.logger.error("❌ System Tray ist nicht verfügbar")
            self.shutdown_event.set()
            return

        try:
            self.system_tray_manager.run()
        except Exception as e:
            self.logger.error(f"❌ System Tray Fehler: {e}")
            self.shutdown_event.set()

    def stop(self) -> None:
        """Stop the Mauscribe application."""
        self.logger.info("🛑 Beende Mauscribe-Anwendung...")

        # Signal shutdown to all threads
        self.shutdown_event.set()

        # Stop recording if active
        if self._is_recording:
            self.logger.info("🛑 Stoppe aktive Aufnahme vor dem Shutdown...")
            self.stop_recording()

        # Stop input handling
        try:
            self.logger.info("🔄 Beende Input Handler...")
            self.input_handler.stop()
            self.logger.info("✅ Input Handler erfolgreich beendet")
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Beenden des Input Handlers: {e}")

        # Cleanup AudioRecorder (stellt Lautstärke wieder her)
        try:
            self.logger.info("🔄 Räume AudioRecorder auf...")
            self.recorder.cleanup()
            self.logger.info("✅ AudioRecorder erfolgreich aufgeräumt")
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Aufräumen des AudioRecorders: {e}")

        # Stop system tray
        try:
            self.system_tray_manager.stop()
            self.logger.info("✅ System Tray erfolgreich beendet")
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Beenden des System Tray: {e}")

        # Cleanup other components
        try:
            if hasattr(self, "spell_checker"):
                self.spell_checker.close()
                self.logger.info("✅ Rechtschreibprüfung erfolgreich beendet")
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Beenden der Rechtschreibprüfung: {e}")

        # Show shutdown notification
        if (
            hasattr(self, "notification_manager")
            and self.notification_manager.is_supported()
            and self.config.notifications_show_shutdown
        ):
            self.notification_manager.show_info(
                "Mauscribe erfolgreich beendet", "Anwendung"
            )

        self.logger.info("✅ Mauscribe-Anwendung erfolgreich beendet")

    def _setup_signal_handlers(self) -> None:
        """Set up signal handlers for graceful shutdown."""
        try:
            signal.signal(signal.SIGINT, self._handle_signal)
            signal.signal(signal.SIGTERM, self._handle_signal)
            self.logger.info("✅ Signal-Handler für Strg+C erfolgreich eingerichtet")
        except Exception as e:
            self.logger.error(
                f"⚠️  Signal-Handler konnte nicht eingerichtet werden: {e}"
            )

    def _handle_signal(self, signum: int, frame: Any) -> None:
        """Handle system signals for graceful shutdown."""
        signal_name = "SIGINT" if signum == signal.SIGINT else "SIGTERM"
        self.logger.info(
            f"🛑 Signal {signal_name} empfangen - starte graceful shutdown..."
        )
        self.shutdown_event.set()

        # Force stop recording if active
        if self._is_recording:
            self.logger.info("🛑 Stoppe aktive Aufnahme...")
            self._is_recording = False
            self.recorder.stop_recording()

        # Stelle Lautstärke sicher wieder her
        if hasattr(self.recorder, "restore_volume"):
            self.logger.info("🔄 Stelle System-Lautstärke wieder her...")
            self._volume_controller.restore_volume()


def start_mouscribe() -> None:
    """Main entry point for the Mauscribe application."""
    app = MauscribeApp()
    try:
        app.run()
    except KeyboardInterrupt:
        app.logger.info("⚠️  Programm durch Benutzer unterbrochen (Strg+C)")
        app.shutdown_event.set()
    except Exception as e:
        app.logger.error(f"❌ Unerwarteter Fehler: {e}")
        app.logger.error(f"Unexpected error in main: {e}")
        app.shutdown_event.set()
    finally:
        app.logger.info("🔄 Beende Anwendung...")
        app.stop()
        app.logger.info("✅ Anwendung erfolgreich beendet")


if __name__ == "__main__":
    start_mouscribe()
