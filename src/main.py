from __future__ import annotations
import time
from typing import Optional
from pathlib import Path
import os

import pyperclip
from pynput import mouse
import pystray
from PIL import Image, ImageDraw

from . import config
from .recorder import AudioRecorder
from .stt import SpeechToText
from .input_handler import InputHandler
from .sound_controller import SoundController


class MauscribeController:
    def __init__(self) -> None:
        self._recorder = AudioRecorder()
        self._stt = SpeechToText()
        self._system_actions = SoundController()
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
        
        # System Tray
        self._tray_icon = None
        self._setup_system_tray()

    def _setup_system_tray(self) -> None:
        """Erstellt das System Tray Icon"""
        try:
            print("Erstelle System Tray Icon...")
            icon_size = 64
            icon_image = Image.new('RGB', (icon_size, icon_size), color='blue')
            draw = ImageDraw.Draw(icon_image)
            # Drawing logic for microphone icon
            margin = 8
            draw.ellipse([margin, margin, icon_size-margin, icon_size-margin], fill='white')
            inner_margin = 12
            draw.ellipse([inner_margin, inner_margin, icon_size-inner_margin, icon_size-inner_margin], fill='blue')
            mic_width = 8
            mic_height = 20
            mic_x = (icon_size - mic_width) // 2
            mic_y = (icon_size - mic_height) // 2
            draw.rectangle([mic_x, mic_y, mic_x + mic_width, mic_y + mic_height], fill='white')
            base_width = 16
            base_height = 6
            base_x = (icon_size - base_width) // 2
            base_y = mic_y + mic_height
            draw.rectangle([base_x, base_y, base_x + base_width, base_y + base_height], fill='white')

            menu = pystray.Menu(
                pystray.MenuItem("Status", self._show_status),
                pystray.MenuItem("Konfiguration", self._open_config),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Beenden", self.stop)
            )
            self._tray_icon = pystray.Icon(
                "mauscribe",
                icon_image,
                "Mauscribe - Voice-to-Text",
                menu
            )
            print("System Tray Icon erstellt")
        except Exception as e:
            print(f"System Tray konnte nicht erstellt werden: {e}")
            print("Verwende Fallback-Modus ohne System Tray")
            self._tray_icon = None

    def _show_status(self, icon, item) -> None:
        """Zeigt den aktuellen Status an"""
        status = "Aufnahme läuft" if self._input_handler._is_recording else "Bereit"
        print(f"Status: {status}")

    def _open_config(self, icon, item) -> None:
        """Öffnet die Konfigurationsdatei"""
        try:
            config_path = Path(__file__).parent.parent / "config.toml"
            if config_path.exists():
                os.startfile(str(config_path))
            else:
                print("Konfigurationsdatei nicht gefunden")
        except Exception as e:
            print(f"Konnte Konfiguration nicht öffnen: {e}")

    def _on_recording_start(self) -> None:
        """Callback wenn Aufnahme startet"""
        # Volume reduzieren
        self._reduce_volume()
        
        # Audio-Aufnahme starten
        self._recorder.start_recording()

    def _on_recording_stop(self) -> None:
        """Callback wenn Aufnahme stoppt"""
        # Volume wiederherstellen
        self._restore_volume()
        
        # Audio-Aufnahme stoppen
        audio = self._recorder.stop_recording()
        
        # Audio verarbeiten
        if audio.size > 0:
            self._process_audio(audio)

    def _on_recording_stop_system_only(self) -> None:
        """Callback für kurze Aufnahmen"""
        # Volume wiederherstellen
        self._restore_volume()

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
                print(f"Volume reduziert: {self._original_volume}% -> {new_volume}%")
        except Exception as e:
            print(f"Volume-Reduktion fehlgeschlagen: {e}")

    def _restore_volume(self) -> None:
        """Stellt die ursprüngliche System-Lautstärke wieder her"""
        try:
            if not self._volume_restored and self._original_volume is not None:
                # Mehrfache Versuche mit Pausen
                for attempt in range(3):
                    try:
                        self._system_actions.set_volume_percent(self._original_volume)
                        print(f"Volume wiederhergestellt: {self._original_volume}%")
                        self._volume_restored = True
                        self._original_volume = None
                        break
                    except Exception as e:
                        if attempt < 2:  # Nicht beim letzten Versuch
                            print(f"Volume-Wiederherstellung Versuch {attempt + 1} fehlgeschlagen, versuche erneut...")
                            time.sleep(0.2)
                        else:
                            raise e
        except Exception as e:
            print(f"Volume-Wiederherstellung fehlgeschlagen: {e}")
            # Als letzten Ausweg: Volume auf 50% setzen
            try:
                self._system_actions.set_volume_percent(50)
                print("Volume auf 50% gesetzt (Fallback)")
                self._volume_restored = True
                self._original_volume = None
            except Exception as e2:
                print(f"Auch Fallback-Volume fehlgeschlagen: {e2}")

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
                            print(f"Text automatisch eingefügt!")
                            self._last_text = None  # Reset after paste
                            self._last_click_time = 0  # Reset click timer
                            return
                        except Exception as exc:
                            print(f"Fehler beim automatischen Einfügen: {exc}")
                    
                    self._last_click_time = current_time
        
        # Always allow normal mouse function for other buttons
        return True

    def _process_audio(self, audio):  # type: ignore[no-untyped-def]
        """Verarbeitet die Audio-Aufnahme"""
        try:
            # STT-Verarbeitung
            text = self._stt.transcribe(audio)
            
            if text and text.strip():
                # Text in Zwischenablage kopieren
                if config.ADD_SPACE_AFTER_TEXT:
                    text += " "
                
                pyperclip.copy(text)
                print(f"Text automatisch eingefügt!")
                
                # Für Doppelklick-Funktionalität speichern
                self._last_text = text
                self._last_text_time = time.time()
                
                # Auto-Paste falls aktiviert
                if config.AUTO_PASTE_AFTER_TRANSCRIPTION:
                    try:
                        import pyautogui
                        time.sleep(0.1)  # Kurze Pause
                        pyautogui.hotkey('ctrl', 'v')
                    except Exception as e:
                        print(f"Auto-Paste fehlgeschlagen: {e}")
            else:
                print("Kein Text erkannt")
                
        except Exception as e:
            print(f"Audio-Verarbeitung fehlgeschlagen: {e}")

    def run(self) -> None:
        """Startet den Controller"""
        try:
            # Input-Listener starten
            self._input_handler.start()
            
            # Status ausgeben
            self._print_status()
            
            # System Tray oder Fallback
            if self._tray_icon:
                print("System Tray Icon aktiv - Rechtsklick für Menü")
                try:
                    self._tray_icon.run()
                except Exception as e:
                    print(f"System Tray Fehler: {e}")
                    self._run_fallback()
            else:
                self._run_fallback()
                
        except KeyboardInterrupt:
            print("\nBeende...")
        except Exception as e:
            print(f"Fehler: {e}")
        finally:
            self.stop()

    def _run_fallback(self) -> None:
        """Fallback-Modus ohne System Tray"""
        print("Fallback-Modus aktiv")
        try:
            while not self._exit_requested:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nBeende...")

    def _print_status(self) -> None:
        """Gibt den Status aus"""
        print("=" * 50)
        print("Mauscribe - Voice-to-Text Tool")
        
        # Input-Konfiguration
        input_config = config.ACTIVE_INPUT_CONFIG
        if config.INPUT_METHOD == "mouse_button":
            print(f"Input: {input_config['primary']}, {input_config['secondary']}")
            if input_config.get('left_with_ctrl', False):
                print(f"+ Strg + Linke Maus")
        elif config.INPUT_METHOD == "keyboard":
            print(f"Input: {input_config['primary']}, {input_config['secondary']}")
        elif config.INPUT_METHOD == "custom":
            print(f"Custom-Kombinationen: {len(input_config['combinations'])}")
        
        # Features
        print("Text -> Zwischenablage (mit Leerzeichen)")
        if config.AUTO_PASTE_AFTER_TRANSCRIPTION:
            print("Auto-Paste nach Transkription")
        else:
            print(f"Doppelklick (linke Maus) zum Einfügen ({config.PASTE_DOUBLE_CLICK_WINDOW}s)")
        
        print("System Tray Icon verfügbar")
        print("=" * 50)

    def stop(self, icon=None, item=None) -> None:
        """Stoppt den Controller"""
        self._exit_requested = True
        if self._tray_icon:
            self._tray_icon.stop()


def main() -> None:
    try:
        MauscribeController().run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
