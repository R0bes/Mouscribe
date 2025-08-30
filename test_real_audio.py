#!/usr/bin/env python3
"""
Test-Skript für echte Audio-Daten aus dem Mauscribe-Projekt
Testet die STT-Pipeline mit realen Aufnahmen
"""

import os
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

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
    from utils.config import Config
    from utils.logger import get_logger


def load_audio_file(file_path: str) -> np.ndarray:
    """Lädt eine Audio-Datei und konvertiert sie zu float32 mono."""
    try:
        # Prüfe Dateiendung
        if file_path.endswith(".npy"):
            # NumPy-Array laden
            audio = np.load(file_path)
            sample_rate = 16000  # Standard für Mauscribe
        else:
            # Normale Audio-Datei laden
            audio, sample_rate = sf.read(file_path)

        # Prüfe ob Audio gültig ist
        if audio.size == 0:
            print(f"⚠️ Audio-Datei ist leer: {file_path}")
            return None

        # Konvertiere zu mono falls nötig
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)

        # Konvertiere zu float32
        audio = audio.astype(np.float32)

        # Prüfe ob Audio nach Konvertierung gültig ist
        if np.isnan(audio).any() or np.isinf(audio).any():
            print(f"⚠️ Audio enthält ungültige Werte: {file_path}")
            return None

        # Normalisiere auf [-1, 1] nur wenn Audio nicht leer ist
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio)) * 0.95

        print(f"✅ Audio geladen: {audio.size} Samples, {sample_rate}Hz, Shape: {audio.shape}")
        return audio

    except Exception as e:
        print(f"❌ Fehler beim Laden von {file_path}: {e}")
        return None


def test_real_audio_files():
    """Testet die STT-Pipeline mit echten Audio-Dateien."""
    print("🎵 Teste STT-Pipeline mit echten Audio-Dateien...")

    # Suche nach Audio-Dateien
    audio_dirs = ["audio", "data/audio"]
    audio_files = []

    for audio_dir in audio_dirs:
        if os.path.exists(audio_dir):
            for file in os.listdir(audio_dir):
                if file.endswith((".wav", ".mp3", ".flac", ".npy")):
                    audio_files.append(os.path.join(audio_dir, file))

    if not audio_files:
        print("⚠️ Keine Audio-Dateien gefunden")
        return False

                print("📁 Gefundene Audio-Dateien: {}".format(len(audio_files)))

    # Initialisiere STT und SpellChecker
    stt = SpeechToText()
    spell_checker = SpellChecker()

    if stt._model is None:
        print("❌ STT-Modell nicht verfügbar")
        return False

    # Teste die ersten 3 Audio-Dateien
    test_files = audio_files[:3]

    for i, audio_file in enumerate(test_files, 1):
        print("\n🔍 Teste Audio-Datei {}/{}: {}".format(i, len(test_files), os.path.basename(audio_file)))

        try:
            # Lade Audio
            audio = load_audio_file(audio_file)
            if audio is None:
                continue

            # Prüfe Audio-Länge
            duration = audio.size / 16000  # Bei 16kHz
            if duration < 0.5:
                print(f"⚠️ Audio zu kurz ({duration:.2f}s), überspringe...")
                continue

            # STT-Transkription
            print(f"🗣️ Transkribiere {duration:.2f}s Audio...")
            raw_text = stt.transcribe_raw(audio)

            if raw_text:
                print("✅ Transkription erfolgreich: '{}'".format(raw_text))

                # Rechtschreibprüfung
                corrected_text = check_and_correct_text(raw_text)
                if corrected_text != raw_text:
                    print("✅ Rechtschreibprüfung: '{}' -> '{}'".format(raw_text, corrected_text))
                else:
                    print("ℹ️ Keine Rechtschreibkorrekturen nötig")

            else:
                print("⚠️ Keine Transkription erhalten")

        except Exception as e:
            print(f"❌ Fehler bei Audio-Datei {audio_file}: {e}")
            continue

    return True


def main():
    """Hauptfunktion."""
    print("🚀 Starte Test mit echten Audio-Dateien...")
    print("=" * 60)

    try:
        success = test_real_audio_files()

        print("\n" + "=" * 60)
        if success:
            print("🎉 Test mit echten Audio-Dateien erfolgreich abgeschlossen!")
        else:
            print("⚠️ Test mit echten Audio-Dateien fehlgeschlagen.")

        return 0 if success else 1

    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
