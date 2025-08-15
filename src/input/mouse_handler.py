# src/mouse_handler.py - Mouse event handling for Mauscribe
"""
Mouse event handling for Mauscribe application.
Manages mouse input for recording control with debouncing.
"""

import time
from typing import Any, Callable, Dict, Optional

from pynput import mouse

from ..utils.logger import get_logger
from .keys import get_mouse_button


class MouseHandler:
    """Handles mouse events for Mauscribe application with debouncing."""

    def __init__(self, debounce_time_ms: int = 300) -> None:
        """Initialize the mouse handler.

        Args:
            debounce_time_ms: Minimum time between events in milliseconds (default: 300ms)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.mouse_listener: Optional[mouse.Listener] = None
        self.mouse_callback: Optional[Callable] = None

        # Debouncing
        self.debounce_time_ms = debounce_time_ms
        self.last_event_time: dict[str, float] = {}
        self.debounce_enabled = True

    def set_debounce_time(self, debounce_time_ms: int) -> None:
        """Set the debounce time for mouse events.

        Args:
            debounce_time_ms: Minimum time between events in milliseconds
        """
        if debounce_time_ms >= 0:
            self.debounce_time_ms = debounce_time_ms
            self.logger.debug(f"Debounce time set to {debounce_time_ms}ms")
        else:
            self.logger.warning("Debounce time cannot be negative")

    def enable_debouncing(self, enabled: bool = True) -> None:
        """Enable or disable debouncing.

        Args:
            enabled: True to enable debouncing, False to disable
        """
        self.debounce_enabled = enabled
        self.logger.debug(f"Debouncing {'enabled' if enabled else 'disabled'}")

    def _is_debounced(self, button: str, event_type: str) -> bool:
        """Check if an event should be debounced.

        Args:
            button: Mouse button identifier
            event_type: Type of event ('press' or 'release')

        Returns:
            True if event should be debounced, False otherwise
        """
        if not self.debounce_enabled:
            return False

        current_time = time.time()
        event_key = f"{button}_{event_type}"

        if event_key in self.last_event_time:
            time_since_last = (current_time - self.last_event_time[event_key]) * 1000
            if time_since_last < self.debounce_time_ms:
                self.logger.debug(
                    f"Debounced {event_type} for {button} (time: {time_since_last:.1f}ms)"
                )
                return True

        self.last_event_time[event_key] = current_time
        return False

    def setup_listener(self, callback: Callable) -> None:
        """Setup mouse event listener with callback function.

        Args:
            callback: Function to call when mouse events occur
        """
        try:
            self.mouse_callback = callback
            self.mouse_listener = mouse.Listener(on_click=self._on_mouse_click)
            try:
                self.mouse_listener.start()
                self.logger.debug("Mouse listener started with debouncing")
            except Exception as e:
                self.logger.error(f"Mouse listener start error: {e}")
                self.mouse_listener = None
                raise
        except Exception as e:
            self.logger.error(f"Mouse listener setup error: {e}")
            self.mouse_listener = None
            raise

    def _on_mouse_click(self, x: int, y: int, button: Any, pressed: bool) -> None:
        """Handle mouse click events with debouncing.

        Args:
            x: X coordinate of the click
            y: Y coordinate of the click
            button: Mouse button that was clicked
            pressed: True if button was pressed, False if released
        """
        if self.mouse_callback:
            try:
                # Check debouncing
                button_str = str(button)
                event_type = "press" if pressed else "release"
                if self._is_debounced(button_str, event_type):
                    return

                # Call callback if not debounced
                self.mouse_callback(x, y, button, pressed)

            except Exception as e:
                self.logger.error(f"Mouse callback error: {e}")

    def stop(self) -> None:
        """Stop the mouse listener."""
        if self.mouse_listener:
            try:
                self.mouse_listener.stop()
            except Exception as e:
                self.logger.error(f"Mouse listener stop error: {e}")
            finally:
                self.mouse_listener = None
                self.logger.info("Mouse listener stopped")

    def is_active(self) -> bool:
        """Check if the mouse listener is active.

        Returns:
            True if mouse listener is active, False otherwise
        """
        if self.mouse_listener is not None:
            try:
                return self.mouse_listener.is_alive()
            except Exception as e:
                self.logger.error(f"Mouse listener is_alive error: {e}")
                return False
        return False

    def get_status(self) -> dict:
        """Get the current status of the mouse handler.

        Returns:
            Dictionary with status information
        """
        return {
            "active": self.is_active(),
            "listener_initialized": self.mouse_listener is not None,
            "callback_set": self.mouse_callback is not None,
            "debouncing_enabled": self.debounce_enabled,
            "debounce_time_ms": self.debounce_time_ms,
            "last_events": len(self.last_event_time),
        }

    def reset_debounce_timers(self) -> None:
        """Reset all debounce timers."""
        self.last_event_time.clear()
        self.logger.debug("Debounce timers reset")
