from __future__ import annotations

import sys
import threading
import time
from typing import Optional

import pyperclip
from pynput import mouse

from . import config
from .audio import AudioRecorder
from .stt import SpeechToText
from .input_handler import InputHandler
from .cursor_manager import start_recording_cursor, stop_recording_cursor, set_cursor_type
from .actions import SystemActions


class MauscribeController:
    def __init__(self) -> None:
        self._recorder = AudioRecorder()
        self._stt = SpeechToText()
        self._system_actions = SystemActions()
        self._input_handler = InputHandler(
            on_start=self._on_recording_start,
            on_stop=self._on_recording_stop
        )
        # Separater Callback für System-Sound Wiederherstellung bei kurzen Aufnahmen
        self._input_handler.on_stop_system_only = self._on_recording_stop_system_only
        
        # Maus-Click Handler für Doppelklick registrieren
        self._input_handler.set_mouse_click_callback(self._on_mouse_click)
        self._exit_requested = False
        self._last_text = None
        self._last_text_time = 0  # Zeitpunkt der letzten Transkription
        self._last_click_time = 0
        self._double_click_threshold = config.DOUBLE_CLICK_THRESHOLD
        
        # Volume-Management
        self._original_volume = None
        self._volume_restored = True

    def _on_recording_start(self) -> None:
        """Callback wenn Aufnahme startet"""
        # Volume reduzieren
        self._reduce_volume()
        
        # Cursor-Feedback starten
        if config.ENABLE_CURSOR_FEEDBACK:
            set_cursor_type(config.CURSOR_TYPE)
            start_recording_cursor()
        
        # Audio-Aufnahme starten
        self._recorder.start_recording()

    def _on_recording_stop(self) -> None:
        """Callback wenn Aufnahme stoppt"""
        # Volume wiederherstellen
        self._restore_volume()
        
        # Cursor-Feedback stoppen
        if config.ENABLE_CURSOR_FEEDBACK:
            stop_recording_cursor()
        
        # Audio-Aufnahme stoppen
        audio = self._recorder.stop_recording()
        
        # Audio verarbeiten
        if audio.size > 0:
            self._process_audio(audio)

    def _on_recording_stop_system_only(self) -> None:
        """Callback für kurze Aufnahmen"""
        # Volume wiederherstellen
        self._restore_volume()
        
        # Cursor-Feedback stoppen
        if config.ENABLE_CURSOR_FEEDBACK:
            stop_recording_cursor()

    def _reduce_volume(self) -> None:
        """Reduziert die System-Lautstärke"""
        try:
            if self._volume_restored:
                self._original_volume = self._system_actions.get_volume_percent()
                new_volume = max(
                    config.MIN_VOLUME_PERCENT,
                    int(self._original_volume * config.VOLUME_REDUCTION_FACTOR)
                )
                self._system_actions.set_volume_percent(new_volume)
                self._volume_restored = False
                print(f"🔉 Volume reduziert: {self._original_volume}% → {new_volume}%")
        except Exception as e:
            print(f"❌ Volume-Reduktion fehlgeschlagen: {e}")

    def _restore_volume(self) -> None:
        """Stellt die ursprüngliche System-Lautstärke wieder her"""
        try:
            if not self._volume_restored and self._original_volume is not None:
                # Mehrfache Versuche mit Pausen
                for attempt in range(3):
                    try:
                        self._system_actions.set_volume_percent(self._original_volume)
                        print(f"🔊 Volume wiederhergestellt: {self._original_volume}%")
                        self._volume_restored = True
                        self._original_volume = None
                        break
                    except Exception as e:
                        if attempt < 2:  # Nicht beim letzten Versuch
                            print(f"⚠️  Volume-Wiederherstellung Versuch {attempt + 1} fehlgeschlagen, versuche erneut...")
                            time.sleep(0.2)
                        else:
                            raise e
        except Exception as e:
            print(f"❌ Volume-Wiederherstellung fehlgeschlagen: {e}")
            # Als letzten Ausweg: Volume auf 50% setzen
            try:
                self._system_actions.set_volume_percent(50)
                print("🔊 Volume auf 50% gesetzt (Fallback)")
                self._volume_restored = True
                self._original_volume = None
            except Exception as e2:
                print(f"❌ Auch Fallback-Volume fehlgeschlagen: {e2}")

    def _on_mouse_click(self, x, y, button, pressed):  # type: ignore[no-untyped-def]
        """Maus-Click Handler für Doppelklick-Funktionalität mit Entprellung"""
        # Nur linke Maustaste und nur wenn Text vorhanden ist
        if pressed and button == mouse.Button.left and self._last_text:
            current_time = time.time()
            
            # Prüfe ob das Zeitfenster noch aktiv ist
            if (current_time - self._last_text_time) <= config.PASTE_DOUBLE_CLICK_WINDOW:
                # Entprellung: Mindestabstand zwischen Klicks
                if (current_time - self._last_click_time) >= 0.1:  # 100ms Minimum
                    # Check for double-click (paste functionality)
                    if (current_time - self._last_click_time < self._double_click_threshold):
                        try:
                            import pyautogui
                            # Kurze Pause um sicherzustellen, dass der Klick abgeschlossen ist
                            time.sleep(0.05)
                            pyautogui.hotkey('ctrl', 'v')
                            print(f"📋 Text automatisch eingefügt!")
                            self._last_text = None  # Reset after paste
                            self._last_click_time = 0  # Reset click timer
                            return
                        except Exception as exc:
                            print(f"Fehler beim automatischen Einfügen: {exc}")
                    
                    self._last_click_time = current_time
        
        # Always allow normal mouse function for other buttons
        return True

    def _process_audio(self, audio):  # type: ignore[no-untyped-def]
        try:
            text = self._stt.transcribe(audio)
        except Exception as exc:
            print(f"STT Fehler: {exc}")
            return
        
        text = (text or "").strip()
        if not text:
            return
        
        # Copy to clipboard and store for later paste
        try:
            # Add space at the end if configured
            if config.ADD_SPACE_AFTER_TEXT:
                text_with_space = text + " "
            else:
                text_with_space = text
                
            pyperclip.copy(text_with_space)
            self._last_text = text_with_space  # Store for auto-paste
            self._last_text_time = time.time()  # Zeitpunkt der Transkription setzen
            
            # Automatisches Einfügen nach Transkription
            if config.AUTO_PASTE_AFTER_TRANSCRIPTION:
                try:
                    import pyautogui
                    pyautogui.hotkey('ctrl', 'v')
                    print(f"📋 Text automatisch eingefügt!")
                    self._last_text = None  # Reset after paste
                except Exception as exc:
                    print(f"Fehler beim automatischen Einfügen: {exc}")
                        
        except Exception as exc:
            print(f"Fehler beim Kopieren: {exc}")

    def run(self) -> None:
        """Hauptschleife"""
        # Input-Handler starten
        self._input_handler.start()
        
        # Status anzeigen
        self._print_status()
        
        # Hauptschleife
        try:
            while not self._exit_requested:
                time.sleep(0.05)
        except KeyboardInterrupt:
            print("\n👋 Mauscribe beendet")
        finally:
            # Volume wiederherstellen beim Beenden
            self._restore_volume()
            self._input_handler.stop()

    def _print_status(self) -> None:
        """Zeigt den aktuellen Status an"""
        input_method = config.INPUT_METHOD
        input_config = config.ACTIVE_INPUT_CONFIG
        
        print("=" * 50)
        # Input-Info
        print("🎤 Mauscribe - Voice-to-Text Tool")
        if input_method == "mouse_button":
            print(f"🎯 Input: {input_config['primary']}, {input_config['secondary']}")
            if input_config.get('left_with_ctrl'):
                print(f"🎯 + Strg + Linke Maus")
        elif input_method == "keyboard":
            print(f"🎯 Input: {input_config['primary']}, {input_config['secondary']}")
        elif input_method == "custom":
            print(f"🎯 Custom-Kombinationen: {len(input_config['combinations'])}")
        
        # Features
        print("📋 Text → Zwischenablage (mit Leerzeichen)")
        if config.ENABLE_CURSOR_FEEDBACK:
            print(f"🖱️  Cursor-Feedback: {config.CURSOR_TYPE}")
        if config.AUTO_PASTE_AFTER_TRANSCRIPTION:
            print("💡 Auto-Paste nach Transkription")
        else:
            print(f"💡 Doppelklick (linke Maus) zum Einfügen ({config.PASTE_DOUBLE_CLICK_WINDOW}s)")
        
        print("💡 Ctrl+C zum Beenden")
        print("=" * 50)

    def stop(self) -> None:
        """Stoppt den Controller"""
        self._exit_requested = True


def main() -> None:
    try:
        MauscribeController().run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
