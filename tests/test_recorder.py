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
        with patch("src.recorder.sd"):
            recorder = AudioRecorder()
            assert recorder is not None
            assert hasattr(recorder, "sample_rate_hz")
            assert hasattr(recorder, "num_channels")

    def test_recorder_initialization_with_custom_values(self):
        """Test AudioRecorder initialization with custom values."""
        with patch("src.recorder.sd"):
            recorder = AudioRecorder(sample_rate_hz=48000, num_channels=2)
            assert recorder.sample_rate_hz == 48000
            assert recorder.num_channels == 2

    def test_start_recording(self):
        """Test starting recording."""
        with patch("src.recorder.sd") as mock_sd:
            recorder = AudioRecorder()
            recorder.start_recording()
            # Should call sd.InputStream
            mock_sd.InputStream.assert_called_once()

    def test_start_recording_when_already_active(self):
        """Test starting recording when already active."""
        with patch("src.recorder.sd"):
            recorder = AudioRecorder()
            recorder._active = True
            recorder.start_recording()
            # Should not create new stream when already active

    def test_stop_recording(self):
        """Test stopping recording."""
        with patch("src.recorder.sd"):
            recorder = AudioRecorder()
            # Mock the stream and set recording as active
            mock_stream = MagicMock()
            recorder._stream = mock_stream
            recorder._active = True

            recorder.stop_recording()
            # Should call stop and close on stream
            mock_stream.stop.assert_called_once()
            mock_stream.close.assert_called_once()

    def test_get_audio_data(self):
        """Test getting audio data."""
        with patch("src.recorder.sd"):
            recorder = AudioRecorder()
            # Mock audio data and set recording as active
            mock_audio = np.array([0.1, 0.2, 0.3])
            recorder._chunks = [mock_audio]
            recorder._active = True
            recorder._stream = MagicMock()

            result = recorder.stop_recording()
            assert result is not None
            assert len(result) == 3

    def test_get_audio_data_multichannel(self):
        """Test getting audio data with multichannel audio."""
        with patch("src.recorder.sd"):
            recorder = AudioRecorder()
            # Mock multichannel audio data
            mock_audio = np.array([[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]])
            recorder._chunks = [mock_audio]
            recorder._active = True
            recorder._stream = MagicMock()

            result = recorder.stop_recording()
            assert result is not None
            assert len(result) == 3
            # Should be downmixed to mono
            assert result.ndim == 1

    def test_is_recording(self):
        """Test recording status."""
        with patch("src.recorder.sd"):
            recorder = AudioRecorder()
            # Initially not recording
            assert not recorder._active

            # Start recording
            recorder.start_recording()
            assert recorder._active

            # Stop recording
            recorder.stop_recording()
            assert not recorder._active

    def test_stop_recording_when_not_active(self):
        """Test stopping recording when not active."""
        with patch("src.recorder.sd"):
            recorder = AudioRecorder()
            recorder._active = False

            result = recorder.stop_recording()
            # Should return empty array when not active
            assert len(result) == 0
            assert result.dtype == np.float32

    def test_stop_recording_with_no_chunks(self):
        """Test stopping recording with no audio chunks."""
        with patch("src.recorder.sd"):
            recorder = AudioRecorder()
            recorder._active = True
            recorder._stream = MagicMock()
            recorder._chunks = []

            result = recorder.stop_recording()
            # Should return empty array when no chunks
            assert len(result) == 0
            assert result.dtype == np.float32

    def test_callback_when_not_active(self):
        """Test callback when recording is not active."""
        recorder = AudioRecorder()
        recorder._active = False

        # Mock input data
        mock_indata = np.array([0.1, 0.2, 0.3])

        # Call callback
        recorder._callback(mock_indata, 1, 0, None)

        # Should not add to chunks when not active
        assert len(recorder._chunks) == 0

    def test_callback_when_active(self):
        """Test callback when recording is active."""
        recorder = AudioRecorder()
        recorder._active = True

        # Mock input data
        mock_indata = np.array([0.1, 0.2, 0.3])

        # Call callback
        recorder._callback(mock_indata, 1, 0, None)

        # Should add to chunks when active
        assert len(recorder._chunks) == 1
        assert np.array_equal(recorder._chunks[0], mock_indata)

    def test_callback_with_status(self):
        """Test callback with status (should not crash)."""
        recorder = AudioRecorder()
        recorder._active = True

        # Mock input data
        mock_indata = np.array([0.1, 0.2, 0.3])

        # Call callback with status (should not crash)
        recorder._callback(mock_indata, 1, 0, "some_status")

        # Should still add to chunks
        assert len(recorder._chunks) == 1


if __name__ == "__main__":
    pytest.main([__file__])
