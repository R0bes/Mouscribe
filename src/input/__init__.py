# src/input/__init__.py - Input Module for Mauscribe
"""
Input Module für Mauscribe
Enthält das vereinheitlichte Input-Management-System
"""

from .input_manager import (
    InputEvent,
    InputManager,
    InputMapping,
    InputType,
    MouseButton,
    create_keyboard_mapping,
    create_mouse_mapping,
)

__all__ = [
    "InputManager",
    "InputType",
    "MouseButton",
    "InputEvent",
    "InputMapping",
    "create_mouse_mapping",
    "create_keyboard_mapping",
]
