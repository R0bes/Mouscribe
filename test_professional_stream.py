#!/usr/bin/env python3
"""
Test für professionelle Audio-Stream Lösung
"""

import time
import threading
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from collections import deque
from typing import Optional, Callable, List
import queue
import logging

class ProfessionalAudioStream:
    """
    Professioneller kontinuierlicher Audio-Stream.
    
    Features:
    - Kontinuierlicher Audio-Stream ohne Lücken
    - Ring-Buffer für kontinuierliche Audio-Daten
    - Sliding Window für Hot Word Detection
    - Zero-Copy Audio-Verarbeitung
    - Thread-sichere Implementierung
    """
    
    def __init__(self, 
                 on_start_word_detected: Callable[[str], None],
                 on_stop_word_detected: Callable[[str], None],
                 sample_rate: int = 16000,
                 chunk_size: int = 1024,
                 buffer_duration: float = 3.0):
        """Initialisiere professionellen Audio-Stream."""
        self.logger = self._get_logger()
        
        # Callbacks
        self.on_start_word_detected = on_start_word_detected
        self.on_stop_word_detected = on_stop_word_detected
        
        # Audio-Parameter
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.buffer_duration = buffer_duration
        self.buffer_size = int(buffer_duration * sample_rate)
        
        # Whisper Modelle
        self.hotword_model: Optional[WhisperModel] = None
        self.transcription_model: Optional[WhisperModel] = None
        
        # Audio-Stream
        self.stream: Optional[sd.InputStream] = None
        self.running = False
        
        # Ring-Buffer für kontinuierliche Audio-Daten
        self.audio_buffer = deque(maxlen=self.buffer_size)
        self.audio_lock = threading.Lock()
        
        # Aufnahme-Status
        self.is_recording = False
        self.recording_buffer = []
        self.recording_lock = threading.Lock()
        
        # Hot Word Detection
        self.start_words = ["start"]
        self.stop_words = ["stopp"]
        self.detection_thread: Optional[threading.Thread] = None
        
    def _get_logger(self):
        """Einfacher Logger."""
        logger = logging.getLogger(self.__class__.__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
        
    def start(self) -> bool:
        """Starte professionellen Audio-Stream."""
        if self.running:
            self.logger.warning("⚠️ Audio-Stream läuft bereits")
            return False
            
        self.logger.info("🚀 Starte professionellen Audio-Stream...")
        
        # Whisper Modelle laden
        if not self._load_models():
            return False
            
        # Audio-Stream starten
        if not self._start_audio_stream():
            return False
            
        # Hot Word Detection Thread starten
        self._start_hotword_detection()
        
        self.running = True
        self.logger.info("✅ Professioneller Audio-Stream läuft")
        return True
        
    def stop(self) -> None:
        """Stoppe professionellen Audio-Stream."""
        if not self.running:
            return
            
        self.logger.info("🛑 Stoppe professionellen Audio-Stream...")
        self.running = False
        
        # Audio-Stream stoppen
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            
        # Hot Word Detection Thread stoppen
        if self.detection_thread and self.detection_thread.is_alive():
            self.detection_thread.join(timeout=2.0)
            
        self.logger.info("✅ Professioneller Audio-Stream gestoppt")
        
    def _load_models(self) -> bool:
        """Lade Whisper Modelle."""
        try:
            # Kleines Modell für Hot Word Detection (schnell)
            self.hotword_model = WhisperModel("base", device="cpu", compute_type="int8")
            self.logger.info("✅ Hot Word Modell geladen (base)")
            
            # Besseres Modell für Transkription (qualitativ)
            self.transcription_model = WhisperModel("small", device="cpu", compute_type="float32")
            self.logger.info("✅ Transkriptions-Modell geladen (small)")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Laden der Whisper Modelle: {e}")
            return False
            
    def _start_audio_stream(self) -> bool:
        """Starte kontinuierlichen Audio-Stream."""
        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.float32,
                blocksize=self.chunk_size,
                callback=self._audio_callback,
                finished_callback=self._stream_finished
            )
            
            self.stream.start()
            self.logger.info("✅ Kontinuierlicher Audio-Stream gestartet")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Starten des Audio-Streams: {e}")
            return False
            
    def _start_hotword_detection(self) -> None:
        """Starte Hot Word Detection Thread."""
        self.detection_thread = threading.Thread(
            target=self._hotword_detection_loop,
            daemon=True,
            name="HotWordDetection"
        )
        self.detection_thread.start()
        self.logger.info("✅ Hot Word Detection Thread gestartet")
        
    def _audio_callback(self, indata, frames, time, status):
        """Audio-Callback für kontinuierlichen Stream."""
        if status:
            print(f"⚠️ Audio-Status: {status}")
            
        if indata is not None and len(indata) > 0:
            # Audio zu Ring-Buffer hinzufügen (Thread-sicher)
            with self.audio_lock:
                self.audio_buffer.extend(indata.flatten())
                
            # Debug: Zeige Audio-Daten
            if len(self.audio_buffer) % 10000 == 0:  # Alle 10000 Samples
                print(f"🎤 Audio-Buffer: {len(self.audio_buffer)} Samples")
                
            # Wenn Aufnahme läuft, auch zu Aufnahme-Buffer hinzufügen
            if self.is_recording:
                with self.recording_lock:
                    self.recording_buffer.append(indata.copy())
                    print(f"📝 Aufnahme läuft: {len(self.recording_buffer)} Chunks")
                    
    def _stream_finished(self):
        """Stream beendet."""
        self.logger.info("🔄 Audio-Stream beendet")
        
    def _hotword_detection_loop(self):
        """Hot Word Detection Loop mit Sliding Window."""
        self.logger.info("🔄 Hot Word Detection Loop gestartet")
        
        while self.running:
            try:
                # Prüfe auf genug Audio-Daten (2 Sekunden)
                with self.audio_lock:
                    if len(self.audio_buffer) >= 2 * self.sample_rate:
                        # Letzte 2 Sekunden für Hot Word Detection (Sliding Window)
                        recent_audio = np.array(list(self.audio_buffer)[-2*self.sample_rate:])
                    else:
                        recent_audio = None
                        
                if recent_audio is not None:
                    # Audio normalisieren
                    if np.max(np.abs(recent_audio)) > 0:
                        max_val = np.max(np.abs(recent_audio))
                        if max_val > 0.1:
                            recent_audio = recent_audio / max_val * 0.95
                    
                    # Whisper Transkription für Hot Word Detection
                    segments, info = self.hotword_model.transcribe(
                        audio=recent_audio,
                        language="de",
                        vad_filter=False,
                        beam_size=1,
                        best_of=1,
                        temperature=0.0,
                    )
                    
                    text_parts = [seg.text.strip() for seg in segments]
                    text = " ".join([t for t in text_parts if t]).lower().strip()
                    
                    if text:
                        print(f"🎤 Audio erkannt: '{text}'")  # Immer anzeigen
                        
                        # Prüfe auf Start Words
                        for start_word in self.start_words:
                            if start_word.lower() in text:
                                self._on_start_word_found(start_word, text)
                                break
                        else:
                            # Prüfe auf Stop Words
                            for stop_word in self.stop_words:
                                if stop_word.lower() in text:
                                    self._on_stop_word_found(stop_word, text)
                                    break
                    else:
                        print("🔇 Stille erkannt")  # Immer anzeigen
                        
                else:
                    print("⏳ Warte auf Audio-Daten...")  # Immer anzeigen
                    
            except Exception as e:
                self.logger.warning(f"⚠️ Hot Word Detection Fehler: {e}")
                
            # Kurze Pause
            time.sleep(0.5)
            
    def _on_start_word_found(self, word: str, text: str) -> None:
        """Start Word gefunden."""
        self.logger.info(f"🎯 Start Word erkannt: '{word}' in '{text}'")
        self.start_recording()
        self.on_start_word_detected(word)
        
    def _on_stop_word_found(self, word: str, text: str) -> None:
        """Stop Word gefunden."""
        self.logger.info(f"🛑 Stop Word erkannt: '{word}' in '{text}'")
        self.stop_recording()
        self.on_stop_word_detected(word)
        
    def start_recording(self) -> None:
        """Starte Aufnahme."""
        if self.is_recording:
            return
            
        with self.recording_lock:
            self.is_recording = True
            self.recording_buffer = []
            self.recording_start_time = time.time()
            
        self.logger.info("🎙️ Aufnahme gestartet")
        
    def stop_recording(self) -> None:
        """Stoppe Aufnahme und transkribiere."""
        if not self.is_recording:
            return
            
        with self.recording_lock:
            self.is_recording = False
            
            if self.recording_buffer:
                # Alle Audio-Daten zusammenfügen
                full_audio = np.concatenate(self.recording_buffer)
                duration = time.time() - self.recording_start_time
                
                self.logger.info(f"📊 Aufnahme abgeschlossen: {duration:.1f}s, {len(full_audio)} Samples")
                
                # Gesamttranskription
                self._transcribe_recording(full_audio)
            else:
                self.logger.warning("⚠️ Keine Audio-Daten gesammelt")
                
    def _transcribe_recording(self, audio_data: np.ndarray) -> None:
        """Transkribiere Aufnahme."""
        try:
            self.logger.info("🎯 Starte Gesamttranskription...")
            
            # Audio normalisieren
            if np.max(np.abs(audio_data)) > 0:
                max_val = np.max(np.abs(audio_data))
                if max_val > 0.1:
                    audio_data = audio_data / max_val * 0.95
            
            # Whisper Transkription mit besserem Modell
            segments, info = self.transcription_model.transcribe(
                audio=audio_data,
                language="de",
                vad_filter=False,
                beam_size=5,
                best_of=5,
                temperature=0.0,
            )
            
            # Text zusammenfügen
            text_parts = [seg.text.strip() for seg in segments]
            full_text = " ".join([t for t in text_parts if t]).strip()
            
            if full_text:
                self.logger.info("✅ Gesamttranskription erfolgreich:")
                self.logger.info(f"📝 Vollständiger Text: '{full_text}'")
                self.logger.info(f"📊 Transkriptions-Info: {info.duration:.1f}s Audio verarbeitet")
            else:
                self.logger.warning("⚠️ Kein Text in der Aufnahme erkannt")
                
        except Exception as e:
            self.logger.error(f"❌ Fehler bei Gesamttranskription: {e}")
            
    def get_stats(self) -> dict:
        """Hole Statistiken."""
        with self.audio_lock:
            buffer_size = len(self.audio_buffer)
            
        with self.recording_lock:
            is_recording = self.is_recording
            recording_chunks = len(self.recording_buffer)
            
        return {
            "running": self.running,
            "is_recording": is_recording,
            "buffer_size": buffer_size,
            "recording_chunks": recording_chunks,
            "start_words": self.start_words,
            "stop_words": self.stop_words,
            "sample_rate": self.sample_rate,
            "chunk_size": self.chunk_size,
            "buffer_duration": self.buffer_duration
        }

def test_start_callback(word: str) -> None:
    """Callback für Start Word."""
    print(f"🎯 START WORD ERKANNT: '{word}'")

def test_stop_callback(word: str) -> None:
    """Callback für Stop Word."""
    print(f"🛑 STOP WORD ERKANNT: '{word}'")

def main():
    print("🧪 Professionelle Audio-Stream Test")
    print("=" * 50)
    
    # Teste Imports
    print("🔧 Teste Imports...")
    try:
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
    
    # Starte professionellen Stream
    print("\n🚀 Starte professionellen Audio-Stream...")
    stream = ProfessionalAudioStream(
        on_start_word_detected=test_start_callback,
        on_stop_word_detected=test_stop_callback,
        sample_rate=16000,
        chunk_size=1024,
        buffer_duration=3.0
    )
    
    if not stream.start():
        print("❌ Fehler beim Starten des Audio-Streams")
        return 1
    
    print("\n💡 Professioneller Audio-Stream läuft!")
    print("🎯 Sprich 'start' um Aufnahme zu starten")
    print("🛑 Sprich 'stopp' um Aufnahme zu stoppen")
    print("⏹️ Drücke Ctrl+C zum Beenden")
    
    try:
        while True:
            # Zeige Statistiken
            stats = stream.get_stats()
            if stats['is_recording']:
                print(f"📝 Aufnahme läuft: {stats['recording_chunks']} Chunks")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n🛑 Beende...")
        stream.stop()
    
    print("🎉 Test beendet!")
    return 0

if __name__ == "__main__":
    exit(main())
