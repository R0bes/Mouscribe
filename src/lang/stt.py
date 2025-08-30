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
        self._model = None
        self._initialize_model()

    def _initialize_model(self) -> None:
        """Initialisiert das Whisper-Modell mit robuster Fehlerbehandlung."""
        try:
            device = "cpu"  # Use CPU for better compatibility
            config_instance = Config()

            self.logger.info(f"🔧 Initialisiere Whisper-Modell: {config_instance.stt_model}")
            self.logger.info(f"🔧 Compute-Type: {config_instance.stt_compute_type}")
            self.logger.info(f"🔧 Sprache: {config_instance.stt_language}")

            self._model = WhisperModel(
                model_size_or_path=config_instance.stt_model,
                device=device,
                compute_type=config_instance.stt_compute_type,
            )

            self.logger.info("✅ Whisper-Modell erfolgreich initialisiert")

        except Exception as e:
            self.logger.error(f"❌ Fehler bei Whisper-Modell-Initialisierung: {e}")
            self.logger.info("🔄 Versuche Fallback auf 'base' Modell...")

            try:
                self._model = WhisperModel(
                    model_size_or_path="base",
                    device="cpu",
                    compute_type="float32",
                )
                self.logger.info("✅ Fallback-Modell erfolgreich geladen")
            except Exception as fallback_error:
                self.logger.error(f"❌ Auch Fallback-Modell fehlgeschlagen: {fallback_error}")
                self._model = None

    def transcribe_raw(self, audio_f32_mono: np.ndarray, language: str | None = None) -> str:
        """Transkribiere Audio ohne Rechtschreibkorrektur für schnelle Rückgabe."""
        if audio_f32_mono.size == 0:
            self.logger.warning("⚠️ Leere Audio-Daten erhalten")
            return ""

        # Prüfe ob Modell verfügbar ist
        if self._model is None:
            self.logger.error("❌ Whisper-Modell nicht verfügbar")
            self._initialize_model()  # Versuche erneut zu initialisieren
            if self._model is None:
                return ""

        # Log Audio-Daten für Debugging
        self.logger.info(
            f"🎵 Transkribiere Audio: {audio_f32_mono.size} Samples, Shape: {audio_f32_mono.shape}, Dtype: {audio_f32_mono.dtype}"
        )

        # Audio-Format validieren und konvertieren
        try:
            # faster-whisper expects 16kHz float32 mono. We record at 16kHz already.
            # Ensure shape (n,), dtype float32
            audio = audio_f32_mono.astype(np.float32).flatten()

            # Audio-Qualität prüfen
            if audio.size < 1600:  # Weniger als 0.1 Sekunden bei 16kHz
                self.logger.warning("⚠️ Audio zu kurz für Transkription (< 0.1s)")
                return ""

            # Audio-Normalisierung für bessere Whisper-Performance
            if np.max(np.abs(audio)) > 0:
                audio = audio / np.max(np.abs(audio)) * 0.95

        except Exception as e:
            self.logger.error(f"❌ Fehler bei Audio-Formatierung: {e}")
            return ""

        config_instance = Config()
        lang = language or config_instance.stt_language

        self.logger.info(f"🗣️ Starte Whisper-Transkription mit Sprache: {lang}")

        try:
            # Whisper-Parameter für bessere deutsche Transkription
            segments, info = self._model.transcribe(
                audio=audio,
                language=lang,
                vad_filter=False,
                beam_size=3,  # Erhöht für bessere Qualität
                best_of=3,  # Erhöht für bessere Qualität
                temperature=0.0,  # Deterministisch für konsistente Ergebnisse
                condition_on_previous_text=False,  # Für kurze Audio-Snippets
            )

            text_parts = [seg.text.strip() for seg in segments]
            raw_text = " ".join([t for t in text_parts if t])

            if raw_text:
                self.logger.info(f"✅ Whisper-Transkription erfolgreich: '{raw_text}'")
                self.logger.info(f"📊 Transkriptions-Info: {info}")
            else:
                self.logger.warning("⚠️ Whisper gab leeren Text zurück")

            return raw_text

        except Exception as e:
            self.logger.error(f"❌ Fehler bei Whisper-Transkription: {e}")
            self.logger.info("🔄 Versuche Transkription ohne Sprachspezifikation...")

            try:
                # Fallback: Versuche ohne Sprachspezifikation
                segments, info = self._model.transcribe(
                    audio=audio,
                    language=None,  # Automatische Spracherkennung
                    vad_filter=False,
                    beam_size=1,
                    best_of=1,
                )

                text_parts = [seg.text.strip() for seg in segments]
                raw_text = " ".join([t for t in text_parts if t])

                if raw_text:
                    self.logger.info(f"✅ Fallback-Transkription erfolgreich: '{raw_text}'")
                    return raw_text

            except Exception as fallback_error:
                self.logger.error(f"❌ Auch Fallback-Transkription fehlgeschlagen: {fallback_error}")

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
