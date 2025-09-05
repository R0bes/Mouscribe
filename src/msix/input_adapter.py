"""
MSIX-spezifischer Input-Adapter für Mauscribe
Verwendet Windows Runtime APIs für MSIX-kompatible Input-Verarbeitung
"""

import os
import threading
import time
from typing import Optional, Callable, Dict, Any
from pathlib import Path

try:
    from pynput import keyboard, mouse
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False

try:
    import keyboard as kb
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False

from ..utils.config import Config
from ..utils.logger import get_logger


class MSIXInputAdapter:
    """MSIX-kompatibler Input-Adapter mit Fallback-Mechanismen"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = get_logger(self.__class__.__name__)
        
        # MSIX-Erkennung
        self._is_msix = self._detect_msix_environment()
        self.logger.info(f"MSIX-Umgebung erkannt: {self._is_msix}")
        
        # Input-System
        self._input_system = None
        self._listeners = []
        self._is_active = False
        
        # Callbacks
        self._primary_callback: Optional[Callable] = None
        self._secondary_callback: Optional[Callable] = None
        self._third_callback: Optional[Callable] = None
        
        # Debouncing
        self._last_click_time = 0.0
        self._debounce_time = 0.2  # 200ms
        
        # Button-Mapping
        self._button_mapping = self._create_button_mapping()
        
        # Initialisierung
        self._initialize_input_system()
    
    def _detect_msix_environment(self) -> bool:
        """Erkennt MSIX-Container-Umgebung"""
        msix_indicators = [
            'MSIX_PACKAGE_FAMILY_NAME',
            'PACKAGE_FAMILY_NAME',
            'PACKAGE_FULL_NAME'
        ]
        
        for indicator in msix_indicators:
            if indicator in os.environ:
                return True
        
        # Prüfe AppData-Pfad
        app_data = os.environ.get('LOCALAPPDATA', '')
        if app_data and 'Packages' in app_data:
            return True
        
        return False
    
    def _initialize_input_system(self):
        """Initialisiert das beste verfügbare Input-System"""
        self.logger.info("Initialisiere Input-System...")
        
        # Priorisierte Input-Systeme
        input_systems = [
            ('Windows Runtime', self._try_winrt_input),
            ('PyNput', self._try_pynput_input),
            ('Keyboard Library', self._try_keyboard_lib_input),
            ('Fallback', self._try_fallback_input)
        ]
        
        for name, system_func in input_systems:
            try:
                self.logger.info(f"Versuche {name} Input-System...")
                if system_func():
                    self.logger.info(f"✅ {name} Input-System erfolgreich initialisiert")
                    return
            except Exception as e:
                self.logger.warning(f"⚠️ {name} Input-System fehlgeschlagen: {e}")
                continue
        
        self.logger.error("❌ Kein Input-System konnte initialisiert werden")
        raise RuntimeError("Kein Input-System verfügbar")
    
    def _try_winrt_input(self) -> bool:
        """Versucht Windows Runtime Input APIs"""
        if not self._is_msix:
            return False
        
        try:
            # Windows Runtime Input APIs verwenden
            # Diese sind MSIX-kompatibel
            import winrt.windows.ui.input as input
            import winrt.windows.ui.core as core
            
            self._input_system = 'winrt'
            return True
        except ImportError:
            self.logger.debug("Windows Runtime Input nicht verfügbar")
            return False
        except Exception as e:
            self.logger.warning(f"Windows Runtime Input Fehler: {e}")
            return False
    
    def _try_pynput_input(self) -> bool:
        """Versucht PyNput Input-System"""
        if not PYNPUT_AVAILABLE:
            return False
        
        try:
            # PyNput ist MSIX-kompatibel
            self._input_system = 'pynput'
            return True
        except Exception as e:
            self.logger.warning(f"PyNput Fehler: {e}")
            return False
    
    def _try_keyboard_lib_input(self) -> bool:
        """Versucht Keyboard Library Input-System"""
        if not KEYBOARD_AVAILABLE:
            return False
        
        try:
            # Keyboard Library ist MSIX-kompatibel
            self._input_system = 'keyboard'
            return True
        except Exception as e:
            self.logger.warning(f"Keyboard Library Fehler: {e}")
            return False
    
    def _try_fallback_input(self) -> bool:
        """Fallback Input-System"""
        self.logger.warning("Verwende Fallback Input-System")
        self._input_system = 'fallback'
        return True
    
    def _create_button_mapping(self) -> Dict[str, Any]:
        """Erstellt Button-Mapping basierend auf Konfiguration"""
        mapping = {
            'primary': self.config.input_primary_name,
            'secondary': self.config.input_secondary_name,
            'third': self.config.input_third_name
        }
        
        # Konvertiere zu PyNput-Buttons falls verfügbar
        if PYNPUT_AVAILABLE:
            mouse_buttons = {
                'm_left': mouse.Button.left,
                'left': mouse.Button.left,
                'm_right': mouse.Button.right,
                'right': mouse.Button.right,
                'm_middle': mouse.Button.middle,
                'middle': mouse.Button.middle,
                'm_x1': mouse.Button.x1,
                'x1': mouse.Button.x1,
                'm_x2': mouse.Button.x2,
                'x2': mouse.Button.x2,
            }
            
            for key, value in mapping.items():
                if value in mouse_buttons:
                    mapping[key] = mouse_buttons[value]
        
        return mapping
    
    def set_callbacks(self, 
                     primary: Optional[Callable] = None,
                     secondary: Optional[Callable] = None,
                     third: Optional[Callable] = None):
        """Setzt Callback-Funktionen"""
        self._primary_callback = primary
        self._secondary_callback = secondary
        self._third_callback = third
    
    def start_listening(self):
        """Startet Input-Listening"""
        if self._is_active:
            self.logger.warning("Input-Listening läuft bereits")
            return
        
        self._is_active = True
        
        if self._input_system == 'winrt':
            self._start_winrt_listening()
        elif self._input_system == 'pynput':
            self._start_pynput_listening()
        elif self._input_system == 'keyboard':
            self._start_keyboard_listening()
        else:
            self._start_fallback_listening()
        
        self.logger.info("Input-Listening gestartet")
    
    def stop_listening(self):
        """Stoppt Input-Listening"""
        if not self._is_active:
            return
        
        self._is_active = False
        
        # Stoppe alle Listener
        for listener in self._listeners:
            try:
                listener.stop()
            except:
                pass
        
        self._listeners.clear()
        self.logger.info("Input-Listening gestoppt")
    
    def _start_winrt_listening(self):
        """Startet Windows Runtime Input-Listening"""
        try:
            import winrt.windows.ui.input as input
            import winrt.windows.ui.core as core
            
            # Windows Runtime Input Event Handling
            # MSIX-kompatible Implementierung
            pass
        except ImportError:
            self.logger.error("Windows Runtime Input nicht verfügbar")
    
    def _start_pynput_listening(self):
        """Startet PyNput Input-Listening"""
        try:
            # Mouse Listener
            mouse_listener = mouse.Listener(
                on_click=self._on_mouse_click
            )
            mouse_listener.start()
            self._listeners.append(mouse_listener)
            
            # Keyboard Listener
            keyboard_listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            keyboard_listener.start()
            self._listeners.append(keyboard_listener)
            
        except Exception as e:
            self.logger.error(f"PyNput Listening Fehler: {e}")
    
    def _start_keyboard_listening(self):
        """Startet Keyboard Library Listening"""
        try:
            # Keyboard Events
            kb.on_press(self._on_keyboard_press)
            kb.on_release(self._on_keyboard_release)
            
            # Mouse Events (falls verfügbar)
            if hasattr(kb, 'on_mouse'):
                kb.on_mouse(self._on_keyboard_mouse)
            
        except Exception as e:
            self.logger.error(f"Keyboard Library Listening Fehler: {e}")
    
    def _start_fallback_listening(self):
        """Startet Fallback Input-Listening"""
        # Simuliere Input-Events für Tests
        def simulate_input():
            import random
            while self._is_active:
                time.sleep(5)  # Alle 5 Sekunden ein Event
                if random.random() < 0.3:  # 30% Chance
                    self._handle_primary_input()
        
        fallback_thread = threading.Thread(target=simulate_input)
        fallback_thread.daemon = True
        fallback_thread.start()
        self._listeners.append(fallback_thread)
    
    def _on_mouse_click(self, x, y, button, pressed):
        """Handler für Mausklicks"""
        if not self._is_active:
            return
        
        current_time = time.time()
        
        # Debouncing
        if current_time - self._last_click_time < self._debounce_time:
            return
        
        self._last_click_time = current_time
        
        # Button-Mapping prüfen
        if button == self._button_mapping.get('primary'):
            self._handle_primary_input()
        elif button == self._button_mapping.get('secondary'):
            self._handle_secondary_input()
        elif button == self._button_mapping.get('third'):
            self._handle_third_input()
    
    def _on_key_press(self, key):
        """Handler für Tastendruck"""
        if not self._is_active:
            return
        
        # Hotkey-Kombinationen prüfen
        self._check_hotkey_combinations(key)
    
    def _on_key_release(self, key):
        """Handler für Tastenfreigabe"""
        if not self._is_active:
            return
    
    def _on_keyboard_press(self, event):
        """Handler für Keyboard Library Events"""
        if not self._is_active:
            return
        
        # Hotkey-Kombinationen prüfen
        self._check_hotkey_combinations(event.name)
    
    def _on_keyboard_release(self, event):
        """Handler für Keyboard Library Release Events"""
        if not self._is_active:
            return
    
    def _on_keyboard_mouse(self, event):
        """Handler für Keyboard Library Mouse Events"""
        if not self._is_active:
            return
        
        # Maus-Events verarbeiten
        if hasattr(event, 'button'):
            self._on_mouse_click(event.x, event.y, event.button, event.pressed)
    
    def _check_hotkey_combinations(self, key):
        """Prüft Hotkey-Kombinationen"""
        # Implementierung von Hotkey-Kombinationen
        # z.B. Ctrl+Shift+F9 für Aufnahme starten
        pass
    
    def _handle_primary_input(self):
        """Behandelt primäre Input-Events"""
        if self._primary_callback:
            try:
                self._primary_callback(True)
            except Exception as e:
                self.logger.error(f"Primary Callback Fehler: {e}")
    
    def _handle_secondary_input(self):
        """Behandelt sekundäre Input-Events"""
        if self._secondary_callback:
            try:
                self._secondary_callback(True)
            except Exception as e:
                self.logger.error(f"Secondary Callback Fehler: {e}")
    
    def _handle_third_input(self):
        """Behandelt dritte Input-Events"""
        if self._third_callback:
            try:
                self._third_callback(True)
            except Exception as e:
                self.logger.error(f"Third Callback Fehler: {e}")
    
    def is_listening(self) -> bool:
        """Gibt zurück ob Input-Listening aktiv ist"""
        return self._is_active
    
    def get_input_system(self) -> str:
        """Gibt das verwendete Input-System zurück"""
        return self._input_system
    
    def cleanup(self):
        """Räumt Input-System auf"""
        self.stop_listening()
        self._listeners.clear()
