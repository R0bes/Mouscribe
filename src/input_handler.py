# src/input_handler.py - Input event handling for Mauscribe
"""
Input event handling for Mauscribe application.
Manages mouse and keyboard input for recording control.
"""

from typing import Any, Callable, Optional

from pynput import keyboard, mouse

from .logger import get_logger


class InputHandler:
    """Handles input events for Mauscribe application."""

    def __init__(self) -> None:
        """Initialize the input handler."""
        self.logger = get_logger(self.__class__.__name__)
        self.mouse_listener: Optional[mouse.Listener] = None
        self.keyboard_listener: Optional[keyboard.Listener] = None
        self.mouse_callback: Optional[Callable] = None
        self.keyboard_callback: Optional[Callable] = None

    def setup_mouse_listener(self, callback: Callable) -> None:
        """Setup mouse event listener with callback function."""
        try:
            self.mouse_callback = callback
            self.mouse_listener = mouse.Listener(on_click=self._on_mouse_click)
            try:
                self.mouse_listener.start()
                self.logger.debug("Mouse listener started")
            except Exception as e:
                self.logger.error(f"Mouse listener start error: {e}")
                self.mouse_listener = None
                raise
        except Exception as e:
            self.logger.error(f"Mouse listener setup error: {e}")
            self.mouse_listener = None
            raise

    def setup_keyboard_listener(self, callback: Callable) -> None:
        """Setup keyboard event listener with callback function."""
        self.keyboard_callback = callback
        self.keyboard_listener = keyboard.Listener(on_press=self._on_key_press, on_release=self._on_key_release)
        self.keyboard_listener.start()
        self.logger.debug("Keyboard listener started")

    def _on_mouse_click(self, x: int, y: int, button: Any, pressed: bool) -> None:
        """Handle mouse click events."""
        if self.mouse_callback:
            try:
                self.mouse_callback(x, y, button, pressed)
            except Exception as e:
                self.logger.error(f"Mouse callback error: {e}")

    def _on_key_press(self, key: Any) -> None:
        """Handle keyboard key press events."""
        if self.keyboard_callback:
            try:
                self.keyboard_callback(key, True)
            except Exception as e:
                self.logger.error(f"Keyboard callback error: {e}")

    def _on_key_release(self, key: Any) -> None:
        """Handle keyboard key release events."""
        if self.keyboard_callback:
            try:
                self.keyboard_callback(key, False)
            except Exception as e:
                self.logger.error(f"Keyboard callback error: {e}")

    def stop(self) -> None:
        """Stop all input listeners."""
        if self.mouse_listener:
            try:
                self.mouse_listener.stop()
            except Exception as e:
                self.logger.error(f"Mouse listener stop error: {e}")
            finally:
                self.mouse_listener = None
                self.logger.info("Mouse listener stopped")

        if self.keyboard_listener:
            try:
                self.keyboard_listener.stop()
            except Exception as e:
                self.logger.error(f"Keyboard listener stop error: {e}")
            finally:
                self.keyboard_listener = None
                self.logger.info("Keyboard listener stopped")

    def is_active(self) -> bool:
        """Check if any input listeners are active."""
        mouse_active = False
        if self.mouse_listener is not None:
            try:
                mouse_active = self.mouse_listener.is_alive()
            except Exception as e:
                self.logger.error(f"Mouse listener is_alive error: {e}")
                mouse_active = False

        keyboard_active = False
        if self.keyboard_listener is not None:
            try:
                keyboard_active = self.keyboard_listener.is_alive()
            except Exception as e:
                self.logger.error(f"Keyboard listener is_alive error: {e}")
                keyboard_active = False

        return mouse_active or keyboard_active
