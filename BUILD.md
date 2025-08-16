# Mauscribe Build Guide

Dieser Guide erklärt, wie Sie Mauscribe für Windows als ausführbare Datei (.exe) erstellen können.

## Voraussetzungen

- Python 3.9+ installiert
- pip verfügbar
- Windows 10/11 (für Windows Builds)
- Mindestens 4GB freier Speicherplatz

## Schnellstart

### Option 1: PowerShell Script (Empfohlen)

```powershell
# Vollständiger Build mit Tests und Linting
.\build.ps1

# Build ohne Tests
.\build.ps1 -SkipTests

# Build ohne Linting
.\build.ps1 -SkipLint

# Nur Build-Dateien bereinigen
.\build.ps1 -CleanOnly

# Hilfe anzeigen
.\build.ps1 -Help
```

### Option 2: Batch-Datei

```cmd
# Einfacher Build
build.bat
```

### Option 3: Python Script

```bash
# Direkter Python-Build
python build.py
```

### Option 4: Make (falls verfügbar)

```bash
# Tests und Linting
make all

# Nur Build
make build

# Bereinigung
make clean
```

## Automatische CI/CD Pipeline

Das Repository enthält eine GitHub Actions Workflow-Datei (`.github/workflows/ci-cd.yml`), die automatisch:

1. **Tests** auf verschiedenen Python-Versionen und Betriebssystemen ausführt
2. **Code-Qualität** mit Linting-Tools überprüft
3. **Windows Executable** erstellt (nur bei Push auf main)
4. **Sicherheits-Scans** durchführt

## Pre-commit Hooks

Installieren Sie die Pre-commit Hooks für automatische Code-Qualitäts-Checks:

```bash
pip install pre-commit
pre-commit install
```

Die Hooks führen automatisch aus:
- Code-Formatierung (Black, isort)
- Linting (flake8, mypy)
- Sicherheits-Checks (bandit)
- Python-Upgrades (pyupgrade)

## Build-Prozess Details

### 1. Abhängigkeiten prüfen
- Überprüft alle erforderlichen Python-Pakete
- Installiert fehlende Pakete automatisch

### 2. Tests ausführen
- Führt alle Unit-Tests aus
- Stoppt den Build bei fehlgeschlagenen Tests

### 3. Code-Qualität prüfen
- Flake8 für Style-Checks
- Black für Code-Formatierung
- isort für Import-Sortierung
- MyPy für Typ-Checks

### 4. Executable erstellen
- PyInstaller für .exe-Erstellung
- Optimiert für Windows
- Enthält alle erforderlichen Abhängigkeiten

### 5. Executable testen
- Überprüft, ob die .exe-Datei startet
- Zeigt Dateigröße an

## Ausgabe

Nach erfolgreichem Build finden Sie:
- `dist/mauscribe.exe` - Die ausführbare Datei
- `build/` - Temporäre Build-Dateien
- `mauscribe.spec` - PyInstaller-Spezifikation

## Fehlerbehebung

### Häufige Probleme

1. **Python nicht im PATH**
   - Stellen Sie sicher, dass Python in der System-PATH-Variable ist
   - Verwenden Sie den vollständigen Pfad zu Python

2. **Fehlende Abhängigkeiten**
   - Führen Sie `pip install -r requirements.txt` aus
   - Führen Sie `pip install -r requirements-dev.txt` aus

3. **PyInstaller-Fehler**
   - Aktualisieren Sie PyInstaller: `pip install --upgrade pyinstaller`
   - Löschen Sie alte Build-Dateien mit `.\build.ps1 -CleanOnly`

4. **Speicherplatz-Probleme**
   - Mindestens 4GB freier Speicherplatz erforderlich
   - Bereinigen Sie temporäre Dateien

### Debug-Modus

Für detaillierte Ausgaben:

```bash
python build.py --verbose
```

## Konfiguration

### PyInstaller-Optionen

Die Build-Konfiguration kann in `build.py` angepasst werden:

- `--onefile`: Erstellt eine einzelne .exe-Datei
- `--windowed`: Keine Konsolen-Fenster
- `--icon`: Benutzerdefiniertes Icon
- `--hidden-import`: Explizite Imports

### Icon-Anpassung

Platzieren Sie Ihr Icon in:
- `icons/mauscribe_icon.ico` (empfohlen für Windows)
- `icons/mauscribe_icon.svg`
- `icons/mauscribe_small.svg`

## Support

Bei Problemen:
1. Überprüfen Sie die Fehlermeldungen
2. Stellen Sie sicher, dass alle Voraussetzungen erfüllt sind
3. Öffnen Sie ein Issue im GitHub-Repository
4. Überprüfen Sie die CI/CD-Pipeline-Ergebnisse
