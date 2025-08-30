# src/ui/notifications.py - Simplified notification system for Mauscribe
"""
Simplified notification system using Windows 10/11 toast notifications.
Provides clean, maintainable notification types for different Mauscribe events.
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

    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False

try:
    from winotify import Notification, audio

    WINOTIFY_AVAILABLE = True
except ImportError:
    WINOTIFY_AVAILABLE = False

from ..utils.logger import get_logger


class NotificationManager:
    """Simplified notification manager for Mauscribe application."""

    def __init__(self, config=None):
        """Initialize the notification manager."""
        file_name = os.path.splitext(os.path.basename(__file__))[0]
        self.logger = get_logger(file_name.title())
        self.config = config
        self.is_available = WINDOWS_AVAILABLE and self._check_windows_version()

        if not self.is_available:
            self.logger.warning("Notifications are not available on this system")
            return

        self.logger.info("🔔 Notification Manager initialized")

        # Notification settings from config or defaults
        if self.config:
            self.notification_duration = getattr(self.config, "notifications_duration", 5000)
            self.enable_sound = getattr(self.config, "notifications_sound", True)
            self.enable_toast = getattr(self.config, "notifications_toast", True)
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

            # Check version (10+ supports modern notifications)
            version = sys.getwindowsversion()
            major_version = version.major

            # Windows 10 is version 10.0, Windows 11 is version 10.0 with higher build
            if major_version >= 10:
                self.logger.debug(f"Windows {major_version}.{version.minor} detected - notifications supported")
                return True
            else:
                self.logger.warning(f"Windows {major_version}.{version.minor} detected - notifications not supported")
                return False

        except Exception as e:
            self.logger.error(f"Error checking Windows version: {e}")
            return False

    def _is_winotify_available(self) -> bool:
        """Check if winotify is available and working."""
        if not WINOTIFY_AVAILABLE:
            return False

        # Test if winotify actually works
        try:
            test_toast = Notification(app_id="Mauscribe", title="Test", msg="Test Message", icon=None)
            self.logger.debug("Winotify test successful - library is working")
            return True
        except Exception as e:
            self.logger.warning(f"Winotify test failed: {e}")
            return False

    def show_recording_started(self, duration: Optional[int] = None) -> None:
        """Show notification when recording starts."""
        if not self._should_show_notification("recording_events"):
            return

        title = "🎙️ Recording Started"
        message = "Recording is running... Press again to stop."
        self._show_notification(title, message, "info")

    def show_recording_stopped(self, text_length: int = 0) -> None:
        """Show notification when recording stops."""
        if not self._should_show_notification("recording_events"):
            return

        title = "🛑 Recording Stopped"
        if text_length > 0:
            message = f"Recording ended. {text_length} characters transcribed."
        else:
            message = "Recording ended. Text is being processed..."

        self._show_notification(title, message, "success")

    def show_transcription_complete(self, text: str, duration: float) -> None:
        """Show notification when transcription is complete."""
        if not self._should_show_notification("transcription_events"):
            return

        title = "✨ Transcription Complete"

        # Truncate text if too long
        if len(text) > 100:
            display_text = text[:97] + "..."
        else:
            display_text = text

        message = f"'{display_text}' ({duration:.1f}s)"
        self._show_notification(title, message, "success")

    def show_text_pasted(self, text: str) -> None:
        """Show notification when text is pasted."""
        if not self._should_show_notification("text_events"):
            return

        title = "📋 Text Pasted"

        # Truncate text if too long
        if len(text) > 80:
            display_text = text[:77] + "..."
        else:
            display_text = text

        message = f"Text was pasted: '{display_text}'"
        self._show_notification(title, message, "info")

    def show_error(self, error_message: str, context: str = "") -> None:
        """Show error notification."""
        if not self._should_show_notification("errors"):
            return

        title = "❌ Error"
        if context:
            message = f"{context}: {error_message}"
        else:
            message = error_message

        self._show_notification(title, message, "error")

    def show_warning(self, warning_message: str, context: str = "") -> None:
        """Show warning notification."""
        if not self._should_show_notification("warnings"):
            return

        title = "⚠️ Warning"
        if context:
            message = f"{context}: {warning_message}"
        else:
            message = warning_message

        self._show_notification(title, message, "warning")

    def show_info(self, info_message: str, context: str = "") -> None:
        """Show info notification."""
        if not self._should_show_notification("startup"):
            return

        title = "ℹ️ Information"
        if context:
            message = f"{context}: {info_message}"
        else:
            message = info_message

        self._show_notification(title, message, "info")

    def show_spell_check_complete(self, original_text: str, corrected_text: str) -> None:
        """Show notification when spell checking is complete."""
        if not self._should_show_notification("spell_check_events"):
            return

        title = "🔍 Spell Check Complete"

        if original_text == corrected_text:
            message = "No corrections needed - text is already correct"
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

            message = f"Correction: '{orig_display}' → '{corr_display}'"

        self._show_notification(title, message, "info")

    def _should_show_notification(self, notification_type: str) -> bool:
        """Check if a specific notification type should be shown."""
        if not self.is_available:
            return False

        if not self.config:
            return True

        # Use simplified configuration - just check if all notifications are enabled
        return getattr(self.config, "notifications_show_all", True)

    def _show_notification(self, title: str, message: str, notification_type: str = "info") -> None:
        """Show a notification using the best available method."""
        try:
            # Try modern toast notification first
            if self.enable_toast and self._is_winotify_available():
                self._show_winotify_notification(title, message, notification_type)
            else:
                # Fallback to MessageBox
                self._show_messagebox_notification(title, message, notification_type)

        except Exception as e:
            self.logger.error(f"Error showing notification: {e}")
            # Final fallback to MessageBox
            try:
                self._show_messagebox_notification(title, message, notification_type)
            except Exception as e2:
                self.logger.error(f"All notification methods failed: {e2}")

    def _show_winotify_notification(self, title: str, message: str, notification_type: str) -> None:
        """Show a notification using winotify for real Windows 10/11 toasts."""
        try:
            # Validate and sanitize inputs
            title = str(title).strip() or "Mauscribe"
            message = str(message).strip() or "Notification"

            # Create notification
            toast = Notification(app_id="Mauscribe", title=title, msg=message, icon=None)

            # Set audio based on notification type
            if self.enable_sound:
                if notification_type == "error":
                    toast.set_audio(audio.Default, loop=False)  # Use Default for errors
                elif notification_type == "warning":
                    toast.set_audio(audio.Default, loop=False)  # Use Default for warnings
                elif notification_type == "success":
                    toast.set_audio(audio.Default, loop=False)
                else:
                    toast.set_audio(audio.Default, loop=False)

            # Show the toast notification
            toast.show()
            self.logger.debug(f"Winotify toast notification shown: '{title}'")

        except Exception as e:
            self.logger.error(f"Error showing winotify notification: {e}")
            raise

    def _show_messagebox_notification(self, title: str, message: str, notification_type: str) -> None:
        """Show a notification using Windows MessageBox as fallback."""
        try:
            # Set appropriate icon flags
            flags = win32con.MB_OK | win32con.MB_TOPMOST

            if notification_type == "error":
                flags |= win32con.MB_ICONERROR
            elif notification_type == "warning":
                flags |= win32con.MB_ICONWARNING
            else:
                flags |= win32con.MB_ICONINFORMATION

            # Show notification in background thread to avoid blocking
            threading.Thread(target=lambda: win32api.MessageBox(0, message, title, flags), daemon=True).start()

            self.logger.debug(f"MessageBox notification shown: {title}")

        except Exception as e:
            self.logger.error(f"Error showing MessageBox notification: {e}")
            raise

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
                "screen_resolution": "1920x1080",  # Simplified
                "notification_duration": self.notification_duration,
                "enable_sound": self.enable_sound,
                "enable_toast": self.enable_toast,
                "active_notifications": len(self.active_notifications),
            }
            return info
        except Exception as e:
            return {"supported": True, "error": str(e)}
