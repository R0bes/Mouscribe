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
from .input import InputHandler
from .lang.spell_checker import SpellChecker
from .lang.stt import SpeechToText
from .ui.system_tray import SystemTrayManager
from .ui.windows_notifications import WindowsNotificationManager
from .utils.config import Config
from .utils.database import AudioDatabase
from .utils.logger import get_logger

logger = get_logger("Mauscribe")


class MauscribeApp:
    """Main application class for Mauscribe voice-to-text tool."""

    def __init__(self) -> None:
        """Initialize Mauscribe application."""
        self.config = Config()
        self.logger = get_logger(self.__class__.__name__)
        self.recorder = AudioRecorder(self.config)
        self.stt = SpeechToText()  # SpeechToText nimmt keinen Config-Parameter
        self.spell_checker = (
            SpellChecker()
        )  # SpellChecker nimmt keinen Config-Parameter
        self.system_tray_manager = SystemTrayManager(self.config, self)
        self._volume_controller = VolumeController(target=0.1)
        self.notification_manager = WindowsNotificationManager(self.config)
        self.input_handler = InputHandler(
            pk_callback=self._on_primary_key_pressed,
            sk_callback=self._on_secondary_key_pressed,
        )

        # Initialize database
        self.audio_database = AudioDatabase()

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
                self._stop_recording_legacy()

    def _start_recording_legacy(self) -> None:
        print("start_recording")
        self._volume_controller.reduce_volume()
        self.recorder.start_recording()

    def _stop_recording_legacy(self) -> None:
        print("stop recording")
        self._volume_controller.restore_volume()
        self.recorder.stop_recording()
        self._last_recording_stop_timestamp = time.time()

    def _on_secondary_key_pressed(self, pressed: bool) -> None:
        if pressed:
            self._paste_text()

    def _paste_text(self, _: bool = False) -> None:
        """Paste transcribed text to current cursor position."""
        try:
            text = pyperclip.paste()
            if text and text.strip():
                pyautogui.write(text)
                logger.info(f"📋 Text eingefügt: {text[:50]}...")
                self.notification_manager.show_text_pasted(text)
            else:
                logger.warning("⚠️  Kein Text in der Zwischenablage zum Einfügen")
                self.notification_manager.show_warning(
                    "Kein Text in der Zwischenablage zum Einfügen", "Text einfügen"
                )
        except Exception as e:
            logger.error(f"❌ Text konnte nicht eingefügt werden: {e}")
            self.notification_manager.show_error(
                f"Text konnte nicht eingefügt werden: {e}", "Text einfügen"
            )

    def _setup_system_tray(self) -> None:
        """Initialize the system tray icon and menu."""
        self.system_tray_manager.setup()

    def start_recording(self) -> None:
        """Start voice recording and transcription."""
        if self._is_recording:
            logger.warning("⚠️  Aufnahme läuft bereits")
            self.notification_manager.show_warning("Aufnahme läuft bereits", "Aufnahme")
            return

        logger.info("🎙️  Starte Aufnahme...")
        self._is_recording = True

        # Start the recorder
        try:
            logger.debug("Starting audio recorder")
            self.recorder.start_recording()
            logger.info("✅ Audio recorder started successfully")

            # Show notification
            self.notification_manager.show_recording_started()

            # Update system tray icon
            self.system_tray_manager.update_recording_state(True)

        except Exception as e:
            logger.error(f"❌ Failed to start audio recorder: {e}")
            self._is_recording = False
            self.notification_manager.show_error(
                f"Fehler beim Starten der Aufnahme: {e}", "Aufnahme"
            )
            return

    def stop_recording(self) -> None:
        """Stop voice recording and process audio."""
        if not self._is_recording:
            logger.warning("⚠️  Keine Aufnahme aktiv")
            self.notification_manager.show_warning("Keine Aufnahme aktiv", "Aufnahme")
            return

        logger.info("🛑 Stoppe Aufnahme...")
        self._is_recording = False
        self._last_recording_stop_timestamp = time.time()

        # Stop the recorder
        try:
            # Get audio data & stopping
            audio_data = self.recorder.stop_recording()
            logger.info("Audio recorder stopped")

            # Process audio data immediately if available
            if audio_data is not None and len(audio_data) <= 0:
                logger.warning("❌ Keine Audioaufnahme")
                self.notification_manager.show_warning(
                    "Keine Audioaufnahme", "Aufnahme"
                )

            # Transcribe audio (ohne Spellchecking für schnelle Rückgabe)
            duration = len(audio_data) / self.recorder.sample_rate_hz
            logger.info(f"🔊 Audio-Daten: {len(audio_data)} Samples, {duration:.2f}s")

            logger.info("🎯 Starting speech-to-text transcription...")
            raw_text = self.stt.transcribe_raw(audio_data)

            self.notification_manager.show_transcription_complete(raw_text, duration)

            # Save audio recording to database if enabled
            recording_id = None
            if self.config.database_enabled and self.config.auto_save_recordings:
                try:
                    logger.info("💾 Speichere Audio-Aufnahme in Datenbank...")
                    recording_id = self.audio_database.save_audio_recording(
                        audio_data=audio_data,
                        sample_rate=self.recorder.sample_rate_hz,
                        channels=self.recorder.num_channels,
                        duration=duration,
                        audio_format=self.config.audio_format,
                    )
                    logger.info(f"✅ Audio-Aufnahme gespeichert (ID: {recording_id})")
                except Exception as e:
                    logger.warning(f"⚠️  Konnte Audio-Aufnahme nicht speichern: {e}")

                if raw_text and raw_text.strip():
                    logger.info("✨ STT-Transkription abgeschlossen!")
                    logger.info(f"📝 Roher Text: '{raw_text}'")

                    # Save transcription to database if enabled
                    transcription_id = None
                    if (
                        self.config.database_enabled
                        and self.config.auto_save_transcriptions
                        and recording_id
                    ):
                        try:
                            transcription_id = self.audio_database.save_transcription(
                                audio_recording_id=recording_id,
                                raw_text=raw_text,
                                language=self.config.stt_language,
                            )
                            logger.info(
                                f"✅ Transkription gespeichert (ID: {transcription_id})"
                            )

                            # Mark as training data if enabled
                            if self.config.mark_as_training_data:
                                self.audio_database.save_training_data(
                                    transcription_id=transcription_id,
                                    is_valid_for_training=True,
                                )
                                logger.info("✅ Als Trainingsdaten markiert")
                        except Exception as e:
                            logger.warning(
                                f"⚠️  Konnte Transkription nicht speichern: {e}"
                            )
                    else:
                        logger.debug(
                            "💾 Transkriptions-Speicherung deaktiviert oder keine Aufnahme-ID verfügbar"
                        )

                    # Show transcription complete notification
                    duration = len(audio_data) / self.recorder.sample_rate_hz
                    self.notification_manager.show_transcription_complete(
                        raw_text, duration
                    )

                    # Sofort rohe Transkription in Clipboard kopieren
                    logger.info("📋 Kopiere rohen Text in Clipboard...")
                    pyperclip.copy(raw_text)
                    logger.info("✅ Roher Text in Clipboard verfügbar!")
                    logger.info(f"🎤 Transkribiert (roh): {raw_text}")

                    # Automatisches Einfügen falls aktiviert
                    if self.config.auto_paste_after_transcription:
                        logger.info(
                            "🔄 Automatisches Einfügen aktiviert - füge Text ein..."
                        )
                        time.sleep(0.2)  # Kurze Pause für bessere Stabilität
                        self._paste_text()
                        logger.info("✅ Text automatisch eingefügt!")

                    # Im Hintergrund Spellchecking machen
                    # logger.info(f"🔄 Starte Hintergrund-Spellchecking...")
                    # self._spellcheck_background(raw_text, audio_data)
                else:
                    logger.warning("❌ Keine Sprache erkannt")
                    self.notification_manager.show_warning(
                        "Keine Sprache erkannt", "Transkription"
                    )

        except Exception as e:
            logger.error(f"Failed to stop recorder: {e}")
            self.notification_manager.show_error(
                f"Fehler beim Stoppen der Aufnahme: {e}", "Aufnahme"
            )

        # Update system tray icon
        self.system_tray_manager.update_recording_state(False)

    def _spellcheck_background(self, raw_text: str, audio_data: np.ndarray) -> None:
        """Mache Spellchecking im Hintergrund und aktualisiere Clipboard wenn nötig."""

        def spellcheck_worker():
            try:
                logger.info("🔄 Hintergrund-Spellchecking gestartet...")

                logger.info(f"📝 Analysiere Text: '{raw_text}'")
                logger.info("🔍 Starte Rechtschreibprüfung...")

                # Spell check and correct
                corrected_text = self.spell_checker.check_text(raw_text)
                logger.info(f"Corrected text: {corrected_text}")

                logger.info("✨ Spellchecking abgeschlossen!")
                logger.info(f"📖 Ursprünglicher Text: '{raw_text}'")
                logger.info(f"✅ Korrigierter Text: '{corrected_text}'")

                # Nur aktualisieren wenn sich was geändert hat
                if corrected_text != raw_text:
                    logger.info("🔄 Text hat sich geändert - aktualisiere Clipboard...")
                    pyperclip.copy(corrected_text)
                    logger.info("📋 Clipboard aktualisiert mit korrigiertem Text!")
                    logger.info(f"🎯 Korrektur: '{raw_text}' → '{corrected_text}'")

                    # Show notification
                    self.notification_manager.show_spell_check_complete(
                        raw_text, corrected_text
                    )
                else:
                    logger.info("✅ Keine Korrekturen nötig - Text ist bereits korrekt")
                    logger.info("📋 Clipboard bleibt unverändert")

                    # Show notification
                    self.notification_manager.show_spell_check_complete(
                        raw_text, corrected_text
                    )

                logger.info("🏁 Hintergrund-Spellchecking abgeschlossen")

            except Exception as spell_error:
                logger.warning(f"❌ Spellchecking fehlgeschlagen: {spell_error}")
                logger.warning("⚠️  Verwende ursprünglichen Text ohne Korrekturen")

        logger.info("🚀 Starte Spellchecking-Thread im Hintergrund...")
        # Starte Spellchecking im Hintergrund
        spellcheck_thread = threading.Thread(target=spellcheck_worker)
        spellcheck_thread.daemon = True
        spellcheck_thread.start()
        logger.info(
            f"✅ Spellchecking-Thread gestartet (Thread-ID: {spellcheck_thread.ident})"
        )

    def run(self) -> None:
        """Start the Mauscribe application."""
        logger.info("🚀 Starte Mauscribe...")

        # Setup system tray
        self._setup_system_tray()

        # Start system tray if available
        if self.system_tray_manager.is_available():
            try:
                logger.info("🔄 Starte System Tray...")
                # Run system tray in a separate thread so we can monitor shutdown
                tray_thread = threading.Thread(target=self._run_system_tray)
                tray_thread.daemon = True
                tray_thread.start()

                logger.info("✅ System Tray läuft im Hintergrund")

                # Show startup notification
                if (
                    self.notification_manager.is_supported()
                    and self.config.notifications_show_startup
                ):
                    self.notification_manager.show_info(
                        "Mauscribe erfolgreich gestartet", "Anwendung"
                    )

                logger.info("🎯 Mauscribe Steuerung:")
                logger.info(
                    f"- {self.config.mouse_button_primary} (einfach): Aufnahme starten/stoppen"
                )
                logger.info(
                    f"-{self.config.mouse_button_secondary} (langes Drücken >1.5s): Text automatisch einfügen"
                )

                # Monitor shutdown in main thread
                while not self.shutdown_event.is_set():
                    time.sleep(0.1)

                logger.info("🔄 Shutdown signal empfangen - beende System Tray...")

            except Exception as e:
                logger.error(f"❌ System Tray fehlgeschlagen: {e}")
                logger.warning("⚠️  Lauf im Konsolenmodus...")
                self._run_console_mode()
        else:
            logger.warning("⚠️  Lauf im Konsolenmodus...")
            self._run_console_mode()

    def _run_system_tray(self) -> None:
        """Run system tray in a separate thread."""
        if not self.system_tray_manager.is_available():
            logger.error("❌ System Tray ist nicht verfügbar")
            self.shutdown_event.set()
            return

        try:
            self.system_tray_manager.run()
        except Exception as e:
            logger.error(f"❌ System Tray Fehler: {e}")
            self.shutdown_event.set()

    def _run_console_mode(self) -> None:
        """Run the application in console mode without system tray."""
        logger.info("🖥️  Mauscribe läuft im Konsolenmodus")
        logger.info("📋 Verwendung:")
        logger.info("- X2-Maustaste (einfach): Aufnahme starten/stoppen")
        logger.info("- X2-Maustaste (doppelklick): Text einfügen")
        logger.info(
            "- X2-Doppelklick während Aufnahme: Stoppt Aufnahme und fügt Text ein"
        )
        logger.info("- X1-Maustaste (langes Drücken >1.5s): Text automatisch einfügen")
        logger.info("- X1-Maustaste (kurzes Drücken): Keine Aktion")
        logger.info("- Drücken Sie Strg+C um zu beenden")

        try:
            while not self.shutdown_event.is_set():
                time.sleep(0.1)  # Check more frequently
        except KeyboardInterrupt:
            logger.info("🛑 Strg+C empfangen...")
            self.shutdown_event.set()

        logger.info("🛑 Beende Anwendung...")
        self.stop()

    def stop(self) -> None:
        """Stop the Mauscribe application."""
        logger.info("🛑 Beende Mauscribe...")

        # Signal shutdown to all threads
        self.shutdown_event.set()

        # Stop recording if active
        if self._is_recording:
            logger.info("🛑 Stoppe aktive Aufnahme vor dem Shutdown")
            self.stop_recording()

        # Stop input handling
        try:
            logger.info("🔄 Beende Input Handler...")
            self.input_handler.stop()
            logger.info("✅ Input Handler beendet")
        except Exception as e:
            logger.error(f"❌ Fehler beim Beenden des Input Handlers: {e}")

        # Cleanup AudioRecorder (stellt Lautstärke wieder her)
        try:
            logger.info("🔄 Räume AudioRecorder auf...")
            self.recorder.cleanup()
            logger.info("✅ AudioRecorder aufgeräumt")
        except Exception as e:
            logger.error(f"❌ Fehler beim Aufräumen des AudioRecorders: {e}")

        # Stop system tray
        try:
            self.system_tray_manager.stop()
            logger.info("✅ System Tray beendet")
        except Exception as e:
            logger.error(f"❌ Fehler beim Beenden des System Tray: {e}")

        # Cleanup other components
        try:
            if hasattr(self, "spell_checker"):
                self.spell_checker.close()
                logger.info("✅ Rechtschreibprüfung beendet")
        except Exception as e:
            logger.error(f"❌ Fehler beim Beenden der Rechtschreibprüfung: {e}")

        # Show shutdown notification
        if (
            hasattr(self, "notification_manager")
            and self.notification_manager.is_supported()
            and self.config.notifications_show_shutdown
        ):
            self.notification_manager.show_info(
                "Mauscribe erfolgreich beendet", "Anwendung"
            )

        logger.info("✅ Mauscribe erfolgreich beendet")
        logger.info("Mauscribe shutdown completed")

    def _setup_signal_handlers(self) -> None:
        """Set up signal handlers for graceful shutdown."""
        try:
            signal.signal(signal.SIGINT, self._handle_signal)
            signal.signal(signal.SIGTERM, self._handle_signal)
            logger.info("✅ Signal-Handler für Strg+C eingerichtet")
        except Exception as e:
            logger.error(f"⚠️  Signal-Handler konnte nicht eingerichtet werden: {e}")

    def _handle_signal(self, signum: int, frame: Any) -> None:
        """Handle system signals for graceful shutdown."""
        signal_name = "SIGINT" if signum == signal.SIGINT else "SIGTERM"
        logger.info(f"🛑 Signal {signal_name} empfangen - starte graceful shutdown...")
        logger.info(
            f"Received signal {signum} ({signal_name}). Initiating graceful shutdown."
        )
        self.shutdown_event.set()

        # Force stop recording if active
        if self._is_recording:
            logger.info("🛑 Stoppe aktive Aufnahme...")
            self._is_recording = False
            if hasattr(self.recorder, "stop_recording"):
                try:
                    self.recorder.stop_recording()
                except Exception:
                    pass

        # Stelle Lautstärke sicher wieder her
        if hasattr(self.recorder, "restore_volume"):
            try:
                logger.info("🔄 Stelle Lautstärke wieder her...")
                self.recorder.restore_volume()
            except Exception as e:
                logger.error(f"❌ Fehler beim Wiederherstellen der Lautstärke: {e}")


def main() -> None:
    """Main entry point for the Mauscribe application."""
    logger = get_logger(__name__)
    logger.info("🚀 Starte Mauscribe...")

    app = MauscribeApp()

    try:
        app.run()
    except KeyboardInterrupt:
        logger.info("⚠️  Programm durch Benutzer unterbrochen (Strg+C)")
        app.shutdown_event.set()
    except Exception as e:
        logger.error(f"❌ Unerwarteter Fehler: {e}")
        logger.error(f"Unexpected error in main: {e}")
        app.shutdown_event.set()
    finally:
        logger.info("🔄 Beende Anwendung...")
        app.stop()
        logger.info("✅ Anwendung erfolgreich beendet")


if __name__ == "__main__":
    main()
