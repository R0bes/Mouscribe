# src/ui/notifications.py - Improved notification system for Mauscribe
"""
Clean notification system with proper abstractions and platform detection.
"""
import os
import sys
import threading
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Optional, Protocol
from dataclasses import dataclass
import platform
from ..utils.logger import get_logger

class NotificationType(Enum):
    """Notification types with corresponding icons and sounds."""
    INFO = ("ℹ️", "info")
    SUCCESS = ("✅", "success") 
    WARNING = ("⚠️", "warning")
    ERROR = ("❌", "error")
    RECORDING = ("🎙️", "info")
    TRANSCRIPTION = ("✨", "success")
    PASTE = ("📋", "info")
    SPELL_CHECK = ("🔍", "info")


@dataclass
class NotificationData:
    """Notification data container."""
    title: str
    message: str
    notification_type: NotificationType = NotificationType.INFO
    duration: int = 5000
    sound: bool = True
    clickable: bool = False
    callback: Optional[callable] = None


class NotificationBackend(Protocol):
    """Protocol for notification backends."""
    
    def is_available(self) -> bool:
        """Check if backend is available."""
        ...
    
    def show(self, notification: NotificationData) -> bool:
        """Show notification. Returns True if successful."""
        ...


class WindowsToastBackend:
    """Windows 10/11 toast notifications using win10toast-click."""
    
    def __init__(self):
        self._available = self._check_availability()
        if self._available:
            from win10toast_click import ToastNotifier
            self._toaster = ToastNotifier()
    
    def is_available(self) -> bool:
        return self._available
    
    def _check_availability(self) -> bool:
        """Check if Windows toast notifications are available."""
        if not sys.platform == "win32":
            return False
            
        try:
            # Check Windows version (10+)
            version = sys.getwindowsversion()
            if version.major < 10:
                return False
                
            # Try importing the library
            import win10toast_click
            return True
        except ImportError:
            return False
    
    def show(self, notification: NotificationData) -> bool:
        """Show Windows toast notification."""
        if not self._available:
            return False
            
        try:
            icon_emoji, _ = notification.notification_type.value
            title = f"{icon_emoji} {notification.title}"
            
            if notification.clickable and notification.callback:
                self._toaster.show_toast(
                    title=title,
                    msg=notification.message,
                    duration=notification.duration // 1000,
                    callback_on_click=notification.callback,
                    threaded=True
                )
            else:
                self._toaster.show_toast(
                    title=title,
                    msg=notification.message, 
                    duration=notification.duration // 1000,
                    threaded=True
                )
            return True
        except Exception:
            return False


class WindowsMessageBoxBackend:
    """Fallback Windows MessageBox notifications."""
    
    def __init__(self):
        self._available = self._check_availability()
    
    def is_available(self) -> bool:
        return self._available
    
    def _check_availability(self) -> bool:
        if not sys.platform == "win32":
            return False
        try:
            import win32api
            import win32con
            return True
        except ImportError:
            return False
    
    def show(self, notification: NotificationData) -> bool:
        """Show MessageBox notification."""
        if not self._available:
            return False
            
        try:
            import win32api
            import win32con
            
            # Map notification types to MessageBox flags
            type_flags = {
                NotificationType.ERROR: win32con.MB_ICONERROR,
                NotificationType.WARNING: win32con.MB_ICONWARNING,
                NotificationType.SUCCESS: win32con.MB_ICONINFORMATION,
                NotificationType.INFO: win32con.MB_ICONINFORMATION,
            }
            
            icon_emoji, _ = notification.notification_type.value
            title = f"{icon_emoji} {notification.title}"
            
            flags = (win32con.MB_OK | win32con.MB_TOPMOST | 
                    type_flags.get(notification.notification_type, win32con.MB_ICONINFORMATION))
            
            # Non-blocking call
            threading.Thread(
                target=lambda: win32api.MessageBox(0, notification.message, title, flags),
                daemon=True
            ).start()
            
            return True
        except Exception:
            return False


class ConsoleBackend:
    """Fallback console notifications for development."""
    
    def is_available(self) -> bool:
        return True
    
    def show(self, notification: NotificationData) -> bool:
        """Show console notification."""
        icon_emoji, _ = notification.notification_type.value
        print(f"{icon_emoji} {notification.title}: {notification.message}")
        return True


class Toaster:
    """Main notification manager with backend selection."""
    
    def __init__(self, enable_sound: bool = True, default_duration: int = 5000, enabled: bool = True, notification_settings: dict = None):
        self.enable_sound = enable_sound
        self.default_duration = default_duration
        self.enabled = enabled
        self.notification_settings = notification_settings or {}
        
        # Initialize backends in priority order
        self._backends = [
            WindowsToastBackend(),
            WindowsMessageBoxBackend(), 
            ConsoleBackend()  # Always available fallback
        ]
        
        # Select first available backend
        self._active_backend = next(
            (backend for backend in self._backends if backend.is_available()),
            ConsoleBackend()
        )
    
    def show(self, title: str, message: str, 
             notification_type: NotificationType = NotificationType.INFO,
             duration: Optional[int] = None,
             clickable: bool = False,
             callback: Optional[callable] = None,
             force_show: bool = False) -> bool:
        """Show notification with specified parameters."""
        
        # Check if notifications are globally disabled (unless forced)
        if not self.enabled and not force_show:
            return False
        
        # Check if this specific notification type is disabled (unless forced)
        if not force_show and not self._is_notification_type_enabled(notification_type):
            return False
        
        notification = NotificationData(
            title=title,
            message=message,
            notification_type=notification_type,
            duration=duration or self.default_duration,
            sound=self.enable_sound,
            clickable=clickable,
            callback=callback
        )
        
        return self._active_backend.show(notification)
    
    def _is_notification_type_enabled(self, notification_type: NotificationType) -> bool:
        """Check if a specific notification type is enabled."""
        # Mapping from NotificationType to setting key
        type_to_setting = {
            NotificationType.INFO: "show_info",
            NotificationType.SUCCESS: "show_success", 
            NotificationType.WARNING: "show_warning",
            NotificationType.ERROR: "show_error",
            NotificationType.RECORDING: "show_recording",
            NotificationType.TRANSCRIPTION: "show_transcription",
            NotificationType.PASTE: "show_paste",
            NotificationType.SPELL_CHECK: "show_spell_check"
        }
        
        setting_key = type_to_setting.get(notification_type, "show_info")
        return self.notification_settings.get(setting_key, True)  # Default to True if not specified
    
    # Convenience methods for different notification types
    def show_info(self, title: str, message: str, **kwargs) -> bool:
        return self.show(title, message, NotificationType.INFO, **kwargs)
    
    def show_success(self, title: str, message: str, **kwargs) -> bool:
        return self.show(title, message, NotificationType.SUCCESS, **kwargs)
    
    def show_warning(self, title: str, message: str, **kwargs) -> bool:
        return self.show(title, message, NotificationType.WARNING, **kwargs)
    
    def show_error(self, title: str, message: str, **kwargs) -> bool:
        return self.show(title, message, NotificationType.ERROR, **kwargs)
    
    # Application-specific methods
    def recording_started(self, **kwargs) -> bool:
        return self.show(
            "Recording Started", 
            "Recording is running... Press again to stop.",
            NotificationType.RECORDING,
            **kwargs
        )
    
    def recording_stopped(self, text_length: int = 0, **kwargs) -> bool:
        message = (f"Recording ended. {text_length} characters transcribed." 
                  if text_length > 0 else "Recording ended. Processing...")
        return self.show("Recording Stopped", message, NotificationType.SUCCESS, **kwargs)
    
    def transcription_complete(self, text: str, duration: float, **kwargs) -> bool:
        display_text = text[:97] + "..." if len(text) > 100 else text
        message = f"'{display_text}' ({duration:.1f}s)"
        return self.show("Transcription Complete", message, NotificationType.TRANSCRIPTION, **kwargs)
    
    def text_pasted(self, text: str, **kwargs) -> bool:
        display_text = text[:77] + "..." if len(text) > 80 else text
        message = f"Text pasted: '{display_text}'"
        return self.show("Text Pasted", message, NotificationType.PASTE, **kwargs)
    
    def spell_check_complete(self, original: str, corrected: str, **kwargs) -> bool:
        if original == corrected:
            message = "No corrections needed"
        else:
            orig_short = original[:47] + "..." if len(original) > 50 else original
            corr_short = corrected[:47] + "..." if len(corrected) > 50 else corrected
            message = f"'{orig_short}' → '{corr_short}'"
        
        return self.show("Spell Check Complete", message, NotificationType.SPELL_CHECK, **kwargs)
    
    @property
    def backend_name(self) -> str:
        """Get name of active backend."""
        return self._active_backend.__class__.__name__
    
    def get_system_info(self) -> dict[str, Any]:
        """Get system info for debugging."""
        return {
            "active_backend": self.backend_name,
            "available_backends": [
                backend.__class__.__name__ 
                for backend in self._backends 
                if backend.is_available()
            ],
            "platform": sys.platform,
            "windows_version": (f"{sys.getwindowsversion().major}.{sys.getwindowsversion().minor}" 
                              if sys.platform == "win32" else "N/A")
        }


# Convenience factory function
def create_notification_manager(**kwargs) -> Toaster:
    """Create notification manager with platform detection."""
    return Toaster(**kwargs)


# Example usage
if __name__ == "__main__":
    notifier = create_notification_manager()
    
    # Test different notification types
    notifier.info("Test", "This is an info notification")
    notifier.success("Success", "Operation completed successfully")
    notifier.warning("Warning", "This is a warning")
    notifier.error("Error", "Something went wrong")
    
    # Test clickable notification
    def on_click():
        print("Notification clicked!")
    
    notifier.info("Clickable", "Click me!", clickable=True, callback=on_click)
    
    # Print system info
    print(f"System info: {notifier.get_system_info()}")