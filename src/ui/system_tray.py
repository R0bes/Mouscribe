# src/system_tray.py - System Tray Management for Mauscribe
"""
System Tray Management Module
Handles system tray icon, menu, and related functionality
"""
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import pystray
from PIL import Image

from ..config import AppConfig
from ..utils import get_logger


class MenuItem(Enum):
    """System tray menu items."""

    WHISPER_MODEL_SUBMENU = "🎤 Whisper-Modell"
    LANGUAGE_SUBMENU = "🌍 Sprachen"
    VOLUME_REDUCTION_SUBMENU = "🔊 Lautstärke-Reduzierung"
    SEPARATOR = "---"
    CONTROL_CENTER = "🎮 Control Center"
    NOTIFICATIONS_TOGGLE = "🔔 Benachrichtigungen"
    EXIT = "Exit"


class SysTray:
    """Manages the system tray icon and menu for Mauscribe."""

    def __init__(self, config: AppConfig, app_instance: Any) -> None:
        """Initialize the system tray manager.

        Args:
            config: AppConfig instance
            app_instance: Reference to the main application instance
        """
        self.config = config
        self.app_instance = app_instance

        self.logger = get_logger("SystemTray")

        # State management
        self.system_tray: Optional[pystray.Icon] = None
        self.is_recording = False

        # Menu definitions - centralized Settings
        self.menu_definitions = {
            MenuItem.WHISPER_MODEL_SUBMENU.value: self._create_whisper_model_submenu,
            MenuItem.LANGUAGE_SUBMENU.value: self._create_language_submenu,
            MenuItem.VOLUME_REDUCTION_SUBMENU.value: self._create_volume_reduction_submenu,
            MenuItem.SEPARATOR.value: None,  # Separator item
            MenuItem.CONTROL_CENTER.value: self._open_control_center,
            MenuItem.NOTIFICATIONS_TOGGLE.value: self._toggle_notifications,
            MenuItem.EXIT.value: self.app_instance.stop,
        }

    def create_icon(self) -> Image.Image:
        """Load icon from icons directory for the system tray."""
        try:
            # Use absolute path to icon
            project_root = Path(__file__).parent.parent.parent
            icons_dir = project_root / "src" / "ui" / "icons"

            # Choose icon based on recording state
            if self.is_recording:
                icon_path = icons_dir / "icon_record.ico"
            else:
                icon_path = icons_dir / "icon_idle.ico"

            # Fallback to PNG if ICO fails
            if not icon_path.exists():
                if self.is_recording:
                    icon_path = icons_dir / "icon_record.png"
                else:
                    icon_path = icons_dir / "icon_idle.png"

            # Load the icon and resize to appropriate size for system tray
            icon = Image.open(icon_path)
            # Convert to RGBA if needed and resize to 64x64
            if icon.mode != "RGBA":
                icon = icon.convert("RGBA")
            icon = icon.resize((64, 64), Image.Resampling.LANCZOS)

            return icon

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Laden des Icons: {e}")
            # Create a simple fallback icon
            fallback_icon = Image.new("RGBA", (64, 64), (128, 128, 128, 255))
            return fallback_icon

    def set_recording_state(self, is_recording: bool) -> None:
        """Update recording state and refresh icon."""
        try:
            if self.is_recording != is_recording:
                self.is_recording = is_recording
                self._refresh_icon()
                self.logger.info(f"🎙️ Recording state changed: {'Recording' if is_recording else 'Idle'}")
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Aktualisieren des Recording-Status: {e}")

    def _refresh_icon(self) -> None:
        """Refresh the system tray icon."""
        try:
            if self.system_tray:
                new_icon = self.create_icon()
                self.system_tray.icon = new_icon
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Aktualisieren des Icons: {e}")

    def setup(self) -> None:
        """Initialize the system tray icon and menu."""
        try:
            icon_image = self.create_icon()

            # Generate menu items from definitions
            menu_items = []
            for item_name in self.menu_definitions.keys():
                if item_name == MenuItem.SEPARATOR.value:
                    menu_items.append(pystray.Menu.SEPARATOR)
                elif item_name == MenuItem.NOTIFICATIONS_TOGGLE.value:
                    # Create checkbox-style menu item for notifications toggle
                    menu_items.append(
                        pystray.MenuItem(
                            self._get_notifications_menu_text(),
                            self._toggle_notifications,
                            checked=lambda item: self._is_notifications_enabled(),
                        )
                    )
                elif item_name == MenuItem.WHISPER_MODEL_SUBMENU.value:
                    # Create submenu for whisper model selection
                    submenu_items = self._create_whisper_model_submenu()
                    menu_items.append(
                        pystray.MenuItem(
                            MenuItem.WHISPER_MODEL_SUBMENU.value,
                            pystray.Menu(*submenu_items),
                        )
                    )
                elif item_name == MenuItem.LANGUAGE_SUBMENU.value:
                    # Create submenu for language selection
                    submenu_items = self._create_language_submenu()
                    menu_items.append(
                        pystray.MenuItem(
                            MenuItem.LANGUAGE_SUBMENU.value,
                            pystray.Menu(*submenu_items),
                        )
                    )
                elif item_name == MenuItem.VOLUME_REDUCTION_SUBMENU.value:
                    # Create submenu for volume reduction selection
                    submenu_items = self._create_volume_reduction_submenu()
                    menu_items.append(
                        pystray.MenuItem(
                            MenuItem.VOLUME_REDUCTION_SUBMENU.value,
                            pystray.Menu(*submenu_items),
                        )
                    )
                else:
                    # Create a proper callback function for each menu item
                    def create_callback(name):
                        return lambda icon, item: self._handle_menu_click(name)

                    menu_items.append(pystray.MenuItem(item_name, create_callback(item_name)))

            menu = tuple(menu_items)

            self.system_tray = pystray.Icon("mauscribe", icon_image, "Mauscribe - Voice-to-Text Tool", menu)
            self.logger.info("🖥️  System Tray erfolgreich initialisiert")
        except Exception as e:
            self.logger.error(f"❌ System Tray konnte nicht initialisiert werden: {e}")
            self.logger.warning("⚠️  System Tray nicht verfügbar - Anwendung läuft im Konsolenmodus")
            self.system_tray = None

    def _handle_menu_click(self, item_name: str) -> None:
        """Handle menu item clicks with error handling."""
        try:
            action = self.menu_definitions.get(item_name)
            if action:
                action()
            else:
                self.logger.warning(f"⚠️  Unbekanntes Menü-Item: {item_name}")
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Verarbeiten des Menü-Klicks: {e}")

    def _refresh_menu(self) -> None:
        """Refresh the system tray menu to show updated state."""
        try:
            if self.system_tray:
                # Stop current system tray
                self.system_tray.stop()

                # Recreate the menu with updated state
                self.setup()

                # Restart the system tray
                self.system_tray.run_detached()
                self.logger.debug("✅ System Tray Menü aktualisiert")
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Aktualisieren des Menüs: {e}")

    # Hotword Detection entfernt

    def update_recording_state(self, is_recording: bool) -> None:
        """Update the recording state and refresh the icon.

        Args:
            is_recording: Whether recording is currently active
        """
        self.set_recording_state(is_recording)

    def run(self) -> None:
        """Run the system tray in a separate thread."""
        if self.system_tray is None:
            self.logger.error("❌ System Tray ist nicht verfügbar")
            return

        try:
            self.system_tray.run()
        except Exception as e:
            self.logger.error(f"❌ System Tray Fehler: {e}")

    def stop(self) -> None:
        """Stop the system tray."""
        if self.system_tray:
            try:
                self.system_tray.stop()
                self.logger.info("✅ System Tray beendet")
            except Exception as e:
                self.logger.error(f"❌ Fehler beim Beenden des System Tray: {e}")

    def is_available(self) -> bool:
        """Check if system tray is available.

        Returns:
            True if system tray is available, False otherwise
        """
        try:
            # Try to create an icon to test if system tray is available
            self.create_icon()
            return True
        except Exception as e:
            self.logger.error(f"❌ System Tray nicht verfügbar: {e}")
            return False

    def _is_notifications_enabled(self) -> bool:
        """Check if notifications are currently enabled."""
        try:
            # Check if any notification type is enabled
            notifications = self.config.ui.notifications
            return (
                notifications.transcription_success.toast
                or notifications.transcription_success.sound
                or notifications.recording_start.toast
                or notifications.recording_start.sound
            )
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Prüfen des Notification Status: {e}")
            return True

    def _get_notifications_menu_text(self) -> str:
        """Get the menu text for notifications toggle."""
        enabled = self._is_notifications_enabled()
        status = "✅" if enabled else "❌"
        return f"{status} 🔔 Benachrichtigungen"

    def _toggle_notifications(self, icon=None, item=None) -> None:
        """Toggle notifications on/off."""
        try:
            # Get current state
            current_state = self._is_notifications_enabled()
            new_state = not current_state

            # Update config object and save selectively
            notification_keys = [
                "ui.notifications.transcription_success.toast",
                "ui.notifications.transcription_success.sound",
                "ui.notifications.recording_start.toast",
                "ui.notifications.recording_start.sound",
                "ui.notifications.recording_stop.toast",
                "ui.notifications.recording_stop.sound",
                "ui.notifications.recording_error.toast",
                "ui.notifications.recording_error.sound",
                "ui.notifications.transcription_error.toast",
                "ui.notifications.transcription_error.sound",
                "ui.notifications.transcription_empty.toast",
                "ui.notifications.transcription_empty.sound",
                "ui.notifications.text_inserted.toast",
                "ui.notifications.text_inserted.sound",
                "ui.notifications.text_insert_error.toast",
                "ui.notifications.text_insert_error.sound",
                "ui.notifications.app_start.toast",
                "ui.notifications.app_start.sound",
                "ui.notifications.app_shutdown.toast",
                "ui.notifications.app_shutdown.sound",
            ]

            for key in notification_keys:
                self.config.update_and_save(key, new_state)

            # Update app instance config
            notifications = self.app_instance.config.ui.notifications
            notifications.transcription_success.toast = new_state
            notifications.transcription_success.sound = new_state
            notifications.recording_start.toast = new_state
            notifications.recording_start.sound = new_state
            notifications.recording_stop.toast = new_state
            notifications.recording_stop.sound = new_state
            notifications.recording_error.toast = new_state
            notifications.recording_error.sound = new_state
            notifications.transcription_error.toast = new_state
            notifications.transcription_error.sound = new_state
            notifications.transcription_empty.toast = new_state
            notifications.transcription_empty.sound = new_state
            notifications.text_inserted.toast = new_state
            notifications.text_inserted.sound = new_state
            notifications.text_insert_error.toast = new_state
            notifications.text_insert_error.sound = new_state
            notifications.app_start.toast = new_state
            notifications.app_start.sound = new_state
            notifications.app_shutdown.toast = new_state
            notifications.app_shutdown.sound = new_state

            # Refresh menu to show updated state
            self._refresh_menu()

            # Show notification
            status_text = "aktiviert" if new_state else "deaktiviert"
            if hasattr(self.app_instance, "toaster"):
                self.app_instance.toaster.show_info(
                    f"🔔 Benachrichtigungen {status_text}",
                    f"Notifications sind jetzt {status_text}",
                )

            self.logger.info(f"✅ Benachrichtigungen {status_text}")

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Umschalten der Benachrichtigungen: {e}")

    def _create_whisper_model_submenu(self) -> list:
        """Create submenu for whisper model selection."""
        try:
            # Available whisper models
            models = [
                ("tiny", "Tiny (39 MB) - Schnellste"),
                ("base", "Base (74 MB) - Ausgewogen"),
                ("small", "Small (244 MB) - Gut"),
                ("medium", "Medium (769 MB) - Sehr gut"),
                ("large", "Large (1550 MB) - Beste Qualität"),
            ]

            # Get current model
            current_model = self.config.audio.model

            submenu_items = []
            for model_id, model_desc in models:
                # Create callback for this model
                def create_model_callback(model):
                    return lambda icon, item: self._set_whisper_model(model, icon, item)

                # Create menu item with checkmark for current model
                menu_item = pystray.MenuItem(
                    f"{'✅' if model_id == current_model else '  '} {model_desc}",
                    create_model_callback(model_id),
                    checked=lambda item, m=model_id: m == current_model,
                )
                submenu_items.append(menu_item)

            return submenu_items

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Erstellen des Whisper-Modell Submenus: {e}")
            return []

    def _set_whisper_model(self, model: str, icon=None, item=None) -> None:
        """Set whisper model."""
        try:
            # Update config object and save selectively
            self.config.update_and_save("audio.model", model)
            self.config.update_and_save("model", model)  # Legacy compatibility

            # Update app instance config
            self.app_instance.config.audio.model = model
            self.app_instance.config.model = model

            # Emit settings change event
            self._emit_settings_event("MODEL_CHANGED", {"model": model})

            # Refresh menu to show updated state
            self._refresh_menu()

            # Show notification
            if hasattr(self.app_instance, "toaster"):
                self.app_instance.toaster.show_info("🎤 Whisper-Modell geändert", f"Neues Modell: {model}")

            self.logger.info(f"✅ Whisper-Modell auf {model} gesetzt")

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Setzen des Whisper-Modells: {e}")

    def _create_language_submenu(self) -> list:
        """Create submenu for language selection."""
        try:
            # Available languages
            languages = [
                ("de", "🇩🇪 Deutsch"),
                ("en", "🇺🇸 English"),
                ("auto", "🔍 Automatisch"),
            ]

            # Get current language
            current_primary = self.config.audio.language

            submenu_items = []

            # Language selection items
            for lang_id, lang_desc in languages:

                def create_lang_callback(lang):
                    return lambda icon, item: self._set_language(lang, icon, item)

                menu_item = pystray.MenuItem(
                    f"{'✅' if lang_id == current_primary else '  '} {lang_desc}",
                    create_lang_callback(lang_id),
                    checked=lambda item, lang=lang_id: lang == current_primary,
                )
                submenu_items.append(menu_item)

            return submenu_items

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Erstellen des Sprach-Submenus: {e}")
            return []

    def _set_language(self, language: str, icon=None, item=None) -> None:
        """Set language."""
        try:
            # Update config object and save selectively
            self.config.update_and_save("audio.language", language)
            self.config.update_and_save("language", language)  # Legacy compatibility

            # Update app instance config
            self.app_instance.config.audio.language = language
            self.app_instance.config.language = language

            # Emit settings change event
            self._emit_settings_event("LANGUAGE_CHANGED", {"language": language})

            # Refresh menu to show updated state
            self._refresh_menu()

            # Show notification
            if hasattr(self.app_instance, "toaster"):
                self.app_instance.toaster.show_info(
                    "🌍 Sprache geändert",
                    f"Neue Sprache: {language.upper()}",
                )

            self.logger.info(f"✅ Sprache auf {language} gesetzt")

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Setzen der Sprache: {e}")

    def _emit_settings_event(self, event_type: str, data: dict) -> None:
        """Emit settings change event."""
        try:
            if hasattr(self.app_instance, "event_bus") and self.app_instance.event_bus:
                import time

                from ...utils.eventbus import Event, EventType

                event = Event(event_type=EventType(event_type), data=data, timestamp=time.time(), source="system_tray")
                self.app_instance.event_bus.emit(event)
        except Exception as e:
            self.logger.error(f"Error emitting settings event: {e}")

    def _create_volume_reduction_submenu(self) -> list:
        """Create volume reduction submenu with 20% steps."""
        try:
            # Get current volume reduction factor
            current_factor = self.config.volume_reduction_factor

            # Create menu items for different reduction levels (20% steps)
            # FIXED: Inverted logic - reduction_factor = 0.0 means 100% reduction (mute)
            reduction_levels = [
                (1.0, "0% (Keine Reduzierung)"),
                (0.8, "20% Reduzierung"),
                (0.6, "40% Reduzierung"),
                (0.4, "60% Reduzierung"),
                (0.2, "80% Reduzierung"),
                (0.0, "100% (Stumm)"),
            ]

            submenu_items = []
            for factor, label in reduction_levels:
                # Mark current selection
                status = "✅" if abs(factor - current_factor) < 0.01 else "⚪"
                menu_text = f"{status} {label}"

                def create_volume_callback(f):
                    return lambda icon, item: self._set_volume_reduction(f)

                submenu_items.append(pystray.MenuItem(menu_text, create_volume_callback(factor)))

            return submenu_items

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Erstellen des Lautstärke-Submenüs: {e}")
            return []

    def _set_volume_reduction(self, factor: float, icon=None, item=None) -> None:
        """Set volume reduction factor."""
        try:
            # Update config object and save selectively
            self.config.update_and_save("volume_reduction_factor", factor)
            self.config.update_and_save("audio.volume_reduction_factor", factor)

            # Update volume controller if available
            if hasattr(self.app_instance, "volume_controller"):
                self.app_instance.volume_controller.reduction_factor = factor
                reduction_percent = (1.0 - factor) * 100
                self.logger.info(f"🔊 Lautstärke-Reduzierung auf {reduction_percent:.0f}% gesetzt (sofort wirksam)")
            else:
                self.logger.warning("⚠️ Volume Controller nicht verfügbar")

            # Update app instance config
            self.app_instance.config.volume_reduction_factor = factor
            self.app_instance.config.audio.volume_reduction_factor = factor

            # Emit settings change event
            self._emit_settings_event("VOLUME_REDUCTION_CHANGED", {"value": factor})

            # Refresh menu to show updated selection
            self._refresh_menu()

            # Show notification
            if hasattr(self.app_instance, "toaster"):
                reduction_percent = (1.0 - factor) * 100
                self.app_instance.toaster.show_info(
                    "🔊 Lautstärke-Reduzierung",
                    f"{reduction_percent:.0f}% Reduzierung gesetzt",
                )

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Setzen der Lautstärke-Reduzierung: {e}")

    def _open_control_center(self, icon=None, item=None) -> None:
        """Open the Control Center window."""
        try:
            # Import here to avoid circular imports and missing dependencies
            from .control_center import open_control_center

            open_control_center(self.config, self.app_instance)
            self.logger.info("🎮 Control Center opened from SystemTray")
        except ImportError as e:
            self.logger.error(f"❌ Failed to import Control Center: {e}")
            # Show notification if available
            if hasattr(self.app_instance, "toaster"):
                self.app_instance.toaster.show_error("Control Center Error", f"Control Center not available: {str(e)}")
        except Exception as e:
            self.logger.error(f"❌ Failed to open Control Center: {e}")
            # Show notification if available
            if hasattr(self.app_instance, "toaster"):
                self.app_instance.toaster.show_error("Control Center Error", f"Failed to open Control Center: {str(e)}")
