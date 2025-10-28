<!-- 82526ced-cfb7-404e-8b39-b6b23b6048cf cefc038a-e709-4597-855b-5d5dd74d16ed -->
# Setup.exe Installer mit Whisper-Modell-Auswahl

## Übersicht

Wir erweitern den bestehenden Inno Setup Installer (`installer/mauscribe.iss`) um:

1. Einzelne Auswahloptionen für alle 5 Whisper-Modelle während der Installation
2. Optional installierbare Audio-Datenbank
3. Flexible Installationsverzeichnis-Wahl (Default: Program Files)
4. Post-Install Download der ausgewählten Modelle

Die Anwendung wird erweitert um:

1. Visuelle Unterscheidung zwischen heruntergeladenen und nicht heruntergeladenen Modellen im System Tray
2. Bestätigungsdialog vor Download neuer Modelle
3. Download-Manager mit Progress-Anzeige

## Dateien zum Ändern

### 1. `installer/features.json`

- Alle 5 Whisper-Modell Download-URLs hinzufügen (tiny, base fehlen aktuell)
- Modell-Metadaten aktualisieren (Größen, Beschreibungen)

### 2. `installer/mauscribe.iss`

- 5 separate Tasks für Whisper-Modelle (tiny, base, small, medium, large)
- Audio-Datenbank als optionale Task
- Installationsverzeichnis-Auswahl aktivieren
- Post-Install Script mit ausgewählten Features aufrufen

### 3. `tools/post_install.py`

- `download_whisper_models()` erweitern für selektiven Download
- Modelle nach `%APPDATA%\Mauscribe\models\` herunterladen (Fallback: Program Files)
- Progress-Feedback während Download
- Fehlerbehandlung und Retry-Logik

### 4. `src/ui/system_tray.py`

- `_create_whisper_model_submenu()` erweitern
- Modell-Download-Status prüfen (`_is_model_downloaded()`)
- Icons/Präfixe: "✅" für geladen, "⬇️" für nicht geladen
- Bei nicht geladenen Modellen: Dialog vor Modellwechsel

### 5. `src/utils/model_downloader.py` (neu)

- Zentraler Modell-Download-Manager
- Async Download mit Progress-Callback
- Validierung heruntergeladener Dateien
- Fehlerbehandlung und Retry

### 6. `src/ui/dialogs/model_download_dialog.py` (neu)

- Bestätigungsdialog: "Modell X (Größe Y MB) herunterladen?"
- Progress-Bar während Download
- Abbrechen-Funktion
- Erfolgs-/Fehlermeldung

### 7. `tools/build_setup.py` (neu)

- Automatisiertes Build-Script für Setup.exe
- Ruft PyInstaller auf
- Kompiliert Inno Setup Script
- Erstellt `dist/Mauscribe-{version}-Setup.exe`

### 8. `.github/workflows/installer.yml`

- Inno Setup Compiler Installation hinzufügen
- Setup.exe Build-Schritt
- Upload als Release-Artifact

## Implementation Details

### Whisper-Modelle in features.json

```json
"whisper_models": {
  "download_urls": {
    "tiny": "https://huggingface.co/guillaumekln/faster-whisper-tiny/resolve/main/model.bin",
    "base": "https://huggingface.co/guillaumekln/faster-whisper-base/resolve/main/model.bin",
    "small": "https://huggingface.co/guillaumekln/faster-whisper-small/resolve/main/model.bin",
    "medium": "https://huggingface.co/guillaumekln/faster-whisper-medium/resolve/main/model.bin",
    "large": "https://huggingface.co/guillaumekln/faster-whisper-large-v2/resolve/main/model.bin"
  },
  "sizes_mb": {
    "tiny": 39,
    "base": 74,
    "small": 244,
    "medium": 769,
    "large": 1550
  }
}
```

### Inno Setup Tasks

```ini
[Tasks]
Name: "whisper_tiny"; Description: "Tiny (39 MB) - Schnellste"; GroupDescription: "Whisper-Modelle (optional)"
Name: "whisper_base"; Description: "Base (74 MB) - Ausgewogen"; GroupDescription: "Whisper-Modelle (optional)"
Name: "whisper_small"; Description: "Small (244 MB) - Gut"; GroupDescription: "Whisper-Modelle (optional)"
Name: "whisper_medium"; Description: "Medium (769 MB) - Sehr gut"; GroupDescription: "Whisper-Modelle (optional)"; Flags: checked
Name: "whisper_large"; Description: "Large (1550 MB) - Beste Qualität"; GroupDescription: "Whisper-Modelle (optional)"
Name: "audio_database"; Description: "Audio-Datenbank installieren"; GroupDescription: "Features"; Flags: checked
```

### System Tray Modell-Status

```python
def _is_model_downloaded(self, model: str) -> bool:
    """Prüft, ob Whisper-Modell bereits heruntergeladen ist."""
    appdata = Path(os.getenv('APPDATA', ''))
    models_dir = appdata / 'Mauscribe' / 'models'
    model_file = models_dir / f"{model}.bin"
    return model_file.exists()

def _create_whisper_model_submenu(self) -> list:
    models = [
        ("tiny", "Tiny (39 MB) - Schnellste"),
        ("base", "Base (74 MB) - Ausgewogen"),
        ("small", "Small (244 MB) - Gut"),
        ("medium", "Medium (769 MB) - Sehr gut"),
        ("large", "Large (1550 MB) - Beste Qualität"),
    ]

    current_model = self.config.audio.model
    submenu_items = []

    for model_id, model_desc in models:
        is_downloaded = self._is_model_downloaded(model_id)

        # Status-Icon
        if model_id == current_model:
            prefix = "✅"
        elif is_downloaded:
            prefix = "📦"
        else:
            prefix = "⬇️"

        status = " (geladen)" if is_downloaded else " (nicht geladen)"

        menu_item = pystray.MenuItem(
            f"{prefix} {model_desc}{status}",
            lambda icon, item, m=model_id, dl=is_downloaded: self._select_model(m, dl)
        )
        submenu_items.append(menu_item)

    return submenu_items

def _select_model(self, model: str, is_downloaded: bool):
    """Modell auswählen - bei nicht geladenen Modellen Dialog anzeigen."""
    if not is_downloaded:
        # Dialog-Bestätigung erforderlich
        self._show_model_download_dialog(model)
    else:
        # Direkt wechseln
        self._set_whisper_model(model)
```

## Testing

1. **Installer testen**:

   - Setup.exe lokal bauen und ausführen
   - Verschiedene Modell-Kombinationen auswählen
   - Audio-Datenbank an/aus
   - Installationsverzeichnis ändern

2. **Modell-Download testen**:

   - Post-Install Download verifizieren
   - Fehlerfall testen (kein Internet)
   - Modelle in korrektem Verzeichnis

3. **GUI-Funktionen testen**:

   - System Tray zeigt korrekten Status
   - Dialog erscheint bei nicht geladenen Modellen
   - Download funktioniert aus Anwendung heraus
   - Modellwechsel funktioniert

4. **Audio-Datenbank optional**:

   - Mit Audio-DB: Tab sichtbar, DB funktioniert
   - Ohne Audio-DB: Tab nicht sichtbar, keine Fehler

### To-dos

- [ ] features.json: Alle 5 Whisper-Modelle mit URLs und Größen hinzufügen
- [ ] mauscribe.iss: Tasks für alle Modelle und Audio-DB erweitern
- [ ] post_install.py: Selektiver Modell-Download nach User-Auswahl
- [ ] model_downloader.py: Zentrale Download-Logik mit Progress
- [ ] model_download_dialog.py: GUI-Dialog für Download-Bestätigung
- [ ] system_tray.py: Modell-Status anzeigen und Dialog integrieren
- [ ] build_setup.py: Automatisches Build-Script für Setup.exe
- [ ] installer.yml: CI/CD für Setup.exe-Build
- [ ] Komplettes Testing: Installer, Downloads, GUI, Audio-DB
