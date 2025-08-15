from __future__ import annotations

from typing import Optional

import numpy as np
from faster_whisper import WhisperModel

from ..utils.config import Config
from ..utils.logger import get_logger
from .spell_checker import check_and_correct_text


class SpeechToText:
    def __init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__)
        device = "cpu"  # Use CPU for better compatibility
        config_instance = Config()
        self._model = WhisperModel(
            model_size_or_path=config_instance.stt_model,
            device=device,
            compute_type=config_instance.stt_compute_type,
        )

    def transcribe_raw(self, audio_f32_mono: np.ndarray, language: str | None = None) -> str:
        """Transkribiere Audio ohne Rechtschreibkorrektur für schnelle Rückgabe."""
        if audio_f32_mono.size == 0:
            self.logger.warning("Leere Audio-Daten erhalten")
            return ""

        # Log Audio-Daten für Debugging
        self.logger.info(
            f"Transkribiere Audio: {audio_f32_mono.size} Samples, Shape: {audio_f32_mono.shape}, Dtype: {audio_f32_mono.dtype}"
        )

        # faster-whisper expects 16kHz float32 mono. We record at 16kHz already.
        # Ensure shape (n,), dtype float32
        audio = audio_f32_mono.astype(np.float32).flatten()
        config_instance = Config()
        lang = language or config_instance.stt_language

        self.logger.info(f"Starte Whisper-Transkription mit Sprache: {lang}")

        try:
            segments, info = self._model.transcribe(
                audio=audio,
                language=lang,
                vad_filter=False,
                beam_size=1,
                best_of=1,
            )

            text_parts = [seg.text.strip() for seg in segments]
            raw_text = " ".join([t for t in text_parts if t])

            self.logger.info(f"Whisper-Transkription abgeschlossen: '{raw_text}'")
            return raw_text

        except Exception as e:
            self.logger.error(f"Fehler bei Whisper-Transkription: {e}")
            return ""

    def transcribe(self, audio_f32_mono: np.ndarray, language: str | None = None) -> str:
        """Transkribiere Audio mit Rechtschreibkorrektur (für Kompatibilität)."""
        raw_text = self.transcribe_raw(audio_f32_mono, language)

        # Rechtschreibkorrektur anwenden falls aktiviert
        if raw_text and hasattr(Config(), "spell_check_enabled") and Config().spell_check_enabled:
            try:
                corrected_text = check_and_correct_text(raw_text)
                return corrected_text
            except Exception as e:
                self.logger.error(f"Rechtschreibkorrektur fehlgeschlagen: {e}")
                return raw_text

        return raw_text
