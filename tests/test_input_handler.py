"""Tests for the Input Handler module."""
from unittest.mock import MagicMock, patch

import pytest

# Import the module to test
from src.input_handler import InputHandler


class TestInputHandler:
    """Test cases for InputHandler class."""

    def test_input_handler_initialization(self):
        """Test InputHandler initialization."""
        handler = InputHandler()
        assert handler.mouse_listener is None
        assert handler.keyboard_listener is None
        assert handler.mouse_callback is None
        assert handler.keyboard_callback is None

    @patch("src.input_handler.mouse.Listener")
    def test_setup_mouse_listener(self, mock_mouse_listener):
        """Test mouse listener setup."""
        handler = InputHandler()
        mock_callback = MagicMock()

        # Mock the listener instance
        mock_listener_instance = MagicMock()
        mock_mouse_listener.return_value = mock_listener_instance

        handler.setup_mouse_listener(mock_callback)

        assert handler.mouse_callback == mock_callback
        assert handler.mouse_listener == mock_listener_instance
        mock_mouse_listener.assert_called_once_with(on_click=handler._on_mouse_click)
        mock_listener_instance.start.assert_called_once()

    @patch("src.input_handler.keyboard.Listener")
    def test_setup_keyboard_listener(self, mock_keyboard_listener):
        """Test keyboard listener setup."""
        handler = InputHandler()
        mock_callback = MagicMock()

        # Mock the listener instance
        mock_listener_instance = MagicMock()
        mock_keyboard_listener.return_value = mock_listener_instance

        handler.setup_keyboard_listener(mock_callback)

        assert handler.keyboard_callback == mock_callback
        assert handler.keyboard_listener == mock_listener_instance
        mock_keyboard_listener.assert_called_once_with(on_press=handler._on_key_press, on_release=handler._on_key_release)
        mock_listener_instance.start.assert_called_once()

    def test_on_mouse_click_with_callback(self):
        """Test mouse click handling with callback."""
        handler = InputHandler()
        mock_callback = MagicMock()
        handler.mouse_callback = mock_callback

        # Test mouse click
        handler._on_mouse_click(100, 200, "left", True)

        mock_callback.assert_called_once_with(100, 200, "left", True)

    def test_on_mouse_click_without_callback(self):
        """Test mouse click handling without callback."""
        handler = InputHandler()
        # No callback set

        # Should not raise an exception
        handler._on_mouse_click(100, 200, "left", True)

    def test_on_mouse_click_callback_exception(self):
        """Test mouse click handling when callback raises exception."""
        handler = InputHandler()

        def failing_callback(x, y, button, pressed):
            raise ValueError("Test exception")

        handler.mouse_callback = failing_callback

        # Should handle exception gracefully
        handler._on_mouse_click(100, 200, "left", True)

    def test_on_key_press_with_callback(self):
        """Test key press handling with callback."""
        handler = InputHandler()
        mock_callback = MagicMock()
        handler.keyboard_callback = mock_callback

        # Test key press
        test_key = "a"
        handler._on_key_press(test_key)

        mock_callback.assert_called_once_with(test_key, True)

    def test_on_key_press_without_callback(self):
        """Test key press handling without callback."""
        handler = InputHandler()
        # No callback set

        # Should not raise an exception
        handler._on_key_press("a")

    def test_on_key_press_callback_exception(self):
        """Test key press handling when callback raises exception."""
        handler = InputHandler()

        def failing_callback(key, pressed):
            raise ValueError("Test exception")

        handler.keyboard_callback = failing_callback

        # Should handle exception gracefully
        handler._on_key_press("a")

    def test_on_key_release_with_callback(self):
        """Test key release handling with callback."""
        handler = InputHandler()
        mock_callback = MagicMock()
        handler.keyboard_callback = mock_callback

        # Test key release
        test_key = "a"
        handler._on_key_release(test_key)

        mock_callback.assert_called_once_with(test_key, False)

    def test_on_key_release_without_callback(self):
        """Test key release handling without callback."""
        handler = InputHandler()
        # No callback set

        # Should not raise an exception
        handler._on_key_release("a")

    def test_on_key_release_callback_exception(self):
        """Test key release handling when callback raises exception."""
        handler = InputHandler()

        def failing_callback(key, pressed):
            raise ValueError("Test exception")

        handler.keyboard_callback = failing_callback

        # Should handle exception gracefully
        handler._on_key_release("a")

    def test_stop_with_active_listeners(self):
        """Test stopping active listeners."""
        handler = InputHandler()

        # Mock listeners
        mock_mouse_listener = MagicMock()
        mock_keyboard_listener = MagicMock()

        handler.mouse_listener = mock_mouse_listener
        handler.keyboard_listener = mock_keyboard_listener

        handler.stop()

        mock_mouse_listener.stop.assert_called_once()
        mock_keyboard_listener.stop.assert_called_once()
        assert handler.mouse_listener is None
        assert handler.keyboard_listener is None

    def test_stop_without_listeners(self):
        """Test stopping without active listeners."""
        handler = InputHandler()
        # No listeners set

        # Should not raise an exception
        handler.stop()

    def test_is_active_with_mouse_listener(self):
        """Test is_active when mouse listener is active."""
        handler = InputHandler()

        # Mock active mouse listener
        mock_mouse_listener = MagicMock()
        mock_mouse_listener.is_alive.return_value = True
        handler.mouse_listener = mock_mouse_listener
        handler.keyboard_listener = None

        assert handler.is_active() is True

    def test_is_active_with_keyboard_listener(self):
        """Test is_active when keyboard listener is active."""
        handler = InputHandler()

        # Mock active keyboard listener
        mock_keyboard_listener = MagicMock()
        mock_keyboard_listener.is_alive.return_value = True
        handler.keyboard_listener = mock_keyboard_listener
        handler.mouse_listener = None

        assert handler.is_active() is True

    def test_is_active_with_inactive_listeners(self):
        """Test is_active when all listeners are inactive."""
        handler = InputHandler()

        # Mock inactive listeners
        mock_mouse_listener = MagicMock()
        mock_mouse_listener.is_alive.return_value = False
        mock_keyboard_listener = MagicMock()
        mock_keyboard_listener.is_alive.return_value = False

        handler.mouse_listener = mock_mouse_listener
        handler.keyboard_listener = mock_keyboard_listener

        assert handler.is_active() is False

    def test_is_active_without_listeners(self):
        """Test is_active without any listeners."""
        handler = InputHandler()
        # No listeners set

        assert handler.is_active() is False


if __name__ == "__main__":
    pytest.main([__file__])
