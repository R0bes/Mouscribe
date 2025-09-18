#!/usr/bin/env python3
"""
Test für kontinuierliche Audio-Aufnahme ohne Lücken
"""

import time
import threading
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from collections import deque

def test_start_callback(word: str, text: str) -> None:
    """Callback für Start Word."""
    print(f"🎯 START WORD ERKANNT: '{word}' in '{text}'")
    return True

def test_stop_callback(word: str, text: str) -> None:
    """Callback für Stop Word."""
    print(f"🛑 STOP WORD ERKANNT: '{word}' in '{text}'")
    return True

class ContinuousAudioPipeline:
    """Kontinuierliche Audio-Pipeline ohne Lücken."""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.hotword_model = None
        self.transcription_model = None
        self.start_words = ["start"]
        self.stop_words = ["stopp"]
        
        # Kontinuierliche Audio-Aufnahme
        self._is_recording = False
        self._recording_start_time = None
        self._recording_buffer = deque(maxlen=1000)  # Ring-Buffer für kontinuierliche Aufnahme
        self._sample_rate = 16000
        
    def start(self):
        """Starte kontinuierliche Audio-Pipeline."""
        if self.running:
            print("⚠️ Audio-Pipeline läuft bereits")
            return
            
        print("🚀 Starte kontinuierliche Audio-Pipeline...")
        
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
        self.thread = threading.Thread(target=self._continuous_loop, daemon=True)
        self.thread.start()
        print("✅ Kontinuierliche Audio-Pipeline läuft")
        
    def stop(self):
        """Stoppe kontinuierliche Audio-Pipeline."""
        if not self.running:
            print("⚠️ Audio-Pipeline läuft nicht")
            return
            
        print("🛑 Stoppe Audio-Pipeline...")
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("✅ Audio-Pipeline gestoppt")
        
    def _continuous_loop(self):
        """Kontinuierliche Schleife ohne Lücken."""
        chunk_duration = 0.5  # 0.5 Sekunden Chunks
        chunk_size = int(chunk_duration * self._sample_rate)
        
        print("🔄 Kontinuierliche Audio-Pipeline gestartet")
        
        # Kontinuierlicher Audio-Stream
        with sd.InputStream(
            samplerate=self._sample_rate,
            channels=1,
            dtype=np.float32,
            blocksize=chunk_size,
            callback=self._audio_callback
        ):
            while self.running:
                time.sleep(0.1)  # Kurze Pause
                
    def _audio_callback(self, indata, frames, time, status):
        """Audio-Callback für kontinuierliche Aufnahme."""
        if status:
            print(f"⚠️ Audio-Status: {status}")
            
        if indata is not None and len(indata) > 0:
            # Audio zu Buffer hinzufügen
            self._recording_buffer.append(indata.copy())
            
            # Hot Word Detection alle 0.5 Sekunden
            if len(self._recording_buffer) >= 4:  # 2 Sekunden Audio
                self._check_hot_words()
                
    def _check_hot_words(self):
        """Prüfe auf Hot Words in den letzten 2 Sekunden."""
        try:
            # Letzte 2 Sekunden Audio für Hot Word Detection
            recent_audio = np.concatenate(list(self._recording_buffer)[-4:])
            
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
                print(f"🎤 Audio erkannt: '{text}'")
                
                # Prüfe auf Start Words
                for start_word in self.start_words:
                    if start_word.lower() in text:
                        if test_start_callback(start_word, text):
                            self._start_recording()
                        break
                else:
                    # Prüfe auf Stop Words
                    for stop_word in self.stop_words:
                        if stop_word.lower() in text:
                            if test_stop_callback(stop_word, text):
                                self._stop_recording()
                            break
            else:
                print("🔇 Stille erkannt")
                
        except Exception as e:
            print(f"❌ Hot Word Check Fehler: {e}")
    
    def _start_recording(self):
        """Starte kontinuierliche Aufnahme."""
        if self._is_recording:
            return
            
        print("🎙️ Starte kontinuierliche Aufnahme...")
        self._is_recording = True
        self._recording_start_time = time.time()
        print("✅ Kontinuierliche Aufnahme gestartet")
    
    def _stop_recording(self):
        """Stoppe Aufnahme und transkribiere."""
        if not self._is_recording:
            return
            
        print("🛑 Stoppe kontinuierliche Aufnahme...")
        self._is_recording = False
        
        # Alle gesammelten Audio-Daten zusammenfügen
        if self._recording_buffer:
            full_audio = np.concatenate(list(self._recording_buffer))
            duration = time.time() - self._recording_start_time
            
            print(f"📊 Aufnahme abgeschlossen:")
            print(f"   - Dauer: {duration:.1f}s")
            print(f"   - Samples: {len(full_audio)}")
            print(f"   - Chunks: {len(self._recording_buffer)}")
            
            # Gesamttranskription
            print("🎯 Starte Gesamttranskription...")
            try:
                # Audio normalisieren
                if np.max(np.abs(full_audio)) > 0:
                    max_val = np.max(np.abs(full_audio))
                    if max_val > 0.1:
                        full_audio = full_audio / max_val * 0.95
                
                # Whisper Transkription mit besserem Modell
                segments, info = self.transcription_model.transcribe(
                    audio=full_audio,
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
                    print("✅ Gesamttranskription erfolgreich:")
                    print(f"📝 Vollständiger Text: '{full_text}'")
                    print(f"📊 Transkriptions-Info: {info.duration:.1f}s Audio verarbeitet")
                else:
                    print("⚠️ Kein Text in der Aufnahme erkannt")
                    
            except Exception as e:
                print(f"❌ Fehler bei Gesamttranskription: {e}")
        else:
            print("⚠️ Keine Audio-Daten gesammelt")

def main():
    print("🧪 Kontinuierliche Audio-Pipeline Test")
    print("=" * 50)
    
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
    
    # Starte kontinuierliche Pipeline
    print("\n🚀 Starte kontinuierliche Audio-Pipeline...")
    pipeline = ContinuousAudioPipeline()
    pipeline.start()
    
    print("\n💡 Kontinuierliche Audio-Pipeline läuft!")
    print("🎯 Sprich 'start' um Aufnahme zu starten")
    print("🛑 Sprich 'stopp' um Aufnahme zu stoppen")
    print("⏹️ Drücke Ctrl+C zum Beenden")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Beende...")
        pipeline.stop()
    
    print("🎉 Test beendet!")
    return 0

if __name__ == "__main__":
    exit(main())

