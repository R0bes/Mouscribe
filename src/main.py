# src/main.py - Main application entry point for Mauscribe
"""
Mauscribe - Voice-to-Text Tool
Main application logic and system tray integration
"""

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
        self.config = Config()
        self.sound_controller = SoundController()
        self.input_handler = InputHandler()
        self.stt = SpeechToText()
        self.recorder = AudioRecorder()
        self.spell_checker = SpellGrammarChecker()

        self.is_recording = False
        self.recording_thread: Optional[threading.Thread] = None
        self.system_tray: Optional[pystray.Icon] = None

        # Volume management
        self._original_volume = None
        self._last_click_time = 0
        self._click_debounce_ms = 500

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
        try:
            self._original_volume = self.sound_controller.get_volume()
            target_volume = max(
                10, int(self._original_volume * self.config.volume_reduction_factor)
            )
            self.sound_controller.set_volume(target_volume)
            print(f"Volume reduced from {self._original_volume}% to {target_volume}%")
        except Exception as e:
            print(f"Failed to reduce volume: {e}")

    def _restore_volume(self) -> None:
        """Restore system volume after recording."""
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

        # Debounce double-clicks
        current_time = time.time() * 1000
        if current_time - self._last_click_time < self._click_debounce_ms:
            return
        self._last_click_time = current_time

        if str(button) == self.config.mouse_button_primary:
            if not self.is_recording:
                self.start_recording()
            else:
                self.stop_recording()
        elif str(button) == self.config.mouse_button_secondary:
            self._paste_text()

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
            print("Already recording")
            return

        print("Starting recording...")
        self.is_recording = True

        # Reduce volume
        self._reduce_volume()

        # Start recording in background thread
        self.recording_thread = threading.Thread(target=self._recording_worker)
        self.recording_thread.daemon = True
        self.recording_thread.start()

        # Update system tray icon
        if self.system_tray:
            self.system_tray.icon = self._create_system_tray_icon()

    def stop_recording(self) -> None:
        """Stop voice recording and process audio."""
        if not self.is_recording:
            print("Not recording")
            return

        print("Stopping recording...")
        self.is_recording = False

        # Wait for recording thread to finish
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=2)

        # Restore volume
        self._restore_volume()

        # Update system tray icon
        if self.system_tray:
            self.system_tray.icon = self._create_system_tray_icon()

    def _recording_worker(self) -> None:
        """Background worker for audio recording and processing."""
        try:
            # Record audio
            audio_data = self.recorder.record_audio()

            if audio_data is not None and len(audio_data) > 0:
                # Transcribe audio
                text = self.stt.transcribe(audio_data)

                if text and text.strip():
                    # Spell check and correct
                    corrected_text = self.spell_checker.correct_text(text)

                    # Copy to clipboard
                    pyperclip.copy(corrected_text)
                    print(f"Transcribed: {corrected_text}")
                else:
                    print("No speech detected")
            else:
                print("No audio recorded")

        except Exception as e:
            print(f"Recording error: {e}")

    def run(self) -> None:
        """Start the Mauscribe application."""
        print("Starting Mauscribe...")

        # Setup system tray
        self._setup_system_tray()

        # Setup input handling
        self.input_handler.setup_mouse_listener(self._on_mouse_click)

        # Start system tray
        if self.system_tray:
            self.system_tray.run()

    def stop(self) -> None:
        """Stop the Mauscribe application."""
        print("Stopping Mauscribe...")

        # Stop recording if active
        if self.is_recording:
            self.stop_recording()

        # Stop input handling
        self.input_handler.stop()

        # Stop system tray
        if self.system_tray:
            self.system_tray.stop()

        print("Mauscribe stopped")


def main() -> None:
    """Main entry point for the Mauscribe application."""
    app = MauscribeApp()

    try:
        app.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Application error: {e}")
    finally:
        app.stop()


if __name__ == "__main__":
    main()
