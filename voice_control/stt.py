from __future__ import annotations

from typing import Optional

import numpy as np
from faster_whisper import WhisperModel

from . import config


class SpeechToText:
    def __init__(self) -> None:
        device = "cpu"  # Use CPU for better compatibility
        self._model = WhisperModel(
            model_size_or_path=config.WHISPER_MODEL,
            device=device,
            compute_type=config.COMPUTE_TYPE,
        )

    def transcribe(self, audio_f32_mono: np.ndarray, language: Optional[str] = None) -> str:
        if audio_f32_mono.size == 0:
            return ""
        # faster-whisper expects 16kHz float32 mono. We record at 16kHz already.
        # Ensure shape (n,), dtype float32
        audio = audio_f32_mono.astype(np.float32).flatten()
        lang = language or config.LANGUAGE
        segments, info = self._model.transcribe(
            audio=audio,
            language=lang,
            vad_filter=False,
            beam_size=1,
            best_of=1,
        )
        text_parts = [seg.text.strip() for seg in segments]
        return " ".join([t for t in text_parts if t])
