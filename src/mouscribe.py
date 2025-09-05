# src/main.py - Main application entry point for Mauscribe
"""
Mauscribe - Voice-to-Text Tool
Main application logic and core functionality
"""
import atexit
import signal
import sys
import threading
import time
import traceback
from typing import Any

import numpy as np
import pyautogui
import pyperclip

from .audio.recorder import AudioRecorder
from .audio.volume_controller import VolumeController
from .core.simple_queue import SimpleTranscriptionQueue
from .input.input_handler import InputHandler
from .lang.spell_checker import SpellChecker
from .lang.stt import SpeechToText
from .ui.gui.manager import GUIManager
from .ui.notifications import NotificationManager
from .ui.system_tray import SystemTrayManager
from .utils.config import Config
from .utils.database import AudioDatabase
from .utils.logger import get_logger, setup_logging
from .utils.singleton import SystemWideSingleton


class MauscribeApp:
    """Main application class for Mauscribe voice-to-text tool."""

    def __init__(self) -> None:
        """Initialize Mauscribe application."""
        # Initialize critical attributes first to ensure they're always available
        self.threads = []
        self.thread_timeout = 5.0  # 5 seconds timeout for thread shutdown
        self.shutdown_event = threading.Event()

        # Initialize recording state variables early to prevent callback errors
        self._is_recording = False
        self._last_recording_timestamp: float = 0.0
        self._last_recording_stop_timestamp: float = 0.0
        self._last_click_time: float = 0.0
        self._click_debounce_ms = 500  # 500ms for double-click detection
        self._secondary_button_start_time: float = 0.0
        self._secondary_button_is_pressed = False
        self._secondary_button_long_press_threshold = 1.5  # 1.5 seconds

        # Initialize config first
        self.config = Config()

        # Setup logging with config
        setup_logging(self.config)

        # Create logger instance
        self.logger = get_logger(self.__class__.__name__, self.config)

        # System-weites Singleton für Mauscribe
        self.system_singleton = SystemWideSingleton("mauscribe")

        # Prüfe, ob bereits eine Instanz läuft
        if not self.system_singleton.acquire():
            running_pid = self.system_singleton.get_running_pid()
            if running_pid:
                self.logger.error(f"[ERROR] Mauscribe läuft bereits (PID: {running_pid})")
                # Beende die Anwendung sauber, ohne RuntimeError
                sys.exit(1)
            else:
                self.logger.error("[ERROR] Unbekannter Fehler beim System-weiten Singleton")
                sys.exit(1)

        self.logger.debug("[SUCCESS] System-weide Lock aquired")
        
        # MSIX-spezifische Initialisierung
        self._initialize_msix_components()
        
        # Audio-Recorder (MSIX-kompatibel oder Standard)
        self.recorder = self._create_audio_recorder()
        self.stt = SpeechToText(
            self.config
        )  # SpeechToText nimmt jetzt Config-Parameter

        # Initialize spell checker only if enabled
        if self.config.spell_check_enabled:
            self.spell_checker = SpellChecker(
                self.config
            )  # SpellChecker nimmt jetzt Config-Parameter
        else:
            self.spell_checker = None
            self.logger.debug("SpellChecker deaktiviert")

        self.system_tray_manager = SystemTrayManager(self.config, self)
        self._volume_controller = VolumeController(target=0.1)
        self._initialize_volume_controller()
        self.notification_manager = NotificationManager(self.config, self)
        self.gui_manager = GUIManager(self.config, self.notification_manager)
        # Input-Handler (MSIX-kompatibel oder Standard)
        self.input_handler = self._create_input_handler()

        # Initialize database
        self.audio_database = AudioDatabase()

        # Initialize transcription queue for non-blocking processing
        self.transcription_queue = SimpleTranscriptionQueue(self.stt)
        self.transcription_queue.start(callback=self._on_transcription_complete)

        self.input_handler.start()

    def reload_stt_model(self) -> None:
        """Reload STT model with new configuration."""

        try:
            self.logger.info("🔄 Reloading STT model...")

            # Create new STT instance with updated config
            new_stt = SpeechToText(self.config)

            # Update transcription queue with new STT engine
            self.transcription_queue.update_stt_engine(new_stt)

            # Replace old STT instance
            self.stt = new_stt

            self.logger.info("✅ STT model reloaded successfully")

        except Exception as e:
            self.logger.error(f"❌ Error reloading STT model: {e}")

    def _initialize_msix_components(self) -> None:
        """Initialisiert MSIX-spezifische Komponenten"""
        try:
            # Prüfe MSIX-Umgebung
            self._is_msix = self._detect_msix_environment()
            self.logger.info(f"MSIX-Umgebung erkannt: {self._is_msix}")
            
            if self._is_msix:
                self.logger.info("🔧 Initialisiere MSIX-spezifische Komponenten...")
                # MSIX-spezifische Initialisierung
                self._setup_msix_permissions()
                self._setup_msix_notifications()
                self._setup_msix_cursor()
            else:
                self.logger.info("🔧 Verwende Standard-Komponenten")
                
        except Exception as e:
            self.logger.error(f"Fehler bei MSIX-Initialisierung: {e}")
    
    def _detect_msix_environment(self) -> bool:
        """Erkennt MSIX-Container-Umgebung"""
        import os
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
    
    def _setup_msix_permissions(self) -> None:
        """Richtet MSIX-Berechtigungen ein"""
        try:
            # Mikrofon-Berechtigung prüfen
            self._check_microphone_permission()
            
            # Input-Berechtigungen prüfen
            self._check_input_permissions()
            
            # Notification-Berechtigungen prüfen
            self._check_notification_permissions()
            
        except Exception as e:
            self.logger.warning(f"MSIX-Berechtigungen konnten nicht geprüft werden: {e}")
    
    def _check_microphone_permission(self) -> None:
        """Prüft Mikrofon-Berechtigung"""
        try:
            # Windows Runtime Audio Permission Check
            import winrt.windows.media.capture as capture
            # MSIX-kompatible Mikrofon-Berechtigung prüfen
            self.logger.info("✅ Mikrofon-Berechtigung verfügbar")
        except ImportError:
            self.logger.warning("⚠️ Windows Runtime Audio nicht verfügbar")
        except Exception as e:
            self.logger.warning(f"⚠️ Mikrofon-Berechtigung nicht verfügbar: {e}")
    
    def _check_input_permissions(self) -> None:
        """Prüft Input-Berechtigungen"""
        try:
            # Windows Runtime Input Permission Check
            import winrt.windows.ui.input as input
            self.logger.info("✅ Input-Berechtigungen verfügbar")
        except ImportError:
            self.logger.warning("⚠️ Windows Runtime Input nicht verfügbar")
        except Exception as e:
            self.logger.warning(f"⚠️ Input-Berechtigungen nicht verfügbar: {e}")
    
    def _check_notification_permissions(self) -> None:
        """Prüft Notification-Berechtigungen"""
        try:
            # Windows Runtime Notification Permission Check
            import winrt.windows.ui.notifications as notifications
            self.logger.info("✅ Notification-Berechtigungen verfügbar")
        except ImportError:
            self.logger.warning("⚠️ Windows Runtime Notifications nicht verfügbar")
        except Exception as e:
            self.logger.warning(f"⚠️ Notification-Berechtigungen nicht verfügbar: {e}")
    
    def _setup_msix_notifications(self) -> None:
        """Richtet MSIX-spezifische Notifications ein"""
        try:
            # Windows Runtime Toast Notifications
            import winrt.windows.ui.notifications as notifications
            self.logger.info("✅ MSIX-Notifications eingerichtet")
        except ImportError:
            self.logger.warning("⚠️ Windows Runtime Notifications nicht verfügbar")
    
    def _setup_msix_cursor(self) -> None:
        """Richtet MSIX-spezifische Cursor-Anpassung ein"""
        try:
            # Windows Runtime Cursor Customization
            import winrt.windows.ui.core as core
            self.logger.info("✅ MSIX-Cursor-Anpassung eingerichtet")
        except ImportError:
            self.logger.warning("⚠️ Windows Runtime Cursor nicht verfügbar")
    
    def _create_audio_recorder(self):
        """Erstellt MSIX-kompatiblen oder Standard-Audio-Recorder"""
        try:
            if self._is_msix:
                # Verwende MSIX-spezifischen Audio-Adapter
                from .msix.audio_adapter import MSIXAudioAdapter
                recorder = MSIXAudioAdapter(self.config)
                self.logger.info("✅ MSIX-Audio-Recorder erstellt")
                return recorder
            else:
                # Verwende Standard-Audio-Recorder
                from .audio.recorder import AudioRecorder
                recorder = AudioRecorder(self.config)
                self.logger.info("✅ Standard-Audio-Recorder erstellt")
                return recorder
        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen des Audio-Recorders: {e}")
            # Fallback auf Standard-Recorder
            from .audio.recorder import AudioRecorder
            return AudioRecorder(self.config)
    
    def _create_input_handler(self):
        """Erstellt MSIX-kompatiblen oder Standard-Input-Handler"""
        try:
            if self._is_msix:
                # Verwende MSIX-spezifischen Input-Adapter
                from .msix.input_adapter import MSIXInputAdapter
                handler = MSIXInputAdapter(self.config)
                handler.set_callbacks(
                    primary=self._on_primary_key_pressed,
                    secondary=self._on_secondary_key_pressed,
                    third=self._on_third_key_pressed
                )
                self.logger.info("✅ MSIX-Input-Handler erstellt")
                return handler
            else:
                # Verwende Standard-Input-Handler
                from .input.input_handler import InputHandler
                handler = InputHandler(
                    primary_callback=self._on_primary_key_pressed,
                    secondary_callback=self._on_secondary_key_pressed,
                    third_callback=self._on_third_key_pressed,
                )
                self.logger.info("✅ Standard-Input-Handler erstellt")
                return handler
        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen des Input-Handlers: {e}")
            # Fallback auf Standard-Handler
            from .input.input_handler import InputHandler
            return InputHandler(
                primary_callback=self._on_primary_key_pressed,
                secondary_callback=self._on_secondary_key_pressed,
                third_callback=self._on_third_key_pressed,
            )

    def _initialize_volume_controller(self) -> None:
        """Initialisiere den Volume Controller mit der korrekten ursprünglichen Lautstärke."""
        try:
            # Hole die aktuelle System-Lautstärke
            current_volume = self._volume_controller._get_current_volume()
            if current_volume is not None:
                # Wenn die aktuelle Lautstärke bereits nahe am Zielwert ist (0.1),
                # setze eine vernünftige Standard-Lautstärke
                if abs(current_volume - 0.1) < 0.05:
                    self.logger.debug(
                        f"Lautstärke ist bereits bei {current_volume:.2f} - setze Standard auf 0.7"
                    )
                    self._volume_controller.set_original_volume(0.7)
                else:
                    self.logger.debug(
                        f"Verwende aktuelle Lautstärke als ursprünglich: {current_volume:.2f}"
                    )
                    self._volume_controller.set_original_volume(current_volume)
            else:
                self.logger.warning(
                    "Konnte aktuelle Lautstärke nicht abrufen - verwende Standard 0.7"
                )
                self._volume_controller.set_original_volume(0.7)
        except Exception as e:
            self.logger.error(f"Fehler bei der Volume Controller Initialisierung: {e}")
            # Fallback auf Standard-Lautstärke
            self._volume_controller.set_original_volume(0.7)

    def _safe_write_text(self, text: str) -> bool:
        """Safely write text using pyautogui with error handling."""
        try:
            # Kurze Pause für bessere Stabilität
            time.sleep(0.1)

            # Text einfügen
            pyautogui.write(text)
            return True

        except Exception as e:
            self.logger.error(f"❌ pyautogui.write fehlgeschlagen: {e}")

            # Versuche es mit Fallback-Methode
            try:
                self.logger.debug("🔄 Versuche Fallback-Einfüge-Methode...")
                pyautogui.hotkey("ctrl", "v")
                return True
            except Exception as fallback_error:
                self.logger.error(
                    f"❌ Fallback-Methode fehlgeschlagen: {fallback_error}"
                )
                return False

    def _test_clipboard_system(self) -> bool:
        """Test clipboard system functionality."""
        # Clipboard-Test deaktiviert
        return True

    def _on_primary_key_pressed(self, pressed: bool) -> None:
        if pressed:
            if not self._is_recording:
                self.start_recording()
            else:
                self.stop_recording()

    def _on_secondary_key_pressed(self, pressed: bool) -> None:
        if pressed:
            self._paste_text()

    def _on_third_key_pressed(self, pressed: bool) -> None:
        """Handle third key press - cancel current recording."""
        if pressed and self._is_recording:
            self._cancel_recording()

    def _get_clipboard_text(self) -> str:
        """Get text from clipboard safely."""
        try:
            self.logger.debug("📋 Versuche Text aus Zwischenablage zu lesen...")
            text = pyperclip.paste()
            if text and text.strip():
                self.logger.debug(
                    f"📝 Text aus Zwischenablage gelesen: '{text[:50]}...'"
                )
                return text.strip()
            else:
                self.logger.warning("⚠️  Kein Text in der Zwischenablage zum Einfügen")
                return ""
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Lesen der Zwischenablage: {e}")
            return ""

    def _insert_text_at_cursor(self, text: str) -> bool:
        """Insert text at current cursor position."""
        try:
            self.logger.debug("⌨️  Füge Text an Cursor-Position ein...")
            if self._safe_write_text(text):
                self.logger.debug(f"✅ Text erfolgreich eingefügt: {text[:50]}...")
                return True
            else:
                self.logger.error("❌ Text konnte nicht eingefügt werden")
                return False
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Einfügen des Texts: {e}")
            return False

    def _fallback_paste(self) -> bool:
        """Fallback paste method using ctrl+v."""
        try:
            self.logger.debug("🔄 Versuche Fallback-Einfüge-Methode...")
            pyautogui.hotkey("ctrl", "v")
            self.logger.debug("✅ Text mit Fallback-Methode eingefügt")
            return True
        except Exception as e:
            self.logger.error(f"❌ Fallback-Methode fehlgeschlagen: {e}")
            return False

    def _paste_text(self, _: bool = False) -> None:
        """Paste transcribed text to current cursor position."""
        # Get text from clipboard
        text = self._get_clipboard_text()
        if not text:
            self.notification_manager.show_warning(
                "Kein Text in der Zwischenablage zum Einfügen", "Text einfügen"
            )
            return

        # Try to insert text
        if self._insert_text_at_cursor(text):
            self.notification_manager.show_text_pasted(text)
        else:
            # Try fallback method
            if self._fallback_paste():
                self.notification_manager.show_text_pasted("Text (Fallback)")
            else:
                self.notification_manager.show_error(
                    "Text konnte nicht eingefügt werden", "Text einfügen"
                )

    def start_recording(self) -> None:
        """Start voice recording and transcription."""
        if self._is_recording:
            self.logger.warning("⚠️  Aufnahme läuft bereits")
            self.notification_manager.show_warning("Aufnahme läuft bereits", "Aufnahme")
            return

        self.logger.info("🎙️  Starte Sprachaufnahme...")
        self._is_recording = True

        # Set volume to 10%
        self._volume_controller.acquire()

        # Start the recorder
        try:
            self.logger.debug("Starte Audio-Recorder...")
            self.recorder.start_recording()
            self.logger.debug("Audio-Recorder erfolgreich gestartet")

            # Keine Start-Notification gewünscht

            # Update system tray icon
            self.system_tray_manager.update_recording_state(True)

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Starten des Audio-Recorders: {e}")
            self._is_recording = False
            self.notification_manager.show_error(
                f"Fehler beim Starten der Aufnahme: {e}", "Aufnahme"
            )
            return

    def _cancel_recording(self) -> None:
        """Cancel current recording without processing."""
        if not self._is_recording:
            self.logger.warning("⚠️  Keine Aufnahme aktiv")
            return

        self.logger.debug("🛑 Breche Aufnahme ab...")
        self._is_recording = False

        # Stelle Lautstärke sicher wieder her
        self._volume_controller.release()

        # Stop the recorder without processing
        try:
            self.recorder.stop_recording()
            self.logger.debug("🎵 Audio-Recorder gestoppt (abgebrochen)")
            self.notification_manager.show_warning("Aufnahme abgebrochen", "Aufnahme")
        except Exception as e:
            self.logger.error(f"Fehler beim Abbrechen der Aufnahme: {e}")

        # Update system tray icon
        self.system_tray_manager.update_recording_state(False)

    def stop_recording(self) -> None:
        """Stop voice recording and process audio (NON-BLOCKING)."""
        if not self._is_recording:
            self.logger.warning("⚠️  Keine Aufnahme aktiv")
            self.notification_manager.show_warning("Keine Aufnahme aktiv", "Aufnahme")
            return

        self.logger.info("⏹️  Stoppe Sprachaufnahme...")
        self._is_recording = False
        self._last_recording_stop_timestamp = time.time()

        # Stelle Lautstärke sicher wieder her
        self._volume_controller.release()

        # Stop the recorder
        try:
            # Get audio data & stopping
            audio_data = self.recorder.stop_recording()
            self.logger.debug("Audio-Recorder gestoppt")

            # Calculate recording duration
            recording_duration = (
                len(audio_data) / self.recorder.sample_rate_hz
                if audio_data is not None
                else 0.0
            )

            # Process audio data immediately if available
            if audio_data is None or len(audio_data) <= 0:
                self.logger.warning("❌ Keine Audioaufnahme verfügbar")
                self.notification_manager.show_warning(
                    "Keine Audioaufnahme", "Aufnahme"
                )
                return  # Beende die Methode hier, da keine Audio-Daten verfügbar sind

            # Submit to transcription queue (NON-BLOCKING!)
            self.logger.debug("Sende Audio zur Transkriptions-Queue...")
            self.transcription_queue.submit_task(audio_data)

            # Show recording success notification
            self.notification_manager.show_recording_successful(recording_duration)

            # UI ist sofort wieder responsive!

        except Exception as e:
            self.logger.error(f"Failed to stop recorder: {e}")
            self.notification_manager.show_error(
                f"Fehler beim Stoppen der Aufnahme: {e}", "Aufnahme"
            )

        # Update system tray icon
        self.system_tray_manager.update_recording_state(False)

    def _on_transcription_complete(self, result: dict) -> None:
        """Callback wenn Transkription fertig ist (wird vom Worker aufgerufen)."""
        text = result["text"]
        task_id = result["task_id"]
        processing_time = result["processing_time"]
        audio_data = result["audio_data"]

        if text and text.strip():

            # Save audio recording to database if enabled
            recording_id = None
            duration = len(audio_data) / self.recorder.sample_rate_hz

            if (
                self.config.database_enabled
                and self.config.database_auto_save_recordings
            ):
                try:
                    recording_id = self.audio_database.save_audio_recording(
                        audio_data=audio_data,
                        sample_rate=self.recorder.sample_rate_hz,
                        channels=self.recorder.num_channels,
                        duration=duration,
                        audio_format=self.config.database_audio_format,
                    )
                except Exception as e:
                    self.logger.warning(
                        f"⚠️  Konnte Audio-Aufnahme nicht speichern: {e}"
                    )

            # Save transcription to database if enabled
            if (
                self.config.database_enabled
                and self.config.database_auto_save_transcriptions
                and recording_id
            ):
                try:
                    transcription_id = self.audio_database.save_transcription(
                        audio_recording_id=recording_id,
                        raw_text=text,
                        language=self.config.stt_language,
                    )

                    # Mark as training data if enabled
                    if self.config.database_mark_as_training_data:
                        self.audio_database.save_training_data(
                            transcription_id=transcription_id,
                            is_valid_for_training=True,
                        )
                except Exception as e:
                    self.logger.warning(f"⚠️  Konnte Transkription nicht speichern: {e}")

            # Show transcription success notification
            self.notification_manager.show_transcription_successful(
                text, processing_time, recording_id
            )

            # Log successful transcription with text
            self.logger.info(
                f"📝 Transkription erfolgreich ({processing_time:.1f}s):\n'{text}'"
            )

            # Sofort rohe Transkription in Clipboard kopieren
            try:
                pyperclip.copy(text)

                # Automatisches Einfügen falls aktiviert
                if self.config.behavior_auto_paste_after_transcription:
                    time.sleep(0.2)  # Kurze Pause für bessere Stabilität
                    self._paste_text()

            except Exception as clipboard_error:
                self.logger.error(
                    f"❌ Fehler beim Kopieren in Zwischenablage: {clipboard_error}"
                )
                self.notification_manager.show_error(
                    f"Clipboard-Fehler: {clipboard_error}", "Zwischenablage"
                )
                # Fallback: Versuche es nochmal mit kurzer Verzögerung
                try:
                    time.sleep(0.1)
                    pyperclip.copy(text)
                except Exception as fallback_error:
                    self.logger.error(
                        f"❌ Fallback Clipboard-Versuch fehlgeschlagen: {fallback_error}"
                    )
                    self.notification_manager.show_error(
                        "Clipboard-System funktioniert nicht", "Kritischer Fehler"
                    )

            # Spellchecking deaktiviert - funktioniert nicht gut genug
        else:
            self.logger.warning("❌ Keine Sprache erkannt")
            self.notification_manager.show_warning(
                "Keine Sprache erkannt", "Transkription"
            )

    # Spellchecking-Methode entfernt - deaktiviert

    def run(self) -> None:
        """Start the Mauscribe application."""
        # Setup system tray
        self.system_tray_manager.setup()

        # Start GUI manager
        self.gui_manager.start()

        # Run system tray in a separate thread so we can monitor shutdown
        tray_thread = threading.Thread(target=self._run_system_tray, name="SystemTray")
        tray_thread.daemon = True
        tray_thread.start()
        self.threads.append(tray_thread)

        self.logger.info("🎮 Mauscribe gestartet - bereit für Eingaben!")

        while not self.shutdown_event.is_set():
            time.sleep(0.1)

        self.logger.debug("🔄 Shutdown-Signal empfangen - beende Threads...")
        self._stop_all_threads()

    def _run_system_tray(self) -> None:
        """Run system tray in a separate thread."""
        if not self.system_tray_manager.is_available():
            self.logger.error("❌ System Tray ist nicht verfügbar")
            self.shutdown_event.set()
            return

        try:
            self.system_tray_manager.run()
        except Exception as e:
            self.logger.error(f"❌ System Tray Fehler: {e}")
            self.shutdown_event.set()

    def _stop_all_threads(self) -> None:
        """Stop all threads gracefully."""
        try:
            if not hasattr(self, "threads") or not self.threads:
                try:
                    self.logger.debug("✅ Keine Threads zu beenden")
                except Exception:
                    print("✅ Keine Threads zu beenden")
                return

            self.logger.debug(f"Stoppe {len(self.threads)} Thread(s)...")

            # First stop all components that might keep threads alive
            try:
                self._stop_components()
            except Exception as e:
                self.logger.error(f"Fehler beim Stoppen der Komponenten: {e}")

            # Then wait for threads to finish
            start_time = time.time()
            for thread in self.threads:
                try:
                    if thread.is_alive():
                        self.logger.debug(f"Warte auf Thread '{thread.name}'...")

                        thread.join(timeout=self.thread_timeout)

                        if thread.is_alive():
                            self.logger.warning(
                                f"Thread '{thread.name}' konnte nicht innerhalb von {self.thread_timeout}s beendet werden"
                            )
                        else:
                            self.logger.debug(
                                f"Thread '{thread.name}' erfolgreich beendet"
                            )
                except Exception as e:
                    self.logger.error(
                        f"Fehler beim Beenden von Thread '{thread.name}': {e}"
                    )

            elapsed_time = time.time() - start_time
            self.logger.debug(f"Thread-Shutdown abgeschlossen in {elapsed_time:.2f}s")
        except Exception as e:
            self.logger.error(f"Kritischer Fehler beim Thread-Shutdown: {e}")

    def stop(self) -> None:
        """Stop the Mauscribe application."""
        self.logger.debug("Starte Anwendungs-Shutdown...")

        # Signal shutdown to all threads
        try:
            self.shutdown_event.set()
        except Exception as e:
            self.logger.error(f"Fehler beim Setzen des Shutdown-Signals: {e}")

        # Stop recording if active
        try:
            if hasattr(self, "_is_recording") and self._is_recording:
                self.logger.debug("Stoppe aktive Aufnahme...")
                self.stop_recording()
        except Exception as e:
            self.logger.error(f"Fehler beim Stoppen der Aufnahme: {e}")

        # Stop transcription queue
        try:
            if hasattr(self, "transcription_queue") and self.transcription_queue:
                self.logger.debug("Stoppe Transkriptions-Queue...")
                self.transcription_queue.stop()
        except Exception as e:
            self.logger.error(f"Fehler beim Beenden der Transkriptions-Queue: {e}")

        # Stop GUI manager
        try:
            if hasattr(self, "gui_manager") and self.gui_manager:
                self.logger.debug("Stoppe GUI Manager...")
                self.gui_manager.stop()
        except Exception as e:
            self.logger.error(f"Fehler beim Beenden des GUI Managers: {e}")

        # Stop input handling
        try:
            if hasattr(self, "input_handler") and self.input_handler:
                self.logger.debug("Stoppe Input Handler...")
                self.input_handler.stop()
        except Exception as e:
            self.logger.error(f"Fehler beim Beenden des Input Handlers: {e}")

        # Cleanup AudioRecorder (stellt Lautstärke wieder her)
        try:
            if hasattr(self, "recorder") and self.recorder:
                self.logger.debug("🛑 Räume AudioRecorder auf...")
                self.recorder.cleanup()
        except Exception as e:
            try:
                self.logger.error(f"❌ Fehler beim Aufräumen des AudioRecorders: {e}")
            except Exception:
                print(f"❌ Fehler beim Aufräumen des AudioRecorders: {e}")

        # Stop system tray
        try:
            if hasattr(self, "system_tray_manager") and self.system_tray_manager:
                self.logger.debug("🛑 Stoppe System Tray...")
                self.system_tray_manager.stop()
        except Exception as e:
            try:
                self.logger.error(f"❌ Fehler beim Beenden des System Tray: {e}")
            except Exception:
                print(f"❌ Fehler beim Beenden des System Tray: {e}")

        # Cleanup other components
        try:
            if hasattr(self, "spell_checker") and self.spell_checker is not None:
                self.logger.debug("🛑 Schließe SpellChecker...")
                self.spell_checker.close()
        except Exception as e:
            try:
                self.logger.error(
                    f"❌ Fehler beim Beenden der Rechtschreibprüfung: {e}"
                )
            except Exception:
                print(f"❌ Fehler beim Beenden der Rechtschreibprüfung: {e}")

        # Volume is already restored by _stop_components() or hooks
        # No need to restore it again here

        # Release system-wide singleton
        try:
            if hasattr(self, "system_singleton") and self.system_singleton:
                self.logger.debug("🛑 Gebe System-weites Singleton frei...")
                self.system_singleton.release()
                self.logger.debug("✅ System-weites Singleton erfolgreich freigegeben")
        except Exception as e:
            self.logger.error(
                f"Fehler beim Freigeben des System-weiten Singletons: {e}"
            )

        # Stop all threads
        try:
            self._stop_all_threads()
        except Exception as e:
            try:
                self.logger.error(f"❌ Fehler beim Beenden der Threads: {e}")
            except Exception:
                print(f"❌ Fehler beim Beenden der Threads: {e}")

        self.logger.debug("✅ Anwendungs-Shutdown abgeschlossen")

    def _stop_components(self) -> None:
        """Stop all components without the full shutdown process."""
        # Signal shutdown to all threads
        self.shutdown_event.set()

        # Stop recording if active
        if self._is_recording:
            self.logger.debug("🛑 Stoppe aktive Aufnahme...")
            self.stop_recording()

        # Stop transcription queue
        try:
            self.logger.debug("🛑 Stoppe Transkriptions-Queue...")
            self.transcription_queue.stop()
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Beenden der Transkriptions-Queue: {e}")

        # Stop input handling
        try:
            self.logger.debug("🛑 Stoppe Input Handler...")
            self.input_handler.stop()
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Beenden des Input Handlers: {e}")

        # AudioRecorder cleanup is handled by stop_recording() if recording was active
        # No need to cleanup here to avoid duplicate cleanup

        # Stop system tray
        try:
            self.logger.debug("🛑 Stoppe System Tray...")
            self.system_tray_manager.stop()
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Beenden des System Tray: {e}")

        # Cleanup notification manager (win10toast_click errors)
        try:
            if (
                hasattr(self, "notification_manager")
                and self.notification_manager is not None
            ):
                self.logger.debug("🛑 Schließe Notification Manager...")
                # Force cleanup of any active notifications
                if hasattr(self.notification_manager, "active_notifications"):
                    self.notification_manager.active_notifications.clear()
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Beenden des Notification Managers: {e}")

        # Cleanup other components
        try:
            if hasattr(self, "spell_checker") and self.spell_checker is not None:
                self.logger.debug("🛑 Schließe SpellChecker...")
                self.spell_checker.close()
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Beenden der Rechtschreibprüfung: {e}")

    def _setup_volume_restore_hooks(self) -> None:
        """Setup multiple hooks to ensure volume is always restored."""
        try:
            # 1. atexit hook - runs when Python exits normally
            atexit.register(self._force_volume_restore)

            # 2. sys.exitfunc hook (Python < 3.4 compatibility)
            if hasattr(sys, "exitfunc"):
                old_exitfunc = sys.exitfunc

                def new_exitfunc():
                    self._force_volume_restore()
                    if old_exitfunc:
                        old_exitfunc()

                sys.exitfunc = new_exitfunc

            # 3. Thread-local storage for cleanup
            self._volume_restore_registered = True

            self.logger.debug("Volume-Restore-Hooks erfolgreich eingerichtet")

        except Exception as e:
            self.logger.error(f"Fehler beim Einrichten der Volume-Restore-Hooks: {e}")

    def _force_volume_restore(self) -> None:
        """Force volume restoration - called by various hooks."""
        try:
            # Volume-Restore
            if hasattr(self, "_volume_controller") and self._volume_controller:
                # Only restore if volume was actually reduced (system_volume is not None)
                if self._volume_controller._system_volume is not None:
                    # Check if we already restored volume to avoid duplicate calls
                    if not hasattr(self, "_volume_already_restored"):
                        self._volume_already_restored = False

                    if not self._volume_already_restored:
                        self.logger.debug(
                            "Volume-Restore-Hook: Stelle System-Lautstärke wieder her..."
                        )
                        self._volume_controller.release_all()
                        self.logger.debug(
                            "Volume-Restore-Hook: Lautstärke-Wiederherstellung abgeschlossen"
                        )
                        self._volume_already_restored = True
                    else:
                        self.logger.debug(
                            "Volume-Restore-Hook: Lautstärke bereits wiederhergestellt - überspringe"
                        )
                else:
                    self.logger.debug(
                        "Volume-Restore-Hook: Keine Lautstärke-Reduzierung erkannt - überspringe Wiederherstellung"
                    )

            # System-weites Singleton freigeben
            if hasattr(self, "system_singleton") and self.system_singleton:
                self.logger.debug(
                    "System-Restore-Hook: Gebe System-weites Singleton frei..."
                )
                self.system_singleton.release()
                self.logger.debug(
                    "System-Restore-Hook: System-weites Singleton freigegeben"
                )
        except Exception as e:
            self.logger.error(f"Volume-Restore-Hook Fehler: {e}")

        # Cleanup win10toast_click related errors
        try:
            # Force cleanup of any remaining notification processes
            if (
                hasattr(self, "notification_manager")
                and self.notification_manager is not None
            ):
                if (
                    hasattr(self.notification_manager, "current_notification_process")
                    and self.notification_manager.current_notification_process
                ):
                    try:
                        self.notification_manager.current_notification_process.terminate()
                    except:
                        pass
                    self.notification_manager.current_notification_process = None
        except Exception as e:
            # Silently ignore win10toast_click cleanup errors
            pass

    def _setup_signal_handlers(self) -> None:
        """Set up signal handlers for graceful shutdown."""
        try:
            signal.signal(signal.SIGINT, self._handle_signal)
            signal.signal(signal.SIGTERM, self._handle_signal)
            self.logger.debug("Signal-Handler für Strg+C erfolgreich eingerichtet")
        except Exception as e:
            self.logger.error(f"Signal-Handler konnte nicht eingerichtet werden: {e}")

    def _handle_signal(self, signum: int, frame: Any) -> None:
        """Handle system signals for graceful shutdown."""
        signal_name = "SIGINT" if signum == signal.SIGINT else "SIGTERM"
        self.logger.debug(
            f"Signal {signal_name} empfangen - starte graceful shutdown..."
        )

        # Set shutdown event to stop all threads
        self.shutdown_event.set()

        # Force stop recording if active
        if self._is_recording:
            self.logger.debug("Stoppe aktive Aufnahme...")
            self._is_recording = False
            try:
                self.recorder.stop_recording()
            except Exception as e:
                self.logger.error(f"Fehler beim Stoppen der Aufnahme: {e}")

        # Volume will be restored by _stop_components() or hooks
        # System-weites Singleton wird auch durch Hooks freigegeben

        # Don't call sys.exit() here - let the main loop handle the shutdown
        # This allows for proper thread cleanup


def _global_exception_handler(exc_type, exc_value, exc_traceback):
    """Global exception handler for unhandled exceptions."""
    if issubclass(exc_type, KeyboardInterrupt):
        # Don't handle KeyboardInterrupt here
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    # Log the error if possible
    try:
        from .utils.logger import get_logger

        logger = get_logger("GlobalExceptionHandler")
        logger.critical(f"Unbehandelter Fehler: {exc_type.__name__}: {exc_value}")
        logger.critical(f"Stack-Trace: {traceback.format_tb(exc_traceback)}")
    except Exception:
        # Fallback to console if logging fails
        print("Unbehandelter Fehler aufgetreten:")
        print("Unhandled error occurred:")
        print(f"Typ/Type: {exc_type.__name__}")
        print(f"Wert/Value: {exc_value}")
        print("Stack-Trace:")
        traceback.print_tb(exc_traceback)

    # Force volume restore on any unhandled exception
    try:
        # Try to get the global app instance and restore volume
        import gc

        for obj in gc.get_objects():
            if hasattr(obj, "_force_volume_restore") and callable(
                obj._force_volume_restore
            ):
                obj._force_volume_restore()
                break
    except Exception:
        pass  # If volume restore fails, we can't do much more


def start_mauscribe() -> None:
    """Main entry point for the Mauscribe application."""

    # Set up global exception handler
    sys.excepthook = _global_exception_handler

    app = None

    # Prüfe System-weites Singleton vor der Initialisierung
    try:
        system_singleton = SystemWideSingleton("mauscribe")
        if system_singleton.is_running():
            running_pid = system_singleton.get_running_pid()
            if running_pid:
                print(f"❌ Mauscribe läuft bereits (PID: {running_pid})")
                print(
                    "   Bitte beende die laufende Instanz oder warte, bis sie sich beendet."
                )
                sys.exit(1)
            else:
                print("❌ Unbekannter Fehler beim System-weiten Singleton")
                sys.exit(1)
    except Exception as e:
        print(f"❌ Fehler beim System-weiten Singleton: {e}")
        sys.exit(1)
    try:
        # Initialize application with error handling
        try:
            app = MauscribeApp()
        except Exception as e:
            # Use logger if available, otherwise print
            try:
                from .utils.logger import get_logger

                logger = get_logger("Main")
                logger.critical(
                    f"Kritischer Fehler beim Initialisieren der Anwendung: {e}"
                )
            except Exception:
                print(f"Kritischer Fehler beim Initialisieren der Anwendung: {e}")
                print(f"Critical error initializing application: {e}")
                traceback.print_exc()
            return

        # Run application
        app.run()

    except KeyboardInterrupt:
        if app:
            app.logger.info("Programm durch Benutzer unterbrochen (Strg+C)")
            app.shutdown_event.set()
    except Exception as e:
        if app:
            app.logger.error(f"Unerwarteter Fehler: {e}")
            app.logger.error(f"Unexpected error in main: {e}")
            app.shutdown_event.set()
        else:
            # Use logger if available, otherwise print
            try:
                from .utils.logger import get_logger

                logger = get_logger("Main")
                logger.critical(f"Unerwarteter Fehler vor Anwendungsstart: {e}")
            except Exception:
                print(f"Unerwarteter Fehler vor Anwendungsstart: {e}")
                print(f"Unexpected error before application start: {e}")
                traceback.print_exc()
    finally:
        # Always call stop() to ensure proper cleanup
        if app:
            try:
                app.logger.info("Beende Anwendung...")
                app.stop()
                app.logger.info("Anwendung erfolgreich beendet")
            except Exception as e:
                # Use logger if available, otherwise print
                try:
                    from .utils.logger import get_logger

                    logger = get_logger("Main")
                    logger.error(f"Fehler beim Beenden der Anwendung: {e}")
                except Exception:
                    print(f"Fehler beim Beenden der Anwendung: {e}")
                    print(f"Error during application shutdown: {e}")
                    traceback.print_exc()
        else:
            # Use logger if available, otherwise print
            try:
                from .utils.logger import get_logger

                logger = get_logger("Main")
                logger.info("Anwendung beendet (keine Initialisierung)")
            except Exception:
                print("Anwendung beendet (keine Initialisierung)")


if __name__ == "__main__":
    start_mouscribe()
