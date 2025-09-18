# GitHub Token Setup für Pipeline Monitoring

## 🔑 GitHub Token erstellen

1. **Gehe zu GitHub Settings:**
   - https://github.com/settings/tokens
   - Oder: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **Erstelle einen neuen Token:**
   - Klicke auf "Generate new token" → "Generate new token (classic)"
   - Gib einen Namen ein: z.B. "Mauscribe Pipeline Monitor"

3. **Wähle die benötigten Berechtigungen:**
   ```
   ✅ repo (Full control of private repositories)
     ✅ repo:status (Access commit status)
     ✅ repo_deployment (Access deployment status)
     ✅ public_repo (Access public repositories)
   ✅ workflow (Update GitHub Action workflows)
   ```

4. **Token kopieren und speichern:**
   - ⚠️ **WICHTIG**: Kopiere den Token sofort, er wird nur einmal angezeigt!

## 🔧 Token verwenden

### Option 1: Umgebungsvariable setzen
```bash
# Windows PowerShell
$env:GITHUB_TOKEN="dein_token_hier"

# Windows CMD
set GITHUB_TOKEN=dein_token_hier

# Linux/Mac
export GITHUB_TOKEN="dein_token_hier"
```

### Option 2: .env Datei erstellen
Erstelle eine `.env` Datei im Projektverzeichnis:
```
GITHUB_TOKEN=dein_token_hier
```

### Option 3: GitHub CLI verwenden
```bash
gh auth login
gh auth token
```

## 🚀 Pipeline Monitoring starten

Nach dem Token-Setup:

```bash
# Normales Monitoring
python pipeline_monitor.py

# Fehleranalyse
python pipeline_monitor.py --analyze
```

## 📊 Was das Monitoring zeigt

- ✅ **Status aller Workflow-Runs**
- ❌ **Fehlgeschlagene Jobs mit Details**
- 📝 **Vollständige Logs der fehlgeschlagenen Jobs**
- 🔗 **Direkte Links zu GitHub Actions**

## 🔍 Aktuelle Pipeline-Fehler

Basierend auf der letzten Analyse:

- **Hauptproblem**: "Validate Code" Jobs schlagen fehl
- **Betroffene Python-Versionen**: 3.9, 3.10, 3.11
- **Status**: Alle anderen Jobs werden übersprungen (skipped)

**Nächste Schritte:**
1. GitHub Token einrichten
2. Detaillierte Logs analysieren
3. Spezifische Fehler beheben
