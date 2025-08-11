# Mauscribe Git Hooks

Dieses Verzeichnis enthält Git Hooks für das Mauscribe Repository, die automatisch Code-Qualitätschecks, Tests und Pipeline Monitoring durchführen.

## Verfügbare Hooks

### pre-commit
- **Wird ausgeführt:** Vor jedem `git commit`
- **Funktionalität:**
  - Läuft Pre-commit-Checks (Linting, Formatierung)
  - Überprüft gestagte Dateien auf Probleme
  - Verhindert Commit bei Fehlern
- **Verwendung:** Automatisch vor jedem Commit

### pre-push
- **Wird ausgeführt:** Vor jedem `git push`
- **Funktionalität:**
  - Läuft Tests vor dem Push
  - Startet Pipeline Monitoring
  - Überprüft geschützte Branches
  - Verhindert Push bei Test-Fehlern
- **Verwendung:** Automatisch vor jedem Push

## Installation

### Automatisch (Empfohlen)
```bash
python setup_git_hooks.py
```

### Manuell
1. Kopiere die gewünschten Hook-Dateien in `.git/hooks/`
2. Stelle sicher, dass die Dateien ausführbar sind:
   ```bash
   chmod +x .git/hooks/pre-commit
   chmod +x .git/hooks/pre-push
   ```

## Für neue Repositories

1. Klone dieses Repository
2. Führe `python setup_git_hooks.py` aus
3. Die Hooks werden automatisch installiert und funktionieren sofort

## Hook-Ablauf

```
git commit → pre-commit → git push → pre-push
     ↓           ↓           ↓         ↓
   Commit    Linting      Push     Tests +
            Checks                Pipeline Monitoring
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

### Pre-commit Hook blockiert Commit
- Behebe Linting-Fehler: `pre-commit run --all-files`
- Überprüfe gestagte Dateien auf Probleme
- Stelle sicher, dass pre-commit installiert ist

### Pre-push Hook blockiert Push
- Führe Tests aus: `python run_tests.py`
- Behebe fehlgeschlagene Tests
- Überprüfe, ob du auf einem geschützten Branch bist
