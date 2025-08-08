"""
Mauscribe Cursor Manager
Verwandelt den Mauszeiger während der Aufnahme in ein Mikrofon oder kleine Maus
"""

from __future__ import annotations

import os
import sys
import threading
import time
from typing import Optional, Tuple
from pathlib import Path

try:
    import win32api
    import win32con
    import win32gui
    import win32ui
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False

from . import config


class CursorManager:
    """Verwaltet den Mauszeiger während der Aufnahme"""
    
    def __init__(self) -> None:
        self._original_cursor = None
        self._recording_cursor = None
        self._is_recording = False
        self._lock = threading.Lock()
        self._cursor_type = getattr(config, 'CURSOR_TYPE', 'microphone')  # 'microphone' oder 'mouse'
        
        # Cursor-Pfade
        self._setup_cursor_paths()
        
    def _setup_cursor_paths(self) -> None:
        """Setzt die Cursor-Pfade"""
        icons_dir = Path("icons")
        
        # Standard-Cursor-Pfade
        self.cursor_paths = {
            'microphone': {
                'recording': icons_dir / "mauscribe_recording.cur",
                'idle': icons_dir / "mauscribe_icon.cur"
            },
            'mouse': {
                'recording': icons_dir / "mouse_recording.cur", 
                'idle': icons_dir / "mouse_idle.cur"
            }
        }
        
        # Fallback auf Windows-System-Cursor
        self.fallback_cursors = {
            'microphone': {
                'recording': win32con.IDC_HAND,  # Hand-Cursor als Mikrofon
                'idle': win32con.IDC_ARROW
            },
            'mouse': {
                'recording': win32con.IDC_SIZEALL,  # Move-Cursor als kleine Maus
                'idle': win32con.IDC_ARROW
            }
        }
    
    def _create_custom_cursor(self, icon_path: Path, size: Tuple[int, int] = (32, 32)) -> Optional[int]:
        """Erstellt einen benutzerdefinierten Cursor aus einer Icon-Datei"""
        if not WINDOWS_AVAILABLE:
            return None
            
        try:
            if not icon_path.exists():
                return None
                
            # Lade Icon und erstelle Cursor
            hicon = win32gui.LoadImage(
                0, str(icon_path), win32con.IMAGE_CURSOR,
                size[0], size[1], win32con.LR_LOADFROMFILE
            )
            
            if hicon:
                return hicon
                
        except Exception as e:
            if config.VERBOSE_LOGGING:
                print(f"⚠️  Konnte benutzerdefinierten Cursor nicht laden: {e}")
        
        return None
    
    def _set_system_cursor(self, cursor_id: int) -> None:
        """Setzt einen System-Cursor"""
        if not WINDOWS_AVAILABLE:
            return
            
        try:
            # Lade den Cursor
            cursor = win32gui.LoadCursor(0, cursor_id)
            # Setze Cursor für das aktuelle Fenster
            win32gui.SetCursor(cursor)
        except Exception as e:
            print(f"⚠️  Konnte System-Cursor nicht setzen: {e}")

    def _restore_system_cursor(self) -> None:
        """Stellt den ursprünglichen System-Cursor wieder her"""
        if not WINDOWS_AVAILABLE:
            return
            
        try:
            # Stelle Standard-Cursor wieder her
            win32gui.SystemParametersInfo(
                win32con.SPI_SETCURSORS, 0, 0, 0
            )
        except Exception as e:
            print(f"⚠️  Konnte System-Cursor nicht wiederherstellen: {e}")

    def start_recording_cursor(self) -> None:
        """Startet den Aufnahme-Cursor"""
        with self._lock:
            if self._is_recording:
                return
                
            self._is_recording = True
            
            # Speichere aktuellen Cursor
            if WINDOWS_AVAILABLE:
                try:
                    self._original_cursor = win32gui.GetCursor()
                except:
                    self._original_cursor = None
            
            # Setze Aufnahme-Cursor
            self._set_recording_cursor()
            
            print(f"🎤 Cursor geändert zu {self._cursor_type}")

    def stop_recording_cursor(self) -> None:
        """Stoppt den Aufnahme-Cursor"""
        with self._lock:
            if not self._is_recording:
                return
                
            self._is_recording = False
            
            # Stelle ursprünglichen Cursor wieder her
            self._restore_original_cursor()
            
            print("🖱️  Cursor wiederhergestellt")

    def _set_recording_cursor(self) -> None:
        """Setzt den Aufnahme-Cursor"""
        if not WINDOWS_AVAILABLE:
            return
            
        cursor_type = self._cursor_type
        cursor_path = self.cursor_paths[cursor_type]['recording']
        
        # Versuche benutzerdefinierten Cursor zu laden
        custom_cursor = self._create_custom_cursor(cursor_path)
        
        if custom_cursor:
            try:
                # Setze benutzerdefinierten Cursor
                win32gui.SetCursor(custom_cursor)
                self._recording_cursor = custom_cursor
                return
            except Exception as e:
                print(f"⚠️  Benutzerdefinierter Cursor fehlgeschlagen: {e}")
        
        # Fallback auf System-Cursor
        try:
            fallback_id = self.fallback_cursors[cursor_type]['recording']
            self._set_system_cursor(fallback_id)
        except Exception as e:
            print(f"⚠️  System-Cursor fehlgeschlagen: {e}")

    def _restore_original_cursor(self) -> None:
        """Stellt den ursprünglichen Cursor wieder her"""
        if not WINDOWS_AVAILABLE:
            return
            
        try:
            if self._original_cursor:
                # Stelle ursprünglichen Cursor wieder her
                win32gui.SetCursor(self._original_cursor)
            else:
                # Fallback auf Standard-Cursor
                self._restore_system_cursor()
                
            # Cleanup
            if self._recording_cursor:
                try:
                    win32gui.DestroyCursor(self._recording_cursor)
                except:
                    pass
                self._recording_cursor = None
        except Exception as e:
            print(f"⚠️  Cursor-Wiederherstellung fehlgeschlagen: {e}")
            # Als letzten Ausweg: System-Cursor wiederherstellen
            try:
                self._restore_system_cursor()
            except:
                pass
    
    def set_cursor_type(self, cursor_type: str) -> None:
        """Setzt den Cursor-Typ ('microphone' oder 'mouse')"""
        if cursor_type in ['microphone', 'mouse']:
            self._cursor_type = cursor_type
            if config.VERBOSE_LOGGING:
                print(f"🎯 Cursor-Typ geändert zu: {cursor_type}")
    
    def get_status(self) -> dict:
        """Gibt den aktuellen Status zurück"""
        return {
            "is_recording": self._is_recording,
            "cursor_type": self._cursor_type,
            "windows_available": WINDOWS_AVAILABLE
        }


# Globaler Cursor-Manager
_cursor_manager = None

def get_cursor_manager() -> CursorManager:
    """Gibt den globalen Cursor-Manager zurück"""
    global _cursor_manager
    if _cursor_manager is None:
        _cursor_manager = CursorManager()
    return _cursor_manager

def start_recording_cursor() -> None:
    """Startet den Aufnahme-Cursor"""
    get_cursor_manager().start_recording_cursor()

def stop_recording_cursor() -> None:
    """Stoppt den Aufnahme-Cursor"""
    get_cursor_manager().stop_recording_cursor()

def set_cursor_type(cursor_type: str) -> None:
    """Setzt den Cursor-Typ"""
    get_cursor_manager().set_cursor_type(cursor_type)
