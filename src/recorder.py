from __future__ import annotations

import threading
from typing import List, Optional

import numpy as np
import sounddevice as sd

from .config import Config


class AudioRecorder:
    def __init__(self, sample_rate_hz: int | None = None, num_channels: int | None = None) -> None:
        config_instance = Config()
        self.sample_rate_hz: int = sample_rate_hz or config_instance.audio_sample_rate
        self.num_channels: int = num_channels or config_instance.audio_channels
        self._stream: Optional[sd.InputStream] = None
        self._buffer_lock = threading.Lock()
        self._chunks: List[np.ndarray] = []
        self._active: bool = False

    def _callback(self, indata, frames, time, status) -> None:  # type: ignore[no-untyped-def]
        if status:
            # Dropouts/overflows are not critical for speech commands, ignore logging here.
            pass
        if not self._active:
            return
        # indata is float32 by default; we force dtype float32 on stream to ensure consistent type
        with self._buffer_lock:
            self._chunks.append(indata.copy())

    def start_recording(self) -> None:
        if self._active:
            return
        self._chunks = []
        self._active = True
        self._stream = sd.InputStream(
            samplerate=self.sample_rate_hz,
            channels=self.num_channels,
            dtype="float32",
            callback=self._callback,
            blocksize=int(self.sample_rate_hz * 0.03),  # ~30ms blocks
        )
        self._stream.start()

    def stop_recording(self) -> np.ndarray:
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
