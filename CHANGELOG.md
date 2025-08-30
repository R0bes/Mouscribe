# Changelog

Alle wichtigen Änderungen an Mauscribe werden in dieser Datei dokumentiert.

## [Unreleased]

### Geplant
- Weitere Features und Verbesserungen
- Performance-Optimierungen
- Zusätzliche Sprachunterstützung

## [1.0.0] - 2025-08-26

### ✨ Neu
- Automatische Release-Erstellung
- Verbesserte Audio-Speicherung mit Komprimierung
- Cross-Platform Builds (Windows, Linux, macOS)
- GitHub Actions CI/CD Pipeline
- Release-Management-Skripte

### 🛠️ Verbessert
- Build-Prozess optimiert
- Fehlerbehandlung verbessert
- Debug-Logging erweitert
- Konfigurationsverwaltung

### 🐛 Behoben
- Audio-Speicherung funktioniert jetzt korrekt
- Zwischenablage-Integration repariert
- Git-Hooks bereinigt
- Pre-Commit-Checks funktionieren

### 🔧 Technisch
- PyInstaller-Integration
- Automatische Verzeichnis-Erstellung
- Robuste Fallback-Mechanismen
- Plattformübergreifende Kompatibilität

---

## Versionierung

Dieses Projekt folgt [Semantic Versioning](https://semver.org/):

- **MAJOR**: Inkompatible API-Änderungen
- **MINOR**: Neue Features (rückwärtskompatibel)
- **PATCH**: Bugfixes (rückwärtskompatibel)

## Release-Prozess

1. **Patch-Release**: `make release-patch`
2. **Minor-Release**: `make release-minor`
3. **Major-Release**: `make release-major`
4. **Custom-Release**: `make release VERSION=X.Y.Z`

## Automatisierung

- GitHub Actions erstellt automatisch Releases bei Git-Tags
- Cross-Platform Builds für alle unterstützten Betriebssysteme
- Automatische Asset-Uploads zu GitHub Releases
- Release Notes werden automatisch generiert
