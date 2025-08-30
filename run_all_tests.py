#!/usr/bin/env python3
"""
Test-Runner für Mauscribe
Führt alle Tests aus und erstellt eine detaillierte Zusammenfassung
"""

import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def run_tests():
    """Führt alle Tests aus."""
    print("🧪 Mauscribe Test-Suite")
    print("=" * 50)
    print(f"Startzeit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Teste ob pytest verfügbar ist
    try:
        import pytest

        print("✅ pytest verfügbar")
    except ImportError:
        print("❌ pytest nicht verfügbar - installiere es mit: pip install pytest")
        return False

    # Teste ob psutil verfügbar ist (für Performance-Tests)
    try:
        import psutil

        print("✅ psutil verfügbar")
    except ImportError:
        print("⚠️  psutil nicht verfügbar - Performance-Tests werden übersprungen")
        print("   Installiere es mit: pip install psutil")

    print()

    # Führe Tests in der richtigen Reihenfolge aus
    test_files = [
        "tests/test_main.py",  # Hauptsystem-Tests
        "tests/test_integration.py",  # Integrations-Tests
        "tests/test_performance.py",  # Performance-Tests
        "tests/test_error_handling.py",  # Fehlerbehandlungs-Tests
        "tests/test_config.py",  # Konfigurations-Tests
        "tests/test_input_filter.py",  # Input-Filter-Tests
        "tests/test_button_mapper.py",  # Button-Mapper-Tests
        "tests/test_simple.py",  # Einfache Tests
    ]

    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    skipped_tests = 0

    for test_file in test_files:
        if not Path(test_file).exists():
            print(f"⚠️  Test-Datei nicht gefunden: {test_file}")
            continue

        print(f"🔍 Führe Tests aus: {test_file}")
        print("-" * 40)

        try:
            # Führe Tests aus
            result = subprocess.run(
                [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short", "--color=yes"],
                capture_output=True,
                text=True,
                timeout=300,
            )

            # Analysiere Ergebnis
            if result.returncode == 0:
                print("✅ Alle Tests bestanden")
                # Zähle Tests
                lines = result.stdout.split("\n")
                for line in lines:
                    if "passed" in line and "failed" in line:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part == "passed":
                                passed = int(parts[i - 1])
                                passed_tests += passed
                            elif part == "failed":
                                failed = int(parts[i - 1])
                                failed_tests += failed
                            elif part == "skipped":
                                skipped = int(parts[i - 1])
                                skipped_tests += skipped
            else:
                print("❌ Einige Tests fehlgeschlagen")
                print("Ausgabe:")
                print(result.stdout)
                if result.stderr:
                    print("Fehler:")
                    print(result.stderr)

        except subprocess.TimeoutExpired:
            print("⏰ Tests überschritten Zeitlimit (5 Minuten)")
        except Exception as e:
            print(f"❌ Fehler beim Ausführen der Tests: {e}")

        print()

    # Zusammenfassung
    total_tests = passed_tests + failed_tests + skipped_tests

    print("📊 Test-Zusammenfassung")
    print("=" * 50)
    print(f"Gesamtanzahl Tests: {total_tests}")
    print(f"Bestanden:          {passed_tests} ✅")
    print(f"Fehlgeschlagen:     {failed_tests} ❌")
    print(f"Übersprungen:       {skipped_tests} ⏭️")

    if total_tests > 0:
        success_rate = (passed_tests / total_tests) * 100
        print(f"Erfolgsrate:        {success_rate:.1f}%")

        if success_rate >= 90:
            print("🎉 Ausgezeichnete Testabdeckung!")
        elif success_rate >= 80:
            print("👍 Gute Testabdeckung")
        elif success_rate >= 70:
            print("⚠️  Mittelmäßige Testabdeckung - Verbesserung empfohlen")
        else:
            print("❌ Schlechte Testabdeckung - dringende Verbesserung erforderlich")

    print()

    # System-Status
    print("🔧 System-Status")
    print("=" * 50)

    # Teste wichtige Komponenten
    components = [
        ("Konfiguration", "src/utils/config.py"),
        ("Hauptanwendung", "src/mouscribe.py"),
        ("Audio-Recorder", "src/audio/recorder.py"),
        ("STT-Engine", "src/lang/stt.py"),
        ("Spell Checker", "src/lang/spell_checker.py"),
        ("Input Handler", "src/input/input_handler.py"),
        ("Notifications", "src/ui/notifications.py"),
        ("System Tray", "src/ui/system_tray.py"),
        ("Datenbank", "src/utils/database.py"),
        ("Logger", "src/utils/logger.py"),
    ]

    for name, path in components:
        if Path(path).exists():
            print(f"✅ {name}: {path}")
        else:
            print(f"❌ {name}: {path} - FEHLT!")

    print()

    # Abhängigkeiten testen
    print("📦 Abhängigkeiten")
    print("=" * 50)

    dependencies = [
        "numpy",
        "pyautogui",
        "pyperclip",
        "sounddevice",
        "soundfile",
        "faster-whisper",
        "pyspellchecker",
        "pystray",
        "pywin32",
        "tomli-w",
    ]

    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - FEHLT!")

    print()

    # Empfehlungen
    if failed_tests > 0:
        print("💡 Empfehlungen")
        print("=" * 50)
        print("• Überprüfe fehlgeschlagene Tests und behebe die Probleme")
        print("• Stelle sicher, dass alle Abhängigkeiten installiert sind")
        print("• Überprüfe die Konfigurationsdatei config.toml")
        print("• Teste das System manuell mit verschiedenen Szenarien")

    print()
    print(f"Endzeit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return failed_tests == 0


def run_specific_test(test_name):
    """Führt einen spezifischen Test aus."""
    print(f"🔍 Führe spezifischen Test aus: {test_name}")
    print("-" * 40)

    try:
        result = subprocess.run([sys.executable, "-m", "pytest", test_name, "-v", "--tb=long", "--color=yes"], timeout=300)

        if result.returncode == 0:
            print("✅ Test erfolgreich")
            return True
        else:
            print("❌ Test fehlgeschlagen")
            return False

    except subprocess.TimeoutExpired:
        print("⏰ Test überschritten Zeitlimit")
        return False
    except Exception as e:
        print(f"❌ Fehler beim Ausführen des Tests: {e}")
        return False


def main():
    """Hauptfunktion."""
    if len(sys.argv) > 1:
        # Spezifischen Test ausführen
        test_name = sys.argv[1]
        success = run_specific_test(test_name)
        sys.exit(0 if success else 1)
    else:
        # Alle Tests ausführen
        success = run_tests()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
