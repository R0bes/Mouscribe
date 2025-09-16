# Hot Word Detection - Dokumentation

## 🎯 Übersicht

Die Hot Word Detection ermöglicht es, Mauscribe durch Sprachbefehle zu aktivieren, ohne dass Mausklicks erforderlich sind. Das System erkennt vordefinierte Wake Words und startet automatisch die Audioaufnahme.

## ⚙️ Konfiguration

### settings.toml Einstellungen

```toml
[hotword]
enabled = false                    # Hot Word Detection aktivieren/deaktivieren
wake_words = [                    # Liste der Wake Words
    "hey mauscribe",
    "mauscribe", 
    "hey mouse"
]
sensitivity = 0.5                 # Erkennungssensitivität (0.0 - 1.0)
timeout_seconds = 30               # Timeout für kontinuierliche Überwachung
continuous_listening = true        # Kontinuierliche Überwachung aktivieren
auto_start_recording = true        # Automatisch Aufnahme nach Wake Word starten
fallback_to_click = true           # Fallback auf Mausklick-Modus bei Fehlern
```

### Konfigurationsoptionen

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `enabled` | bool | false | Aktiviert/deaktiviert Hot Word Detection |
| `wake_words` | list | ["hey mauscribe", "mauscribe", "hey mouse"] | Liste der zu erkennenden Wake Words |
| `sensitivity` | float | 0.5 | Erkennungssensitivität (0.0 = sehr empfindlich, 1.0 = weniger empfindlich) |
| `timeout_seconds` | int | 30 | Timeout in Sekunden für kontinuierliche Überwachung |
| `continuous_listening` | bool | true | Aktiviert kontinuierliche Audio-Überwachung |
| `auto_start_recording` | bool | true | Startet automatisch Aufnahme nach Wake Word |
| `fallback_to_click` | bool | true | Fallback auf Mausklick-Modus bei Fehlern |

## 🚀 Verwendung

### Aktivierung über System Tray

1. **Rechtsklick** auf das Mauscribe-System Tray Icon
2. **"🎯 Hot Word Detection"** auswählen
3. Status wird über Benachrichtigung angezeigt

### Aktivierung über Konfiguration

1. Öffne `settings.toml`
2. Setze `enabled = true` im `[hotword]` Bereich
3. Starte Mauscribe neu

### Wake Words verwenden

1. Stelle sicher, dass Hot Word Detection aktiviert ist
2. Sprich eines der konfigurierten Wake Words:
   - "Hey Mauscribe"
   - "Mauscribe"
   - "Hey Mouse"
3. Die Aufnahme startet automatisch
4. Sprich deinen Text
5. Verwende den Sekundär-Button (X1) zum Einfügen

## 🔧 Technische Details

### Architektur

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Microphone    │───▶│ HotWordDetector  │───▶│   Callback      │
│   (speech_rec)  │    │   (Threading)    │    │ (Start Recording)│
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Komponenten

1. **HotWordDetector**: Hauptklasse für Wake Word Erkennung
2. **Speech Recognition**: Google Speech-to-Text API
3. **Threading**: Kontinuierliche Audio-Überwachung
4. **Callback System**: Integration mit MauscribeApp

### Abhängigkeiten

- `speechrecognition>=3.10.0`: Speech-to-Text Engine
- `pyaudio`: Audio-Interface (automatisch installiert)
- `google-api-python-client`: Google Speech API (optional)

## 🧪 Testing

### Test-Skript ausführen

```bash
python test_hotword.py
```

Das Test-Skript:
- Initialisiert Hot Word Detection isoliert
- Zeigt aktuelle Konfiguration
- Startet kontinuierliche Überwachung
- Zeigt erkannte Wake Words an
- Beendet sich mit Ctrl+C

### Manuelle Tests

1. **Wake Word Erkennung testen**:
   ```bash
   python test_hotword.py
   # Sprich: "Hey Mauscribe"
   ```

2. **Integration testen**:
   ```bash
   python main.py
   # Aktiviere Hot Word Detection über System Tray
   # Sprich: "Mauscribe"
   ```

## 🐛 Troubleshooting

### Häufige Probleme

#### 1. Mikrofon nicht erkannt
```
❌ Kein Mikrofon verfügbar für Hot Word Detection
```
**Lösung**: 
- Prüfe Mikrofon-Verbindung
- Teste Mikrofon in anderen Anwendungen
- Starte Mauscribe als Administrator

#### 2. Wake Words werden nicht erkannt
```
⚠️ Keine Sprache erkannt
```
**Lösung**:
- Erhöhe `sensitivity` in settings.toml
- Sprich deutlicher und langsamer
- Reduziere Hintergrundgeräusche
- Prüfe Mikrofon-Lautstärke

#### 3. Speech Recognition Fehler
```
⚠️ Speech Recognition Fehler: [Errno 11001]
```
**Lösung**:
- Prüfe Internetverbindung (Google API benötigt Internet)
- Verwende andere Speech Recognition Engine
- Prüfe Firewall-Einstellungen

#### 4. Performance-Probleme
```
⚠️ Audio-Stream konnte nicht gestartet werden
```
**Lösung**:
- Reduziere `chunk_size` in audio-Einstellungen
- Verwende `cpu` als compute_device
- Schließe andere Audio-Anwendungen

### Debug-Modus

Aktiviere Debug-Logging in `settings.toml`:

```toml
[logging]
console_level = "DEBUG"
file_level = "DEBUG"
```

## 📊 Statistiken

### Verfügbare Statistiken

```python
stats = app.get_hotword_status()
print(f"Aktiv: {stats['active']}")
print(f"Detections: {stats['detection_count']}")
print(f"Letzte Erkennung: {stats['last_detection_time']}")
print(f"Wake Words: {stats['wake_words']}")
```

### Performance-Metriken

- **Erkennungszeit**: ~1-2 Sekunden
- **CPU-Verbrauch**: ~5-10% (kontinuierlich)
- **Speicherverbrauch**: ~50-100MB zusätzlich
- **Netzwerk**: ~1-2KB pro Erkennungsversuch

## 🔄 Modus-Umschaltung

### Automatischer Fallback

Wenn Hot Word Detection fehlschlägt:
1. System fällt automatisch auf Mausklick-Modus zurück
2. Benachrichtigung wird angezeigt
3. Normale Funktionalität bleibt erhalten

### Manuelle Umschaltung

```python
# In der Anwendung
app.toggle_hotword_detection()  # Ein/Aus schalten
```

## 🎛️ Erweiterte Konfiguration

### Wake Words anpassen

```toml
[hotword]
wake_words = [
    "hey computer",
    "computer",
    "hey assistant",
    "assistant"
]
```

### Sensitivität optimieren

```toml
[hotword]
sensitivity = 0.3  # Sehr empfindlich (mehr False Positives)
sensitivity = 0.7  # Weniger empfindlich (weniger Erkennungen)
```

### Timeout konfigurieren

```toml
[hotword]
timeout_seconds = 60  # 1 Minute kontinuierliche Überwachung
timeout_seconds = 0   # Unbegrenzte Überwachung
```

## 🔒 Sicherheit & Datenschutz

### Datenschutz

- **Google Speech API**: Audio wird an Google gesendet
- **Lokale Verarbeitung**: Keine dauerhafte Speicherung
- **Verschlüsselung**: HTTPS-Verbindung zu Google

### Alternative Engines

Für bessere Datenschutz können andere Engines verwendet werden:
- **Vosk**: Offline Speech Recognition
- **Sphinx**: CMU Speech Recognition
- **Azure Speech**: Microsoft Speech Services

## 📈 Zukünftige Erweiterungen

### Geplante Features

1. **Offline-Modus**: Lokale Speech Recognition
2. **Custom Wake Words**: Benutzerdefinierte Training
3. **Sprachbefehle**: Erweiterte Sprachsteuerung
4. **Multi-Language**: Mehrsprachige Unterstützung
5. **Noise Cancellation**: Rauschunterdrückung

### API-Erweiterungen

```python
# Zukünftige API
detector.add_custom_wake_word("custom word")
detector.set_language("en-US")
detector.enable_noise_cancellation()
```

## 📝 Changelog

### v1.0.0 (Initial)
- Grundlegende Hot Word Detection
- Google Speech Recognition Integration
- System Tray Integration
- Konfigurierbare Wake Words
- Automatischer Fallback auf Mausklick-Modus
