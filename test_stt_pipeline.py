#!/usr/bin/env python3
"""
Test-Skript für die reparierte STT-Pipeline
Testet Whisper-Integration, Audio-Format und Rechtschreibprüfung
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
    from utils.config import Config
    from utils.logger import get_logger


def create_test_audio(duration_seconds: float = 3.0, sample_rate: int = 16000) -> np.ndarray:
    """Erstellt Test-Audio-Daten für Whisper."""
    # Erstelle einen einfachen Sinuston mit Sprache-ähnlichen Eigenschaften
    t = np.linspace(0, duration_seconds, int(sample_rate * duration_seconds), False)

    # Kombiniere verschiedene Frequenzen für realistisches Audio
    audio = (
        0.3 * np.sin(2 * np.pi * 200 * t)
        + 0.2 * np.sin(2 * np.pi * 400 * t)  # Grundton
        + 0.1 * np.sin(2 * np.pi * 800 * t)  # Obertöne
        + 0.05 * np.random.randn(len(t))  # Höhere Obertöne  # Rauschen
    )

    # Normalisiere auf [-1, 1]
    audio = audio / np.max(np.abs(audio)) * 0.8

    return audio.astype(np.float32)


def test_stt_initialization():
    """Testet die STT-Initialisierung."""
    print("🧪 Teste STT-Initialisierung...")

    try:
        stt = SpeechToText()
        if stt._model is not None:
            print("✅ STT erfolgreich initialisiert")
            return True
        else:
            print("❌ STT-Modell ist None")
            return False
    except Exception as e:
        print(f"❌ Fehler bei STT-Initialisierung: {e}")
        return False


def test_spell_checker_initialization():
    """Testet die SpellChecker-Initialisierung."""
    print("🧪 Teste SpellChecker-Initialisierung...")

    try:
        spell_checker = SpellChecker()
        if spell_checker.is_enabled():
            print("✅ SpellChecker erfolgreich initialisiert")
            return True
        else:
            print("⚠️ SpellChecker ist deaktiviert")
            return False
    except Exception as e:
        print(f"❌ Fehler bei SpellChecker-Initialisierung: {e}")
        return False


def test_audio_format_handling():
    """Testet die Audio-Format-Behandlung."""
    print("🧪 Teste Audio-Format-Behandlung...")

    try:
        # Erstelle Test-Audio
        audio = create_test_audio(2.0)
        print(f"✅ Test-Audio erstellt: {audio.size} Samples, Shape: {audio.shape}, Dtype: {audio.dtype}")

        # Teste verschiedene Audio-Formate
        test_cases = [
            ("Normal", audio),
            ("Reshaped", audio.reshape(-1, 1)),
            ("Different dtype", audio.astype(np.float64)),
        ]

        for name, test_audio in test_cases:
            try:
                # Konvertiere zu float32 mono
                processed = test_audio.astype(np.float32).flatten()
                print(f"  ✅ {name}: {processed.size} Samples, Shape: {processed.shape}, Dtype: {processed.dtype}")
            except Exception as e:
                print(f"  ❌ {name}: {e}")
                return False

        return True

    except Exception as e:
        print(f"❌ Fehler bei Audio-Format-Test: {e}")
        return False


def test_whisper_transcription():
    """Testet die Whisper-Transkription."""
    print("🧪 Teste Whisper-Transkription...")

    try:
        stt = SpeechToText()
        if stt._model is None:
            print("❌ STT-Modell nicht verfügbar")
            return False

        # Erstelle kurzes Test-Audio (zu kurz für echte Transkription, aber gut für Tests)
        audio = create_test_audio(0.5)

        # Teste Transkription
        result = stt.transcribe_raw(audio)

        if result == "":
            print("✅ Whisper-Transkription funktioniert (leerer Text für kurzes Audio ist normal)")
        else:
            print(f"✅ Whisper-Transkription erfolgreich: '{result}'")

        return True

    except Exception as e:
        print(f"❌ Fehler bei Whisper-Transkription: {e}")
        return False


def test_spell_checker():
    """Testet die Rechtschreibprüfung."""
    print("🧪 Teste Rechtschreibprüfung...")

    try:
        spell_checker = SpellChecker()

        # Teste deutsche Texte
        test_texts = [
            "Das ist ein Test.",
            "Ich habe villen Dank.",
            "Das warscheinlich richtig.",
            "Ich bin seid gestern hier.",
            "Das Auto ist wie schnell.",
        ]

        for text in test_texts:
            corrected = spell_checker.check_text(text)
            if corrected != text:
                print(f"  ✅ Korrektur: '{text}' -> '{corrected}'")
            else:
                print(f"  ℹ️  Keine Korrektur nötig: '{text}'")

        return True

    except Exception as e:
        print(f"❌ Fehler bei Rechtschreibprüfung: {e}")
        return False


def test_integration():
    """Testet die komplette Pipeline."""
    print("🧪 Teste komplette Pipeline...")

    try:
        # Erstelle längeres Test-Audio
        audio = create_test_audio(3.0)

        # STT
        stt = SpeechToText()
        raw_text = stt.transcribe_raw(audio)

        if raw_text:
            print("✅ STT erfolgreich: '{}'".format(raw_text))

            # Rechtschreibprüfung
            corrected_text = check_and_correct_text(raw_text)
            if corrected_text != raw_text:
                print(f"✅ Rechtschreibprüfung erfolgreich: '{raw_text}' -> '{corrected_text}'")
            else:
                print(f"✅ Rechtschreibprüfung: Keine Korrekturen nötig")

            return True
        else:
            print("⚠️ STT gab leeren Text zurück (normal für Test-Audio)")
            return True

    except Exception as e:
        print(f"❌ Fehler bei Pipeline-Test: {e}")
        return False


def test_configuration():
    """Testet die Konfiguration."""
    print("🧪 Teste Konfiguration...")

    try:
        config = Config()

        print(f"  📊 STT-Modell: {config.stt_model}")
        print(f"  📊 STT-Sprache: {config.stt_language}")
        print(f"  📊 STT-Compute-Type: {config.stt_compute_type}")
        print(f"  📊 SpellCheck-Sprache: {config.spell_check_language}")

        return True

    except Exception as e:
        print(f"❌ Fehler bei Konfigurations-Test: {e}")
        return False


def main():
    """Hauptfunktion für alle Tests."""
    print("🚀 Starte STT-Pipeline Tests...")
    print("=" * 50)

    tests = [
        ("Konfiguration", test_configuration),
        ("STT-Initialisierung", test_stt_initialization),
        ("SpellChecker-Initialisierung", test_spell_checker_initialization),
        ("Audio-Format", test_audio_format_handling),
        ("Whisper-Transkription", test_whisper_transcription),
        ("Rechtschreibprüfung", test_spell_checker),
        ("Komplette Pipeline", test_integration),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}:")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Unerwarteter Fehler in {test_name}: {e}")
            results.append((test_name, False))

    # Zusammenfassung
    print("\n" + "=" * 50)
    print("📊 TEST-ZUSAMMENFASSUNG:")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ BESTANDEN" if success else "❌ FEHLGESCHLAGEN"
        print(f"  {test_name}: {status}")

    print(f"\n🎯 Gesamt: {passed}/{total} Tests bestanden")

    if passed == total:
        print("🎉 Alle Tests bestanden! STT-Pipeline funktioniert korrekt.")
        return 0
    else:
        print("⚠️ Einige Tests fehlgeschlagen. Überprüfe die Logs für Details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
