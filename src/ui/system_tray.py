# src/system_tray.py - System Tray Management for Mauscribe
"""
System Tray Management Module
Handles system tray icon, menu, and related functionality
"""
import subprocess
import threading
from pathlib import Path
from typing import Any, Optional

import pystray
from PIL import Image, ImageDraw

from ..utils.config import Config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SystemTrayManager:
    """Manages the system tray icon and menu for Mauscribe."""

    def __init__(self, config: Config, app_instance: Any) -> None:
        """Initialize the system tray manager.

        Args:
            config: Configuration instance
            app_instance: Reference to the main application instance
        """
        self.config = config
        self.app_instance = app_instance
        self.logger = get_logger(self.__class__.__name__)

        # State management
        self.system_tray: Optional[pystray.Icon] = None
        self.is_recording = False

    def create_icon(self) -> Image.Image:
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

    def setup(self) -> None:
        """Initialize the system tray icon and menu."""
        try:
            icon_image = self.create_icon()

            def on_clicked(icon: Any, item: Any) -> None:
                """Handle system tray menu item clicks."""
                if str(item) == "Status":
                    self._log_status()
                elif str(item) == "Open Config":
                    self._open_config_file()
                elif str(item) == "Database Manager":
                    self._open_database_manager()
                elif str(item) == "Exit":
                    self.app_instance.stop()

            # Create system tray menu
            menu = (
                pystray.MenuItem("Status", on_clicked),
                pystray.MenuItem("Open Config", on_clicked),
                pystray.MenuItem("Database Manager", on_clicked),
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

    def _open_database_manager(self) -> None:
        """Open the database manager GUI."""
        try:
            from .database_gui import DatabaseManagerGUI

            # Open database manager in a separate thread to avoid blocking
            def open_gui():
                try:
                    gui = DatabaseManagerGUI()
                    gui.run()
                except Exception as e:
                    logger.error(f"Failed to open database manager: {e}")

            thread = threading.Thread(target=open_gui, daemon=True)
            thread.start()
            logger.info("📊 Database Manager geöffnet")
        except Exception as e:
            logger.error(f"Failed to open database manager: {e}")

    def _open_config_file(self) -> None:
        """Open the configuration file in default editor."""
        config_path = Path(self.config.config_path)
        if config_path.exists():
            try:
                subprocess.run(["notepad", str(config_path)], shell=True)
            except Exception as e:
                logger.error(f"❌ Konfigurationsdatei konnte nicht geöffnet werden: {e}")
        else:
            logger.warning("⚠️  Konfigurationsdatei nicht gefunden")

    def update_recording_state(self, is_recording: bool) -> None:
        """Update the recording state and refresh the icon.

        Args:
            is_recording: Whether recording is currently active
        """
        self.is_recording = is_recording
        if self.system_tray:
            try:
                self.system_tray.icon = self.create_icon()
                logger.debug("System tray icon updated")
            except Exception as e:
                logger.error(f"❌ Fehler beim Aktualisieren des System Tray Icons: {e}")

    def run(self) -> None:
        """Run the system tray in a separate thread."""
        if self.system_tray is None:
            logger.error("❌ System Tray ist nicht verfügbar")
            return

        try:
            self.system_tray.run()
        except Exception as e:
            logger.error(f"❌ System Tray Fehler: {e}")

    def stop(self) -> None:
        """Stop the system tray."""
        if self.system_tray:
            try:
                self.system_tray.stop()
                logger.info("✅ System Tray beendet")
            except Exception as e:
                logger.error(f"❌ Fehler beim Beenden des System Tray: {e}")

    def is_available(self) -> bool:
        """Check if system tray is available.

        Returns:
            True if system tray is available, False otherwise
        """
        return self.system_tray is not None
