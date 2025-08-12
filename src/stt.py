from __future__ import annotations

from typing import Optional

import numpy as np
from faster_whisper import WhisperModel

from .config import Config
from .spell_checker import check_and_correct_text


class SpeechToText:
    def __init__(self) -> None:
        device = "cpu"  # Use CPU for better compatibility
        config_instance = Config()
        self._model = WhisperModel(
            model_size_or_path=config_instance.stt_model_size,
            device=device,
            compute_type=config_instance.stt_compute_type,
        )

    def transcribe(
        self, audio_f32_mono: np.ndarray, language: str | None = None
    ) -> str:
        if audio_f32_mono.size == 0:
            return ""
        # faster-whisper expects 16kHz float32 mono. We record at 16kHz already.
        # Ensure shape (n,), dtype float32
        audio = audio_f32_mono.astype(np.float32).flatten()
        config_instance = Config()
        lang = language or config_instance.stt_language
        segments, info = self._model.transcribe(
            audio=audio,
            language=lang,
            vad_filter=False,
            beam_size=1,
            best_of=1,
        )
        text_parts = [seg.text.strip() for seg in segments]
        raw_text = " ".join([t for t in text_parts if t])

        # Rechtschreibkorrektur anwenden falls aktiviert
        if config_instance.spell_check_enabled and raw_text:
            try:
                corrected_text = check_and_correct_text(raw_text)
                return corrected_text
            except Exception as e:
                print(f"Rechtschreibkorrektur fehlgeschlagen: {e}")
                return raw_text

        return raw_text
