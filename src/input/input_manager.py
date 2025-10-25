# src/input/input_manager.py - Unified Input Management
"""
Unified input management system for Mauscribe.
Replaces both ControllsManager and InputSystem with a single, event-based architecture.
"""

import logging
import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, List, Optional, Set

from pynput import keyboard, mouse

logger = logging.getLogger(__name__)


class InputType(Enum):
    """Types of input events."""

    MOUSE_CLICK = "mouse_click"
    MOUSE_HOLD = "mouse_hold"
    MOUSE_RELEASE = "mouse_release"
    KEYBOARD_PRESS = "keyboard_press"
    KEYBOARD_RELEASE = "keyboard_release"


class MouseButton(Enum):
    """Mouse button types."""

    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"
    X1 = "x1"
    X2 = "x2"


@dataclass
class InputEvent:
    """Input event data."""

    type: InputType
    button: Optional[MouseButton] = None
    key: Optional[str] = None
    position: Optional[tuple[int, int]] = None
    timestamp: float = 0.0


@dataclass
class InputMapping:
    """Input mapping configuration."""

    name: str
    input_type: InputType
    button: Optional[MouseButton] = None
    key: Optional[str] = None
    handler: Optional[Callable] = None
    description: str = ""


class InputManager:
    """
    Unified input management system.

    Features:
    - Single input system replacing both ControllsManager and InputSystem
    - Event-based architecture with centralized event dispatching
    - Configurable input mappings
    - Thread-safe operations
    - Support for mouse and keyboard events
    - Combination key detection
    """

    def __init__(self):
        """Initialize the input manager."""
        self._mouse_listener: Optional[mouse.Listener] = None
        self._keyboard_listener: Optional[keyboard.Listener] = None
        self._active = False

        # Event handlers
        self._event_handlers: dict[str, Callable] = {}

        # Input mappings
        self._input_mappings: list[InputMapping] = []

        # State tracking for combination keys
        self._pressed_buttons: set[MouseButton] = set()
        self._pressed_keys: set[str] = set()
        self._combination_state: dict[str, bool] = {}

        # Thread safety
        self._lock = threading.Lock()

        logger.info("🎮 InputManager initialisiert")

    def register_handler(self, event_name: str, handler: Callable) -> None:
        """
        Register an event handler.

        Args:
            event_name: Name of the event to handle
            handler: Function to call when event occurs
        """
        with self._lock:
            self._event_handlers[event_name] = handler
            logger.info(f"✅ Event-Handler registriert: {event_name}")

    def add_input_mapping(self, mapping: InputMapping) -> None:
        """
        Add an input mapping.

        Args:
            mapping: Input mapping configuration
        """
        with self._lock:
            self._input_mappings.append(mapping)
            logger.info(f"✅ Input-Mapping hinzugefügt: {mapping.name}")

    def remove_input_mapping(self, name: str) -> bool:
        """
        Remove an input mapping.

        Args:
            name: Name of the mapping to remove

        Returns:
            True if mapping was removed, False if not found
        """
        with self._lock:
            for i, mapping in enumerate(self._input_mappings):
                if mapping.name == name:
                    del self._input_mappings[i]
                    logger.info(f"✅ Input-Mapping entfernt: {name}")
                    return True
            return False

    def start(self) -> None:
        """Start the input manager."""
        if self._active:
            logger.warning("⚠️ InputManager läuft bereits")
            return

        try:
            self._active = True

            # Start mouse listener
            self._mouse_listener = mouse.Listener(on_click=self._on_mouse_click, on_scroll=self._on_mouse_scroll)
            self._mouse_listener.start()

            # Start keyboard listener
            self._keyboard_listener = keyboard.Listener(on_press=self._on_key_press, on_release=self._on_key_release)
            self._keyboard_listener.start()

            logger.info("✅ InputManager gestartet")

        except Exception as e:
            logger.error(f"❌ Fehler beim Starten des InputManagers: {e}")
            self._active = False
            raise

    def stop(self) -> None:
        """Stop the input manager."""
        if not self._active:
            return

        try:
            self._active = False

            if self._mouse_listener:
                self._mouse_listener.stop()
                self._mouse_listener = None

            if self._keyboard_listener:
                self._keyboard_listener.stop()
                self._keyboard_listener = None

            # Clear state
            with self._lock:
                self._pressed_buttons.clear()
                self._pressed_keys.clear()
                self._combination_state.clear()

            logger.info("✅ InputManager gestoppt")

        except Exception as e:
            logger.error(f"❌ Fehler beim Stoppen des InputManagers: {e}")

    def _on_mouse_click(self, x: int, y: int, button: mouse.Button, pressed: bool) -> None:
        """Handle mouse click events."""
        try:
            button_enum = self._button_to_enum(button)
            if not button_enum:
                return

            # Update button state
            with self._lock:
                if pressed:
                    self._pressed_buttons.add(button_enum)
                else:
                    self._pressed_buttons.discard(button_enum)

            # Create event
            event_type = InputType.MOUSE_HOLD if pressed else InputType.MOUSE_RELEASE
            event = InputEvent(type=event_type, button=button_enum, position=(x, y), timestamp=time.time())

            # Dispatch event
            self._dispatch_event(event)

        except Exception as e:
            logger.error(f"❌ Mouse click handler error: {e}")

    def _on_mouse_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
        """Handle mouse scroll events."""
        # Currently not used, but available for future extensions
        pass

    def _on_key_press(self, key) -> None:
        """Handle keyboard press events."""
        try:
            key_str = self._key_to_string(key)

            with self._lock:
                self._pressed_keys.add(key_str)

            # Create event
            event = InputEvent(type=InputType.KEYBOARD_PRESS, key=key_str, timestamp=time.time())

            # Dispatch event
            self._dispatch_event(event)

        except Exception as e:
            logger.error(f"❌ Key press handler error: {e}")

    def _on_key_release(self, key) -> None:
        """Handle keyboard release events."""
        try:
            key_str = self._key_to_string(key)

            with self._lock:
                self._pressed_keys.discard(key_str)

            # Create event
            event = InputEvent(type=InputType.KEYBOARD_RELEASE, key=key_str, timestamp=time.time())

            # Dispatch event
            self._dispatch_event(event)

        except Exception as e:
            logger.error(f"❌ Key release handler error: {e}")

    def _dispatch_event(self, event: InputEvent) -> None:
        """Dispatch event to registered handlers."""
        try:
            # Check input mappings
            for mapping in self._input_mappings:
                if self._matches_mapping(event, mapping):
                    if mapping.handler:
                        mapping.handler(event)
                    break

            # Check combination mappings
            self._check_combinations(event)

        except Exception as e:
            logger.error(f"❌ Event dispatch error: {e}")

    def _matches_mapping(self, event: InputEvent, mapping: InputMapping) -> bool:
        """Check if event matches a mapping."""
        if event.type != mapping.input_type:
            return False

        if mapping.button and event.button != mapping.button:
            return False

        if mapping.key and event.key != mapping.key:
            return False

        return True

    def _check_combinations(self, event: InputEvent) -> None:
        """Check for combination key events."""
        try:
            # Check for left mouse + X2 combination
            if (
                event.type == InputType.MOUSE_HOLD
                and event.button == MouseButton.X2
                and MouseButton.LEFT in self._pressed_buttons
            ):
                # Dispatch combination event
                combo_event = InputEvent(
                    type=InputType.MOUSE_HOLD, button=MouseButton.X2, position=event.position, timestamp=event.timestamp
                )

                handler = self._event_handlers.get("insert_combination")
                if handler:
                    handler(combo_event)

        except Exception as e:
            logger.error(f"❌ Combination check error: {e}")

    def _button_to_enum(self, button: mouse.Button) -> Optional[MouseButton]:
        """Convert pynput mouse button to enum."""
        button_map = {
            mouse.Button.left: MouseButton.LEFT,
            mouse.Button.right: MouseButton.RIGHT,
            mouse.Button.middle: MouseButton.MIDDLE,
            mouse.Button.x1: MouseButton.X1,
            mouse.Button.x2: MouseButton.X2,
        }
        return button_map.get(button)

    def _key_to_string(self, key) -> str:
        """Convert pynput key to string."""
        if hasattr(key, "char") and key.char:
            return key.char
        elif hasattr(key, "name"):
            return key.name
        else:
            return str(key)

    def is_active(self) -> bool:
        """Check if input manager is active."""
        return self._active

    def get_status(self) -> dict:
        """Get input manager status."""
        with self._lock:
            return {
                "active": self._active,
                "event_handlers": len(self._event_handlers),
                "input_mappings": len(self._input_mappings),
                "pressed_buttons": [btn.value for btn in self._pressed_buttons],
                "pressed_keys": list(self._pressed_keys),
            }


# Convenience functions for creating input mappings
def create_mouse_mapping(
    name: str, button: MouseButton, input_type: InputType, handler: Callable, description: str = ""
) -> InputMapping:
    """Create a mouse input mapping."""
    return InputMapping(name=name, input_type=input_type, button=button, handler=handler, description=description)


def create_keyboard_mapping(
    name: str, key: str, input_type: InputType, handler: Callable, description: str = ""
) -> InputMapping:
    """Create a keyboard input mapping."""
    return InputMapping(name=name, input_type=input_type, key=key, handler=handler, description=description)
