# Requirements-Dokumentation

## Übersicht

Mauscribe verwendet verschiedene Requirements-Dateien für unterschiedliche Plattformen und Zwecke.

## Requirements-Dateien

### `requirements.txt`
**Hauptdependencies für alle Plattformen**
- Enthält alle grundlegenden Pakete
- Funktioniert auf Windows, Linux und macOS
- Wird für lokale Entwicklung und Installation verwendet

### `requirements-windows.txt`
**Windows-spezifische Dependencies**
- Enthält alle Pakete aus `requirements.txt`
- Zusätzlich Windows-spezifische Pakete:
  - `pycaw` - Windows Audio Control
  - `comtypes` - COM-Interface für Windows
  - `pywin32` - Windows API-Zugriff
- Wird in GitHub Actions für Windows-Builds verwendet

### `requirements-linux.txt`
**Linux-spezifische Dependencies**
- Enthält alle Pakete aus `requirements.txt` (außer Windows-spezifische)
- Zusätzlich Linux-spezifische Pakete:
  - `pyaudio` - Linux Audio-Interface
- Wird in GitHub Actions für Linux-Tests verwendet

### `requirements-dev.txt`
**Entwicklungsdependencies**
- Testing-Tools: pytest, pytest-cov, pytest-mock
- Code-Qualität: flake8, black, isort, mypy
- Build-Tools: pyinstaller, build, wheel
- Pre-commit Hooks und Development Utilities

## Verwendung

### Lokale Entwicklung
```bash
# Alle Dependencies installieren
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Oder mit pip-tools
pip install -r requirements.txt -r requirements-dev.txt
```

### Plattformspezifische Installation
```bash
# Windows
pip install -r requirements-windows.txt

# Linux
pip install -r requirements-linux.txt

# macOS (verwendet requirements.txt)
pip install -r requirements.txt
```

### CI/CD Workflows
- **Linux-Tests**: `requirements-linux.txt` + `requirements-dev.txt`
- **Windows-Builds**: `requirements-windows.txt` + `pyinstaller`
- **Feature-Branches**: Plattformspezifische Requirements + Dev-Dependencies

## Paket-Kategorien

### Core Dependencies
- **Audio Processing**: faster-whisper, sounddevice, webrtcvad
- **System Integration**: pynput, pyautogui, pystray
- **AI/ML**: openai, numpy
- **Utilities**: python-dotenv, pyperclip, requests

### Windows-spezifische Dependencies
- **Audio Control**: pycaw (Windows Audio)
- **System API**: pywin32 (Windows API)
- **COM Interface**: comtypes (Windows COM)

### Linux-spezifische Dependencies
- **Audio Interface**: pyaudio (Linux Audio)

### Development Dependencies
- **Testing**: pytest, pytest-cov, pytest-mock
- **Code Quality**: flake8, black, isort, mypy
- **Build**: pyinstaller, build, wheel
- **Development**: pre-commit, ipython

## Kompatibilität

### Python-Versionen
- **Minimum**: Python 3.8
- **Empfohlen**: Python 3.11+
- **CI/CD**: Python 3.11

### Plattformen
- **Windows**: 10/11 (64-bit)
- **Linux**: Ubuntu 20.04+, Debian 11+
- **macOS**: 10.15+ (Catalina)

### Architekturen
- **x86_64**: Vollständig unterstützt
- **ARM64**: Teilweise unterstützt (Linux/macOS)

## Troubleshooting

### Häufige Probleme

1. **pywin32 Installation fehlschlägt**
   - Problem: Windows-spezifisches Paket auf Linux
   - Lösung: Verwende `requirements-linux.txt` auf Linux

2. **pyaudio Installation fehlschlägt**
   - Problem: Linux-spezifisches Paket auf Windows
   - Lösung: Verwende `requirements-windows.txt` auf Windows

3. **Version-Konflikte**
   - Problem: Inkompatible Paket-Versionen
   - Lösung: Verwende die empfohlenen Versionen aus den Requirements-Dateien

### Lösungsansätze

1. **Plattform-Erkennung**
   ```python
   import platform
   if platform.system() == "Windows":
       requirements_file = "requirements-windows.txt"
   else:
       requirements_file = "requirements-linux.txt"
   ```

2. **Conditional Installation**
   ```bash
   if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
       pip install -r requirements-windows.txt
   else
       pip install -r requirements-linux.txt
   fi
   ```

## Wartung

### Regelmäßige Updates
- Überprüfe monatlich auf neue Paket-Versionen
- Teste Kompatibilität mit verschiedenen Python-Versionen
- Aktualisiere CI/CD Workflows bei Änderungen

### Sicherheit
- Überprüfe Pakete auf bekannte Sicherheitslücken
- Verwende nur vertrauenswürdige Paket-Quellen
- Halte Dependencies aktuell

### Performance
- Überwache Build-Zeiten in CI/CD
- Optimiere Paket-Installation mit Caching
- Reduziere unnötige Dependencies
