# Mauscribe - Voice-to-Text Tool

Ein fortschrittliches Sprach-zu-Text-Tool, das Audio-Aufnahmen über Mausklicks steuert und transkribierten Text automatisch in die Zwischenablage kopiert.

## 🚀 Features

- **Einfache Bedienung**: Mausklicks starten/stoppen Audio-Aufnahmen
- **Hochwertige Transkription**: Nutzt OpenAI Whisper für präzise Spracherkennung
- **Automatische Rechtschreibprüfung**: Integrierte Korrektur für bessere Ergebnisse
- **Intelligente Benachrichtigungen**: Windows-Toasts und Fallback-Benachrichtigungen
- **Konfigurierbar**: Umfangreiche Einstellungsmöglichkeiten über TOML-Konfiguration
- **System Tray Integration**: Läuft im Hintergrund ohne störende Fenster
- **Datenbank-Support**: Speichert Aufnahmen und Transkriptionen für Training

## 📋 Systemanforderungen

- **Betriebssystem**: Windows 10/11
- **Python**: 3.8 oder höher
- **RAM**: Mindestens 4GB (8GB empfohlen)
- **Speicherplatz**: 2GB für Anwendung + Modell-Downloads

## 🚀 Release Management

Mauscribe verwendet ein automatisiertes CI/CD-System mit GitHub Actions und benutzerdefinierten Python-Tools für Release-Management.

### Release-Prozess

1. **Version Bump**: `make release-patch` (oder `release-minor`/`release-major`)
2. **Automatischer Build**: GitHub Actions erstellt .exe auf Tag-Push
3. **Automatisches Release**: Release-Manager erstellt GitHub Release mit Changelog

### Verfügbare Make-Targets

```bash
# Release-Management
make release-patch    # Patch-Version (1.0.0 -> 1.0.1)
make release-minor    # Minor-Version (1.0.0 -> 1.1.0)
make release-major    # Major-Version (1.0.0 -> 2.0.0)
make changelog        # Changelog-Vorschau generieren
make upload-release   # Release-Assets hochladen

# Entwicklung
make dev-release      # Development-Release für Tests
```

### CI/CD Pipeline

- **Tests**: Automatische Tests bei jedem Push/PR
- **Linting**: Code-Quality-Checks mit Black, isort, flake8
- **Security**: Bandit und Safety Scans
- **Build**: Automatischer .exe-Build bei Version-Tags
- **Release**: Automatische GitHub Releases mit Changelog

### Release-Tools

- **`tools/version_bump.py`**: Semantic Versioning und Git-Tagging
- **`tools/release_manager.py`**: GitHub Release-Erstellung mit Changelog
- **`tools/release_config.toml`**: Release-Konfiguration
- **Audio**: Mikrofon oder Audio-Eingabegerät

## 🛠️ Installation

### 1. Repository klonen
```bash
git clone https://github.com/R0bes/Mauscribe.git
cd mauscribe
```

### 2. Python-Umgebung einrichten
```bash
# Virtuelle Umgebung erstellen
python -m venv venv

# Umgebung aktivieren (Windows)
venv\Scripts\activate

# Umgebung aktivieren (Linux/Mac)
source venv/bin/activate
```

### 3. Abhängigkeiten installieren
```bash
# Hauptabhängigkeiten
pip install -e .

# Windows-spezifische Abhängigkeiten
pip install -e ".[windows]"

# Entwicklungs-Abhängigkeiten (optional)
pip install -e ".[dev]"
```

### 4. Konfiguration anpassen
Die Standardkonfiguration ist in `settings.toml` gespeichert. Passe sie nach deinen Bedürfnissen an:

```toml
[audio]
sample_rate = 16000
channels = 1
device = 1  # Dein Mikrofon-Index

[transcription]
language = "de"  # oder "en", "auto"
whisper_model = "base"  # tiny, base, small, medium, large
```

### 5. Anwendung starten
```bash
# Mit Makefile (empfohlen)
make run

# Oder direkt
python main.py
```

## 🎯 Verwendung

### Grundlegende Bedienung

1. **Anwendung starten**:
   ```bash
   make run
   # oder
   python main.py
   ```

2. **Audio aufnehmen**:
   - **X2-Button**: Einfacher Klick startet/stoppt Aufnahme (Toggle)

3. **Text einfügen**:
   - **Linke Maustaste gedrückt halten + X2-Button**: Stoppt Aufnahme und fügt Text ein
   - Transkribierter Text wird automatisch in die Zwischenablage kopiert

### System Tray Funktionen

- **Whisper-Modell auswählen**: Verschiedene Modelle für bessere Qualität
- **Hotword Detection**: Ein/Aus-Schalter für Sprachsteuerung
- **Benachrichtigungen**: Ein/Aus-Schalter für System-Benachrichtigungen

## ⚙️ Konfiguration

### Audio-Einstellungen

```toml
[audio]
sample_rate = 16000      # Abtastrate (8000, 16000, 22050, 44100, 48000)
channels = 1             # Kanäle (1 = Mono, 2 = Stereo)
chunk_size = 1024        # Chunk-Größe für Audio-Verarbeitung
format = "wav"           # Audio-Format (wav, mp3, flac)
device = 1               # Audio-Gerät-Index
auto_select_device = true # Automatische Geräteauswahl
```

### Transkriptions-Einstellungen

```toml
[transcription]
language = "de"          # Sprache (de, en, auto)
whisper_model = "medium" # Whisper-Modell (tiny, base, small, medium, large) - medium für bessere deutsche Umlaute
compute_type = "float32" # Berechnungstyp (float32, float16, int8)
```

### System-Einstellungen

```toml
[system]
volume_reduction_factor = 1.0   # Lautstärkereduktion (1.0 = deaktiviert)
min_volume_percent = 10         # Minimale Lautstärke in Prozent

[input.primary]
name = "x2"                     # Primärer Button (X2)
type = "click"                  # Button-Typ

[input.secondary]
name = "left"                   # Sekundärer Button (linke Maustaste)
type = "hold"                   # Button-Typ für Kombination
```

### Benachrichtigungen

```toml
[notifications]
enabled = true          # Benachrichtigungen aktivieren
duration = 5000         # Anzeigedauer in Millisekunden
sound = true            # Sound abspielen
toast = true            # Windows-Toasts verwenden
show_all = true         # Alle Benachrichtigungen anzeigen
```

## 🧪 Tests

### Test-Suite ausführen

```bash
# Alle Tests ausführen
make tests

# Tests mit Coverage
make tests-coverage

# Mit pytest direkt
pytest tests/ -v
```

### Test-Abdeckung

- **Integration Tests**: Testet alle Komponenten zusammen
- **Performance Tests**: Überprüft Geschwindigkeit und Stabilität
- **Error Handling Tests**: Testet alle Fehlerszenarien
- **Unit Tests**: Einzelne Komponenten testen

### Test-Ergebnisse

Die Test-Suite generiert detaillierte Berichte über:
- Test-Erfolgsrate
- Performance-Metriken
- Fehlerbehandlung
- System-Integration

## 🔧 Entwicklung

### Projektstruktur

```
mauscribe/
├── src/                    # Quellcode
│   ├── audio/             # Audio-Verarbeitung
│   ├── input/              # Eingabe-Behandlung
│   ├── lang/               # Sprachverarbeitung
│   ├── ui/                 # Benutzeroberfläche
│   └── utils/              # Hilfsfunktionen
├── tests/                  # Test-Suite
├── config.toml             # Konfiguration
├── requirements.txt         # Abhängigkeiten
└── main.py                 # Hauptanwendung
```

### Neue Features hinzufügen

1. **Komponente implementieren** in `src/`
2. **Tests schreiben** in `tests/`
3. **Konfiguration erweitern** in `settings.toml`
4. **Dokumentation aktualisieren**

### Code-Qualität

```bash
# Alle Checks ausführen
make check

# Auto-Fix für Code-Issues
make fix

# Komplette Validierung (Checks + Tests)
make validate

# Einzelne Tools
black src/ tests/          # Code formatieren
flake8 src/ tests/         # Linting
mypy src/                  # Typ-Checking
pytest --cov=src tests/    # Coverage
```

## 🐛 Fehlerbehebung

### Häufige Probleme

**Audio-Gerät nicht erkannt**:
- Überprüfe `settings.toml` Audio-Einstellungen
- Teste verschiedene `device`-Indizes
- Stelle sicher, dass das Mikrofon aktiv ist

**Transkription funktioniert nicht**:
- Überprüfe Internetverbindung
- Stelle sicher, dass Whisper-Modelle heruntergeladen sind
- Überprüfe `transcription`-Einstellungen

**Clipboard-Fehler**:
- Überprüfe Berechtigungen
- Teste mit `python -c "import pyperclip; print(pyperclip.paste())"`

**Performance-Probleme**:
- Reduziere `whisper_model` auf "tiny" oder "base"
- Erhöhe `chunk_size` in Audio-Einstellungen
- Überprüfe verfügbaren RAM

### Logs

Logs werden in folgenden Dateien gespeichert:
- `mauscribe.log`: Hauptanwendung
- `app.log`: Anwendungs-Logs
- `pipeline_monitor.log`: Pipeline-Überwachung

## 📈 Performance

### Benchmarks

- **Initialisierung**: < 2 Sekunden
- **Audio-Verarbeitung**: 0.1x realtime
- **Memory-Verbrauch**: < 100MB
- **CPU-Nutzung**: < 80% während Verarbeitung

### Optimierungen

- **Whisper-Modell**: Kleinere Modelle für schnellere Verarbeitung
- **Audio-Chunks**: Optimale Chunk-Größe für dein System
- **Compute-Type**: float16 für bessere Performance bei GPU

## 🔒 Sicherheit

- **Lokale Verarbeitung**: Audio wird lokal verarbeitet
- **Keine Cloud-Speicherung**: Alle Daten bleiben auf deinem System
- **Verschlüsselte Kommunikation**: HTTPS für Modell-Downloads
- **Berechtigungen**: Minimale Systemberechtigungen

## 🤝 Beitragen

1. **Fork** das Repository
2. **Feature-Branch** erstellen (`git checkout -b feature/AmazingFeature`)
3. **Änderungen committen** (`git commit -m 'Add AmazingFeature'`)
4. **Branch pushen** (`git push origin feature/AmazingFeature`)
5. **Pull Request** erstellen

### Entwicklungsrichtlinien

- **Code-Stil**: PEP 8 befolgen
- **Tests**: Neue Features müssen getestet werden
- **Dokumentation**: Code und README aktualisieren
- **Commits**: Aussagekräftige Commit-Nachrichten

## 📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe [LICENSE](LICENSE) Datei für Details.

## 🙏 Danksagungen

- **OpenAI Whisper**: Für die Spracherkennung
- **PyAudio**: Für Audio-Verarbeitung
- **PyAutoGUI**: Für System-Integration
- **PySpellChecker**: Für Rechtschreibprüfung

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/R0bes/Mauscribe/issues)
- **Discussions**: [GitHub Discussions](https://github.com/R0bes/Mauscribe/discussions)
- **Wiki**: [Projekt-Wiki](https://github.com/R0bes/Mauscribe/wiki)

---

**Mauscribe** - Macht Spracherkennung einfach und effizient! 🎤✨
