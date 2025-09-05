"""
Simplified button mapping for Mauscribe.
Maps configuration strings to pynput button types for mouse and keyboard input.
"""

from typing import Optional, Union

from pynput import keyboard, mouse

from ..utils.config import Config


class ButtonMapper:
    """Maps configuration strings to pynput button types."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize button mapper with configuration."""
        self.config = config or Config()

        # Mouse button mapping
        self.mouse_button_map = {
            "m_left": mouse.Button.left,
            "left": mouse.Button.left,
            "m_right": mouse.Button.right,
            "right": mouse.Button.right,
            "m_middle": mouse.Button.middle,
            "middle": mouse.Button.middle,
            "m_x1": mouse.Button.x1,
            "x1": mouse.Button.x1,
            "m_x2": mouse.Button.x2,
            "x2": mouse.Button.x2,
        }

        # Keyboard key mapping
        self.keyboard_key_map = {
            # Function keys
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
            # Modifier keys
            "ctrl": keyboard.Key.ctrl,
            "shift": keyboard.Key.shift,
            "alt": keyboard.Key.alt,
            "cmd": keyboard.Key.cmd,
            # Special keys
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
            # Arrow keys
            "up": keyboard.Key.up,
            "down": keyboard.Key.down,
            "left": keyboard.Key.left,
            "right": keyboard.Key.right,
        }

    def get_mouse_button(self, button_name: str) -> Optional[mouse.Button]:
        """Get mouse button from configuration name."""
        button_name_lower = button_name.lower().strip()
        return self.mouse_button_map.get(button_name_lower)

    def get_keyboard_key(self, key_name: str) -> Optional[Union[keyboard.Key, str]]:
        """Get keyboard key from configuration name."""
        key_name_lower = key_name.lower().strip()

        # Check predefined map first
        if key_name_lower in self.keyboard_key_map:
            return self.keyboard_key_map[key_name_lower]

        # Return regular letters/numbers as strings
        if len(key_name_lower) == 1 and key_name_lower.isalnum():
            return key_name_lower

        return None

    def parse_key_combination(
        self, combination_str: str
    ) -> list[Union[keyboard.Key, str]]:
        """Parse key combination string (e.g., "ctrl+shift+f9")."""
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
                # Add unknown key as string
                keys.append(part)

        return keys

    def get_primary_mouse_button(self) -> Optional[mouse.Button]:
        """Get primary mouse button from configuration."""
        button_name = self.config.primary_name
        return self.get_mouse_button(button_name)

    def get_secondary_mouse_button(self) -> Optional[mouse.Button]:
        """Get secondary mouse button from configuration."""
        button_name = self.config.secondary_name
        return self.get_mouse_button(button_name)

    def get_primary_keyboard_key(self) -> Union[keyboard.Key, str, None]:
        """Get primary keyboard key from configuration."""
        if self.config.primary_type == "keyboard":
            key_name = self.config.primary_name
            return self.get_keyboard_key(key_name)
        return None

    def get_secondary_keyboard_key(self) -> Union[keyboard.Key, str, None]:
        """Get secondary keyboard key from configuration."""
        if self.config.secondary_type == "keyboard":
            key_name = self.config.secondary_name
            return self.get_keyboard_key(key_name)
        return None

    def get_third_mouse_button(self) -> Optional[mouse.Button]:
        """Get third mouse button from configuration."""
        button_name = self.config.third_name
        return self.get_mouse_button(button_name)

    def get_third_keyboard_key(self) -> Union[keyboard.Key, str, None]:
        """Get third keyboard key from configuration."""
        if self.config.third_type == "keyboard":
            key_name = self.config.third_name
            return self.get_keyboard_key(key_name)
        return None

    def is_valid_mouse_button(self, button_name: str) -> bool:
        """Check if mouse button name is valid."""
        return self.get_mouse_button(button_name) is not None

    def is_valid_keyboard_key(self, key_name: str) -> bool:
        """Check if keyboard key name is valid."""
        return self.get_keyboard_key(key_name) is not None

    def get_all_mouse_button_names(self) -> list[str]:
        """Get all available mouse button names."""
        return list(self.mouse_button_map.keys())

    def get_all_keyboard_key_names(self) -> list[str]:
        """Get all available keyboard key names."""
        return list(self.keyboard_key_map.keys())


# Convenience functions
def get_button_mapper(config: Optional[Config] = None) -> ButtonMapper:
    """Get button mapper instance."""
    return ButtonMapper(config)


def get_mouse_button(
    button_name: str, config: Optional[Config] = None
) -> Optional[mouse.Button]:
    """Get mouse button from name."""
    mapper = get_button_mapper(config)
    return mapper.get_mouse_button(button_name)


def get_keyboard_key(
    key_name: str, config: Optional[Config] = None
) -> Union[keyboard.Key, str, None]:
    """Get keyboard key from name."""
    mapper = get_button_mapper(config)
    return mapper.get_keyboard_key(key_name)
