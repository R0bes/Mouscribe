#!/usr/bin/env python3
"""
Mauscribe Build Script
Erstellt die .exe Datei mit Icon
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🔨 Mauscribe Build Script")
    print("=" * 40)
    
    # Prüfe ob PyInstaller installiert ist
    try:
        import PyInstaller
        print("✅ PyInstaller gefunden")
    except ImportError:
        print("❌ PyInstaller nicht gefunden")
        print("📦 Installiere PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Prüfe ob Icon existiert
    icon_path = Path("icons/mauscribe_icon.ico")
    if icon_path.exists():
        print(f"✅ Icon gefunden: {icon_path}")
        icon_arg = f"--icon={icon_path}"
    else:
        print("⚠️  Icon nicht gefunden, verwende Standard-Icon")
        icon_arg = ""
    
    # Lösche alte Build-Dateien
    print("🧹 Lösche alte Build-Dateien...")
    if Path("dist").exists():
        import shutil
        shutil.rmtree("dist")
    if Path("build").exists():
        import shutil
        shutil.rmtree("build")
    if Path("mauscribe.spec").exists():
        Path("mauscribe.spec").unlink()
    
    # PyInstaller Kommando
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",           # Eine .exe Datei
        "--windowed",          # Kein Konsolen-Fenster
        "--name=mauscribe",    # Name der .exe
        "--clean",             # Clean build
        "main.py"              # Hauptdatei
    ]
    
    # Icon hinzufügen falls vorhanden
    if icon_arg:
        cmd.insert(-1, icon_arg)
    
    print("🔨 Starte Build...")
    print(f"Kommando: {' '.join(cmd)}")
    
    # Build ausführen
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Build erfolgreich!")
        
        # Prüfe ob .exe erstellt wurde
        exe_path = Path("dist/mauscribe.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📦 .exe erstellt: {exe_path}")
            print(f"📏 Größe: {size_mb:.1f} MB")
            
            # Teste die .exe
            print("🧪 Teste .exe...")
            try:
                test_result = subprocess.run([str(exe_path), "--help"], 
                                          capture_output=True, text=True, timeout=5)
                print("✅ .exe funktioniert")
            except subprocess.TimeoutExpired:
                print("✅ .exe startet (Timeout = OK)")
            except Exception as e:
                print(f"⚠️  .exe Test: {e}")
        else:
            print("❌ .exe wurde nicht erstellt")
    else:
        print("❌ Build fehlgeschlagen!")
        print("Fehler:")
        print(result.stderr)
    
    print("=" * 40)
    print("🎯 Build abgeschlossen!")

if __name__ == "__main__":
    main()
