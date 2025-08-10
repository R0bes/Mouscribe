# src/input_handler.py - Input event handling for Mauscribe
"""
Input event handling for Mauscribe application.
Manages mouse and keyboard input for recording control.
"""

import time
from typing import Callable, Optional
from pynput import mouse, keyboard

class InputHandler:
    """Handles input events for Mauscribe application."""
    
    def __init__(self):
        """Initialize the input handler."""
        self.mouse_listener: Optional[mouse.Listener] = None
        self.keyboard_listener: Optional[keyboard.Listener] = None
        self.mouse_callback: Optional[Callable] = None
        self.keyboard_callback: Optional[Callable] = None
        
    def setup_mouse_listener(self, callback: Callable):
        """Setup mouse event listener with callback function."""
        self.mouse_callback = callback
        self.mouse_listener = mouse.Listener(
            on_click=self._on_mouse_click
        )
        self.mouse_listener.start()
        print("Mouse listener started")
        
    def setup_keyboard_listener(self, callback: Callable):
        """Setup keyboard event listener with callback function."""
        self.keyboard_callback = callback
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self.keyboard_listener.start()
        print("Keyboard listener started")
        
    def _on_mouse_click(self, x: int, y: int, button, pressed: bool):
        """Handle mouse click events."""
        if self.mouse_callback:
            try:
                self.mouse_callback(x, y, button, pressed)
            except Exception as e:
                print(f"Mouse callback error: {e}")
                
    def _on_key_press(self, key):
        """Handle keyboard key press events."""
        if self.keyboard_callback:
            try:
                self.keyboard_callback(key, True)
            except Exception as e:
                print(f"Keyboard callback error: {e}")
                
    def _on_key_release(self, key):
        """Handle keyboard key release events."""
        if self.keyboard_callback:
            try:
                self.keyboard_callback(key, False)
            except Exception as e:
                print(f"Keyboard callback error: {e}")
                
    def stop(self):
        """Stop all input listeners."""
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
            print("Mouse listener stopped")
            
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
            print("Keyboard listener stopped")
            
    def is_active(self) -> bool:
        """Check if any input listeners are active."""
        return (self.mouse_listener and self.mouse_listener.is_alive()) or \
               (self.keyboard_listener and self.keyboard_listener.is_alive())
