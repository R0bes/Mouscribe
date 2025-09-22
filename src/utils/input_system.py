#!/usr/bin/env python3
"""
Neues Input-System für Mauscribe
Flexible Definition von Inputs und Commands
"""

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, List, Optional, Union

from pynput import keyboard, mouse


class InputType(Enum):
    """Typen von Eingaben."""

    KEYBOARD = "keyboard"
    MOUSE = "mouse"
    OTHER = "other"


class ActionType(Enum):
    """Aktionen für Eingaben."""

    PRESS = "press"  # Drücken
    RELEASE = "release"  # Loslassen
    CLICK = "click"  # Klick (press + release)
    DOUBLE_CLICK = "double_click"  # Doppelklick
    HOLD = "hold"  # Halten
    SCROLL = "scroll"  # Scrollen


@dataclass
class Input:
    """Einzelne Eingabe."""

    name: str  # Name der Eingabe (z.B. "x2", "ctrl+v", "left")
    input_type: InputType  # Typ der Eingabe
    action: ActionType  # Aktion
    key_code: Optional[str] = None  # Tastatur-Code
    button: Optional[mouse.Button] = None  # Maus-Button

    def __str__(self) -> str:
        return f"{self.name} ({self.action.value})"


@dataclass
class Command:
    """Command bestehend aus einem oder zwei Inputs."""

    name: str  # Name des Commands
    inputs: list[Input]  # Liste der Inputs (1-2)
    callback: Callable  # Callback-Funktion
    description: str = ""  # Beschreibung

    def __str__(self) -> str:
        input_str = " + ".join(str(inp) for inp in self.inputs)
        return f"{self.name}: {input_str}"


class InputSystem:
    """Neues Input-System für Mauscribe."""

    def __init__(self):
        self.commands: dict[str, Command] = {}
        self._mouse_listener: Optional[mouse.Listener] = None
        self._keyboard_listener: Optional[keyboard.Listener] = None
        self._active = False

        # State tracking für Kombinationen
        self._pressed_keys: set = set()
        self._pressed_buttons: set = set()
        self._combination_state: dict[str, bool] = {}

    def add_command(self, command: Command) -> None:
        """Füge Command hinzu."""
        self.commands[command.name] = command

    def remove_command(self, name: str) -> None:
        """Entferne Command."""
        if name in self.commands:
            del self.commands[name]

    def start(self) -> None:
        """Starte Input-System."""
        if self._active:
            return

        self._active = True

        # Starte Mouse Listener
        self._mouse_listener = mouse.Listener(on_click=self._on_mouse_click, on_scroll=self._on_mouse_scroll)
        self._mouse_listener.start()

        # Starte Keyboard Listener
        self._keyboard_listener = keyboard.Listener(on_press=self._on_key_press, on_release=self._on_key_release)
        self._keyboard_listener.start()

    def stop(self) -> None:
        """Stoppe Input-System."""
        self._active = False

        if self._mouse_listener:
            self._mouse_listener.stop()
            self._mouse_listener = None

        if self._keyboard_listener:
            self._keyboard_listener.stop()
            self._keyboard_listener = None

    def _on_mouse_click(self, x: int, y: int, button: mouse.Button, pressed: bool) -> None:
        """Behandle Maus-Klicks."""
        try:
            # Aktualisiere Button-State
            if pressed:
                self._pressed_buttons.add(button)
            else:
                self._pressed_buttons.discard(button)

            # Prüfe Commands
            self._check_commands(InputType.MOUSE, button, ActionType.PRESS if pressed else ActionType.RELEASE)

        except Exception as e:
            print(f"Mouse click error: {e}")

    def _on_mouse_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
        """Behandle Maus-Scroll."""
        try:
            self._check_commands(InputType.MOUSE, None, ActionType.SCROLL)
        except Exception as e:
            print(f"Mouse scroll error: {e}")

    def _on_key_press(self, key) -> None:
        """Behandle Tastatur-Druck."""
        try:
            key_str = self._key_to_string(key)
            self._pressed_keys.add(key_str)
            self._check_commands(InputType.KEYBOARD, key_str, ActionType.PRESS)
        except Exception as e:
            print(f"Key press error: {e}")

    def _on_key_release(self, key) -> None:
        """Behandle Tastatur-Loslassen."""
        try:
            key_str = self._key_to_string(key)
            self._pressed_keys.discard(key_str)
            self._check_commands(InputType.KEYBOARD, key_str, ActionType.RELEASE)
        except Exception as e:
            print(f"Key release error: {e}")

    def _key_to_string(self, key) -> str:
        """Konvertiere Key zu String."""
        if hasattr(key, "char") and key.char:
            return key.char
        elif hasattr(key, "name"):
            return key.name
        else:
            return str(key)

    def _check_commands(self, input_type: InputType, input_value, action: ActionType) -> None:
        """Prüfe alle Commands auf Übereinstimmung."""
        for command in self.commands.values():
            if self._matches_command(command, input_type, input_value, action):
                try:
                    command.callback()
                except Exception as e:
                    print(f"Command callback error: {e}")

    def _matches_command(self, command: Command, input_type: InputType, input_value, action: ActionType) -> bool:
        """Prüfe ob Command mit aktueller Eingabe übereinstimmt."""
        for input_def in command.inputs:
            if not self._matches_input(input_def, input_type, input_value, action):
                return False
        return True

    def _matches_input(self, input_def: Input, input_type: InputType, input_value, action: ActionType) -> bool:
        """Prüfe ob Input-Definition mit aktueller Eingabe übereinstimmt."""
        # Typ muss übereinstimmen
        if input_def.input_type != input_type:
            return False

        # Aktion muss übereinstimmen
        if input_def.action != action:
            return False

        # Wert muss übereinstimmen
        if input_type == InputType.MOUSE:
            return input_def.button == input_value
        elif input_type == InputType.KEYBOARD:
            return input_def.key_code == str(input_value)

        return False

    def get_status(self) -> dict:
        """Gib Status des Input-Systems zurück."""
        return {
            "active": self._active,
            "commands": len(self.commands),
            "pressed_keys": list(self._pressed_keys),
            "pressed_buttons": [str(btn) for btn in self._pressed_buttons],
        }


# Vordefinierte Input-Definitionen
def create_mouse_input(name: str, button: mouse.Button, action: ActionType) -> Input:
    """Erstelle Maus-Input."""
    return Input(name=name, input_type=InputType.MOUSE, action=action, button=button)


def create_keyboard_input(name: str, key_code: str, action: ActionType) -> Input:
    """Erstelle Tastatur-Input."""
    return Input(name=name, input_type=InputType.KEYBOARD, action=action, key_code=key_code)


# Beispiel-Commands
def create_recording_command(callback: Callable) -> Command:
    """Erstelle Recording-Command (X2-Klick)."""
    return Command(
        name="recording",
        inputs=[create_mouse_input("x2", mouse.Button.x2, ActionType.CLICK)],
        callback=callback,
        description="Aufnahme starten/stoppen",
    )


def create_insert_command(callback: Callable) -> Command:
    """Erstelle Insert-Command (Linke Maus halten + X2 drücken)."""
    return Command(
        name="insert",
        inputs=[
            create_mouse_input("left", mouse.Button.left, ActionType.HOLD),
            create_mouse_input("x2", mouse.Button.x2, ActionType.PRESS),
        ],
        callback=callback,
        description="Text einfügen",
    )


def create_paste_command(callback: Callable) -> Command:
    """Erstelle Paste-Command (Ctrl+V)."""
    return Command(
        name="paste",
        inputs=[create_keyboard_input("ctrl+v", "ctrl+v", ActionType.CLICK)],
        callback=callback,
        description="Text einfügen",
    )
