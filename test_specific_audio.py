#!/usr/bin/env python3
"""
Test-Skript für eine spezifische längere Audio-Datei
"""

import os
import sys
from pathlib import Path

import numpy as np

# Füge src zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from src.lang.spell_checker import SpellChecker, check_and_correct_text
    from src.lang.stt import SpeechToText
    from src.utils.config import Config
    from src.utils.logger import get_logger
except ImportError:
    # Fallback für direkte Ausführung
    from lang.spell_checker import SpellChecker, check_and_correct_text
    from lang.stt import SpeechToText
    from src.utils.logger import get_logger
    from utils.config import Config


def test_long_audio():
    """Testet eine spezifische längere Audio-Datei."""
    print("🎵 Teste längere Audio-Datei...")

    # Wähle eine längere Audio-Datei
    audio_file = "data/audio/recording_20250828_035339_609.npy"  # 5.7MB

    if not os.path.exists(audio_file):
        print(f"❌ Audio-Datei nicht gefunden: {audio_file}")
        return False

    try:
        # Lade Audio
        print(f"📁 Lade Audio-Datei: {audio_file}")
        audio = np.load(audio_file)

        print(f"📊 Audio-Details: {audio.size} Samples, Shape: {audio.shape}, Dtype: {audio.dtype}")

        # Konvertiere zu float32 mono
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)

        audio = audio.astype(np.float32)

        # Prüfe Audio-Qualität
        duration = audio.size / 16000
        print(f"⏱️ Audio-Länge: {duration:.2f} Sekunden")

        if duration < 1.0:
            print("⚠️ Audio zu kurz für aussagekräftige Transkription")
            return False

        # Normalisiere Audio
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio)) * 0.95

        # Initialisiere STT
        print("🔧 Initialisiere STT...")
        stt = SpeechToText()

        if stt._model is None:
            print("❌ STT-Modell nicht verfügbar")
            return False

        # Transkribiere Audio
        print("🗣️ Starte Transkription...")
        raw_text = stt.transcribe_raw(audio)

        if raw_text:
            print("✅ Transkription erfolgreich: '{}'".format(raw_text))

            # Rechtschreibprüfung
            print("🔤 Starte Rechtschreibprüfung...")
            corrected_text = check_and_correct_text(raw_text)

            if corrected_text != raw_text:
                print(f"✅ Rechtschreibprüfung: '{raw_text}' -> '{corrected_text}'")
            else:
                print(f"ℹ️ Keine Rechtschreibkorrekturen nötig")

            return True
        else:
            print("⚠️ Keine Transkription erhalten")
            return False

    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False


def main():
    """Hauptfunktion."""
    print("🚀 Starte Test mit längerer Audio-Datei...")
    print("=" * 60)

    try:
        success = test_long_audio()

        print("\n" + "=" * 60)
        if success:
            print("🎉 Test erfolgreich! STT-Pipeline funktioniert mit echten Audio-Daten.")
        else:
            print("⚠️ Test fehlgeschlagen.")

        return 0 if success else 1

    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
