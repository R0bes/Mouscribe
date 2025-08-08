@echo off
echo ========================================
echo Mauscribe Installation
echo ========================================

REM Prüfe ob Python installiert ist
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python ist nicht installiert!
    echo Bitte installiere Python von https://python.org
    pause
    exit /b 1
)

echo ✅ Python gefunden

REM Erstelle virtuelles Environment
echo.
echo 🔧 Erstelle virtuelles Environment...
python -m venv .venv

REM Aktiviere virtuelles Environment
echo.
echo 🔧 Aktiviere virtuelles Environment...
call .venv\Scripts\activate.bat

REM Installiere Dependencies
echo.
echo 📦 Installiere Dependencies...
pip install -r requirements.txt

echo.
echo ✅ Installation abgeschlossen!
echo.
echo 🚀 Starte Mauscribe mit: python main.py
echo.
pause
