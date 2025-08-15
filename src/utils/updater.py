from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import zipfile
from pathlib import Path
from typing import Any, Dict, Optional

import requests

from .utils import config
from .utils.logger import get_logger

# Konfiguration
GITHUB_REPO = "R0bes/Mauscribe"  # GitHub-Repository für Mauscribe
CURRENT_VERSION = "1.0.0"  # Aktuelle Version
UPDATE_CHECK_INTERVAL = 24 * 60 * 60  # 24 Stunden in Sekunden
USER_AGENT = "Mauscribe-Updater/1.0"


class UpdateInfo:
    """Container für Update-Informationen."""

    def __init__(
        self,
        version: str,
        download_url: str,
        release_notes: str,
        prerelease: bool = False,
    ):
        self.version = version
        self.download_url = download_url
        self.release_notes = release_notes
        self.prerelease = prerelease
        self.download_size = 0
        self.published_at = ""
        self.download_path: Path | None = None

    def __str__(self) -> str:
        return f"Update {self.version} ({'Pre-release' if self.prerelease else 'Stable'})"


class AutoUpdater:
    """
    Automatischer Update-Checker und Installer für Mauscribe.

    Funktionalitäten:
    - Regelmäßige Prüfung auf GitHub Updates
    - Download von Updates
    - Automatische Installation
    - Rollback bei Fehlern
    """

    def __init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__)

        self._enabled = getattr(config, "auto_update_enabled", False)
        self._check_interval = getattr(config, "auto_update_check_interval", None) or UPDATE_CHECK_INTERVAL
        self._last_check: float = 0.0
        self._update_thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._is_checking = False
        self._current_version = CURRENT_VERSION

        if self._enabled:
            self._start_update_thread()

    def _start_update_thread(self) -> None:
        """Startet den Update-Check-Thread."""
        if self._update_thread and self._update_thread.is_alive():
            return

        self._update_thread = threading.Thread(target=self._update_check_loop, daemon=True, name="Mauscribe-Updater")
        self._update_thread.start()
        self.logger.info("Auto-Updater Thread gestartet")

    def _update_check_loop(self) -> None:
        """Hauptschleife für Update-Checks."""
        while not self._stop_event.is_set():
            try:
                # Warte bis zum nächsten Check
                time.sleep(self._check_interval)

                if self._stop_event.is_set():
                    break

                # Update-Check durchführen
                self._check_for_updates_silent()

            except Exception as e:
                self.logger.error(f"Fehler im Update-Check-Thread: {e}")
                time.sleep(60)  # Kurze Pause bei Fehlern

    def _check_for_updates_silent(self) -> None:
        """Führt einen stillen Update-Check durch."""
        try:
            update_info = self._fetch_latest_release()
            if update_info and self._is_newer_version(update_info.version):
                self.logger.info(f"Neues Update verfügbar: {update_info.version}")
                # Hier könnte eine Benachrichtigung gesendet werden

        except Exception as e:
            self.logger.error(f"Stiller Update-Check fehlgeschlagen: {e}")

    def check_for_updates(self, force: bool = False) -> UpdateInfo | None:
        """
        Prüft manuell auf Updates.

        Args:
            force: Ignoriert den Zeitabstand und prüft sofort

        Returns:
            UpdateInfo wenn Update verfügbar, sonst None
        """
        if not self._enabled:
            self.logger.info("Auto-Updater ist deaktiviert")
            return None

        if not force and time.time() - self._last_check < self._check_interval:
            remaining = self._check_interval - (time.time() - self._last_check)
            self.logger.info(f"Update-Check erst in {int(remaining / 60)} Minuten verfügbar")
            return None

        try:
            self._is_checking = True
            self.logger.info("Prüfe auf Updates...")

            update_info = self._fetch_latest_release()
            self._last_check = time.time()

            if update_info and self._is_newer_version(update_info.version):
                self.logger.info(f"✅ Update verfügbar: {update_info.version}")
                self.logger.info(f"📝 Release Notes: {update_info.release_notes[:100]}...")
                return update_info
            else:
                self.logger.info("✅ Keine Updates verfügbar")
                return None

        except Exception as e:
            self.logger.error(f"❌ Update-Check fehlgeschlagen: {e}")
            return None
        finally:
            self._is_checking = False

    def _fetch_latest_release(self) -> UpdateInfo | None:
        """Holt die neueste Release-Information von GitHub."""
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            headers = {
                "User-Agent": USER_AGENT,
                "Accept": "application/vnd.github.v3+json",
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Assets durchsuchen (nach .exe oder .zip)
            download_url = None
            for asset in data.get("assets", []):
                if asset["name"].endswith((".exe", ".zip")):
                    download_url = asset["browser_download_url"]
                    break

            if not download_url:
                self.logger.warning("Keine passende Download-Datei gefunden")
                return None

            update_info = UpdateInfo(
                version=data["tag_name"].lstrip("v"),
                download_url=download_url,
                release_notes=data.get("body", "Keine Release Notes verfügbar"),
                prerelease=data.get("prerelease", False),
            )

            return update_info

        except Exception as e:
            self.logger.error(f"Fehler beim Update-Check: {e}")
            return None

    def _is_newer_version(self, new_version: str) -> bool:
        """Vergleicht Versionen."""
        if not new_version:
            return False

        try:
            current_parts = [int(x) for x in self._current_version.split(".")]
            new_parts = [int(x) for x in new_version.split(".")]

            # Padding für ungleiche Längen
            max_len = max(len(current_parts), len(new_parts))
            current_parts.extend([0] * (max_len - len(current_parts)))
            new_parts.extend([0] * (max_len - len(new_parts)))

            return new_parts > current_parts

        except (ValueError, AttributeError):
            # Fallback: String-Vergleich
            if new_version and self._current_version:
                return new_version > self._current_version
            return False

    def download_update(self, update_info: UpdateInfo, progress_callback=None) -> bool:
        """
        Lädt ein Update herunter.

        Args:
            update_info: Update-Informationen
            progress_callback: Callback für Fortschrittsanzeige

        Returns:
            True wenn Download erfolgreich
        """
        try:
            self.logger.info(f"Lade Update {update_info.version} herunter...")

            # Temporäres Verzeichnis erstellen
            temp_dir = Path(tempfile.mkdtemp(prefix="mauscribe_update_"))
            download_path = temp_dir / f"mauscribe_update_{update_info.version}.zip"

            # Download mit Fortschrittsanzeige
            response = requests.get(update_info.download_url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0

            with open(download_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        if progress_callback and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            progress_callback(progress)

            self.logger.info(f"✅ Download abgeschlossen: {download_path}")
            update_info.download_path = download_path
            return True

        except Exception as e:
            self.logger.error(f"❌ Download fehlgeschlagen: {e}")
            return False

    def install_update(self, update_info: UpdateInfo) -> bool:
        """
        Installiert ein heruntergeladenes Update.

        Args:
            update_info: Update-Informationen mit download_path

        Returns:
            True wenn Installation erfolgreich
        """
        if not hasattr(update_info, "download_path"):
            self.logger.error("❌ Kein Download-Pfad verfügbar")
            return False

        backup_path = None
        try:
            self.logger.info(f"Installiere Update {update_info.version}...")

            # Backup des aktuellen Programms erstellen
            backup_path = self._create_backup()

            # Update extrahieren und installieren
            current_exe = Path(sys.executable)
            if update_info.download_path and update_info.download_path.suffix == ".zip":
                self._install_from_zip(update_info.download_path, current_exe.parent)
            elif update_info.download_path:
                # Direkte .exe Installation
                shutil.copy2(update_info.download_path, current_exe)
            else:
                self.logger.error("❌ Kein Download-Pfad verfügbar")
                return False

            self.logger.info("✅ Update erfolgreich installiert!")
            self.logger.info("Das Programm wird neu gestartet...")

            # Neustart vorbereiten
            self._schedule_restart()
            return True

        except Exception as e:
            self.logger.error(f"❌ Installation fehlgeschlagen: {e}")
            if backup_path:
                self._rollback_update(backup_path)
            return False

    def _create_backup(self) -> Path:
        """Erstellt ein Backup des aktuellen Programms."""
        current_exe = Path(sys.executable)
        backup_dir = current_exe.parent / "backup"
        backup_dir.mkdir(exist_ok=True)

        backup_path = backup_dir / f"mauscribe_backup_{self._current_version}.exe"
        shutil.copy2(current_exe, backup_path)
        self.logger.info(f"Backup erstellt: {backup_path}")
        return backup_path

    def _install_from_zip(self, zip_path: Path, install_dir: Path) -> None:
        """Installiert ein Update aus einer ZIP-Datei."""
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            # Alle Dateien extrahieren
            zip_ref.extractall(install_dir)

            # Berechtigungen setzen
            for file_path in zip_ref.namelist():
                extracted_file = install_dir / file_path
                if extracted_file.is_file():
                    extracted_file.chmod(0o755)

    def _rollback_update(self, backup_path: Path) -> None:
        """Rollback bei fehlgeschlagener Installation."""
        try:
            self.logger.info("Führe Rollback durch...")
            current_exe = Path(sys.executable)
            shutil.copy2(backup_path, current_exe)
            self.logger.info("✅ Rollback erfolgreich")
        except Exception as e:
            self.logger.error(f"❌ Rollback fehlgeschlagen: {e}")

    def _schedule_restart(self) -> None:
        """Plant einen Neustart des Programms."""
        try:
            # Kurze Verzögerung für sauberes Beenden
            time.sleep(2)

            # Neustart über Batch-Datei
            restart_script = Path(tempfile.mktemp(suffix=".bat"))
            with open(restart_script, "w") as f:
                f.write("@echo off\n")
                f.write("timeout /t 2 /nobreak >nul\n")
                f.write(f'start "" "{sys.executable}"\n')
                f.write('del "%~f0"\n')

            # Batch-Datei ausführen
            subprocess.Popen([str(restart_script)], shell=True)

        except Exception as e:
            self.logger.error(f"Fehler beim Neustart: {e}")
            self.logger.warning("Bitte starten Sie das Programm manuell neu.")

    def get_status(self) -> dict[str, Any]:
        """Gibt den aktuellen Status des Updaters zurück."""
        return {
            "enabled": self._enabled,
            "is_checking": self._is_checking,
            "last_check": self._last_check,
            "next_check": self._last_check + self._check_interval,
            "current_version": self._current_version,
            "check_interval_hours": int(self._check_interval // 3600),
        }

    def stop(self) -> None:
        """Stoppt den Updater."""
        self._stop_event.set()
        if self._update_thread and self._update_thread.is_alive():
            self._update_thread.join(timeout=5)
        self.logger.info("Auto-Updater gestoppt")


# Globale Instanz
_updater_instance: AutoUpdater | None = None


def get_updater() -> AutoUpdater:
    """Gibt die globale AutoUpdater-Instanz zurück."""
    global _updater_instance
    if _updater_instance is None:
        _updater_instance = AutoUpdater()
    return _updater_instance


def check_for_updates(force: bool = False) -> UpdateInfo | None:
    """Convenience-Funktion für Update-Checks."""
    return get_updater().check_for_updates(force)


def stop_updater() -> None:
    """Stoppt den globalen Updater."""
    global _updater_instance
    if _updater_instance:
        _updater_instance.stop()
        _updater_instance = None
