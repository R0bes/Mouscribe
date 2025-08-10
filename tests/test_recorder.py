"""Tests for the recorder module."""
import pytest
from unittest.mock import patch, MagicMock
import numpy as np

# Import the module to test
from src.recorder import AudioRecorder


class TestAudioRecorder:
    """Test cases for AudioRecorder class."""
    
    def test_recorder_initialization(self):
        """Test AudioRecorder initialization."""
        with patch('src.recorder.sd') as mock_sd:
            recorder = AudioRecorder()
            assert recorder is not None
            assert hasattr(recorder, 'sample_rate')
            assert hasattr(recorder, 'channels')
    
    def test_start_recording(self):
        """Test starting recording."""
        with patch('src.recorder.sd') as mock_sd:
            recorder = AudioRecorder()
            recorder.start_recording()
            # Should call sd.InputStream
            mock_sd.InputStream.assert_called_once()
    
    def test_stop_recording(self):
        """Test stopping recording."""
        with patch('src.recorder.sd') as mock_sd:
            recorder = AudioRecorder()
            # Mock the stream
            mock_stream = MagicMock()
            recorder.stream = mock_stream
            
            recorder.stop_recording()
            # Should call stop and close on stream
            mock_stream.stop.assert_called_once()
            mock_stream.close.assert_called_once()
    
    def test_get_audio_data(self):
        """Test getting audio data."""
        with patch('src.recorder.sd') as mock_sd:
            recorder = AudioRecorder()
            # Mock audio data
            mock_audio = np.array([0.1, 0.2, 0.3])
            recorder.audio_data = mock_audio
            
            result = recorder.get_audio_data()
            assert result is not None
            assert len(result) == 3
    
    def test_is_recording(self):
        """Test recording status."""
        with patch('src.recorder.sd') as mock_sd:
            recorder = AudioRecorder()
            # Initially not recording
            assert not recorder.is_recording()
            
            # Start recording
            recorder.start_recording()
            assert recorder.is_recording()
            
            # Stop recording
            recorder.stop_recording()
            assert not recorder.is_recording()


if __name__ == '__main__':
    pytest.main([__file__])
