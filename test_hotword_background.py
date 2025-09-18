#!/usr/bin/env python3
"""
Hot Word Detection Test - ECHT IM HINTERGRUND
"""

import time
import threading
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

def test_start_callback(word: str, text: str) -> None:
    """Callback für Start Word."""
    print(f"🎯 START WORD ERKANNT: '{word}' in '{text}'")

def test_stop_callback(word: str, text: str) -> None:
    """Callback für Stop Word."""
    print(f"🛑 STOP WORD ERKANNT: '{word}' in '{text}'")

class BackgroundHotWordDetector:
    """Hot Word Detection im Hintergrund."""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.model = None
        self.start_words = ["start"]
        self.stop_words = ["stopp"]
        
    def start(self):
        """Starte Hintergrund-Überwachung."""
        if self.running:
            print("⚠️ Hot Word Detection läuft bereits")
            return
            
        print("🚀 Starte Hot Word Detection im Hintergrund...")
        
        # Whisper Modell laden
        try:
            self.model = WhisperModel("base", device="cpu", compute_type="int8")
            print("✅ Whisper Modell geladen")
        except Exception as e:
            print(f"❌ Whisper Modell Fehler: {e}")
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._background_loop, daemon=True)
        self.thread.start()
        print("✅ Hot Word Detection läuft im Hintergrund")
        
    def stop(self):
        """Stoppe Hintergrund-Überwachung."""
        if not self.running:
            print("⚠️ Hot Word Detection läuft nicht")
            return
            
        print("🛑 Stoppe Hot Word Detection...")
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("✅ Hot Word Detection gestoppt")
        
    def _background_loop(self):
        """Hintergrund-Schleife für kontinuierliche Überwachung."""
        duration = 2  # 2 Sekunden (optimiert für Hot Words)
        sample_rate = 16000
        
        print("🔄 Hintergrund-Überwachung gestartet")
        
        while self.running:
            try:
                # Audio aufnehmen OHNE Countdown
                audio_data = sd.rec(
                    int(duration * sample_rate),
                    samplerate=sample_rate,
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
                    
                    # Whisper Transkription
                    segments, info = self.model.transcribe(
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
                        print(f"🎤 Hintergrund erkannt: '{text}'")
                        
                        # Prüfe auf Start Words
                        for start_word in self.start_words:
                            if start_word.lower() in text:
                                test_start_callback(start_word, text)
                                break
                        else:
                            # Prüfe auf Stop Words
                            for stop_word in self.stop_words:
                                if stop_word.lower() in text:
                                    test_stop_callback(stop_word, text)
                                    break
                    else:
                        print("🔇 Stille erkannt")
                        
                else:
                    print("❌ Keine Audio-Daten erhalten")
                    
            except Exception as e:
                print(f"❌ Hintergrund-Fehler: {e}")
                
            # Optimierte Pause zwischen Aufnahmen
            time.sleep(0.3)  # 0.3s = schneller, aber nicht zu aggressiv

def main():
    print("🧪 Hot Word Detection Test - ECHT IM HINTERGRUND")
    print("=" * 60)
    
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
    
    # Starte Hintergrund-Überwachung
    print("\n🚀 Starte Hintergrund-Überwachung...")
    detector = BackgroundHotWordDetector()
    detector.start()
    
    print("\n💡 Hot Word Detection läuft jetzt im Hintergrund!")
    print("🎯 Sprich 'start' oder 'stopp'...")
    print("⏹️ Drücke Ctrl+C zum Beenden")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Beende...")
        detector.stop()
    
    print("🎉 Test beendet!")
    return 0

if __name__ == "__main__":
    exit(main())
