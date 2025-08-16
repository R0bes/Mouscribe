"""
Input handling package for Mauscribe.

This package contains:
- keyboard_handler: Keyboard event handling
- mouse_handler: Mouse event handling
- input_handler: Main input interface with four callback methods
"""

from .input_handler import InputHandler
from .keyboard_handler import KeyboardHandler
from .mouse_handler import MouseHandler

__all__ = ["KeyboardHandler", "MouseHandler", "InputHandler"]
