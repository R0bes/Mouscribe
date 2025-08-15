# src/windows_notifications.py - Windows notification system for Mauscribe
"""
Windows notification system using Windows 10/11 toast notifications.
Provides various notification types for different Mauscribe events.
"""

import os
import sys
import threading
import time
from datetime import datetime
from typing import Any, Dict, Optional

try:
    import win32api
    import win32con
    import win32gui
    import win32ui
    from win32api import GetSystemMetrics
    from win32con import SM_CXSCREEN, SM_CYSCREEN

    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False

try:
    from winotify import Notification, audio

    WINOTIFY_AVAILABLE = True
except ImportError:
    WINOTIFY_AVAILABLE = False

from ..utils.logger import get_logger


class WindowsNotificationManager:
    """Manages Windows notifications for Mauscribe application."""

    def __init__(self, config=None):
        """Initialize the Windows notification manager."""
        self.logger = get_logger(self.__class__.__name__)
        self.config = config
        self.is_available = WINDOWS_AVAILABLE and self._check_windows_version()

        if not self.is_available:
            self.logger.warning("Windows notifications are not available on this system")
            return

        self.logger.info("Windows notification manager initialized")

        # Notification settings from config or defaults
        if self.config:
            self.notification_duration = self.config.notifications_duration
            self.enable_sound = self.config.notifications_sound
            self.enable_toast = self.config.notifications_toast
        else:
            self.notification_duration = 5000  # 5 seconds
            self.enable_sound = True
            self.enable_toast = True

        # Active notifications tracking
        self.active_notifications = []
        self.notification_counter = 0

    def _check_windows_version(self) -> bool:
        """Check if Windows version supports modern notifications."""
        try:
            if not WINDOWS_AVAILABLE:
                return False

            # Check Windows version (Windows 10+ supports modern notifications)
            version = sys.getwindowsversion()
            major_version = version.major
            minor_version = version.minor

            # Windows 10 is version 10.0, Windows 11 is version 10.0 with higher build
            if major_version >= 10:
                self.logger.info(f"Windows {major_version}.{minor_version} detected - notifications supported")
                return True
            else:
                self.logger.warning(f"Windows {major_version}.{minor_version} detected - notifications not supported")
                return False

        except Exception as e:
            self.logger.error(f"Error checking Windows version: {e}")
            return False

    def _is_winotify_available(self) -> bool:
        """Check if winotify is available."""
        return WINOTIFY_AVAILABLE

    def show_recording_started(self, duration: Optional[int] = None) -> None:
        """Show notification when recording starts."""
        if not self.is_available:
            return

        # Check if recording notifications are enabled
        if self.config and not self.config.notifications_show_recording_events:
            return

        title = "🎙️ Aufnahme gestartet"
        message = "Aufnahme läuft... Drücken Sie erneut um zu stoppen."

        self._show_toast_notification(title, message, "info")
        self.logger.debug("Recording started notification shown")

    def show_recording_stopped(self, text_length: int = 0) -> None:
        """Show notification when recording stops."""
        if not self.is_available:
            return

        # Check if recording notifications are enabled
        if self.config and not self.config.notifications_show_recording_events:
            return

        title = "🛑 Aufnahme gestoppt"
        if text_length > 0:
            message = f"Aufnahme beendet. {text_length} Zeichen transkribiert."
        else:
            message = "Aufnahme beendet. Text wird verarbeitet..."

        self._show_toast_notification(title, message, "success")
        self.logger.debug("Recording stopped notification shown")

    def show_transcription_complete(self, text: str, duration: float) -> None:
        """Show notification when transcription is complete."""
        if not self.is_available:
            return

        # Check if transcription notifications are enabled
        if self.config and not self.config.notifications_show_transcription_events:
            return

        title = "✨ Transkription abgeschlossen"

        # Truncate text if too long
        if len(text) > 100:
            display_text = text[:97] + "..."
        else:
            display_text = text

        message = f"'{display_text}' ({duration:.1f}s)"

        self._show_toast_notification(title, message, "success")
        self.logger.debug("Transcription complete notification shown")

    def show_text_pasted(self, text: str) -> None:
        """Show notification when text is pasted."""
        if not self.is_available:
            return

        # Check if text event notifications are enabled
        if self.config and not self.config.notifications_show_text_events:
            return

        title = "📋 Text eingefügt"

        # Truncate text if too long
        if len(text) > 80:
            display_text = text[:77] + "..."
        else:
            display_text = text

        message = f"Text wurde eingefügt: '{display_text}'"

        self._show_toast_notification(title, message, "info")
        self.logger.debug("Text pasted notification shown")

    def show_error(self, error_message: str, context: str = "") -> None:
        """Show error notification."""
        if not self.is_available:
            return

        # Check if error notifications are enabled
        if self.config and not self.config.notifications_show_errors:
            return

        title = "❌ Fehler"
        if context:
            message = f"{context}: {error_message}"
        else:
            message = error_message

        self._show_toast_notification(title, message, "error")
        self.logger.debug("Error notification shown")

    def show_warning(self, warning_message: str, context: str = "") -> None:
        """Show warning notification."""
        if not self.is_available:
            return

        # Check if warning notifications are enabled
        if self.config and not self.config.notifications_show_warnings:
            return

        title = "⚠️ Warnung"
        if context:
            message = f"{context}: {warning_message}"
        else:
            message = warning_message

        self._show_toast_notification(title, message, "warning")
        self.logger.debug("Warning notification shown")

    def show_info(self, info_message: str, context: str = "") -> None:
        """Show info notification."""
        if not self.is_available:
            return

        # Check if info notifications are enabled
        if self.config and not self.config.notifications_show_startup:
            return

        title = "ℹ️ Information"
        if context:
            message = f"{context}: {info_message}"
        else:
            message = info_message

        self._show_toast_notification(title, message, "info")
        self.logger.debug("Info notification shown")

    def show_spell_check_complete(self, original_text: str, corrected_text: str) -> None:
        """Show notification when spell checking is complete."""
        if not self.is_available:
            return

        # Check if spell check notifications are enabled
        if self.config and not self.config.notifications_show_spell_check_events:
            return

        title = "🔍 Rechtschreibprüfung"

        if original_text == corrected_text:
            message = "Keine Korrekturen nötig - Text ist bereits korrekt"
        else:
            # Show first few characters of correction
            if len(original_text) > 50:
                orig_display = original_text[:47] + "..."
            else:
                orig_display = original_text

            if len(corrected_text) > 50:
                corr_display = corrected_text[:47] + "..."
            else:
                corr_display = corrected_text

            message = f"Korrektur: '{orig_display}' → '{corr_display}'"

        self._show_toast_notification(title, message, "info")
        self.logger.debug("Spell check complete notification shown")

    def _show_toast_notification(self, title: str, message: str, notification_type: str = "info") -> None:
        """Show a modern Windows toast notification."""
        try:
            # Create and show a modern toast notification
            self._create_toast_notification(title, message, notification_type)
        except Exception as e:
            self.logger.warning(f"Modern toast failed, falling back to simple notification: {e}")
            try:
                self._show_simple_notification(title, message, notification_type)
            except Exception as e2:
                self.logger.error(f"Both notification methods failed: {e2}")

    def _create_toast_notification(self, title: str, message: str, notification_type: str) -> None:
        """Create a modern toast notification widget."""
        try:
            # Use a simple, guaranteed working approach
            notification_id = self.notification_counter
            self.notification_counter += 1

            # Start notification in a separate thread to avoid blocking
            notification_thread = threading.Thread(
                target=self._show_working_toast, args=(notification_id, title, message, notification_type)
            )
            notification_thread.daemon = True
            notification_thread.start()

            # Track active notification
            self.active_notifications.append(notification_id)

        except Exception as e:
            self.logger.error(f"Error creating toast notification: {e}")
            raise

    def _show_working_toast(self, notification_id: int, title: str, message: str, notification_type: str) -> None:
        """Show a working toast notification."""
        try:
            # Use Windows taskbar notification - guaranteed to work
            self._show_taskbar_notification(title, message, notification_type)

            # Remove from active notifications after duration
            threading.Timer(self.notification_duration / 1000.0, lambda: self._remove_notification(notification_id)).start()

        except Exception as e:
            self.logger.error(f"Error showing working toast: {e}")

    def _show_taskbar_notification(self, title: str, message: str, notification_type: str):
        """Show a Windows taskbar notification."""
        try:
            # Try winotify first for real Windows 10/11 toast notifications
            if self._is_winotify_available():
                self._show_winotify_notification(title, message, notification_type)
            else:
                # Fallback to Windows MessageBox
                self._show_messagebox_notification(title, message, notification_type)

        except Exception as e:
            self.logger.error(f"Error showing taskbar notification: {e}")
            # Final fallback to MessageBox
            self._show_messagebox_notification(title, message, notification_type)

    def _show_winotify_notification(self, title: str, message: str, notification_type: str):
        """Show a notification using winotify for real Windows 10/11 toasts."""
        try:
            # Create notification with app_id for Mauscribe
            toast = Notification(app_id="Mauscribe", title=title, msg=message, icon=None)  # Use default icon

            # Set audio based on notification type
            if self.enable_sound:
                if notification_type == "error":
                    toast.set_audio(audio.Error, loop=False)
                elif notification_type == "warning":
                    toast.set_audio(audio.Warning, loop=False)
                elif notification_type == "success":
                    toast.set_audio(audio.Default, loop=False)
                else:
                    toast.set_audio(audio.Default, loop=False)

            # Show the toast notification
            toast.show()

            self.logger.debug(f"Winotify toast notification shown: {title}")

        except Exception as e:
            self.logger.error(f"Error showing winotify notification: {e}")
            raise

    def _show_modern_messagebox_notification(self, title: str, message: str, notification_type: str):
        """Show a modern-looking MessageBox notification."""
        try:
            # Use Windows MessageBox with modern styling and positioning
            flags = win32con.MB_OK | win32con.MB_ICONINFORMATION | win32con.MB_TOPMOST

            if notification_type == "error":
                flags = win32con.MB_OK | win32con.MB_ICONERROR | win32con.MB_TOPMOST
            elif notification_type == "warning":
                flags = win32con.MB_OK | win32con.MB_ICONWARNING | win32con.MB_TOPMOST
            elif notification_type == "success":
                flags = win32con.MB_OK | win32con.MB_ICONINFORMATION | win32con.MB_TOPMOST

            # Show notification in background thread to avoid blocking
            threading.Thread(target=lambda: win32api.MessageBox(0, message, title, flags), daemon=True).start()

            self.logger.debug(f"Modern MessageBox notification shown: {title}")

        except Exception as e:
            self.logger.error(f"Error showing modern MessageBox notification: {e}")
            raise

    def _show_messagebox_notification(self, title: str, message: str, notification_type: str):
        """Show a notification using Windows MessageBox."""
        try:
            # Use Windows MessageBox with modern styling
            flags = win32con.MB_OK | win32con.MB_ICONINFORMATION | win32con.MB_TOPMOST

            if notification_type == "error":
                flags = win32con.MB_OK | win32con.MB_ICONERROR | win32con.MB_TOPMOST
            elif notification_type == "warning":
                flags = win32con.MB_OK | win32con.MB_ICONWARNING | win32con.MB_TOPMOST
            elif notification_type == "success":
                flags = win32con.MB_OK | win32con.MB_ICONINFORMATION | win32con.MB_TOPMOST

            # Show notification in background thread
            threading.Thread(target=lambda: win32api.MessageBox(0, message, title, flags), daemon=True).start()

            self.logger.debug(f"MessageBox notification shown: {title}")

        except Exception as e:
            self.logger.error(f"Error showing MessageBox notification: {e}")
            raise

    def _show_simple_toast(self, notification_id: int, title: str, message: str, notification_type: str) -> None:
        """Legacy method - now redirects to working toast."""
        self._show_working_toast(notification_id, title, message, notification_type)

    def _create_minimal_notification(
        self, title: str, message: str, notification_type: str, x: int, y: int, width: int, height: int
    ):
        """Legacy method - now redirects to taskbar notification."""
        self._show_taskbar_notification(title, message, notification_type)

    def _show_fallback_notification(self, title: str, message: str, notification_type: str):
        """Show a fallback notification using Windows taskbar."""
        try:
            # Use Windows taskbar notification as fallback
            flags = win32con.MB_OK | win32con.MB_ICONINFORMATION | win32con.MB_TOPMOST | win32con.MB_SYSTEMMODAL

            if notification_type == "error":
                flags = win32con.MB_OK | win32con.MB_ICONERROR | win32con.MB_TOPMOST | win32con.MB_SYSTEMMODAL
            elif notification_type == "warning":
                flags = win32con.MB_OK | win32con.MB_ICONWARNING | win32con.MB_TOPMOST | win32con.MB_SYSTEMMODAL
            elif notification_type == "success":
                flags = win32con.MB_OK | win32con.MB_ICONINFORMATION | win32con.MB_TOPMOST | win32con.MB_SYSTEMMODAL

            # Show in background thread to avoid blocking
            threading.Thread(target=lambda: win32api.MessageBox(0, message, title, flags), daemon=True).start()

        except Exception as e:
            self.logger.error(f"Error showing fallback notification: {e}")

    def _get_notification_color(self, notification_type: str) -> int:
        """Get background color for notification type."""
        colors = {
            "info": 0x2196F3,  # Blue
            "success": 0x4CAF50,  # Green
            "warning": 0xFF9800,  # Orange
            "error": 0xF44336,  # Red
        }
        return colors.get(notification_type, 0x2196F3)

    def _hide_window(self, hwnd):
        """Hide a notification window."""
        try:
            if hwnd and win32gui.IsWindow(hwnd):
                win32gui.DestroyWindow(hwnd)
        except Exception as e:
            self.logger.error(f"Error hiding window: {e}")

    def _remove_notification(self, notification_id: int):
        """Remove notification from tracking."""
        try:
            if notification_id in self.active_notifications:
                self.active_notifications.remove(notification_id)
        except Exception as e:
            self.logger.error(f"Error removing notification: {e}")

    def _show_toast_widget(self, notification_id: int, title: str, message: str, notification_type: str) -> None:
        """Legacy method - now redirects to simple toast."""
        self._show_simple_toast(notification_id, title, message, notification_type)

    def _create_simple_notification_window(
        self, notification_id: int, title: str, message: str, notification_type: str, x: int, y: int, width: int, height: int
    ):
        """Legacy method - now redirects to minimal notification."""
        self._create_minimal_notification(title, message, notification_type, x, y, width, height)
        return None  # Return None since we don't need the handle

    def _simple_notification_proc(self, hwnd, msg, wparam, lparam):
        """Legacy method - no longer used."""
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    def _paint_simple_notification(self, hwnd):
        """Legacy method - no longer used."""
        pass

    def _hide_notification(self, notification_id: int, hwnd):
        """Hide notification by ID."""
        try:
            if hwnd and win32gui.IsWindow(hwnd):
                win32gui.DestroyWindow(hwnd)
        except Exception as e:
            self.logger.error(f"Error hiding notification: {e}")

    def _hide_notification_by_hwnd(self, hwnd):
        """Hide notification by window handle."""
        try:
            if hwnd and win32gui.IsWindow(hwnd):
                win32gui.DestroyWindow(hwnd)
        except Exception as e:
            self.logger.error(f"Error hiding notification by hwnd: {e}")

    def _show_simple_notification(self, title: str, message: str, notification_type: str) -> None:
        """Fallback to simple notification method."""
        try:
            # Use a simple taskbar notification as fallback
            flags = win32con.MB_OK | win32con.MB_ICONINFORMATION | win32con.MB_TOPMOST

            if notification_type == "error":
                flags = win32con.MB_OK | win32con.MB_ICONERROR | win32con.MB_TOPMOST
            elif notification_type == "warning":
                flags = win32con.MB_OK | win32con.MB_ICONWARNING | win32con.MB_TOPMOST
            elif notification_type == "success":
                flags = win32con.MB_OK | win32con.MB_ICONINFORMATION | win32con.MB_TOPMOST

            # Show in background thread to avoid blocking
            threading.Thread(target=lambda: win32api.MessageBox(0, message, title, flags), daemon=True).start()

        except Exception as e:
            self.logger.error(f"Error showing simple notification: {e}")

    def show_balloon_tip(self, title: str, message: str, icon_type: str = "info", duration: int = 5000) -> None:
        """Show a balloon tip notification in the system tray."""
        if not self.is_available:
            return

        try:
            # Use our modern toast system instead
            self._show_toast_notification(title, message, icon_type)
        except Exception as e:
            self.logger.error(f"Error showing balloon tip: {e}")

    def is_supported(self) -> bool:
        """Check if Windows notifications are supported on this system."""
        return self.is_available

    def get_system_info(self) -> dict[str, Any]:
        """Get system information for debugging."""
        if not self.is_available:
            return {"supported": False, "reason": "Windows notifications not available"}

        try:
            info = {
                "supported": True,
                "windows_version": f"{sys.getwindowsversion().major}.{sys.getwindowsversion().minor}",
                "screen_resolution": f"{GetSystemMetrics(SM_CXSCREEN)}x{GetSystemMetrics(SM_CYSCREEN)}",
                "notification_duration": self.notification_duration,
                "enable_sound": self.enable_sound,
                "enable_toast": self.enable_toast,
                "active_notifications": len(self.active_notifications),
            }
            return info
        except Exception as e:
            return {"supported": True, "error": str(e)}
