# Mauscribe Test Suite

Diese Testbibliothek für Mauscribe bietet eine solide Grundlage für Unit-Tests und Integration-Tests.

## Struktur

```
tests/
├── __init__.py                 # Test-Paket-Initialisierung
├── conftest.py                 # Pytest-Konfiguration und Fixtures
├── utils.py                    # Test-Utilities und Hilfsfunktionen
├── README.md                   # Diese Datei
├── unit/                       # Unit-Tests
│   ├── __init__.py
│   ├── test_config.py          # Tests für Config-Klasse
│   └── test_logger.py          # Tests für Logger-System
└── integration/                # Integration-Tests
    ├── __init__.py
    └── test_app_initialization.py  # Tests für App-Initialisierung
```

## Features

### Konfiguration (conftest.py)
- **Test-Config**: Automatische Test-Konfiguration mit deaktivierten Features
- **Mock-Fixtures**: Vorgefertigte Mocks für alle Hauptkomponenten
- **Temporäre Dateien**: Automatische Erstellung und Bereinigung
- **Custom Markers**: Pytest-Marker für verschiedene Test-Typen

### Test-Utilities (utils.py)
- **Audio-Dateien**: Erstellung temporärer WAV-Dateien für Tests
- **Konfigurationsdateien**: Dynamische TOML-Konfigurationen
- **Wörterbuch-Dateien**: JSON-Wörterbücher für Tests
- **Validierung**: Assertion-Funktionen für Dateivalidierung
- **Mock-Klassen**: Mock-Implementierungen für Audio und Transkription

### Unit-Tests
- **Config-Tests**: Vollständige Tests der Konfigurationsklasse
- **Logger-Tests**: Tests für das Logger-System mit Emoji-Support

### Integration-Tests
- **App-Initialisierung**: Tests für die Hauptanwendungsinitialisierung
- **Komponenten-Interaktion**: Tests für das Zusammenspiel der Komponenten

## Verwendung

### Tests ausführen

```bash
# Alle Tests
make test

# Nur Unit-Tests
pytest tests/unit/ -v

# Nur Integration-Tests
pytest tests/integration/ -v

# Tests mit Markern
pytest -m unit -v
pytest -m integration -v
pytest -m "not slow" -v  # Schnelle Tests auslassen
```

### Neue Tests hinzufügen

1. **Unit-Tests**: Erstellen Sie Dateien in `tests/unit/`
2. **Integration-Tests**: Erstellen Sie Dateien in `tests/integration/`
3. **Fixtures verwenden**: Nutzen Sie die vorgefertigten Fixtures aus `conftest.py`
4. **Utilities nutzen**: Verwenden Sie Hilfsfunktionen aus `tests/utils.py`

### Beispiel für einen neuen Test

```python
# tests/unit/test_new_component.py
import pytest
from unittest.mock import patch

class TestNewComponent:
    def test_component_initialization(self, test_config, mock_logger):
        """Test component initialization."""
        # Test-Implementierung hier
        pass
    
    @pytest.mark.slow
    def test_component_performance(self, test_config):
        """Test component performance (slow test)."""
        # Performance-Test hier
        pass
```

## Test-Marker

- `@pytest.mark.unit`: Unit-Tests
- `@pytest.mark.integration`: Integration-Tests
- `@pytest.mark.slow`: Langsame Tests
- `@pytest.mark.audio`: Tests, die Audio-Hardware benötigen
- `@pytest.mark.gui`: Tests, die GUI benötigen

## Best Practices

1. **Isolation**: Jeder Test sollte unabhängig von anderen sein
2. **Mocks verwenden**: Nutzen Sie Mocks für externe Abhängigkeiten
3. **Fixtures nutzen**: Verwenden Sie die vorgefertigten Fixtures
4. **Temporäre Dateien**: Nutzen Sie `temp_dir` Fixture für Datei-Tests
5. **Cleanup**: Bereinigen Sie temporäre Ressourcen nach Tests

## Erweiterung

Die Testbibliothek ist so konzipiert, dass sie einfach erweitert werden kann:

1. **Neue Fixtures**: Fügen Sie neue Fixtures zu `conftest.py` hinzu
2. **Neue Utilities**: Erweitern Sie `tests/utils.py` um neue Hilfsfunktionen
3. **Neue Test-Kategorien**: Erstellen Sie neue Ordner für spezielle Test-Typen
4. **Neue Marker**: Definieren Sie neue Pytest-Marker in `conftest.py`

## Abhängigkeiten

Die Tests verwenden folgende Python-Pakete:
- `pytest`: Test-Framework
- `numpy`: Für Audio-Daten-Generierung
- `wave`: Für WAV-Datei-Handling
- `unittest.mock`: Für Mocking

Diese sind bereits in `requirements-dev.txt` enthalten.
