# Mauscribe Git Hooks

Dieses Verzeichnis enthält Git Hooks für das Mauscribe Repository, die automatisch Pipeline Monitoring und andere CI/CD-Funktionen starten.

## Verfügbare Hooks

### post-commit
- **Wird ausgeführt:** Nach jedem `git commit`
- **Funktionalität:** 
  - Fragt, ob direkt `git push` ausgeführt werden soll
  - Startet bei Bestätigung das Pipeline Monitoring
- **Verwendung:** Automatisch nach jedem Commit

### post-push
- **Wird ausgeführt:** Nach jedem `git push`
- **Funktionalität:** 
  - Startet automatisch das Pipeline Monitoring
  - Überwacht CI/CD-Pipelines
- **Verwendung:** Automatisch nach jedem Push

## Installation

### Automatisch (Empfohlen)
```bash
python setup_git_hooks.py
```

### Manuell
1. Kopiere die gewünschten Hook-Dateien in `.git/hooks/`
2. Stelle sicher, dass die Dateien ausführbar sind:
   ```bash
   chmod +x .git/hooks/post-commit
   chmod +x .git/hooks/post-push
   ```

## Für neue Repositories

1. Klone dieses Repository
2. Führe `python setup_git_hooks.py` aus
3. Die Hooks werden automatisch installiert und funktionieren sofort

## Anpassung

Die Hooks können nach Bedarf angepasst werden:
- Ändere die Logik in den Hook-Dateien
- Füge neue Hooks hinzu
- Passe die Pipeline-Monitoring-Funktionalität an

## Troubleshooting

### Hooks werden nicht ausgeführt
- Überprüfe, ob die Dateien in `.git/hooks/` existieren
- Stelle sicher, dass die Dateien ausführbar sind
- Überprüfe die Berechtigungen

### Pipeline Monitoring funktioniert nicht
- Überprüfe, ob `pipeline_monitor.py` im Repository existiert
- Stelle sicher, dass Python verfügbar ist
- Überprüfe die Ausgabe der Hooks für Fehlermeldungen
