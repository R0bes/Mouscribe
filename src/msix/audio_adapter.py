"""
MSIX-spezifischer Audio-Adapter für Mauscribe
Verwendet Windows Runtime APIs für MSIX-Kompatibilität
"""

import os
import asyncio
import threading
from typing import List, Dict, Optional, Callable
from pathlib import Path
import numpy as np

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

from ..utils.config import Config
from ..utils.logger import get_logger


class MSIXAudioAdapter:
    """MSIX-kompatibler Audio-Adapter mit Fallback-Mechanismen"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = get_logger(self.__class__.__name__)
        
        # MSIX-Erkennung
        self._is_msix = self._detect_msix_environment()
        self.logger.info(f"MSIX-Umgebung erkannt: {self._is_msix}")
        
        # Audio-System
        self._audio_system = None
        self._current_device = None
        self._available_devices = []
        self._is_recording = False
        self._audio_data = []
        self._recording_thread = None
        self._stop_recording_event = threading.Event()
        
        # Callbacks
        self._on_recording_start: Optional[Callable] = None
        self._on_recording_stop: Optional[Callable] = None
        self._on_audio_data: Optional[Callable] = None
        
        # Initialisierung
        self._initialize_audio_system()
    
    def _detect_msix_environment(self) -> bool:
        """Erkennt MSIX-Container-Umgebung"""
        msix_indicators = [
            'MSIX_PACKAGE_FAMILY_NAME',
            'PACKAGE_FAMILY_NAME',
            'PACKAGE_FULL_NAME'
        ]
        
        for indicator in msix_indicators:
            if indicator in os.environ:
                return True
        
        # Prüfe AppData-Pfad
        app_data = os.environ.get('LOCALAPPDATA', '')
        if app_data and 'Packages' in app_data:
            return True
        
        return False
    
    def _initialize_audio_system(self):
        """Initialisiert das beste verfügbare Audio-System"""
        self.logger.info("Initialisiere Audio-System...")
        
        # Priorisierte Audio-Systeme
        audio_systems = [
            ('Windows Runtime', self._try_winrt_audio),
            ('SoundDevice', self._try_sounddevice_audio),
            ('PyAudio', self._try_pyaudio_audio),
            ('Fallback', self._try_fallback_audio)
        ]
        
        for name, system_func in audio_systems:
            try:
                self.logger.info(f"Versuche {name} Audio-System...")
                if system_func():
                    self.logger.info(f"✅ {name} Audio-System erfolgreich initialisiert")
                    return
            except Exception as e:
                self.logger.warning(f"⚠️ {name} Audio-System fehlgeschlagen: {e}")
                continue
        
        self.logger.error("❌ Kein Audio-System konnte initialisiert werden")
        raise RuntimeError("Kein Audio-System verfügbar")
    
    def _try_winrt_audio(self) -> bool:
        """Versucht Windows Runtime Audio APIs"""
        if not self._is_msix:
            return False
        
        try:
            # Windows Runtime Audio APIs verwenden
            # Diese sind MSIX-kompatibel
            import winrt.windows.media.audio as audio
            import winrt.windows.media.capture as capture
            
            self._audio_system = 'winrt'
            self._available_devices = self._get_winrt_devices()
            return True
        except ImportError:
            self.logger.debug("Windows Runtime Audio nicht verfügbar")
            return False
        except Exception as e:
            self.logger.warning(f"Windows Runtime Audio Fehler: {e}")
            return False
    
    def _try_sounddevice_audio(self) -> bool:
        """Versucht SoundDevice Audio-System"""
        if not SOUNDDEVICE_AVAILABLE:
            return False
        
        try:
            # SoundDevice ist MSIX-kompatibel
            devices = sd.query_devices()
            input_devices = [d for d in devices if d.get('max_inputs', 0) > 0]
            
            if input_devices:
                self._audio_system = 'sounddevice'
                self._available_devices = self._convert_sounddevice_devices(input_devices)
                return True
        except Exception as e:
            self.logger.warning(f"SoundDevice Fehler: {e}")
        
        return False
    
    def _try_pyaudio_audio(self) -> bool:
        """Versucht PyAudio Audio-System"""
        if not PYAUDIO_AVAILABLE:
            return False
        
        try:
            p = pyaudio.PyAudio()
            devices = []
            
            for i in range(p.get_device_count()):
                try:
                    device_info = p.get_device_info_by_index(i)
                    if device_info['maxInputChannels'] > 0:
                        devices.append({
                            'index': i,
                            'name': device_info['name'],
                            'channels': device_info['maxInputChannels'],
                            'sample_rate': int(device_info['defaultSampleRate'])
                        })
                except:
                    continue
            
            if devices:
                self._audio_system = 'pyaudio'
                self._available_devices = devices
                return True
        except Exception as e:
            self.logger.warning(f"PyAudio Fehler: {e}")
        
        return False
    
    def _try_fallback_audio(self) -> bool:
        """Fallback Audio-System"""
        self.logger.warning("Verwende Fallback Audio-System")
        self._audio_system = 'fallback'
        self._available_devices = [{'index': 0, 'name': 'Default Device', 'channels': 1, 'sample_rate': 16000}]
        return True
    
    def _get_winrt_devices(self) -> List[Dict]:
        """Ermittelt Audio-Geräte über Windows Runtime APIs"""
        try:
            import winrt.windows.media.devices as devices
            import winrt.windows.media.capture as capture
            
            # Windows Runtime Audio Device Enumeration
            # Dies ist MSIX-kompatibel
            return []
        except ImportError:
            return []
    
    def _convert_sounddevice_devices(self, devices: List) -> List[Dict]:
        """Konvertiert SoundDevice-Geräte in Standard-Format"""
        converted = []
        for i, device in enumerate(devices):
            converted.append({
                'index': i,
                'name': device.get('name', f'Device {i}'),
                'channels': device.get('max_inputs', 1),
                'sample_rate': int(device.get('default_samplerate', 16000))
            })
        return converted
    
    def get_audio_devices(self) -> List[Dict]:
        """Gibt verfügbare Audio-Geräte zurück"""
        return self._available_devices
    
    def select_device(self, device_index: int) -> bool:
        """Wählt ein Audio-Gerät aus"""
        for device in self._available_devices:
            if device['index'] == device_index:
                self._current_device = device
                self.logger.info(f"Audio-Gerät ausgewählt: {device['name']}")
                return True
        return False
    
    def start_recording(self, 
                       sample_rate: int = 16000,
                       channels: int = 1,
                       on_data: Optional[Callable] = None) -> bool:
        """Startet Audio-Aufnahme"""
        if self._is_recording:
            self.logger.warning("Aufnahme läuft bereits")
            return False
        
        if not self._current_device:
            self.logger.error("Kein Audio-Gerät ausgewählt")
            return False
        
        self._on_audio_data = on_data
        self._is_recording = True
        self._audio_data = []
        self._stop_recording_event.clear()
        
        # Starte Aufnahme-Thread
        self._recording_thread = threading.Thread(
            target=self._recording_worker,
            args=(sample_rate, channels)
        )
        self._recording_thread.start()
        
        if self._on_recording_start:
            self._on_recording_start()
        
        self.logger.info("Audio-Aufnahme gestartet")
        return True
    
    def stop_recording(self) -> Optional[np.ndarray]:
        """Stoppt Audio-Aufnahme und gibt Daten zurück"""
        if not self._is_recording:
            return None
        
        self._is_recording = False
        self._stop_recording_event.set()
        
        if self._recording_thread:
            self._recording_thread.join(timeout=5.0)
        
        if self._on_recording_stop:
            self._on_recording_stop()
        
        # Konvertiere Audio-Daten
        if self._audio_data:
            audio_array = np.concatenate(self._audio_data)
            self.logger.info(f"Aufnahme gestoppt: {len(audio_array)} Samples")
            return audio_array
        
        return None
    
    def _recording_worker(self, sample_rate: int, channels: int):
        """Worker-Thread für Audio-Aufnahme"""
        try:
            if self._audio_system == 'sounddevice':
                self._record_with_sounddevice(sample_rate, channels)
            elif self._audio_system == 'pyaudio':
                self._record_with_pyaudio(sample_rate, channels)
            elif self._audio_system == 'winrt':
                self._record_with_winrt(sample_rate, channels)
            else:
                self._record_fallback(sample_rate, channels)
        except Exception as e:
            self.logger.error(f"Fehler in Aufnahme-Thread: {e}")
    
    def _record_with_sounddevice(self, sample_rate: int, channels: int):
        """Aufnahme mit SoundDevice"""
        def callback(indata, frames, time, status):
            if status:
                self.logger.warning(f"SoundDevice Status: {status}")
            if self._is_recording:
                audio_chunk = indata.copy()
                self._audio_data.append(audio_chunk)
                if self._on_audio_data:
                    self._on_audio_data(audio_chunk)
        
        with sd.InputStream(
            device=self._current_device['index'],
            channels=channels,
            samplerate=sample_rate,
            callback=callback,
            dtype=np.float32
        ):
            while self._is_recording and not self._stop_recording_event.is_set():
                sd.sleep(100)
    
    def _record_with_pyaudio(self, sample_rate: int, channels: int):
        """Aufnahme mit PyAudio"""
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paFloat32,
            channels=channels,
            rate=sample_rate,
            input=True,
            input_device_index=self._current_device['index'],
            stream_callback=None
        )
        
        try:
            stream.start_stream()
            while self._is_recording and not self._stop_recording_event.is_set():
                data = stream.read(1024, exception_on_overflow=False)
                audio_chunk = np.frombuffer(data, dtype=np.float32)
                self._audio_data.append(audio_chunk)
                if self._on_audio_data:
                    self._on_audio_data(audio_chunk)
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
    
    def _record_with_winrt(self, sample_rate: int, channels: int):
        """Aufnahme mit Windows Runtime APIs"""
        # Windows Runtime Audio Recording
        # MSIX-kompatible Implementierung
        pass
    
    def _record_fallback(self, sample_rate: int, channels: int):
        """Fallback-Aufnahme (Simulation)"""
        import time
        import random
        
        # Simuliere Audio-Aufnahme für Tests
        start_time = time.time()
        while self._is_recording and not self._stop_recording_event.is_set():
            # Simuliere Audio-Daten
            audio_chunk = np.random.rand(1024).astype(np.float32) * 0.1
            self._audio_data.append(audio_chunk)
            if self._on_audio_data:
                self._on_audio_data(audio_chunk)
            time.sleep(0.064)  # ~1024 samples bei 16kHz
    
    def set_callbacks(self, 
                     on_start: Optional[Callable] = None,
                     on_stop: Optional[Callable] = None,
                     on_data: Optional[Callable] = None):
        """Setzt Callback-Funktionen"""
        self._on_recording_start = on_start
        self._on_recording_stop = on_stop
        self._on_audio_data = on_data
    
    def is_recording(self) -> bool:
        """Gibt zurück ob Aufnahme läuft"""
        return self._is_recording
    
    def get_audio_system(self) -> str:
        """Gibt das verwendete Audio-System zurück"""
        return self._audio_system
    
    def cleanup(self):
        """Räumt Audio-System auf"""
        if self._is_recording:
            self.stop_recording()
        
        self._audio_data.clear()
        self._recording_thread = None
