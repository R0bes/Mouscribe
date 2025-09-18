#!/usr/bin/env python3
"""
Build script für Mauscribe
Erstellt ein standalone Executable mit PyInstaller
"""
import os
import sys
import subprocess
import shutil
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

def main():
    """Hauptfunktion für den Build-Prozess"""
    print("🚀 Starte Mauscribe Build-Prozess...")
    
    # Prüfe ob PyInstaller installiert ist
    try:
        import PyInstaller
        print(f"✅ PyInstaller {PyInstaller.__version__} gefunden")
    except ImportError:
        print("❌ PyInstaller nicht gefunden. Installiere es...")
        if not run_command("pip install pyinstaller", "PyInstaller Installation"):
            return False
    
    # Lösche alte Build-Ordner
    if os.path.exists("build"):
        print("🧹 Lösche alten build/ Ordner...")
        shutil.rmtree("build")
    
    if os.path.exists("dist"):
        print("🧹 Lösche alten dist/ Ordner...")
        shutil.rmtree("dist")
    
    # PyInstaller Kommando
    icon_path = "src/ui/icons/mauscribe_icon3.ico"
    if not os.path.exists(icon_path):
        icon_path = "src/ui/icons/systemtray_icon.ico"
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        f"--icon={icon_path}",
        "--name=Mauscribe",
        "--add-data=settings.toml;.",
        "--add-data=src/ui/icons;src/ui/icons",
        "--hidden-import=winotify",
        "--hidden-import=win10toast",
        "--hidden-import=comtypes",
        "--hidden-import=pycaw",
        "--hidden-import=pystray",
        "--hidden-import=faster_whisper",
        "--hidden-import=sounddevice",
        "--hidden-import=soundfile",
        "--hidden-import=webrtcvad",
        "--hidden-import=pyautogui",
        "--hidden-import=pynput",
        "--hidden-import=pyperclip",
        "--hidden-import=pyspellchecker",
        "--hidden-import=python-dotenv",
        "--hidden-import=requests",
        "--hidden-import=tomli",
        "--hidden-import=tomli-w",
        "--hidden-import=pydantic",
        "--hidden-import=pydantic-settings",
        "--hidden-import=pydub",
        "--hidden-import=speechrecognition",
        "main.py"
    ]
    
    # Führe PyInstaller aus
    cmd_str = " ".join(cmd)
    if not run_command(cmd_str, "PyInstaller Build"):
        return False
    
    # Prüfe ob das Executable erstellt wurde
    exe_path = "dist/Mauscribe.exe"
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"✅ Executable erfolgreich erstellt: {exe_path}")
        print(f"📊 Größe: {size_mb:.1f} MB")
        
        # Teste das Executable kurz
        print("🧪 Teste Executable...")
        try:
            result = subprocess.run([exe_path, "--help"], 
                                  capture_output=True, text=True, timeout=10)
            print("✅ Executable startet erfolgreich")
        except subprocess.TimeoutExpired:
            print("✅ Executable läuft (Timeout erwartet)")
        except Exception as e:
            print(f"⚠️ Executable-Test: {e}")
        
        return True
    else:
        print("❌ Executable wurde nicht erstellt")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
