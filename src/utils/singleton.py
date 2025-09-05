"""
System-weites Singleton für Mauscribe.
Verhindert, dass mehrere Instanzen gleichzeitig laufen.
"""

import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Optional

import psutil

from ..utils.logger import get_logger


class SystemWideSingleton:
    """
    System-weites Singleton für Mauscribe.

    Features:
    - Lock-Datei basierte Erkennung
    - Prozess-Überprüfung
    - Automatische Bereinigung toter Lock-Dateien
    - Graceful Fehlerbehandlung
    - Benachrichtigungen bei bereits laufender Instanz
    """

    def __init__(self, app_name: str = "mauscribe"):
        """Initialisiere das System-weite Singleton."""
        self.app_name = app_name
        self.logger = get_logger("SystemWideSingleton")

        # Lock-Datei Pfad
        self.lock_file = self._get_lock_file_path()
        self.lock_file_handle: Optional[int] = None

        # Prozess-ID für Lock-Datei
        self.pid = os.getpid()

        self.logger.debug(f"System-weites Singleton initialisiert für {app_name}")

    def _get_lock_file_path(self) -> Path:
        """Ermittle den Pfad für die Lock-Datei."""
        # Verwende temp-Verzeichnis für Lock-Datei
        temp_dir = Path(tempfile.gettempdir())
        lock_file = temp_dir / f"{self.app_name}.lock"
        return lock_file

    def acquire(self) -> bool:
        """
        Versuche das System-weite Lock zu erwerben.

        Returns:
            True wenn erfolgreich, False wenn bereits eine Instanz läuft
        """
        try:
            # Prüfe zuerst, ob Lock-Datei existiert
            if self.lock_file.exists():
                self.logger.debug(f"Lock-Datei gefunden: {self.lock_file}")

                # Versuche Lock-Datei zu lesen
                try:
                    with open(self.lock_file, "r") as f:
                        stored_pid = f.read().strip()

                    if stored_pid:
                        pid = int(stored_pid)
                        self.logger.debug(f"Gespeicherte PID: {pid}")

                        # Prüfe, ob Prozess noch läuft
                        if self._is_process_running(pid):
                            self.logger.warning(
                                f"[WARNING] Mauscribe läuft bereits (PID: {pid})"
                            )
                            # Zeige Benachrichtigung an
                            self._show_already_running_notification(pid)
                            return False
                        else:
                            self.logger.debug(
                                f"Toter Prozess gefunden (PID: {pid}) - bereinige Lock-Datei"
                            )
                            self._cleanup_dead_lock()
                except (ValueError, IOError) as e:
                    self.logger.warning(f"Fehler beim Lesen der Lock-Datei: {e}")
                    self._cleanup_dead_lock()

            # Erstelle neue Lock-Datei
            try:
                # Erstelle Lock-Datei mit exklusivem Zugriff
                self.lock_file_handle = os.open(
                    self.lock_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY
                )

                # Schreibe aktuelle PID
                os.write(self.lock_file_handle, str(self.pid).encode())
                os.fsync(self.lock_file_handle)

                self.logger.debug(f"[SUCCESS] System-weites Lock erworben (PID: {self.pid})")
                return True

            except OSError as e:
                if e.errno == 17:  # File exists
                    self.logger.warning("[WARNING] Lock-Datei wurde zwischenzeitlich erstellt")
                    return False
                else:
                    self.logger.error(f"Fehler beim Erstellen der Lock-Datei: {e}")
                    return False

        except Exception as e:
            self.logger.error(f"Unerwarteter Fehler beim Lock-Erwerb: {e}")
            return False

    def _show_already_running_notification(self, running_pid: int) -> None:
        """
        Zeige eine Benachrichtigung an, dass die Anwendung bereits läuft.
        
        Args:
            running_pid: Die PID der bereits laufenden Instanz
        """
        try:
            # Versuche NotificationManager zu importieren und zu verwenden
            from ..ui.notifications import NotificationManager
            
            # Erstelle eine temporäre NotificationManager-Instanz
            notification_manager = NotificationManager()
            
            # Zeige Benachrichtigung an
            notification_manager.show_warning(
                f"Mauscribe läuft bereits (PID: {running_pid})",
                "Anwendung bereits gestartet"
            )
            
            self.logger.info(f"[INFO] Benachrichtigung angezeigt: Mauscribe läuft bereits (PID: {running_pid})")
            
        except ImportError:
            # Fallback: Nur Logging, wenn NotificationManager nicht verfügbar
            self.logger.warning(f"NotificationManager nicht verfügbar - nur Logging")
        except Exception as e:
            # Fallback bei Fehlern
            self.logger.error(f"Fehler beim Anzeigen der Benachrichtigung: {e}")

    def release(self) -> None:
        """Gib das System-weite Lock frei."""
        try:
            if self.lock_file_handle is not None:
                os.close(self.lock_file_handle)
                self.lock_file_handle = None

            if self.lock_file.exists():
                try:
                    os.unlink(self.lock_file)
                    self.logger.debug("[SUCCESS] System-weites Lock freigegeben")
                except OSError as e:
                    self.logger.warning(f"Fehler beim Löschen der Lock-Datei: {e}")

        except Exception as e:
            self.logger.error(f"Fehler beim Freigeben des Locks: {e}")

    def _is_process_running(self, pid: int) -> bool:
        """Prüfe, ob ein Prozess mit der gegebenen PID läuft."""
        try:
            process = psutil.Process(pid)
            return process.is_running()
        except psutil.NoSuchProcess:
            return False
        except Exception as e:
            self.logger.warning(f"Fehler beim Prüfen des Prozesses {pid}: {e}")
            return False

    def _cleanup_dead_lock(self) -> None:
        """Bereinige tote Lock-Datei."""
        try:
            if self.lock_file.exists():
                os.unlink(self.lock_file)
                self.logger.debug("Tote Lock-Datei bereinigt")
        except OSError as e:
            self.logger.warning(f"Fehler beim Bereinigen der Lock-Datei: {e}")

    def is_running(self) -> bool:
        """Prüfe, ob bereits eine Instanz läuft."""
        if not self.lock_file.exists():
            return False

        try:
            with open(self.lock_file, "r") as f:
                stored_pid = f.read().strip()

            if stored_pid:
                pid = int(stored_pid)
                return self._is_process_running(pid)
        except (ValueError, IOError):
            pass

        return False

    def get_running_pid(self) -> Optional[int]:
        """Ermittle die PID der laufenden Instanz."""
        if not self.lock_file.exists():
            return None

        try:
            with open(self.lock_file, "r") as f:
                stored_pid = f.read().strip()

            if stored_pid:
                pid = int(stored_pid)
                if self._is_process_running(pid):
                    return pid
        except (ValueError, IOError):
            pass

        return None
