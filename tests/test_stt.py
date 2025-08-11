"""Tests for the STT module."""
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

# Import the module to test
from src.stt import SpeechToText


class TestSpeechToText:
    """Test cases for SpeechToText class."""

    def test_stt_initialization(self):
        """Test SpeechToText initialization."""
        with patch("src.stt.WhisperModel") as mock_model:
            stt = SpeechToText()
            assert stt is not None
            assert hasattr(stt, "_model")

    def test_transcribe_audio(self):
        """Test audio transcription."""
        with patch("src.stt.WhisperModel") as mock_model:
            stt = SpeechToText()

            # Mock audio data
            mock_audio = np.array([0.1, 0.2, 0.3])

            # Mock transcription result
            mock_result = MagicMock()
            mock_result.text = "Hello world"
            mock_result.language = "en"

            # Mock the model's transcribe method
            stt._model.transcribe.return_value = ([mock_result], {"language": "en"})

            result = stt.transcribe(mock_audio)
            assert result is not None
            assert result == "Hello world"
            # The transcribe method returns the text directly, not an object

    def test_transcribe_empty_audio(self):
        """Test transcription with empty audio."""
        with patch("src.stt.WhisperModel") as mock_model:
            stt = SpeechToText()

            # Empty audio
            empty_audio = np.array([])

            result = stt.transcribe(empty_audio)
            # Should handle empty audio gracefully
            assert result == ""

    def test_get_language(self):
        """Test language detection."""
        with patch("src.stt.WhisperModel") as mock_model:
            stt = SpeechToText()

            # Mock audio data
            mock_audio = np.array([0.1, 0.2, 0.3])

            # Mock language detection result
            mock_result = MagicMock()
            mock_result.text = "Hallo Welt"
            mock_result.language = "de"

            stt._model.transcribe.return_value = ([mock_result], {"language": "de"})

            result = stt.transcribe(mock_audio)
            assert result == "Hallo Welt"


if __name__ == "__main__":
    pytest.main([__file__])
