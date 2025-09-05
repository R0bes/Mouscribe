# src/system_tray.py - System Tray Management for Mauscribe
"""
System Tray Management Module
Handles system tray icon, menu, and related functionality
"""
import os
import subprocess
import threading
from pathlib import Path
from typing import Any, Optional

import pystray
from PIL import Image, ImageDraw

from ..utils.config import Config
from ..utils.logger import get_logger


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

        logger_name = (
            os.path.splitext(os.path.basename(__file__))[0]
            .replace("_", " ")
            .title()
            .replace(" ", "")
        )
        self.logger = get_logger(logger_name)

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

    def setup(self) -> None:
        """Initialize the system tray icon and menu."""
        try:
            icon_image = self.create_icon()

            def on_clicked(icon: Any, item: Any) -> None:
                """Handle system tray menu item clicks."""
                item_text = str(item)
                if item_text == "Status":
                    self._show_status_dialog()
                elif item_text == "Open Config":
                    self._open_config_file()
                elif item_text == "Datenbank & Wörterbuch":
                    self._open_unified_manager()
                elif item_text == "Exit":
                    self.app_instance.stop()
                elif item_text.startswith("✓ "):
                    # Handle Whisper model selection (with checkmark)
                    model = item_text.replace("✓ ", "")
                    self._change_whisper_model(model)
                elif item_text in ["tiny", "base", "small", "medium", "large"]:
                    # Handle Whisper model selection (without checkmark)
                    self._change_whisper_model(item_text)

            def create_whisper_submenu():
                """Create Whisper model submenu."""
                current_model = self.config.transcription_whisper_model
                available_models = self.config.get_available_whisper_models()

                menu_items = []
                for model in available_models:
                    # Add checkmark to current model
                    label = f"✓ {model}" if model == current_model else model
                    menu_items.append(pystray.MenuItem(label, on_clicked))

                return pystray.MenuItem("Whisper Model", pystray.Menu(*menu_items))

            # Create system tray menu
            menu = (
                pystray.MenuItem("Status", on_clicked),
                pystray.MenuItem("Open Config", on_clicked),
                pystray.MenuItem("Datenbank & Wörterbuch", on_clicked),
                create_whisper_submenu(),
                pystray.MenuItem("Exit", on_clicked),
            )

            self.system_tray = pystray.Icon(
                "mauscribe", icon_image, "Mauscribe - Voice-to-Text Tool", menu
            )
        except Exception as e:
            # Silently ignore system tray errors
            self.system_tray = None

    def _show_status_dialog(self) -> None:
        """Show status dialog instead of logging to console."""
        try:
            import tkinter as tk
            from tkinter import messagebox

            status = "Recording" if self.is_recording else "Idle"

            status_text = f"""Mauscribe Status: {status}

Input Methode: mouse_button
Maus-Taste: {self.config.primary_name}
Audio-Gerät: {self.config.audio_device}

Die Anwendung läuft im Hintergrund.
Verwenden Sie das System Tray für weitere Aktionen."""

            # Create a simple dialog
            dialog = tk.Toplevel()
            dialog.title("Mauscribe Status")
            dialog.geometry("400x300")
            dialog.resizable(False, False)

            # Center dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
            y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
            dialog.geometry(f"+{x}+{y}")

            # Add status text
            text_widget = tk.Text(dialog, wrap=tk.WORD, padx=20, pady=20)
            text_widget.pack(fill=tk.BOTH, expand=True)
            text_widget.insert(tk.END, status_text)
            text_widget.config(state=tk.DISABLED)

            # Add close button
            close_button = tk.Button(dialog, text="Schließen", command=dialog.destroy)
            close_button.pack(pady=10)

            # Make dialog modal
            dialog.transient()
            dialog.grab_set()
            dialog.focus_set()

        except Exception as e:
            # Silently ignore status dialog errors
            pass

    def _log_status(self) -> None:
        """Log current application status to console (fallback)."""
        # Silently ignore status logging
        pass

    def _open_unified_manager(self) -> None:
        """Open the unified database and dictionary manager GUI."""
        try:
            from .unified_manager_gui import UnifiedManagerGUI

            # Open unified manager in a separate thread to avoid blocking
            def open_gui():
                try:
                    gui = UnifiedManagerGUI()
                    gui.run()
                except Exception as e:
                    # Silently ignore GUI errors
                    pass

            thread = threading.Thread(target=open_gui, daemon=True)
            thread.start()
        except Exception as e:
            # Silently ignore unified manager errors
            pass

    def _open_database_manager(self) -> None:
        """Open the database manager GUI (legacy)."""
        try:
            from .database_gui import DatabaseManagerGUI

            # Open database manager in a separate thread to avoid blocking
            def open_gui():
                try:
                    gui = DatabaseManagerGUI()
                    gui.run()
                except Exception as e:
                    # Silently ignore GUI errors
                    pass

            thread = threading.Thread(target=open_gui, daemon=True)
            thread.start()
        except Exception as e:
            # Silently ignore database manager errors
            pass

    def _open_config_file(self) -> None:
        """Open the configuration file in default editor."""
        config_path = Path(self.config.config_path)
        if config_path.exists():
            try:
                subprocess.run(["notepad", str(config_path)], shell=True)
            except Exception as e:
                # Silently ignore config file open errors
                pass

    def _change_whisper_model(self, model: str) -> None:
        """Change Whisper model and reload STT.

        Args:
            model: Whisper model to switch to
        """
        try:
            # Update configuration
            self.config.set_whisper_model(model)

            # Reload STT model in the main application
            if hasattr(self.app_instance, "reload_stt_model"):
                self.app_instance.reload_stt_model()

            # Show notification
            self._show_model_change_notification(model)

            # Update system tray menu to reflect the change
            self._update_system_tray_menu()

        except Exception as e:
            self.logger.error(f"Error changing Whisper model: {e}")

    def _update_system_tray_menu(self) -> None:
        """Update system tray menu to reflect current configuration."""
        if self.system_tray is None:
            return

        try:
            # Recreate the menu with updated Whisper model selection
            def on_clicked(icon: Any, item: Any) -> None:
                """Handle system tray menu item clicks."""
                item_text = str(item)
                if item_text == "Status":
                    self._show_status_dialog()
                elif item_text == "Open Config":
                    self._open_config_file()
                elif item_text == "Datenbank & Wörterbuch":
                    self._open_unified_manager()
                elif item_text == "Exit":
                    self.app_instance.stop()
                elif item_text.startswith("✓ "):
                    # Handle Whisper model selection (with checkmark)
                    model = item_text.replace("✓ ", "")
                    self._change_whisper_model(model)
                elif item_text in ["tiny", "base", "small", "medium", "large"]:
                    # Handle Whisper model selection (without checkmark)
                    self._change_whisper_model(item_text)

            def create_whisper_submenu():
                """Create Whisper model submenu."""
                current_model = self.config.transcription_whisper_model
                available_models = self.config.get_available_whisper_models()

                menu_items = []
                for model in available_models:
                    # Add checkmark to current model
                    label = f"✓ {model}" if model == current_model else model
                    menu_items.append(pystray.MenuItem(label, on_clicked))

                return pystray.MenuItem("Whisper Model", pystray.Menu(*menu_items))

            # Create updated system tray menu
            menu = (
                pystray.MenuItem("Status", on_clicked),
                pystray.MenuItem("Open Config", on_clicked),
                pystray.MenuItem("Datenbank & Wörterbuch", on_clicked),
                create_whisper_submenu(),
                pystray.MenuItem("Exit", on_clicked),
            )

            # Update the system tray menu
            self.system_tray.menu = menu

        except Exception as e:
            self.logger.error(f"Error updating system tray menu: {e}")

    def _show_model_change_notification(self, model: str) -> None:
        """Show notification about Whisper model change.

        Args:
            model: New Whisper model name
        """
        try:
            import tkinter as tk
            from tkinter import messagebox

            # Create a simple notification dialog
            dialog = tk.Toplevel()
            dialog.title("Whisper Model Changed")
            dialog.geometry("300x150")
            dialog.resizable(False, False)

            # Center dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
            y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
            dialog.geometry(f"+{x}+{y}")

            # Add message
            message = tk.Label(
                dialog,
                text=f"Whisper Model geändert zu:\n{model.upper()}",
                font=("Arial", 12),
                pady=20,
            )
            message.pack()

            # Add close button
            close_button = tk.Button(dialog, text="OK", command=dialog.destroy)
            close_button.pack(pady=10)

            # Auto-close after 3 seconds
            dialog.after(3000, dialog.destroy)

            # Make dialog modal
            dialog.transient()
            dialog.grab_set()
            dialog.focus_set()

        except Exception as e:
            # Silently ignore notification errors
            pass

    def update_recording_state(self, is_recording: bool) -> None:
        """Update the recording state and refresh the icon.

        Args:
            is_recording: Whether recording is currently active
        """
        self.is_recording = is_recording
        if self.system_tray:
            try:
                self.system_tray.icon = self.create_icon()
            except Exception as e:
                # Silently ignore icon update errors
                pass

    def run(self) -> None:
        """Run the system tray in a separate thread."""
        if self.system_tray is None:
            return

        try:
            self.system_tray.run()
        except Exception as e:
            # Silently ignore system tray run errors
            pass

    def stop(self) -> None:
        """Stop the system tray."""
        if self.system_tray:
            try:
                self.system_tray.stop()
            except Exception as e:
                # Silently ignore system tray stop errors
                pass

    def is_available(self) -> bool:
        """Check if system tray is available.

        Returns:
            True if system tray is available, False otherwise
        """
        return self.system_tray is not None
