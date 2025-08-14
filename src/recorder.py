from __future__ import annotations

import threading
import time
from ctypes import POINTER, cast
from typing import Any, Dict, List, Optional

import numpy as np
import sounddevice as sd
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

from .config import Config
from .logger import get_logger


class AudioRecorder:
    """
    Einfacher und robuster Audio-Recorder für Mauscribe.

    Features:
    - Automatische Geräteauswahl
    - Thread-sichere Aufnahme
    - Einfache API
    - Robuste Fehlerbehandlung
    """

    def __init__(
        self,
        sample_rate_hz: int | None = None,
        num_channels: int | None = None,
        device_id: int | None = None,
    ) -> None:
        """Initialisiere den Audio-Recorder."""
        self.logger = get_logger(self.__class__.__name__)

        # Konfiguration laden
        config = Config()
        self.sample_rate_hz = sample_rate_hz or config.audio_sample_rate
        self.num_channels = num_channels or config.audio_channels
        self.device_id = device_id or config.audio_device

        # Interne Zustände
        self._stream: sd.InputStream | None = None
        self._active = False
        self._chunks: list[np.ndarray] = []
        self._buffer_lock = threading.Lock()

        # Geräteauswahl
        self._selected_device: dict[str, Any] | None = None
        self._available_devices: list[dict[str, Any]] = []

        # Geräte initialisieren
        self._initialize_audio_devices()

        # Audio-Interface initialisieren
        self._volume_interface: Any | None = None
        self._system_volume: float | None = None
        self._setup_audio_interface()

    def _setup_audio_interface(self):
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

    def _initialize_audio_devices(self) -> None:
        """Initialisiere verfügbare Audio-Geräte und wähle das beste aus."""
        try:
            # Alle Geräte abfragen
            devices = sd.query_devices()
            default_input = sd.query_devices(kind="input")

            # Eingabegeräte filtern
            self._available_devices = []
            for i, device in enumerate(devices):
                try:
                    input_device = sd.query_devices(i, kind="input")
                    if input_device and input_device.get("max_inputs", 0) > 0:
                        self._available_devices.append(
                            {
                                "index": i,
                                "name": input_device.get("name", f"Device {i}"),
                                "max_inputs": input_device.get("max_inputs", 1),
                                "default_samplerate": input_device.get(
                                    "default_samplerate", 44100
                                ),
                                "is_default": i == default_input["index"],
                            }
                        )
                except Exception:
                    continue

            pass

            # Gerät auswählen
            self._select_audio_device()

        except Exception:
            self._fallback_to_default_device()

    def _select_audio_device(self) -> None:
        """Wähle das beste verfügbare Audio-Gerät aus."""
        if not self._available_devices:
            self._fallback_to_default_device()
            return

        # Wenn ein spezifisches Gerät konfiguriert ist, verwende es
        if self.device_id is not None:
            for device in self._available_devices:
                if device["index"] == self.device_id:
                    if self._test_device(device):
                        self._selected_device = device
                        return
                    break

        # Bestes Gerät automatisch auswählen
        best_device = None

        # Priorität 1: Standard-Gerät testen
        for device in self._available_devices:
            if device["is_default"]:
                if self._test_device(device):
                    best_device = device
                    break

        # Priorität 2: Andere Geräte testen
        if not best_device:
            for device in self._available_devices:
                if not device["is_default"]:
                    if self._test_device(device):
                        best_device = device
                        break

        # Priorität 3: Erstes verfügbares Gerät als Fallback
        if not best_device and self._available_devices:
            best_device = self._available_devices[0]

        if best_device:
            self._selected_device = best_device
        else:
            self._fallback_to_default_device()

    def _test_device(self, device: dict[str, Any]) -> bool:
        """Teste, ob ein Audio-Gerät funktioniert."""
        try:
            test_stream = sd.InputStream(
                device=device["index"],
                samplerate=self.sample_rate_hz,
                channels=self.num_channels,
                dtype=np.float32,
                blocksize=1024,
            )
            test_stream.start()
            test_stream.stop()
            test_stream.close()
            return True
        except Exception:
            return False

    def _fallback_to_default_device(self) -> None:
        """Fallback auf Standard-Gerät."""
        try:
            default_device = sd.query_devices(kind="input")
            self._selected_device = {
                "index": default_device["index"],
                "name": default_device["name"],
                "max_inputs": 1,
                "default_samplerate": default_device.get("default_samplerate", 44100),
                "is_default": True,
            }
        except Exception:
            raise RuntimeError("Kein funktionierendes Audio-Gerät verfügbar")

    def _audio_callback(
        self, indata: np.ndarray, frames: int, _: Any, status: Any
    ) -> None:
        """Callback für eingehende Audio-Daten."""
        if not self._active or indata is None:
            return

        try:
            with self._buffer_lock:
                self._chunks.append(indata.copy())
        except Exception:
            pass

    def start_recording(self) -> None:
        """Starte die Audioaufnahme."""
        if self._active:
            return

        if not self._selected_device:
            raise RuntimeError("Kein Audio-Gerät ausgewählt")

        # Aufnahme vorbereiten
        self._chunks = []
        self._active = True

        # Lautstärke nur ändern wenn Interface verfügbar ist
        if self._volume_interface:
            try:
                # Aktuelle System-Lautstärke speichern
                self._system_volume = (
                    self._volume_interface.GetMasterVolumeLevelScalar()
                )
                # Lautstärke auf 10% reduzieren (0.1 = 10%)
                self._volume_interface.SetMasterVolumeLevelScalar(0.1, None)
                self.logger.debug(
                    f"Lautstärke reduziert von {self._system_volume:.2f} auf 0.10"
                )
            except Exception as e:
                self.logger.warning(f"Fehler beim Ändern der Lautstärke: {e}")
                self._system_volume = None
        else:
            self.logger.debug(
                "Kein Lautstärke-Interface verfügbar - überspringe Lautstärke-Änderung"
            )
            self._system_volume = None

        # Audio-Stream starten
        self._stream = sd.InputStream(
            device=self._selected_device["index"],
            samplerate=self.sample_rate_hz,
            channels=self.num_channels,
            dtype=np.float32,
            callback=self._audio_callback,
            blocksize=1024,
        )

        self._stream.start()

    def stop_recording(self) -> np.ndarray:
        """Stoppe die Aufnahme und gib die Audio-Daten zurück."""
        if not self._active:
            return np.array([], dtype=np.float32)

        # Aufnahme stoppen
        self._active = False

        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        # Lautstärke nur wiederherstellen wenn Interface verfügbar ist und ursprüngliche Lautstärke gespeichert wurde
        if self._volume_interface and self._system_volume is not None:
            try:
                self._volume_interface.SetMasterVolumeLevelScalar(
                    self._system_volume, None
                )
                self.logger.debug(
                    f"Lautstärke wiederhergestellt auf {self._system_volume:.2f}"
                )
            except Exception as e:
                self.logger.error(f"Fehler beim Wiederherstellen der Lautstärke: {e}")
        elif self._volume_interface:
            self.logger.warning(
                "Keine ursprüngliche Lautstärke gespeichert - überspringe Wiederherstellung"
            )
        else:
            self.logger.debug(
                "Kein Lautstärke-Interface verfügbar - überspringe Lautstärke-Wiederherstellung"
            )

        # Audio-Daten verarbeiten
        with self._buffer_lock:
            chunks_to_process = self._chunks.copy()
            self._chunks = []

        if not chunks_to_process:
            return np.array([], dtype=np.float32)

        # Audio-Chunks zusammenfügen
        audio = np.concatenate(chunks_to_process, axis=0)

        # Bei mehreren Kanälen zu Mono konvertieren
        if audio.ndim == 2 and audio.shape[1] > 1:
            audio = np.mean(audio, axis=1)

        return audio.astype(np.float32)

    def is_recording(self) -> bool:
        """Prüfe, ob gerade aufgenommen wird."""
        return self._active

    def get_current_device(self) -> dict[str, Any] | None:
        """Gib Informationen über das aktuelle Audio-Gerät zurück."""
        return self._selected_device.copy() if self._selected_device else None

    def list_devices(self) -> list[dict[str, Any]]:
        """Liste alle verfügbaren Audio-Geräte auf."""
        return self._available_devices.copy()

    def change_device(self, device_id: int) -> bool:
        """Wechsle zu einem anderen Audio-Gerät."""
        if self._active:
            return False

        # Gerät finden
        target_device = None
        for device in self._available_devices:
            if device["index"] == device_id:
                target_device = device
                break

        if not target_device:
            return False

        # Gerät testen
        if self._test_device(target_device):
            self._selected_device = target_device
            return True
        return False

    def get_audio_info(self) -> dict[str, Any]:
        """Gib Informationen über die aktuelle Audio-Konfiguration zurück."""
        return {
            "sample_rate": self.sample_rate_hz,
            "channels": self.num_channels,
            "device": self._selected_device,
            "is_recording": self._active,
        }

    def restore_volume(self) -> None:
        """Stelle die ursprüngliche System-Lautstärke wieder her."""
        if self._volume_interface and self._system_volume is not None:
            try:
                self._volume_interface.SetMasterVolumeLevelScalar(
                    self._system_volume, None
                )
                self.logger.info(
                    f"✅ Lautstärke wiederhergestellt auf {self._system_volume:.2f}"
                )
            except Exception as e:
                self.logger.error(
                    f"❌ Fehler beim Wiederherstellen der Lautstärke: {e}"
                )
        elif self._volume_interface:
            self.logger.warning("⚠️  Keine ursprüngliche Lautstärke gespeichert")
        else:
            self.logger.debug("Kein Lautstärke-Interface verfügbar")

    def cleanup(self) -> None:
        """Sauberes Aufräumen beim Beenden."""
        try:
            # Stoppe Aufnahme falls aktiv
            if self._active:
                self.stop_recording()

            # Stelle Lautstärke sicher wieder her
            self.restore_volume()

            self.logger.info("✅ AudioRecorder erfolgreich aufgeräumt")
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Aufräumen des AudioRecorders: {e}")
