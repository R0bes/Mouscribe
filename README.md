# Mauscribe - Voice-to-Text Tool

Ein professionelles Voice-to-Text Tool mit erweiterten Features und Windows-Installer.

![Mauscribe Icon](icons/mauscribe_icon.svg)

## 🚀 Neue Features v1.1.0

- 🎯 **Erweiterte Input-Konfiguration** - Strg + Linke Maus, Tastatur-Kombinationen, Custom-Inputs
- 🖱️ **Cursor-Feedback** - Mauszeiger verwandelt sich während der Aufnahme in Mikrofon/Maus
- 📦 **Windows Setup.exe** - Einfache Installation für Freunde ohne Python-Kenntnisse
- ⚙️ **Production-Ready** - Professionelle Konfiguration und Fehlerbehandlung
- 🎨 **Custom Cursor-Icons** - Automatisch generierte Cursor-Icons

## Features

- 🎤 **Push-to-Talk** mit fünfter Maustaste (Button.x2) oder Strg + Linke Maus
- 🗣️ **Offline Spracherkennung** mit Whisper
- 📋 **Automatisches Kopieren** in die Zwischenablage (mit Leerzeichen)
- 🔊 **Sprach-Feedback** bei erfolgreicher Transkription
- 🔇 **System-Sound Reduzierung** während Aufnahme (auf 15%)
- 💡 **Doppelklick** zum automatischen Einfügen
- 🖱️ **Cursor-Feedback** - Mauszeiger wird zu Mikrofon/Maus während Aufnahme
- 🚀 **Autostart** beim Windows-Start
- ⚙️ **Umfassende Konfiguration** für alle Einstellungen

## Installation

### Option 1: Windows Setup.exe (Empfohlen für Freunde)

```bash
# Doppelklick auf Mauscribe-Setup.exe oder:
python setup_installer.py
```

**Folgen Sie dem Setup-Assistenten:**
1. **Weiter** → System-Anforderungen prüfen
2. **Installieren** → Automatische Installation
3. **Fertig** → Tool ist bereit!

### Option 2: Portable Version

```bash
# Doppelklick auf dist/Mauscribe-Portable/Mauscribe.exe
# Oder: dist/Mauscribe-Portable/Start-Mauscribe.bat
```

### Option 3: Manuelle Installation

```bash
# Repository klonen
git clone https://github.com/yourusername/mauscribe.git
cd mauscribe

# Virtual Environment erstellen
python -m venv .venv
.\.venv\Scripts\activate  # Windows

# Installieren
pip install -e .

# Starten
mauscribe
```

### Option 4: Direkt ausführen

```bash
# Ohne Installation
python voice_control_simple.py
```

## Konfiguration

Die umfassende Konfiguration erfolgt in `voice_control/config.py`:

### Input-Konfiguration
```python
# Input-Methode: "mouse_button", "keyboard", "custom"
INPUT_METHOD = "mouse_button"

# Push-to-Talk Konfiguration
PUSH_TO_TALK_CONFIG = {
    "mouse_button": {
        "primary": "x2",  # Fünfte Maustaste
        "secondary": "x1",  # Vierte Maustaste
        "left_with_ctrl": True,  # Strg + Linke Maus
    },
    "keyboard": {
        "primary": "f9",  # F9 Taste
        "combinations": [("ctrl", "f9")]  # Strg + F9
    }
}
```

### Cursor-Konfiguration
```python
# Cursor-Typ während Aufnahme: "microphone", "mouse"
CURSOR_TYPE = "microphone"

# Cursor-Feedback aktivieren
ENABLE_CURSOR_FEEDBACK = True
```

### Audio-Konfiguration
```python
SAMPLE_RATE = 16000           # Audio-Sample-Rate
CHANNELS = 1                  # Mono/Stereo
VAD_SENSITIVITY = 1           # Voice Activity Detection
```

### Speech-to-Text Konfiguration
```python
WHISPER_MODEL = "base"        # Modell-Größe (tiny/base/small/medium/large)
LANGUAGE = None               # Sprache (None = automatisch)
COMPUTE_TYPE = "float32"      # Genauigkeit vs. Geschwindigkeit
```

### System Sound Konfiguration
```python
VOLUME_REDUCTION_FACTOR = 0.15  # System-Sound Reduzierung (15%)
MIN_VOLUME_PERCENT = 5          # Minimale Lautstärke (5%)
```

### Clipboard Konfiguration
```python
ADD_SPACE_AFTER_TEXT = True     # Leerzeichen am Ende hinzufügen
DOUBLE_CLICK_THRESHOLD = 0.5    # Doppelklick-Schwelle (0.5s)
AUTO_PASTE_AFTER_TRANSCRIPTION = False  # Automatisches Einfügen
```

## Verwendung

1. **Tool starten** (siehe Installation)
2. **Fünfte Maustaste drücken und halten** (oder Strg + Linke Maus)
3. **Sprechen** (egal was - Prompts, Notizen, etc.)
4. **Maustaste loslassen**
5. **Text ist automatisch in der Zwischenablage** (mit Leerzeichen am Ende)
6. **Doppelklick** zum automatischen Einfügen

### Input-Methoden

- **Maus-Buttons**: Fünfte Maustaste (x2), Vierte Maustaste (x1)
- **Strg + Linke Maus**: Halte Strg und linke Maustaste
- **Tastatur**: F9, F10, oder Strg + F9
- **Custom**: Eigene Kombinationen konfigurierbar

## Technische Details

- **STT**: faster-whisper (offline)
- **Audio**: sounddevice + webrtcvad
- **Input**: pynput für Maus/Keyboard
- **Clipboard**: pyperclip
- **TTS**: pyttsx3 (optional)
- **Cursor**: win32gui für Windows-Cursor-Management
- **Build**: PyInstaller für Windows-Executable

## Troubleshooting

### Windows Audio Issues
- Mikrofon-Berechtigungen prüfen
- Standard-Audio-Gerät setzen
- Antivirus-Software temporär deaktivieren

### Installation Issues
```bash
# Dependencies manuell installieren
pip install faster-whisper numpy sounddevice webrtcvad pynput pycaw comtypes python-dotenv openai pyperclip pyautogui pywin32 pystray pillow
```

### Cursor-Feedback Issues
- Windows-Berechtigungen prüfen
- Antivirus-Software kann Cursor-Änderungen blockieren
- Fallback auf System-Cursor funktioniert immer

### Autostart Issues
- Administrator-Rechte prüfen
- Windows-Startup-Ordner: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`
- Fehler-Logs: `mauscribe_error.log`

## Entwicklung

```bash
# Repository klonen
git clone https://github.com/yourusername/mauscribe.git
cd mauscribe

# Virtual Environment
python -m venv .venv
.\.venv\Scripts\activate

# Dependencies installieren
pip install -r requirements.txt

# Entwicklungsmodus installieren
pip install -e .

# Cursor-Icons erstellen
python create_cursor_icons.py

# Windows-Installer erstellen
python build_installer.py

# Tests ausführen
python voice_control_simple.py
```

## Icons

Mauscribe verfügt über verschiedene Icons in verschiedenen Größen:

- **`icons/mauscribe_icon.svg`** (64x64) - Haupticon
- **`icons/mauscribe_recording.svg`** (64x64) - Aufnahme-Icon mit Animation
- **`icons/mauscribe_small.svg`** (32x32) - Kleines Icon für System Tray
- **`icons/mauscribe_favicon.svg`** (16x16) - Favicon für Webseiten
- **`icons/mauscribe_icon.ico`** - Windows-Icon für Executable
- **`icons/*.cur`** - Cursor-Icons für Aufnahme-Feedback

Siehe `icons/README.md` für weitere Details zur Verwendung.

## Lizenz

MIT License

## Changelog

### v1.1.0
- ✅ Erweiterte Input-Konfiguration (Strg + Linke Maus, Tastatur-Kombinationen)
- ✅ Cursor-Feedback während Aufnahme (Mikrofon/Maus-Cursor)
- ✅ Windows Setup.exe für einfache Installation
- ✅ Production-ready Konfiguration
- ✅ Custom Cursor-Icon Generator
- ✅ Verbesserte Fehlerbehandlung
- ✅ Umfassende Dokumentation

### v1.0.0
- ✅ Push-to-Talk mit fünfter Maustaste
- ✅ Offline Spracherkennung mit Whisper
- ✅ Automatisches Clipboard-Management (mit Leerzeichen)
- ✅ System-Sound Reduzierung (15%)
- ✅ Doppelklick zum Einfügen
- ✅ Saubere Logs ohne Warnungen
- ✅ Installierbares Paket
- ✅ Autostart-Funktionalität
- ✅ Einfacher Setup-Installer
- ✅ Aufgeräumte Projektstruktur
- ✅ Umfassende Konfigurationsdatei
- ✅ Umbenennung zu "Mauscribe"
- ✅ Professionelle Icons in verschiedenen Größen
