# src/main.py - Main application entry point for Mauscribe
"""
Mauscribe - Voice-to-Text Tool
Main application logic and system tray integration
"""

import logging
import sys
import threading
import time
from pathlib import Path
from typing import Any, Optional

import pyautogui
import pyperclip
import pystray
from PIL import Image, ImageDraw

from .config import Config
from .input_handler import InputHandler
from .recorder import AudioRecorder
from .sound_controller import SoundController
from .spell_checker import SpellGrammarChecker
from .stt import SpeechToText


class MauscribeApp:
    """Main application class for Mauscribe voice-to-text tool."""

    def __init__(self):
        """Initialize the Mauscribe application."""
        # Setup logging first
        self._setup_logging()

        try:
            self.config = Config()
            print("Configuration loaded successfully")
        except Exception as e:
            print(f"Failed to load configuration: {e}")
            sys.exit(1)

        try:
            self.sound_controller = SoundController()
            if not self.sound_controller.is_available():
                print(
                    "⚠️  Warning: Audio control not available - volume reduction disabled"
                )
            else:
                print("Audio control initialized successfully")
        except Exception as e:
            print(f"Failed to initialize sound controller: {e}")
            self.sound_controller = None

        try:
            self.input_handler = InputHandler()
            print("Input handler initialized successfully")
        except Exception as e:
            print(f"Failed to initialize input handler: {e}")
            sys.exit(1)

        try:
            self.stt = SpeechToText()
            print("Speech-to-text initialized successfully")
        except Exception as e:
            print(f"Failed to initialize STT: {e}")
            sys.exit(1)

        try:
            self.recorder = AudioRecorder()
            print("Audio recorder initialized successfully")
        except Exception as e:
            print(f"Failed to initialize audio recorder: {e}")
            sys.exit(1)

        try:
            self.spell_checker = SpellGrammarChecker()
            print("Spell checker initialized successfully")
        except Exception as e:
            print(f"Failed to initialize spell checker: {e}")
            sys.exit(1)

        self.is_recording = False
        self.recording_thread: Optional[threading.Thread] = None
        self.system_tray: Optional[pystray.Icon] = None

        # Volume management
        self._original_volume = None
        self._last_click_time = 0
        self._click_debounce_ms = 500

    def _setup_logging(self) -> None:
        """Setup logging configuration based on config."""
        try:
            # Get log level from config
            config = Config()
            log_level = getattr(logging, config.debug_level.upper(), logging.INFO)

            # Configure logging
            logging.basicConfig(
                level=log_level,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.StreamHandler(),
                    logging.FileHandler("mauscribe.log", encoding="utf-8"),
                ],
            )

            self.logger = logging.getLogger("Mauscribe")

            if config.debug_enabled:
                self.logger.setLevel(logging.DEBUG)
                self.logger.debug("Debug logging enabled")
            else:
                self.logger.setLevel(log_level)

        except Exception as e:
            # Fallback logging if config fails
            logging.basicConfig(
                level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
            )
            self.logger = logging.getLogger("Mauscribe")
            self.logger.warning(f"Failed to setup logging from config: {e}")

    def _create_system_tray_icon(self) -> Image.Image:
        """Create a custom microphone icon for the system tray."""
        # Create a 64x64 image with transparent background
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Draw microphone icon
        # Microphone body (rectangle)
        draw.rectangle(
            (20, 15, 44, 45), fill=(70, 130, 180), outline=(50, 100, 150), width=2
        )

        # Microphone head (circle)
        draw.ellipse(
            (18, 8, 46, 36), fill=(70, 130, 180), outline=(50, 100, 150), width=2
        )

        # Microphone stand
        draw.rectangle(
            (30, 45, 34, 55), fill=(70, 130, 180), outline=(50, 100, 150), width=2
        )

        # Recording indicator (red dot when recording)
        if self.is_recording:
            draw.ellipse(
                [50, 10, 58, 18], fill=(255, 0, 0), outline=(200, 0, 0), width=1
            )

        return img

    def _setup_system_tray(self) -> None:
        """Initialize the system tray icon and menu."""
        try:
            icon_image = self._create_system_tray_icon()

            def on_clicked(icon: Any, item: Any) -> None:
                """Handle system tray menu item clicks."""
                if str(item) == "Status":
                    self._print_status()
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

            self.system_tray = pystray.Icon(
                "mauscribe", icon_image, "Mauscribe - Voice-to-Text Tool", menu
            )
            print("System tray initialized successfully")
        except Exception as e:
            print(f"Failed to initialize system tray: {e}")
            print(
                "⚠️  Warning: System tray not available - application will run in console mode"
            )
            self.system_tray = None

    def _print_status(self) -> None:
        """Print current application status."""
        status = "Recording" if self.is_recording else "Idle"
        print(f"Mauscribe Status: {status}")
        print(f"Input Method: {self.config.input_method}")
        print(f"Mouse Button: {self.config.mouse_button_primary}")
        print(f"Audio Device: {self.config.audio_device}")

    def _open_config_file(self) -> None:
        """Open the configuration file in default editor."""
        config_path = Path("config.toml")
        if config_path.exists():
            try:
                import subprocess

                subprocess.run(["notepad", str(config_path)], shell=True)
            except Exception as e:
                print(f"Could not open config file: {e}")
        else:
            print("Configuration file not found")

    def _reduce_volume(self) -> None:
        """Reduce system volume during recording."""
        if not self.sound_controller or not self.sound_controller.is_available():
            print("Audio control not available - skipping volume reduction")
            return

        try:
            self._original_volume = self.sound_controller.get_volume()
            target_volume = max(
                10, int(self._original_volume * self.config.volume_reduction_factor)
            )
            self.sound_controller.set_volume(target_volume)
            print(f"Volume reduced from {self._original_volume}% to {target_volume}%")
        except Exception as e:
            print(f"Failed to reduce volume: {e}")
            self._original_volume = None

    def _restore_volume(self) -> None:
        """Restore system volume after recording."""
        if not self.sound_controller or not self.sound_controller.is_available():
            print("Audio control not available - skipping volume restoration")
            return

        if self._original_volume is not None:
            try:
                # Try to restore original volume
                self.sound_controller.set_volume(self._original_volume)
                print(f"Volume restored to {self._original_volume}%")
            except Exception as e:
                print(f"Failed to restore volume: {e}")
                # Fallback: set to 50%
                try:
                    self.sound_controller.set_volume(50)
                    print("Volume set to 50% (fallback)")
                except Exception as e2:
                    print(f"Fallback volume setting failed: {e2}")
            finally:
                self._original_volume = None

    def _on_mouse_click(self, x: int, y: int, button: Any, pressed: bool) -> None:
        """Handle mouse click events for recording control."""
        if not pressed:
            return

        # Extract button name (remove "Button." prefix)
        button_name = str(button).replace("Button.", "")
        self.logger.debug(
            f"Mouse click detected: button={button_name}, position=({x}, {y})"
        )

        # Only handle X2 button
        if button_name == self.config.mouse_button_primary:
            current_time = time.time() * 1000
            time_diff = current_time - self._last_click_time

            if time_diff < self._click_debounce_ms:
                # This is a double-click X2 - handle based on recording state
                self.logger.info(f"Double-click X2 detected ({time_diff:.1f}ms)")

                if self.is_recording:
                    # If recording: stop recording and insert text
                    self.logger.info(
                        "Double-click X2 while recording - stopping and inserting text"
                    )
                    self.stop_recording()
                    # Wait a moment for recording to finish, then insert text
                    time.sleep(0.5)
                    self._paste_text()
                else:
                    # If not recording: just insert text
                    self.logger.info(
                        "Double-click X2 while not recording - inserting text"
                    )
                    self._paste_text()

                self._last_click_time = 0  # Reset to allow new double-clicks
            else:
                # Single click X2 - toggle recording
                self.logger.debug("Single click X2 - toggling recording")
                if not self.is_recording:
                    self.logger.info("Starting recording via single X2 click")
                    self.start_recording()
                else:
                    self.logger.info("Stopping recording via single X2 click")
                    self.stop_recording()

                self._last_click_time = current_time
        else:
            # Other buttons - just log for debugging
            self.logger.debug(f"Ignoring non-X2 button: {button_name}")

    def _paste_text(self) -> None:
        """Paste transcribed text to current cursor position."""
        try:
            text = pyperclip.paste()
            if text and text.strip():
                pyautogui.write(text)
                print(f"Text pasted: {text[:50]}...")
            else:
                print("No text in clipboard to paste")
        except Exception as e:
            print(f"Failed to paste text: {e}")

    def start_recording(self) -> None:
        """Start voice recording and transcription."""
        if self.is_recording:
            self.logger.warning("Already recording")
            print("Already recording")
            return

        self.logger.info("Starting recording...")
        print("Starting recording...")
        self.is_recording = True

        # Reduce volume
        self.logger.debug("Reducing system volume")
        self._reduce_volume()

        # Start recording in background thread
        self.logger.debug("Starting recording thread")
        self.recording_thread = threading.Thread(target=self._recording_worker)
        self.recording_thread.daemon = True
        self.recording_thread.start()

        # Update system tray icon
        if self.system_tray:
            self.logger.debug("Updating system tray icon")
            self.system_tray.icon = self._create_system_tray_icon()

    def stop_recording(self) -> None:
        """Stop voice recording and process audio."""
        if not self.is_recording:
            self.logger.warning("Not recording")
            print("Not recording")
            return

        self.logger.info("Stopping recording...")
        print("Stopping recording...")
        self.is_recording = False

        # Stop the recorder immediately
        if hasattr(self.recorder, "stop_recording_immediate"):
            try:
                self.recorder.stop_recording_immediate()
                self.logger.info("Audio recorder stopped immediately")
            except Exception as e:
                self.logger.error(f"Failed to stop recorder immediately: {e}")

        # Wait for recording thread to finish
        if self.recording_thread and self.recording_thread.is_alive():
            self.logger.debug("Waiting for recording thread to finish")
            self.recording_thread.join(timeout=2)

        # Restore volume
        self.logger.debug("Restoring system volume")
        self._restore_volume()

        # Update system tray icon
        if self.system_tray:
            self.logger.debug("Updating system tray icon")
            self.system_tray.icon = self._create_system_tray_icon()

    def _recording_worker(self) -> None:
        """Background worker for audio recording and processing."""
        try:
            self.logger.info("Starting audio recording...")

            # Record audio until stopped
            timeout_seconds = getattr(self.config, "recording_timeout_seconds", 60)
            audio_data = self.recorder.record_audio(timeout_seconds)

            if audio_data is not None and len(audio_data) > 0:
                self.logger.info(
                    f"Audio recorded successfully: {len(audio_data)} samples"
                )

                # Transcribe audio
                self.logger.info("Starting speech-to-text transcription...")
                text = self.stt.transcribe(audio_data)

                if text and text.strip():
                    self.logger.info(f"Raw transcription: {text}")

                    # Spell check and correct
                    try:
                        self.logger.info("Applying spell checking...")
                        corrected_text = self.spell_checker.check_and_correct_text(text)
                        self.logger.info(f"Corrected text: {corrected_text}")

                        # Copy to clipboard
                        pyperclip.copy(corrected_text)
                        self.logger.info(f"Text copied to clipboard: {corrected_text}")
                        print(f"🎤 Transkribiert: {corrected_text}")
                    except Exception as spell_error:
                        self.logger.warning(f"Spell checking failed: {spell_error}")
                        # Fallback: use original text
                        corrected_text = text
                        pyperclip.copy(corrected_text)
                        self.logger.info(
                            f"Using original text (spell check failed): {corrected_text}"
                        )
                        print(f"🎤 Transkribiert (ohne Korrektur): {corrected_text}")
                else:
                    self.logger.warning("No speech detected in audio")
                    print("❌ Keine Sprache erkannt")
            else:
                self.logger.warning("No audio data recorded")
                print("❌ Keine Audioaufnahme")

        except Exception as e:
            self.logger.error(f"Recording error: {e}", exc_info=True)
            print(f"❌ Aufnahmefehler: {e}")

    def run(self) -> None:
        """Start the Mauscribe application."""
        print("Starting Mauscribe...")

        # Setup system tray
        self._setup_system_tray()

        # Setup input handling
        try:
            self.input_handler.setup_mouse_listener(self._on_mouse_click)
            print("Input handling setup complete")
        except Exception as e:
            print(f"Failed to setup input handling: {e}")
            return

        # Start system tray if available
        if self.system_tray:
            try:
                print("Starting system tray...")
                self.system_tray.run()
            except Exception as e:
                print(f"System tray failed: {e}")
                print("Running in console mode...")
                self._run_console_mode()
        else:
            print("Running in console mode...")
            self._run_console_mode()

    def _run_console_mode(self) -> None:
        """Run the application in console mode without system tray."""
        print("\n" + "=" * 50)
        print("Mauscribe läuft im Konsolenmodus")
        print("=" * 50)
        print("Verwendung:")
        print("- X2-Maustaste (einfach): Aufnahme starten/stoppen")
        print("- X2-Maustaste (doppelklick): Text einfügen")
        print("- X2-Doppelklick während Aufnahme: Stoppt Aufnahme und fügt Text ein")
        print("- Drücken Sie Strg+C um zu beenden")
        print("=" * 50)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nBeende Anwendung...")
            self.stop()

    def stop(self) -> None:
        """Stop the Mauscribe application."""
        print("\n" + "=" * 50)
        print("🛑 Beende Mauscribe...")
        print("=" * 50)

        # Stop recording if active
        if self.is_recording:
            self.logger.info("Stopping active recording before shutdown")
            self.stop_recording()

        # Stop input handling
        try:
            self.input_handler.stop()
            self.logger.info("Input handler stopped")
        except Exception as e:
            self.logger.error(f"Error stopping input handler: {e}")

        # Stop system tray
        if self.system_tray:
            try:
                self.system_tray.stop()
                self.logger.info("System tray stopped")
            except Exception as e:
                self.logger.error(f"Error stopping system tray: {e}")

        # Cleanup other components
        try:
            if hasattr(self, "spell_checker"):
                self.spell_checker.close()
                self.logger.info("Spell checker closed")
        except Exception as e:
            self.logger.error(f"Error closing spell checker: {e}")

        print("✅ Mauscribe erfolgreich beendet")
        print("=" * 50)
        self.logger.info("Mauscribe shutdown completed")


def main() -> None:
    """Main entry point for the Mauscribe application."""
    print("🚀 Starte Mauscribe...")
    print("=" * 50)

    app = MauscribeApp()

    try:
        app.run()
    except KeyboardInterrupt:
        print("\n" + "=" * 50)
        print("⚠️  Programm durch Benutzer unterbrochen (Strg+C)")
        print("=" * 50)
    except Exception as e:
        print("\n" + "=" * 50)
        print(f"❌ Unerwarteter Fehler: {e}")
        print("=" * 50)
        app.logger.error(f"Unexpected error in main: {e}", exc_info=True)
    finally:
        app.stop()


if __name__ == "__main__":
    main()
