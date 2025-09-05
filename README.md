# Mauscribe - Voice-to-Text Tool

Ein fortschrittliches Sprach-zu-Text-Tool, das Audio-Aufnahmen über Mausklicks steuert und transkribierten Text in die Zwischenablage kopiert.

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
- **Audio**: Mikrofon oder Audio-Eingabegerät

## 🛠️ Installation

### 1. Repository klonen
```bash
git clone https://github.com/yourusername/mauscribe.git
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
pip install -r requirements.txt

# Test-Abhängigkeiten (optional)
pip install -r requirements-test.txt
```

### 4. Konfiguration anpassen
Die Standardkonfiguration ist in `config.toml` gespeichert. Passe sie nach deinen Bedürfnissen an:

```toml
[audio]
sample_rate = 16000
channels = 1
device = 1  # Dein Mikrofon-Index

[transcription]
language = "de"  # oder "en", "auto"
whisper_model = "base"  # tiny, base, small, medium, large
```

## 🎯 Verwendung

### Grundlegende Bedienung

1. **Anwendung starten**:
   ```bash
   python main.py
   ```

2. **Audio aufnehmen**:
   - **Primärer Button** (X2): Einfacher Klick startet Aufnahme
   - **Sekundärer Button** (X1): Langer Druck (1.5s) für erweiterte Funktionen

3. **Aufnahme beenden**:
   - Erneut auf den primären Button klicken
   - Automatische Beendigung nach 30 Sekunden

4. **Text einfügen**:
   - Transkribierter Text wird automatisch in die Zwischenablage kopiert
   - Text kann manuell mit Strg+V eingefügt werden oder über den sekundären Button

### Erweiterte Funktionen

- **Doppelklick**: Schnelle Wiederholung der letzten Aufnahme
- **Langer Druck**: Öffnet Konfigurationsmenü
- **System Tray**: Rechtsklick für Einstellungen und Status

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
whisper_model = "base"   # Whisper-Modell (tiny, base, small, medium, large)
compute_type = "float32" # Berechnungstyp (float32, float16, int8)
```

### System-Einstellungen

```toml
[system]
volume_reduction_factor = 0.15  # Lautstärkereduktion während Aufnahme
min_volume_percent = 5          # Minimale Lautstärke in Prozent

[behavior]
debounce_time = 0.5             # Entprellzeit für Mausklicks
auto_paste_after_transcription = false  # Automatisches Einfügen nach Transkription
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
python run_all_tests.py

# Spezifischen Test ausführen
python run_all_tests.py tests/test_integration.py

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
3. **Konfiguration erweitern** in `config.toml`
4. **Dokumentation aktualisieren**

### Code-Qualität

```bash
# Code formatieren
black src/ tests/

# Linting
flake8 src/ tests/

# Typ-Checking
mypy src/

# Coverage
pytest --cov=src tests/
```

## 🐛 Fehlerbehebung

### Häufige Probleme

**Audio-Gerät nicht erkannt**:
- Überprüfe `config.toml` Audio-Einstellungen
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

- **Issues**: [GitHub Issues](https://github.com/yourusername/mauscribe/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/mauscribe/discussions)
- **Wiki**: [Projekt-Wiki](https://github.com/yourusername/mauscribe/wiki)

---

**Mauscribe** - Macht Spracherkennung einfach und effizient! 🎤✨
