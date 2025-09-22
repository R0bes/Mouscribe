# src/ui/notifications.py - Improved notification system for Mauscribe
"""
Clean notification system with proper abstractions and platform detection.
"""
import os
import platform
import sys
import threading
import types
import winsound
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, Protocol

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
    duration: int = 500  # 0.5 seconds
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
    """Windows 10/11 toast notifications using win10toast_click."""

    def __init__(self):
        self._available = self._check_availability()
        if self._available:
            try:
                from win10toast_click import ToastNotifier

                self._toaster = ToastNotifier()
                # Fix für Shell Notify Icon Löschfehler
                self._patch_shell_notify_icon_bug()
            except ImportError:
                self._available = False

    def _patch_shell_notify_icon_bug(self):
        """Fix für Shell Notify Icon Löschfehler in win10toast_click."""
        try:
            # Speichere die ursprüngliche on_destroy Methode
            original_on_destroy = self._toaster.on_destroy

            def fixed_on_destroy(hwnd, msg, wparam, lparam):
                """Fixed on_destroy Methode die Shell Notify Icon Fehler vermeidet."""
                try:
                    # Versuche das Icon mit korrekten Flags zu löschen
                    # Das nid muss die gleichen Flags haben wie beim Erstellen
                    nid = (self._toaster.hwnd, 0, 0x07, 0x4014, None, "Tooltip")  # NIF_ICON | NIF_MESSAGE | NIF_TIP
                    from win32gui import NIM_DELETE, Shell_NotifyIcon

                    Shell_NotifyIcon(NIM_DELETE, nid)
                except Exception:
                    # Falls das fehlschlägt, versuche es ohne Flags
                    try:
                        nid = (self._toaster.hwnd, 0)
                        from win32gui import NIM_DELETE, Shell_NotifyIcon

                        Shell_NotifyIcon(NIM_DELETE, nid)
                    except Exception:
                        # Falls auch das fehlschlägt, ignoriere den Fehler
                        pass

                # Rufe die ursprüngliche Methode auf (ohne Shell_NotifyIcon)
                try:
                    from win32api import PostQuitMessage

                    PostQuitMessage(0)
                except Exception:
                    pass

            # Überschreibe die on_destroy Methode
            self._toaster.on_destroy = fixed_on_destroy

            # Fix auch für wnd_proc Methode
            original_wnd_proc = self._toaster.wnd_proc

            def fixed_wnd_proc(hwnd, msg, wparam, lparam, **kwargs):
                """Fixed wnd_proc Methode die WNDPROC Fehler vermeidet."""
                try:
                    # Rufe die ursprüngliche Methode auf, aber fange Fehler ab
                    result = original_wnd_proc(hwnd, msg, wparam, lparam, **kwargs)
                    return result if result is not None else 0
                except Exception:
                    # Bei Fehlern einfach 0 zurückgeben
                    return 0

            self._toaster.wnd_proc = fixed_wnd_proc

            # Fix für Fenster-Titel - überschreibe die _show_toast Methode
            original_show_toast = self._toaster._show_toast

            def fixed_show_toast(title, msg, icon_path, duration, callback_on_click):
                """Fixed _show_toast Methode mit Mauscribe Fenster-Titel."""
                try:
                    # Rufe die ursprüngliche Methode auf, aber ändere den Fenster-Titel
                    # Wir müssen die ursprüngliche Methode kopieren und nur den Titel ändern

                    # Importiere alle benötigten Module
                    import time
                    from os import path
                    from time import sleep

                    from pkg_resources import Requirement, resource_filename
                    from win32api import GetModuleHandle, PostQuitMessage
                    from win32con import (
                        CW_USEDEFAULT,
                        IDI_APPLICATION,
                        IMAGE_ICON,
                        LR_DEFAULTSIZE,
                        LR_LOADFROMFILE,
                        WM_DESTROY,
                        WM_USER,
                        WS_OVERLAPPED,
                        WS_SYSMENU,
                    )
                    from win32gui import (
                        NIF_ICON,
                        NIF_INFO,
                        NIF_MESSAGE,
                        NIF_TIP,
                        NIM_ADD,
                        NIM_MODIFY,
                        WNDCLASS,
                        CreateWindow,
                        DestroyWindow,
                        LoadIcon,
                        LoadImage,
                        PumpMessages,
                        RegisterClass,
                        Shell_NotifyIcon,
                        UnregisterClass,
                        UpdateWindow,
                    )

                    message_map = {WM_DESTROY: self._toaster.on_destroy}

                    # Register the window class.
                    wc = WNDCLASS()
                    hinst = wc.hInstance = GetModuleHandle(None)
                    wc.lpszClassName = str("MauscribeTaskbar" + str(time.time()).replace(".", ""))
                    wc.lpfnWndProc = self._toaster.wnd_proc

                    try:
                        classAtom = RegisterClass(wc)
                    except Exception as e:
                        pass

                    style = WS_OVERLAPPED | WS_SYSMENU
                    # HIER ist der wichtige Teil - "Mauscribe" statt "Taskbar"
                    hwnd = CreateWindow(classAtom, "Mauscribe", style, 0, 0, CW_USEDEFAULT, CW_USEDEFAULT, 0, 0, hinst, None)
                    UpdateWindow(hwnd)

                    # Ändere den Fenster-Titel nach der Erstellung
                    try:
                        from win32gui import SetWindowText

                        SetWindowText(hwnd, "Mauscribe")
                    except Exception:
                        pass

                    # Speichere hwnd für on_destroy
                    self._toaster.hwnd = hwnd
                    self._toaster.classAtom = classAtom
                    self._toaster.wc = wc

                    # icon
                    if icon_path is not None:
                        icon_path = path.realpath(icon_path)
                    else:
                        icon_path = resource_filename(
                            Requirement.parse("win10toast_click"), "win10toast_click/icon/notification.ico"
                        )
                    icon_flags = LR_LOADFROMFILE | LR_DEFAULTSIZE
                    try:
                        hicon = LoadImage(hinst, icon_path, IMAGE_ICON, 0, 0, icon_flags)
                    except Exception:
                        hicon = LoadIcon(0, IDI_APPLICATION)

                    # Taskbar icon
                    flags = NIF_ICON | NIF_MESSAGE | NIF_TIP
                    nid = (hwnd, 0, flags, WM_USER + 20, hicon, "Mauscribe Tooltip")
                    Shell_NotifyIcon(NIM_ADD, nid)
                    Shell_NotifyIcon(
                        NIM_MODIFY, (hwnd, 0, NIF_INFO, WM_USER + 20, hicon, "Mauscribe Balloon Tooltip", msg, 200, title)
                    )
                    PumpMessages()

                    # take a rest then destroy
                    if duration is not None:
                        sleep(duration)
                        DestroyWindow(hwnd)
                        UnregisterClass(wc.lpszClassName, None)
                    return None

                except Exception as e:
                    # Fallback zur ursprünglichen Methode
                    return original_show_toast(title, msg, icon_path, duration, callback_on_click)

            self._toaster._show_toast = fixed_show_toast

        except Exception:
            # Falls Patching fehlschlägt, ignorieren wir es
            pass

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
        """Show Windows toast notification with click functionality."""
        if not self._available:
            return False

        try:
            icon_emoji, _ = notification.notification_type.value
            title = f"{icon_emoji} {notification.title}"

            # Toast-Benachrichtigung mit Klick-Callback und gefixtem Shell Notify Icon
            self._toaster.show_toast(
                title=title,
                msg=notification.message,
                duration=notification.duration // 1000,
                threaded=True,
                icon_path=None,  # Verhindert zusätzliche Shell Notify Icon Probleme
                callback_on_click=notification.callback if notification.clickable else None,
            )
            return True
        except Exception as e:
            print(f"Toast notification error: {e}")
            return False


class Toaster:
    """Main notification manager with Windows Toast backend only."""

    def __init__(
        self, enable_sound: bool = True, default_duration: int = 500, enabled: bool = True, notification_settings: dict = None
    ):
        self.enable_sound = enable_sound
        self.default_duration = default_duration
        self.enabled = enabled
        self.notification_settings = notification_settings or {}
        self.logger = get_logger(__name__)

        # Only use Windows Toast backend
        self._active_backend = WindowsToastBackend()

    def show(
        self,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        duration: Optional[int] = None,
        clickable: bool = False,
        callback: Optional[callable] = None,
        force_show: bool = False,
    ) -> bool:
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
            callback=callback,
        )

        # Sound wird von der Toast-Bibliothek selbst abgespielt, daher hier deaktiviert
        # if notification.sound and self.enable_sound:
        #     self._play_notification_sound(notification.notification_type)

        return self._active_backend.show(notification)

    def _play_notification_sound(self, notification_type: NotificationType) -> None:
        """Play appropriate sound for notification type."""
        try:
            if sys.platform == "win32":
                # Map notification types to Windows system sounds
                sound_map = {
                    NotificationType.INFO: winsound.MB_ICONASTERISK,
                    NotificationType.SUCCESS: winsound.MB_ICONASTERISK,
                    NotificationType.WARNING: winsound.MB_ICONEXCLAMATION,
                    NotificationType.ERROR: winsound.MB_ICONHAND,
                    NotificationType.RECORDING: winsound.MB_ICONASTERISK,
                    NotificationType.TRANSCRIPTION: winsound.MB_ICONASTERISK,
                    NotificationType.PASTE: winsound.MB_ICONASTERISK,
                    NotificationType.SPELL_CHECK: winsound.MB_ICONASTERISK,
                }

                sound = sound_map.get(notification_type, winsound.MB_ICONASTERISK)
                winsound.MessageBeep(sound)
                self.logger.debug(f"🔊 Sound abgespielt für {notification_type.name}")

        except Exception as e:
            self.logger.warning(f"⚠️ Fehler beim Abspielen des Sounds: {e}")

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
            NotificationType.SPELL_CHECK: "show_spell_check",
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
            "Recording Started", "Recording is running... Press again to stop.", NotificationType.RECORDING, **kwargs
        )

    def recording_stopped(self, text_length: int = 0, **kwargs) -> bool:
        message = (
            f"Recording ended. {text_length} characters transcribed." if text_length > 0 else "Recording ended. Processing..."
        )
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
            "available_backends": [self._active_backend.__class__.__name__] if self._active_backend.is_available() else [],
            "platform": sys.platform,
            "windows_version": (
                f"{sys.getwindowsversion().major}.{sys.getwindowsversion().minor}" if sys.platform == "win32" else "N/A"
            ),
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
