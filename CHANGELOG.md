# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt folgt [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- GitHub Actions CI/CD Workflows
- Branch Protection für Main-Branch
- Pull Request und Issue Templates
- Contributing Guidelines
- Automatische Feature-Entwicklung Workflows

### Changed
- Repository-Struktur verbessert
- Dokumentation erweitert

## [1.0.0] - 2024-12-19

### Added
- 🎤 Voice-to-Text Funktionalität mit Whisper
- 🖱️ Push-to-Talk mit Maus-Buttons
- ⌨️ Keyboard-Shortcuts für Aufnahme
- 📋 Automatisches Clipboard-Management
- 🎵 Intelligente Lautstärke-Steuerung
- 🖥️ System Tray Integration
- 🔧 TOML-basierte Konfiguration
- ✍️ Rechtschreib- und Grammatikkorrektur
- 🔄 Auto-Updater System
- 🎯 Multi-Agent AI Workflow Support

### Features
- **Audio Recording**: High-Quality Aufnahme mit automatischer Lautstärke-Anpassung
- **Speech-to-Text**: Schnelle und genaue Transkription
- **Smart Input**: Intuitive Steuerung über Maus oder Tastatur
- **System Integration**: Hintergrund-Betrieb mit System Tray
- **Configuration**: Umfassende Anpassungsmöglichkeiten
- **Spell Checking**: Integrierte Rechtschreibprüfung
- **Auto-Paste**: Intelligentes Einfügen in aktive Fenster

### Technical
- Python 3.8+ Support
- Cross-Platform Kompatibilität
- Modularer Code-Architektur
- Umfassende Fehlerbehandlung
- Logging und Debug-Funktionen
- PyInstaller Build-System

## [0.9.0] - 2024-12-01

### Added
- Grundlegende Audio-Aufnahme
- Basis STT-Integration
- Einfache Maus-Button-Steuerung

### Changed
- Erste funktionsfähige Version

## [0.8.0] - 2024-11-15

### Added
- Projektstruktur
- Basis-Konfiguration
- Entwicklungsumgebung

---

## Versionsrichtlinien

- **MAJOR**: Breaking Changes, neue Hauptversionen
- **MINOR**: Neue Features, rückwärtskompatibel
- **PATCH**: Bugfixes, rückwärtskompatibel

## Migration

### Von 0.9.0 zu 1.0.0
- Neue Konfigurationsdatei `config.toml` erforderlich
- Einige Konfigurationsoptionen haben sich geändert
- Siehe [MIGRATION.md](docs/MIGRATION.md) für Details

---

**Hinweis**: Alle Änderungen vor Version 1.0.0 sind als Beta-Versionen zu betrachten.
