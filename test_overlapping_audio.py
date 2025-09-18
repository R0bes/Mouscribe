#!/usr/bin/env python3
"""
Test für überlappende Audio-Segmente ohne Lücken
"""

import time
import threading
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

def test_start_callback(word: str, text: str) -> None:
    """Callback für Start Word."""
    print(f"🎯 START WORD ERKANNT: '{word}' in '{text}'")
    return True

def test_stop_callback(word: str, text: str) -> None:
    """Callback für Stop Word."""
    print(f"🛑 STOP WORD ERKANNT: '{word}' in '{text}'")
    return True

class OverlappingAudioPipeline:
    """Audio-Pipeline mit überlappenden Segmenten."""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.hotword_model = None
        self.transcription_model = None
        self.start_words = ["start"]
        self.stop_words = ["stopp"]
        
        # Überlappende Audio-Aufnahme
        self._is_recording = False
        self._recording_start_time = None
        self._recording_buffer = []
        self._sample_rate = 16000
        
    def start(self):
        """Starte überlappende Audio-Pipeline."""
        if self.running:
            print("⚠️ Audio-Pipeline läuft bereits")
            return
            
        print("🚀 Starte überlappende Audio-Pipeline...")
        
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
        self.thread = threading.Thread(target=self._overlapping_loop, daemon=True)
        self.thread.start()
        print("✅ Überlappende Audio-Pipeline läuft")
        
    def stop(self):
        """Stoppe überlappende Audio-Pipeline."""
        if not self.running:
            print("⚠️ Audio-Pipeline läuft nicht")
            return
            
        print("🛑 Stoppe Audio-Pipeline...")
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("✅ Audio-Pipeline gestoppt")
        
    def _overlapping_loop(self):
        """Überlappende Schleife ohne Lücken."""
        segment_duration = 2  # 2 Sekunden
        overlap_duration = 0.5  # 0.5 Sekunden Überlappung
        step_duration = segment_duration - overlap_duration  # 1.5 Sekunden Schritt
        
        print("🔄 Überlappende Audio-Pipeline gestartet")
        
        while self.running:
            try:
                # Audio aufnehmen
                audio_data = sd.rec(
                    int(segment_duration * self._sample_rate),
                    samplerate=self._sample_rate,
                    channels=1,
                    dtype=np.float32,
                    blocking=True
                )
                
                if audio_data is not None and len(audio_data) > 0:
                    # Audio normalisieren
                    audio_data = audio_data.flatten()
                    if np.max(np.abs(audio_data)) > 0:
                        max_val = np.max(np.abs(audio_data))
                        if max_val > 0.1:
                            audio_data = audio_data / max_val * 0.95
                    
                    # Whisper Transkription für Hot Word Detection
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
                        
                        # Prüfe auf Start Words
                        for start_word in self.start_words:
                            if start_word.lower() in text:
                                if test_start_callback(start_word, text):
                                    self._start_recording(audio_data)
                                break
                        else:
                            # Prüfe auf Stop Words
                            for stop_word in self.stop_words:
                                if stop_word.lower() in text:
                                    if test_stop_callback(stop_word, text):
                                        self._stop_recording()
                                    break
                            else:
                                # Normale Audio-Verarbeitung
                                if self._is_recording:
                                    self._add_to_recording(audio_data)
                                    print(f"📝 Aufnahme läuft: {len(self._recording_buffer)} Segmente")
                    else:
                        print("🔇 Stille erkannt")
                        if self._is_recording:
                            self._add_to_recording(audio_data)
                        
                else:
                    print("❌ Keine Audio-Daten erhalten")
                    
            except Exception as e:
                print(f"❌ Pipeline-Fehler: {e}")
                
            # Überlappender Schritt (1.5s statt 2s)
            time.sleep(step_duration)
    
    def _start_recording(self, audio_data):
        """Starte Aufnahme mit vorhandenen Audio-Daten."""
        print("🎙️ Starte Aufnahme mit vorhandenen Audio-Daten...")
        self._is_recording = True
        self._recording_start_time = time.time()
        self._recording_buffer = [audio_data.copy()]
        print(f"✅ Aufnahme gestartet mit {len(audio_data)} Samples")
    
    def _stop_recording(self):
        """Stoppe Aufnahme und transkribiere."""
        if not self._is_recording:
            return
            
        print("🛑 Stoppe Aufnahme...")
        self._is_recording = False
        
        if self._recording_buffer:
            # Alle Audio-Segmente zusammenfügen
            full_audio = np.concatenate(self._recording_buffer)
            duration = time.time() - self._recording_start_time
            
            print(f"📊 Aufnahme abgeschlossen:")
            print(f"   - Dauer: {duration:.1f}s")
            print(f"   - Samples: {len(full_audio)}")
            print(f"   - Segmente: {len(self._recording_buffer)}")
            
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
            
            # Buffer leeren
            self._recording_buffer = []
        else:
            print("⚠️ Keine Audio-Daten gesammelt")
    
    def _add_to_recording(self, audio_data):
        """Füge Audio-Daten zur laufenden Aufnahme hinzu."""
        if self._is_recording:
            self._recording_buffer.append(audio_data.copy())

def main():
    print("🧪 Überlappende Audio-Pipeline Test")
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
    
    # Starte überlappende Pipeline
    print("\n🚀 Starte überlappende Audio-Pipeline...")
    pipeline = OverlappingAudioPipeline()
    pipeline.start()
    
    print("\n💡 Überlappende Audio-Pipeline läuft!")
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

