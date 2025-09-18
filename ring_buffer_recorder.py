#!/usr/bin/env python3
"""
Professioneller Ring Buffer Recorder
- Verwendet sounddevice.InputStream für kontinuierlichen Audio-Stream
- collections.deque als effizienter Ring Buffer
- Thread-sichere Operationen
- Minimale Memory-Nutzung durch automatisches Überschreiben
"""

import time
import threading
import numpy as np
import sounddevice as sd
from collections import deque
from typing import Optional, Callable, List, Tuple
import logging

# Logging Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RingBufferRecorder:
    """
    Professioneller Ring Buffer Recorder für kontinuierliche Audio-Aufnahme.
    
    Features:
    - Kontinuierlicher Audio-Stream ohne Unterbrechungen
    - Thread-sicherer Ring Buffer mit automatischem Überschreiben
    - Minimale Memory-Nutzung
    - Einfache API für Audio-Zugriff
    """
    
    def __init__(self, 
                 sample_rate: int = 16000,
                 channels: int = 1,
                 buffer_duration: float = 10.0,  # 10 Sekunden Ring Buffer
                 chunk_size: int = 1024):  # Chunk Größe für Audio-Stream
        """
        Initialisiere Ring Buffer Recorder.
        
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
        
        # Statistiken
        self.total_samples_recorded = 0
        self.start_time = 0.0
        
        logger.info(f"🎯 Ring Buffer Recorder initialisiert:")
        logger.info(f"   - Sample Rate: {sample_rate} Hz")
        logger.info(f"   - Channels: {channels}")
        logger.info(f"   - Buffer Duration: {buffer_duration}s")
        logger.info(f"   - Buffer Samples: {self.buffer_samples}")
        logger.info(f"   - Chunk Size: {chunk_size}")
    
    def start(self) -> bool:
        """
        Starte kontinuierliche Audio-Aufnahme.
        
        Returns:
            True wenn erfolgreich gestartet, False bei Fehler
        """
        if self.is_recording:
            logger.warning("⚠️ Recording läuft bereits")
            return True
        
        try:
            logger.info("🚀 Starte Ring Buffer Recording...")
            
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
            self.total_samples_recorded = 0
            
            logger.info("✅ Ring Buffer Recording gestartet")
            return True
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Starten: {e}")
            return False
    
    def stop(self):
        """Stoppe Audio-Aufnahme."""
        if not self.is_recording:
            return
        
        logger.info("🛑 Stoppe Ring Buffer Recording...")
        
        try:
            if self.audio_stream:
                self.audio_stream.stop()
                self.audio_stream.close()
                self.audio_stream = None
            
            self.is_recording = False
            
            duration = time.time() - self.start_time
            logger.info(f"✅ Recording gestoppt nach {duration:.1f}s")
            logger.info(f"📊 Total Samples: {self.total_samples_recorded}")
            
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
                
                # Debug: Zeige Ring Buffer Status
                if self.total_samples_recorded % (self.sample_rate * 2) == 0:  # Alle 2 Sekunden
                    logger.info(f"📊 Ring Buffer: {len(self.ring_buffer)}/{self.buffer_samples} Samples")
        
        except Exception as e:
            logger.error(f"❌ Audio Callback Fehler: {e}")
    
    def _stream_finished(self):
        """Callback wenn Audio Stream beendet wird."""
        logger.info("🔚 Audio Stream beendet")
        self.is_recording = False
    
    def get_audio_segment(self, duration: float, offset: float = 0.0) -> Optional[np.ndarray]:
        """
        Hole Audio-Segment aus Ring Buffer.
        
        Args:
            duration: Dauer des Segments in Sekunden
            offset: Offset vom Ende des Buffers in Sekunden
            
        Returns:
            Audio-Segment als numpy array oder None bei Fehler
        """
        try:
            with self.buffer_lock:
                if not self.ring_buffer:
                    logger.warning("⚠️ Ring Buffer ist leer")
                    return None
                
                # Segment-Größe berechnen
                segment_samples = int(duration * self.sample_rate)
                offset_samples = int(offset * self.sample_rate)
                
                # Prüfe ob genug Daten vorhanden
                available_samples = len(self.ring_buffer)
                if available_samples < segment_samples + offset_samples:
                    logger.warning(f"⚠️ Nicht genug Audio-Daten: {available_samples}/{segment_samples + offset_samples}")
                    return None
                
                # Segment extrahieren (vom Ende des Buffers)
                start_idx = available_samples - segment_samples - offset_samples
                end_idx = available_samples - offset_samples
                
                # Konvertiere deque zu numpy array
                audio_data = np.array(list(self.ring_buffer)[start_idx:end_idx])
                
                logger.debug(f"📊 Segment extrahiert: {len(audio_data)} Samples ({duration}s)")
                return audio_data
                
        except Exception as e:
            logger.error(f"❌ Fehler beim Extrahieren: {e}")
            return None
    
    def get_latest_audio(self, duration: float) -> Optional[np.ndarray]:
        """
        Hole die neuesten Audio-Daten aus dem Ring Buffer.
        
        Args:
            duration: Dauer in Sekunden
            
        Returns:
            Neueste Audio-Daten oder None
        """
        return self.get_audio_segment(duration, offset=0.0)
    
    def get_buffer_status(self) -> dict:
        """
        Hole Ring Buffer Status-Informationen.
        
        Returns:
            Dictionary mit Status-Informationen
        """
        with self.buffer_lock:
            return {
                'is_recording': self.is_recording,
                'buffer_samples': len(self.ring_buffer),
                'max_buffer_samples': self.buffer_samples,
                'buffer_fill_percent': (len(self.ring_buffer) / self.buffer_samples) * 100,
                'total_samples_recorded': self.total_samples_recorded,
                'recording_duration': time.time() - self.start_time if self.is_recording else 0.0
            }
    
    def clear_buffer(self):
        """Leere den Ring Buffer."""
        with self.buffer_lock:
            self.ring_buffer.clear()
            logger.info("🧹 Ring Buffer geleert")

def test_ring_buffer_recorder():
    """Teste Ring Buffer Recorder."""
    print("🧪 Ring Buffer Recorder Test")
    print("=" * 50)
    
    # Teste Mikrofon
    print("\n🎤 Teste Mikrofon...")
    try:
        default_input_device = sd.query_devices(kind='input')
        print(f"✅ Mikrofon gefunden: {default_input_device['name']}")
    except Exception as e:
        print(f"❌ Mikrofon Fehler: {e}")
        return 1
    
    # Erstelle Recorder
    print("\n🎯 Erstelle Ring Buffer Recorder...")
    recorder = RingBufferRecorder(
        sample_rate=16000,
        channels=1,
        buffer_duration=5.0,  # 5 Sekunden Buffer
        chunk_size=1024
    )
    
    # Starte Recording
    print("\n🚀 Starte Recording...")
    if not recorder.start():
        print("❌ Fehler beim Starten")
        return 1
    
    print("✅ Recording läuft!")
    print("💡 Teste verschiedene Audio-Segmente...")
    print("⏹️ Drücke Ctrl+C zum Beenden")
    
    try:
        test_count = 0
        while True:
            time.sleep(2)
            test_count += 1
            
            # Teste verschiedene Segmente
            if test_count == 1:
                # Neueste 1 Sekunde
                audio = recorder.get_latest_audio(1.0)
                if audio is not None:
                    print(f"✅ 1s Segment: {len(audio)} Samples")
                else:
                    print("⚠️ 1s Segment: Nicht verfügbar")
            
            elif test_count == 2:
                # Neueste 2 Sekunden
                audio = recorder.get_latest_audio(2.0)
                if audio is not None:
                    print(f"✅ 2s Segment: {len(audio)} Samples")
                else:
                    print("⚠️ 2s Segment: Nicht verfügbar")
            
            elif test_count == 3:
                # 1 Sekunde mit 0.5s Offset
                audio = recorder.get_audio_segment(1.0, offset=0.5)
                if audio is not None:
                    print(f"✅ 1s Segment (0.5s Offset): {len(audio)} Samples")
                else:
                    print("⚠️ 1s Segment (0.5s Offset): Nicht verfügbar")
            
            elif test_count == 4:
                # Buffer Status
                status = recorder.get_buffer_status()
                print(f"📊 Buffer Status: {status['buffer_fill_percent']:.1f}% gefüllt")
                print(f"📊 Total Samples: {status['total_samples_recorded']}")
                print(f"📊 Recording Duration: {status['recording_duration']:.1f}s")
                
                # Reset für weitere Tests
                test_count = 0
            
    except KeyboardInterrupt:
        print("\n🛑 Beende...")
    finally:
        recorder.stop()
        print("🎉 Test beendet!")

if __name__ == "__main__":
    test_ring_buffer_recorder()
