"""Tests for the STT module."""
import pytest
from unittest.mock import patch, MagicMock
import numpy as np

# Import the module to test
from src.stt import SpeechToText


class TestSpeechToText:
    """Test cases for SpeechToText class."""
    
    def test_stt_initialization(self):
        """Test SpeechToText initialization."""
        with patch('src.stt.FasterWhisperModel') as mock_model:
            stt = SpeechToText()
            assert stt is not None
            assert hasattr(stt, 'model')
    
    def test_transcribe_audio(self):
        """Test audio transcription."""
        with patch('src.stt.FasterWhisperModel') as mock_model:
            stt = SpeechToText()
            
            # Mock audio data
            mock_audio = np.array([0.1, 0.2, 0.3])
            
            # Mock transcription result
            mock_result = MagicMock()
            mock_result.text = "Hello world"
            mock_result.language = "en"
            
            # Mock the model's transcribe method
            stt.model.transcribe.return_value = [mock_result]
            
            result = stt.transcribe(mock_audio)
            assert result is not None
            assert result.text == "Hello world"
            assert result.language == "en"
    
    def test_transcribe_empty_audio(self):
        """Test transcription with empty audio."""
        with patch('src.stt.FasterWhisperModel') as mock_model:
            stt = SpeechToText()
            
            # Empty audio
            empty_audio = np.array([])
            
            result = stt.transcribe(empty_audio)
            # Should handle empty audio gracefully
            assert result is None or result.text == ""
    
    def test_get_language(self):
        """Test language detection."""
        with patch('src.stt.FasterWhisperModel') as mock_model:
            stt = SpeechToText()
            
            # Mock audio data
            mock_audio = np.array([0.1, 0.2, 0.3])
            
            # Mock language detection result
            mock_result = MagicMock()
            mock_result.language = "de"
            
            stt.model.transcribe.return_value = [mock_result]
            
            result = stt.transcribe(mock_audio)
            assert result.language == "de"


if __name__ == '__main__':
    pytest.main([__file__])
