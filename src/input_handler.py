# src/input_handler.py
from __future__ import annotations

import threading
import time
from typing import Callable, Dict, List, Optional, Tuple, Union

from pynput import keyboard, mouse

from . import config


class InputHandler:
    """Erweiterter Input-Handler für verschiedene Eingabemethoden"""
    
    def __init__(self, on_start: Callable, on_stop: Callable) -> None:
        self.on_start = on_start
        self.on_stop = on_stop
        self._is_recording = False
        self._lock = threading.Lock()
        self._active_modifiers: set = set()
        self._keyboard_listener: Optional[keyboard.Listener] = None
        self._mouse_listener: Optional[mouse.Listener] = None
        self._start_time = 0
        
        # Input-Konfiguration laden
        self._setup_input_config()
        
    def _setup_input_config(self) -> None:
        """Lädt die aktive Input-Konfiguration"""
        self.input_config = config.ACTIVE_INPUT_CONFIG
        self.input_method = config.INPUT_METHOD
        
        if self.input_method == "mouse_button":
            self._setup_mouse_input()
        elif self.input_method == "keyboard":
            self._setup_keyboard_input()
        elif self.input_method == "custom":
            self._setup_custom_input()
        else:
            # Fallback auf mouse_button
            self.input_config = config.PUSH_TO_TALK_CONFIG["mouse_button"]
            self._setup_mouse_input()
    
    def _setup_mouse_input(self) -> None:
        """Konfiguriert Maus-Input"""
        self.mouse_buttons = {
            "primary": getattr(mouse.Button, self.input_config["primary"]),
            "secondary": getattr(mouse.Button, self.input_config["secondary"])
        }
        
        # Modifier-Kombinationen
        self.modifier_combinations = []
        if self.input_config.get("left_with_ctrl"):
            self.modifier_combinations.append(("ctrl", mouse.Button.left))
        if self.input_config.get("right_with_ctrl"):
            self.modifier_combinations.append(("ctrl", mouse.Button.right))
        if self.input_config.get("middle_with_ctrl"):
            self.modifier_combinations.append(("ctrl", mouse.Button.middle))
    
    def _setup_keyboard_input(self) -> None:
        """Konfiguriert Tastatur-Input"""
        self.keyboard_keys = {
            "primary": getattr(keyboard.Key, self.input_config["primary"]),
            "secondary": getattr(keyboard.Key, self.input_config["secondary"])
        }
        
        # Modifier
        self.modifier_key = getattr(keyboard.Key, self.input_config["modifier"])
        
        # Kombinationen
        self.keyboard_combinations = []
        for combo in self.input_config["combinations"]:
            modifier, key = combo
            self.keyboard_combinations.append((
                getattr(keyboard.Key, modifier),
                getattr(keyboard.Key, key)
            ))
    
    def _setup_custom_input(self) -> None:
        """Konfiguriert Custom-Input"""
        self.custom_combinations = []
        for combo in self.input_config["combinations"]:
            modifier, key = combo
            mod_key = getattr(keyboard.Key, modifier)
            
            # Prüfe ob es eine Maus-Taste ist
            try:
                key_obj = getattr(mouse.Button, key)
            except AttributeError:
                key_obj = getattr(keyboard.Key, key)
            
            self.custom_combinations.append((mod_key, key_obj))
    
    def _on_mouse_click(self, x: int, y: int, button: mouse.Button, pressed: bool) -> bool:
        """Maus-Click Handler"""
        # Zusätzlicher Callback für Doppelklick-Funktionalität
        if hasattr(self, '_mouse_click_callback'):
            try:
                self._mouse_click_callback(x, y, button, pressed)
            except Exception:
                pass
        
        if pressed and not self._is_recording:
            # Prüfe normale Maus-Buttons
            if button in [self.mouse_buttons["primary"], self.mouse_buttons["secondary"]]:
                self._start_recording()
                return True
            
            # Prüfe Modifier-Kombinationen
            for modifier, mouse_button in self.modifier_combinations:
                if (modifier in self._active_modifiers and 
                    button == mouse_button):
                    self._start_recording()
                    return True
                    
        elif not pressed and self._is_recording:
            # Prüfe ob der Button losgelassen wurde
            if button in [self.mouse_buttons["primary"], self.mouse_buttons["secondary"]]:
                self._stop_recording()
                return True
            
            # Prüfe Modifier-Kombinationen
            for modifier, mouse_button in self.modifier_combinations:
                if (modifier in self._active_modifiers and 
                    button == mouse_button):
                    self._stop_recording()
                    return True
        
        return True  # Erlaube normale Maus-Funktionen
    
    def _on_key_press(self, key) -> bool:
        """Tastatur-Press Handler"""
        # Modifier-Tasten tracken
        if key in [keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r,
                   keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r,
                   keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r]:
            self._active_modifiers.add(key)
            return True
        
        if not self._is_recording:
            # Prüfe normale Tasten
            if key in [self.keyboard_keys["primary"], self.keyboard_keys["secondary"]]:
                self._start_recording()
                return True
            
            # Prüfe Kombinationen
            for modifier, key_combo in self.keyboard_combinations:
                if (modifier in self._active_modifiers and key == key_combo):
                    self._start_recording()
                    return True
        
        return True
    
    def _on_key_release(self, key) -> bool:
        """Tastatur-Release Handler"""
        # Modifier-Tasten tracken
        if key in [keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r,
                   keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r,
                   keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r]:
            self._active_modifiers.discard(key)
            return True
        
        if self._is_recording:
            # Prüfe normale Tasten
            if key in [self.keyboard_keys["primary"], self.keyboard_keys["secondary"]]:
                self._stop_recording()
                return True
            
            # Prüfe Kombinationen
            for modifier, key_combo in self.keyboard_combinations:
                if (modifier in self._active_modifiers and key == key_combo):
                    self._stop_recording()
                    return True
        
        return True
    
    def _start_recording(self) -> None:
        """Startet die Aufnahme"""
        with self._lock:
            if not self._is_recording:
                self._is_recording = True
                self._start_time = time.time()
                self.on_start()
    
    def _stop_recording(self) -> None:
        """Stoppt die Aufnahme"""
        with self._lock:
            if self._is_recording:
                duration = time.time() - self._start_time
                # Audio-Verarbeitung nur bei ausreichender Länge
                if duration >= config.MIN_RECORDING_SECONDS:
                    self.on_stop()
                else:
                    # Bei zu kurzer Aufnahme IMMER System-Sound wiederherstellen
                    if hasattr(self, 'on_stop_system_only'):
                        self.on_stop_system_only()
                self._is_recording = False
    
    def start(self) -> None:
        """Startet die Input-Listener"""
        if self.input_method == "mouse_button":
            self._mouse_listener = mouse.Listener(on_click=self._on_mouse_click)
            self._mouse_listener.start()
            
        elif self.input_method == "keyboard":
            self._keyboard_listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            self._keyboard_listener.start()
            
        elif self.input_method == "custom":
            # Kombinierter Input
            self._mouse_listener = mouse.Listener(on_click=self._on_mouse_click)
            self._keyboard_listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            self._mouse_listener.start()
            self._keyboard_listener.start()
    
    def stop(self) -> None:
        """Stoppt die Input-Listener"""
        if self._mouse_listener:
            self._mouse_listener.stop()
        if self._keyboard_listener:
            self._keyboard_listener.stop()
    
    def set_mouse_click_callback(self, callback) -> None:
        """Setzt einen zusätzlichen Maus-Click Callback"""
        self._mouse_click_callback = callback
    
    def get_status(self) -> Dict:
        """Gibt den aktuellen Status zurück"""
        return {
            "is_recording": self._is_recording,
            "input_method": self.input_method,
            "active_modifiers": list(self._active_modifiers),
            "duration": time.time() - self._start_time if self._is_recording else 0
        }
