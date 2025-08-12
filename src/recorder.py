from __future__ import annotations

import threading
from typing import List, Optional

import numpy as np
import sounddevice as sd

from .config import Config


class AudioRecorder:
    def __init__(
        self, sample_rate_hz: int | None = None, num_channels: int | None = None
    ) -> None:
        config_instance = Config()
        self.sample_rate_hz: int = sample_rate_hz or config_instance.audio_sample_rate
        self.num_channels: int = num_channels or config_instance.audio_channels
        self._stream: sd.InputStream | None = None
        self._buffer_lock = threading.Lock()
        self._chunks: list[np.ndarray] = []
        self._active: bool = False

        # Show available audio devices
        self._show_audio_devices()

    def _show_audio_devices(self) -> None:
        """Show available audio devices and current default."""
        try:
            devices = sd.query_devices()
            default_input = sd.query_devices(kind="input")

            print("🎤 Verfügbare Audio-Eingabegeräte:")
            for i, device in enumerate(devices):
                # Check if device has input capability
                if "max_inputs" in device and device["max_inputs"] > 0:
                    status = " (Standard)" if i == default_input["index"] else ""
                    print(f"  {i}: {device['name']}{status}")
                elif "inputs" in device and device["inputs"] > 0:
                    status = " (Standard)" if i == default_input["index"] else ""
                    print(f"  {i}: {device['name']}{status}")

            print(f"🎤 Aktuelles Standard-Mikrofon: {default_input['name']}")
            print(
                f"🎤 Sample Rate: {self.sample_rate_hz} Hz, Kanäle: {self.num_channels}"
            )

        except Exception as e:
            print(f"⚠️  Konnte Audio-Geräte nicht auflisten: {e}")
            # Fallback: show basic info
            try:
                default_input = sd.query_devices(kind="input")
                print(f"🎤 Standard-Mikrofon: {default_input['name']}")
            except Exception:
                print("🎤 Konnte Standard-Mikrofon nicht ermitteln")

    def _callback(self, indata, frames, time, status) -> None:  # type: ignore[no-untyped-def]
        if status:
            print(f"⚠️  Audio-Status: {status}")
        if not self._active:
            return
        # indata is float32 by default; we force dtype float32 on stream to ensure consistent type
        with self._buffer_lock:
            self._chunks.append(indata.copy())

    def start_recording(self) -> None:
        if self._active:
            return

        try:
            self._chunks = []
            self._active = True

            print("🎤 Starte Aufnahme mit Mikrofon...")
            self._stream = sd.InputStream(
                samplerate=self.sample_rate_hz,
                channels=self.num_channels,
                dtype="float32",
                callback=self._callback,
                blocksize=int(self.sample_rate_hz * 0.03),  # ~30ms blocks
            )
            self._stream.start()
            print("✅ Audio-Stream gestartet")

        except Exception as e:
            print(f"❌ Fehler beim Starten der Audioaufnahme: {e}")
            self._active = False
            self._stream = None
            raise

    def stop_recording_immediate(self) -> np.ndarray:
        """Stop recording immediately and return audio data."""
        if not self._active:
            return np.zeros((0,), dtype=np.float32)

        self._active = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        with self._buffer_lock:
            if not self._chunks:
                return np.zeros((0,), dtype=np.float32)
            audio = np.concatenate(self._chunks, axis=0)

        # If multichannel, downmix to mono
        if audio.ndim == 2 and audio.shape[1] > 1:
            audio = np.mean(audio, axis=1)
        return audio.astype(np.float32)

    def stop_recording(self) -> np.ndarray:
        """Stop recording and return audio data."""
        if not self._active:
            return np.zeros((0,), dtype=np.float32)
        self._active = False
        assert self._stream is not None
        self._stream.stop()
        self._stream.close()
        self._stream = None
        with self._buffer_lock:
            if not self._chunks:
                return np.zeros((0,), dtype=np.float32)
            audio = np.concatenate(self._chunks, axis=0)
        # If multichannel, downmix to mono
        if audio.ndim == 2 and audio.shape[1] > 1:
            audio = np.mean(audio, axis=1)
        return audio.astype(np.float32)

    def record_audio(self, duration_seconds: float = 60.0) -> np.ndarray | None:
        """Record audio until stopped or timeout reached."""
        try:
            print(f"🎤 Starte Audioaufnahme (Timeout: {duration_seconds}s)...")

            # Start recording first
            self.start_recording()

            if not self._active:
                print("❌ Aufnahme konnte nicht gestartet werden")
                return None

            # Wait until stopped or timeout reached
            import time

            start_time = time.time()

            print("🎤 Warte auf Audio-Daten...")
            while self._active and (time.time() - start_time) < duration_seconds:
                time.sleep(0.1)  # Check every 100ms
                if not self._active:
                    print("✅ Aufnahme durch Benutzer gestoppt")
                    break

            if (time.time() - start_time) >= duration_seconds:
                print("⏰ Aufnahme-Timeout erreicht")

            print("🛑 Stoppe Audioaufnahme...")
            audio_data = self.stop_recording()

            if len(audio_data) > 0:
                duration = len(audio_data) / self.sample_rate_hz
                print(
                    f"✅ Audio aufgenommen: {len(audio_data)} Samples ({duration:.2f}s)"
                )
                return audio_data
            else:
                print("❌ Keine Audio-Daten aufgenommen")
                return None

        except Exception as e:
            print(f"❌ Fehler während der Audioaufnahme: {e}")
            import traceback

            traceback.print_exc()
            return None
