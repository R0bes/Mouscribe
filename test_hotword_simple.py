#!/usr/bin/env python3
"""
Einfacher Test für Hot Word Detection
Testet nur die Hot Word Detection isoliert
"""

import sys
import time
import numpy as np
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_start_callback(word: str) -> None:
    print(f"🎯 START WORD ERKANNT: '{word}'")

def test_stop_callback(word: str) -> None:
    print(f"🛑 STOP WORD ERKANNT: '{word}'")

def main():
    print("🧪 Einfacher Hot Word Detection Test")
    print("=" * 50)
    
    try:
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
            input_device = sd.query_devices(kind="input")
            print(f"✅ Mikrofon gefunden: {input_device['name']}")
        except Exception as e:
            print(f"❌ Mikrofon-Fehler: {e}")
            return 1
            
        # Teste Whisper Modell
        print("\n🤖 Teste Whisper Modell...")
        try:
            model = WhisperModel(
                model_size_or_path="tiny",
                device="cpu",
                compute_type="float32",
            )
            print("✅ Whisper Modell geladen")
        except Exception as e:
            print(f"❌ Whisper Modell Fehler: {e}")
            return 1
            
        # Teste Audio-Aufnahme
        print("\n🎵 Teste Audio-Aufnahme...")
        try:
            duration = 3
            sample_rate = 16000
            print(f"📹 Nehme {duration}s Audio auf...")
            print("⏰ Countdown:")
            for i in range(3, 0, -1):
                print(f"   {i}...")
                time.sleep(1)
            print("🎤 JETZT SPRECHEN!")
            
            # Audio mit niedrigerer Lautstärke aufnehmen
            audio_data = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype=np.float32,
                device=None,  # Standard-Gerät
                blocking=True  # Warten bis Aufnahme fertig
            )
            
            if audio_data is not None and len(audio_data) > 0:
                print(f"✅ Audio aufgenommen: {len(audio_data)} Samples")
                
                # Audio-Analyse
                max_val = np.max(np.abs(audio_data))
                mean_val = np.mean(np.abs(audio_data))
                print(f"📊 Audio-Analyse: Max={max_val:.3f}, Mean={mean_val:.3f}")
                
                if max_val > 0.9:
                    print("⚠️ WARNUNG: Audio ist sehr laut (kann überlaufen)")
                elif max_val < 0.01:
                    print("⚠️ WARNUNG: Audio ist sehr leise")
                else:
                    print("✅ Audio-Lautstärke OK")
            else:
                print("❌ Keine Audio-Daten erhalten")
                return 1
                
        except Exception as e:
            print(f"❌ Audio-Aufnahme Fehler: {e}")
            return 1
            
        # Teste Whisper Transkription
        print("\n🗣️ Teste Whisper Transkription...")
        try:
            # Audio normalisieren
            audio_data = audio_data.flatten()
            if np.max(np.abs(audio_data)) > 0:
                audio_data = audio_data / np.max(np.abs(audio_data)) * 0.95
            
            segments, info = model.transcribe(
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
                print(f"✅ Text erkannt: '{text}'")
            else:
                print("⚠️ Kein Text erkannt (normal bei Stille)")
                
        except Exception as e:
            print(f"❌ Whisper Transkription Fehler: {e}")
            return 1
            
        # Teste Hot Word Detection
        print("\n🎯 Teste Hot Word Detection...")
        try:
            from src.audio.hotword_detector import HotWordDetector
            
            detector = HotWordDetector(test_start_callback, test_stop_callback)
            stats = detector.get_stats()
            
            print(f"📊 Start Words: {stats['start_words']}")
            print(f"📊 Stop Words: {stats['stop_words']}")
            
            # Teste Start
            if detector.start_listening():
                print("✅ Hot Word Detection gestartet")
                print("\n💡 Sprich 'start' oder 'stopp'...")
                print("⏹️ Drücke Ctrl+C zum Beenden")
                
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n🛑 Test beendet")
                    detector.stop_listening()
            else:
                print("❌ Hot Word Detection konnte nicht gestartet werden")
                return 1
                
        except Exception as e:
            print(f"❌ Hot Word Detection Fehler: {e}")
            return 1
            
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        return 1
        
    print("\n🎉 Alle Tests erfolgreich!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
