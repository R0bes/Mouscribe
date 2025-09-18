#!/usr/bin/env python3
"""
Professionelle Ring Buffer Lösung mit sounddevice
- Verwendet sounddevice.InputStream mit Callback
- Eingebauter Ring Buffer für kontinuierliche Audio-Daten
- 2-Sekunden Segmente alle 0.5 Sekunden mit 1.5s Überlappung
"""

import time
import threading
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from collections import deque
from typing import Optional, Callable, List, Dict, Any
import logging
import sys
import pyperclip
import re

# Logging Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProfessionalRingBufferAgent:
    """Agent mit professionellem Ring Buffer und sounddevice InputStream."""
    
    def __init__(self):
        self.running = False
        self.hotword_model = None
        self.transcription_model = None
        
        # Kato Agent System
        self.wake_words = ["kato", "hey kato", "okay kato"]
        self.start_words = ["start"]
        self.stop_words = ["stopp", "stop"]
        self.exit_words = ["beenden", "exit"]
        self.insert_words = ["einfügen", "insert", "paste"]
        
        # State Management
        self.wake_word_detected = False
        self.command_pending = False
        self.is_recording = False
        
        # Audio Parameter
        self.sample_rate = 16000
        self.chunk_duration = 0.5  # 0.5 Sekunden Chunks
        self.analysis_duration = 2.0  # 2 Sekunden für Analyse
        self.overlap_duration = 1.5  # 1.5 Sekunden Überlappung
        self.chunk_samples = int(self.chunk_duration * self.sample_rate)
        self.analysis_samples = int(self.analysis_duration * self.sample_rate)
        self.overlap_samples = int(self.overlap_duration * self.sample_rate)
        
        # Professioneller Ring Buffer mit deque
        self.ring_buffer = deque(maxlen=self.analysis_samples * 2)  # 4 Sekunden Ring Buffer
        self.ring_buffer_lock = threading.Lock()
        
        # Recording Buffer für Aufnahme
        self.recording_buffer = []
        self.recording_start_time = 0.0
        
        # Analysis Timer
        self.last_analysis_time = 0
        self.analysis_interval = 0.5  # Alle 0.5 Sekunden analysieren
        
        # Debug Counter
        self.chunk_counter = 0
        self.analysis_counter = 0
        
        # Audio Stream
        self.audio_stream = None
        
    def _load_models(self) -> bool:
        """Lade Whisper Modelle."""
        try:
            # Verwende größeres Modell für bessere Hot Word Erkennung
            self.hotword_model = WhisperModel("small", device="cpu", compute_type="float32")
            logger.info("✅ Hot Word Modell geladen (small - verbessert)")
            self.transcription_model = WhisperModel("medium", device="cpu", compute_type="float32")
            logger.info("✅ Transkriptions-Modell geladen (medium - verbessert)")
            return True
        except Exception as e:
            logger.error(f"❌ Whisper Modell Fehler: {e}")
            return False
    
    def start(self):
        """Starte den Agent mit professionellem Ring Buffer."""
        if self.running:
            logger.warning("⚠️ Agent läuft bereits")
            return

        logger.info("🚀 Starte Agent mit professionellem Ring Buffer...")
        logger.info(f"📊 Ring Buffer Größe: {self.analysis_samples * 2} Samples ({self.analysis_samples * 2 / self.sample_rate:.1f}s)")
        logger.info(f"📊 Chunk Größe: {self.chunk_samples} Samples ({self.chunk_duration}s)")
        logger.info(f"📊 Segment Größe: {self.analysis_samples} Samples ({self.analysis_duration}s)")
        logger.info(f"📊 Überlappung: {self.overlap_samples} Samples ({self.overlap_duration}s)")
        
        if not self._load_models():
            return

        self.running = True
        
        # Starte Audio Stream mit Callback
        self._start_audio_stream()
        
        # Starte Analysis Thread
        self.analysis_thread = threading.Thread(target=self._analysis_loop, daemon=True)
        self.analysis_thread.start()
        
        logger.info("✅ Agent mit professionellem Ring Buffer läuft")
    
    def stop(self):
        """Stoppe den Agent."""
        if not self.running:
            return
        
        logger.info("🛑 Stoppe Agent...")
        self.running = False
        
        if self.audio_stream:
            self.audio_stream.stop()
            self.audio_stream.close()
        
        if self.analysis_thread:
            self.analysis_thread.join(timeout=5)
            
        logger.info("✅ Agent gestoppt")
    
    def _start_audio_stream(self):
        """Starte Audio Stream mit Callback."""
        try:
            self.audio_stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.float32,
                blocksize=self.chunk_samples,
                callback=self._audio_callback,
                latency='low'
            )
            self.audio_stream.start()
            logger.info("✅ Audio Stream gestartet")
        except Exception as e:
            logger.error(f"❌ Audio Stream Fehler: {e}")
            raise
    
    def _audio_callback(self, indata, frames, time, status):
        """Audio Callback für kontinuierliche Audio-Daten."""
        if status:
            logger.warning(f"⚠️ Audio Status: {status}")
        
        if indata is not None and len(indata) > 0:
            # Audio-Daten zu Ring Buffer hinzufügen (vereinfacht)
            try:
                with self.ring_buffer_lock:
                    self.chunk_counter += 1
                    audio_flat = indata.flatten()
                    
                    # Füge Audio-Daten zum Ring Buffer hinzu (batch)
                    self.ring_buffer.extend(audio_flat)
                    
                    # Debug: Zeige Ring Buffer Status
                    if self.chunk_counter % 10 == 0:  # Alle 10 Chunks
                        logger.info(f"📊 Chunk #{self.chunk_counter}: Ring Buffer gefüllt mit {len(self.ring_buffer)} Samples")
            except Exception as e:
                logger.error(f"❌ Audio Callback Fehler: {e}")
    
    def _analysis_loop(self):
        """Analysis Loop für kontinuierliche Hot Word Detection."""
        logger.info("🔄 Analysis Loop gestartet")
        
        while self.running:
            try:
                # Alle 0.5 Sekunden analysieren
                current_time = time.time()
                if current_time - self.last_analysis_time >= self.analysis_interval:
                    # Prüfe ob wir genug Audio für Analyse haben
                    with self.ring_buffer_lock:
                        if len(self.ring_buffer) >= self.analysis_samples:
                            self._analyze_current_segment()
                        else:
                            logger.info(f"⚠️ Noch nicht genug Audio für Analyse: {len(self.ring_buffer)}/{self.analysis_samples}")
                    
                    self.last_analysis_time = current_time
                
                time.sleep(0.01)  # 10ms für bessere Responsivität
                    
            except Exception as e:
                logger.error(f"❌ Analysis Loop Fehler: {e}")
    
    def _analyze_current_segment(self):
        """Analysiere aktuelles 2-Sekunden Segment auf Hot Words."""
        try:
            self.analysis_counter += 1
            
            # Hole aktuelles Segment aus Ring Buffer
            with self.ring_buffer_lock:
                # Hole die letzten analysis_samples aus dem Ring Buffer
                current_segment = np.array(list(self.ring_buffer)[-self.analysis_samples:])
            
            # Debug: Zeige Segment-Info
            segment_max = np.max(np.abs(current_segment))
            segment_rms = np.sqrt(np.mean(current_segment**2))
            logger.info(f"📊 Analyse #{self.analysis_counter}: Segment {len(current_segment)} Samples ({self.analysis_duration}s), Max: {segment_max:.4f}, RMS: {segment_rms:.4f}")
            
            # Prüfe ob Audio laut genug ist
            if segment_max > 0.01:
                # Audio normalisieren
                if segment_max > 0.1:
                    current_segment = current_segment / segment_max * 0.95
                    logger.info(f"📊 Audio normalisiert: Max-Wert {segment_max:.4f} → 0.95")
                
                # Hot Word Detection in separatem Thread (nicht-blockierend)
                threading.Thread(target=self._check_hot_words, args=(current_segment,), daemon=True).start()
            else:
                logger.info("🔇 Stille erkannt - überspringe Whisper-Transkription")
                    
        except Exception as e:
            logger.error(f"❌ Segment-Analyse Fehler: {e}")
    
    def _check_hot_words(self, audio_data: np.ndarray):
        """Prüfe auf Hot Words mit verbesserter Erkennung."""
        try:
            # Verbesserte Whisper Transkription für bessere Erkennung
            segments, info = self.hotword_model.transcribe(
                audio=audio_data,
                language="de",
                vad_filter=True,  # Voice Activity Detection aktiviert
                beam_size=5,      # Mehr Beam Search für bessere Erkennung
                best_of=5,        # Mehr Kandidaten für bessere Erkennung
                temperature=0.0,  # Deterministisch
                condition_on_previous_text=False,  # Keine Abhängigkeit von vorherigem Text
            )
            
            text_parts = [seg.text.strip() for seg in segments]
            text = " ".join([t for t in text_parts if t]).lower().strip()
            
            if text:
                logger.info(f"🎤 Audio erkannt: '{text}'")
                
                # Prüfe auf Wake Word + Kommando
                self._process_wake_word_command(text)
            else:
                logger.debug("🔇 Stille erkannt")
                
        except Exception as e:
            logger.error(f"❌ Hot Word Check Fehler: {e}")
    
    def _process_wake_word_command(self, text: str):
        """Verarbeite Wake Word + Kommando Pattern mit verbesserter Erkennung."""
        text_lower = text.lower()
        
        # Verbesserte Wake Word Erkennung mit Fuzzy Matching
        detected_wake_word = self._fuzzy_wake_word_detection(text_lower)
        
        if detected_wake_word:
            logger.info(f"🎯 Wake Word '{detected_wake_word}' erkannt!")
            self.wake_word_detected = True
            self.command_pending = True
            
            # Extrahiere das Kommando nach dem Wake Word
            wake_word_pos = text_lower.find(detected_wake_word)
            command_text = text_lower[wake_word_pos + len(detected_wake_word):].strip()
            
            logger.info(f"📝 Kommando-Text: '{command_text}'")
            
            # Prüfe auf Kommandos
            self._check_command(command_text)
            
        elif self.command_pending:
            # Wenn Wake Word bereits erkannt, prüfe nur auf Kommandos
            logger.info(f"📝 Kommando-Text (ohne Wake Word): '{text_lower}'")
            self._check_command(text_lower)
        else:
            # Kein Wake Word erkannt - ignoriere
            logger.debug("🔇 Kein Wake Word erkannt - ignoriere")
    
    def _fuzzy_wake_word_detection(self, text: str) -> Optional[str]:
        """Fuzzy Wake Word Detection für bessere Erkennung."""
        # Direkte Matches
        for wake_word in self.wake_words:
            if wake_word in text:
                return wake_word
        
        # Fuzzy Matches für häufige Erkennungsfehler
        fuzzy_patterns = {
            "kato": ["kartel", "kartour", "kanzo", "karto", "kato", "katost", "katostar", "kau", "kaut"],
            "hey kato": ["hey kartel", "hey kartour", "hey karto", "hey kau"],
            "okay kato": ["okay kartel", "okay kartour", "okay karto", "okay kau"]
        }
        
        for wake_word, patterns in fuzzy_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    logger.info(f"🔍 Fuzzy Match: '{pattern}' → '{wake_word}'")
                    return wake_word
        
        return None
    
    def _check_command(self, command_text: str):
        """Prüfe auf spezifische Kommandos mit verbesserter Erkennung."""
        # Verbesserte Kommando-Erkennung mit Fuzzy Matching
        
        # Start Kommando mit Fuzzy Matching
        start_patterns = ["start", "stark", "stahl", "starten", "starte"]
        for pattern in start_patterns:
            if pattern in command_text:
                logger.info(f"🔍 Start Fuzzy Match: '{pattern}' → 'start'")
                self._on_start_word_found("start", command_text)
                self._reset_wake_word_state()
                return
        
        # Stop Kommando mit Fuzzy Matching
        stop_patterns = ["stopp", "stop", "stoppen", "stoppe", "halt", "halte"]
        for pattern in stop_patterns:
            if pattern in command_text:
                logger.info(f"🔍 Stop Fuzzy Match: '{pattern}' → 'stopp'")
                self._on_stop_word_found("stopp", command_text)
                self._reset_wake_word_state()
                return
        
        # Exit Kommando mit Fuzzy Matching
        exit_patterns = ["beenden", "beende", "exit", "ende", "schließen", "quit"]
        for pattern in exit_patterns:
            if pattern in command_text:
                logger.info(f"🔍 Exit Fuzzy Match: '{pattern}' → 'beenden'")
                self._on_exit_word_found("beenden", command_text)
                self._reset_wake_word_state()
                return
        
        # Insert Kommando mit Fuzzy Matching
        insert_patterns = ["einfügen", "einfüge", "insert", "paste", "fügen", "füge"]
        for pattern in insert_patterns:
            if pattern in command_text:
                logger.info(f"🔍 Insert Fuzzy Match: '{pattern}' → 'einfügen'")
                self._on_insert_word_found("einfügen", command_text)
                self._reset_wake_word_state()
                return
        
        # Kein gültiges Kommando erkannt
        logger.warning(f"⚠️ Kein gültiges Kommando in '{command_text}' erkannt")
        self._reset_wake_word_state()
    
    def _reset_wake_word_state(self):
        """Reset Wake Word State."""
        self.wake_word_detected = False
        self.command_pending = False
        logger.debug("🔄 Wake Word State zurückgesetzt")
    
    def _on_start_word_found(self, word: str, text: str):
        """Start Word gefunden."""
        logger.info(f"🎯 Start Word erkannt: '{word}' in '{text}'")
        self.start_recording()
        logger.info("✅ Start Word verarbeitet - Streaming läuft weiter")
    
    def _on_stop_word_found(self, word: str, text: str):
        """Stop Word gefunden."""
        logger.info(f"🛑 Stop Word erkannt: '{word}' in '{text}'")
        self.stop_recording()
    
    def _on_exit_word_found(self, word: str, text: str):
        """Exit Word erkannt."""
        logger.info(f"🚪 Exit Word erkannt: '{word}' in '{text}'")
        logger.info("🛑 Beende Programm...")
        self.running = False
        import os
        os._exit(0)
    
    def _on_insert_word_found(self, word: str, text: str):
        """Insert Word gefunden - füge Clipboard-Inhalt ein."""
        logger.info(f"📋 Insert Word erkannt: '{word}' in '{text}'")
        self._insert_clipboard_content()
    
    def _insert_clipboard_content(self):
        """Füge Clipboard-Inhalt ein."""
        try:
            import pyperclip
            import pyautogui
            
            clipboard_text = pyperclip.paste()
            
            if clipboard_text:
                logger.info(f"📋 Clipboard-Inhalt: '{clipboard_text}'")
                pyautogui.hotkey('ctrl', 'v')
                logger.info("✅ Clipboard-Inhalt eingefügt!")
            else:
                logger.warning("⚠️ Clipboard ist leer")
                
        except ImportError:
            logger.error("❌ pyautogui nicht verfügbar - kann nicht einfügen")
        except Exception as e:
            logger.error(f"❌ Fehler beim Einfügen: {e}")
    
    def start_recording(self):
        """Starte Aufnahme."""
        if self.is_recording:
            logger.warning("⚠️ Aufnahme läuft bereits - ignoriere")
            return
            
        logger.info("🎙️ Starte Aufnahme...")
        self.is_recording = True
        self.recording_buffer = []
        self.recording_start_time = time.time()
        logger.info("✅ Aufnahme gestartet - Streaming läuft weiter")
    
    def stop_recording(self):
        """Stoppe Aufnahme und transkribiere."""
        if not self.is_recording:
            return

        logger.info("🛑 Stoppe Aufnahme...")
        self.is_recording = False

        if self.recording_buffer:
            logger.info(f"📊 Recording Buffer: {len(self.recording_buffer)} Chunks")
            
            # Echte überlappende Audio-Zusammensetzung
            full_audio = self._overlapping_audio_composition()
            duration = time.time() - self.recording_start_time

            logger.info(f"📊 Aufnahme abgeschlossen:")
            logger.info(f"   - Dauer: {duration:.1f}s")
            logger.info(f"   - Samples: {len(full_audio)}")
            logger.info(f"   - Chunks: {len(self.recording_buffer)}")

            self._transcribe_recording(full_audio)
        else:
            logger.warning("⚠️ Keine Audio-Daten gesammelt")
    
    def _overlapping_audio_composition(self) -> np.ndarray:
        """Echte überlappende Audio-Zusammensetzung."""
        if not self.recording_buffer:
            return np.array([])
        
        if len(self.recording_buffer) == 1:
            return self.recording_buffer[0].flatten()
        
        # Echte überlappende Zusammensetzung
        chunk_duration = 0.5  # 0.5 Sekunden pro Chunk
        chunk_samples = int(chunk_duration * self.sample_rate)
        overlap_samples = int(0.25 * self.sample_rate)  # 0.25 Sekunden Überlappung
        
        result = []
        
        for i, chunk in enumerate(self.recording_buffer):
            chunk_flat = chunk.flatten()
            
            if i == 0:
                # Erstes Chunk komplett hinzufügen
                result.append(chunk_flat)
            else:
                # Überlappung mit Crossfade
                if len(result) > 0 and len(chunk_flat) >= overlap_samples:
                    # Letzte overlap_samples des vorherigen Chunks
                    prev_tail = result[-1][-overlap_samples:]
                    # Erste overlap_samples des aktuellen Chunks
                    curr_head = chunk_flat[:overlap_samples]
                    
                    # Crossfade (sanfter Übergang)
                    fade_out = np.linspace(1, 0, overlap_samples)
                    fade_in = np.linspace(0, 1, overlap_samples)
                    
                    crossfade = prev_tail * fade_out + curr_head * fade_in
                    
                    # Ersetze das Ende des vorherigen Chunks
                    result[-1] = np.concatenate([result[-1][:-overlap_samples], crossfade])
                    
                    # Füge den Rest des aktuellen Chunks hinzu
                    result.append(chunk_flat[overlap_samples:])
                else:
                    result.append(chunk_flat)
        
        return np.concatenate(result)
    
    def _transcribe_recording(self, audio_data: np.ndarray):
        """Transkribiere Aufnahme mit professionellem Modell."""
        try:
            logger.info("🎯 Starte professionelle Transkription...")
            
            # Audio normalisieren
            if np.max(np.abs(audio_data)) > 0:
                max_val = np.max(np.abs(audio_data))
                if max_val > 0.1:
                    audio_data = audio_data / max_val * 0.95
            
            # Professionelle Whisper Transkription
            segments, info = self.transcription_model.transcribe(
                audio=audio_data,
                language="de",
                vad_filter=False,
                beam_size=5,
                best_of=5,
                temperature=0.0,
            )
            
            segments_list = list(segments)
            logger.info(f"📊 Whisper Segmente: {len(segments_list)}")
            
            # Text zusammenfügen und bereinigen
            text_parts = [seg.text.strip() for seg in segments_list]
            full_text = " ".join([t for t in text_parts if t]).strip()
            
            # Professionelle Text-Bereinigung
            full_text = self._clean_transcription_text(full_text)
            
            if full_text:
                logger.info("✅ Professionelle Transkription erfolgreich:")
                logger.info(f"📝 Vollständiger Text: '{full_text}'")
                logger.info(f"📊 Transkriptions-Info: {info.duration:.1f}s Audio verarbeitet")

                # Kopiere in Zwischenablage
                try:
                    pyperclip.copy(full_text)
                    logger.info("📋 Text erfolgreich in Zwischenablage kopiert!")
                except Exception as e:
                    logger.error(f"❌ Fehler beim Kopieren: {e}")
            else:
                logger.warning("⚠️ Kein Text in der Aufnahme erkannt")

        except Exception as e:
            logger.error(f"❌ Fehler bei professioneller Transkription: {e}")
    
    def _clean_transcription_text(self, text: str) -> str:
        """Professionelle Text-Bereinigung."""
        if not text:
            return text
            
        # Entferne "stopp" am Ende
        if text.lower().endswith("stopp"):
            text = text[:-5].strip()
            logger.info("🔧 'stopp' am Ende entfernt")
        
        # Entferne überflüssige Satzzeichen am Ende
        while text and text[-1] in "!?.":
            text = text[:-1].strip()
            logger.info("🔧 Satzzeichen am Ende entfernt")
        
        # Entferne mehrfache Leerzeichen
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

def main():
    """Hauptfunktion für Agent mit professionellem Ring Buffer."""
    print("🧪 Agent mit professionellem Ring Buffer Test")
    print("=" * 60)
    
    # Teste Mikrofon
    print("\n🎤 Teste Mikrofon...")
    try:
        default_input_device = sd.query_devices(kind='input')
        print(f"✅ Mikrofon gefunden: {default_input_device['name']}")
    except Exception as e:
        print(f"❌ Mikrofon Fehler: {e}")
        return 1
    
    # Starte Agent
    print("\n🚀 Starte Agent mit professionellem Ring Buffer...")
    agent = ProfessionalRingBufferAgent()
    agent.start()
    
    print("\n💡 Agent mit professionellem Ring Buffer läuft!")
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
    finally:
        agent.stop()
        print("🎉 Test beendet!")

if __name__ == "__main__":
    exit(main())
