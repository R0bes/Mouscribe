"""
Button type mapping and configuration integration for Mauscribe.
Maps configuration strings to pynput button types for mouse and keyboard input.
"""

from typing import Optional, Union

from pynput import keyboard, mouse

from ..utils.config import Config


class ButtonMapper:
    """Maps configuration strings to pynput button types."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize button mapper with configuration.

        Args:
            config: Configuration instance, uses default if None
        """
        self.config = config or Config()

        # Mouse button mapping
        self.mouse_button_map = {
            "left": mouse.Button.left,
            "right": mouse.Button.right,
            "middle": mouse.Button.middle,
            "x1": mouse.Button.x1,
            "x2": mouse.Button.x2,
            "button8": mouse.Button.x1,  # Alternative Namen
            "button9": mouse.Button.x2,
            "side1": mouse.Button.x1,
            "side2": mouse.Button.x2,
            "back": mouse.Button.x1,  # Browser-Navigation
            "forward": mouse.Button.x2,
        }

        # Keyboard key mapping
        self.keyboard_key_map = {
            # Funktionstasten
            "f1": keyboard.Key.f1,
            "f2": keyboard.Key.f2,
            "f3": keyboard.Key.f3,
            "f4": keyboard.Key.f4,
            "f5": keyboard.Key.f5,
            "f6": keyboard.Key.f6,
            "f7": keyboard.Key.f7,
            "f8": keyboard.Key.f8,
            "f9": keyboard.Key.f9,
            "f10": keyboard.Key.f10,
            "f11": keyboard.Key.f11,
            "f12": keyboard.Key.f12,
            # Modifier-Tasten
            "ctrl": keyboard.Key.ctrl,
            "shift": keyboard.Key.shift,
            "alt": keyboard.Key.alt,
            "cmd": keyboard.Key.cmd,  # Windows-Key auf Windows
            # Spezielle Tasten
            "space": keyboard.Key.space,
            "enter": keyboard.Key.enter,
            "esc": keyboard.Key.esc,
            "tab": keyboard.Key.tab,
            "backspace": keyboard.Key.backspace,
            "delete": keyboard.Key.delete,
            "insert": keyboard.Key.insert,
            "home": keyboard.Key.home,
            "end": keyboard.Key.end,
            "page_up": keyboard.Key.page_up,
            "page_down": keyboard.Key.page_down,
            # Pfeiltasten
            "up": keyboard.Key.up,
            "down": keyboard.Key.down,
            "left": keyboard.Key.left,
            "right": keyboard.Key.right,
        }

    def get_mouse_button(self, button_name: str) -> Optional[mouse.Button]:
        """Get mouse button from configuration name.

        Args:
            button_name: Button name from configuration (e.g., "x1", "x2")

        Returns:
            pynput mouse.Button or None if not found
        """
        button_name_lower = button_name.lower().strip()
        return self.mouse_button_map.get(button_name_lower)

    def get_keyboard_key(self, key_name: str) -> Optional[Union[keyboard.Key, str]]:
        """Get keyboard key from configuration name.

        Args:
            key_name: Key name from configuration (e.g., "f9", "ctrl")

        Returns:
            pynput keyboard.Key, string for regular keys, or None if not found
        """
        key_name_lower = key_name.lower().strip()

        # Zuerst in der vordefinierten Map suchen
        if key_name_lower in self.keyboard_key_map:
            return self.keyboard_key_map[key_name_lower]

        # Für reguläre Buchstaben/Zahlen als String zurückgeben
        if len(key_name_lower) == 1 and key_name_lower.isalnum():
            return key_name_lower

        return None

    def parse_key_combination(self, combination_str: str) -> list[Union[keyboard.Key, str]]:
        """Parse key combination string (e.g., "ctrl+shift+f9").

        Args:
            combination_str: Key combination string

        Returns:
            List of keyboard keys
        """
        if not combination_str:
            return []

        keys = []
        parts = combination_str.lower().split("+")

        for part in parts:
            part = part.strip()
            key = self.get_keyboard_key(part)
            if key is not None:
                keys.append(key)
            else:
                # Unbekannte Taste als String hinzufügen
                keys.append(part)

        return keys

    def get_primary_mouse_button(self) -> Optional[mouse.Button]:
        """Get primary mouse button from configuration."""
        button_name = self.config.mouse_button_primary
        return self.get_mouse_button(button_name)

    def get_secondary_mouse_button(self) -> Optional[mouse.Button]:
        """Get secondary mouse button from configuration."""
        button_name = self.config.mouse_button_secondary
        return self.get_mouse_button(button_name)

    def get_primary_keyboard_key(self) -> Union[keyboard.Key, str, None]:
        """Get primary keyboard key from configuration."""
        key_name = self.config.keyboard_primary
        return self.get_keyboard_key(key_name)

    def get_secondary_keyboard_key(self) -> Union[keyboard.Key, str, None]:
        """Get secondary keyboard key from configuration."""
        key_name = self.config.keyboard_secondary
        return self.get_keyboard_key(key_name)

    def get_secondary_keyboard_combination(self) -> list[Union[keyboard.Key, str]]:
        """Get secondary keyboard combination from configuration."""
        key_name = self.config.keyboard_secondary
        return self.parse_key_combination(key_name)

    def is_valid_mouse_button(self, button_name: str) -> bool:
        """Check if mouse button name is valid.

        Args:
            button_name: Button name to validate

        Returns:
            True if valid, False otherwise
        """
        return self.get_mouse_button(button_name) is not None

    def is_valid_keyboard_key(self, key_name: str) -> bool:
        """Check if keyboard key name is valid.

        Args:
            key_name: Key name to validate

        Returns:
            True if valid, False otherwise
        """
        return self.get_keyboard_key(key_name) is not None

    def get_all_mouse_button_names(self) -> list[str]:
        """Get all available mouse button names.

        Returns:
            List of all available mouse button names
        """
        return list(self.mouse_button_map.keys())

    def get_all_keyboard_key_names(self) -> list[str]:
        """Get all available keyboard key names.

        Returns:
            List of all available keyboard key names
        """
        return list(self.keyboard_key_map.keys())


# Convenience functions for easy access
def get_button_mapper(config: Optional[Config] = None) -> ButtonMapper:
    """Get button mapper instance.

    Args:
        config: Configuration instance, uses default if None

    Returns:
        ButtonMapper instance
    """
    return ButtonMapper(config)


def get_mouse_button(button_name: str, config: Optional[Config] = None) -> Optional[mouse.Button]:
    """Get mouse button from name.

    Args:
        button_name: Button name from configuration
        config: Configuration instance, uses default if None

    Returns:
        pynput mouse.Button or None if not found
    """
    mapper = get_button_mapper(config)
    return mapper.get_mouse_button(button_name)


def get_keyboard_key(key_name: str, config: Optional[Config] = None) -> Union[keyboard.Key, str, None]:
    """Get keyboard key from name.

    Args:
        key_name: Key name from configuration
        config: Configuration instance, uses default if None

    Returns:
        pynput keyboard.Key, string for regular keys, or None if not found
    """
    mapper = get_button_mapper(config)
    return mapper.get_keyboard_key(key_name)
