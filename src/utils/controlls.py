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

    def __init__(self, config: Settings, primary_callback: Callable, secondary_callback: Callable):
        """Initialize the controls manager.
        
        Args:
            config: Settings instance with button configuration
            primary_callback: Function to call when primary button is pressed
            secondary_callback: Function to call when secondary button is pressed
        """
        self.config = config
        self.primary_callback = primary_callback
        self.secondary_callback = secondary_callback
        self.logger = get_logger(self.__class__.__name__)
        
        # Get button names from config
        self.primary_button = self.config.primary_name
        self.secondary_button = self.config.secondary_name
        
        # Mouse listener
        self._mouse_listener: Optional[mouse.Listener] = None
        self._active = False
        
        self.logger.info(f"🎮 Simple Controls Manager initialized:")
        self.logger.info(f"   Primary button: {self.primary_button}")
        self.logger.info(f"   Secondary button: {self.secondary_button}")

    def start(self) -> None:
        """Start input listeners."""
        if self._active:
            return
            
        try:
            self._mouse_listener = mouse.Listener(
                on_click=self._on_mouse_click
            )
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
            # Only handle button release (click complete)
            if not pressed:
                button_name = self._get_mouse_button_name(button)
                if button_name:
                    self._handle_button_click(button_name)
        except Exception as e:
            self.logger.error(f"❌ Mouse click handler error: {e}")

    def _get_mouse_button_name(self, button: mouse.Button) -> Optional[str]:
        """Convert mouse button to name."""
        button_map = {
            mouse.Button.left: "left",
            mouse.Button.right: "right", 
            mouse.Button.middle: "middle",
            mouse.Button.x1: "x1",
            mouse.Button.x2: "x2"
        }
        return button_map.get(button)

    def _handle_button_click(self, button_name: str) -> None:
        """Handle button click and call appropriate callback."""
        try:
            if button_name == self.primary_button:
                self.logger.debug(f"🎮 Primary button ({button_name}) clicked")
                self.primary_callback()
            elif button_name == self.secondary_button:
                self.logger.debug(f"🎮 Secondary button ({button_name}) clicked")
                self.secondary_callback()
            else:
                self.logger.debug(f"🎮 Other button ({button_name}) clicked - ignored")
        except Exception as e:
            self.logger.error(f"❌ Button callback error: {e}")

    def is_active(self) -> bool:
        """Check if controls manager is active."""
        return self._active
