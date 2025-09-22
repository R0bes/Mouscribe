# src/main.py - Main application entry point for Mauscribe
"""
Mauscribe - Voice-to-Text Tool
Main application logic and core functionality
"""
import signal
import sys
import threading
import time
from typing import Any, Literal, Optional

import numpy as np
import pyautogui
import pyperclip
from pydantic import Field

from .audio.computer_agent import ComputerAgent
from .audio.hotword_detector import HotWordDetector
from .audio.multi_transcriptor import MultiTranscriptor
from .audio.recorder import Recorder
from .audio.transcriptor import Transcriptor
from .audio.volumizer import Volumizer
from .ui.notifications import Toaster
from .ui.system_tray import SysTray
from .ui.widgets import MouseOverlayManager, RecordingWidget, TextWidget, WidgetConfig
from .utils import AudioDatabase, Settings, get_logger, setup_logging
from .utils.controlls import ControllsManager
from .utils.input_system import InputSystem, create_insert_command, create_recording_command

# TranscriptionWidgetManager import removed - widgets disabled


class AppSettings(Settings):
    """Application metadata settings."""

    app_name: str = Field(default="Mauscribe", description="Application name")
    version: str = Field(default="1.0.0", description="Application version")
    name: str = Field(default="x2", description="Key/Button name")
    type: str = Field(default="click", description="Input type")
    model_config = {"env_prefix": "MAUSCRIBE_APP_"}


class MauscribeApp:
    """Main application class for Mauscribe voice-to-text tool."""

    def __init__(self) -> None:
        """Initialize Mauscribe application."""
        # Initialize settings first
        self.config = Settings()

        # Setup logging
        setup_logging()

        # Create logger instance
        self.logger = get_logger(self.__class__.__name__, self.config)
        self.logger.info("🚀 Starte Mauscribe...")

        self.logger.info("🔧 Initialisiere Komponenten...")

        self.systray = SysTray(self.config, self)
        self.recorder = Recorder()
        # Initialize transcriptor with simplified settings
        self.transcriptor = MultiTranscriptor(
            model=self.config.model, language=self.config.language, auto_detect_language=self.config.auto_detect_language
        )
        # Initialize volume controller with simplified settings
        volume_reduction_factor = float(self.config.volume_reduction_factor)
        self.volume_controller = Volumizer(reduction_factor=volume_reduction_factor, min_volume=10, enabled=True)
        self.overlay_manager = MouseOverlayManager()

        # Initialize Hot Word Detector (alte Version)
        self.hotword_detector = HotWordDetector(self._on_start_word_detected, self._on_stop_word_detected)

        # Initialize Computer Agent (neue Version)
        computer_agent_config = self.config.hotword.get("computer_agent", {})
        self.computer_agent = ComputerAgent(
            sample_rate=computer_agent_config.get("sample_rate", 16000),
            channels=1,
            buffer_duration=computer_agent_config.get("buffer_duration", 6.0),
            chunk_size=1024,
        )
        # Initialize toaster with notification settings
        # Load notification settings directly from TOML to ensure correct values
        # Initialize simplified notification system
        self.toaster = Toaster(
            enable_sound=self.config.sound,
            default_duration=1000,  # Changed from 3000 to 1000 (1 second)
            enabled=True,
            notification_settings={"toast": self.config.toast},
        )

        self.logger.info("🔊 Notification-System initialisiert:")
        self.logger.info(f"   - Sound: {self.config.sound}")
        self.logger.info(f"   - Toast: {self.config.toast}")
        # Initialize new input system
        self.input_system = InputSystem()

        # Add commands
        self.input_system.add_command(create_recording_command(self.on_primary_action))
        self.input_system.add_command(create_insert_command(self.on_insert_action))

        # Transcription widgets disabled - using only beautiful toast notifications

        # Keep old controls for compatibility
        self.controlls = ControllsManager(
            config=self.config,
            primary_callback=self.on_primary_action,
            secondary_callback=self.on_secondary_action,
            insert_callback=self.on_insert_action,
        )

        self.overlay_manager.register_widget("recording", TextWidget("Test"), "left", 0.5)

        # Initialize database
        self.audio_database = AudioDatabase()

        # Start controls manager if enabled
        if self.config.input.get("enabled", True):
            self.controlls.start()
            # Start new input system
            self.input_system.start()
        else:
            self.logger.info("🔇 Input-Steuerung deaktiviert")

        # Start Hot Word Detection if enabled
        self._start_hotword_detection()

        # Start Computer Agent if enabled
        self._start_computer_agent()

        self.logger.info("✅ Alle Komponenten initialisiert")

        # Initialize recording state variables
        self._is_recording = False
        self._last_recording_timestamp: float = 0.0
        self._last_paste_time = 0  # Debounce für Text-Einfügen
        self._last_recording_stop_timestamp: float = 0.0

        # Initialize double-click enter functionality
        self._double_click_window_active = False
        self._double_click_window_start_time: float = 0.0
        self._last_secondary_action_position: tuple[int, int] = (0, 0)
        self._double_click_window_duration = 3.0  # 3 seconds window
        self._double_click_max_distance = 50  # pixels

        self.shutdown_event = threading.Event()

        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()

    def on_primary_action(self) -> None:
        """Handle primary button action (x2 button) - toggle recording."""
        self.logger.info("🎮 X2-Taste gedrückt - Aufnahme starten/stoppen")
        if not self._is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def on_secondary_action(self) -> None:
        """Handle secondary button action (left mouse) - handle double-click enter."""
        self.logger.info("🎮 Linke Maustaste gedrückt - prüfe Doppelklick-Enter-Modus")

        # Prüfe ob Doppelklick-Enter-Modus aktiv ist
        self._handle_double_click_enter()

    def on_insert_action(self) -> None:
        """Handle insert combination action (left mouse held + x2 button) - stop recording and paste text."""
        self.logger.info("🎮 Kombination gedrückt (linke Maustaste + X2-Taste) - Aufnahme stoppen und Text einfügen")
        if self._is_recording:
            self.stop_recording()
            # Warte kurz, damit die Aufnahme verarbeitet wird
            import time

            time.sleep(0.5)
            self._paste_text()
        else:
            self.logger.info("⚠️ Keine aktive Aufnahme - nur Text einfügen")
            self._paste_text()

    def _check_double_click_window(self) -> None:
        """Check if double-click window is active and handle double-clicks."""
        if not self._double_click_window_active:
            return

        # Check if window has expired
        current_time = time.time()
        if current_time - self._double_click_window_start_time > self._double_click_window_duration:
            self.logger.info("⏰ Doppelklick-Fenster abgelaufen")
            self._double_click_window_active = False
            self.toaster.show_info("Doppelklick-Fenster", "Abgelaufen")
            return

        # Check for mouse clicks in the vicinity
        try:
            # Check if left mouse button is pressed
            if pyautogui.mouseDown(button="left"):
                current_pos = pyautogui.position()
                distance = (
                    (current_pos.x - self._last_secondary_action_position[0]) ** 2
                    + (current_pos.y - self._last_secondary_action_position[1]) ** 2
                ) ** 0.5

                if distance <= self._double_click_max_distance:
                    # Wait for mouse release
                    while pyautogui.mouseDown(button="left"):
                        time.sleep(0.01)

                    # Check for second click within short time
                    time.sleep(0.1)  # Small delay to detect double-click
                    if pyautogui.mouseDown(button="left"):
                        # Second click detected - simulate Enter
                        self.logger.info("⌨️ Doppelklick erkannt - simuliere Enter-Druck...")
                        pyautogui.press("enter")
                        self.logger.info("✅ Enter-Druck simuliert")
                        self.toaster.show_success("Enter gedrückt", "Doppelklick erkannt")

                        # Deactivate window
                        self._double_click_window_active = False

                        # Wait for second click to finish
                        while pyautogui.mouseDown(button="left"):
                            time.sleep(0.01)

        except Exception as e:
            self.logger.error(f"❌ Fehler bei Doppelklick-Überprüfung: {e}")

    # Widget copy method removed - widgets disabled

    def _on_start_word_detected(self, start_word: str) -> None:
        """Handle start word detection."""
        self.logger.info(f"🎯 Start Word erkannt: '{start_word}'")

        # Zeige Benachrichtigung
        self.toaster.show_info("🎯 Start Word erkannt", f"'{start_word}' - Starte Aufnahme...")

        # Starte automatisch die Aufnahme
        if not self._is_recording:
            self.start_recording()
        else:
            self.logger.info("⚠️ Aufnahme läuft bereits - ignoriere Start Word")

    def _on_stop_word_detected(self, stop_word: str) -> None:
        """Handle stop word detection."""
        self.logger.info(f"🛑 Stop Word erkannt: '{stop_word}'")

        # Zeige Benachrichtigung
        self.toaster.show_info("🛑 Stop Word erkannt", f"'{stop_word}' - Stoppe Aufnahme...")

        # Stoppe automatisch die Aufnahme
        if self._is_recording:
            self.stop_recording()
        else:
            self.logger.info("⚠️ Keine aktive Aufnahme - ignoriere Stop Word")

    def _start_hotword_detection(self) -> None:
        """Starte Hot Word Detection falls aktiviert."""
        try:
            # Prüfe ob Hotword Detection aktiviert ist
            if not self.config.hotword.get("enabled", False):
                self.logger.info("🔇 Hotword Detection deaktiviert")
                return

            # Prüfe ob Input-Steuerung aktiviert ist
            if not self.config.input.get("enabled", True):
                self.logger.info("🔇 Input-Steuerung deaktiviert")
                return

            if self.hotword_detector.start_listening():
                self.logger.info("✅ Hot Word Detection gestartet")
            else:
                self.logger.info("🔇 Hot Word Detection deaktiviert oder nicht verfügbar")
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Starten der Hot Word Detection: {e}")

    def _start_computer_agent(self) -> None:
        """Starte Computer Agent falls aktiviert."""
        try:
            # Prüfe ob Computer Agent aktiviert ist
            computer_agent_config = self.config.hotword.get("computer_agent", {})
            if not computer_agent_config.get("enabled", False):
                self.logger.info("🔇 Computer Agent deaktiviert")
                return

            if self.computer_agent.start():
                self.logger.info("✅ Computer Agent gestartet")
            else:
                self.logger.info("🔇 Computer Agent konnte nicht gestartet werden")
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Starten des Computer Agents: {e}")

    def toggle_hotword_detection(self) -> bool:
        """Schalte Hot Word Detection ein/aus."""
        try:
            if self.hotword_detector.is_active():
                self.hotword_detector.stop_listening()
                self.logger.info("🔇 Hot Word Detection deaktiviert")
                self.toaster.show_info("Hot Word Detection", "Deaktiviert")
                return False
            else:
                if self.hotword_detector.start_listening():
                    self.logger.info("🎯 Hot Word Detection aktiviert")
                    self.toaster.show_info("Hot Word Detection", "Aktiviert")
                    return True
                else:
                    self.logger.warning("⚠️ Hot Word Detection konnte nicht gestartet werden")
                    self.toaster.show_warning("Hot Word Detection", "Konnte nicht gestartet werden")
                    return False
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Umschalten der Hot Word Detection: {e}")
            self.toaster.show_error("Hot Word Detection", f"Fehler: {e}")
            return False

    def get_hotword_status(self) -> dict[str, Any]:
        """Gib Status der Hot Word Detection zurück."""
        return self.hotword_detector.get_stats()

    def toggle_computer_agent(self) -> bool:
        """Schalte Computer Agent ein/aus."""
        try:
            if self.computer_agent.is_recording:
                self.computer_agent.stop()
                self.logger.info("🔇 Computer Agent deaktiviert")
                self.toaster.show_info("Computer Agent", "Deaktiviert")
                return False
            else:
                if self.computer_agent.start():
                    self.logger.info("🎯 Computer Agent aktiviert")
                    self.toaster.show_info("Computer Agent", "Aktiviert")
                    return True
                else:
                    self.logger.warning("⚠️ Computer Agent konnte nicht gestartet werden")
                    self.toaster.show_warning("Computer Agent", "Konnte nicht gestartet werden")
                    return False
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Umschalten des Computer Agents: {e}")
            self.toaster.show_error("Computer Agent", f"Fehler: {e}")
            return False

    def get_computer_agent_status(self) -> dict[str, Any]:
        """Gib Status des Computer Agents zurück."""
        return self.computer_agent.get_status()

    def _safe_write_text(self, text: str) -> bool:
        """Safely write text to current cursor position."""
        try:
            # Use pyautogui for safe text input
            pyautogui.write(text)
            return True
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Schreiben des Textes: {e}")
            return False

    def _paste_text(self, _: bool = False) -> None:
        """Paste transcribed text to current cursor position."""
        try:
            # Debounce: Verhindere doppeltes Einfügen innerhalb von 1 Sekunde
            import time

            current_time = time.time()
            if current_time - self._last_paste_time < 1.0:
                self.logger.warning("⚠️ Text-Einfügen ignoriert (Debounce)")
                return
            self._last_paste_time = current_time

            self.logger.info("📋 Versuche Text aus Zwischenablage zu lesen...")
            text = pyperclip.paste()

            if text and text.strip():
                self.logger.info(f"📝 Text aus Zwischenablage gelesen: '{text[:50]}...'")
                self.logger.info("⌨️  Füge Text an Cursor-Position ein...")

                # Verwende sichere Text-Eingabe
                if self._safe_write_text(text):
                    self.logger.info(f"✅ Text erfolgreich eingefügt: {text[:50]}...")

                    # Aktiviere Doppelklick-Enter-Modus für 3 Sekunden
                    self._activate_double_click_enter_mode()

                    self.toaster.show_info("📋 Text eingefügt", f"'{text[:50]}...'")
                else:
                    self.logger.error("❌ Text konnte nicht eingefügt werden")
                    self.toaster.show_error("Text konnte nicht eingefügt werden", "Text einfügen")

            else:
                self.logger.warning("⚠️  Kein Text in der Zwischenablage zum Einfügen")
                self.toaster.show_warning("Kein Text in der Zwischenablage zum Einfügen", "Text einfügen")

        except Exception as e:
            self.logger.error(f"❌ Text konnte nicht eingefügt werden: {e}")
            self.logger.error(f"🔍 Exception Details: {type(e).__name__}: {e}")

            # Versuche es mit Fallback-Methode
            try:
                self.logger.info("🔄 Versuche Fallback-Einfüge-Methode...")
                # Verwende pyautogui.hotkey für bessere Kompatibilität
                pyautogui.hotkey("ctrl", "v")
                self.logger.info("✅ Text mit Fallback-Methode eingefügt")
                self.toaster.show_info("📋 Text eingefügt", "Text (Fallback)")
            except Exception as fallback_error:
                self.logger.error(f"❌ Fallback-Einfüge-Methode fehlgeschlagen: {fallback_error}")
                self.toaster.show_error("Text konnte nicht eingefügt werden", "Kritischer Fehler")

    def _activate_double_click_enter_mode(self) -> None:
        """Aktiviere Doppelklick-Enter-Modus für 3 Sekunden."""
        import time

        self._double_click_window_active = True
        self._double_click_window_start_time = time.time()
        self.logger.info("🖱️ Doppelklick-Enter-Modus aktiviert (3 Sekunden)")

        # Deaktiviere nach 3 Sekunden automatisch
        def deactivate():
            time.sleep(3.0)
            if self._double_click_window_active:
                self._double_click_window_active = False
                self.logger.info("🖱️ Doppelklick-Enter-Modus deaktiviert")

        import threading

        threading.Thread(target=deactivate, daemon=True).start()

    def _handle_double_click_enter(self) -> None:
        """Behandle Doppelklick für Enter-Drücken."""
        if self._double_click_window_active:
            import time

            current_time = time.time()
            if current_time - self._double_click_window_start_time <= 3.0:
                self.logger.info("⏎ Doppelklick erkannt - drücke Enter...")
                pyautogui.press("enter")
                self._double_click_window_active = False
                self.logger.info("🖱️ Doppelklick-Enter-Modus deaktiviert")
            else:
                self.logger.warning("⚠️ Doppelklick zu spät - Enter-Modus bereits abgelaufen")
        else:
            self.logger.debug("🖱️ Doppelklick ignoriert - Enter-Modus nicht aktiv")

    def start_recording(self) -> None:
        """Start voice recording and transcription."""
        if self._is_recording:
            self.logger.warning("⚠️  Aufnahme läuft bereits")
            self.toaster.show_warning("Aufnahme läuft bereits", "Aufnahme")
            return

        self.logger.info("🎙️  Starte Sprachaufnahme...")

        # Set volume to reduced level
        self.volume_controller.reduce_volume()

        # Start the recorder
        try:
            self.logger.debug("🎵 Starte Audio-Recorder...")
            self.recorder.start_recording()
            self.logger.info("✅ Audio-Recorder erfolgreich gestartet")

            # Only set recording state after successful start
            self._is_recording = True

            # Show notification
            self.toaster.show_info("🎙️ Aufnahme gestartet", "Sprachaufnahme läuft...")

            # Update system tray icon
            self.systray.update_recording_state(True)

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Starten des Audio-Recorders: {e}")
            self._is_recording = False
            self.toaster.show_error(f"Fehler beim Starten der Aufnahme: {e}", "Aufnahme")
            return

    def stop_recording(self) -> None:
        """Stop voice recording and process audio."""
        if not self._is_recording:
            self.logger.warning("⚠️  Keine Aufnahme aktiv")
            self.toaster.show_warning("Keine Aufnahme aktiv", "Aufnahme")
            return

        self.logger.info("🛑 Stoppe Sprachaufnahme...")
        self._is_recording = False
        self._last_recording_stop_timestamp = time.time()

        # Stelle Lautstärke sicher wieder her
        self.volume_controller.restore_volume()

        # Stop the recorder
        try:
            # Get audio data & stopping
            audio_data = self.recorder.stop_recording()
            self.logger.info("🎵 Audio-Recorder gestoppt")

            # Process audio data immediately if available
            if audio_data is None or len(audio_data) <= 0:
                self.logger.warning("❌ Keine Audioaufnahme verfügbar")
                self.toaster.show_warning("Keine Audioaufnahme", "Aufnahme")
                return  # Beende die Methode hier, da keine Audio-Daten verfügbar sind

            # Transcribe audio (ohne Spellchecking für schnelle Rückgabe)
            duration = len(audio_data) / self.recorder.sample_rate_hz
            self.logger.info(f"🔊 Audio verarbeitet: {len(audio_data):,} Samples, {duration:.2f}s")

            self.logger.info("🎯 Starte Sprach-zu-Text Transkription im Hintergrund...")

            # Starte Transkription in separatem Thread
            import threading

            transcription_thread = threading.Thread(target=self._transcribe_in_background, args=(audio_data,), daemon=True)
            transcription_thread.start()

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Verarbeiten der Aufnahme: {e}")
            self.toaster.show_error(f"Fehler beim Verarbeiten: {e}", "Aufnahme")
        finally:
            # Reset recording state
            self._is_recording = False
            self.systray.update_recording_state(False)

    def _transcribe_in_background(self, audio_data: bytes) -> None:
        """Transkription in separatem Hintergrundthread."""
        try:
            self.logger.info("🎯 Starte Transkription im Hintergrund...")

            # Verwende Multi-Transcriptor für bessere Ergebnisse
            results = self.transcriptor.transcribe_parallel(audio_data)

            if results:
                # Wähle bestes Ergebnis
                best_result = results[0]  # Erste ist das beste
                raw_text = best_result.text
                confidence = best_result.confidence

                self.logger.info(f"🏆 Bestes Ergebnis: {best_result.model} ({best_result.language}) - '{raw_text}'")

                # Kopiere Text immer in Zwischenablage
                self.logger.info("📋 Kopiere Text in Zwischenablage...")
                try:
                    pyperclip.copy(raw_text)
                    self.logger.info("✅ Text erfolgreich in Zwischenablage kopiert!")
                    self.logger.info(f"🎤 Transkribiert: '{raw_text}'")
                except Exception as clipboard_error:
                    self.logger.error(f"❌ Fehler beim Kopieren in Zwischenablage: {clipboard_error}")

                # Hole Mausposition
                import pyautogui

                mouse_x, mouse_y = pyautogui.position()

                # Zeige Widget und Notification über Hauptthread (thread-safe)
                self._schedule_transcription_display(raw_text, confidence, mouse_x, mouse_y, len(audio_data))

                # Speichere auch in Datenbank (im Hintergrund)
                self._save_recording_to_database(audio_data, raw_text)
            else:
                self.logger.warning("⚠️ Keine Transkription erfolgreich")
                raw_text = ""
                self.toaster.show_warning("❌ Keine Sprache erkannt", "Transkription")

        except Exception as e:
            self.logger.error(f"❌ Fehler bei Hintergrund-Transkription: {e}")
            self.toaster.show_error(f"Transkriptionsfehler: {e}", "Transkription")

    def _schedule_transcription_display(
        self, raw_text: str, confidence: float, mouse_x: int, mouse_y: int, audio_data_length: int
    ) -> None:
        """Plane Transkription-Anzeige über Hauptthread."""
        try:
            # Direkter Aufruf - nur Toast-Benachrichtigungen (keine Widgets)
            self._show_transcription_result(raw_text, confidence, mouse_x, mouse_y, audio_data_length)
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Planen der Transkription-Anzeige: {e}")

    def _show_transcription_result(
        self, raw_text: str, confidence: float, mouse_x: int, mouse_y: int, audio_data_length: int
    ) -> None:
        """Zeige Transkription-Ergebnis über Hauptthread."""
        try:
            # Zeige nur schöne Toast-Benachrichtigung (keine hässlichen Widgets)
            duration = audio_data_length / self.recorder.sample_rate_hz
            self.toaster.transcription_complete(raw_text, duration)
            self.logger.info(f"✨ Schöne Toast-Benachrichtigung für Transkription ({confidence:.2f})")

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Anzeigen der Transkription: {e}")

    def _save_recording_to_database(self, audio_data: bytes, raw_text: str = "") -> None:
        """Speichere Aufnahme in Datenbank."""
        try:
            # Save audio recording to database if enabled
            recording_id = None
            duration = len(audio_data) / self.recorder.sample_rate_hz  # Calculate duration
            self.logger.debug(
                f"🔍 Database config: enabled={self.config.database.get('enabled', False)}, auto_save={self.config.database.get('auto_save_recordings', False)}"
            )
            if self.config.database.get("enabled", False) and self.config.database.get("auto_save_recordings", False):
                try:
                    self.logger.info("💾 Speichere Audio-Aufnahme in Datenbank...")
                    self.logger.debug(
                        f"🔍 Audio data: shape={audio_data.shape}, dtype={audio_data.dtype}, duration={duration}s"
                    )
                    self.logger.debug(f"🔍 Sample rate: {self.recorder.sample_rate_hz}, channels: {self.recorder.num_channels}")
                    self.logger.debug(f"🔍 Audio format: {self.config.audio.get('format', 'wav')}")

                    recording_id = self.audio_database.save_audio_recording(
                        audio_data=audio_data,
                        sample_rate=self.recorder.sample_rate_hz,
                        channels=self.recorder.num_channels,
                        duration=duration,
                        audio_format=self.config.database.get("audio_format", "wav"),
                    )
                    self.logger.info(f"✅ Audio-Aufnahme gespeichert (ID: {recording_id})")
                except Exception as e:
                    self.logger.warning(f"⚠️  Konnte Audio-Aufnahme nicht speichern: {e}")
                    self.logger.debug(f"🔍 Exception details: {type(e).__name__}: {e}")
            else:
                self.logger.debug("💾 Audio-Speicherung deaktiviert")

            # Process transcription results
            if raw_text and raw_text.strip():
                self.logger.info("✨ Transkription erfolgreich abgeschlossen!")
                self.logger.info(f"📝 Roher Text: '{raw_text}'")

                # Save transcription to database if enabled
                transcription_id = None
                if (
                    self.config.database.get("enabled", False)
                    and self.config.database.get("auto_save_transcriptions", False)
                    and recording_id
                ):
                    try:
                        transcription_id = self.audio_database.save_transcription(
                            audio_recording_id=recording_id,
                            raw_text=raw_text,
                            language=self.config.transcription.get("language", "de"),
                        )
                        self.logger.info(f"✅ Transkription in Datenbank gespeichert (ID: {transcription_id})")

                        # Mark as training data if enabled
                        if self.config.database.get("mark_as_training_data", False):
                            self.audio_database.save_training_data(
                                transcription_id=transcription_id,
                                is_valid_for_training=True,
                            )
                            self.logger.info("🏷️  Als Trainingsdaten markiert")
                    except Exception as e:
                        self.logger.warning(f"⚠️  Konnte Transkription nicht speichern: {e}")
                else:
                    self.logger.debug("💾 Transkriptions-Speicherung deaktiviert oder keine Aufnahme-ID verfügbar")

                # Show transcription complete notification
                notification_duration = len(audio_data) / self.recorder.sample_rate_hz
                self.toaster.show_success(
                    "✨ Transkription abgeschlossen", f"'{raw_text[:50]}...' ({notification_duration:.1f}s)", force_show=True
                )

                # Sofort rohe Transkription in Clipboard kopieren
                self.logger.info("📋 Kopiere Text in Zwischenablage...")
                try:
                    pyperclip.copy(raw_text)
                    self.logger.info("✅ Text erfolgreich in Zwischenablage kopiert!")
                    self.logger.info(f"🎤 Transkribiert: '{raw_text}'")

                    # Automatisches Einfügen falls aktiviert
                    if self.config.notifications.get("auto_insert_enabled", False):  # Check if auto insert is enabled
                        self.logger.info("🔄 Automatisches Einfügen aktiviert - füge Text ein...")
                        time.sleep(0.2)  # Kurze Pause für bessere Stabilität
                        self._paste_text()
                        self.logger.info("✅ Text automatisch eingefügt!")

                except Exception as clipboard_error:
                    self.logger.error(f"❌ Fehler beim Kopieren in Zwischenablage: {clipboard_error}")
                    self.toaster.show_error(f"Clipboard-Fehler: {clipboard_error}", "Zwischenablage")
                    # Fallback: Versuche es nochmal mit kurzer Verzögerung
                    try:
                        time.sleep(0.1)
                        pyperclip.copy(raw_text)
                        self.logger.info("✅ Text erfolgreich in Zwischenablage kopiert (Fallback)!")
                    except Exception as fallback_error:
                        self.logger.error(f"❌ Fallback Clipboard-Versuch fehlgeschlagen: {fallback_error}")
                        self.toaster.show_error("Clipboard-System funktioniert nicht", "Kritischer Fehler")

                # Im Hintergrund Spellchecking machen
                # self.logger.info(f"🔄 Starte Hintergrund-Spellchecking...")
                # self._spellcheck_background(raw_text, audio_data)
            else:
                self.logger.warning("❌ Keine Sprache erkannt")
                self.toaster.show_warning("Keine Sprache erkannt", "Transkription")

        except Exception as e:
            self.logger.error(f"Failed to stop recorder: {e}")
            self.toaster.show_error(f"Fehler beim Stoppen der Aufnahme: {e}", "Aufnahme")

        # Update system tray icon
        self.systray.update_recording_state(False)

    def _spellcheck_background(self, raw_text: str, audio_data: np.ndarray) -> None:
        """Mache Spellchecking im Hintergrund und aktualisiere Clipboard wenn nötig."""

        def spellcheck_worker():
            try:
                self.logger.info("🔄 Starte Hintergrund-Spellchecking...")

                self.logger.info(f"📝 Analysiere Text: '{raw_text}'")
                self.logger.info("🔍 Starte Rechtschreibprüfung...")

                # Spell check and correct
                corrected_text = self.spell_checker.check_text(raw_text)
                self.logger.info(f"📖 Korrigierter Text: {corrected_text}")

                self.logger.info("✨ Rechtschreibprüfung abgeschlossen!")
                self.logger.info(f"📖 Ursprünglicher Text: '{raw_text}'")
                self.logger.info(f"✅ Korrigierter Text: '{corrected_text}'")

                # Nur aktualisieren wenn sich was geändert hat
                if corrected_text != raw_text:
                    self.logger.info("🔄 Text korrigiert - aktualisiere Zwischenablage...")
                    pyperclip.copy(corrected_text)
                    self.logger.info("📋 Zwischenablage mit korrigiertem Text aktualisiert!")
                    self.logger.info(f"🎯 Korrektur: '{raw_text}' → '{corrected_text}'")

                    # Show notification
                    self.toaster.show_success("🔍 Rechtschreibprüfung", f"'{raw_text}' → '{corrected_text}'")
                else:
                    self.logger.info("✅ Keine Korrekturen nötig - Text ist bereits korrekt")
                    self.logger.info("📋 Zwischenablage bleibt unverändert")

                    # Show notification
                    self.toaster.show_success("🔍 Rechtschreibprüfung", f"'{raw_text}' → '{corrected_text}'")

                self.logger.info("🏁 Hintergrund-Spellchecking erfolgreich abgeschlossen")

            except Exception as spell_error:
                self.logger.warning(f"❌ Spellchecking fehlgeschlagen: {spell_error}")
                self.logger.warning("⚠️  Verwende ursprünglichen Text ohne Korrekturen")

        self.logger.info("🚀 Starte Spellchecking-Thread im Hintergrund...")
        # Starte Spellchecking im Hintergrund
        spellcheck_thread = threading.Thread(target=spellcheck_worker)
        spellcheck_thread.daemon = True
        spellcheck_thread.start()
        self.logger.info(f"✅ Spellchecking-Thread gestartet (Thread-ID: {spellcheck_thread.ident})")

    def run(self) -> None:
        """Start the Mauscribe application."""
        self.logger.info("🚀 Starte Mauscribe-Anwendung...")

        # Setup system tray
        self.systray.setup()

        self.logger.info("🔄 Initialisiere System Tray...")

        # Run system tray in a separate thread so we can monitor shutdown
        tray_thread = threading.Thread(target=self._run_system_tray)
        tray_thread.daemon = True
        tray_thread.start()
        self.logger.info("✅ System Tray läuft im Hintergrund")

        self.toaster.show_info("Mauscribe erfolgreich gestartet", "Anwendung")

        self.logger.info("🎯 Mauscribe Steuerung:")
        self.logger.info(f"\t🐭 {self.config.primary_name} (press): Aufnahme starten/stoppen")
        if self.config.secondary_name and self.config.secondary_type != "disabled":
            self.logger.info(f"\t🐭 {self.config.secondary_name} (press): Doppelklick-Enter-Fenster aktivieren")
            self.logger.info(f"\t🐭 {self.config.secondary_name} (hold) + {self.config.primary_name} (press): Text einfügen")
        else:
            self.logger.info("\t🐭 Sekundäre Eingabe deaktiviert")
        self.logger.info("🎮 Bereit für Eingaben!")

        while not self.shutdown_event.is_set():
            # Check for double-click window
            self._check_double_click_window()
            time.sleep(0.1)
        self.logger.info("🔄 Shutdown-Signal empfangen - beende System Tray...")

    def _run_system_tray(self) -> None:
        """Run system tray in a separate thread."""
        if not self.systray.is_available():
            self.logger.error("❌ System Tray ist nicht verfügbar")
            return

        try:
            self.logger.info("🔄 Starte System Tray Thread...")
            self.systray.run()
            self.logger.info("✅ System Tray Thread läuft")
        except Exception as e:
            self.logger.error(f"❌ System Tray Fehler: {e}")
            # Don't shutdown the entire app if system tray fails

    def stop(self) -> None:
        """Stop the Mauscribe application."""
        self.logger.info("🛑 Beende Mauscribe-Anwendung...")

        # Signal shutdown to all threads
        self.shutdown_event.set()

        # Stop recording if active
        if self._is_recording:
            self.logger.info("🛑 Stoppe aktive Aufnahme vor dem Shutdown...")
            self.stop_recording()

        # Stop Hot Word Detection
        try:
            self.logger.info("🔄 Beende Hot Word Detection...")
            self.hotword_detector.cleanup()
            self.logger.info("✅ Hot Word Detection erfolgreich beendet")
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Beenden der Hot Word Detection: {e}")

        # Stop Computer Agent
        try:
            self.logger.info("🔄 Beende Computer Agent...")
            self.computer_agent.stop()
            self.logger.info("✅ Computer Agent erfolgreich beendet")
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Beenden des Computer Agents: {e}")

        # Stop input handling
        try:
            self.logger.info("🔄 Beende Input Handler...")
            self.controlls.stop()
            self.logger.info("✅ Input Handler erfolgreich beendet")
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Beenden des Input Handlers: {e}")

        # Cleanup AudioRecorder (stellt Lautstärke wieder her)
        try:
            self.logger.info("🔄 Räume AudioRecorder auf...")
            self.recorder.cleanup()
            self.logger.info("✅ AudioRecorder erfolgreich aufgeräumt")
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Aufräumen des AudioRecorders: {e}")

        # Stop system tray
        try:
            self.systray.stop()
            self.logger.info("✅ System Tray erfolgreich beendet")
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Beenden des System Tray: {e}")

        # Cleanup other components
        try:
            if hasattr(self, "spell_checker"):
                self.spell_checker.close()
                self.logger.info("✅ Rechtschreibprüfung erfolgreich beendet")
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Beenden der Rechtschreibprüfung: {e}")

        # Show shutdown notification
        if hasattr(self, "toaster"):
            self.toaster.show_info("Mauscribe erfolgreich beendet", "Anwendung")

        self.logger.info("✅ Mauscribe-Anwendung erfolgreich beendet")

    def _setup_signal_handlers(self) -> None:
        """Set up signal handlers for graceful shutdown."""
        try:
            signal.signal(signal.SIGINT, self._handle_signal)
            signal.signal(signal.SIGTERM, self._handle_signal)
            self.logger.info("✅ Signal-Handler für Strg+C erfolgreich eingerichtet")
        except Exception as e:
            self.logger.error(f"⚠️  Signal-Handler konnte nicht eingerichtet werden: {e}")

    def _handle_signal(self, signum: int, frame: Any) -> None:
        """Handle system signals for graceful shutdown."""
        signal_name = "SIGINT" if signum == signal.SIGINT else "SIGTERM"
        self.logger.info(f"🛑 Signal {signal_name} empfangen - starte graceful shutdown...")
        self.shutdown_event.set()

        # Force stop recording if active
        if self._is_recording:
            self.logger.info("🛑 Stoppe aktive Aufnahme...")
            self._is_recording = False
            self.recorder.stop_recording()

        # Stelle Lautstärke sicher wieder her
        if hasattr(self.recorder, "restore_volume"):
            self.logger.info("🔄 Stelle System-Lautstärke wieder her...")
            self.volume_controller.restore_volume()


def start_mouscribe() -> None:
    """Main entry point for the Mauscribe application."""
    app = MauscribeApp()
    try:
        app.run()
    except KeyboardInterrupt:
        app.logger.info("⚠️  Programm durch Benutzer unterbrochen (Strg+C)")
        app.shutdown_event.set()
    except Exception as e:
        app.logger.error(f"❌ Unerwarteter Fehler: {e}")
        app.logger.error(f"Unexpected error in main: {e}")
        app.shutdown_event.set()
    finally:
        app.logger.info("🔄 Beende Anwendung...")
        app.stop()
        app.logger.info("✅ Anwendung erfolgreich beendet")


if __name__ == "__main__":
    start_mouscribe()
