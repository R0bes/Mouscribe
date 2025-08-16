from __future__ import annotations

from ctypes import POINTER, cast
from typing import Any

from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

from ..utils.logger import get_logger


class VolumeController:
    """
    Volume-Control für Mauscribe.

    Features:
    - Automatische Lautstärke-Reduzierung während der Aufnahme
    - Wiederherstellung der ursprünglichen Lautstärke
    - Robuste Fehlerbehandlung
    """

    def __init__(self, target: float) -> None:
        """Initialisiere den Volume-Controller."""
        self.logger = get_logger(self.__class__.__name__)

        # Audio-Interface initialisieren
        self._volume_interface: Any | None = None
        self._system_volume: float | None = None
        self._setup_audio_interface()
        self._target_volume = target

    def _setup_audio_interface(self) -> None:
        """Setup audio interface for volume control."""
        try:
            # Get default audio device
            devices = AudioUtilities.GetSpeakers()
            if not devices:
                self.logger.warning("No audio devices found")
                self._volume_interface = None
                return

            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            if not interface:
                self.logger.error("Failed to activate audio interface")
                self._volume_interface = None
                return
            self._volume_interface = cast(interface, POINTER(IAudioEndpointVolume))

        except Exception as e:
            self.logger.error(f"Failed to initialize audio interface: {e}")
            self.logger.warning("Audio control will be disabled")
            self._volume_interface = None

    def reduce_volume(self) -> bool:
        """
        Reduziere die System-Lautstärke.
        Returns:
            True wenn erfolgreich, False sonst
        """
        if not self._volume_interface:
            self.logger.debug(
                "Kein Lautstärke-Interface verfügbar - überspringe Lautstärke-Änderung"
            )
            return False

        try:
            # Aktuelle System-Lautstärke speichern
            self._system_volume = self._volume_interface.GetMasterVolumeLevelScalar()
            # Lautstärke auf Zielwert reduzieren
            self._volume_interface.SetMasterVolumeLevelScalar(self._target_volume, None)
            self.logger.debug(
                f"Lautstärke reduziert von {self._system_volume:.2f} auf {self._target_volume:.2f}"
            )
            return True
        except Exception as e:
            self.logger.warning(f"Fehler beim Ändern der Lautstärke: {e}")
            self._system_volume = None
            return False

    def restore_volume(self) -> bool:
        """
        Stelle die ursprüngliche System-Lautstärke wieder her.

        Returns:
            True wenn erfolgreich, False sonst
        """
        if not self._volume_interface or self._system_volume is None:
            self.logger.debug(
                "Kein Lautstärke-Interface verfügbar oder keine ursprüngliche Lautstärke gespeichert"
            )
            return False

        try:
            self._volume_interface.SetMasterVolumeLevelScalar(self._system_volume, None)
            self.logger.debug(
                f"Lautstärke wiederhergestellt auf {self._system_volume:.2f}"
            )
            return True
        except Exception as e:
            self.logger.error(f"Fehler beim Wiederherstellen der Lautstärke: {e}")
            return False

    def cleanup(self) -> None:
        """Sauberes Aufräumen beim Beenden."""
        try:
            # Stelle Lautstärke sicher wieder her
            if self.restore_volume():
                self.logger.info("✅ Volume-Controller erfolgreich aufgeräumt")
            else:
                self.logger.warning(
                    "⚠️  Lautstärke konnte nicht wiederhergestellt werden"
                )
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Aufräumen des Volume-Controllers: {e}")
