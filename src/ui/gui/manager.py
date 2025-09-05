# src/ui/gui/manager.py - GUI Manager for Mauscribe
"""
Central GUI manager for Mauscribe application.
Handles GUI initialization, lifecycle, and coordination.
"""

import threading
import time
from typing import Optional

from ...utils.config import Config
from ...utils.logger import get_logger
from ..notifications import NotificationManager
from .audio_database_gui import AudioDatabaseGUI
from .dictionary_gui import DictionaryGUI
from .modern_manager_gui import ModernManagerGUI
from .unified_manager_gui import UnifiedManagerGUI


class GUIManager:
    """Central GUI manager for Mauscribe application."""

    def __init__(self, config: Config, notification_manager: NotificationManager):
        """Initialize the GUI manager."""
        self.logger = get_logger(self.__class__.__name__)
        self.config = config
        self.notification_manager = notification_manager

        # GUI components
        self.unified_gui: Optional[UnifiedManagerGUI] = None
        self.modern_gui: Optional[ModernManagerGUI] = None
        self.audio_database_gui: Optional[AudioDatabaseGUI] = None
        self.dictionary_gui: Optional[DictionaryGUI] = None
        self.gui_thread: Optional[threading.Thread] = None

        # State management
        self._is_running = False
        self._should_auto_start = config.gui_auto_start

        self.logger.info("🔧 GUIManager wird initialisiert...")
        self.logger.info(f"   • Auto-Start: {self._should_auto_start}")
        self.logger.info(
            f"   • Window Size: {config.gui_window_width}x{config.gui_window_height}"
        )
        self.logger.info(f"   • Theme: {config.gui_theme}")
        self.logger.info(f"   • Show on Startup: {config.gui_show_on_startup}")

    def start(self) -> bool:
        """Start the GUI manager and optionally launch GUI."""
        try:
            self._is_running = True
            self.logger.info("✅ GUIManager gestartet")

            # Auto-start GUI if configured
            if self._should_auto_start and self.config.gui_show_on_startup:
                self.logger.info("🚀 Starte GUI automatisch...")
                return self.show_modern_gui()  # Use modern GUI by default

            return True

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Starten des GUIManagers: {e}")
            return False

    def stop(self) -> None:
        """Stop the GUI manager and close all GUI windows."""
        try:
            self.logger.info("🛑 Stoppe GUIManager...")
            self._is_running = False

            # Close GUI windows
            if self.unified_gui:
                self.unified_gui.close()
                self.unified_gui = None
            if self.modern_gui:
                self.modern_gui.close()
                self.modern_gui = None
            if self.audio_database_gui:
                self.audio_database_gui.close()
                self.audio_database_gui = None
            if self.dictionary_gui:
                self.dictionary_gui.close()
                self.dictionary_gui = None

            # Wait for GUI thread to finish
            if self.gui_thread and self.gui_thread.is_alive():
                self.gui_thread.join(timeout=5.0)
                if self.gui_thread.is_alive():
                    self.logger.warning(
                        "⚠️ GUI-Thread konnte nicht innerhalb von 5s beendet werden"
                    )

            self.logger.info("✅ GUIManager gestoppt")

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Stoppen des GUIManagers: {e}")

    def show_unified_gui(self) -> bool:
        """Show the unified manager GUI."""
        try:
            if self.unified_gui:
                self.logger.debug("GUI bereits geöffnet, bringe in den Vordergrund")
                self.unified_gui.bring_to_front()
                return True

            self.logger.info("🖥️ Öffne Unified Manager GUI...")

            # Create GUI in separate thread
            self.gui_thread = threading.Thread(
                target=self._run_unified_gui, name="UnifiedGUI", daemon=True
            )
            self.gui_thread.start()

            # Wait a moment for GUI to initialize
            time.sleep(0.5)

            self.logger.info("✅ Unified Manager GUI gestartet")
            return True

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Öffnen der Unified GUI: {e}")
            return False

    def show_modern_gui(self) -> bool:
        """Show the modern manager GUI."""
        try:
            if self.modern_gui:
                self.logger.debug("GUI bereits geöffnet, bringe in den Vordergrund")
                self.modern_gui.bring_to_front()
                return True

            self.logger.info("🖥️ Öffne Modern Manager GUI...")

            # Create GUI in separate thread
            self.gui_thread = threading.Thread(
                target=self._run_modern_gui, name="ModernGUI", daemon=True
            )
            self.gui_thread.start()

            # Wait a moment for GUI to initialize
            time.sleep(0.5)

            self.logger.info("✅ Modern Manager GUI gestartet")
            return True

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Öffnen der Modern GUI: {e}")
            return False

    def show_audio_database_gui(self) -> bool:
        """Show the audio database GUI."""
        try:
            if self.audio_database_gui:
                self.logger.debug(
                    "Audio Database GUI bereits geöffnet, bringe in den Vordergrund"
                )
                self.audio_database_gui.bring_to_front()
                return True

            self.logger.info("🎙️ Öffne Audio Database GUI...")

            # Create GUI in separate thread
            self.gui_thread = threading.Thread(
                target=self._run_audio_database_gui,
                name="AudioDatabaseGUI",
                daemon=True,
            )
            self.gui_thread.start()

            # Wait a moment for GUI to initialize
            time.sleep(0.5)

            self.logger.info("✅ Audio Database GUI gestartet")
            return True

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Starten der Audio Database GUI: {e}")
            self.notification_manager.show_error(
                f"GUI-Fehler: {e}", "Audio Database GUI"
            )
            return False

    def show_dictionary_gui(self) -> bool:
        """Show the dictionary GUI."""
        try:
            if self.dictionary_gui:
                self.logger.debug(
                    "Dictionary GUI bereits geöffnet, bringe in den Vordergrund"
                )
                self.dictionary_gui.bring_to_front()
                return True

            self.logger.info("📚 Öffne Dictionary GUI...")

            # Create GUI in separate thread
            self.gui_thread = threading.Thread(
                target=self._run_dictionary_gui, name="DictionaryGUI", daemon=True
            )
            self.gui_thread.start()

            # Wait a moment for GUI to initialize
            time.sleep(0.5)

            self.logger.info("✅ Dictionary GUI gestartet")
            return True

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Starten der Dictionary GUI: {e}")
            self.notification_manager.show_error(f"GUI-Fehler: {e}", "Dictionary GUI")
            return False

    def _run_unified_gui(self) -> None:
        """Run the unified GUI in a separate thread."""
        try:
            self.unified_gui = UnifiedManagerGUI(
                config=self.config, notification_manager=self.notification_manager
            )

            # Set window size
            self.unified_gui.set_window_size(
                self.config.gui_window_width, self.config.gui_window_height
            )

            # Run the GUI
            self.unified_gui.run()

        except Exception as e:
            self.logger.error(f"❌ Fehler in GUI-Thread: {e}")
            self.notification_manager.show_error(
                f"GUI-Fehler: {e}", "Unified Manager GUI"
            )

    def _run_modern_gui(self) -> None:
        """Run the modern GUI in a separate thread."""
        try:
            self.modern_gui = ModernManagerGUI(
                config=self.config, notification_manager=self.notification_manager
            )

            # Run the GUI
            self.modern_gui.run()

        except Exception as e:
            self.logger.error(f"❌ Fehler in Modern GUI-Thread: {e}")
            self.notification_manager.show_error(
                f"Modern GUI-Fehler: {e}", "Modern Manager GUI"
            )

    def _run_audio_database_gui(self) -> None:
        """Run the audio database GUI in a separate thread."""
        try:
            self.audio_database_gui = AudioDatabaseGUI(
                config=self.config, notification_manager=self.notification_manager
            )

            # Run the GUI
            self.audio_database_gui.run()

        except Exception as e:
            self.logger.error(f"❌ Fehler in Audio Database GUI-Thread: {e}")
            self.notification_manager.show_error(
                f"Audio Database GUI-Fehler: {e}", "Audio Database GUI"
            )

    def _run_dictionary_gui(self) -> None:
        """Run the dictionary GUI in a separate thread."""
        try:
            self.dictionary_gui = DictionaryGUI(
                config=self.config, notification_manager=self.notification_manager
            )

            # Run the GUI
            self.dictionary_gui.run()

        except Exception as e:
            self.logger.error(f"❌ Fehler in Dictionary GUI-Thread: {e}")
            self.notification_manager.show_error(
                f"Dictionary GUI-Fehler: {e}", "Dictionary GUI"
            )

    def hide_unified_gui(self) -> None:
        """Hide the unified manager GUI."""
        try:
            if self.unified_gui:
                self.logger.info("🖥️ Schließe Unified Manager GUI...")
                self.unified_gui.close()
                self.unified_gui = None
                self.logger.info("✅ Unified Manager GUI geschlossen")
            else:
                self.logger.debug("GUI ist bereits geschlossen")

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Schließen der GUI: {e}")

    def hide_modern_gui(self) -> None:
        """Hide the modern manager GUI."""
        try:
            if self.modern_gui:
                self.logger.info("🖥️ Schließe Modern Manager GUI...")
                self.modern_gui.close()
                self.modern_gui = None
                self.logger.info("✅ Modern Manager GUI geschlossen")
            else:
                self.logger.debug("Moderne GUI ist bereits geschlossen")

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Schließen der modernen GUI: {e}")

    def toggle_unified_gui(self) -> bool:
        """Toggle the unified manager GUI visibility."""
        if self.unified_gui and self.unified_gui.is_visible():
            self.hide_unified_gui()
            return False
        else:
            return self.show_unified_gui()

    def toggle_modern_gui(self) -> bool:
        """Toggle the modern manager GUI visibility."""
        if self.modern_gui and self.modern_gui.is_visible():
            self.hide_modern_gui()
            return False
        else:
            return self.show_modern_gui()

    def is_gui_visible(self) -> bool:
        """Check if any GUI is currently visible."""
        return (self.unified_gui is not None and self.unified_gui.is_visible()) or (
            self.modern_gui is not None and self.modern_gui.is_visible()
        )

    def get_gui_status(self) -> dict:
        """Get current GUI status information."""
        return {
            "is_running": self._is_running,
            "auto_start_enabled": self._should_auto_start,
            "unified_gui_active": self.unified_gui is not None,
            "unified_gui_visible": (
                self.unified_gui.is_visible() if self.unified_gui else False
            ),
            "modern_gui_active": self.modern_gui is not None,
            "modern_gui_visible": (
                self.modern_gui.is_visible() if self.modern_gui else False
            ),
            "gui_thread_alive": (
                self.gui_thread.is_alive() if self.gui_thread else False
            ),
            "window_size": f"{self.config.gui_window_width}x{self.config.gui_window_height}",
            "theme": self.config.gui_theme,
        }
