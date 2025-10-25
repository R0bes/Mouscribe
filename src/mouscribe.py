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

from .audio.audio_service import get_audio_service
from .audio.recorder import Recorder
from .audio.volumizer import Volumizer
from .config import get_config
from .input import InputManager, InputType, MouseButton, create_mouse_mapping
from .ui.notifications import Toaster
from .ui.system_tray import SysTray
from .ui.widgets import MouseOverlayManager, RecordingWidget, TextWidget, WidgetConfig
from .utils import AudioDatabase, get_logger, setup_logging
from .utils.eventbus import EventType, emit_event, get_event_bus

# TranscriptionWidgetManager import removed - widgets disabled


# AppSettings removed - using unified AppConfig instead


class MauscribeApp:
    """Main application class for Mauscribe voice-to-text tool."""

    def __init__(self) -> None:
        """Initialize Mauscribe application."""
        # Initialize unified configuration
        self.config = get_config()

        # Setup logging
        setup_logging()

        # Create logger instance
        self.logger = get_logger(self.__class__.__name__, self.config)
        self.logger.info("🚀 Starte Mauscribe...")

        self.logger.info("🔧 Initialisiere Komponenten...")

        self.systray = SysTray(self.config, self)
        self.recorder = Recorder()
        # Initialize audio service for transcription
        self.audio_service = get_audio_service()
        # Initialize volume controller with unified config
        self.volume_controller = Volumizer(
            reduction_factor=self.config.audio.volume_reduction_factor, min_volume=self.config.audio.min_volume, enabled=True
        )
        self.overlay_manager = MouseOverlayManager()

        # Hot Word Detector removed - only using ComputerAgent

        # Computer Agent entfernt - keine Hotword Detection mehr
        # Initialize toaster with notification settings
        # Load notification settings directly from TOML to ensure correct values
        # Initialize notification system with granular config
        self.toaster = Toaster(
            enable_sound=True,  # Sound wird pro Benachrichtigung gesteuert
            default_duration=self.config.ui.notifications.toast_duration,
            enabled=True,  # Toast wird pro Benachrichtigung gesteuert
            notification_settings={"toast": True},
        )

        self.logger.info("🔊 Notification-System initialisiert:")
        self.logger.info(f"   - Duration: {self.config.ui.notifications.toast_duration}ms")
        self.logger.info(f"   - Position: {self.config.ui.notifications.toast_position}")
        # Initialize unified input manager
        self.input_manager = InputManager()

        # Register event handlers
        self.input_manager.register_handler("primary_action", self.on_primary_action)
        self.input_manager.register_handler("secondary_action", self.on_secondary_action)
        self.input_manager.register_handler("insert_combination", self.on_insert_action)

        # Add input mappings - X2-Taste für Aufnahme, keine sekundäre Aktion
        self.input_manager.add_input_mapping(
            create_mouse_mapping(
                name="primary_recording",
                button=MouseButton.X2,
                input_type=InputType.MOUSE_HOLD,
                handler=self.on_primary_action,
                description="X2-Taste für Aufnahme starten/stoppen",
            )
        )

        # Transcription widgets disabled - using only beautiful toast notifications

        self.overlay_manager.register_widget("recording", TextWidget("Test"), "left", 0.5)

        # Initialize database
        self.audio_database = AudioDatabase()

        # Start input manager if enabled
        if self.config.input_config.enabled:
            self.input_manager.start()
            self.logger.info("✅ InputManager gestartet")
        else:
            self.logger.info("🔇 Input-Steuerung deaktiviert")

        # Hotword Detection und Computer Agent entfernt

        self.logger.info("✅ Alle Komponenten initialisiert")

        # Initialize recording state variables
        self._is_recording = False
        self._last_recording_timestamp: float = 0.0
        self._last_paste_time = 0  # Debounce für Text-Einfügen
        self._last_recording_stop_timestamp: float = 0.0

        # Initialize double-click enter functionality
        # Doppelklick-Enter-Fenster entfernt

        self.shutdown_event = threading.Event()

        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()

    def on_primary_action(self, event=None) -> None:
        """Handle primary button action (x2 button) - toggle recording."""
        self.logger.info("🎮 X2-Taste gedrückt - Aufnahme starten/stoppen")
        if not self._is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def on_secondary_action(self, event=None) -> None:
        """Handle secondary button action - deaktiviert."""
        # Doppelklick-Enter-Fenster entfernt
        pass

    def on_insert_action(self, event=None) -> None:
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

    # Doppelklick-Enter-Fenster entfernt

    # Widget copy method removed - widgets disabled

    # Start/Stop Word Detection entfernt

    # Alle Hotword Detection und Computer Agent Methoden entfernt

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
                    # Doppelklick-Enter-Modus entfernt

                    if self.config.ui.notifications.text_inserted.toast:
                        self.toaster.show_info("📋 Text eingefügt", f"'{text[:50]}...'")
                else:
                    self.logger.error("❌ Text konnte nicht eingefügt werden")
                    if self.config.ui.notifications.text_insert_error.toast:
                        self.toaster.show_error("Text konnte nicht eingefügt werden", "Text einfügen")

            else:
                self.logger.warning("⚠️  Kein Text in der Zwischenablage zum Einfügen")
                if self.config.ui.notifications.text_insert_error.toast:
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
                if self.config.ui.notifications.text_inserted.toast:
                    self.toaster.show_info("📋 Text eingefügt", "Text (Fallback)")
            except Exception as fallback_error:
                self.logger.error(f"❌ Fallback-Einfüge-Methode fehlgeschlagen: {fallback_error}")
                if self.config.ui.notifications.text_insert_error.toast:
                    self.toaster.show_error("Text konnte nicht eingefügt werden", "Kritischer Fehler")

    # Doppelklick-Enter-Modus entfernt

    # Doppelklick-Enter-Handler entfernt

    def start_recording(self) -> None:
        """Start voice recording and transcription."""
        if self._is_recording:
            self.logger.warning("⚠️  Aufnahme läuft bereits")
            if self.config.ui.notifications.recording_error.toast:
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

            # Emit recording started event
            emit_event(
                EventType.RECORDING_STARTED,
                {"timestamp": time.time(), "recorder_state": self.recorder.is_recording},
                source="MauscribeApp",
            )

            # Show notification
            if self.config.ui.notifications.recording_start.toast:
                self.toaster.show_info("🎙️ Aufnahme gestartet", "Sprachaufnahme läuft...")

            # Update system tray icon
            self.systray.set_recording_state(True)

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Starten des Audio-Recorders: {e}")
            self._is_recording = False
            if self.config.ui.notifications.recording_error.toast:
                self.toaster.show_error(f"Fehler beim Starten der Aufnahme: {e}", "Aufnahme")
            return

    def stop_recording(self) -> None:
        """Stop voice recording and process audio."""
        if not self._is_recording:
            self.logger.warning("⚠️  Keine Aufnahme aktiv")
            if self.config.ui.notifications.recording_error.toast:
                self.toaster.show_warning("Keine Aufnahme aktiv", "Aufnahme")
            return

        self.logger.info("🛑 Stoppe Sprachaufnahme...")
        self._is_recording = False
        self._last_recording_stop_timestamp = time.time()

        # Emit recording stopped event
        emit_event(
            EventType.RECORDING_STOPPED,
            {"timestamp": time.time(), "recorder_state": self.recorder.is_recording},
            source="MauscribeApp",
        )

        # Update system tray icon
        self.systray.set_recording_state(False)

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
                if self.config.ui.notifications.recording_error.toast:
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
            if self.config.ui.notifications.recording_error.toast:
                self.toaster.show_error(f"Fehler beim Verarbeiten: {e}", "Aufnahme")
        finally:
            # Reset recording state
            self._is_recording = False
            self.systray.update_recording_state(False)

    def _transcribe_in_background(self, audio_data: bytes) -> None:
        """Transkription in separatem Hintergrundthread."""
        try:
            self.logger.info("🎯 Starte Transkription im Hintergrund...")

            # Emit transcription started event
            emit_event(
                EventType.TRANSCRIPTION_STARTED,
                {"timestamp": time.time(), "audio_length": len(audio_data)},
                source="MauscribeApp",
            )

            # Verwende AudioService für Transkription
            result = self.audio_service.transcribe(audio_data, model_size=self.config.model, language=self.config.language)

            if result:
                raw_text = result.text
                confidence = result.confidence

                # Emit transcription completed event
                emit_event(
                    EventType.TRANSCRIPTION_COMPLETED,
                    {
                        "timestamp": time.time(),
                        "text": raw_text,
                        "confidence": confidence,
                        "model": result.model,
                        "language": result.language,
                    },
                    source="MauscribeApp",
                )

                self.logger.info(f"🏆 Transkription erfolgreich: {result.model} ({result.language}) - '{raw_text}'")

                # Kopiere Text immer in Zwischenablage
                try:
                    pyperclip.copy(raw_text)
                    self.logger.info("✅ Text in Zwischenablage kopiert")
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
                if self.config.ui.notifications.transcription_empty.toast:
                    self.toaster.show_warning("❌ Keine Sprache erkannt", "Transkription")

        except Exception as e:
            self.logger.error(f"❌ Fehler bei Hintergrund-Transkription: {e}")

            # Emit transcription failed event
            emit_event(EventType.TRANSCRIPTION_FAILED, {"timestamp": time.time(), "error": str(e)}, source="MauscribeApp")

            if self.config.ui.notifications.transcription_error.toast:
                self.toaster.show_error(f"Transkriptionsfehler: {e}", "Transkription")

    def _schedule_transcription_display(
        self,
        raw_text: str,
        confidence: float,
        mouse_x: int,
        mouse_y: int,
        audio_data_length: int,
    ) -> None:
        """Plane Transkription-Anzeige über Hauptthread."""
        try:
            # Direkter Aufruf - nur Toast-Benachrichtigungen (keine Widgets)
            self._show_transcription_result(raw_text, confidence, mouse_x, mouse_y, audio_data_length)
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Planen der Transkription-Anzeige: {e}")

    def _show_transcription_result(
        self,
        raw_text: str,
        confidence: float,
        mouse_x: int,
        mouse_y: int,
        audio_data_length: int,
    ) -> None:
        """Zeige Transkription-Ergebnis über Hauptthread."""
        try:
            # Zeige nur schöne Toast-Benachrichtigung (keine hässlichen Widgets)
            duration = audio_data_length / self.recorder.sample_rate_hz

            # Callback für Notification-Klick - öffne Control Center
            def open_control_center_on_click():
                try:
                    from .config.app_config import AppConfig
                    from .ui.control_center import open_control_center

                    config = AppConfig()
                    open_control_center(config, self)
                    self.logger.info("🎮 Control Center geöffnet durch Notification-Klick")

                except Exception as e:
                    self.logger.error(f"❌ Fehler beim Öffnen des Control Centers: {e}")

            # Zeige klickbare Notification mit Control Center Callback
            self.toaster.transcription_complete(raw_text, duration, clickable=True, callback=open_control_center_on_click)
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
                f"🔍 Database config: enabled={self.config.database.enabled}, auto_save={self.config.database.auto_save_recordings}"
            )
            if self.config.database.enabled and self.config.database.auto_save_recordings:
                try:
                    self.logger.info("💾 Speichere Audio-Aufnahme in Datenbank...")
                    self.logger.debug(
                        f"🔍 Audio data: shape={audio_data.shape}, dtype={audio_data.dtype}, duration={duration}s"
                    )
                    self.logger.debug(f"🔍 Sample rate: {self.recorder.sample_rate_hz}, channels: {self.recorder.num_channels}")
                    self.logger.debug(f"🔍 Audio format: {getattr(self.config.audio, 'format', 'wav')}")

                    recording_id = self.audio_database.save_audio_recording(
                        audio_data=audio_data,
                        sample_rate=self.recorder.sample_rate_hz,
                        channels=self.recorder.num_channels,
                        duration=duration,
                        audio_format=self.config.database.audio_format,
                    )
                    self.logger.info(f"✅ Audio-Aufnahme gespeichert (ID: {recording_id})")

                    # Emit audio file saved event
                    emit_event(
                        EventType.AUDIO_FILE_SAVED,
                        {"recording_id": recording_id, "duration": duration, "timestamp": time.time()},
                        source="MauscribeApp",
                    )

                except Exception as e:
                    self.logger.warning(f"⚠️  Konnte Audio-Aufnahme nicht speichern: {e}")
                    self.logger.debug(f"🔍 Exception details: {type(e).__name__}: {e}")
            else:
                self.logger.debug("💾 Audio-Speicherung deaktiviert")

            # Process transcription results
            if raw_text and raw_text.strip():
                # Transkription bereits geloggt, keine doppelten Logs

                # Save transcription to database if enabled
                transcription_id = None
                if self.config.database.enabled and self.config.database.auto_save_transcriptions and recording_id:
                    try:
                        transcription_id = self.audio_database.save_transcription(
                            audio_recording_id=recording_id,
                            raw_text=raw_text,
                            language=self.config.language,
                        )
                        self.logger.info(f"✅ Transkription in Datenbank gespeichert (ID: {transcription_id})")

                        # Mark as training data if enabled
                        if self.config.database.mark_as_training_data:
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
                if self.config.ui.notifications.transcription_success.toast:
                    self.toaster.show_success(
                        "✨ Transkription abgeschlossen",
                        f"'{raw_text[:50]}...' ({notification_duration:.1f}s)",
                    )

                # Sofort rohe Transkription in Clipboard kopieren
                try:
                    pyperclip.copy(raw_text)
                    # Text bereits in Zwischenablage kopiert, keine doppelten Logs

                    # Automatisches Einfügen deaktiviert - nur manuell über Input

                except Exception as clipboard_error:
                    self.logger.error(f"❌ Fehler beim Kopieren in Zwischenablage: {clipboard_error}")
                    if self.config.ui.notifications.transcription_error.toast:
                        self.toaster.show_error(f"Clipboard-Fehler: {clipboard_error}", "Zwischenablage")
                    # Fallback: Versuche es nochmal mit kurzer Verzögerung
                    try:
                        time.sleep(0.1)
                        pyperclip.copy(raw_text)
                        self.logger.info("✅ Text erfolgreich in Zwischenablage kopiert (Fallback)!")
                    except Exception as fallback_error:
                        self.logger.error(f"❌ Fallback Clipboard-Versuch fehlgeschlagen: {fallback_error}")
                        if self.config.ui.notifications.transcription_error.toast:
                            self.toaster.show_error("Clipboard-System funktioniert nicht", "Kritischer Fehler")

                # Im Hintergrund Spellchecking machen
                # self.logger.info(f"🔄 Starte Hintergrund-Spellchecking...")
                # self._spellcheck_background(raw_text, audio_data)
            else:
                self.logger.warning("❌ Keine Sprache erkannt")
                if self.config.ui.notifications.transcription_empty.toast:
                    self.toaster.show_warning("Keine Sprache erkannt", "Transkription")

        except Exception as e:
            self.logger.error(f"Failed to stop recorder: {e}")
            if self.config.ui.notifications.recording_error.toast:
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
                    if self.config.ui.notifications.transcription_success.toast:
                        self.toaster.show_success("🔍 Rechtschreibprüfung", f"'{raw_text}' → '{corrected_text}'")
                else:
                    self.logger.info("✅ Keine Korrekturen nötig - Text ist bereits korrekt")
                    self.logger.info("📋 Zwischenablage bleibt unverändert")

                    # Show notification
                    if self.config.ui.notifications.transcription_success.toast:
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

        if self.config.ui.notifications.app_start.toast:
            self.toaster.show_info("Mauscribe erfolgreich gestartet", "Anwendung")

        self.logger.info("🎯 Mauscribe Steuerung:")
        self.logger.info("\t🐭 X2-Taste (hold): Aufnahme starten/stoppen")
        if self.config.input_config.enabled:
            self.logger.info("\t🐭 Linke Maustaste (hold) + X2-Taste (press): Text einfügen")
        else:
            self.logger.info("\t🐭 Sekundäre Eingabe deaktiviert")
        self.logger.info("🎮 Bereit für Eingaben!")

        # Auto-start GUI if enabled
        if hasattr(self.config.ui, "auto_start_gui") and self.config.ui.auto_start_gui:
            self.logger.info("🎮 Auto-starting Control Center...")
            from .ui.control_center import open_control_center

            open_control_center(self.config, self)

        while not self.shutdown_event.is_set():
            # Check for double-click window
            # Doppelklick-Enter-Fenster entfernt
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

        # Hot Word Detection removed

        # Stop Computer Agent
        # Computer Agent entfernt

        # Stop input handling
        try:
            self.logger.info("🔄 Beende Input Handler...")
            self.input_manager.stop()
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
            if self.config.ui.notifications.app_shutdown.toast:
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
