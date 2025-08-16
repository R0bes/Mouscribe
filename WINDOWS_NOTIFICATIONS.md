# Windows-Benachrichtigungen für Mauscribe

## Übersicht

Mauscribe unterstützt jetzt Windows-Benachrichtigungen (Toast-Notifications) für Windows 10 und 11. Diese Benachrichtigungen bieten visuelles Feedback für verschiedene Anwendungsereignisse.

## Funktionen

### Unterstützte Benachrichtigungstypen

- **🎙️ Aufnahme gestartet** - Wird angezeigt, wenn die Sprachaufnahme beginnt
- **🛑 Aufnahme gestoppt** - Wird angezeigt, wenn die Aufnahme beendet wird
- **✨ Transkription abgeschlossen** - Wird angezeigt, wenn die Spracherkennung abgeschlossen ist
- **📋 Text eingefügt** - Wird angezeigt, wenn transkribierter Text eingefügt wird
- **🔍 Rechtschreibprüfung** - Wird angezeigt, wenn die Rechtschreibprüfung abgeschlossen ist
- **ℹ️ Information** - Allgemeine Informationsbenachrichtigungen
- **⚠️ Warnung** - Warnungsbenachrichtigungen
- **❌ Fehler** - Fehlerbenachrichtigungen

### Systemanforderungen

- Windows 10 oder höher
- Python mit `pywin32` Paket
- Aktivierte Windows-Benachrichtigungen im System

## Konfiguration

### Grundlegende Einstellungen

```toml
[notifications]
# Windows-Benachrichtigungen aktivieren
enabled = true
# Anzeigedauer in Millisekunden
duration = 5000
# Benachrichtigungstöne aktivieren
sound = true
# Toast-Benachrichtigungen aktivieren
toast = true
```

### Ereignis-spezifische Einstellungen

```toml
[notifications]
# Start-Benachrichtigung anzeigen
show_startup = true
# Beendigungs-Benachrichtigung anzeigen
show_shutdown = true
# Aufnahme-Ereignisse anzeigen (Start/Stopp)
show_recording_events = true
# Transkriptions-Ereignisse anzeigen
show_transcription_events = true
# Text-Ereignisse anzeigen (Einfügen)
show_text_events = true
# Rechtschreibprüfungs-Ereignisse anzeigen
show_spell_check_events = true
# Fehler-Benachrichtigungen anzeigen
show_errors = true
# Warnungs-Benachrichtigungen anzeigen
show_warnings = true
```

## Verwendung

### Automatische Benachrichtigungen

Die Benachrichtigungen werden automatisch angezeigt bei:

1. **Anwendungsstart** - Bestätigung, dass Mauscribe erfolgreich gestartet wurde
2. **Aufnahmebeginn** - Visueller Hinweis, dass die Aufnahme läuft
3. **Aufnahmeende** - Bestätigung, dass die Aufnahme beendet wurde
4. **Transkriptionsabschluss** - Anzeige des transkribierten Texts
5. **Texteinfügung** - Bestätigung, dass Text eingefügt wurde
6. **Rechtschreibprüfung** - Ergebnis der Rechtschreibprüfung
7. **Fehler und Warnungen** - Wichtige Systemmeldungen
8. **Anwendungsende** - Bestätigung des erfolgreichen Beendens

### Benachrichtigungen deaktivieren

Um alle Benachrichtigungen zu deaktivieren:

```toml
[notifications]
enabled = false
```

Um nur bestimmte Benachrichtigungstypen zu deaktivieren:

```toml
[notifications]
enabled = true
show_startup = false
show_recording_events = false
show_transcription_events = false
```

## Technische Details

### Implementierung

- **Primäre Methode**: Moderne MessageBox-Notifications als elegante Popup-Dialoge
- **Design**: Windows-native Dialoge mit modernen Icons und Styling
- **Position**: Automatisch zentriert, immer sichtbar
- **Verhalten**: Nicht-blockierend, konfigurierbare Anzeigedauer, Klick zum Schließen
- **Konfiguration**: Vollständig über `config.toml` steuerbar
- **Performance**: Thread-basierte, nicht-blockierende Benachrichtigungen
- **Fallback**: Robuste Fehlerbehandlung mit automatischem Fallback

### Abhängigkeiten

- `pywin32` - Für Windows-API-Zugriff
- `sys` - Für Windows-Versionserkennung
- Integriert in die bestehende Mauscribe-Architektur
- **Hinweis**: `win10toast` wird nicht mehr verwendet, da es instabil ist

### Fehlerbehandlung

- Automatische Erkennung der Windows-Version
- Graceful Fallback bei fehlenden Abhängigkeiten
- Robuste Fehlerbehandlung für alle Benachrichtigungstypen
- Logging aller Benachrichtigungsereignisse
- Konfigurierbare Fehlerbehandlung

## Testen

### Test-Skript ausführen

```bash
python test_notifications.py
```

Das Test-Skript zeigt alle verfügbaren Benachrichtigungstypen an.

### Manuelle Tests

1. Starten Sie Mauscribe
2. Führen Sie eine Sprachaufnahme durch
3. Beobachten Sie die Benachrichtigungen
4. Überprüfen Sie die Konfigurationseinstellungen

## Troubleshooting

### Häufige Probleme

1. **Keine Benachrichtigungen angezeigt**
   - Überprüfen Sie, ob `enabled = true` in der Konfiguration
   - Stellen Sie sicher, dass Windows 10+ läuft
   - Überprüfen Sie die Windows-Benachrichtigungseinstellungen

2. **Fehler beim Importieren**
   - Installieren Sie `pywin32`: `pip install pywin32`
   - Überprüfen Sie die Python-Umgebung

3. **Benachrichtigungen zu häufig**
   - Reduzieren Sie die `duration` in der Konfiguration
   - Deaktivieren Sie nicht benötigte Benachrichtigungstypen

### Debugging

Aktivieren Sie Debug-Logging:

```toml
[debug]
enabled = true
level = "DEBUG"
```

### Logs überprüfen

Benachrichtigungsereignisse werden im Mauscribe-Log protokolliert.

## Zukünftige Verbesserungen

- Erweiterte Animationen (Ein-/Ausblenden)
- Benutzerdefinierte Benachrichtigungstöne
- Verschiedene Positionen (oben, links, rechts)
- Integration mit Windows Action Center
- Push-Benachrichtigungen für mobile Geräte
- Benutzerdefinierte Themes und Farben

## Support

Bei Problemen mit den Windows-Benachrichtigungen:

1. Überprüfen Sie die Konfiguration
2. Führen Sie das Test-Skript aus
3. Überprüfen Sie die Logs
4. Erstellen Sie ein Issue im Mauscribe-Repository
