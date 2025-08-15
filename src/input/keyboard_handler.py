# src/keyboard_handler.py - Keyboard event handling for Mauscribe
"""
Keyboard event handling for Mauscribe application.
Manages keyboard input for recording control and shortcuts with debouncing.
"""

import time
from typing import Any, Callable, Dict, Optional

from pynput import keyboard

from ..utils.logger import get_logger
from .keys import get_button_mapper, get_keyboard_key


class KeyboardHandler:
    """Handles keyboard events for Mauscribe application with debouncing."""

    def __init__(self, debounce_time_ms: int = 200) -> None:
        """Initialize the keyboard handler.

        Args:
            debounce_time_ms: Minimum time between events in milliseconds (default: 200ms)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.keyboard_listener: Optional[keyboard.Listener] = None
        self.keyboard_callback: Optional[Callable] = None

        # Debouncing
        self.debounce_time_ms = debounce_time_ms
        self.last_event_time: dict[str, float] = {}
        self.debounce_enabled = True

    def set_debounce_time(self, debounce_time_ms: int) -> None:
        """Set the debounce time for keyboard events.

        Args:
            debounce_time_ms: Minimum time between events in milliseconds
        """
        if debounce_time_ms >= 0:
            self.debounce_time_ms = debounce_time_ms
            self.logger.debug(f"Keyboard debounce time set to {debounce_time_ms}ms")
        else:
            self.logger.warning("Keyboard debounce time cannot be negative")

    def enable_debouncing(self, enabled: bool = True) -> None:
        """Enable or disable debouncing.

        Args:
            enabled: True to enable debouncing, False to disable
        """
        self.debounce_enabled = enabled
        self.logger.debug(f"Keyboard debouncing {'enabled' if enabled else 'disabled'}")

    def _is_debounced(self, key: str, event_type: str) -> bool:
        """Check if an event should be debounced.

        Args:
            key: Keyboard key identifier
            event_type: Type of event ('press' or 'release')

        Returns:
            True if event should be debounced, False otherwise
        """
        if not self.debounce_enabled:
            return False

        current_time = time.time()
        event_key = f"{key}_{event_type}"

        if event_key in self.last_event_time:
            time_since_last = (current_time - self.last_event_time[event_key]) * 1000
            if time_since_last < self.debounce_time_ms:
                self.logger.debug(
                    f"Debounced {event_type} for {key} (time: {time_since_last:.1f}ms)"
                )
                return True

        self.last_event_time[event_key] = current_time
        return False

    def setup_listener(self, callback: Callable) -> None:
        """Setup keyboard event listener with callback function.

        Args:
            callback: Function to call when keyboard events occur
        """
        try:
            self.keyboard_callback = callback
            self.keyboard_listener = keyboard.Listener(
                on_press=self._on_key_press, on_release=self._on_key_release
            )
            try:
                self.keyboard_listener.start()
                self.logger.debug("Keyboard listener started with debouncing")
            except Exception as e:
                self.logger.error(f"Keyboard listener start error: {e}")
                self.keyboard_listener = None
                raise
        except Exception as e:
            self.logger.error(f"Keyboard listener setup error: {e}")
            self.keyboard_listener = None
            raise

    def _on_key_press(self, key: Any) -> None:
        """Handle keyboard key press events with debouncing.

        Args:
            key: Key that was pressed
        """
        if self.keyboard_callback:
            try:
                # Check debouncing
                key_str = str(key)
                if self._is_debounced(key_str, "press"):
                    return

                # Call callback if not debounced
                self.keyboard_callback(key, True)
            except Exception as e:
                self.logger.error(f"Keyboard callback error: {e}")

    def _on_key_release(self, key: Any) -> None:
        """Handle keyboard key release events with debouncing.

        Args:
            key: Key that was released
        """
        if self.keyboard_callback:
            try:
                # Check debouncing
                key_str = str(key)
                if self._is_debounced(key_str, "release"):
                    return

                # Call callback if not debounced
                self.keyboard_callback(key, False)
            except Exception as e:
                self.logger.error(f"Keyboard callback error: {e}")

    def stop(self) -> None:
        """Stop the keyboard listener."""
        if self.keyboard_listener:
            try:
                self.keyboard_listener.stop()
            except Exception as e:
                self.logger.error(f"Keyboard listener stop error: {e}")
            finally:
                self.keyboard_listener = None
                self.logger.info("Keyboard listener stopped")

    def is_active(self) -> bool:
        """Check if the keyboard listener is active.

        Returns:
            True if keyboard listener is active, False otherwise
        """
        if self.keyboard_listener is not None:
            try:
                return self.keyboard_listener.is_alive()
            except Exception as e:
                self.logger.error(f"Keyboard listener is_alive error: {e}")
                return False
        return False

    def get_status(self) -> dict:
        """Get the current status of the keyboard handler.

        Returns:
            Dictionary with status information
        """
        return {
            "active": self.is_active(),
            "listener_initialized": self.keyboard_listener is not None,
            "callback_set": self.keyboard_callback is not None,
            "debouncing_enabled": self.debounce_enabled,
            "debounce_time_ms": self.debounce_time_ms,
            "last_events": len(self.last_event_time),
        }

    def add_hotkey(self, keys: list, callback: Callable) -> None:
        """Add a hotkey combination.

        Args:
            keys: List of keys that form the hotkey combination
            callback: Function to call when hotkey is pressed
        """
        # This is a placeholder for future hotkey functionality
        self.logger.info(f"Hotkey {keys} registered")
        # Implementation would go here for more advanced hotkey handling

    def reset_debounce_timers(self) -> None:
        """Reset all debounce timers."""
        self.last_event_time.clear()
        self.logger.debug("Keyboard debounce timers reset")
