# Branch Protection Setup Guide

## Übersicht

Da GitHub Actions standardmäßig keine Branch Protection Rules setzen können, müssen diese manuell über das GitHub Webinterface eingerichtet werden.

## Schritt-für-Schritt Anleitung

### 1. Repository öffnen
- Gehe zu: https://github.com/R0bes/Mouscribe
- Klicke auf den **Settings** Tab

### 2. Branch Protection für `main` einrichten
- Klicke im linken Menü auf **Branches**
- Klicke auf **Add rule** neben dem `main` Branch
- Konfiguriere folgende Einstellungen:

#### **Branch name pattern:**
```
main
```

#### **Protect matching branches:**
- ✅ **Require a pull request before merging**
  - ✅ **Require approvals**: `1`
  - ✅ **Dismiss stale PR approvals when new commits are pushed**
  - ✅ **Require review from code owners** (optional)

- ✅ **Require status checks to pass before merging**
  - ✅ **Require branches to be up to date before merging**
  - Status checks: `test`, `build`

- ✅ **Require conversation resolution before merging**

- ✅ **Require signed commits** (optional, für zusätzliche Sicherheit)

- ✅ **Require linear history** (optional)

- ✅ **Restrict pushes that create files that match the specified patterns**
  - Pattern: `*.exe`, `*.msi`, `*.dmg`, `*.deb`, `*.rpm`, `*.AppImage`

- ✅ **Restrict pushes that delete files that match the specified patterns**
  - Pattern: `*.exe`, `*.msi`, `*.dmg`, `*.deb`, `*.rpm`, `*.AppImage`

#### **Restrict pushes that create files that match the specified patterns:**
```
*.exe
*.msi
*.dmg
*.deb
*.rpm
*.AppImage
```

#### **Restrict pushes that delete files that match the specified patterns:**
```
*.exe
*.msi
*.dmg
*.deb
*.rpm
*.AppImage
```

### 3. Branch Protection für `develop` einrichten (falls vorhanden)
- Klicke auf **Add rule** neben dem `develop` Branch
- Konfiguriere ähnliche Einstellungen, aber weniger restriktiv:

#### **Branch name pattern:**
```
develop
```

#### **Protect matching branches:**
- ✅ **Require a pull request before merging**
  - ✅ **Require approvals**: `1`
  - ✅ **Dismiss stale PR approvals when new commits are pushed**

- ✅ **Require status checks to pass before merging**
  - ✅ **Require branches to be up to date before merging**
  - Status checks: `test`

- ❌ **Require conversation resolution before merging** (weniger restriktiv)

### 4. Änderungen speichern
- Klicke auf **Create** oder **Save changes**
- Bestätige die Änderungen

## Überprüfung

Nach der Einrichtung kannst du überprüfen:

1. **Branch Protection Status**: Gehe zu Settings → Branches
2. **Workflow Status**: Gehe zu Actions Tab
3. **Test**: Versuche einen direkten Push auf `main` (sollte fehlschlagen)

## Workflow-Integration

Die eingerichteten Branch Protection Rules arbeiten mit den GitHub Actions Workflows:

- **CI/CD Pipeline**: Läuft bei Pushes auf `main` und `develop`
- **Feature Branch Workflow**: Läuft bei Feature-Branches
- **Auto-Develop Workflow**: Erstellt automatisch Feature-Branches

## Troubleshooting

### Häufige Probleme:

1. **"Branch is not protected"**
   - Überprüfe, ob die Protection Rules korrekt gesetzt wurden
   - Warte einige Minuten, bis die Änderungen aktiv werden

2. **"Required status checks are not passing"**
   - Überprüfe den Actions Tab auf fehlgeschlagene Workflows
   - Stelle sicher, dass alle erforderlichen Status Checks konfiguriert sind

3. **"Conversation resolution required"**
   - Alle Kommentare und Diskussionen müssen aufgelöst werden
   - Überprüfe den PR auf offene Kommentare

## Sicherheitshinweise

- Branch Protection Rules können nicht von GitHub Actions überschrieben werden
- Nur Repository-Administratoren können diese Regeln ändern
- Die Regeln gelten für alle Benutzer, einschließlich Administratoren (falls aktiviert)

## Nächste Schritte

Nach der Einrichtung der Branch Protection:

1. Teste die Workflows mit einem Feature-Branch
2. Überprüfe, ob Pull Requests korrekt funktionieren
3. Stelle sicher, dass alle Status Checks erfolgreich sind
4. Dokumentiere den Workflow für das Team
