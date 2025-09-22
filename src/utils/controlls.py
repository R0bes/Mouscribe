# src/utils/simple_controls.py - Simplified Input Controls Manager
"""
Simplified input controls manager for Mauscribe.
Handles primary and secondary mouse buttons with simple callbacks.
"""
from typing import Callable, Optional

from pynput import mouse

from .logger import get_logger
from .settings import Settings


class ControllsManager:
    """Simplified controls manager with primary and secondary callbacks."""

    def __init__(
        self, config: Settings, primary_callback: Callable, secondary_callback: Callable, insert_callback: Callable = None
    ):
        """Initialize the controls manager.

        Args:
            config: Settings instance with button configuration
            primary_callback: Function to call when primary button is pressed
            secondary_callback: Function to call when secondary button is pressed
            insert_callback: Function to call when left mouse + primary key combination is pressed
        """
        self.config = config
        self.primary_callback = primary_callback
        self.secondary_callback = secondary_callback
        self.insert_callback = insert_callback
        self.logger = get_logger(self.__class__.__name__)

        # Get button names and types from config
        self.primary_button = self.config.primary_name
        self.primary_type = self.config.primary_type
        self.secondary_button = self.config.secondary_name
        self.secondary_type = self.config.secondary_type

        # Check if secondary input is disabled
        self.secondary_enabled = self.secondary_button and self.secondary_type != "disabled"

        # Mouse listener
        self._mouse_listener: Optional[mouse.Listener] = None
        self._active = False

        # State tracking for combination keys
        self._left_mouse_pressed = False
        self._primary_pressed_while_left_held = False

        self.logger.info("🎮 Simple Controls Manager initialized:")
        self.logger.info(f"   {self.primary_button} ({self.primary_type}): Aufnahme starten/stoppen")
        if self.secondary_enabled:
            self.logger.info(
                f"   {self.secondary_button} ({self.secondary_type}) + {self.primary_button} ({self.primary_type}): Aufnahme stoppen und Text einfügen"
            )
        else:
            self.logger.info("   Sekundäre Eingabe deaktiviert")

    def start(self) -> None:
        """Start input listeners."""
        if self._active:
            return

        try:
            self._mouse_listener = mouse.Listener(on_click=self._on_mouse_click)
            self._mouse_listener.start()
            self._active = True

            self.logger.info("✅ Simple Controls Manager started")
        except Exception as e:
            self.logger.error(f"❌ Failed to start controls manager: {e}")
            raise

    def stop(self) -> None:
        """Stop input listeners."""
        if not self._active:
            return

        try:
            if self._mouse_listener:
                self._mouse_listener.stop()
        finally:
            self._mouse_listener = None
            self._active = False
            self.logger.info("✅ Simple Controls Manager stopped")

    def _on_mouse_click(self, x: int, y: int, button: mouse.Button, pressed: bool) -> None:
        """Handle mouse click events."""
        try:
            button_name = self._get_mouse_button_name(button)
            if not button_name:
                return

            # Handle left mouse button state for combination (only if secondary input is enabled)
            if button_name == "left" and self.secondary_enabled:
                self._left_mouse_pressed = pressed
                if not pressed:  # Left mouse released
                    self._primary_pressed_while_left_held = False
                return

            # Handle primary button with combination logic
            if button_name == self.primary_button:
                if pressed:  # Primary button pressed
                    if self._left_mouse_pressed and self.insert_callback and self.secondary_enabled:
                        # Left mouse is held + primary pressed = insert combination
                        self._primary_pressed_while_left_held = True
                        self.logger.debug(
                            f"🎮 Kombination ausgelöst: {self.secondary_button} ({self.secondary_type}) + {self.primary_button} ({self.primary_type})"
                        )
                        self.insert_callback()
                        return
                else:  # Primary button released
                    if not self._primary_pressed_while_left_held:
                        # Normal primary button action based on type
                        if self.primary_type == "click":
                            self.logger.debug(f"🎮 {self.primary_button} ({self.primary_type}) geklickt")
                            self.primary_callback()
                        elif self.primary_type == "hold" and not pressed:
                            # For hold type, trigger on release
                            self.logger.debug(f"🎮 {self.primary_button} ({self.primary_type}) losgelassen")
                            self.primary_callback()
                    self._primary_pressed_while_left_held = False
                return

            # Handle secondary button based on type (only if enabled)
            if button_name == self.secondary_button and self.secondary_enabled:
                if self.secondary_type == "click" and not pressed:
                    # Click type: trigger on release
                    self.logger.debug(f"🎮 {self.secondary_button} ({self.secondary_type}) geklickt (keine Aktion)")
                    self.secondary_callback()
                elif self.secondary_type == "hold" and pressed:
                    # Hold type: trigger on press (for combination detection)
                    self.logger.debug(f"🎮 {self.secondary_button} ({self.secondary_type}) gedrückt (für Kombination)")
                    # Secondary button is mainly used for combination detection
                    # The actual action happens in the combination logic above

        except Exception as e:
            self.logger.error(f"❌ Mouse click handler error: {e}")

    def _get_mouse_button_name(self, button: mouse.Button) -> Optional[str]:
        """Convert mouse button to name."""
        button_map = {
            mouse.Button.left: "left",
            mouse.Button.right: "right",
            mouse.Button.middle: "middle",
            mouse.Button.x1: "x1",
            mouse.Button.x2: "x2",
        }
        return button_map.get(button)

    def is_active(self) -> bool:
        """Check if controls manager is active."""
        return self._active
