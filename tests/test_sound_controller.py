"""Tests for the Sound Controller module."""

from unittest.mock import MagicMock, call, patch

import pytest

# Import the module to test
from src.sound_controller import SoundController


class TestSoundController:
    """Test cases for SoundController class."""

    def test_sound_controller_initialization_success(self):
        """Test successful sound controller initialization."""
        # Create controller and manually set the interface to test the rest of the functionality
        controller = SoundController()

        # Since we can't easily mock the COM interfaces, we'll test the functionality
        # by manually setting the interface and testing other methods
        mock_interface = MagicMock()
        controller._volume_interface = mock_interface

        # Test that the interface is set correctly
        assert controller._volume_interface == mock_interface
        assert controller.is_available() is True

    @patch("src.sound_controller.AudioUtilities")
    def test_sound_controller_initialization_failure(self, mock_audio_utils):
        """Test sound controller initialization when audio setup fails."""
        # Mock audio setup failure
        mock_audio_utils.GetSpeakers.side_effect = Exception("Audio device not found")

        controller = SoundController()

        assert controller._volume_interface is None

    def test_get_volume_with_interface(self):
        """Test getting volume when audio interface is available."""
        controller = SoundController()

        # Mock the volume interface
        mock_interface = MagicMock()
        mock_interface.GetMasterVolumeLevelScalar.return_value = 0.75
        controller._volume_interface = mock_interface

        volume = controller.get_volume()

        assert volume == 75
        mock_interface.GetMasterVolumeLevelScalar.assert_called_once()

    def test_get_volume_without_interface(self):
        """Test getting volume when audio interface is not available."""
        controller = SoundController()
        controller._volume_interface = None

        volume = controller.get_volume()

        assert volume == 100

    def test_get_volume_exception_handling(self):
        """Test getting volume when interface raises exception."""
        controller = SoundController()

        # Mock the volume interface that raises exception
        mock_interface = MagicMock()
        mock_interface.GetMasterVolumeLevelScalar.side_effect = Exception(
            "Volume access denied"
        )
        controller._volume_interface = mock_interface

        volume = controller.get_volume()

        assert volume == 100

    def test_set_volume_with_interface(self):
        """Test setting volume when audio interface is available."""
        controller = SoundController()

        # Mock the volume interface
        mock_interface = MagicMock()
        controller._volume_interface = mock_interface

        controller.set_volume(50)

        mock_interface.SetMasterVolumeLevelScalar.assert_called_once_with(0.5, None)

    def test_set_volume_without_interface(self):
        """Test setting volume when audio interface is not available."""
        controller = SoundController()
        controller._volume_interface = None

        # Should not raise exception
        controller.set_volume(50)

    def test_set_volume_exception_handling(self):
        """Test setting volume when interface raises exception."""
        controller = SoundController()

        # Mock the volume interface that raises exception
        mock_interface = MagicMock()
        mock_interface.SetMasterVolumeLevelScalar.side_effect = Exception(
            "Volume control denied"
        )
        controller._volume_interface = mock_interface

        # Should not raise exception
        controller.set_volume(50)

    def test_set_volume_clamping_upper_bound(self):
        """Test volume clamping to upper bound (100%)."""
        controller = SoundController()

        # Mock the volume interface
        mock_interface = MagicMock()
        controller._volume_interface = mock_interface

        controller.set_volume(150)  # Above 100%

        mock_interface.SetMasterVolumeLevelScalar.assert_called_once_with(1.0, None)

    def test_set_volume_clamping_lower_bound(self):
        """Test volume clamping to lower bound (0%)."""
        controller = SoundController()

        # Mock the volume interface
        mock_interface = MagicMock()
        controller._volume_interface = mock_interface

        controller.set_volume(-10)  # Below 0%

        mock_interface.SetMasterVolumeLevelScalar.assert_called_once_with(0.0, None)

    def test_set_volume_edge_cases(self):
        """Test volume setting with edge case values."""
        controller = SoundController()

        # Mock the volume interface
        mock_interface = MagicMock()
        controller._volume_interface = mock_interface

        # Test edge cases
        controller.set_volume(0)
        controller.set_volume(100)
        controller.set_volume(50)

        # Verify calls
        expected_calls = [call(0.0, None), call(1.0, None), call(0.5, None)]
        mock_interface.SetMasterVolumeLevelScalar.assert_has_calls(expected_calls)

    def test_reduce_volume_normal_case(self):
        """Test volume reduction with normal parameters."""
        controller = SoundController()

        # Mock get_volume and set_volume methods
        with patch.object(controller, "get_volume", return_value=80):
            with patch.object(controller, "set_volume") as mock_set_volume:
                original, target = controller.reduce_volume(factor=0.5, min_percent=20)

                assert original == 80
                assert target == 40  # 80 * 0.5 = 40, which is above min_percent=20
                mock_set_volume.assert_called_once_with(40)

    def test_reduce_volume_below_minimum(self):
        """Test volume reduction when calculated volume is below minimum."""
        controller = SoundController()

        # Mock get_volume and set_volume methods
        with patch.object(controller, "get_volume", return_value=80):
            with patch.object(controller, "set_volume") as mock_set_volume:
                original, target = controller.reduce_volume(factor=0.1, min_percent=20)

                assert original == 80
                assert target == 20  # 80 * 0.1 = 8, but min_percent=20, so target=20
                mock_set_volume.assert_called_once_with(20)

    def test_reduce_volume_default_parameters(self):
        """Test volume reduction with default parameters."""
        controller = SoundController()

        # Mock get_volume and set_volume methods
        with patch.object(controller, "get_volume", return_value=100):
            with patch.object(controller, "set_volume") as mock_set_volume:
                original, target = controller.reduce_volume()

                assert original == 100
                assert target == 30  # 100 * 0.3 = 30, which is above min_percent=10
                mock_set_volume.assert_called_once_with(30)

    def test_restore_volume(self):
        """Test volume restoration."""
        controller = SoundController()

        # Mock set_volume method
        with patch.object(controller, "set_volume") as mock_set_volume:
            controller.restore_volume(75)

            mock_set_volume.assert_called_once_with(75)

    def test_is_available_with_interface(self):
        """Test availability check when interface is available."""
        controller = SoundController()
        controller._volume_interface = MagicMock()

        assert controller.is_available() is True

    def test_is_available_without_interface(self):
        """Test availability check when interface is not available."""
        controller = SoundController()
        controller._volume_interface = None

        assert controller.is_available() is False

    def test_is_available_with_none_interface(self):
        """Test availability check when interface is explicitly None."""
        controller = SoundController()
        controller._volume_interface = None

        assert controller.is_available() is False


if __name__ == "__main__":
    pytest.main([__file__])
