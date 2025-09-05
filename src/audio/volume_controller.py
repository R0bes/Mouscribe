from __future__ import annotations

from ctypes import POINTER, cast
from typing import Any

from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

from ..utils.logger import get_logger


class VolumeController:
    """
    Volume-Control für Mauscribe als Singleton.
    
    Features:
    - Automatische Lautstärke-Reduzierung während der Aufnahme
    - Wiederherstellung der ursprünglichen Lautstärke
    - Robuste Fehlerbehandlung
    - Verifikation der Lautstärke-Änderungen
    - Singleton-Pattern mit Referenzzähler für Multitasking
    """

    _instance: VolumeController | None = None
    _lock = None

    def __new__(cls, target: float = 0.1) -> VolumeController:
        """Singleton-Pattern: Nur eine Instanz erlauben."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, target: float = 0.1) -> None:
        """Initialisiere den Volume-Controller (nur einmal)."""
        if self._initialized:
            return
            
        self.logger = get_logger(self.__class__.__name__)

        # Audio-Interface initialisieren
        self._volume_interface: Any | None = None
        self._system_volume: float | None = None
        self._original_volume: float | None = None  # Speichert die echte ursprüngliche Lautstärke
        self._target_volume = target
        
        # Referenzzähler für Multitasking
        self._reference_count = 0
        self._volume_reduced = False
        
        # Threading-Lock für Thread-Sicherheit
        import threading
        if VolumeController._lock is None:
            VolumeController._lock = threading.Lock()
        
        self._setup_audio_interface()
        self._initialized = True

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

    def set_original_volume(self, volume: float) -> None:
        """Setze die ursprüngliche Lautstärke manuell (für Debugging)."""
        with self._lock:
            self._original_volume = volume
            self.logger.debug(f"Ursprüngliche Lautstärke manuell gesetzt auf: {volume:.2f}")

    def _get_current_volume(self) -> float | None:
        """Get current system volume level."""
        if not self._volume_interface:
            return None
        
        try:
            volume = self._volume_interface.GetMasterVolumeLevelScalar()
            return volume
        except Exception as e:
            self.logger.warning(f"Fehler beim Abrufen der aktuellen Lautstärke: {e}")
            return None

    def _set_volume_with_verification(self, target_volume: float, operation: str) -> bool:
        """Set volume and verify the change was applied."""
        if not self._volume_interface:
            self.logger.debug("Kein Lautstärke-Interface verfügbar")
            return False

        try:
            # Get volume before change
            volume_before = self._get_current_volume()
            if volume_before is None:
                self.logger.warning(f"Konnte Lautstärke vor {operation} nicht abrufen")
                return False

            # Set new volume
            self._volume_interface.SetMasterVolumeLevelScalar(target_volume, None)
            
            # Wait a moment for the change to take effect
            import time
            time.sleep(0.1)
            
            # Verify the change
            volume_after = self._get_current_volume()
            if volume_after is None:
                self.logger.warning(f"Konnte Lautstärke nach {operation} nicht abrufen")
                return False

            # Check if change was successful (allow small tolerance)
            tolerance = 0.05
            if abs(volume_after - target_volume) <= tolerance:
                self.logger.debug(f"✅ {operation} erfolgreich: {volume_before:.2f} → {volume_after:.2f}")
                return True
            else:
                self.logger.warning(f"⚠️ {operation} fehlgeschlagen: erwartet {target_volume:.2f}, tatsächlich {volume_after:.2f}")
                return False

        except Exception as e:
            self.logger.error(f"Fehler bei {operation}: {e}")
            return False

    def acquire(self) -> None:
        """Erhöhe den Referenzzähler und reduziere Lautstärke bei Bedarf."""
        with self._lock:
            self._reference_count += 1
            self.logger.debug(f"Volume Controller Referenz erhöht: {self._reference_count}")
            
            # Reduziere Lautstärke nur beim ersten Aufruf
            if self._reference_count == 1:
                self._reduce_volume_internal()

    def release(self) -> None:
        """Verringere den Referenzzähler und stelle Lautstärke bei Bedarf wieder her."""
        with self._lock:
            if self._reference_count > 0:
                self._reference_count -= 1
                self.logger.debug(f"Volume Controller Referenz verringert: {self._reference_count}")
                
                # Stelle Lautstärke nur beim letzten Aufruf wieder her
                if self._reference_count == 0:
                    self._restore_volume_internal()

    def release_all(self) -> None:
        """Finale Volume-Wiederherstellung beim Graceful Shutdown."""
        with self._lock:
            if self._reference_count > 0:
                self.logger.debug(f"Volume-Restore-All: Setze {self._reference_count} Referenzen zurück")
                self._reference_count = 0
                
                # Stelle Lautstärke sicher wieder her
                if self._volume_reduced:
                    self.logger.debug("Volume-Restore-All: Stelle System-Lautstärke wieder her...")
                    success = self._restore_volume_internal()
                    if success:
                        self.logger.debug("✅ Volume-Restore-All: Lautstärke erfolgreich wiederhergestellt")
                    else:
                        self.logger.warning("⚠️ Volume-Restore-All: Lautstärke konnte nicht wiederhergestellt werden")
                else:
                    self.logger.debug("Volume-Restore-All: Keine Lautstärke-Reduzierung erkannt - überspringe Wiederherstellung")
            else:
                self.logger.debug("Volume-Restore-All: Keine aktiven Referenzen - überspringe")

    def _reduce_volume_internal(self) -> bool:
        """
        Interne Methode zur Lautstärke-Reduzierung (nur einmal aufgerufen).
        Returns:
            True wenn erfolgreich, False sonst
        """
        if not self._volume_interface:
            self.logger.debug("Kein Lautstärke-Interface verfügbar - überspringe Lautstärke-Änderung")
            return False

        if self._volume_reduced:
            self.logger.debug("Lautstärke bereits reduziert - überspringe")
            return True

        try:
            # Aktuelle System-Lautstärke speichern (nur wenn noch nicht gespeichert)
            if self._system_volume is None:
                current_volume = self._get_current_volume()
                if current_volume is None:
                    self.logger.warning("Konnte aktuelle Lautstärke nicht abrufen")
                    return False
                
                # Prüfe, ob die aktuelle Lautstärke bereits nahe am Zielwert ist
                if abs(current_volume - self._target_volume) < 0.05:
                    self.logger.warning(f"Lautstärke ist bereits bei {current_volume:.2f} (Ziel: {self._target_volume:.2f})")
                    if self._original_volume is not None:
                        self.logger.debug(f"Verwende manuell gesetzte ursprüngliche Lautstärke: {self._original_volume:.2f}")
                        self._system_volume = self._original_volume
                    else:
                        self.logger.warning("Keine ursprüngliche Lautstärke verfügbar - überspringe Reduzierung")
                        return False
                else:
                    self._system_volume = current_volume
                    self.logger.debug(f"Originale Lautstärke gespeichert: {self._system_volume:.2f}")

            # Lautstärke auf Zielwert reduzieren
            success = self._set_volume_with_verification(self._target_volume, "Lautstärke-Reduzierung")
            if success:
                self._volume_reduced = True
                self.logger.debug(f"Lautstärke reduziert von {self._system_volume:.2f} auf {self._target_volume:.2f}")
            else:
                self.logger.warning("Lautstärke-Reduzierung fehlgeschlagen")
            return success

        except Exception as e:
            self.logger.warning(f"Fehler beim Ändern der Lautstärke: {e}")
            return False

    def _restore_volume_internal(self) -> bool:
        """
        Interne Methode zur Lautstärke-Wiederherstellung (nur einmal aufgerufen).
        Returns:
            True wenn erfolgreich, False sonst
        """
        if not self._volume_interface:
            self.logger.debug("Kein Lautstärke-Interface verfügbar")
            return False

        if not self._volume_reduced:
            self.logger.debug("Lautstärke wurde nicht reduziert - überspringe Wiederherstellung")
            return True

        if self._system_volume is None:
            self.logger.debug("Keine ursprüngliche Lautstärke gespeichert - überspringe Wiederherstellung")
            return False

        try:
            success = self._set_volume_with_verification(self._system_volume, "Lautstärke-Wiederherstellung")
            if success:
                self.logger.debug(f"Lautstärke wiederhergestellt auf {self._system_volume:.2f}")
                # Reset the stored volume after successful restoration
                self._system_volume = None
                self._volume_reduced = False
            else:
                self.logger.warning("Lautstärke-Wiederherstellung fehlgeschlagen")
            return success

        except Exception as e:
            self.logger.error(f"Fehler beim Wiederherstellen der Lautstärke: {e}")
            return False

    def reduce_volume(self) -> bool:
        """
        Reduziere die System-Lautstärke (veraltet - verwende acquire()).
        Returns:
            True wenn erfolgreich, False sonst
        """
        self.logger.warning("reduce_volume() ist veraltet - verwende acquire()")
        self.acquire()
        return self._volume_reduced

    def restore_volume(self) -> bool:
        """
        Stelle die ursprüngliche System-Lautstärke wieder her (veraltet - verwende release()).
        Returns:
            True wenn erfolgreich, False sonst
        """
        self.logger.warning("restore_volume() ist veraltet - verwende release()")
        self.release()
        return not self._volume_reduced

    def cleanup(self) -> None:
        """Sauberes Aufräumen beim Beenden."""
        try:
            # Stelle Lautstärke sicher wieder her
            self.release_all()
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Aufräumen des Volume-Controllers: {e}")

    def get_volume_info(self) -> dict[str, Any]:
        """Get current volume information for debugging."""
        current_volume = self._get_current_volume()
        return {
            "current_volume": current_volume,
            "stored_volume": self._system_volume,
            "original_volume": self._original_volume,
            "target_volume": self._target_volume,
            "interface_available": self._volume_interface is not None,
            "reference_count": self._reference_count,
            "volume_reduced": self._volume_reduced
        }
