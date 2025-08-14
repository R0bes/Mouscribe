# src/main.py - Main application entry point for Mauscribe
"""
Mauscribe - Voice-to-Text Tool
Main application logic and system tray integration
"""
import signal
import sys
import threading
import time
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pyautogui
import pyperclip
import pystray
from PIL import Image, ImageDraw

from .config import Config
from .input_handler import InputHandler
from .logger import get_logger
from .recorder import AudioRecorder
from .spell_checker import SpellChecker
from .stt import SpeechToText

logger = get_logger("Mauscribe")


class MauscribeApp:
    """Main application class for Mauscribe voice-to-text tool."""

    def __init__(self):
        """Initialize the Mauscribe application."""

        try:
            self.config = Config()
            logger.info("✅ Konfiguration erfolgreich geladen")
        except Exception as e:
            logger.error(f"❌ Konfiguration konnte nicht geladen werden: {e}")
            sys.exit(1)

        try:
            self.input_handler = InputHandler()
            logger.info("🖱️  Input Handler erfolgreich initialisiert")
        except Exception as e:
            logger.error(f"❌ Input Handler konnte nicht initialisiert werden: {e}")
            sys.exit(1)

        try:
            self.stt = SpeechToText()
            logger.info("🎤 Speech-to-Text erfolgreich initialisiert")
        except Exception as e:
            logger.error(f"❌ Speech-to-Text konnte nicht initialisiert werden: {e}")
            sys.exit(1)

        try:
            self.recorder = AudioRecorder()
            logger.info("🎙️  Audio-Recorder erfolgreich initialisiert")
        except Exception as e:
            logger.error(f"❌ Audio-Recorder konnte nicht initialisiert werden: {e}")
            sys.exit(1)

        try:
            self.spell_checker = SpellChecker()
            logger.info("✏️  Rechtschreibprüfung erfolgreich initialisiert")
        except Exception as e:
            logger.error(f"❌ Rechtschreibprüfung konnte nicht initialisiert werden: {e}")
            sys.exit(1)

        self.is_recording = False
        self.system_tray: Optional[pystray.Icon] = None
        self.shutdown_event = threading.Event()

        self._last_click_time = 0
        self._click_debounce_ms = 500

        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()

    def _create_system_tray_icon(self) -> Image.Image:
        """Create a custom microphone icon for the system tray."""
        # Create a 64x64 image with transparent background
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Draw microphone icon
        # Microphone body (rectangle)
        draw.rectangle((20, 15, 44, 45), fill=(70, 130, 180), outline=(50, 100, 150), width=2)

        # Microphone head (circle)
        draw.ellipse((18, 8, 46, 36), fill=(70, 130, 180), outline=(50, 100, 150), width=2)

        # Microphone stand
        draw.rectangle((30, 45, 34, 55), fill=(70, 130, 180), outline=(50, 100, 150), width=2)

        # Recording indicator (red dot when recording)
        if self.is_recording:
            draw.ellipse([50, 10, 58, 18], fill=(255, 0, 0), outline=(200, 0, 0), width=1)

        return img

    def _setup_system_tray(self) -> None:
        """Initialize the system tray icon and menu."""
        try:
            icon_image = self._create_system_tray_icon()

            def on_clicked(icon: Any, item: Any) -> None:
                """Handle system tray menu item clicks."""
                if str(item) == "Status":
                    self._log_status()
                elif str(item) == "Open Config":
                    self._open_config_file()
                elif str(item) == "Exit":
                    self.stop()

            # Create system tray menu
            menu = (
                pystray.MenuItem("Status", on_clicked),
                pystray.MenuItem("Open Config", on_clicked),
                pystray.MenuItem("Exit", on_clicked),
            )

            self.system_tray = pystray.Icon("mauscribe", icon_image, "Mauscribe - Voice-to-Text Tool", menu)
            logger.info("🖥️  System Tray erfolgreich initialisiert")
        except Exception as e:
            logger.error(f"❌ System Tray konnte nicht initialisiert werden: {e}")
            logger.warning("⚠️  System Tray nicht verfügbar - Anwendung läuft im Konsolenmodus")
            self.system_tray = None

    def _log_status(self) -> None:
        """Log current application status."""
        status = "Recording" if self.is_recording else "Idle"
        logger.info(f"📊 Mauscribe Status: {status}")
        logger.info(f"🖱️  Input Methode: {self.config.input_method}")
        logger.info(f"🔘 Maus-Taste: {self.config.mouse_button_primary}")
        logger.info(f"🎤 Audio-Gerät: {self.config.audio_device}")

    def _open_config_file(self) -> None:
        """Open the configuration file in default editor."""
        config_path = Path("config.toml")
        if config_path.exists():
            try:
                import subprocess

                subprocess.run(["notepad", str(config_path)], shell=True)
            except Exception as e:
                logger.error(f"❌ Konfigurationsdatei konnte nicht geöffnet werden: {e}")
        else:
            logger.warning("⚠️  Konfigurationsdatei nicht gefunden")

    def _on_mouse_click(self, x: int, y: int, button: Any, pressed: bool) -> None:
        """Handle mouse click events for recording control."""
        if not pressed:
            return

        # Extract button name (remove "Button." prefix)
        button_name = str(button).replace("Button.", "")
        logger.debug(f"Mouse click detected: button={button_name}, position=({x}, {y})")

        # Only handle X2 button
        if button_name == self.config.mouse_button_primary:
            current_time = time.time() * 1000
            time_diff = current_time - self._last_click_time

            if time_diff < self._click_debounce_ms:
                # This is a double-click X2 - handle based on recording state
                logger.info(f"Double-click X2 detected ({time_diff:.1f}ms)")

                if self.is_recording:
                    # If recording: stop recording and insert text
                    logger.info("Double-click X2 while recording - stopping and inserting text")
                    self.stop_recording()
                    # Wait a moment for recording to finish, then insert text
                    time.sleep(0.5)
                    self._paste_text()
                else:
                    # If not recording: just insert text
                    logger.info("Double-click X2 while not recording - inserting text")
                    self._paste_text()

                self._last_click_time = 0  # Reset to allow new double-clicks
            else:
                # Single click X2 - toggle recording
                logger.debug("Single click X2 - toggling recording")
                if not self.is_recording:
                    logger.info("Starting recording via single X2 click")
                    self.start_recording()
                else:
                    logger.info("Stopping recording via single X2 click")
                    self.stop_recording()

                self._last_click_time = current_time
        else:
            # Other buttons - just log for debugging
            logger.debug(f"Ignoring non-X2 button: {button_name}")

    def _paste_text(self) -> None:
        """Paste transcribed text to current cursor position."""
        try:
            text = pyperclip.paste()
            if text and text.strip():
                pyautogui.write(text)
                logger.info(f"📋 Text eingefügt: {text[:50]}...")
            else:
                logger.warning("⚠️  Kein Text in der Zwischenablage zum Einfügen")
        except Exception as e:
            logger.error(f"❌ Text konnte nicht eingefügt werden: {e}")

    def start_recording(self) -> None:
        """Start voice recording and transcription."""
        if self.is_recording:
            logger.warning("⚠️  Aufnahme läuft bereits")
            return

        logger.info("🎙️  Starte Aufnahme...")
        self.is_recording = True

        # Start the recorder
        try:
            logger.debug("Starting audio recorder")
            self.recorder.start_recording()
            logger.info("✅ Audio recorder started successfully")
        except Exception as e:
            logger.error(f"❌ Failed to start audio recorder: {e}")
            self.is_recording = False
            return

        # Update system tray icon
        if self.system_tray:
            logger.debug("Updating system tray icon")
            self.system_tray.icon = self._create_system_tray_icon()

    def stop_recording(self) -> None:
        """Stop voice recording and process audio."""
        if not self.is_recording:
            logger.warning("⚠️  Keine Aufnahme aktiv")
            return

        logger.info("🛑 Stoppe Aufnahme...")
        self.is_recording = False

        # Stop the recorder
        try:
            # Get audio data before stopping
            audio_data = self.recorder.stop_recording()
            logger.info("Audio recorder stopped")

            # Process audio data immediately if available
            if audio_data is not None and len(audio_data) > 0:
                logger.info(
                    f"🔊 Audio-Daten: {len(audio_data)} Samples, {len(audio_data) / self.recorder.sample_rate_hz:.2f}s"
                )

                # Transcribe audio (ohne Spellchecking für schnelle Rückgabe)
                logger.info("🎯 Starting speech-to-text transcription...")

                raw_text = self.stt.transcribe_raw(audio_data)

                if raw_text and raw_text.strip():
                    logger.info("✨ STT-Transkription abgeschlossen!")
                    logger.info(f"📝 Roher Text: '{raw_text}'")

                    # Sofort rohe Transkription in Clipboard kopieren
                    logger.info("📋 Kopiere rohen Text in Clipboard...")
                    pyperclip.copy(raw_text)
                    logger.info("✅ Roher Text in Clipboard verfügbar!")
                    logger.info(f"🎤 Transkribiert (roh): {raw_text}")

                    # Im Hintergrund Spellchecking machen
                    # logger.info(f"🔄 Starte Hintergrund-Spellchecking...")
                    # self._spellcheck_background(raw_text, audio_data)
                else:
                    logger.warning("❌ Keine Sprache erkannt")
            else:
                logger.warning("❌ Keine Audioaufnahme")

        except Exception as e:
            logger.error(f"Failed to stop recorder: {e}")

        # Update system tray icon
        if self.system_tray:
            logger.debug("Updating system tray icon")
            self.system_tray.icon = self._create_system_tray_icon()

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
                else:
                    logger.info("✅ Keine Korrekturen nötig - Text ist bereits korrekt")
                    logger.info("📋 Clipboard bleibt unverändert")

                logger.info("🏁 Hintergrund-Spellchecking abgeschlossen")

            except Exception as spell_error:
                logger.warning(f"❌ Spellchecking fehlgeschlagen: {spell_error}")
                logger.warning("⚠️  Verwende ursprünglichen Text ohne Korrekturen")

        logger.info("🚀 Starte Spellchecking-Thread im Hintergrund...")
        # Starte Spellchecking im Hintergrund
        spellcheck_thread = threading.Thread(target=spellcheck_worker)
        spellcheck_thread.daemon = True
        spellcheck_thread.start()
        logger.info(f"✅ Spellchecking-Thread gestartet (Thread-ID: {spellcheck_thread.ident})")

    def run(self) -> None:
        """Start the Mauscribe application."""
        logger.info("🚀 Starte Mauscribe...")

        # Setup system tray
        self._setup_system_tray()

        # Setup input handling
        try:
            logger.info("🔄 Richte Input Handler ein...")
            self.input_handler.setup_mouse_listener(self._on_mouse_click)
            logger.info("✅ Input handling setup complete")
        except Exception as e:
            logger.error(f"❌ Input Handler konnte nicht eingerichtet werden: {e}")
            return

        # Start system tray if available
        if self.system_tray:
            try:
                logger.info("🔄 Starte System Tray...")
                # Run system tray in a separate thread so we can monitor shutdown
                tray_thread = threading.Thread(target=self._run_system_tray)
                tray_thread.daemon = True
                tray_thread.start()

                logger.info("✅ System Tray läuft im Hintergrund")
                logger.info("💡 Drücken Sie Strg+C um zu beenden")

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
        if self.system_tray is None:
            logger.error("❌ System Tray ist nicht verfügbar")
            self.shutdown_event.set()
            return

        try:
            self.system_tray.run()
        except Exception as e:
            logger.error(f"❌ System Tray Fehler: {e}")
            self.shutdown_event.set()

    def _run_console_mode(self) -> None:
        """Run the application in console mode without system tray."""
        logger.info("🖥️  Mauscribe läuft im Konsolenmodus")
        logger.info("📋 Verwendung:")
        logger.info("- X2-Maustaste (einfach): Aufnahme starten/stoppen")
        logger.info("- X2-Maustaste (doppelklick): Text einfügen")
        logger.info("- X2-Doppelklick während Aufnahme: Stoppt Aufnahme und fügt Text ein")
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
        if self.is_recording:
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
        if self.system_tray:
            try:
                self.system_tray.stop()
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
        logger.info(f"Received signal {signum} ({signal_name}). Initiating graceful shutdown.")
        self.shutdown_event.set()

        # Force stop recording if active
        if self.is_recording:
            logger.info("🛑 Stoppe aktive Aufnahme...")
            self.is_recording = False
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
