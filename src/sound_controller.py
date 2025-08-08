# src/sound_controller.py
from typing import Optional

try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    WINDOWS_AUDIO_AVAILABLE = True
except ImportError:
    WINDOWS_AUDIO_AVAILABLE = False

class SoundController:    
    def __init__(self) -> None:
        self._volume_interface = None
        self._setup_volume_control()
    
    def _setup_volume_control(self) -> None:
        if not WINDOWS_AUDIO_AVAILABLE:
            print("⚠️  Windows Audio nicht verfügbar")
            return        
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self._volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
            print("✅ Volume Control initialisiert")
        except Exception as e:
            print(f"❌ Volume Control Fehler: {e}")
            self._volume_interface = None
    
    def get_volume_percent(self) -> int:
        if not self._volume_interface:
            return 50  # Fallback
        
        try:
            volume = self._volume_interface.GetMasterVolumeLevelScalar()
            return int(volume * 100)
        except Exception as e:
            print(f"⚠️  Volume-Abfrage Fehler: {e}")
            return 50  # Fallback
    
    def set_volume_percent(self, percent: int) -> None:
        if not self._volume_interface:
            print("⚠️  Volume Control nicht verfügbar")
            return
        
        try:
            volume_scalar = max(0.0, min(1.0, percent / 100.0))
            self._volume_interface.SetMasterVolumeLevelScalar(volume_scalar, None)
        except Exception as e:
            print(f"❌ Volume-Setzen Fehler: {e}")
    
    def mute_volume(self) -> None:
        if not self._volume_interface:
            return        
        try:
            self._volume_interface.SetMute(1, None)
        except Exception as e:
            print(f"❌ Mute Fehler: {e}")
    
    def unmute_volume(self) -> None:
        """Entstummt das System"""
        if not self._volume_interface:
            return
        try:
            self._volume_interface.SetMute(0, None)
        except Exception as e:
            print(f"❌ Unmute Fehler: {e}")
    
    def is_muted(self) -> bool:
        """Prüft ob das System stumm ist"""
        if not self._volume_interface:
            return False        
        try:
            return bool(self._volume_interface.GetMute())
        except Exception as e:
            print(f"⚠️  Mute-Status Fehler: {e}")
            return False
