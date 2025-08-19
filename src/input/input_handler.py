# src/input/input_handler.py
"""
Unified input handling for Mauscribe:
- Primary / Secondary callbacks with pressed: bool
- Mouse + Keyboard with always-on debouncing
- Uses Config, ButtonMapper, and InputFilter
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, Optional

from pynput import keyboard, mouse

from ..utils.config import Config
from ..utils.logger import get_logger
from .input_filter import InputFilter
from .keys import get_button_mapper


class _Debouncer:
    """Minimal per-event debouncer (always enabled)."""

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
    App-facing interface:
        - pk_callback(pressed: bool)
        - sk_callback(pressed: bool)
    Debouncing is always on.
    """

    def __init__(
        self,
        pk_callback: Callable[[bool], None] | None,
        sk_callback: Callable[[bool], None] | None,
    ) -> None:
        self.log = get_logger(self.__class__.__name__)
        self.config = Config()
        self.mapper = get_button_mapper(self.config)

        # App-level callbacks via InputFilter
        self.primary_callback = pk_callback
        self.secondary_callback = sk_callback

        self.filter = InputFilter(self.config)
        self.filter.set_callbacks(pk_callback, sk_callback)

        # Debounce windows (fixed; always enabled)
        self._mouse_ms = 300
        self._key_ms = 200
        self._db = _Debouncer()

        # Pynput listeners
        self._ml: mouse.Listener | None = None
        self._kl: keyboard.Listener | None = None
        self._active = False

        self._start()

    # -------- lifecycle --------

    def stop(self) -> None:
        try:
            if self._ml:
                self._ml.stop()
            if self._kl:
                self._kl.stop()
            self.filter.cleanup()
        finally:
            self._ml = None
            self._kl = None
            self._active = False
            self.log.debug("Input listeners stopped")

    # -------- internals --------

    def _start(self) -> None:
        try:
            self._ml = mouse.Listener(on_click=self._on_mouse_click)
            self._kl = keyboard.Listener(on_press=self._on_key_press, on_release=self._on_key_release)
            self._ml.start()
            self._kl.start()
            self._active = True
        except Exception as e:
            self.log.error(f"Failed to start listeners: {e}")
            raise

    def _on_mouse_click(self, x: int, y: int, btn: Any, pressed: bool) -> None:
        try:
            if self._db.hit(f"mouse:{btn}:{'down' if pressed else 'up'}", self._mouse_ms):
                return

            if btn == self.mapper.get_primary_mouse_button():
                self.filter.process_primary_input(pressed)
            elif btn == self.mapper.get_secondary_mouse_button():
                self.filter.process_secondary_input(pressed)
        except Exception as e:
            self.log.error(f"Mouse handler error: {e}")

    def _on_key_press(self, key: Any) -> None:
        self._handle_key(key, True)

    def _on_key_release(self, key: Any) -> None:
        self._handle_key(key, False)

    def _handle_key(self, key: Any, pressed: bool) -> None:
        try:
            if self._db.hit(f"key:{key}:{'down' if pressed else 'up'}", self._key_ms):
                return

            primary_key = self.mapper.get_primary_keyboard_key()
            secondary_key = self.mapper.get_keyboard_key(self.config.keyboard_secondary)

            if key == primary_key:
                self.filter.process_primary_input(pressed)
            elif key == secondary_key:
                self.filter.process_secondary_input(pressed)
            # Key chords can be added in InputFilter if needed.
        except Exception as e:
            self.log.error(f"Keyboard handler error: {e}")
