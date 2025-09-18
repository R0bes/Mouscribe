#!/usr/bin/env python3
"""
Einfacher Hot Word Detection Test - FIXED VERSION
"""

import time
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

def test_start_callback(word: str, text: str) -> None:
    """Callback für Start Word."""
    print(f"🎯 START WORD ERKANNT: '{word}' in '{text}'")

def test_stop_callback(word: str, text: str) -> None:
    """Callback für Stop Word."""
    print(f"🛑 STOP WORD ERKANNT: '{word}' in '{text}'")

def main():
    print("🧪 Einfacher Hot Word Detection Test - FIXED")
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
    
    # Teste Whisper Modell
    print("\n🤖 Teste Whisper Modell...")
    try:
        model = WhisperModel("base", device="cpu", compute_type="int8")
        print("✅ Whisper Modell geladen")
    except Exception as e:
        print(f"❌ Whisper Modell Fehler: {e}")
        return 1
    
    # Teste Audio-Aufnahme
    print("\n🎵 Teste Audio-Aufnahme...")
    try:
        duration = 3  # 3 Sekunden
        sample_rate = 16000
        
        print("📹 Nehme 3s Audio auf...")
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
    
    # Teste Hot Word Detection - EINFACHE VERSION
    print("\n🎯 Teste Hot Word Detection...")
    try:
        # Start Words und Stop Words
        start_words = ["start"]
        stop_words = ["stopp"]
        
        print(f"📊 Start Words: {start_words}")
        print(f"📊 Stop Words: {stop_words}")
        
        # Teste 3 Runden
        for round_num in range(1, 4):
            print(f"\n🔄 Runde {round_num}/3:")
            print("⏰ Countdown:")
            for i in range(3, 0, -1):
                print(f"   {i}...")
                time.sleep(1)
            print("🎤 JETZT SPRECHEN!")
            
            # Audio aufnehmen
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
                    audio_data = audio_data / np.max(np.abs(audio_data)) * 0.95
                
                # Whisper Transkription
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
                    
                    # Prüfe auf Start Words
                    for start_word in start_words:
                        if start_word.lower() in text:
                            test_start_callback(start_word, text)
                            break
                    else:
                        # Prüfe auf Stop Words
                        for stop_word in stop_words:
                            if stop_word.lower() in text:
                                test_stop_callback(stop_word, text)
                                break
                        else:
                            print("⚠️ Kein Wake Word erkannt")
                else:
                    print("⚠️ Kein Text erkannt")
            else:
                print("❌ Keine Audio-Daten erhalten")
            
            time.sleep(1)  # Kurze Pause zwischen Runden
            
    except Exception as e:
        print(f"❌ Hot Word Detection Fehler: {e}")
        return 1
    
    print("\n🎉 Alle Tests erfolgreich!")
    return 0

if __name__ == "__main__":
    exit(main())

