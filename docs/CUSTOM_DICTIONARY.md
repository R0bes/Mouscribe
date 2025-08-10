# Benutzerdefiniertes Wörterbuch - Mauscribe

## Übersicht

Das benutzerdefinierte Wörterbuch ist ein Feature von Mauscribe, das es Benutzern ermöglicht, eigene Wörter zu definieren, die bei der Rechtschreibprüfung als korrekt betrachtet werden sollen. Dies ist besonders nützlich für:

- Fachbegriffe und technische Terminologie
- Eigennamen und Abkürzungen
- Branchenspezifische Begriffe
- Regionale oder dialektale Ausdrücke

## Funktionen

### 🆕 Wörter hinzufügen
- Einzelne Wörter über die GUI oder Kommandozeile hinzufügen
- Automatisches Hinzufügen unbekannter Wörter (konfigurierbar)
- Import von Wortlisten aus Textdateien

### 🗑️ Wörter entfernen
- Einzelne Wörter entfernen
- Wörterbuch komplett leeren
- Export aller Wörter vor dem Löschen

### 🔍 Wörter suchen
- Durchsuchbare Wortliste
- Filterung nach Suchbegriffen
- Anzeige der Gesamtanzahl der Wörter

### 📁 Import/Export
- Import von Wortlisten (eine Wort pro Zeile)
- Export aller Wörter in Textdateien
- Unterstützung für UTF-8 Kodierung

## Konfiguration

Das Feature kann über die `config.toml` Datei konfiguriert werden:

```toml
[custom_dictionary]
# Benutzerdefiniertes Wörterbuch aktivieren
enabled = true
# Automatisch unbekannte Wörter zum Wörterbuch hinzufügen
auto_add_unknown = false
# Wörterbuch-Pfad (leer = Standard-Pfad im Benutzerverzeichnis)
path = ""
# Maximale Anzahl von Wörtern im Wörterbuch (0 = unbegrenzt)
max_words = 1000
```

### Einstellungen im Detail

- **enabled**: Aktiviert/deaktiviert das Feature
- **auto_add_unknown**: Fügt automatisch unbekannte Wörter hinzu
- **path**: Benutzerdefinierter Pfad zur Wörterbuch-Datei
- **max_words**: Begrenzung der Wörteranzahl (0 = unbegrenzt)

## Verwendung

### Grafische Benutzeroberfläche

Starte die GUI mit:

```bash
python -m src.dictionary_gui
```

Die GUI bietet:
- Einfaches Hinzufügen von Wörtern
- Durchsuchbare Wortliste
- Import/Export-Funktionen
- Wörterbuch-Informationen

### Kommandozeile

Verwende das Wörterbuch über die Kommandozeile:

```bash
# Alle Wörter anzeigen
python -m src.dictionary_manager list

# Wort hinzufügen
python -m src.dictionary_manager add "Beispielwort"

# Wort entfernen
python -m src.dictionary_manager remove "Beispielwort"

# Wort suchen
python -m src.dictionary_manager search "Beispielwort"

# Wörter importieren
python -m src.dictionary_manager import "wort1,wort2,wort3"

# Wörter exportieren
python -m src.dictionary_manager export output.txt

# Wörterbuch leeren
python -m src.dictionary_manager clear

# Informationen anzeigen
python -m src.dictionary_manager info
```

### Programmierung

Das Feature kann auch programmatisch verwendet werden:

```python
from src.custom_dictionary import get_custom_dictionary

# Wörterbuch-Instanz abrufen
dictionary = get_custom_dictionary()

# Wort hinzufügen
dictionary.add_word("neues_wort")

# Wort prüfen
if dictionary.has_word("testwort"):
    print("Wort ist im Wörterbuch")

# Alle Wörter abrufen
words = dictionary.get_all_words()
```

## Dateistruktur

Das Wörterbuch wird standardmäßig gespeichert unter:

- **Windows**: `%USERPROFILE%\.mauscribe\custom_dictionary.json`
- **Linux/macOS**: `~/.mauscribe/custom_dictionary.json`

Die JSON-Datei hat folgende Struktur:

```json
{
  "words": [
    "beispielwort1",
    "beispielwort2",
    "fachbegriff"
  ],
  "metadata": {
    "version": "1.0",
    "created": "/path/to/creation",
    "total_words": 3
  }
}
```

## Integration mit der Rechtschreibprüfung

Das benutzerdefinierte Wörterbuch wird automatisch in die Rechtschreibprüfung integriert:

1. **Wörter werden gefiltert**: Wörter im benutzerdefinierten Wörterbuch werden nicht als Fehler markiert
2. **Automatische Ergänzung**: Bei aktivierter `auto_add_unknown` Option werden unbekannte Wörter automatisch hinzugefügt
3. **Priorität**: Benutzerdefinierte Wörter haben Vorrang vor dem Standard-Wörterbuch

## Fehlerbehebung

### Häufige Probleme

**Wörterbuch wird nicht geladen**
- Prüfe die Berechtigungen im Benutzerverzeichnis
- Stelle sicher, dass das Feature in der Konfiguration aktiviert ist

**Wörter werden nicht hinzugefügt**
- Prüfe, ob das Wörterbuch die maximale Anzahl erreicht hat
- Stelle sicher, dass der Pfad beschreibbar ist

**Rechtschreibprüfung berücksichtigt Wörter nicht**
- Starte Mauscribe neu nach Änderungen am Wörterbuch
- Prüfe, ob das Feature in der Konfiguration aktiviert ist

### Logs

Das Feature protokolliert alle wichtigen Aktionen. Prüfe die Konsolenausgabe für:
- Erfolgreiche Wörterbuch-Operationen
- Fehler beim Laden/Speichern
- Informationen über die Anzahl der Wörter

## Erweiterte Funktionen

### Batch-Import

Für große Wortlisten können mehrere Wörter gleichzeitig importiert werden:

```bash
# Aus Datei importieren
python -m src.dictionary_manager import "$(cat wordlist.txt)"

# Mehrere Wörter auf einmal
python -m src.dictionary_manager import "wort1,wort2,wort3,wort4"
```

### Wörterbuch-Synchronisation

Das Wörterbuch kann zwischen verschiedenen Systemen synchronisiert werden:

1. Exportiere das Wörterbuch auf System A
2. Kopiere die Datei auf System B
3. Importiere die Wörter auf System B

### Automatisierung

Das Feature kann in Skripten und Automatisierungstools verwendet werden:

```bash
#!/bin/bash
# Automatisches Hinzufügen von Fachbegriffen
python -m src.dictionary_manager add "Fachbegriff1"
python -m src.dictionary_manager add "Fachbegriff2"
python -m src.dictionary_manager add "Fachbegriff3"
```

## Support

Bei Problemen oder Fragen zum benutzerdefinierten Wörterbuch:

1. Prüfe die Dokumentation
2. Schaue in die Logs
3. Erstelle ein Issue im Projekt-Repository
4. Kontaktiere den Support

## Changelog

### Version 1.0
- Grundlegende Wörterbuch-Funktionalität
- GUI und Kommandozeilen-Schnittstelle
- Import/Export-Funktionen
- Integration mit der Rechtschreibprüfung
- Konfigurierbare Einstellungen
