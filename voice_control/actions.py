from __future__ import annotations

import math
import subprocess
import sys
from typing import Optional

from comtypes import CLSCTX_ALL
from ctypes import POINTER, cast
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


class SystemActions:
    def __init__(self) -> None:
        self._volume = self._get_endpoint_volume()

    def _get_endpoint_volume(self) -> IAudioEndpointVolume:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        return volume

    def get_volume_percent(self) -> int:
        """Get current system volume as percentage"""
        try:
            volume_scalar = self._volume.GetMasterVolumeLevelScalar()
            return int(volume_scalar * 100.0)
        except Exception:
            return 50  # Default fallback

    def set_volume_percent(self, percent: int) -> None:
        p = max(0, min(100, int(percent)))
        self._volume.SetMasterVolumeLevelScalar(p / 100.0, None)

    def change_volume_relative(self, delta_percent: int) -> None:
        current = self._volume.GetMasterVolumeLevelScalar() * 100.0
        self.set_volume_percent(int(current + delta_percent))

    def set_mute(self, muted: bool) -> None:
        self._volume.SetMute(1 if muted else 0, None)
