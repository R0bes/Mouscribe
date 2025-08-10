# Contributing to Mauscribe

Vielen Dank, dass du zu Mauscribe beitragen möchtest! 🎉

## 🚀 Quick Start

### 1. Repository klonen
```bash
git clone https://github.com/R0bes/Mauscribe.git
cd Mauscribe
```

### 2. Entwicklungsumgebung einrichten
```bash
# Virtual Environment erstellen
python -m venv .venv

# Aktivieren (Windows)
.venv\Scripts\activate

# Aktivieren (Linux/macOS)
source .venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. Feature Branch erstellen
```bash
# Neuen Feature Branch erstellen
git checkout -b feature/mein-feature

# Oder Bugfix Branch
git checkout -b bugfix/mein-bugfix

# Oder Hotfix Branch
git checkout -b hotfix/kritischer-fix
```

## 📋 Entwicklungsrichtlinien

### Git Workflow
- **Main Branch**: Nur für stabile Releases
- **Develop Branch**: Integration von Features
- **Feature Branches**: `feature/feature-name`
- **Bugfix Branches**: `bugfix/bug-description`
- **Hotfix Branches**: `hotfix/critical-fix`

### Commit Messages
Verwende [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: neue Funktion hinzugefügt
fix: Bug in der Audio-Aufnahme behoben
docs: README aktualisiert
style: Code-Formatierung korrigiert
refactor: Audio-Controller umstrukturiert
test: Unit Tests für SpellChecker hinzugefügt
chore: Dependencies aktualisiert
```

### Code Style
- **Python**: PEP 8, max. 127 Zeilen
- **Linting**: flake8, black
- **Tests**: pytest mit Coverage
- **Typing**: Type Hints verwenden

## 🧪 Testing

### Tests ausführen
```bash
# Alle Tests
pytest

# Mit Coverage
pytest --cov=src --cov-report=html

# Spezifische Tests
pytest tests/test_recorder.py

# Linting
flake8 src/
black --check src/
```

### Test Coverage
- Ziel: Mindestens 80% Coverage
- Neue Features müssen Tests haben
- Bugfixes müssen Regression-Tests haben

## 🔧 Entwicklung

### Projektstruktur
```
src/
├── __init__.py
├── main.py              # Hauptanwendung
├── config.py            # Konfigurationsmanagement
├── input_handler.py     # Eingabe-Behandlung
├── recorder.py          # Audio-Aufnahme
├── stt.py              # Speech-to-Text
├── sound_controller.py  # Audio-Steuerung
├── spell_checker.py    # Rechtschreibprüfung
└── updater.py          # Update-System
```

### Neue Features hinzufügen
1. Feature Branch erstellen
2. Code implementieren
3. Tests schreiben
4. Dokumentation aktualisieren
5. Linting-Checks bestehen
6. Pull Request erstellen

### Konfiguration
- Änderungen in `config.toml` dokumentieren
- Standardwerte in `src/config.py` definieren
- Neue Konfigurationsoptionen in README erklären

## 📚 Dokumentation

### Code-Dokumentation
- Docstrings für alle Funktionen
- Type Hints verwenden
- Kommentare für komplexe Logik

### README aktualisieren
- Neue Features dokumentieren
- Konfigurationsoptionen erklären
- Screenshots bei UI-Änderungen

## 🚀 Pull Request erstellen

### Vor dem PR
- [ ] Alle Tests laufen erfolgreich
- [ ] Linting-Checks bestanden
- [ ] Dokumentation aktualisiert
- [ ] Changelog aktualisiert

### PR Template verwenden
- Beschreibung der Änderungen
- Verwandte Issues verlinken
- Screenshots bei UI-Änderungen
- Testanweisungen

## 🔍 Code Review

### Review-Prozess
1. Automatische Tests müssen bestehen
2. Mindestens 1 Reviewer muss zustimmen
3. Alle Review-Kommentare müssen adressiert werden
4. Squash-Merge nach dem Review

### Review-Kriterien
- Code-Qualität und Lesbarkeit
- Test-Coverage
- Dokumentation
- Performance-Aspekte
- Sicherheitsaspekte

## 🐛 Bug Reports

### Bug melden
- Verwende das Bug Report Template
- Beschreibe den Fehler genau
- Füge Schritte zur Reproduktion hinzu
- System-Informationen angeben

### Bug fixen
- Reproduzierbare Test-Cases schreiben
- Root Cause identifizieren
- Regression-Tests hinzufügen
- Changelog aktualisieren

## 🎯 Release-Prozess

### Versionierung
- [Semantic Versioning](https://semver.org/)
- `MAJOR.MINOR.PATCH`
- Changelog für jede Version

### Release erstellen
1. Version in `pyproject.toml` aktualisieren
2. Changelog aktualisieren
3. Release auf GitHub erstellen
4. Executables hochladen

## 🤝 Community

### Kommunikation
- Issues für Diskussionen verwenden
- Pull Requests für Code-Änderungen
- GitHub Discussions für Fragen

### Hilfe bekommen
- Dokumentation lesen
- Issues durchsuchen
- GitHub Discussions nutzen
- Discord/Community-Kanäle

## 📄 Lizenz

Durch deinen Beitrag stimmst du zu, dass dein Code unter der MIT-Lizenz veröffentlicht wird.

---

**Vielen Dank für deinen Beitrag! 🎉**

Bei Fragen oder Problemen, erstelle einfach ein Issue oder kontaktiere uns.
