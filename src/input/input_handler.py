# src/input/input_handler.py - Input event handling for Mauscribe
"""
Input event handling for Mauscribe application.
Simple interface with four callback methods for Primary and Secondary key events.
Includes debouncing for stable input handling.
"""

from typing import Any, Callable, Optional

from src.utils.config import Config

from ..utils.logger import get_logger
from .input_filter import InputFilter
from .keyboard_handler import KeyboardHandler
from .keys import get_button_mapper
from .mouse_handler import MouseHandler


class InputHandler:
    """
    Simple input handler interface with four callback methods.

    Provides callbacks for:
    - Primary key press
    - Primary key release
    - Secondary key press
    - Secondary key release

    Includes debouncing for stable input handling.
    """

    def __init__(
        self,
        pk_callback: Optional[Callable[[bool], None]] = None,
        sk_callback: Optional[Callable[[bool], None]] = None,
        mouse_debounce_ms: Optional[int] = None,
        keyboard_debounce_ms: Optional[int] = None,
    ) -> None:
        """Initialize the input handler with separate mouse and keyboard handlers.

        Args:
            pk_press_callback: Callback for primary key press
            pk_release_callback: Callback for primary key release
            sk_press_callback: Callback for secondary key press
            sk_release_callback: Callback for secondary key release
            mouse_debounce_ms: Mouse debounce time in milliseconds (default: 300ms)
            keyboard_debounce_ms: Keyboard debounce time in milliseconds (default: 200ms)
        """
        self.config = Config()
        self.logger = get_logger(self.__class__.__name__)

        # Initialize handlers with debouncing
        self.mouse_handler = MouseHandler(debounce_time_ms=mouse_debounce_ms or 300)
        self.keyboard_handler = KeyboardHandler(debounce_time_ms=keyboard_debounce_ms or 200)

        # Initialize button mapper for configuration-based button handling
        self.button_mapper = get_button_mapper(self.config)

        # Initialize input filter
        self.input_filter = InputFilter(self.config)

        # Set callbacks for the input filter
        if pk_callback and sk_callback:
            self.input_filter.set_callbacks(pk_callback, sk_callback)
        else:
            self.logger.warning("One or both callbacks are None, input filtering disabled")

        # Callback functions (kept for backward compatibility)
        self.primary_callback: Optional[Callable[[bool], None]] = pk_callback
        self.secondary_callback: Optional[Callable[[bool], None]] = sk_callback

        # Start listening
        self._start_listening()

    def set_debounce_times(self, mouse_ms: Optional[int] = None, keyboard_ms: Optional[int] = None) -> None:
        """Set debounce times for input handlers.

        Args:
            mouse_ms: Mouse debounce time in milliseconds
            keyboard_ms: Keyboard debounce time in milliseconds
        """
        if mouse_ms is not None:
            self.mouse_handler.set_debounce_time(mouse_ms)
            self.logger.info(f"Mouse debounce time set to {mouse_ms}ms")

        if keyboard_ms is not None:
            self.keyboard_handler.set_debounce_time(keyboard_ms)
            self.logger.info(f"Keyboard debounce time set to {keyboard_ms}ms")

    def enable_debouncing(self, enabled: bool = True) -> None:
        """Enable or disable debouncing for all input handlers.

        Args:
            enabled: True to enable debouncing, False to disable
        """
        self.mouse_handler.enable_debouncing(enabled)
        self.keyboard_handler.enable_debouncing(enabled)
        self.logger.info(f"Debouncing {'enabled' if enabled else 'disabled'} for all input handlers")

    def reset_debounce_timers(self) -> None:
        """Reset all debounce timers."""
        self.mouse_handler.reset_debounce_timers()
        self.keyboard_handler.reset_debounce_timers()
        self.logger.debug("All debounce timers reset")

    def _start_listening(self) -> None:
        """Start listening for input events."""
        try:
            # Setup mouse listener with our callback handler
            self.mouse_handler.setup_listener(self._handle_mouse_event)

            # Setup keyboard listener with our callback handler
            self.keyboard_handler.setup_listener(self._handle_keyboard_event)

            self.logger.info("Input listeners started successfully with debouncing")
        except Exception as e:
            self.logger.error(f"Failed to start input listeners: {e}")
            raise

    def _handle_mouse_event(self, x: int, y: int, button: Any, pressed: bool) -> None:
        """Handle mouse events and route to appropriate callbacks."""
        try:
            self.logger.debug(f"Mouse event: {x}, {y}, {button}, {pressed}")

            # Get configured mouse buttons using button mapper
            primary_button = self.button_mapper.get_primary_mouse_button()
            secondary_button = self.button_mapper.get_secondary_mouse_button()

            # Check if button matches primary button
            if button == primary_button:
                self.logger.debug(f"Primary mouse button {'pressed' if pressed else 'released'}")
                self.input_filter.process_primary_input(pressed)

            # Check if button matches secondary button
            elif button == secondary_button:
                self.logger.debug(f"Secondary mouse button {'pressed' if pressed else 'released'}")
                self.input_filter.process_secondary_input(pressed)

        except Exception as e:
            self.logger.error(f"Error in mouse event handler: {e}")

    def _handle_keyboard_event(self, key: Any, pressed: bool) -> None:
        """Handle keyboard events and route to appropriate callbacks."""
        try:
            self.logger.debug(f"Keyboard event: {key}, {pressed}")

            # Get configured keyboard keys using button mapper
            primary_key = self.button_mapper.get_primary_keyboard_key()
            secondary_key = self.button_mapper.get_keyboard_key(self.config.keyboard_secondary)

            # Check if key matches primary key
            if key == primary_key:
                self.logger.debug(f"Primary keyboard key {'pressed' if pressed else 'released'}")
                self.input_filter.process_primary_input(pressed)

            # Check if key matches secondary key (for single key)
            elif key == secondary_key:
                self.logger.debug(f"Secondary keyboard key {'pressed' if pressed else 'released'}")
                self.input_filter.process_secondary_input(pressed)

            # TODO: Implement key combination handling for secondary keyboard input
            # This would require tracking multiple key states for combinations like "shift+f9"

        except Exception as e:
            self.logger.error(f"Error in keyboard event handler: {e}")

    def stop(self) -> None:
        """Stop all input listeners."""
        try:
            self.mouse_handler.stop()
            self.keyboard_handler.stop()
            self.input_filter.cleanup()
            self.logger.info("Input listeners stopped")
        except Exception as e:
            self.logger.error(f"Error stopping input listeners: {e}")

    def get_status(self) -> dict:
        """Get the current status of all input handlers.

        Returns:
            Dictionary with status information including debouncing details
        """
        return {
            "mouse_handler": self.mouse_handler.get_status(),
            "keyboard_handler": self.keyboard_handler.get_status(),
            "callbacks": {
                "primary_callback": self.primary_callback is not None,
                "secondary_callback": self.secondary_callback is not None,
            },
            "button_mapper": {
                "primary_mouse_button": str(self.button_mapper.get_primary_mouse_button()),
                "secondary_mouse_button": str(self.button_mapper.get_secondary_mouse_button()),
                "primary_keyboard_key": str(self.button_mapper.get_primary_keyboard_key()),
                "secondary_keyboard_key": str(self.button_mapper.get_keyboard_key(self.config.keyboard_secondary)),
            },
        }
