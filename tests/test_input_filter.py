# tests/test_input_filter.py - Tests for simplified input system
"""
Tests for the simplified input handling system.
Tests InputHandler directly without complex filtering.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from pynput import keyboard, mouse

from src.input.input_handler import InputHandler
from src.utils.config import Config


class TestSimplifiedInputHandler:
    """Test the simplified input handler."""

    def test_input_handler_initialization(self):
        """Test input handler initialization."""
        mock_callback = Mock()
        handler = InputHandler(mock_callback, mock_callback)

        assert handler.primary_callback == mock_callback
        assert handler.secondary_callback == mock_callback
        assert handler.config is not None
        assert handler.mapper is not None

    def test_input_handler_stop(self):
        """Test input handler stop functionality."""
        mock_callback = Mock()
        handler = InputHandler(mock_callback, mock_callback)

        # Mock the listeners
        handler._ml = Mock()
        handler._kl = Mock()
        handler._active = True

        handler.stop()

        assert handler._ml is None
        assert handler._kl is None
        assert handler._active is False

    def test_debouncer_functionality(self):
        """Test debouncer functionality."""
        mock_callback = Mock()
        handler = InputHandler(mock_callback, mock_callback)

        # Test debouncing with time delay simulation
        key = "test_key"
        assert not handler._db.hit(key, 100)  # First hit
        assert handler._db.hit(key, 100)  # Second hit within window

        # Simulate time passing by manually setting timestamp
        import time

        handler._db._ts[key] = time.time() - 0.2  # 200ms ago

        assert not handler._db.hit(key, 100)  # Third hit after window

    def test_configuration_loading(self):
        """Test configuration loading."""
        config = Config()

        assert config.primary_name == "m_x2"
        assert config.secondary_name == "m_x1"
        assert config.primary_type == "mouse_button"
        assert config.secondary_type == "mouse_button"

    def test_callback_assignment(self):
        """Test callback assignment."""
        primary_callback = Mock()
        secondary_callback = Mock()

        handler = InputHandler(primary_callback, secondary_callback)

        assert handler.primary_callback == primary_callback
        assert handler.secondary_callback == secondary_callback

    def test_mouse_listener_setup(self):
        """Test mouse listener setup."""
        mock_callback = Mock()
        handler = InputHandler(mock_callback, mock_callback)

        # Mock pynput
        with patch("pynput.mouse.Listener") as mock_listener:
            mock_listener.return_value.start.return_value = None
            handler._start()

            assert handler._ml is not None
            assert handler._active is True

    def test_keyboard_listener_setup(self):
        """Test keyboard listener setup."""
        mock_callback = Mock()
        handler = InputHandler(mock_callback, mock_callback)

        # Mock pynput
        with patch("pynput.keyboard.Listener") as mock_listener:
            mock_listener.return_value.start.return_value = None
            handler._start()

            assert handler._kl is not None
            assert handler._active is True

    def test_error_handling(self):
        """Test error handling in input handler."""
        mock_callback = Mock()

        # Test with invalid configuration by mocking the Config constructor
        with patch("src.input.input_handler.Config") as mock_config_class:
            mock_config_class.side_effect = Exception("Config error")

            with pytest.raises(Exception):
                InputHandler(mock_callback, mock_callback)

    def test_configuration_values(self):
        """Test configuration values are correct."""
        config = Config()

        # Test primary button
        assert config.primary_name == "m_x2"
        assert config.primary_type == "mouse_button"
        assert config.primary_method == {"click": True}

        # Test secondary button
        assert config.secondary_name == "m_x1"
        assert config.secondary_type == "mouse_button"
        assert config.secondary_method == {"hold": 1}

    def test_callback_chain(self):
        """Test callback chain execution."""
        primary_callback = Mock()
        secondary_callback = Mock()

        handler = InputHandler(primary_callback, secondary_callback)

        # Test callback triggering
        handler._trigger_callback(primary_callback, True)
        primary_callback.assert_called_once_with(True)

        handler._trigger_callback(secondary_callback, False)
        secondary_callback.assert_called_once_with(False)

    def test_is_active_method(self):
        """Test is_active method."""
        mock_callback = Mock()
        handler = InputHandler(mock_callback, mock_callback)

        # Initially should be active
        assert handler.is_active() is True

        # After stop should be inactive
        handler.stop()
        assert handler.is_active() is False


class TestInputHandlerIntegration:
    """Integration tests for input handler."""

    def test_input_handler_with_mock_callbacks(self):
        """Test input handler with mock callbacks."""
        primary_callback = Mock()
        secondary_callback = Mock()

        handler = InputHandler(primary_callback, secondary_callback)

        # Verify callbacks are set
        assert handler.primary_callback == primary_callback
        assert handler.secondary_callback == secondary_callback

        # Cleanup
        handler.stop()

    def test_input_handler_lifecycle(self):
        """Test complete input handler lifecycle."""
        mock_callback = Mock()
        handler = InputHandler(mock_callback, mock_callback)

        # Verify active state
        assert handler.is_active() is True

        # Stop and verify inactive state
        handler.stop()
        assert handler.is_active() is False

    def test_configuration_integration(self):
        """Test configuration integration."""
        config = Config()
        handler = InputHandler(Mock(), Mock())

        # Verify configuration is loaded
        assert handler.config.primary_name == config.primary_name
        assert handler.config.secondary_name == config.secondary_name

        handler.stop()

    def test_debouncer_integration(self):
        """Test debouncer integration."""
        handler = InputHandler(Mock(), Mock())

        # Test debouncer is working
        key = "mouse:left:down"
        assert not handler._db.hit(key, 100)
        assert handler._db.hit(key, 100)

        handler.stop()

    def test_filter_integration(self):
        """Test that input filtering is simplified."""
        handler = InputHandler(Mock(), Mock())

        # Verify no complex filtering
        assert not hasattr(handler, "filter")
        assert hasattr(handler, "_trigger_callback")

        handler.stop()

    def test_mapper_integration(self):
        """Test button mapper integration."""
        handler = InputHandler(Mock(), Mock())

        # Verify mapper is available
        assert handler.mapper is not None
        assert hasattr(handler.mapper, "get_primary_mouse_button")
        assert hasattr(handler.mapper, "get_secondary_mouse_button")

        handler.stop()

    def test_listener_setup(self):
        """Test listener setup integration."""
        handler = InputHandler(Mock(), Mock())

        # Verify listeners are created
        assert handler._ml is not None
        assert handler._kl is not None

        handler.stop()

    def test_error_handling_integration(self):
        """Test error handling integration."""
        # Test with invalid callbacks
        handler = InputHandler(None, None)

        # Should not crash with None callbacks
        handler._trigger_callback(None, True)

        handler.stop()

    def test_configuration_validation(self):
        """Test configuration validation."""
        config = Config()

        # Verify required properties exist
        assert hasattr(config, "primary_name")
        assert hasattr(config, "secondary_name")
        assert hasattr(config, "primary_type")
        assert hasattr(config, "secondary_type")

    def test_callback_chain(self):
        """Test complete callback chain."""
        primary_callback = Mock()
        secondary_callback = Mock()

        handler = InputHandler(primary_callback, secondary_callback)

        # Test callback execution
        handler._trigger_callback(primary_callback, True)
        primary_callback.assert_called_once_with(True)

        handler._trigger_callback(secondary_callback, False)
        secondary_callback.assert_called_once_with(False)

        handler.stop()
