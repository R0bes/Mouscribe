"""Tests for the recorder module."""
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

# Import the module to test
from src.recorder import AudioRecorder


class TestAudioRecorder:
    """Test cases for AudioRecorder class."""

    def test_recorder_initialization(self):
        """Test AudioRecorder initialization."""
        with patch("src.recorder.sd") as mock_sd:
            recorder = AudioRecorder()
            assert recorder is not None
            assert hasattr(recorder, "sample_rate_hz")
            assert hasattr(recorder, "num_channels")

    def test_start_recording(self):
        """Test starting recording."""
        with patch("src.recorder.sd") as mock_sd:
            recorder = AudioRecorder()
            recorder.start_recording()
            # Should call sd.InputStream
            mock_sd.InputStream.assert_called_once()

    def test_stop_recording(self):
        """Test stopping recording."""
        with patch("src.recorder.sd") as mock_sd:
            recorder = AudioRecorder()
            # Mock the stream
            mock_stream = MagicMock()
            recorder._stream = mock_stream

            recorder.stop_recording()
            # Should call stop and close on stream
            mock_stream.stop.assert_called_once()
            mock_stream.close.assert_called_once()

    def test_get_audio_data(self):
        """Test getting audio data."""
        with patch("src.recorder.sd") as mock_sd:
            recorder = AudioRecorder()
            # Mock audio data
            mock_audio = np.array([0.1, 0.2, 0.3])
            recorder._chunks = [mock_audio]

            result = recorder.stop_recording()
            assert result is not None
            assert len(result) == 3

    def test_is_recording(self):
        """Test recording status."""
        with patch("src.recorder.sd") as mock_sd:
            recorder = AudioRecorder()
            # Initially not recording
            assert not recorder._active

            # Start recording
            recorder.start_recording()
            assert recorder._active

            # Stop recording
            recorder.stop_recording()
            assert not recorder._active


if __name__ == "__main__":
    pytest.main([__file__])
