# src/ui/notifications.py - Windows toast notification system for Mauscribe
"""
Clickable Windows toast notification system using win10toast-click.
Uses a silent worker process pattern to avoid console noise and ensure reliable notifications.
"""

import os
import shlex
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from win10toast_click import ToastNotifier  # type: ignore

    WIN10TOAST_CLICK_AVAILABLE = True
except ImportError:
    WIN10TOAST_CLICK_AVAILABLE = False

    # Fallback für den Fall, dass win10toast-click nicht verfügbar ist
    class ToastNotifier:
        def __init__(self):
            pass

        def show_toast(
            self,
            title,
            msg,
            duration=3,
            icon_path=None,
            threaded=False,
            callback_on_click=None,
        ):
            print(f"Notification: {title} - {msg}")
            return True


try:
    from ..utils.logger import get_logger
except ImportError:
    # Fallback for standalone execution
    import logging

    def get_logger(name):
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger


class NotificationManager:
    """Advanced notification manager for Mauscribe application using win10toast-click."""

    def __init__(self, config=None, app_instance=None):
        """Initialize the notification manager."""
        file_name = os.path.splitext(os.path.basename(__file__))[0]
        self.logger = get_logger(file_name.title())
        self.config = config
        self.app_instance = app_instance

        self.logger.info("🔧 NotificationManager wird initialisiert...")

        # Get notification settings from config with proper validation
        self._load_configuration()

        # Active notifications tracking
        self.active_notifications = []
        self.notification_counter = 0
        self.current_notification_process = None  # Für frühere Beendigung

        self.logger.info("✅ NotificationManager erfolgreich initialisiert")

    def _load_configuration(self):
        """Load and validate notification configuration."""
        try:
            if self.config:
                # Get configuration values with proper fallbacks
                self.notification_duration = self._get_config_value(
                    "notifications_duration", 5
                )
                self.enable_sound = self._get_config_value("notifications_sound", True)
                self.enable_toast = self._get_config_value("notifications_toast", True)
                self.show_all_notifications = self._get_config_value(
                    "notifications_show_all", True
                )
            else:
                # Default values if no config provided
                self.notification_duration = 5
                self.enable_sound = True
                self.enable_toast = True
                self.show_all_notifications = True

            # Log notification configuration
            self.logger.info(f"📋 Notification-Konfiguration geladen:")
            self.logger.info(f"   • Duration: {self.notification_duration}ms")
            self.logger.info(f"   • Sound: {self.enable_sound}")
            self.logger.info(f"   • Toast: {self.enable_toast}")
            self.logger.info(f"   • Show All: {self.show_all_notifications}")

        except Exception as e:
            # Fallback to safe defaults
            self.logger.warning(
                f"⚠️ Notification-Konfiguration Fehler: {e}, verwende Standardwerte"
            )
            self.notification_duration = 5
            self.enable_sound = True
            self.enable_toast = True
            self.show_all_notifications = True

    def _get_config_value(self, key: str, default: Any) -> Any:
        """Safely get configuration value with type validation."""
        try:
            if not self.config:
                self.logger.debug(
                    f"🔍 Config-Wert '{key}': Keine Config verfügbar, verwende Default {default}"
                )
                return default

            value = getattr(self.config, key, default)
            self.logger.debug(f"🔍 Config-Wert '{key}': {value} (Default: {default})")

            # Type validation based on key
            if key == "notifications_duration":
                if isinstance(value, (int, float)) and value > 0:
                    return int(value)
                else:
                    self.logger.warning(
                        f"⚠️ Ungültiger notifications_duration Wert: {value}, verwende Default {default}"
                    )
                    return default
            elif key in [
                "notifications_sound",
                "notifications_toast",
                "notifications_show_all",
            ]:
                if isinstance(value, bool):
                    return value
                else:
                    self.logger.warning(
                        f"⚠️ Ungültiger {key} Wert: {value}, verwende Default {default}"
                    )
                    return default
            else:
                return value

        except Exception as e:
            # Log configuration errors
            self.logger.error(
                f"❌ Config-Wert '{key}' Fehler: {e}, verwende Default {default}"
            )
            return default

    def _pythonw_executable(self) -> str:
        """Get the pythonw.exe executable path."""
        exe = Path(sys.executable)
        pyw = exe.with_name("pythonw.exe")
        return str(pyw if pyw.exists() else exe)  # fallback to python.exe

    def _spawn_worker(self, args: list[str], wait: bool = False) -> None:
        """Spawn a silent worker process for notifications."""
        # Beende vorherige Notification, falls vorhanden
        self._terminate_current_notification()

        script = Path(__file__).resolve()
        py = self._pythonw_executable()

        # Build command: pythonw.exe notifications.py --worker <args...>
        cmd = [py, str(script), "--worker"] + args

        # Detach from console and silence stdio
        flags = 0
        if os.name == "nt":
            CREATE_NO_WINDOW = 0x08000000
            DETACHED_PROCESS = 0x00000008
            flags = CREATE_NO_WINDOW | DETACHED_PROCESS

        try:
            with open(os.devnull, "w") as devnull:
                proc = subprocess.Popen(
                    cmd,
                    stdout=devnull,
                    stderr=devnull,
                    stdin=devnull,
                    creationflags=flags,
                    close_fds=True,
                    shell=False,
                )

                # Speichere aktuellen Prozess für frühere Beendigung
                self.current_notification_process = proc

                if wait:
                    proc.wait()
                else:
                    # Store process reference to prevent immediate cleanup
                    self.active_notifications.append(proc)

                self.logger.debug(
                    f"Notification Worker-Prozess gestartet (PID: {proc.pid})"
                )

        except Exception as e:
            # Log worker process errors
            self.logger.error(f"❌ Worker-Prozess Fehler: {e}")
            self.logger.error(f"   Kommando: {cmd}")

    def _terminate_current_notification(self) -> None:
        """Beende die aktuelle Notification, falls vorhanden."""
        if (
            self.current_notification_process
            and self.current_notification_process.poll() is None
        ):
            self.logger.debug(
                f"🛑 Beende aktuelle Notification (PID: {self.current_notification_process.pid})"
            )
            try:
                self.current_notification_process.terminate()
                self.logger.debug("✅ Aktuelle Notification erfolgreich beendet")
            except Exception as e:
                # Log termination errors
                self.logger.error(f"❌ Fehler beim Beenden der Notification: {e}")
            finally:
                self.current_notification_process = None
        else:
            self.logger.debug("ℹ️ Keine aktuelle Notification zum Beenden vorhanden")

    def _worker_show_toast(self, args: list[str]) -> None:
        """Worker function to actually show the toast."""
        # Parse args: [title, message, --icon path, --duration seconds, --url url, --command cmd]
        title = args[0] if len(args) > 0 else "Mauscribe"
        message = args[1] if len(args) > 1 else "Notification"

        icon_path = None
        duration = 5  # Default duration
        url = None
        command = None

        i = 2
        while i < len(args):
            if args[i] == "--icon" and i + 1 < len(args):
                icon_path = args[i + 1]
                i += 2
            elif args[i] == "--duration" and i + 1 < len(args):
                duration = int(args[i + 1])
                i += 2
            elif args[i] == "--url" and i + 1 < len(args):
                url = args[i + 1]
                i += 2
            elif args[i] == "--command" and i + 1 < len(args):
                command = args[i + 1]
                i += 2
            else:
                i += 1

        try:
            # Import inside worker so warnings (if any) don't hit parent console
            from win10toast_click import ToastNotifier  # type: ignore

            icon_path = icon_path if (icon_path and Path(icon_path).exists()) else None

            def _on_click():
                try:
                    if url:
                        webbrowser.open(url)
                    elif command:
                        p = Path(command)
                        if p.exists():
                            os.startfile(str(p))  # type: ignore[attr-defined]
                        else:
                            # Fallback: run arbitrary command
                            subprocess.Popen(
                                command if os.name == "nt" else shlex.split(command),
                                shell=(os.name == "nt"),
                            )
                finally:
                    # Must return an int to keep low-level callback happy
                    return 0

            cb = _on_click if (url or command) else (lambda: 0)

            toaster = ToastNotifier()
            # threaded=True so we can keep the process alive until it disappears
            result = toaster.show_toast(
                title,
                message,
                icon_path=icon_path,
                duration=duration,
                threaded=True,
                callback_on_click=cb,
            )

            # Log success or failure
            if result:
                print(f"✅ Notification erfolgreich angezeigt: '{title}'")
            else:
                print(f"❌ Notification fehlgeschlagen: '{title}'")

            # Keep worker alive while toast is visible (prevents teardown errors)
            while toaster.notification_active():
                time.sleep(0.1)

        except Exception as e:
            print(f"❌ Worker Toast-Fehler: {e}")
            print(f"   Titel: '{title}'")
            print(f"   Nachricht: '{message}'")

    def show_recording_started(self, duration: Optional[int] = None) -> None:
        """Show notification when recording starts."""
        # Deaktiviert - keine Start-Notification gewünscht
        return

    def show_recording_successful(self, duration: float, text_length: int = 0) -> None:
        """Show notification when recording is successful."""
        self.logger.debug(
            f"🎯 show_recording_successful aufgerufen: duration={duration}, text_length={text_length}"
        )

        if not self._should_show_notification():
            self.logger.debug("❌ show_recording_successful: Notifications deaktiviert")
            return

        title = "Aufnahme erfolgreich"
        if text_length > 0:
            message = f"Aufnahme abgeschlossen ({duration:.1f}s) - {text_length} Zeichen transkribiert"
        else:
            message = (
                f"Aufnahme abgeschlossen ({duration:.1f}s) - Text wird verarbeitet..."
            )

        self.logger.debug(
            f"📝 show_recording_successful: title='{title}', message='{message}'"
        )
        self._show_notification(title, message, "success")

    def show_recording_stopped(self, text_length: int = 0) -> None:
        """Show notification when recording stops."""
        if not self._should_show_notification():
            return

        title = "Recording Stopped"
        if text_length > 0:
            message = f"Recording ended. {text_length} characters transcribed."
        else:
            message = "Recording ended. Text is being processed..."

        self._show_notification(title, message, "success")

    def show_transcription_successful(
        self, text: str, duration: float, recording_id: int = None
    ) -> None:
        """Show notification when transcription is successful."""
        self.logger.debug(
            f"🎯 show_transcription_successful aufgerufen: text='{text[:50]}...', duration={duration}, recording_id={recording_id}"
        )

        if not self._should_show_notification():
            self.logger.debug(
                "❌ show_transcription_successful: Notifications deaktiviert"
            )
            return

        title = "Transkription erfolgreich"

        # Truncate text if too long
        if len(text) > 100:
            display_text = text[:49] + "..." + text[-49:]
        else:
            display_text = text

        message = f"'{display_text}' ({duration:.1f}s)"
        self.logger.debug(
            f"📝 show_transcription_successful: title='{title}', message='{message}'"
        )
        self._show_notification(title, message, "success", recording_id=recording_id)

    def show_transcription_complete(
        self, text: str, duration: float, recording_id: int = None
    ) -> None:
        """Show notification when transcription is complete."""
        # Verwende die neue erfolgreiche Transkription-Methode
        self.show_transcription_successful(text, duration, recording_id)

    def show_text_pasted(self, text: str) -> None:
        """Show notification when text is pasted."""
        if not self._should_show_notification():
            return

        title = "Text Pasted"

        # Truncate text if too long
        if len(text) > 80:
            display_text = text[:77] + "..."
        else:
            display_text = text

        message = f"Text was pasted: '{display_text}'"
        self._show_notification(title, message, "info")

    def show_error(self, error_message: str, context: str = "") -> None:
        """Show error notification."""
        if not self._should_show_notification():
            return

        title = "Error"
        if context:
            message = f"{context}: {error_message}"
        else:
            message = error_message

        self._show_notification(title, message, "error")

    def show_warning(self, warning_message: str, context: str = "") -> None:
        """Show warning notification."""
        if not self._should_show_notification():
            return

        title = "Warning"
        if context:
            message = f"{context}: {warning_message}"
        else:
            message = warning_message

        self._show_notification(title, message, "warning")

    def show_info(self, info_message: str, context: str = "") -> None:
        """Show info notification."""
        if not self._should_show_notification():
            return

        title = "Information"
        if context:
            message = f"{context}: {info_message}"
        else:
            message = info_message

        self._show_notification(title, message, "info")

    def show_spell_check_complete(
        self, original_text: str, corrected_text: str
    ) -> None:
        """Show notification when spell checking is complete."""
        if not self._should_show_notification():
            return

        title = "Spell Check Complete"

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

            message = f"Correction: '{orig_display}' -> '{corr_display}'"

        self._show_notification(title, message, "info")

    def show_processing(self) -> None:
        """Show notification when processing audio."""
        if not self._should_show_notification():
            return

        title = "Verarbeite Audio"
        message = "Sprachaufnahme wird transkribiert..."

        self._show_notification(title, message, "info")

    def _should_show_notification(self) -> bool:
        """Check if notifications should be shown based on configuration."""
        should_show = self.show_all_notifications
        self.logger.debug(
            f"🔍 Notification-Check: show_all_notifications={self.show_all_notifications}, should_show={should_show}"
        )
        return should_show

    def _show_notification(
        self,
        title: str,
        message: str,
        notification_type: str = "info",
        recording_id: int = None,
    ) -> None:
        """Show a notification using worker process."""
        try:
            # Validate and sanitize inputs
            title = str(title).strip() or "Mauscribe"
            message = str(message).strip() or "Notification"

            # Log notification attempt
            self.logger.info(f"📢 Sende Notification: '{title}' - '{message}'")

            # Get icon path
            icon_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "icons",
                "mauscribe_icon.ico",
            )
            if not os.path.exists(icon_path):
                icon_path = None
                self.logger.debug("Icon-Pfad nicht gefunden, verwende Standard-Icon")

            # Use worker process method to isolate win10toast_click errors
            args = [title, message, "--duration", str(self.notification_duration)]
            if icon_path:
                args.extend(["--icon", icon_path])
            self._spawn_worker(args)

            self.logger.debug("Notification Worker-Prozess gestartet")

        except Exception as e:
            # Log notification errors
            self.logger.error(f"❌ Notification-Fehler: {e}")
            self.logger.error(f"   Titel: '{title}'")
            self.logger.error(f"   Nachricht: '{message}'")
            self.logger.error(f"   Typ: {notification_type}")

    def is_supported(self) -> bool:
        """Check if Windows notifications are supported on this system."""
        supported = os.name == "nt"
        self.logger.debug(
            f"🔍 Windows Notification Support: {supported} (OS: {os.name})"
        )
        return supported

    def get_system_info(self) -> dict[str, Any]:
        """Get system information for debugging."""
        try:
            info = {
                "supported": self.is_supported(),
                "notification_duration": self.notification_duration,
                "enable_sound": self.enable_sound,
                "enable_toast": self.enable_toast,
                "show_all_notifications": self.show_all_notifications,
                "active_notifications": len(self.active_notifications),
                "pythonw_available": Path(self._pythonw_executable()).exists(),
            }
            return info
        except Exception as e:
            return {"supported": True, "error": "Unknown error"}
