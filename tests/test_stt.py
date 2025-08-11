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
        with patch("src.stt.WhisperModel"):
            stt = SpeechToText()
            assert stt is not None
            assert hasattr(stt, "_model")

    def test_transcribe_audio(self):
        """Test audio transcription."""
        with patch("src.stt.WhisperModel"):
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
        with patch("src.stt.WhisperModel"):
            stt = SpeechToText()

            # Empty audio
            empty_audio = np.array([])

            result = stt.transcribe(empty_audio)
            # Should handle empty audio gracefully
            assert result == ""

    def test_get_language(self):
        """Test language detection."""
        with patch("src.stt.WhisperModel"):
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

    def test_transcribe_with_multiple_results(self):
        """Test transcription with multiple results."""
        with patch("src.stt.WhisperModel"):
            stt = SpeechToText()

            # Mock audio data
            mock_audio = np.array([0.1, 0.2, 0.3])

            # Mock multiple transcription results
            mock_result1 = MagicMock()
            mock_result1.text = "First part"
            mock_result2 = MagicMock()
            mock_result2.text = "Second part"

            stt._model.transcribe.return_value = (
                [mock_result1, mock_result2],
                {"language": "en"},
            )

            result = stt.transcribe(mock_audio)
            # Should concatenate all results with spaces
            assert result == "First part Second part"

    def test_transcribe_with_no_results(self):
        """Test transcription with no results."""
        with patch("src.stt.WhisperModel"):
            stt = SpeechToText()

            # Mock audio data
            mock_audio = np.array([0.1, 0.2, 0.3])

            # Mock empty results
            stt._model.transcribe.return_value = ([], {"language": "en"})

            result = stt.transcribe(mock_audio)
            # Should handle empty results gracefully
            assert result == ""

    def test_transcribe_with_large_audio(self):
        """Test transcription with large audio data."""
        with patch("src.stt.WhisperModel"):
            stt = SpeechToText()

            # Mock large audio data
            mock_audio = np.random.random(16000)  # 1 second at 16kHz

            # Mock transcription result
            mock_result = MagicMock()
            mock_result.text = "Large audio transcription"
            mock_result.language = "en"

            stt._model.transcribe.return_value = ([mock_result], {"language": "en"})

            result = stt.transcribe(mock_audio)
            assert result == "Large audio transcription"

    def test_transcribe_with_float_audio(self):
        """Test transcription with float audio data."""
        with patch("src.stt.WhisperModel"):
            stt = SpeechToText()

            # Mock float audio data
            mock_audio = np.array([0.1, -0.5, 0.8, -0.2], dtype=np.float32)

            # Mock transcription result
            mock_result = MagicMock()
            mock_result.text = "Float audio transcription"
            mock_result.language = "en"

            stt._model.transcribe.return_value = ([mock_result], {"language": "en"})

            result = stt.transcribe(mock_audio)
            assert result == "Float audio transcription"

    def test_model_initialization(self):
        """Test that the Whisper model is properly initialized."""
        with patch("src.stt.WhisperModel") as mock_model:
            stt = SpeechToText()

            # Check that WhisperModel was called
            mock_model.assert_called_once()

            # Check that the model is stored
            assert stt._model is not None

    def test_transcribe_calls_model(self):
        """Test that transcribe method calls the model correctly."""
        with patch("src.stt.WhisperModel"):
            stt = SpeechToText()

            # Mock audio data
            mock_audio = np.array([0.1, 0.2, 0.3])

            # Mock transcription result
            mock_result = MagicMock()
            mock_result.text = "Test transcription"
            mock_result.language = "en"

            stt._model.transcribe.return_value = ([mock_result], {"language": "en"})

            # Call transcribe
            stt.transcribe(mock_audio)

            # Check that model.transcribe was called with the correct parameters
            stt._model.transcribe.assert_called_once()
            call_args = stt._model.transcribe.call_args
            # call_args.args contains positional arguments, call_args.kwargs contains keyword arguments
            assert (
                "audio" in call_args.kwargs
            )  # Check that audio parameter is passed as keyword argument
            assert (
                "language" in call_args.kwargs
            )  # Check that language parameter is passed as keyword argument


if __name__ == "__main__":
    pytest.main([__file__])
