# Automated Pipeline Monitoring

## Übersicht

Das Mauscribe-Projekt verfügt über ein automatisiertes Pipeline-Monitoring-System, das nach jedem `git push` automatisch den Status Ihrer CI/CD-Pipelines überwacht und Ihnen detailliertes Feedback gibt.

## 🚀 Features

### Automatische Überwachung
- **Post-Push Hook**: Läuft automatisch nach jedem `git push`
- **Echtzeit-Status**: Zeigt den aktuellen Status der Pipelines
- **Detaillierte Berichte**: Erfolg, Fehler und Fortschritt werden angezeigt
- **Automatische Fehleranalyse**: Zeigt fehlgeschlagene Jobs und Fehlermeldungen

### Benachrichtigungen
- ✅ **Erfolg**: Pipeline erfolgreich abgeschlossen
- ❌ **Fehler**: Detaillierte Fehlerinformationen
- ⚡ **Laufend**: Fortschritt der laufenden Jobs
- ⏳ **Wartend**: Status der wartenden Pipelines

## 🔧 Installation

### 1. Automatische Einrichtung
```bash
# Führen Sie das Setup-Skript aus
python setup_pipeline_monitoring.py
```

### 2. Manuelle Einrichtung
```bash
# Erstellen Sie die Git Hooks manuell
mkdir -p .git/hooks

# Für Windows (PowerShell)
# Kopieren Sie den Inhalt von .git/hooks/post-push.ps1

# Für Unix/Linux/macOS
# Kopieren Sie den Inhalt von .git/hooks/post-push
# chmod +x .git/hooks/post-push
```

## 📋 Verwendung

### Automatische Überwachung
Nach der Einrichtung läuft die Überwachung automatisch:

```bash
# Einfacher Push - Überwachung startet automatisch
git add .
git commit -m "Your commit message"
git push origin your-branch
```

### Manuelle Überwachung
```bash
# Pipeline-Status manuell überprüfen
python pipeline_monitor.py

# Pipeline-Status im Browser öffnen
python pipeline_monitor.py --open
```

## 🔑 GitHub Token Konfiguration

Für die Pipeline-Überwachung benötigen Sie ein GitHub Personal Access Token:

### Option 1: Umgebungsvariable
```bash
# Windows
set GITHUB_TOKEN=your_token_here

# Unix/Linux/macOS
export GITHUB_TOKEN=your_token_here
```

### Option 2: Git Konfiguration
```bash
# Globale Konfiguration
git config --global github.token your_token_here

# Lokale Konfiguration
git config github.token your_token_here
```

### Token erstellen
1. Gehen Sie zu GitHub → Settings → Developer settings → Personal access tokens
2. Klicken Sie auf "Generate new token"
3. Wählen Sie den Scope `repo` aus
4. Kopieren Sie das Token und konfigurieren Sie es wie oben beschrieben

## 📊 Überwachungsdetails

### Was wird überwacht
- **Workflow-Status**: Erfolg, Fehler, Laufend, Wartend
- **Job-Details**: Einzelne Job-Status und -Logs
- **Laufzeit**: Dauer der Pipeline-Ausführung
- **Fehleranalyse**: Detaillierte Fehlermeldungen bei Fehlern

### Überwachungszeitraum
- **Standard**: 5 Minuten (300 Sekunden)
- **Prüfintervall**: Alle 15 Sekunden
- **Konfigurierbar**: Über `.pipeline-monitor-config`

## 🎯 Konfiguration

### Konfigurationsdatei
Die Datei `.pipeline-monitor-config` enthält alle Einstellungen:

```ini
[monitoring]
enabled = true
max_wait_time = 300
check_interval = 15

[notifications]
show_progress = true
show_job_details = true
open_browser_on_failure = false

[github]
token_source = auto
repo_owner = R0bes
repo_name = Mauscribe
```

### Anpassbare Parameter
- **max_wait_time**: Maximale Wartezeit in Sekunden
- **check_interval**: Prüfintervall in Sekunden
- **show_progress**: Fortschrittsanzeige aktivieren
- **show_job_details**: Detaillierte Job-Informationen anzeigen

## 🔍 Fehlerbehebung

### Häufige Probleme

#### 1. Kein GitHub Token
```
⚠️  No GitHub token found. Cannot check pipeline status.
   Set GITHUB_TOKEN environment variable or configure git config github.token
```

**Lösung**: GitHub Token konfigurieren (siehe oben)

#### 2. Hook läuft nicht
```
⚠️  Warning: No post-push hook found for pipeline monitoring
   Run 'python setup_pipeline_monitoring.py' to set up monitoring
```

**Lösung**: Setup-Skript ausführen

#### 3. PowerShell Execution Policy (Windows)
```
❌ Error running pipeline monitor: Execution policy error
```

**Lösung**: PowerShell Execution Policy ändern
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 4. Fehlende Dependencies
```
❌ ModuleNotFoundError: No module named 'requests'
```

**Lösung**: Dependencies installieren
```bash
pip install -r requirements-dev.txt
```

### Debug-Modus
```bash
# Detaillierte Ausgabe aktivieren
python pipeline_monitor.py --debug

# Nur Status prüfen ohne Warten
python pipeline_monitor.py --check-only
```

## 📱 Benachrichtigungen

### Erfolgreiche Pipeline
```
🎉 Pipeline Success Summary:
------------------------------
✅ Workflow: CI/CD Pipeline
⏱️  Duration: 2m 15s
🔗 URL: https://github.com/R0bes/Mauscribe/actions/runs/123456789

📋 Jobs (5):
  ✅ Code Quality: success
  ✅ Testing: success
  ✅ Build: success
  ✅ Coverage: success
  ✅ Deploy: success
```

### Fehlgeschlagene Pipeline
```
❌ Pipeline Failure Details:
------------------------------
🔗 Workflow: CI/CD Pipeline
🔗 URL: https://github.com/R0bes/Mauscribe/actions/runs/123456789
⏱️  Duration: 1m 45s

❌ Failed Jobs (1):
  🔥 Testing
     Started: 2024-01-15T10:30:00Z
     Completed: 2024-01-15T10:31:45Z
     Recent errors:
       ERROR: test_config.py::TestConfig::test_config_initialization FAILED
       ERROR: test_recorder.py::TestAudioRecorder::test_recorder_initialization FAILED
```

## 🚀 Erweiterte Funktionen

### Benutzerdefinierte Hooks
Sie können eigene Hook-Skripte erstellen:

```bash
# .git/hooks/post-push-custom
#!/bin/bash
echo "Custom post-push action"
python pipeline_monitor.py
# Weitere Aktionen...
```

### Integration mit anderen Tools
```bash
# Slack-Benachrichtigung bei Pipeline-Fehlern
if [ $? -ne 0 ]; then
    curl -X POST -H 'Content-type: application/json' \
         --data '{"text":"Pipeline failed!"}' \
         https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
fi
```

### Cron-Jobs für kontinuierliche Überwachung
```bash
# Überprüfen Sie alle 5 Minuten
*/5 * * * * cd /path/to/mouscribe && python pipeline_monitor.py
```

## 📚 API-Referenz

### PipelineMonitor Klasse

#### Methoden
- `monitor_pipelines(max_wait_time=300)`: Überwacht Pipelines
- `get_workflow_runs(branch, commit_sha)`: Holt Workflow-Läufe
- `get_workflow_details(workflow_id)`: Holt Workflow-Details
- `get_job_logs(workflow_id, job_id)`: Holt Job-Logs

#### Eigenschaften
- `repo_owner`: GitHub Repository-Besitzer
- `repo_name`: GitHub Repository-Name
- `github_token`: GitHub Personal Access Token

### Kommandozeilen-Argumente
- `--open`: Öffnet Pipeline-Status im Browser
- `--debug`: Aktiviert Debug-Ausgabe
- `--check-only`: Prüft nur den Status ohne zu warten

## 🤝 Beitragen

### Entwicklung
1. Forken Sie das Repository
2. Erstellen Sie einen Feature-Branch
3. Implementieren Sie Ihre Änderungen
4. Testen Sie die Funktionalität
5. Erstellen Sie einen Pull Request

### Fehler melden
- Verwenden Sie GitHub Issues
- Beschreiben Sie das Problem detailliert
- Fügen Sie Logs und Screenshots hinzu

## 📄 Lizenz

Dieses Projekt steht unter der gleichen Lizenz wie Mauscribe.

## 🆘 Support

Bei Fragen oder Problemen:
1. Überprüfen Sie diese Dokumentation
2. Schauen Sie in die GitHub Issues
3. Erstellen Sie ein neues Issue bei Bedarf

---

**Hinweis**: Die automatische Pipeline-Überwachung ist ein leistungsstarkes Tool, das Ihnen hilft, den Status Ihrer CI/CD-Pipelines immer im Blick zu behalten. Nutzen Sie es, um frühzeitig Probleme zu erkennen und die Qualität Ihres Codes zu gewährleisten.
