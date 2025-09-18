#!/usr/bin/env python3
"""
Hot Word Detection mit Ring Buffer
- 2-Sekunden Chunks alle 1 Sekunde
- 1 Sekunde Überlappung zwischen Chunks
- Kontinuierliche Hot Word Erkennung
- Kato Wake Word System
"""

import time
import threading
import numpy as np
import sounddevice as sd
from collections import deque
from faster_whisper import WhisperModel
from typing import Optional, Callable, List, Dict, Any
import logging
import pyperclip
import pyautogui
import re

# Logging Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HotWordRingBuffer:
    """
    Hot Word Detection mit professionellem Ring Buffer.
    
    Features:
    - Kontinuierlicher Audio-Stream
    - 2-Sekunden Chunks alle 1 Sekunde mit 1s Überlappung
    - Kato Wake Word System
    - Thread-sichere Operationen
    """
    
    def __init__(self, 
                 sample_rate: int = 16000,
                 channels: int = 1,
                 buffer_duration: float = 10.0,  # 10 Sekunden Ring Buffer
                 chunk_size: int = 1024):
        """
        Initialisiere Hot Word Ring Buffer.
        
        Args:
            sample_rate: Audio-Sample-Rate (Hz)
            channels: Anzahl Audio-Kanäle
            buffer_duration: Dauer des Ring Buffers in Sekunden
            chunk_size: Größe der Audio-Chunks für den Stream
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.buffer_duration = buffer_duration
        self.chunk_size = chunk_size
        
        # Ring Buffer Größe berechnen
        self.buffer_samples = int(buffer_duration * sample_rate)
        
        # Ring Buffer mit deque (automatisches Überschreiben)
        self.ring_buffer = deque(maxlen=self.buffer_samples)
        self.buffer_lock = threading.Lock()
        
        # Audio Stream
        self.audio_stream = None
        self.is_recording = False
        
        # Hot Word Detection Parameter
        self.analysis_duration = 2.0  # 2 Sekunden für Analyse
        self.analysis_interval = 1.0    # Alle 1 Sekunde analysieren
        self.overlap_duration = 1.0    # 1 Sekunde Überlappung
        
        # Whisper Modelle
        self.hotword_model = None
        self.transcription_model = None
        
        # Computer Agent System
        self.wake_words = ["computer", "hey computer", "okay computer"]
        self.start_words = ["start"]
        self.stop_words = ["stopp", "stop"]
        self.exit_words = ["beenden", "exit"]
        self.insert_words = ["einfügen", "insert", "paste"]
        
        # State Management
        self.wake_word_detected = False
        self.command_pending = False
        self.is_recording_session = False
        
        # Recording Buffer für Aufnahme
        self.recording_buffer = []
        self.recording_start_time = 0.0
        
        # Statistiken
        self.total_samples_recorded = 0
        self.start_time = 0.0
        self.analysis_counter = 0
        self.last_analysis_time = 0.0
        
        logger.info(f"🎯 Hot Word Ring Buffer initialisiert:")
        logger.info(f"   - Sample Rate: {sample_rate} Hz")
        logger.info(f"   - Buffer Duration: {buffer_duration}s")
        logger.info(f"   - Analysis Duration: {self.analysis_duration}s")
        logger.info(f"   - Analysis Interval: {self.analysis_interval}s")
        logger.info(f"   - Overlap Duration: {self.overlap_duration}s")
    
    def _load_models(self) -> bool:
        """Lade Whisper Modelle."""
        try:
            # Verwende größeres Modell für bessere Hot Word Erkennung
            self.hotword_model = WhisperModel("small", device="cpu", compute_type="float32")
            logger.info("✅ Hot Word Modell geladen (small)")
            self.transcription_model = WhisperModel("medium", device="cpu", compute_type="float32")
            logger.info("✅ Transkriptions-Modell geladen (medium)")
            return True
        except Exception as e:
            logger.error(f"❌ Whisper Modell Fehler: {e}")
            return False
    
    def start(self) -> bool:
        """
        Starte kontinuierliche Hot Word Detection.
        
        Returns:
            True wenn erfolgreich gestartet, False bei Fehler
        """
        if self.is_recording:
            logger.warning("⚠️ Hot Word Detection läuft bereits")
            return True
        
        # Lade Modelle
        if not self._load_models():
            return False
        
        try:
            logger.info("🚀 Starte Hot Word Detection...")
            
            # Audio Stream konfigurieren
            self.audio_stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                blocksize=self.chunk_size,
                dtype=np.float32,
                callback=self._audio_callback,
                finished_callback=self._stream_finished
            )
            
            # Stream starten
            self.audio_stream.start()
            self.is_recording = True
            self.start_time = time.time()
            self.last_analysis_time = time.time()
            self.total_samples_recorded = 0
            
            # Starte Hot Word Detection Thread
            self.hotword_thread = threading.Thread(target=self._hotword_detection_loop, daemon=True)
            self.hotword_thread.start()
            
            logger.info("✅ Hot Word Detection gestartet")
            return True
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Starten: {e}")
            return False
    
    def stop(self):
        """Stoppe Hot Word Detection."""
        if not self.is_recording:
            return
        
        logger.info("🛑 Stoppe Hot Word Detection...")
        
        try:
            if self.audio_stream:
                self.audio_stream.stop()
                self.audio_stream.close()
                self.audio_stream = None
            
            self.is_recording = False
            
            duration = time.time() - self.start_time
            logger.info(f"✅ Hot Word Detection gestoppt nach {duration:.1f}s")
            logger.info(f"📊 Total Samples: {self.total_samples_recorded}")
            logger.info(f"📊 Total Analyses: {self.analysis_counter}")
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Stoppen: {e}")
    
    def _audio_callback(self, indata: np.ndarray, frames: int, time_info, status):
        """
        Audio Callback für kontinuierlichen Stream.
        
        Args:
            indata: Eingangs-Audio-Daten
            frames: Anzahl Frames
            time_info: Zeit-Informationen
            status: Stream-Status
        """
        if status:
            logger.warning(f"⚠️ Audio Stream Status: {status}")
        
        try:
            # Audio-Daten zu Ring Buffer hinzufügen
            with self.buffer_lock:
                # Audio-Daten flach machen (falls mehrkanalig)
                audio_flat = indata.flatten()
                
                # Zu Ring Buffer hinzufügen (automatisches Überschreiben)
                self.ring_buffer.extend(audio_flat)
                
                # Statistiken aktualisieren
                self.total_samples_recorded += len(audio_flat)
                
                # Wenn Aufnahme läuft, zu Recording Buffer hinzufügen
                if self.is_recording_session:
                    self.recording_buffer.append(indata.copy())
        
        except Exception as e:
            logger.error(f"❌ Audio Callback Fehler: {e}")
    
    def _stream_finished(self):
        """Callback wenn Audio Stream beendet wird."""
        logger.info("🔚 Audio Stream beendet")
        self.is_recording = False
    
    def _hotword_detection_loop(self):
        """Hot Word Detection Loop - analysiert alle 1 Sekunde 2-Sekunden Chunks."""
        logger.info("🔄 Hot Word Detection Loop gestartet")
        
        while self.is_recording:
            try:
                current_time = time.time()
                
                # Alle 1 Sekunde analysieren
                if current_time - self.last_analysis_time >= self.analysis_interval:
                    self._analyze_current_chunk()
                    self.last_analysis_time = current_time
                
                # Kurze Pause für bessere Performance
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"❌ Hot Word Detection Loop Fehler: {e}")
                time.sleep(1.0)
    
    def _analyze_current_chunk(self):
        """Analysiere aktuellen 2-Sekunden Chunk auf Hot Words."""
        try:
            self.analysis_counter += 1
            
            # Hole aktuellen 2-Sekunden Chunk aus Ring Buffer
            with self.buffer_lock:
                if not self.ring_buffer:
                    logger.warning("⚠️ Ring Buffer ist leer")
                    return
                
                # Prüfe ob genug Daten vorhanden
                available_samples = len(self.ring_buffer)
                analysis_samples = int(self.analysis_duration * self.sample_rate)
                
                if available_samples < analysis_samples:
                    logger.info(f"⚠️ Noch nicht genug Audio für Analyse: {available_samples}/{analysis_samples}")
                    return
                
                # Hole die letzten 2 Sekunden aus dem Ring Buffer
                current_chunk = np.array(list(self.ring_buffer)[-analysis_samples:])
            
            # Debug: Zeige Chunk-Info
            chunk_max = np.max(np.abs(current_chunk))
            chunk_rms = np.sqrt(np.mean(current_chunk**2))
            logger.info(f"📊 Analyse #{self.analysis_counter}: Chunk {len(current_chunk)} Samples ({self.analysis_duration}s), Max: {chunk_max:.4f}, RMS: {chunk_rms:.4f}")
            
            # Prüfe ob Audio laut genug ist
            if chunk_max > 0.01:
                # Audio normalisieren
                if chunk_max > 0.1:
                    current_chunk = current_chunk / chunk_max * 0.95
                    logger.info(f"📊 Audio normalisiert: Max-Wert {chunk_max:.4f} → 0.95")
                
                # Hot Word Detection in separatem Thread (nicht-blockierend)
                threading.Thread(target=self._check_hot_words, args=(current_chunk,), daemon=True).start()
            else:
                logger.info("🔇 Stille erkannt - überspringe Whisper-Transkription")
                    
        except Exception as e:
            logger.error(f"❌ Chunk-Analyse Fehler: {e}")
    
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
            "computer": ["computer", "computers", "computing", "compute", "computed", "computing"],
            "hey computer": ["hey computer", "hey computers", "hey computing"],
            "okay computer": ["okay computer", "okay computers", "okay computing"]
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
        logger.info("✅ Start Word verarbeitet - Hot Word Detection läuft weiter")
    
    def _on_stop_word_found(self, word: str, text: str):
        """Stop Word gefunden."""
        logger.info(f"🛑 Stop Word erkannt: '{word}' in '{text}'")
        self.stop_recording()
    
    def _on_exit_word_found(self, word: str, text: str):
        """Exit Word erkannt."""
        logger.info(f"🚪 Exit Word erkannt: '{word}' in '{text}'")
        logger.info("🛑 Beende Programm...")
        self.is_recording = False
        import os
        os._exit(0)
    
    def _on_insert_word_found(self, word: str, text: str):
        """Insert Word gefunden - füge Clipboard-Inhalt ein."""
        logger.info(f"📋 Insert Word erkannt: '{word}' in '{text}'")
        self._insert_clipboard_content()
    
    def _insert_clipboard_content(self):
        """Füge Clipboard-Inhalt ein."""
        try:
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
        if self.is_recording_session:
            logger.warning("⚠️ Aufnahme läuft bereits - ignoriere")
            return
            
        logger.info("🎙️ Starte Aufnahme...")
        self.is_recording_session = True
        self.recording_buffer = []
        self.recording_start_time = time.time()
        logger.info("✅ Aufnahme gestartet - Hot Word Detection läuft weiter")
    
    def stop_recording(self):
        """Stoppe Aufnahme und transkribiere."""
        if not self.is_recording_session:
            return

        logger.info("🛑 Stoppe Aufnahme...")
        self.is_recording_session = False

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

def test_hotword_ring_buffer():
    """Teste Hot Word Detection mit Ring Buffer."""
    print("🧪 Hot Word Detection mit Ring Buffer Test")
    print("=" * 60)
    
    # Teste Mikrofon
    print("\n🎤 Teste Mikrofon...")
    try:
        default_input_device = sd.query_devices(kind='input')
        print(f"✅ Mikrofon gefunden: {default_input_device['name']}")
    except Exception as e:
        print(f"❌ Mikrofon Fehler: {e}")
        return 1
    
    # Erstelle Hot Word Ring Buffer
    print("\n🎯 Erstelle Hot Word Ring Buffer...")
    hotword_buffer = HotWordRingBuffer(
        sample_rate=16000,
        channels=1,
        buffer_duration=10.0,  # 10 Sekunden Buffer
        chunk_size=1024
    )
    
    # Starte Hot Word Detection
    print("\n🚀 Starte Hot Word Detection...")
    if not hotword_buffer.start():
        print("❌ Fehler beim Starten")
        return 1
    
    print("✅ Hot Word Detection läuft!")
    print("🎯 Teste Computer Wake Words:")
    print("   - 'Computer start' / 'Hey Computer start' / 'Okay Computer start'")
    print("   - 'Computer stopp' / 'Computer einfügen' / 'Computer beenden'")
    print("🛑 Kommandos: start, stopp, einfügen, beenden")
    print("⏹️ Drücke Ctrl+C zum Beenden")
    
    try:
        while True:
            time.sleep(1)
                
    except KeyboardInterrupt:
        print("\n🛑 Beende...")
    finally:
        hotword_buffer.stop()
        print("🎉 Test beendet!")

if __name__ == "__main__":
    test_hotword_ring_buffer()
