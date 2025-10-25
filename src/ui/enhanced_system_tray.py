# src/ui/system_tray.py - Enhanced SystemTray with Mode Switching
"""
Enhanced SystemTray with mode switching capabilities.
"""

import os
import threading
import tkinter as tk
from tkinter import messagebox
from typing import Any, Optional

from PIL import Image
from pystray import Icon, Menu, MenuItem


class EnhancedSystemTray:
    """Enhanced system tray with mode switching."""

    def __init__(self, app_instance: Any = None):
        self.app_instance = app_instance
        self.icon = None
        self.current_mode = "normal"
        self._create_icon()

    def _create_icon(self) -> None:
        """Create system tray icon."""
        # Create icon image (you can replace with your own icon)
        icon_path = "src/ui/icons/icon_idle.ico"
        if os.path.exists(icon_path):
            image = Image.open(icon_path)
        else:
            # Create a simple icon if file doesn't exist
            image = Image.new("RGB", (64, 64), color="blue")

        # Create menu with mode switching
        menu = Menu(
            MenuItem("🎛️ Mauscribe Control Center", self._open_control_center),
            MenuItem("📊 Current Status", self._show_status),
            Menu.SEPARATOR,
            MenuItem("📝 Switch to Normal Mode", self._switch_to_normal),
            MenuItem("🎯 Switch to Enhanced Mode", self._switch_to_enhanced),
            Menu.SEPARATOR,
            MenuItem("🔄 Refresh Status", self._refresh_status),
            Menu.SEPARATOR,
            MenuItem("❌ Exit", self._exit_app),
        )

        self.icon = Icon("Mauscribe", image, menu=menu)

    def _open_control_center(self, icon: Icon, item: MenuItem) -> None:
        """Open Control Center."""
        try:
            from ..config.app_config import AppConfig
            from .control_center import open_control_center

            config = AppConfig()
            open_control_center(config, self.app_instance)

        except Exception as e:
            print(f"Failed to open Control Center: {e}")

    def _show_status(self, icon: Icon, item: MenuItem) -> None:
        """Show current status."""
        try:
            if not self.app_instance:
                messagebox.showinfo("Status", "No app instance available")
                return

            # Get current mode
            mode = "normal"
            if hasattr(self.app_instance, "recording_config"):
                mode = self.app_instance.recording_config.mode.value

            # Get session info
            session_id = "None"
            if hasattr(self.app_instance, "enhanced_db"):
                session_id = self.app_instance.enhanced_db.current_session_id or "None"

            # Get recording stats
            stats = {}
            if hasattr(self.app_instance, "get_recording_stats"):
                stats = self.app_instance.get_recording_stats()

            status_text = f"""Mauscribe Status:

Mode: {mode.title()}
Session: {session_id}
Recordings: {stats.get('total_recordings', 0)}
Duration: {stats.get('total_duration', 0):.1f}s
Confidence: {stats.get('average_confidence', 0):.1%}

Recording: {'Yes' if stats.get('is_recording', False) else 'No'}
Transcribing: {'Yes' if stats.get('is_transcribing', False) else 'No'}"""

            messagebox.showinfo("Mauscribe Status", status_text)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to get status: {e}")

    def _switch_to_normal(self, icon: Icon, item: MenuItem) -> None:
        """Switch to normal mode."""
        try:
            if not self.app_instance:
                messagebox.showerror("Error", "No app instance available")
                return

            if hasattr(self.app_instance, "switch_recording_mode"):
                self.app_instance.switch_recording_mode("normal")
                self.current_mode = "normal"
                messagebox.showinfo(
                    "Mode Changed", "Switched to Normal Mode\n\nAudio files will be deleted after transcription."
                )
            else:
                messagebox.showerror("Error", "App doesn't support mode switching")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to switch mode: {e}")

    def _switch_to_enhanced(self, icon: Icon, item: MenuItem) -> None:
        """Switch to enhanced mode."""
        try:
            if not self.app_instance:
                messagebox.showerror("Error", "No app instance available")
                return

            if hasattr(self.app_instance, "switch_recording_mode"):
                self.app_instance.switch_recording_mode("enhanced")
                self.current_mode = "enhanced"
                messagebox.showinfo(
                    "Mode Changed", "Switched to Enhanced Mode\n\nAudio files will be saved permanently for training data."
                )
            else:
                messagebox.showerror("Error", "App doesn't support mode switching")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to switch mode: {e}")

    def _refresh_status(self, icon: Icon, item: MenuItem) -> None:
        """Refresh status."""
        self._show_status(icon, item)

    def _exit_app(self, icon: Icon, item: MenuItem) -> None:
        """Exit application."""
        try:
            if self.app_instance and hasattr(self.app_instance, "cleanup_on_exit"):
                self.app_instance.cleanup_on_exit()

            self.icon.stop()

        except Exception as e:
            print(f"Error during exit: {e}")
        finally:
            os._exit(0)

    def run(self) -> None:
        """Run the system tray icon."""
        if self.icon:
            self.icon.run()

    def stop(self) -> None:
        """Stop the system tray icon."""
        if self.icon:
            self.icon.stop()


# Example usage in main app
def create_enhanced_system_tray(app_instance: Any) -> EnhancedSystemTray:
    """Create enhanced system tray with mode switching."""
    return EnhancedSystemTray(app_instance)
