#!/usr/bin/env python3
"""
Computer Agent mit vereinfachter Architektur
- "Computer" → Aufmerksamkeitsmodus aktivieren
- Im Aufmerksamkeitsmodus → Tiefgreifende Kommandos verarbeiten
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

class ComputerAgent:
    """
    Computer Agent mit vereinfachter Architektur.
    
    Features:
    - "Computer" → Aufmerksamkeitsmodus aktivieren
    - Im Aufmerksamkeitsmodus → Tiefgreifende Kommandos verarbeiten
    - Kontinuierlicher Audio-Stream mit Ring Buffer
    - 2-Sekunden Chunks alle 1 Sekunde mit 1s Überlappung
    """
    
    def __init__(self, 
                 sample_rate: int = 16000,
                 channels: int = 1,
                 buffer_duration: float = 10.0,
                 chunk_size: int = 1024):
        """
        Initialisiere Computer Agent.
        
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
        self.normal_analysis_duration = 2.0  # 2.0 Sekunden für normale Analyse
        self.normal_analysis_interval = 1.0    # Alle 1.0 Sekunden analysieren (normal)
        self.attention_analysis_duration = 3.0  # 3.0 Sekunden für Aufmerksamkeitsmodus
        self.attention_analysis_interval = 2.0    # Alle 2.0 Sekunden analysieren (Aufmerksamkeit)
        self.overlap_duration = 1.0    # 1 Sekunde Überlappung
        
        # Whisper Modelle
        self.hotword_model = None
        self.transcription_model = None
        
        # Vereinfachte Architektur
        self.wake_word = "computer"
        self.attention_mode = False
        self.attention_timeout = 5.0  # 5 Sekunden Aufmerksamkeitsmodus
        self.recording_timeout = 5.0  # 5 Sekunden Aufnahme-Timeout
        self.last_attention_time = 0.0
        self.last_recording_time = 0.0
        
        # Kommandos im Aufmerksamkeitsmodus
        self.commands = {
            "aufnahme starten": self._start_recording,
            "aufnahme stoppen": self._stop_recording,
            "programm beenden": self._exit_program,
            "clipboard einfügen": self._insert_clipboard,
            "aufmerksamkeit beenden": self._end_attention_mode
        }
        
        # Recording Buffer für Aufnahme
        self.recording_buffer = []
        self.recording_start_time = 0.0
        self.is_recording_session = False
        
        # Statistiken
        self.total_samples_recorded = 0
        self.start_time = 0.0
        self.analysis_counter = 0
        self.last_analysis_time = 0.0
        
        logger.info(f"🎯 Computer Agent initialisiert:")
        logger.info(f"   - Sample Rate: {sample_rate} Hz")
        logger.info(f"   - Buffer Duration: {buffer_duration}s")
        logger.info(f"   - Normal Analysis Duration: {self.normal_analysis_duration}s")
        logger.info(f"   - Normal Analysis Interval: {self.normal_analysis_interval}s")
        logger.info(f"   - Attention Analysis Duration: {self.attention_analysis_duration}s")
        logger.info(f"   - Attention Analysis Interval: {self.attention_analysis_interval}s")
        logger.info(f"   - Wake Word: '{self.wake_word}'")
        logger.info(f"   - Attention Timeout: {self.attention_timeout}s")
        logger.info(f"   - Recording Timeout: {self.recording_timeout}s")
    
    def _load_models(self) -> bool:
        """Lade Whisper Modelle."""
        try:
            # Verwende größeres Modell für bessere Erkennung
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
        Starte Computer Agent.
        
        Returns:
            True wenn erfolgreich gestartet, False bei Fehler
        """
        if self.is_recording:
            logger.warning("⚠️ Computer Agent läuft bereits")
            return True
        
        # Lade Modelle
        if not self._load_models():
            return False
        
        try:
            logger.info("🚀 Starte Computer Agent...")
            
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
            
            logger.info("✅ Computer Agent gestartet")
            return True
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Starten: {e}")
            return False
    
    def stop(self):
        """Stoppe Computer Agent."""
        if not self.is_recording:
            return
        
        logger.info("🛑 Stoppe Computer Agent...")
        
        try:
            if self.audio_stream:
                self.audio_stream.stop()
                self.audio_stream.close()
                self.audio_stream = None
            
            self.is_recording = False
            
            duration = time.time() - self.start_time
            logger.info(f"✅ Computer Agent gestoppt nach {duration:.1f}s")
            logger.info(f"📊 Total Samples: {self.total_samples_recorded}")
            logger.info(f"📊 Total Analyses: {self.analysis_counter}")
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Stoppen: {e}")
    
    def _audio_callback(self, indata: np.ndarray, frames: int, time_info, status):
        """Audio Callback für kontinuierlichen Stream."""
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
                    self.last_recording_time = time.time()  # Reset Recording Timeout
        
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
                
                # Dynamische Analyse-Intervalle basierend auf Modus
                if self.attention_mode:
                    # Aufmerksamkeitsmodus: Alle 2.0 Sekunden analysieren
                    if current_time - self.last_analysis_time >= self.attention_analysis_interval:
                        self._analyze_current_chunk()
                        self.last_analysis_time = current_time
                else:
                    # Normaler Modus: Alle 1.0 Sekunden analysieren
                    if current_time - self.last_analysis_time >= self.normal_analysis_interval:
                        self._analyze_current_chunk()
                        self.last_analysis_time = current_time
                
                # Prüfe Aufmerksamkeitsmodus Timeout
                if self.attention_mode:
                    if current_time - self.last_attention_time > self.attention_timeout:
                        self._end_attention_mode()
                
                # Prüfe Aufnahme Timeout
                if self.is_recording_session:
                    if current_time - self.last_recording_time > self.recording_timeout:
                        logger.info("⏰ Aufnahme-Timeout erreicht - stoppe automatisch")
                        self._stop_recording()
                
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
                
                # Dynamische Chunk-Größe basierend auf Modus
                if self.attention_mode:
                    analysis_duration = self.attention_analysis_duration
                else:
                    analysis_duration = self.normal_analysis_duration
                
                # Prüfe ob genug Daten vorhanden
                available_samples = len(self.ring_buffer)
                analysis_samples = int(analysis_duration * self.sample_rate)
                
                if available_samples < analysis_samples:
                    logger.info(f"⚠️ Noch nicht genug Audio für Analyse: {available_samples}/{analysis_samples}")
                    return
                
                # Hole die entsprechenden Sekunden aus dem Ring Buffer
                current_chunk = np.array(list(self.ring_buffer)[-analysis_samples:])
            
            # Debug: Zeige Chunk-Info
            chunk_max = np.max(np.abs(current_chunk))
            chunk_rms = np.sqrt(np.mean(current_chunk**2))
            
            if self.attention_mode:
                logger.info(f"👂 Aufmerksamkeitsmodus - Analyse #{self.analysis_counter}: Chunk {len(current_chunk)} Samples ({analysis_duration}s), Max: {chunk_max:.4f}, RMS: {chunk_rms:.4f}")
            else:
                logger.info(f"🔍 Suche nach '{self.wake_word}' - Analyse #{self.analysis_counter}: Chunk {len(current_chunk)} Samples ({analysis_duration}s), Max: {chunk_max:.4f}, RMS: {chunk_rms:.4f}")
            
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
                
                if self.attention_mode:
                    # Im Aufmerksamkeitsmodus: Prüfe auf Kommandos
                    self._process_command(text)
                    self.last_attention_time = time.time()  # Reset Attention Timeout
                else:
                    # Normaler Modus: Prüfe auf Wake Word
                    self._check_wake_word(text)
            else:
                logger.debug("🔇 Stille erkannt")
                
        except Exception as e:
            logger.error(f"❌ Hot Word Check Fehler: {e}")
    
    def _check_wake_word(self, text: str):
        """Prüfe auf Wake Word 'computer'."""
        if self.wake_word in text:
            logger.info(f"🎯 Wake Word '{self.wake_word}' erkannt!")
            self._start_attention_mode()
        else:
            logger.debug("🔇 Kein Wake Word erkannt - ignoriere")
    
    def _start_attention_mode(self):
        """Starte Aufmerksamkeitsmodus."""
        self.attention_mode = True
        self.last_attention_time = time.time()
        logger.info("👂 Aufmerksamkeitsmodus aktiviert!")
        logger.info("💡 Verfügbare Kommandos:")
        for cmd in self.commands.keys():
            logger.info(f"   - '{cmd}'")
    
    def _end_attention_mode(self):
        """Beende Aufmerksamkeitsmodus."""
        self.attention_mode = False
        logger.info("🔇 Aufmerksamkeitsmodus beendet")
    
    def _process_command(self, text: str):
        """Verarbeite Kommando im Aufmerksamkeitsmodus."""
        text_lower = text.lower()
        
        # Prüfe auf verfügbare Kommandos
        for command, handler in self.commands.items():
            if command in text_lower:
                logger.info(f"🎯 Kommando '{command}' erkannt!")
                handler()
                self.last_attention_time = time.time()  # Reset Attention Timeout
                return
        
        # Kein gültiges Kommando erkannt
        logger.warning(f"⚠️ Kein gültiges Kommando in '{text_lower}' erkannt")
        logger.info("💡 Verfügbare Kommandos:")
        for cmd in self.commands.keys():
            logger.info(f"   - '{cmd}'")
    
    def _start_recording(self):
        """Starte Aufnahme."""
        if self.is_recording_session:
            logger.warning("⚠️ Aufnahme läuft bereits - ignoriere")
            return
            
        logger.info("🎙️ Starte Aufnahme...")
        self.is_recording_session = True
        self.recording_buffer = []
        self.recording_start_time = time.time()
        self.last_recording_time = time.time()  # Reset Recording Timeout
        logger.info("✅ Aufnahme gestartet - Aufmerksamkeitsmodus läuft weiter")
    
    def _stop_recording(self):
        """Stoppe Aufnahme und transkribiere."""
        if not self.is_recording_session:
            logger.warning("⚠️ Keine Aufnahme läuft")
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
    
    def _exit_program(self):
        """Beende Programm."""
        logger.info("🚪 Programm wird beendet...")
        self.is_recording = False
        import os
        os._exit(0)
    
    def _insert_clipboard(self):
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
            
        # Entferne überflüssige Satzzeichen am Ende
        while text and text[-1] in "!?.":
            text = text[:-1].strip()
            logger.info("🔧 Satzzeichen am Ende entfernt")
        
        # Entferne mehrfache Leerzeichen
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

def test_computer_agent():
    """Teste Computer Agent."""
    print("🧪 Computer Agent Test")
    print("=" * 50)
    
    # Teste Mikrofon
    print("\n🎤 Teste Mikrofon...")
    try:
        default_input_device = sd.query_devices(kind='input')
        print(f"✅ Mikrofon gefunden: {default_input_device['name']}")
    except Exception as e:
        print(f"❌ Mikrofon Fehler: {e}")
        return 1
    
    # Erstelle Computer Agent
    print("\n🎯 Erstelle Computer Agent...")
    agent = ComputerAgent(
        sample_rate=16000,
        channels=1,
        buffer_duration=10.0,  # 10 Sekunden Buffer
        chunk_size=1024
    )
    
    # Starte Computer Agent
    print("\n🚀 Starte Computer Agent...")
    if not agent.start():
        print("❌ Fehler beim Starten")
        return 1
    
    print("✅ Computer Agent läuft!")
    print("🎯 Teste Wake Word:")
    print("   - Sage 'Computer' um Aufmerksamkeitsmodus zu aktivieren")
    print("💡 Verfügbare Kommandos im Aufmerksamkeitsmodus:")
    print("   - 'aufnahme starten'")
    print("   - 'aufnahme stoppen'")
    print("   - 'clipboard einfügen'")
    print("   - 'programm beenden'")
    print("   - 'aufmerksamkeit beenden'")
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
    test_computer_agent()
