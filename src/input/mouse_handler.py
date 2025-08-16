

from __future__ import annotations
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from pynput import mouse

# --- Configuration hooks (replace with your own config/logger if needed) ---
DEFAULT_DEBOUNCE_MS = 150
DEFAULT_HOLD_MS = 500
DEFAULT_DOUBLE_CLICK_MS = 300

def get_logger(name: str):
    # Minimal stand-in logger; replace with your logger
    import logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    return logging.getLogger(name)
# ---------------------------------------------------------------------------

logger = get_logger(__name__)


class MouseButtonMapping(Enum):
    """Public mapping to make button selection explicit and type-safe."""
    M_LEFT = mouse.Button.left
    M_RIGHT = mouse.Button.right
    M_MIDDLE = mouse.Button.middle
    M_X1 = mouse.Button.x1
    M_X2 = mouse.Button.x2


class MouseButtonFilter(Enum):
    PRESS = "press"            # fires on press
    RELEASE = "release"        # fires on release
    HOLD = "hold"              # fires when press duration >= hold_threshold_ms (on release)
    DOUBLE_CLICK = "double_click"  # two presses within double_click_ms
    SMART = "smart"            # short press -> PRESS, long press -> HOLD (on release)


@dataclass
class MouseButtonHandler:
    """Single rule: which button + which filter + which callback."""
    button: MouseButtonMapping
    filter: MouseButtonFilter
    callback: Callable[[int, int, Any, bool, Dict[str, Any]], None]

    # Internal timing state
    last_down_ts: float = 0.0
    last_up_ts: float = 0.0
    last_click_ts: float = 0.0
    click_count: int = 0

    # Per-handler settings (can be overridden when registering)
    debounce_ms: int = DEFAULT_DEBOUNCE_MS
    hold_threshold_ms: int = DEFAULT_HOLD_MS
    double_click_ms: int = DEFAULT_DOUBLE_CLICK_MS

    # Internal debounce store: event_key -> ts
    last_event_ts: Dict[str, float] = field(default_factory=dict)

    def _debounced(self, key: str) -> bool:
        now = time.time()
        last = self.last_event_ts.get(key, 0.0)
        if (now - last) * 1000 < self.debounce_ms:
            return True
        self.last_event_ts[key] = now
        return False

    def on_press(self, x: int, y: int) -> Optional[Dict[str, Any]]:
        now = time.time()
        self.last_down_ts = now

        # double click window tracking (count presses)
        if (now - self.last_click_ts) * 1000 <= self.double_click_ms:
            self.click_count += 1
        else:
            self.click_count = 1
        self.last_click_ts = now

        meta = {"x": x, "y": y, "button": self.button.value, "event": "press", "ts": now}

        if self.filter == MouseButtonFilter.PRESS:
            if self._debounced("press"):
                return None
            return meta

        if self.filter == MouseButtonFilter.DOUBLE_CLICK:
            # Trigger only on the second (or even) press inside window
            if self.click_count >= 2:
                if self._debounced("double_click"):
                    return None
                return {**meta, "event": "double_click", "click_count": self.click_count}

        # For HOLD/RELEASE/SMART we decide on release
        return None

    def on_release(self, x: int, y: int) -> Optional[Dict[str, Any]]:
        now = time.time()
        self.last_up_ts = now
        press_ms = int((self.last_up_ts - self.last_down_ts) * 1000)
        meta = {
            "x": x, "y": y, "button": self.button.value, "event": "release", "ts": now,
            "press_duration_ms": press_ms
        }

        if self.filter == MouseButtonFilter.RELEASE:
            if self._debounced("release"):
                return None
            return meta

        if self.filter == MouseButtonFilter.HOLD:
            if press_ms >= self.hold_threshold_ms:
                if self._debounced("hold"):
                    return None
                return {**meta, "event": "hold"}
            return None

        if self.filter == MouseButtonFilter.SMART:
            # Short -> PRESS, Long -> HOLD (both decided on release)
            if self._debounced("smart"):
                return None
            if press_ms >= self.hold_threshold_ms:
                return {**meta, "event": "hold"}
            else:
                return {**meta, "event": "press"}

        # DOUBLE_CLICK is handled on press; nothing to do here
        return None


class MouseHandler:
    """Central mouse listener that dispatches events to registered handlers."""

    def __init__(
        self,
        debounce_ms: int = DEFAULT_DEBOUNCE_MS,
        hold_threshold_ms: int = DEFAULT_HOLD_MS,
        double_click_ms: int = DEFAULT_DOUBLE_CLICK_MS,
    ) -> None:
        self.logger = get_logger(self.__class__.__name__)
        self.handlers: List[MouseButtonHandler] = []

        self.default_debounce_ms = debounce_ms
        self.default_hold_ms = hold_threshold_ms
        self.default_double_click_ms = double_click_ms

        self._listener: Optional[mouse.Listener] = None
        self._active = False

    def register_handler(
        self,
        button: MouseButtonMapping,
        event_filter: MouseButtonFilter,
        callback: Callable[[int, int, Any, bool, Dict[str, Any]], None],
        *,
        debounce_ms: Optional[int] = None,
        hold_threshold_ms: Optional[int] = None,
        double_click_ms: Optional[int] = None,
    ) -> None:
        """Register a handler for a specific button + filter."""
        h = MouseButtonHandler(
            button=button,
            filter=event_filter,
            callback=callback,
            debounce_ms=debounce_ms if debounce_ms is not None else self.default_debounce_ms,
            hold_threshold_ms=hold_threshold_ms if hold_threshold_ms is not None else self.default_hold_ms,
            double_click_ms=double_click_ms if double_click_ms is not None else self.default_double_click_ms,
        )
        self.handlers.append(h)
        self.logger.info(f"Registered handler: {button.name} - {event_filter.value}")

    def _dispatch_press(self, x: int, y: int, btn: Any) -> None:
        for h in self.handlers:
            if btn == h.button.value:
                meta = h.on_press(x, y)
                if meta is not None:
                    # pressed=True for PRESS/DOUBLE_CLICK events decided on press
                    try:
                        h.callback(x, y, btn, True, meta)
                    except Exception as e:
                        self.logger.exception(f"Handler press callback error: {e}")

    def _dispatch_release(self, x: int, y: int, btn: Any) -> None:
        for h in self.handlers:
            if btn == h.button.value:
                meta = h.on_release(x, y)
                if meta is not None:
                    # pressed=False for events decided on release (RELEASE/HOLD/SMART)
                    try:
                        h.callback(x, y, btn, False, meta)
                    except Exception as e:
                        self.logger.exception(f"Handler release callback error: {e}")

    def _on_click(self, x: int, y: int, button: Any, pressed: bool) -> None:
        try:
            if pressed:
                self._dispatch_press(x, y, button)
            else:
                self._dispatch_release(x, y, button)
        except Exception as e:
            self.logger.exception(f"Dispatch error: {e}")

    def start(self) -> None:
        if self._active:
            return
        self._listener = mouse.Listener(on_click=self._on_click)
        self._listener.start()
        self._active = True
        self.logger.info("Mouse listener started")

    def stop(self) -> None:
        if not self._active:
            return
        try:
            if self._listener:
                self._listener.stop()
        finally:
            self._listener = None
            self._active = False
            self.logger.info("Mouse listener stopped")

    def is_active(self) -> bool:
        return self._active and self._lis