# src/input/input_handler.py
"""
Simplified input handling for Mauscribe:
- Direct input processing without complex filtering
- Simple debouncing and callback system
- Clean, maintainable architecture
"""

from __future__ import annotations

import time
from typing import Any, Callable, Optional

from pynput import keyboard, mouse

from ..utils.config import Config
from ..utils.logger import get_logger
from .keys import get_button_mapper


class _Debouncer:
    """Simple per-event debouncer."""

    def __init__(self) -> None:
        self._ts: dict[str, float] = {}

    def hit(self, key: str, window_ms: int) -> bool:
        now = time.time()
        last = self._ts.get(key, 0.0)
        if (now - last) * 1000 < window_ms:
            return True
        self._ts[key] = now
        return False


class InputHandler:
    """
    Simplified input handler:
    - Direct callback system
    - Simple debouncing
    - Clean button mapping
    """

    def __init__(
        self,
        primary_callback: Callable[[bool], None] | None,
        secondary_callback: Callable[[bool], None] | None,
        third_callback: Callable[[bool], None] | None = None,
    ) -> None:
        self.log = get_logger(self.__class__.__name__)
        self.config = Config()
        self.mapper = get_button_mapper(self.config)

        # Direct callbacks
        self.primary_callback = primary_callback
        self.secondary_callback = secondary_callback
        self.third_callback = third_callback

        # Debounce settings
        self._mouse_ms = 200
        self._key_ms = 150
        self._db = _Debouncer()

        # Pynput listeners
        self._ml: mouse.Listener | None = None
        self._kl: keyboard.Listener | None = None
        self._active = False

        # Don't start automatically - will be started by the main app

    def start(self) -> None:
        """Start input listeners."""
        if not self._active:
            self._start()

    def stop(self) -> None:
        """Stop all input listeners."""
        try:
            if self._ml:
                self._ml.stop()
            if self._kl:
                self._kl.stop()
        finally:
            self._ml = None
            self._kl = None
            self._active = False
            self.log.debug("Input listeners stopped")

    def _start(self) -> None:
        """Start input listeners."""
        try:
            self.log.info("🚀 Starting input listeners...")
            self._ml = mouse.Listener(on_click=self._on_mouse_click)
            self._kl = keyboard.Listener(
                on_press=self._on_key_press, on_release=self._on_key_release
            )
            self._ml.start()
            self._kl.start()
            self._active = True
            self.log.info("Input listeners started successfully")
        except Exception as e:
            self.log.error(f"Failed to start listeners: {e}")
            raise

    def _on_mouse_click(self, x: int, y: int, btn: Any, pressed: bool) -> None:
        """Handle mouse click events."""
        try:
            # Debounce check
            if self._db.hit(
                f"mouse:{btn}:{'down' if pressed else 'up'}", self._mouse_ms
            ):
                return

            # Check primary button
            primary_btn = self.mapper.get_primary_mouse_button()
            if btn == primary_btn:
                self._trigger_callback(self.primary_callback, pressed)
                return

            # Check secondary button
            secondary_btn = self.mapper.get_secondary_mouse_button()
            if btn == secondary_btn:
                self._trigger_callback(self.secondary_callback, pressed)
                return

            # Check third button
            third_btn = self.mapper.get_third_mouse_button()
            if btn == third_btn:
                self._trigger_callback(self.third_callback, pressed)
                return

        except Exception as e:
            self.log.error(f"Mouse handler error: {e}")

    def _on_key_press(self, key: Any) -> None:
        """Handle key press events."""
        self._handle_key(key, True)

    def _on_key_release(self, key: Any) -> None:
        """Handle key release events."""
        self._handle_key(key, False)

    def _handle_key(self, key: Any, pressed: bool) -> None:
        """Handle keyboard events."""
        try:
            # Debounce check
            if self._db.hit(f"key:{key}:{'down' if pressed else 'up'}", self._key_ms):
                return

            # Check primary key
            primary_key = self.mapper.get_primary_keyboard_key()
            if key == primary_key:
                self._trigger_callback(self.primary_callback, pressed)
                return

            # Check secondary key
            secondary_key = self.mapper.get_secondary_keyboard_key()
            if key == secondary_key:
                self._trigger_callback(self.secondary_callback, pressed)
                return

            # Check third key
            third_key = self.mapper.get_third_keyboard_key()
            if key == third_key:
                self._trigger_callback(self.third_callback, pressed)
                return

        except Exception as e:
            self.log.error(f"Keyboard handler error: {e}")

    def _trigger_callback(
        self, callback: Callable[[bool], None] | None, pressed: bool
    ) -> None:
        """Safely trigger a callback if it exists."""
        if callback:
            try:
                callback(pressed)
            except Exception as e:
                self.log.error(f"Callback error: {e}")
        else:
            self.log.warning(f"No callback registered for event: pressed={pressed}")

    def is_active(self) -> bool:
        """Check if input handler is active."""
        return self._active
