#!/usr/bin/env python3
"""
Version Update Script für Mauscribe
Aktualisiert die Version in pyproject.toml und anderen relevanten Dateien
"""

import re
import sys
import toml
from datetime import datetime
from pathlib import Path


def update_pyproject_toml(version: str) -> None:
    """Aktualisiert die Version in pyproject.toml"""
    print(f"📋 Aktualisiere pyproject.toml auf Version {version}")
    
    # Lade pyproject.toml
    with open("pyproject.toml", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Ersetze Version
    content = re.sub(
        r'version = "[\d\.]+"',
        f'version = "{version}"',
        content
    )
    
    # Schreibe zurück
    with open("pyproject.toml", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ pyproject.toml aktualisiert")


def update_changelog(version: str) -> None:
    """Aktualisiert das CHANGELOG.md"""
    print(f"📋 Aktualisiere CHANGELOG.md für Version {version}")
    
    changelog_path = Path("CHANGELOG.md")
    if not changelog_path.exists():
        print("⚠️  CHANGELOG.md nicht gefunden, überspringe...")
        return
    
    with open(changelog_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Ersetze [Unreleased] mit der neuen Version
    today = datetime.now().strftime("%Y-%m-%d")
    new_version_section = f"""## [{version}] - {today}

### ✨ Neu
- Neue Features und Verbesserungen

### 🛠️ Verbessert
- Performance-Optimierungen
- Code-Qualität verbessert

### 🐛 Behoben
- Bugfixes und Korrekturen

### 🔧 Technisch
- Technische Verbesserungen

## [Unreleased]

### Geplant
- Weitere Features und Verbesserungen
- Performance-Optimierungen
- Zusätzliche Sprachunterstützung

"""
    
    content = content.replace("## [Unreleased]\n", new_version_section)
    
    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ CHANGELOG.md aktualisiert")


def update_main_py(version: str) -> None:
    """Aktualisiert die Version in main.py falls vorhanden"""
    print(f"📋 Prüfe main.py auf Versionsreferenzen...")
    
    main_path = Path("main.py")
    if not main_path.exists():
        print("⚠️  main.py nicht gefunden, überspringe...")
        return
    
    with open(main_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Suche nach VERSION = "x.y.z" Pattern
    version_pattern = r'VERSION\s*=\s*["\'][\d\.]+["\']'
    if re.search(version_pattern, content):
        content = re.sub(version_pattern, f'VERSION = "{version}"', content)
        
        with open(main_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ main.py aktualisiert")
    else:
        print("ℹ️  Keine VERSION-Variable in main.py gefunden")


def validate_version(version: str) -> bool:
    """Validiert das Versionsformat (Semantic Versioning)"""
    pattern = r'^\d+\.\d+\.\d+$'
    if not re.match(pattern, version):
        print(f"❌ Ungültiges Versionsformat: {version}")
        print("   Erwartetes Format: X.Y.Z (z.B. 1.0.0)")
        return False
    return True


def main():
    """Hauptfunktion"""
    if len(sys.argv) != 2:
        print("❌ Verwendung: python scripts/update_version.py <VERSION>")
        print("   Beispiel: python scripts/update_version.py 1.0.1")
        sys.exit(1)
    
    version = sys.argv[1]
    
    print(f"🚀 Aktualisiere Mauscribe auf Version {version}")
    print("=" * 50)
    
    # Validiere Version
    if not validate_version(version):
        sys.exit(1)
    
    try:
        # Aktualisiere Dateien
        update_pyproject_toml(version)
        update_changelog(version)
        update_main_py(version)        
    except Exception as e:
        print(f"❌ Fehler beim Aktualisieren der Version: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
