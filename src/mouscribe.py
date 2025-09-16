# src/main.py - Main application entry point for Mauscribe
"""
Mauscribe - Voice-to-Text Tool
Main application logic and core functionality
"""
import signal
import sys
import threading
import time
from typing import Any, Literal, Optional

import numpy as np
import pyautogui
from pydantic import Field
import pyperclip

from .audio.recorder import Recorder
from .audio.volumizer import Volumizer
from .utils.controlls import ControllsManager
from .audio.transcriptor import Transcriptor
from .ui.notifications import Toaster
from .ui.system_tray import SysTray
from .utils import Settings, AudioDatabase, get_logger, setup_logging
from .ui.widgets import MouseOverlayManager, TextWidget, RecordingWidget, WidgetConfig

class AppSettings(Settings):
    """Application metadata settings."""
    app_name: str = Field(default="Mauscribe", description="Application name")
    version: str = Field(default="1.0.0", description="Application version")
    name: str = Field(default="x2", description="Key/Button name")
    type: str = Field(default="click", description="Input type")
    model_config = { "env_prefix": "MAUSCRIBE_APP_" }


class MauscribeApp:
    """Main application class for Mauscribe voice-to-text tool."""

    def __init__(self) -> None:
        """Initialize Mauscribe application."""
        # Initialize settings first
        self.config = Settings()

        # Setup logging
        setup_logging()

        # Create logger instance
        self.logger = get_logger(self.__class__.__name__, self.config)  
        self.logger.info("🚀 Starte Mauscribe...")

        self.logger.info("🔧 Initialisiere Komponenten...")

        self.systray = SysTray(self.config, self)
        self.recorder = Recorder()
        self.transcriptor = Transcriptor()
        self.volume_controller = Volumizer()
        self.overlay_manager = MouseOverlayManager()
        # Initialize toaster with notification settings
        notification_enabled = self.config.notifications.get("enabled", True)
        notification_sound = self.config.notifications.get("sound", True)
        notification_duration = self.config.notifications.get("duration", 5000)
        self.toaster = Toaster(
            enable_sound=notification_sound,
            default_duration=notification_duration,
            enabled=notification_enabled,
            notification_settings=self.config.notifications
        )
        self.controlls = ControllsManager(
            config=self.config,
            primary_callback=self.on_primary_action,
            secondary_callback=self.on_secondary_action
        )   
        

        self.overlay_manager.register_widget("recording", TextWidget("Test"), "left", 0.5)


        # Initialize database
        self.audio_database = AudioDatabase()
        
        # Start controls manager
        self.controlls.start()
        self.logger.info("✅ Alle Komponenten initialisiert")


        # Initialize recording state variables
        self._is_recording = False
        self._last_recording_timestamp: float = 0.0
        self._last_recording_stop_timestamp: float = 0.0

        self.shutdown_event = threading.Event()

        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()

    def on_primary_action(self) -> None:
        """Handle primary button action."""
        self.logger.info("🎮 Primary button pressed - toggle recording")
        if not self._is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def on_secondary_action(self) -> None:
        """Handle secondary button action."""
        self.logger.info("🎮 Secondary button pressed - paste text")
        self._paste_text()

    def _safe_write_text(self, text: str) -> bool:
        """Safely write text to current cursor position."""
        try:
            # Use pyautogui for safe text input
            pyautogui.write(text)
            return True
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Schreiben des Textes: {e}")
            return False

    def _paste_text(self, _: bool = False) -> None:
        """Paste transcribed text to current cursor position."""
        try:
            self.logger.info("📋 Versuche Text aus Zwischenablage zu lesen...")
            text = pyperclip.paste()

            if text and text.strip():
                self.logger.info(f"📝 Text aus Zwischenablage gelesen: '{text[:50]}...'")
                self.logger.info("⌨️  Füge Text an Cursor-Position ein...")

                # Verwende sichere Text-Eingabe
                if self._safe_write_text(text):
                    self.logger.info(f"✅ Text erfolgreich eingefügt: {text[:50]}...")
                    self.toaster.show_info("📋 Text eingefügt", f"'{text[:50]}...'")
                else:
                    self.logger.error("❌ Text konnte nicht eingefügt werden")
                    self.toaster.show_error("Text konnte nicht eingefügt werden", "Text einfügen")

            else:
                self.logger.warning("⚠️  Kein Text in der Zwischenablage zum Einfügen")
                self.toaster.show_warning("Kein Text in der Zwischenablage zum Einfügen", "Text einfügen")

        except Exception as e:
            self.logger.error(f"❌ Text konnte nicht eingefügt werden: {e}")
            self.logger.error(f"🔍 Exception Details: {type(e).__name__}: {e}")

            # Versuche es mit Fallback-Methode
            try:
                self.logger.info("🔄 Versuche Fallback-Einfüge-Methode...")
                # Verwende pyautogui.hotkey für bessere Kompatibilität
                pyautogui.hotkey("ctrl", "v")
                self.logger.info("✅ Text mit Fallback-Methode eingefügt")
                self.toaster.show_info("📋 Text eingefügt", "Text (Fallback)")
            except Exception as fallback_error:
                self.logger.error(f"❌ Fallback-Methode fehlgeschlagen: {fallback_error}")
                self.toaster.show_error(f"Text konnte nicht eingefügt werden: {e}", "Text einfügen")

    def start_recording(self) -> None:
        """Start voice recording and transcription."""
        if self._is_recording:
            self.logger.warning("⚠️  Aufnahme läuft bereits")
            self.toaster.show_warning("Aufnahme läuft bereits", "Aufnahme")
            return

        self.logger.info("🎙️  Starte Sprachaufnahme...")

        # Set volume to reduced level
        self.volume_controller.reduce_volume()

        # Start the recorder
        try:
            self.logger.debug("🎵 Starte Audio-Recorder...")
            self.recorder.start_recording()
            self.logger.info("✅ Audio-Recorder erfolgreich gestartet")

            # Only set recording state after successful start
            self._is_recording = True

            # Show notification
            self.toaster.show_info("🎙️ Aufnahme gestartet", "Sprachaufnahme läuft...")

            # Update system tray icon
            self.systray.update_recording_state(True)

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Starten des Audio-Recorders: {e}")
            self._is_recording = False
            self.toaster.show_error(f"Fehler beim Starten der Aufnahme: {e}", "Aufnahme")
            return

    def stop_recording(self) -> None:
        """Stop voice recording and process audio."""
        if not self._is_recording:
            self.logger.warning("⚠️  Keine Aufnahme aktiv")
            self.toaster.show_warning("Keine Aufnahme aktiv", "Aufnahme")
            return

        self.logger.info("🛑 Stoppe Sprachaufnahme...")
        self._is_recording = False
        self._last_recording_stop_timestamp = time.time()

        # Stelle Lautstärke sicher wieder her
        self.volume_controller.restore_volume()

        # Stop the recorder
        try:
            # Get audio data & stopping
            audio_data = self.recorder.stop_recording()
            self.logger.info("🎵 Audio-Recorder gestoppt")

            # Process audio data immediately if available
            if audio_data is None or len(audio_data) <= 0:
                self.logger.warning("❌ Keine Audioaufnahme verfügbar")
                self.toaster.show_warning("Keine Audioaufnahme", "Aufnahme")
                return  # Beende die Methode hier, da keine Audio-Daten verfügbar sind

            # Transcribe audio (ohne Spellchecking für schnelle Rückgabe)
            duration = len(audio_data) / self.recorder.sample_rate_hz
            self.logger.info(f"🔊 Audio verarbeitet: {len(audio_data):,} Samples, {duration:.2f}s")

            self.logger.info("🎯 Starte Sprach-zu-Text Transkription...")
            raw_text = self.transcriptor.transcribe_raw(audio_data)

            self.toaster.show_success("✨ Transkription abgeschlossen", f"'{raw_text[:50]}...' ({duration:.1f}s)", force_show=True)

            # Save audio recording to database if enabled
            recording_id = None
            self.logger.debug(
                f"🔍 Database config: enabled={self.config.database.get('enabled', False)}, auto_save={self.config.database.get('auto_save_recordings', False)}"
            )
            if self.config.database.get('enabled', False) and self.config.database.get('auto_save_recordings', False):
                try:
                    self.logger.info("💾 Speichere Audio-Aufnahme in Datenbank...")
                    self.logger.debug(
                        f"🔍 Audio data: shape={audio_data.shape}, dtype={audio_data.dtype}, duration={duration}s"
                    )
                    self.logger.debug(f"🔍 Sample rate: {self.recorder.sample_rate_hz}, channels: {self.recorder.num_channels}")
                    self.logger.debug(f"🔍 Audio format: {self.config.audio.format}")

                    recording_id = self.audio_database.save_audio_recording(
                        audio_data=audio_data,
                        sample_rate=self.recorder.sample_rate_hz,
                        channels=self.recorder.num_channels,
                        duration=duration,
                        audio_format=self.config.database.get('audio_format', 'wav'),
                    )
                    self.logger.info(f"✅ Audio-Aufnahme gespeichert (ID: {recording_id})")
                except Exception as e:
                    self.logger.warning(f"⚠️  Konnte Audio-Aufnahme nicht speichern: {e}")
                    self.logger.debug(f"🔍 Exception details: {type(e).__name__}: {e}")
            else:
                self.logger.debug("💾 Audio-Speicherung deaktiviert")

            # Process transcription results
            if raw_text and raw_text.strip():
                self.logger.info("✨ Transkription erfolgreich abgeschlossen!")
                self.logger.info(f"📝 Roher Text: '{raw_text}'")

                # Save transcription to database if enabled
                transcription_id = None
                if self.config.database.get('enabled', False) and self.config.database.get('auto_save_transcriptions', False) and recording_id:
                    try:
                        transcription_id = self.audio_database.save_transcription(
                            audio_recording_id=recording_id,
                            raw_text=raw_text,
                            language=self.config.transcription.get('language', 'de'),
                        )
                        self.logger.info(f"✅ Transkription in Datenbank gespeichert (ID: {transcription_id})")

                        # Mark as training data if enabled
                        if self.config.database.get('mark_as_training_data', False):
                            self.audio_database.save_training_data(
                                transcription_id=transcription_id,
                                is_valid_for_training=True,
                            )
                            self.logger.info("🏷️  Als Trainingsdaten markiert")
                    except Exception as e:
                        self.logger.warning(f"⚠️  Konnte Transkription nicht speichern: {e}")
                else:
                    self.logger.debug("💾 Transkriptions-Speicherung deaktiviert oder keine Aufnahme-ID verfügbar")

                # Show transcription complete notification
                notification_duration = len(audio_data) / self.recorder.sample_rate_hz
                self.toaster.show_success("✨ Transkription abgeschlossen", f"'{raw_text[:50]}...' ({notification_duration:.1f}s)", force_show=True)

                # Sofort rohe Transkription in Clipboard kopieren
                self.logger.info("📋 Kopiere Text in Zwischenablage...")
                try:
                    pyperclip.copy(raw_text)
                    self.logger.info("✅ Text erfolgreich in Zwischenablage kopiert!")
                    self.logger.info(f"🎤 Transkribiert: '{raw_text}'")

                    # Automatisches Einfügen falls aktiviert
                    if self.config.notifications.get("auto_insert_enabled", False):  # Check if auto insert is enabled
                        self.logger.info("🔄 Automatisches Einfügen aktiviert - füge Text ein...")
                        time.sleep(0.2)  # Kurze Pause für bessere Stabilität
                        self._paste_text()
                        self.logger.info("✅ Text automatisch eingefügt!")

                except Exception as clipboard_error:
                    self.logger.error(f"❌ Fehler beim Kopieren in Zwischenablage: {clipboard_error}")
                    self.toaster.show_error(f"Clipboard-Fehler: {clipboard_error}", "Zwischenablage")
                    # Fallback: Versuche es nochmal mit kurzer Verzögerung
                    try:
                        time.sleep(0.1)
                        pyperclip.copy(raw_text)
                        self.logger.info("✅ Text erfolgreich in Zwischenablage kopiert (Fallback)!")
                    except Exception as fallback_error:
                        self.logger.error(f"❌ Fallback Clipboard-Versuch fehlgeschlagen: {fallback_error}")
                        self.toaster.show_error("Clipboard-System funktioniert nicht", "Kritischer Fehler")

                # Im Hintergrund Spellchecking machen
                # self.logger.info(f"🔄 Starte Hintergrund-Spellchecking...")
                # self._spellcheck_background(raw_text, audio_data)
            else:
                self.logger.warning("❌ Keine Sprache erkannt")
                self.toaster.show_warning("Keine Sprache erkannt", "Transkription")

        except Exception as e:
            self.logger.error(f"Failed to stop recorder: {e}")
            self.toaster.show_error(f"Fehler beim Stoppen der Aufnahme: {e}", "Aufnahme")

        # Update system tray icon
        self.systray.update_recording_state(False)

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
                    self.logger.info("🔄 Text korrigiert - aktualisiere Zwischenablage...")
                    pyperclip.copy(corrected_text)
                    self.logger.info("📋 Zwischenablage mit korrigiertem Text aktualisiert!")
                    self.logger.info(f"🎯 Korrektur: '{raw_text}' → '{corrected_text}'")

                    # Show notification
                    self.toaster.show_success("🔍 Rechtschreibprüfung", f"'{raw_text}' → '{corrected_text}'")
                else:
                    self.logger.info("✅ Keine Korrekturen nötig - Text ist bereits korrekt")
                    self.logger.info("📋 Zwischenablage bleibt unverändert")

                    # Show notification
                    self.toaster.show_success("🔍 Rechtschreibprüfung", f"'{raw_text}' → '{corrected_text}'")

                self.logger.info("🏁 Hintergrund-Spellchecking erfolgreich abgeschlossen")

            except Exception as spell_error:
                self.logger.warning(f"❌ Spellchecking fehlgeschlagen: {spell_error}")
                self.logger.warning("⚠️  Verwende ursprünglichen Text ohne Korrekturen")

        self.logger.info("🚀 Starte Spellchecking-Thread im Hintergrund...")
        # Starte Spellchecking im Hintergrund
        spellcheck_thread = threading.Thread(target=spellcheck_worker)
        spellcheck_thread.daemon = True
        spellcheck_thread.start()
        self.logger.info(f"✅ Spellchecking-Thread gestartet (Thread-ID: {spellcheck_thread.ident})")

    def run(self) -> None:
        """Start the Mauscribe application."""
        self.logger.info("🚀 Starte Mauscribe-Anwendung...")

        # Setup system tray
        self.systray.setup()

        self.logger.info("🔄 Initialisiere System Tray...")

        # Run system tray in a separate thread so we can monitor shutdown
        tray_thread = threading.Thread(target=self._run_system_tray)
        tray_thread.daemon = True
        tray_thread.start()
        self.logger.info("✅ System Tray läuft im Hintergrund")

        self.toaster.show_info("Mauscribe erfolgreich gestartet", "Anwendung")

        self.logger.info("🎯 Mauscribe Steuerung:")
        self.logger.info(f"\t🐭 {self.config.primary_name} (press): Aufnahme starten/stoppen")
        self.logger.info(f"\t🐭 {self.config.secondary_name} (hold): Text einfügen")
        self.logger.info("🎮 Bereit für Eingaben!")

        while not self.shutdown_event.is_set():
            time.sleep(0.1)
        self.logger.info("🔄 Shutdown-Signal empfangen - beende System Tray...")

    def _run_system_tray(self) -> None:
        """Run system tray in a separate thread."""
        if not self.systray.is_available():
            self.logger.error("❌ System Tray ist nicht verfügbar")
            return

        try:
            self.logger.info("🔄 Starte System Tray Thread...")
            self.systray.run()
            self.logger.info("✅ System Tray Thread läuft")
        except Exception as e:
            self.logger.error(f"❌ System Tray Fehler: {e}")
            # Don't shutdown the entire app if system tray fails

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
            self.controlls.stop()
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
            self.systray.stop()
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
        if hasattr(self, "toaster"):
            self.toaster.show_info("Mauscribe erfolgreich beendet", "Anwendung")

        self.logger.info("✅ Mauscribe-Anwendung erfolgreich beendet")

    def _setup_signal_handlers(self) -> None:
        """Set up signal handlers for graceful shutdown."""
        try:
            signal.signal(signal.SIGINT, self._handle_signal)
            signal.signal(signal.SIGTERM, self._handle_signal)
            self.logger.info("✅ Signal-Handler für Strg+C erfolgreich eingerichtet")
        except Exception as e:
            self.logger.error(f"⚠️  Signal-Handler konnte nicht eingerichtet werden: {e}")

    def _handle_signal(self, signum: int, frame: Any) -> None:
        """Handle system signals for graceful shutdown."""
        signal_name = "SIGINT" if signum == signal.SIGINT else "SIGTERM"
        self.logger.info(f"🛑 Signal {signal_name} empfangen - starte graceful shutdown...")
        self.shutdown_event.set()

        # Force stop recording if active
        if self._is_recording:
            self.logger.info("🛑 Stoppe aktive Aufnahme...")
            self._is_recording = False
            self.recorder.stop_recording()

        # Stelle Lautstärke sicher wieder her
        if hasattr(self.recorder, "restore_volume"):
            self.logger.info("🔄 Stelle System-Lautstärke wieder her...")
            self.volume_controller.restore_volume()


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
