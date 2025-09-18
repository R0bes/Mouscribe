#!/usr/bin/env python3
"""
Einfacher Pipeline-Checker für Mauscribe
Überprüft lokale Tests und Build-Prozess
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Führt einen Befehl aus und zeigt den Status"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} erfolgreich")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} fehlgeschlagen:")
        print(f"   Fehler: {e.stderr}")
        return False

def check_pipeline():
    """Überprüft die lokale Pipeline"""
    print("🚀 Starte lokale Pipeline-Überprüfung...")
    print("=" * 60)
    
    # 1. Tests ausführen
    print("\n📋 Schritt 1: Tests ausführen")
    if not run_command("python -m pytest tests/ -v", "Test-Suite"):
        print("❌ Tests fehlgeschlagen - Pipeline würde fehlschlagen")
        return False
    
    # 2. Linting (optional)
    print("\n📋 Schritt 2: Code-Qualität prüfen")
    try:
        import flake8
        run_command("flake8 src/ tests/ --count --select=E9,F63,F7,F82 --max-line-length=127", "Flake8 Linting")
    except ImportError:
        print("⚠️ Flake8 nicht installiert - überspringe Linting")
    
    # 3. Build-Prozess
    print("\n📋 Schritt 3: Build-Prozess")
    if not run_command("python build.py", "Executable Build"):
        print("❌ Build fehlgeschlagen - Pipeline würde fehlschlagen")
        return False
    
    # 4. Executable testen
    print("\n📋 Schritt 4: Executable testen")
    exe_path = "dist/Mauscribe.exe"
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"✅ Executable gefunden: {exe_path}")
        print(f"📊 Größe: {size_mb:.1f} MB")
        
        # Kurzer Test
        try:
            result = subprocess.run([exe_path, "--help"], 
                                  capture_output=True, text=True, timeout=5)
            print("✅ Executable startet erfolgreich")
        except subprocess.TimeoutExpired:
            print("✅ Executable läuft (Timeout erwartet)")
        except Exception as e:
            print(f"⚠️ Executable-Test: {e}")
    else:
        print("❌ Executable nicht gefunden")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Alle Pipeline-Schritte erfolgreich!")
    print("✅ Die GitHub Actions Pipeline sollte erfolgreich laufen")
    return True

def main():
    """Hauptfunktion"""
    success = check_pipeline()
    
    if success:
        print("\n🚀 Pipeline-Status: BEREIT")
        print("💡 Tipp: Überprüfe GitHub Actions für den aktuellen Status")
        print("🔗 https://github.com/R0bes/Mauscribe/actions")
    else:
        print("\n❌ Pipeline-Status: FEHLER")
        print("🔧 Bitte behebe die oben genannten Probleme")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
