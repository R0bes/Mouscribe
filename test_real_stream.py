#!/usr/bin/env python3
"""
Test für echten kontinuierlichen Audio-Stream
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

class RealTimeAudioStream:
    """Echter kontinuierlicher Audio-Stream wie bei den Großen."""
    
    def __init__(self):
        self.running = False
        self.stream = None
        self.hotword_model = None
        self.transcription_model = None
        self.start_words = ["start"]
        self.stop_words = ["stopp"]
        
        # Kontinuierlicher Audio-Buffer
        self._audio_buffer = deque(maxlen=1000)  # Ring-Buffer
        self._sample_rate = 16000
        self._chunk_size = 1024  # Kleine Chunks für Echtzeit
        
        # Aufnahme-Status
        self._is_recording = False
        self._recording_start_time = None
        self._recording_buffer = []
        
    def start(self):
        """Starte kontinuierlichen Audio-Stream."""
        if self.running:
            print("⚠️ Audio-Stream läuft bereits")
            return
            
        print("🚀 Starte kontinuierlichen Audio-Stream...")
        
        # Whisper Modelle laden
        try:
            self.hotword_model = WhisperModel("base", device="cpu", compute_type="int8")
            print("✅ Hot Word Modell geladen (base)")
            
            self.transcription_model = WhisperModel("small", device="cpu", compute_type="float32")
            print("✅ Transkriptions-Modell geladen (small)")
            
        except Exception as e:
            print(f"❌ Whisper Modell Fehler: {e}")
            return
            
        # Kontinuierlicher Audio-Stream starten
        try:
            self.stream = sd.InputStream(
                samplerate=self._sample_rate,
                channels=1,
                dtype=np.float32,
                blocksize=self._chunk_size,
                callback=self._audio_callback,
                finished_callback=self._stream_finished
            )
            
            self.stream.start()
            self.running = True
            
            # Hot Word Detection Thread
            self.hotword_thread = threading.Thread(target=self._hotword_detection_loop, daemon=True)
            self.hotword_thread.start()
            
            print("✅ Kontinuierlicher Audio-Stream läuft")
            
        except Exception as e:
            print(f"❌ Audio-Stream Fehler: {e}")
            return
        
    def stop(self):
        """Stoppe kontinuierlichen Audio-Stream."""
        if not self.running:
            print("⚠️ Audio-Stream läuft nicht")
            return
            
        print("🛑 Stoppe Audio-Stream...")
        self.running = False
        
        if self.stream:
            self.stream.stop()
            self.stream.close()
            
        print("✅ Audio-Stream gestoppt")
        
    def _audio_callback(self, indata, frames, time, status):
        """Audio-Callback für kontinuierlichen Stream."""
        if status:
            print(f"⚠️ Audio-Status: {status}")
            
        if indata is not None and len(indata) > 0:
            # Audio zu Ring-Buffer hinzufügen
            self._audio_buffer.extend(indata.flatten())
            
            # Debug: Zeige Audio-Daten
            if len(self._audio_buffer) % 10000 == 0:  # Alle 10000 Samples
                print(f"🎤 Audio-Buffer: {len(self._audio_buffer)} Samples")
            
            # Wenn Aufnahme läuft, auch zu Aufnahme-Buffer hinzufügen
            if self._is_recording:
                self._recording_buffer.append(indata.copy())
                
    def _stream_finished(self):
        """Stream beendet."""
        print("🔄 Audio-Stream beendet")
        
    def _hotword_detection_loop(self):
        """Hot Word Detection Loop."""
        print("🔄 Hot Word Detection gestartet")
        
        while self.running:
            try:
                # Prüfe auf genug Audio-Daten (2 Sekunden)
                if len(self._audio_buffer) >= 2 * self._sample_rate:
                    # Letzte 2 Sekunden für Hot Word Detection
                    recent_audio = np.array(list(self._audio_buffer)[-2*self._sample_rate:])
                    
                    # Audio normalisieren
                    if np.max(np.abs(recent_audio)) > 0:
                        max_val = np.max(np.abs(recent_audio))
                        if max_val > 0.1:
                            recent_audio = recent_audio / max_val * 0.95
                    
                    # Whisper Transkription
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
                        
                else:
                    print("⏳ Warte auf Audio-Daten...")
                    
            except Exception as e:
                print(f"❌ Hot Word Detection Fehler: {e}")
                
            # Kurze Pause
            time.sleep(0.5)
    
    def _start_recording(self):
        """Starte Aufnahme."""
        if self._is_recording:
            return
            
        print("🎙️ Starte Aufnahme...")
        self._is_recording = True
        self._recording_start_time = time.time()
        self._recording_buffer = []
        print("✅ Aufnahme gestartet")
    
    def _stop_recording(self):
        """Stoppe Aufnahme und transkribiere."""
        if not self._is_recording:
            return
            
        print("🛑 Stoppe Aufnahme...")
        self._is_recording = False
        
        if self._recording_buffer:
            # Alle Audio-Daten zusammenfügen
            full_audio = np.concatenate(self._recording_buffer)
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
    print("🧪 Echter kontinuierlicher Audio-Stream Test")
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
    
    # Starte kontinuierlichen Stream
    print("\n🚀 Starte kontinuierlichen Audio-Stream...")
    stream = RealTimeAudioStream()
    stream.start()
    
    print("\n💡 Kontinuierlicher Audio-Stream läuft!")
    print("🎯 Sprich 'start' um Aufnahme zu starten")
    print("🛑 Sprich 'stopp' um Aufnahme zu stoppen")
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
