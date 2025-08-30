#!/usr/bin/env python3
"""
Release-Skript für Mauscribe
Erstellt automatisch neue Versionen und Git-Tags
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Projekt-Root-Verzeichnis
PROJECT_ROOT = Path(__file__).parent.parent


def run_command(cmd: list[str], cwd: Optional[Path] = None) -> str:
    """Führt einen Befehl aus und gibt die Ausgabe zurück."""
    try:
        result = subprocess.run(cmd, cwd=cwd or PROJECT_ROOT, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Fehler beim Ausführen von {' '.join(cmd)}: {e}")
        print(f"Stderr: {e.stderr}")
        sys.exit(1)


def get_current_version() -> str:
    """Liest die aktuelle Version aus der Konfiguration."""
    config_file = PROJECT_ROOT / "config.toml"

    if not config_file.exists():
        print("❌ config.toml nicht gefunden!")
        sys.exit(1)

    with open(config_file, encoding="utf-8") as f:
        content = f.read()

    # Suche nach Version in der Konfiguration
    version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
    if version_match:
        return version_match.group(1)

    # Fallback: Standardversion
    return "1.0.0"


def update_version(new_version: str) -> None:
    """Aktualisiert die Version in der Konfiguration."""
    config_file = PROJECT_ROOT / "config.toml"

    with open(config_file, encoding="utf-8") as f:
        content = f.read()

    # Ersetze Version
    if re.search(r"version\s*=", content):
        content = re.sub(r'version\s*=\s*["\'][^"\']+["\']', f'version = "{new_version}"', content)
    else:
        # Füge Version hinzu, falls nicht vorhanden
        content = f'# Version\nversion = "{new_version}"\n\n{content}'

    with open(config_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Version in config.toml auf {new_version} aktualisiert")


def update_changelog(version: str, release_type: str) -> None:
    """Aktualisiert die CHANGELOG.md."""
    changelog_file = PROJECT_ROOT / "CHANGELOG.md"

    if not changelog_file.exists():
        # Erstelle neue CHANGELOG.md
        changelog_content = f"""# Changelog

Alle wichtigen Änderungen an Mauscribe werden in dieser Datei dokumentiert.

## [Unreleased]

### Geplant
- Weitere Features und Verbesserungen

## [{version}] - {get_current_date()}

### ✨ Neu
- Automatische Release-Erstellung
- Verbesserte Audio-Speicherung
- Cross-Platform Builds

### 🛠️ Verbessert
- Build-Prozess optimiert
- Fehlerbehandlung verbessert

### 🐛 Behoben
- Audio-Speicherung funktioniert jetzt korrekt
- Zwischenablage-Integration repariert

---
"""
    else:
        # Aktualisiere bestehende CHANGELOG.md
        with open(changelog_file, encoding="utf-8") as f:
            content = f.read()

        # Füge neue Version hinzu
        new_entry = f"""## [{version}] - {get_current_date()}

### ✨ Neu
- Automatische Release-Erstellung
- Verbesserte Audio-Speicherung
- Cross-Platform Builds

### 🛠️ Verbessert
- Build-Prozess optimiert
- Fehlerbehandlung verbessert

### 🐛 Behoben
- Audio-Speicherung funktioniert jetzt korrekt
- Zwischenablage-Integration repariert

"""

        # Ersetze [Unreleased] mit neuer Version
        content = content.replace("## [Unreleased]", new_entry + "## [Unreleased]")

        changelog_content = content

    with open(changelog_file, "w", encoding="utf-8") as f:
        f.write(changelog_content)

    print(f"✅ CHANGELOG.md für Version {version} aktualisiert")


def get_current_date() -> str:
    """Gibt das aktuelle Datum im ISO-Format zurück."""
    from datetime import datetime

    return datetime.now().strftime("%Y-%m-%d")


def create_git_tag(version: str, message: str) -> None:
    """Erstellt einen Git-Tag für die neue Version."""
    try:
        # Prüfe Git-Status
        status = run_command(["git", "status", "--porcelain"])
        if status:
            print("⚠️  Ungespeicherte Änderungen gefunden:")
            print(status)
            response = input("Möchten Sie trotzdem fortfahren? (y/N): ")
            if response.lower() != "y":
                print("❌ Release abgebrochen")
                sys.exit(0)

        # Commit alle Änderungen
        run_command(["git", "add", "."])
        run_command(["git", "commit", "-m", f"Release {version}: {message}"])

        # Push zum Remote
        run_command(["git", "push"])

        # Erstelle und pushe Tag
        run_command(["git", "tag", "-a", f"v{version}", "-m", f"Release {version}"])
        run_command(["git", "push", "origin", f"v{version}"])

        print("✅ Git-Tag v{} erstellt und gepusht".format(version))

    except Exception as e:
        print("❌ Fehler beim Git-Tag: {}".format(e))
        sys.exit(1)


def build_executable() -> None:
    """Baut die ausführbare Datei für Windows."""
    try:
        print("🔨 Baue Windows-Executable...")

        # Installiere PyInstaller falls nicht vorhanden
        try:
            import PyInstaller
        except ImportError:
            print("📦 Installiere PyInstaller...")
            run_command([sys.executable, "-m", "pip", "install", "pyinstaller"])

        # Baue Executable
        run_command(
            [
                sys.executable,
                "-m",
                "PyInstaller",
                "--onefile",
                "--windowed",
                "--name",
                "mauscribe",
                "--distpath",
                "dist",
                "--workpath",
                "build",
                "src/main.py",
            ]
        )

        print("✅ Windows-Executable erfolgreich gebaut")
        print("📁 Datei: {}".format(PROJECT_ROOT / 'dist' / 'mauscribe.exe'))

    except Exception as e:
        print("❌ Fehler beim Build: {}".format(e))
        print("⚠️  Build übersprungen, aber Release wird trotzdem erstellt")


def main():
    """Hauptfunktion des Release-Skripts."""
    parser = argparse.ArgumentParser(description="Erstellt einen neuen Mauscribe Release")
    parser.add_argument("version", help="Neue Versionsnummer (z.B. 1.0.0, 1.1.0, 2.0.0)")
    parser.add_argument("--type", choices=["patch", "minor", "major"], default="patch", help="Release-Typ (Standard: patch)")
    parser.add_argument("--message", default="", help="Zusätzliche Nachricht für den Release")
    parser.add_argument("--no-build", action="store_true", help="Überspringe den Build-Prozess")

    args = parser.parse_args()

    # Validiere Versionsnummer
    if not re.match(r"^\d+\.\d+\.\d+$", args.version):
        print("❌ Ungültige Versionsnummer! Verwende das Format X.Y.Z")
        sys.exit(1)

    current_version = get_current_version()
    print("🚀 Erstelle Release {} (aktuell: {})".format(args.version, current_version))

    # Aktualisiere Dateien
    update_version(args.version)
    update_changelog(args.version, args.type)

    # Baue Executable (falls gewünscht)
    if not args.no_build:
        build_executable()

    # Erstelle Git-Tag
    message = args.message or "Release {}".format(args.version)
    create_git_tag(args.version, message)

    print("\n🎉 Release {} erfolgreich erstellt!".format(args.version))
    print("📝 GitHub Actions wird automatisch den Release erstellen")
    print("🔗 Überprüfe: https://github.com/R0bes/Mauscribe/releases")

    if not args.no_build:
        print("📁 Windows-Executable: dist/mauscribe.exe")


if __name__ == "__main__":
    main()
