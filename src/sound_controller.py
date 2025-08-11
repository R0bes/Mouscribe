# src/sound_controller.py - System volume control for Mauscribe
"""
System volume management for Mauscribe application.
Handles volume reduction during recording and restoration afterward.
"""

import comtypes
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


class SoundController:
    """Controls system audio volume for Mauscribe application."""

    def __init__(self):
        """Initialize the sound controller."""
        self._volume_interface = None
        self._setup_audio_interface()

    def _setup_audio_interface(self):
        """Setup audio interface for volume control."""
        try:
            # Get default audio device
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self._volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
            print("Audio interface initialized successfully")
        except Exception as e:
            print(f"Failed to initialize audio interface: {e}")
            self._volume_interface = None

    def get_volume(self) -> int:
        """Get current system volume percentage."""
        if not self._volume_interface:
            return 100

        try:
            volume = self._volume_interface.GetMasterVolumeLevelScalar()
            return int(volume * 100)
        except Exception as e:
            print(f"Failed to get volume: {e}")
            return 100

    def set_volume(self, volume_percent: int):
        """Set system volume to specified percentage."""
        if not self._volume_interface:
            print("Audio interface not available")
            return

        try:
            # Clamp volume to valid range
            volume_percent = max(0, min(100, volume_percent))
            volume_scalar = volume_percent / 100.0

            self._volume_interface.SetMasterVolumeLevelScalar(volume_scalar, None)
            print(f"Volume set to {volume_percent}%")
        except Exception as e:
            print(f"Failed to set volume: {e}")

    def reduce_volume(self, factor: float = 0.3, min_percent: int = 10):
        """Reduce volume by specified factor with minimum threshold."""
        current_volume = self.get_volume()
        target_volume = max(min_percent, int(current_volume * factor))

        self.set_volume(target_volume)
        return current_volume, target_volume

    def restore_volume(self, original_volume: int):
        """Restore volume to original level."""
        self.set_volume(original_volume)

    def is_available(self) -> bool:
        """Check if audio control is available."""
        return self._volume_interface is not None
