from __future__ import annotations

from typing import Optional

import numpy as np
from faster_whisper import WhisperModel

from .config import Config
from .logger import get_logger
from .spell_checker import check_and_correct_text


class SpeechToText:
    def __init__(self) -> None:
        self.logger = get_logger(__class__.__name__)
        device = "cpu"  # Use CPU for better compatibility
        config_instance = Config()
        self._model = WhisperModel(
            model_size_or_path=config_instance.stt_model_size,
            device=device,
            compute_type=config_instance.stt_compute_type,
        )

    def transcribe_raw(
        self, audio_f32_mono: np.ndarray, language: str | None = None
    ) -> str:
        """Transkribiere Audio ohne Rechtschreibkorrektur für schnelle Rückgabe."""
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
        return raw_text

    def transcribe(
        self, audio_f32_mono: np.ndarray, language: str | None = None
    ) -> str:
        """Transkribiere Audio mit Rechtschreibkorrektur (für Kompatibilität)."""
        raw_text = self.transcribe_raw(audio_f32_mono, language)

        # Rechtschreibkorrektur anwenden falls aktiviert
        if (
            raw_text
            and hasattr(Config(), "spell_check_enabled")
            and Config().spell_check_enabled
        ):
            try:
                corrected_text = check_and_correct_text(raw_text)
                return corrected_text
            except Exception as e:
                self.logger.error(f"Rechtschreibkorrektur fehlgeschlagen: {e}")
                return raw_text

        return raw_text
