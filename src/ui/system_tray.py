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
    LANGUAGE_SUBMENU = "🌍 Sprachen"
    VOLUME_REDUCTION_SUBMENU = "🔊 Lautstärke-Reduzierung"
    SEPARATOR = "---"
    HOTWORD_TOGGLE = "🎯 Hot Word Detection"
    NOTIFICATIONS_TOGGLE = "🔔 Benachrichtigungen"
    EXIT = "Exit"


class SysTray:
    """Manages the system tray icon and menu for Mauscribe."""

    def __init__(self, settings: Settings, app_instance: Any) -> None:
        """Initialize the system tray manager.

        Args:
            settings: Settings instance
            app_instance: Reference to the main application instance
        """
        self.settings = settings
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
            MenuItem.HOTWORD_TOGGLE.value: self._toggle_hotword_detection,
            MenuItem.NOTIFICATIONS_TOGGLE.value: self._toggle_notifications,
            MenuItem.EXIT.value: self.app_instance.stop,
        }

    def create_icon(self) -> Image.Image:
        """Load icon from icons directory for the system tray using Settings."""
        try:
            # Use absolute path to icon
            project_root = Path(__file__).parent.parent.parent
            icon_path = project_root / "src" / "ui" / "icons" / "icon.png"

            # Load the icon and resize to appropriate size for system tray
            icon = Image.open(icon_path)
            # Convert to RGBA if needed and resize to 64x64
            if icon.mode != "RGBA":
                icon = icon.convert("RGBA")
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
            raise e

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
                    menu_items.append(pystray.MenuItem(MenuItem.WHISPER_MODEL_SUBMENU.value, pystray.Menu(*submenu_items)))
                elif item_name == MenuItem.LANGUAGE_SUBMENU.value:
                    # Create submenu for language selection
                    submenu_items = self._create_language_submenu()
                    menu_items.append(pystray.MenuItem(MenuItem.LANGUAGE_SUBMENU.value, pystray.Menu(*submenu_items)))
                elif item_name == MenuItem.VOLUME_REDUCTION_SUBMENU.value:
                    # Create submenu for volume reduction selection
                    submenu_items = self._create_volume_reduction_submenu()
                    menu_items.append(pystray.MenuItem(MenuItem.VOLUME_REDUCTION_SUBMENU.value, pystray.Menu(*submenu_items)))
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

    def _toggle_hotword_detection(self) -> None:
        """Toggle Hot Word Detection on/off."""
        try:
            if not hasattr(self.app_instance, "hotword_detector"):
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
            if hasattr(self.app_instance, "config") and hasattr(self.app_instance.config, "notifications"):
                return self.app_instance.config.notifications.get("enabled", True)
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
            if not hasattr(self.app_instance, "config"):
                self.logger.error("❌ Config nicht verfügbar")
                return

            # Get current state
            current_state = self._is_notifications_enabled()
            new_state = not current_state

            # Save to TOML file first
            self._save_notifications_setting(new_state)

            # Reload settings to apply changes
            if hasattr(self.app_instance, "config"):
                # Reload the config
                from ..utils.settings import Settings

                self.app_instance.config = Settings()

                # Reinitialize toaster with new settings
                if hasattr(self.app_instance, "toaster"):
                    notification_enabled = self.app_instance.config.notifications.get("enabled", True)
                    notification_sound = self.app_instance.config.notifications.get("sound", True)
                    notification_duration = self.app_instance.config.notifications.get(
                        "duration", 1000
                    )  # Changed from 5000 to 1000

                    from ..ui.toast import Toaster

                    self.app_instance.toaster = Toaster(
                        enable_sound=notification_sound,
                        default_duration=notification_duration,
                        enabled=notification_enabled,
                        notification_settings=self.app_instance.config.notifications,
                    )

            # Show notification
            status_text = "aktiviert" if new_state else "deaktiviert"
            if hasattr(self.app_instance, "toaster"):
                self.app_instance.toaster.show_info(
                    f"🔔 Benachrichtigungen {status_text}", f"Notifications sind jetzt {status_text}"
                )

            self.logger.info(f"✅ Benachrichtigungen {status_text}")

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Umschalten der Benachrichtigungen: {e}")

    def _save_notifications_setting(self, enabled: bool) -> None:
        """Save notifications setting to TOML file."""
        try:
            import toml

            # Read current config
            with open("settings.toml", encoding="utf-8") as f:
                config = toml.load(f)

            # Update the setting
            if "notifications" not in config:
                config["notifications"] = {}
            config["notifications"]["enabled"] = enabled

            # Write back to file with clean formatting - manual TOML writing to avoid syntax issues
            self._write_clean_toml(config)

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
                ("large", "Large (1550 MB) - Beste Qualität"),
            ]

            # Get current model
            current_model = self.settings.model

            submenu_items = []
            for model_id, model_desc in models:
                # Create callback for this model
                def create_model_callback(model):
                    return lambda icon, item: self._set_whisper_model(model)

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

    def _set_whisper_model(self, model: str) -> None:
        """Set whisper model."""
        try:
            # Save to TOML file first
            self._save_whisper_model_setting(model)

            # Reload settings to apply changes
            self.app_instance.config = Settings()

            # Reinitialize transcriptor with new model
            if hasattr(self.app_instance, "transcriptor"):
                from ..audio.transcriptor import Transcriptor

                self.app_instance.transcriptor = Transcriptor(
                    model_size=model, language=self.app_instance.config.transcription.get("language", "de")
                )

            # Show notification
            if hasattr(self.app_instance, "toaster"):
                self.app_instance.toaster.show_info("🎤 Whisper-Modell geändert", f"Neues Modell: {model}")

            self.logger.info(f"✅ Whisper-Modell auf {model} gesetzt")

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Setzen des Whisper-Modells: {e}")

    def _save_whisper_model_setting(self, model: str) -> None:
        """Save whisper model setting to TOML file."""
        try:
            import toml

            # Read current config
            with open("settings.toml", encoding="utf-8") as f:
                config = toml.load(f)

            # Update the setting
            if "transcription" not in config:
                config["transcription"] = {}
            config["transcription"]["model"] = model

            # Write back to file with clean formatting - manual TOML writing to avoid syntax issues
            self._write_clean_toml(config)

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Speichern der Whisper-Modell Einstellung: {e}")

    def _create_language_submenu(self) -> list:
        """Create submenu for language selection."""
        try:
            # Available languages
            languages = [("de", "🇩🇪 Deutsch"), ("en", "🇺🇸 English"), ("auto", "🔍 Automatisch")]

            # Get current enabled languages
            current_languages = getattr(self.settings, "enabled_languages", ["de", "en"])
            current_primary = getattr(self.settings, "primary_language", "de")

            submenu_items = []

            # Language toggle items
            for lang_id, lang_desc in languages:
                if lang_id != "auto":  # Skip auto for toggles

                    def create_lang_callback(lang):
                        return lambda icon, item: self._toggle_language(lang)

                    is_enabled = lang_id in current_languages
                    menu_item = pystray.MenuItem(
                        f"{'✅' if is_enabled else '  '} {lang_desc}",
                        create_lang_callback(lang_id),
                        checked=lambda item, lang=lang_id: lang in current_languages,
                    )
                    submenu_items.append(menu_item)

            # Separator
            submenu_items.append(pystray.Menu.SEPARATOR)

            # Primary language selection
            submenu_items.append(pystray.MenuItem("🎯 Hauptsprache:", None))

            for lang_id, lang_desc in languages:

                def create_primary_callback(lang):
                    return lambda icon, item: self._set_primary_language(lang)

                menu_item = pystray.MenuItem(
                    f"{'✅' if lang_id == current_primary else '  '} {lang_desc}",
                    create_primary_callback(lang_id),
                    checked=lambda item, lang=lang_id: lang == current_primary,
                )
                submenu_items.append(menu_item)

            return submenu_items

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Erstellen des Sprach-Submenus: {e}")
            return []

    def _toggle_language(self, language: str) -> None:
        """Toggle language on/off."""
        try:
            # Get current enabled languages
            current_languages = getattr(self.settings, "enabled_languages", ["de", "en"])

            if language in current_languages:
                # Remove language
                current_languages.remove(language)
                status_text = "deaktiviert"
            else:
                # Add language
                current_languages.append(language)
                status_text = "aktiviert"

            # Save to TOML file
            self._save_language_settings(current_languages, getattr(self.settings, "primary_language", "de"))

            # Reload settings
            self.app_instance.config = Settings()

            # Show notification
            if hasattr(self.app_instance, "toaster"):
                self.app_instance.toaster.show_info(f"🌍 Sprache {status_text}", f"{language.upper()} wurde {status_text}")

            self.logger.info(f"✅ Sprache {language} {status_text}")

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Umschalten der Sprache: {e}")

    def _create_volume_reduction_submenu(self) -> list:
        """Create volume reduction submenu with 20% steps."""
        try:
            # Get current volume reduction factor directly from settings object
            current_factor = self.settings.volume_reduction_factor

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

                submenu_items.append(pystray.MenuItem(menu_text, lambda f=factor: self._set_volume_reduction(f)))

            return submenu_items

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Erstellen des Lautstärke-Submenüs: {e}")
            return []

    def _set_volume_reduction(self, factor: float) -> None:
        """Set volume reduction factor."""
        try:
            # Update settings object directly
            self.settings.volume_reduction_factor = factor

            # Update volume controller if available - CRITICAL FIX
            if hasattr(self.app_instance, "volume_controller"):
                self.app_instance.volume_controller.reduction_factor = factor
                reduction_percent = (1.0 - factor) * 100
                self.logger.info(f"🔊 Lautstärke-Reduzierung auf {reduction_percent:.0f}% gesetzt (sofort wirksam)")
            else:
                self.logger.warning("⚠️ Volume Controller nicht verfügbar")

            # Save to TOML file
            self._save_volume_reduction_setting(factor)

            # Refresh menu to show updated selection
            self._refresh_menu()

            # Show notification
            if hasattr(self.app_instance, "toaster"):
                reduction_percent = (1.0 - factor) * 100
                self.app_instance.toaster.show_info(
                    "🔊 Lautstärke-Reduzierung", f"{reduction_percent:.0f}% Reduzierung gesetzt"
                )

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Setzen der Lautstärke-Reduzierung: {e}")

    def _save_volume_reduction_setting(self, factor: float) -> None:
        """Save volume reduction setting to TOML file."""
        try:
            import toml

            # Load current config
            config_path = "settings.toml"
            try:
                with open(config_path, encoding="utf-8") as f:
                    config = toml.load(f)
            except FileNotFoundError:
                config = {}

            # Ensure system section exists
            if "system" not in config:
                config["system"] = {}

            # Set volume reduction factor
            config["system"]["volume_reduction_factor"] = factor

            # Save back to file
            with open(config_path, "w", encoding="utf-8") as f:
                toml.dump(config, f)

            self.logger.info(f"💾 Lautstärke-Reduzierung ({factor:.0%}) in settings.toml gespeichert")

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Speichern der Lautstärke-Einstellung: {e}")

    def _write_clean_toml(self, config: dict) -> None:
        """Write TOML file with clean formatting to avoid syntax issues."""
        try:
            import toml

            # Read current file
            with open("settings.toml", encoding="utf-8") as f:
                current_config = toml.load(f)

            # Update only the changed values
            for section, values in config.items():
                if section in current_config:
                    current_config[section].update(values)
                else:
                    current_config[section] = values

            # Ensure simple values are properly formatted
            if "transcription" in current_config:
                # Clean up any old list-based settings
                if "enabled_models" in current_config["transcription"]:
                    del current_config["transcription"]["enabled_models"]
                if "enabled_languages" in current_config["transcription"]:
                    del current_config["transcription"]["enabled_languages"]
                if "primary_model" in current_config["transcription"]:
                    del current_config["transcription"]["primary_model"]
                if "primary_language" in current_config["transcription"]:
                    del current_config["transcription"]["primary_language"]
                if "whisper_model" in current_config["transcription"]:
                    del current_config["transcription"]["whisper_model"]

            # Write back with clean formatting
            with open("settings.toml", "w", encoding="utf-8") as f:
                toml.dump(current_config, f)

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Schreiben der TOML-Datei: {e}")
            # Fallback: Write minimal config
            try:
                import toml

                with open("settings.toml", "w", encoding="utf-8") as f:
                    toml.dump(config, f)
            except Exception as e2:
                self.logger.error(f"❌ Auch Fallback fehlgeschlagen: {e2}")

    def _set_primary_language(self, language: str) -> None:
        """Set primary language."""
        try:
            # Save to TOML file
            current_languages = getattr(self.settings, "enabled_languages", ["de", "en"])
            self._save_language_settings(current_languages, language)

            # Reload settings
            self.app_instance.config = Settings()

            # Show notification
            if hasattr(self.app_instance, "toaster"):
                self.app_instance.toaster.show_info("🎯 Hauptsprache geändert", f"Neue Hauptsprache: {language.upper()}")

            self.logger.info(f"✅ Hauptsprache auf {language} gesetzt")

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Setzen der Hauptsprache: {e}")

    def _save_language_settings(self, enabled_languages: list, primary_language: str) -> None:
        """Save language settings to TOML file."""
        try:
            import toml

            # Read current config
            with open("settings.toml", encoding="utf-8") as f:
                config = toml.load(f)

            # Update the settings
            if "transcription" not in config:
                config["transcription"] = {}
            config["transcription"]["enabled_languages"] = enabled_languages
            config["transcription"]["primary_language"] = primary_language

            # Write back to file with clean formatting - manual TOML writing to avoid syntax issues
            self._write_clean_toml(config)

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Speichern der Sprach-Einstellungen: {e}")
