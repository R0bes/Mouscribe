#!/usr/bin/env python3
"""
Einfache funktionierende Audio-Stream Lösung
"""

import time
import threading
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from collections import deque

def test_start_callback(word: str) -> None:
    """Callback für Start Word."""
    print(f"🎯 START WORD ERKANNT: '{word}'")

def test_stop_callback(word: str) -> None:
    """Callback für Stop Word."""
    print(f"🛑 STOP WORD ERKANNT: '{word}'")

class SimpleWorkingStream:
    """Einfache funktionierende Audio-Stream Lösung."""
    
    def __init__(self):
        self.running = False
        self.hotword_model = None
        self.transcription_model = None
        # Kato Agent System
        self.wake_words_to_test = [
            "kato",       # Dein gewählter Agent-Name
            "hey kato",   # Mit Hey
            "okay kato",  # Mit Okay
            "kato start", # Direkt mit Kommando
            "kato stopp", # Direkt mit Kommando
            "kato einfügen", # Direkt mit Kommando
            "kato beenden" # Direkt mit Kommando
        ]
        self.wake_word = "kato"  # Haupt-Wake Word
        self.start_words = ["start"]
        self.stop_words = ["stopp"]
        self.exit_words = ["beenden", "exit"]
        self.insert_words = ["einfügen", "insert", "paste"]
        
        # State für Wake Word Detection
        self.wake_word_detected = False
        self.command_pending = False
        
        # Audio-Buffer
        self.audio_buffer = deque(maxlen=48000)  # 3 Sekunden bei 16kHz
        self.is_recording = False
        self.recording_buffer = []
        
    def start(self):
        """Starte einfachen Audio-Stream."""
        if self.running:
            print("⚠️ Stream läuft bereits")
            return
            
        print("🚀 Starte einfachen Audio-Stream...")
        
        # Whisper Modelle laden
        try:
            self.hotword_model = WhisperModel("base", device="cpu", compute_type="int8")
            print("✅ Hot Word Modell geladen (base)")
            
            self.transcription_model = WhisperModel("small", device="cpu", compute_type="float32")
            print("✅ Transkriptions-Modell geladen (small)")
            
        except Exception as e:
            print(f"❌ Whisper Modell Fehler: {e}")
            return
            
        self.running = True
        
        # Starte Audio-Loop
        self.audio_thread = threading.Thread(target=self._audio_loop, daemon=True)
        self.audio_thread.start()
        
        print("✅ Einfacher Audio-Stream läuft")
        
    def stop(self):
        """Stoppe einfachen Audio-Stream."""
        if not self.running:
            return
            
        print("🛑 Stoppe Audio-Stream...")
        self.running = False
        
        if hasattr(self, 'audio_thread'):
            self.audio_thread.join(timeout=2.0)
            
        print("✅ Audio-Stream gestoppt")
        
    def _audio_loop(self):
        """Einfache Audio-Loop ohne Callback."""
        print("🔄 Audio-Loop gestartet")
        
        while self.running:
            try:
                # Audio aufnehmen (4 Sekunden für bessere Erkennung)
                duration = 4
                sample_rate = 16000
                
                print("🎤 Nehme Audio auf...")
                audio_data = sd.rec(
                    int(duration * sample_rate),
                    samplerate=sample_rate,
                    channels=1,
                    dtype=np.float32,
                    blocking=True
                )
                
                if audio_data is not None and len(audio_data) > 0:
                    print(f"✅ Audio aufgenommen: {len(audio_data)} Samples")
                    
                    # Audio zu Buffer hinzufügen
                    self.audio_buffer.extend(audio_data.flatten())
                    
                    # Wenn Aufnahme läuft, auch zu Aufnahme-Buffer hinzufügen
                    if self.is_recording:
                        self.recording_buffer.append(audio_data.copy())
                        print(f"📝 Aufnahme läuft: {len(self.recording_buffer)} Segmente")
                    else:
                        print("🔇 Keine aktive Aufnahme")
                    
                    # Hot Word Detection (mit Timeout)
                    try:
                        self._check_hot_words(audio_data)
                    except Exception as e:
                        print(f"⚠️ Hot Word Check Fehler: {e}")
                        # Reset Wake Word State bei Fehlern
                        self._reset_wake_word_state()
                    
                else:
                    print("❌ Keine Audio-Daten erhalten")
                    
            except Exception as e:
                print(f"❌ Audio-Loop Fehler: {e}")
                
            # Kurze Pause
            time.sleep(0.1)  # Reduzierte Pause für bessere Responsivität
    
    def _check_hot_words(self, audio_data):
        """Prüfe auf Hot Words."""
        try:
            # Audio normalisieren
            audio_data = audio_data.flatten()
            if np.max(np.abs(audio_data)) > 0:
                max_val = np.max(np.abs(audio_data))
                if max_val > 0.1:
                    audio_data = audio_data / max_val * 0.95
            
            # Whisper Transkription
            # Whisper Transkription (ohne Timeout auf Windows)
            segments, info = self.hotword_model.transcribe(
                audio=audio_data,
                language="de",
                vad_filter=False,
                beam_size=1,
                best_of=1,
                temperature=0.0,
            )
            
            text_parts = [seg.text.strip() for seg in segments]
            text = " ".join([t for t in text_parts if t]).lower().strip()
            
            if text:
                print(f"🎤 Audio erkannt: '{text}'")
                
                # Prüfe auf Wake Word + Kommando
                self._process_wake_word_command(text)
            else:
                print("🔇 Stille erkannt")
                
        except Exception as e:
            print(f"❌ Hot Word Check Fehler: {e}")
    
    def _process_wake_word_command(self, text: str) -> None:
        """Verarbeite Wake Word + Kommando Pattern."""
        text_lower = text.lower()
        
        # Teste alle möglichen Wake Words
        detected_wake_word = None
        for wake_word in self.wake_words_to_test:
            if wake_word in text_lower:
                detected_wake_word = wake_word
                break
        
        if detected_wake_word:
            print(f"🎯 Wake Word '{detected_wake_word}' erkannt!")
            self.wake_word_detected = True
            self.command_pending = True
            
            # Extrahiere das Kommando nach dem Wake Word
            wake_word_pos = text_lower.find(detected_wake_word)
            command_text = text_lower[wake_word_pos + len(detected_wake_word):].strip()
            
            print(f"📝 Kommando-Text: '{command_text}'")
            
            # Prüfe auf Kommandos
            self._check_command(command_text)
            
        elif self.command_pending:
            # Wenn Wake Word bereits erkannt, prüfe nur auf Kommandos
            print(f"📝 Kommando-Text (ohne Wake Word): '{text_lower}'")
            self._check_command(text_lower)
        else:
            # Kein Wake Word erkannt - ignoriere
            print(f"🔇 Kein Wake Word erkannt - ignoriere")
    
    def _check_command(self, command_text: str) -> None:
        """Prüfe auf spezifische Kommandos."""
        # Prüfe auf Start Kommando
        for start_word in self.start_words:
            if start_word in command_text:
                self._on_start_word_found(start_word, command_text)
                self._reset_wake_word_state()
                return
        
        # Prüfe auf Stop Kommando
        for stop_word in self.stop_words:
            if stop_word in command_text:
                self._on_stop_word_found(stop_word, command_text)
                self._reset_wake_word_state()
                return
        
        # Prüfe auf Exit Kommando
        for exit_word in self.exit_words:
            if exit_word in command_text:
                self._on_exit_word_found(exit_word, command_text)
                self._reset_wake_word_state()
                return
        
        # Prüfe auf Insert Kommando
        for insert_word in self.insert_words:
            if insert_word in command_text:
                self._on_insert_word_found(insert_word, command_text)
                self._reset_wake_word_state()
                return
        
        # Kein gültiges Kommando erkannt
        print(f"⚠️ Kein gültiges Kommando in '{command_text}' erkannt")
        self._reset_wake_word_state()
    
    def _reset_wake_word_state(self) -> None:
        """Reset Wake Word State."""
        self.wake_word_detected = False
        self.command_pending = False
        print("🔄 Wake Word State zurückgesetzt")
    
    def _on_start_word_found(self, word: str, text: str) -> None:
        """Start Word gefunden."""
        print(f"🎯 Start Word erkannt: '{word}' in '{text}'")
        # Pop-Up deaktiviert um Aufhängungen zu vermeiden
        # self._show_popup("🎯 Start Word erkannt", f"'{word}' - Starte Aufnahme...")
        self.start_recording()
        test_start_callback(word)
        print("✅ Start Word verarbeitet - Audio-Loop läuft weiter")
        
    def _on_stop_word_found(self, word: str, text: str) -> None:
        """Stop Word gefunden."""
        print(f"🛑 Stop Word erkannt: '{word}' in '{text}'")
        # Pop-Up deaktiviert um Aufhängungen zu vermeiden
        # self._show_popup("🛑 Stop Word erkannt", f"'{word}' - Stoppe Aufnahme...")
        self.stop_recording()
        test_stop_callback(word)
    
    def _on_exit_word_found(self, word: str, text: str) -> None:
        """Exit Word gefunden."""
        print(f"🚪 Exit Word erkannt: '{word}' in '{text}'")
        # Pop-Up deaktiviert um Aufhängungen zu vermeiden
        # self._show_popup("🚪 Exit Word erkannt", f"'{word}' - Beende Programm...")
        print("🛑 Beende Programm...")
        self.running = False
        # Sofortiges Beenden mit os._exit für hartes Beenden
        import os
        os._exit(0)
    
    def _on_insert_word_found(self, word: str, text: str) -> None:
        """Insert Word gefunden - füge Clipboard-Inhalt ein."""
        print(f"📋 Insert Word erkannt: '{word}' in '{text}'")
        # Pop-Up deaktiviert um Aufhängungen zu vermeiden
        # self._show_popup("📋 Insert Word erkannt", f"'{word}' - Füge Clipboard-Inhalt ein...")
        self._insert_clipboard_content()
    
    def _show_popup(self, title: str, message: str) -> None:
        """Zeige Pop-Up Benachrichtigung (nicht-blockierend)."""
        try:
            import tkinter as tk
            from tkinter import messagebox
            import threading
            
            def show_popup_thread():
                try:
                    # Erstelle unsichtbares Root-Fenster
                    root = tk.Tk()
                    root.withdraw()  # Verstecke das Hauptfenster
                    
                    # Zeige Messagebox
                    messagebox.showinfo(title, message)
                    
                    # Zerstöre das Fenster
                    root.destroy()
                    
                except Exception as e:
                    print(f"⚠️ Pop-Up Thread Fehler: {e}")
            
            # Starte Pop-Up in separatem Thread
            popup_thread = threading.Thread(target=show_popup_thread, daemon=True)
            popup_thread.start()
            
        except Exception as e:
            print(f"⚠️ Pop-Up Fehler: {e}")
    
    def _insert_clipboard_content(self) -> None:
        """Füge Clipboard-Inhalt ein."""
        try:
            import pyperclip
            import pyautogui
            
            # Hole Clipboard-Inhalt
            clipboard_text = pyperclip.paste()
            
            if clipboard_text:
                print(f"📋 Clipboard-Inhalt: '{clipboard_text}'")
                
                # Simuliere Strg+V (Paste)
                pyautogui.hotkey('ctrl', 'v')
                print("✅ Clipboard-Inhalt eingefügt!")
                
                self._show_popup("✅ Eingefügt", f"Clipboard-Inhalt eingefügt:\n'{clipboard_text[:50]}...'")
            else:
                print("⚠️ Clipboard ist leer")
                self._show_popup("⚠️ Clipboard leer", "Kein Inhalt im Clipboard gefunden")
                
        except ImportError:
            print("❌ pyautogui nicht verfügbar - kann nicht einfügen")
            self._show_popup("❌ Fehler", "pyautogui nicht verfügbar")
        except Exception as e:
            print(f"❌ Fehler beim Einfügen: {e}")
            self._show_popup("❌ Fehler", f"Fehler beim Einfügen: {e}")
    
    def _clean_transcription_text(self, text: str) -> str:
        """Bereinige Transkriptions-Text."""
        if not text:
            return text
            
        # Entferne "stopp" am Ende
        if text.lower().endswith("stopp"):
            text = text[:-5].strip()
            print("🔧 'stopp' am Ende entfernt")
        
        # Entferne überflüssige Satzzeichen am Ende
        while text and text[-1] in "!?.":
            text = text[:-1].strip()
            print("🔧 Satzzeichen am Ende entfernt")
        
        # Entferne mehrfache Leerzeichen
        import re
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _concatenate_audio_with_overlap(self, audio_segments: list) -> np.ndarray:
        """Füge Audio-Segmente mit Überlappung zusammen um Lücken zu vermeiden."""
        if not audio_segments:
            return np.array([])
        
        if len(audio_segments) == 1:
            return audio_segments[0]
        
        # Überlappung: 0.1 Sekunden (1600 Samples bei 16kHz)
        overlap_samples = 1600
        
        result = []
        
        for i, segment in enumerate(audio_segments):
            if i == 0:
                # Erstes Segment komplett hinzufügen
                result.append(segment)
            else:
                # Überlappung: Fade-out des vorherigen + Fade-in des aktuellen
                if len(result) > 0:
                    # Letzte overlap_samples des vorherigen Segments
                    prev_tail = result[-1][-overlap_samples:]
                    # Erste overlap_samples des aktuellen Segments
                    curr_head = segment[:overlap_samples]
                    
                    # Crossfade (sanfter Übergang)
                    fade_out = np.linspace(1, 0, overlap_samples)
                    fade_in = np.linspace(0, 1, overlap_samples)
                    
                    crossfade = prev_tail * fade_out + curr_head * fade_in
                    
                    # Ersetze das Ende des vorherigen Segments
                    result[-1] = np.concatenate([result[-1][:-overlap_samples], crossfade])
                    
                    # Füge den Rest des aktuellen Segments hinzu
                    result.append(segment[overlap_samples:])
                else:
                    result.append(segment)
        
        return np.concatenate(result)
    
    def start_recording(self) -> None:
        """Starte Aufnahme."""
        if self.is_recording:
            print("⚠️ Aufnahme läuft bereits - ignoriere")
            return
            
        print("🎙️ Starte Aufnahme...")
        self.is_recording = True
        self.recording_buffer = []
        self.recording_start_time = time.time()
        print("✅ Aufnahme gestartet - Audio-Loop läuft weiter")
        
    def stop_recording(self) -> None:
        """Stoppe Aufnahme und transkribiere."""
        if not self.is_recording:
            return
            
        print("🛑 Stoppe Aufnahme...")
        self.is_recording = False
        
        if self.recording_buffer:
            # Alle Audio-Daten zusammenfügen
            print(f"📊 Recording Buffer: {len(self.recording_buffer)} Segmente")
            for i, segment in enumerate(self.recording_buffer):
                print(f"   Segment {i}: {segment.shape}")
            
            # Audio-Daten richtig zusammenfügen (flatten first)
            audio_segments = [segment.flatten() for segment in self.recording_buffer]
            full_audio = self._concatenate_audio_with_overlap(audio_segments)
            duration = time.time() - self.recording_start_time
            
            print(f"📊 Aufnahme abgeschlossen:")
            print(f"   - Dauer: {duration:.1f}s")
            print(f"   - Samples: {len(full_audio)}")
            print(f"   - Shape: {full_audio.shape}")
            print(f"   - Segmente: {len(self.recording_buffer)}")
            
            # Gesamttranskription
            self._transcribe_recording(full_audio)
        else:
            print("⚠️ Keine Audio-Daten gesammelt")
    
    def _transcribe_recording(self, audio_data: np.ndarray) -> None:
        """Transkribiere Aufnahme."""
        try:
            print("🎯 Starte Gesamttranskription...")
            print(f"📊 Audio-Daten: {len(audio_data)} Samples, Shape: {audio_data.shape}")
            
            # Audio normalisieren
            if np.max(np.abs(audio_data)) > 0:
                max_val = np.max(np.abs(audio_data))
                print(f"📊 Audio-Max: {max_val:.3f}")
                if max_val > 0.1:
                    audio_data = audio_data / max_val * 0.95
                    print(f"📊 Audio normalisiert: {np.max(np.abs(audio_data)):.3f}")
            
            # Whisper Transkription mit besserem Modell
            print("🤖 Starte Whisper Transkription...")
            segments, info = self.transcription_model.transcribe(
                audio=audio_data,
                language="de",
                vad_filter=False,
                beam_size=5,
                best_of=5,
                temperature=0.0,
            )
            
            # Segmente zu Liste konvertieren
            segments_list = list(segments)
            print(f"📊 Whisper Segmente: {len(segments_list)}")
            for i, seg in enumerate(segments_list):
                print(f"   Segment {i}: '{seg.text}'")
            
            # Text zusammenfügen
            text_parts = [seg.text.strip() for seg in segments_list]
            full_text = " ".join([t for t in text_parts if t]).strip()
            
            # Text-Bereinigung
            full_text = self._clean_transcription_text(full_text)
            
            if full_text:
                print("✅ Gesamttranskription erfolgreich:")
                print(f"📝 Vollständiger Text: '{full_text}'")
                print(f"📊 Transkriptions-Info: {info.duration:.1f}s Audio verarbeitet")
                
                # Text in Zwischenablage kopieren
                try:
                    import pyperclip
                    pyperclip.copy(full_text)
                    print("📋 Text erfolgreich in Zwischenablage kopiert!")
                except ImportError:
                    print("⚠️ pyperclip nicht verfügbar - Text nicht kopiert")
                except Exception as e:
                    print(f"❌ Fehler beim Kopieren: {e}")
            else:
                print("⚠️ Kein Text in der Aufnahme erkannt")
                print(f"📊 Text-Parts: {text_parts}")
                
        except Exception as e:
            print(f"❌ Fehler bei Gesamttranskription: {e}")
            import traceback
            traceback.print_exc()

def main():
    print("🧪 Einfacher funktionierender Audio-Stream Test")
    print("=" * 60)
    
    # Teste Imports
    print("🔧 Teste Imports...")
    try:
        import threading
        import sounddevice as sd
        print("✅ sounddevice verfügbar")
    except ImportError as e:
        print(f"❌ sounddevice nicht verfügbar: {e}")
        return 1
    
    try:
        from faster_whisper import WhisperModel
        print("✅ Whisper verfügbar")
    except ImportError as e:
        print(f"❌ Whisper nicht verfügbar: {e}")
        return 1
    
    # Teste Mikrofon
    print("\n🎤 Teste Mikrofon...")
    try:
        devices = sd.query_devices()
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        if input_devices:
            default_device = sd.default.device[0]
            device_name = devices[default_device]['name']
            print(f"✅ Mikrofon gefunden: {device_name}")
        else:
            print("❌ Kein Mikrofon gefunden")
            return 1
    except Exception as e:
        print(f"❌ Mikrofon Test Fehler: {e}")
        return 1
    
    # Starte einfachen Stream
    print("\n🚀 Starte einfachen Audio-Stream...")
    stream = SimpleWorkingStream()
    stream.start()
    
    print("\n💡 Kato Agent System läuft!")
    print("🎯 Teste Kato Wake Words:")
    print("   - 'Kato start' / 'Hey Kato start' / 'Okay Kato start'")
    print("   - 'Kato stopp' / 'Kato einfügen' / 'Kato beenden'")
    print("🛑 Kommandos: start, stopp, einfügen, beenden")
    print("⏹️ Drücke Ctrl+C zum Beenden")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Beende...")
        stream.stop()
    
    print("🎉 Test beendet!")
    return 0

if __name__ == "__main__":
    exit(main())
