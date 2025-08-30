#!/usr/bin/env python3
"""
Test-Skript für die reparierte Audio-Pipeline
"""

import sys
import time
from pathlib import Path

# Füge src zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    import numpy as np

    from src.audio.recorder import AudioRecorder
    from src.utils.config import Config
    from src.utils.database import AudioDatabase
except ImportError:
    # Fallback für relative Imports
    import numpy as np

    from audio.recorder import AudioRecorder
    from utils.config import Config
    from utils.database import AudioDatabase


def test_audio_pipeline():
    """Teste die reparierte Audio-Pipeline."""
    print("🎯 Teste die reparierte Audio-Pipeline...")

    try:
        # 1. Konfiguration laden
        print("📋 Lade Konfiguration...")
        config = Config()
        print(f"✅ Konfiguration geladen: Sample Rate={config.audio_sample_rate}Hz, Channels={config.audio_channels}")

        # 2. AudioRecorder initialisieren
        print("🎙️  Initialisiere AudioRecorder...")
        recorder = AudioRecorder(config)
        print(f"✅ AudioRecorder initialisiert: Gerät={recorder.get_current_device()}")

        # 3. Verfügbare Geräte anzeigen
        devices = recorder.list_devices()
        print(f"📱 Verfügbare Audio-Geräte: {len(devices)}")
        for device in devices:
            print(f"   - {device['name']} (ID: {device['index']})")

        # 4. AudioDatabase initialisieren
        print("🗄️  Initialisiere AudioDatabase...")
        db = AudioDatabase(config)
        print(f"✅ AudioDatabase initialisiert: {db.db_path}")

        # 5. Test-Audio generieren (Simulation)
        print("🎵 Generiere Test-Audio...")
        sample_rate = config.audio_sample_rate
        duration = 3.0  # 3 Sekunden
        samples = int(sample_rate * duration)

        # Generiere einen Sinuston bei 440Hz (A4)
        t = np.linspace(0, duration, samples, False)
        test_audio = np.sin(2 * np.pi * 440 * t) * 0.1  # 440Hz, 10% Amplitude
        test_audio = test_audio.astype(np.float32)

        print(f"✅ Test-Audio generiert: {len(test_audio)} Samples, {duration}s, {test_audio.dtype}")

        # 6. Test-Audio in Datenbank speichern
        print("💾 Speichere Test-Audio in Datenbank...")
        recording_id = db.save_audio_recording(
            audio_data=test_audio,
            sample_rate=sample_rate,
            channels=config.audio_channels,
            duration=duration,
            audio_format=config.database_audio_format,
        )
        print(f"✅ Test-Audio gespeichert mit ID: {recording_id}")

        # 7. Datenbank-Statistiken anzeigen
        stats = db.get_statistics()
        print(f"📊 Datenbank-Statistiken: {stats}")

        print("\n🎉 Audio-Pipeline-Test erfolgreich abgeschlossen!")
        return True

    except Exception as e:
        print(f"❌ Fehler beim Testen der Audio-Pipeline: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_real_recording():
    """Teste eine echte Audio-Aufnahme."""
    print("\n🎙️  Teste echte Audio-Aufnahme...")

    try:
        # Konfiguration laden
        config = Config()
        recorder = AudioRecorder(config)

        print("🎤 Drücke Enter um mit der Aufnahme zu beginnen...")
        input()

        print("🎙️  Starte Aufnahme... (Drücke Enter um zu stoppen)")
        recorder.start_recording()

        input()

        print("🛑 Stoppe Aufnahme...")
        audio_data = recorder.stop_recording()

        if audio_data is not None and len(audio_data) > 0:
            duration = len(audio_data) / recorder.sample_rate_hz
            print(f"✅ Aufnahme erfolgreich: {len(audio_data)} Samples, {duration:.2f}s")

            # In Datenbank speichern
            db = AudioDatabase(config)
            recording_id = db.save_audio_recording(
                audio_data=audio_data,
                sample_rate=recorder.sample_rate_hz,
                channels=recorder.num_channels,
                duration=duration,
                audio_format=config.database_audio_format,
            )
            print(f"✅ Aufnahme in Datenbank gespeichert mit ID: {recording_id}")

            return True
        else:
            print("❌ Keine Audio-Daten aufgenommen")
            return False

    except Exception as e:
        print(f"❌ Fehler bei der echten Aufnahme: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🎯 Audio-Pipeline Test Suite")
    print("=" * 40)

    # Test 1: Basis-Funktionalität
    success1 = test_audio_pipeline()

    # Test 2: Echte Aufnahme (optional)
    if success1:
        print("\n" + "=" * 40)
        print("Möchtest du eine echte Audio-Aufnahme testen? (j/n)")
        response = input().lower().strip()
        if response in ["j", "ja", "y", "yes"]:
            success2 = test_real_recording()
        else:
            success2 = True
            print("⏭️  Echte Aufnahme übersprungen")
    else:
        success2 = False

    overall_success = success1 and success2
    if overall_success:
        print("\n🎉 Alle Tests erfolgreich abgeschlossen!")
    else:
        print("\n❌ Einige Tests sind fehlgeschlagen!")

    sys.exit(0 if overall_success else 1)
