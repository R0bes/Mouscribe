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

from ..utils import Settings, get_logger


class MenuItem(Enum):
    """System tray menu items."""
    WHISPER_MODEL_SUBMENU = "🎤 Whisper-Modell"
    SEPARATOR = "---"
    HOTWORD_TOGGLE = "🎯 Hot Word Detection"
    NOTIFICATIONS_TOGGLE = "🔔 Benachrichtigungen"
    EXIT = "Exit"


class SysTray:
    """Manages the system tray icon and menu for Mauscribe."""

    def __init__(self, config: Settings, app_instance: Any) -> None:
        """Initialize the system tray manager.

        Args:
            config: Configuration instance
            app_instance: Reference to the main application instance
        """
        self.config = config
        self.app_instance = app_instance

        self.logger = get_logger("SystemTray")

        # State management
        self.system_tray: Optional[pystray.Icon] = None
        self.is_recording = False
        
        # Menu definitions - centralized configuration
        self.menu_definitions = {
            MenuItem.WHISPER_MODEL_SUBMENU.value: self._create_whisper_model_submenu,
            MenuItem.SEPARATOR.value: None,  # Separator item
            MenuItem.HOTWORD_TOGGLE.value: self._toggle_hotword_detection,
            MenuItem.NOTIFICATIONS_TOGGLE.value: self._toggle_notifications,
            MenuItem.EXIT.value: self.app_instance.stop,
        }

    def create_icon(self) -> Image.Image:
        """Load icon from icons directory for the system tray using configuration."""
        try:
            # Use configuration to get icon path with fallback
            icon_path = self.config.get_icon_path("system_tray")
            
            # Load the icon and resize to appropriate size for system tray
            icon = Image.open(icon_path)
            # Convert to RGBA if needed and resize to 64x64
            if icon.mode != 'RGBA':
                icon = icon.convert('RGBA')
            icon = icon.resize((64, 64), Image.Resampling.LANCZOS)
            
            # Add recording indicator if recording
            if self.is_recording:
                from PIL import ImageDraw
                draw = ImageDraw.Draw(icon)
                # Add red dot in top-right corner
                draw.ellipse([50, 10, 58, 18], fill=(255, 0, 0), outline=(200, 0, 0), width=1)
            
            return icon
            
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Laden des konfigurierten Icons: {e}")
            # Fallback to hardcoded icon if configuration fails
            project_root = Path(__file__).parent.parent.parent
            fallback_path = project_root / "src" / "ui" / "icons" / "systray.ico2"
            
            if not fallback_path.exists():
                raise FileNotFoundError(f"Weder konfiguriertes noch Fallback-Icon gefunden: {fallback_path}")
            
            self.logger.warning(f"⚠️  Verwende Fallback-Icon: {fallback_path}")
            icon = Image.open(fallback_path)
            if icon.mode != 'RGBA':
                icon = icon.convert('RGBA')
            icon = icon.resize((64, 64), Image.Resampling.LANCZOS)
            
            # Add recording indicator if recording
            if self.is_recording:
                from PIL import ImageDraw
                draw = ImageDraw.Draw(icon)
                draw.ellipse([50, 10, 58, 18], fill=(255, 0, 0), outline=(200, 0, 0), width=1)
            
            return icon

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
                            checked=lambda item: self._is_notifications_enabled()
                        )
                    )
                elif item_name == MenuItem.WHISPER_MODEL_SUBMENU.value:
                    # Create submenu for whisper model selection
                    submenu_items = self._create_whisper_model_submenu()
                    menu_items.append(
                        pystray.MenuItem(
                            MenuItem.WHISPER_MODEL_SUBMENU.value,
                            pystray.Menu(*submenu_items)
                        )
                    )
                else:
                    # Create a proper callback function for each menu item
                    def create_callback(name):
                        return lambda icon, item: self._handle_menu_click(name)
                    menu_items.append(
                        pystray.MenuItem(item_name, create_callback(item_name))
                    )
            
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



    def _toggle_hotword_detection(self) -> None:
        """Toggle Hot Word Detection on/off."""
        try:
            if not hasattr(self.app_instance, 'hotword_detector'):
                self.logger.error("❌ Hot Word Detector nicht verfügbar")
                return

            # Toggle Hot Word Detection
            is_active = self.app_instance.toggle_hotword_detection()
            
            # Update menu text (simplified - full refresh would be complex)
            status = "Aktiviert" if is_active else "Deaktiviert"
            self.logger.info(f"🎯 Hot Word Detection {status}")

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Umschalten der Hot Word Detection: {e}")

    def update_recording_state(self, is_recording: bool) -> None:
        """Update the recording state and refresh the icon.

        Args:
            is_recording: Whether recording is currently active
        """
        self.is_recording = is_recording
        if self.system_tray:
            try:
                self.system_tray.icon = self.create_icon()
                self.logger.debug("System tray icon updated")
            except Exception as e:
                self.logger.error(f"❌ Fehler beim Aktualisieren des System Tray Icons: {e}")

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
            if hasattr(self.app_instance, 'config') and hasattr(self.app_instance.config, 'notifications'):
                return self.app_instance.config.notifications.get('enabled', True)
            return True  # Default to enabled
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
            if not hasattr(self.app_instance, 'config'):
                self.logger.error("❌ Config nicht verfügbar")
                return

            # Get current state
            current_state = self._is_notifications_enabled()
            new_state = not current_state

            # Save to TOML file first
            self._save_notifications_setting(new_state)
            
            # Reload settings to apply changes
            if hasattr(self.app_instance, 'config'):
                # Reload the config
                from ..utils.settings import Settings
                self.app_instance.config = Settings()
                
                # Reinitialize toaster with new settings
                if hasattr(self.app_instance, 'toaster'):
                    notification_enabled = self.app_instance.config.notifications.get("enabled", True)
                    notification_sound = self.app_instance.config.notifications.get("sound", True)
                    notification_duration = self.app_instance.config.notifications.get("duration", 5000)
                    
                    from ..ui.notifications import Toaster
                    self.app_instance.toaster = Toaster(
                        enable_sound=notification_sound,
                        default_duration=notification_duration,
                        enabled=notification_enabled,
                        notification_settings=self.app_instance.config.notifications
                    )

            # Show notification
            status_text = "aktiviert" if new_state else "deaktiviert"
            if hasattr(self.app_instance, 'toaster'):
                self.app_instance.toaster.show_info(
                    f"🔔 Benachrichtigungen {status_text}",
                    f"Notifications sind jetzt {status_text}"
                )

            self.logger.info(f"✅ Benachrichtigungen {status_text}")

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Umschalten der Benachrichtigungen: {e}")

    def _save_notifications_setting(self, enabled: bool) -> None:
        """Save notifications setting to TOML file."""
        try:
            import toml
            # Read current config
            with open("settings.toml", "r", encoding="utf-8") as f:
                config = toml.load(f)
            
            # Update the setting
            if "notifications" not in config:
                config["notifications"] = {}
            config["notifications"]["enabled"] = enabled
            
            # Write back to file
            with open("settings.toml", "w", encoding="utf-8") as f:
                toml.dump(config, f)
                
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Speichern der Notification Einstellung: {e}")

    def _create_whisper_model_submenu(self) -> list:
        """Create submenu for whisper model selection."""
        try:
            # Available whisper models
            models = [
                ("tiny", "Tiny (39 MB) - Schnellste"),
                ("base", "Base (74 MB) - Ausgewogen"),
                ("small", "Small (244 MB) - Gut"),
                ("medium", "Medium (769 MB) - Sehr gut"),
                ("large", "Large (1550 MB) - Beste Qualität")
            ]
            
            # Get current model
            current_model = self.config.transcription.get('whisper_model', 'base')
            
            submenu_items = []
            for model_id, model_desc in models:
                # Create callback for this model
                def create_model_callback(model):
                    return lambda icon, item: self._set_whisper_model(model)
                
                # Create menu item with checkmark for current model
                menu_item = pystray.MenuItem(
                    f"{'✅' if model_id == current_model else '  '} {model_desc}",
                    create_model_callback(model_id),
                    checked=lambda item, m=model_id: m == current_model
                )
                submenu_items.append(menu_item)
            
            return submenu_items
            
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Erstellen des Whisper-Modell Submenus: {e}")
            return []

    def _set_whisper_model(self, model: str) -> None:
        """Set whisper model."""
        try:
            # Save to TOML file first
            self._save_whisper_model_setting(model)
            
            # Reload settings to apply changes
            self.app_instance.config = Settings()
            
            # Reinitialize transcriptor with new model
            if hasattr(self.app_instance, 'transcriptor'):
                from ..audio.transcriptor import Transcriptor
                self.app_instance.transcriptor = Transcriptor(
                    model_size=model,
                    language=self.app_instance.config.transcription.get('language', 'de')
                )

            # Show notification
            if hasattr(self.app_instance, 'toaster'):
                self.app_instance.toaster.show_info(
                    f"🎤 Whisper-Modell geändert",
                    f"Neues Modell: {model}"
                )

            self.logger.info(f"✅ Whisper-Modell auf {model} gesetzt")

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Setzen des Whisper-Modells: {e}")

    def _save_whisper_model_setting(self, model: str) -> None:
        """Save whisper model setting to TOML file."""
        try:
            import toml
            # Read current config
            with open("settings.toml", "r", encoding="utf-8") as f:
                config = toml.load(f)
            
            # Update the setting
            if "transcription" not in config:
                config["transcription"] = {}
            config["transcription"]["whisper_model"] = model
            
            # Write back to file
            with open("settings.toml", "w", encoding="utf-8") as f:
                toml.dump(config, f)
                
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Speichern der Whisper-Modell Einstellung: {e}")
