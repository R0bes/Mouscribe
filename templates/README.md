# Mauscribe Git Hooks

Dieses Verzeichnis enthält Git Hooks für das Mauscribe Repository, die automatisch Pipeline Monitoring und Qualitätschecks durchführen.

## Verfügbare Hooks

### pre-push
- **Wird ausgeführt:** Vor jedem `git push`
- **Funktionalität:** 
  - Überprüft geschützte Branches
  - Läuft Tests vor dem Push
  - Führt Linting-Checks durch
  - Verhindert Push bei Fehlern
- **Verwendung:** Automatisch vor jedem Push

### post-push
- **Wird ausgeführt:** Nach jedem `git push`
- **Funktionalität:** 
  - Startet automatisch das Pipeline Monitoring
  - Überwacht CI/CD-Pipelines
  - Zeigt hilfreiche Links zu CI/CD-Platforms
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
   chmod +x .git/hooks/pre-push
   chmod +x .git/hooks/post-push
   ```

## Für neue Repositories

1. Klone dieses Repository
2. Führe `python setup_git_hooks.py` aus
3. Die Hooks werden automatisch installiert und funktionieren sofort

## Hook-Ablauf

```
git push → pre-push → post-push
     ↓         ↓         ↓
   Push    Qualitäts-  Pipeline
         checks      Monitoring
```

## Anpassung

Die Hooks können nach Bedarf angepasst werden:
- Ändere die Logik in den Hook-Dateien
- Füge neue Hooks hinzu
- Passe die Pipeline-Monitoring-Funktionalität an
- Modifiziere die geschützten Branches im pre-push Hook

## Troubleshooting

### Hooks werden nicht ausgeführt
- Überprüfe, ob die Dateien in `.git/hooks/` existieren
- Stelle sicher, dass die Dateien ausführbar sind
- Überprüfe die Berechtigungen

### Pipeline Monitoring funktioniert nicht
- Überprüfe, ob `pipeline_monitor.py` im Repository existiert
- Stelle sicher, dass Python verfügbar ist
- Überprüfe die Ausgabe der Hooks für Fehlermeldungen

### Pre-push Hook blockiert Push
- Führe Tests aus: `python run_tests.py`
- Behebe Linting-Fehler: `pre-commit run --all-files`
- Überprüfe, ob du auf einem geschützten Branch bist
