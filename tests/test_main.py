# tests/test_main.py - Tests for main application functionality
"""
Tests for the main Mauscribe application functionality.
Focuses on basic initialization and error handling to improve coverage.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Import the main application class
from src.main import MauscribeApp


class TestMauscribeApp:
    """Test the main Mauscribe application class."""

    @patch("src.main.SoundController")
    @patch("src.main.InputHandler")
    @patch("src.main.SpeechToText")
    @patch("src.main.AudioRecorder")
    @patch("src.main.SpellGrammarChecker")
    @patch("src.main.Config")
    def test_app_initialization_success(
        self,
        mock_config,
        mock_spell_checker,
        mock_recorder,
        mock_stt,
        mock_input_handler,
        mock_sound_controller,
    ):
        """Test successful application initialization."""
        # Mock all dependencies
        mock_config_instance = Mock()
        mock_config_instance.debug_level = "INFO"
        mock_config.return_value = mock_config_instance

        mock_sound_controller_instance = Mock()
        mock_sound_controller_instance.is_available.return_value = True
        mock_sound_controller.return_value = mock_sound_controller_instance

        mock_input_handler_instance = Mock()
        mock_input_handler.return_value = mock_input_handler_instance

        mock_stt_instance = Mock()
        mock_stt.return_value = mock_stt_instance

        mock_recorder_instance = Mock()
        mock_recorder.return_value = mock_recorder_instance

        mock_spell_checker_instance = Mock()
        mock_spell_checker.return_value = mock_spell_checker_instance

        # Create app instance
        app = MauscribeApp()

        # Verify all components were initialized
        assert app.config == mock_config_instance
        assert app.sound_controller == mock_sound_controller_instance
        assert app.input_handler == mock_input_handler_instance
        assert app.stt == mock_stt_instance
        assert app.recorder == mock_recorder_instance
        assert app.spell_checker == mock_spell_checker_instance
        assert app.is_recording is False
        assert app.recording_thread is None
        assert app.system_tray is None

    @patch("src.main.SoundController")
    @patch("src.main.InputHandler")
    @patch("src.main.SpeechToText")
    @patch("src.main.AudioRecorder")
    @patch("src.main.SpellGrammarChecker")
    @patch("src.main.Config")
    def test_app_initialization_sound_controller_failure(
        self,
        mock_config,
        mock_spell_checker,
        mock_recorder,
        mock_stt,
        mock_input_handler,
        mock_sound_controller,
    ):
        """Test application initialization with sound controller failure."""
        # Mock all dependencies
        mock_config_instance = Mock()
        mock_config_instance.debug_level = "INFO"
        mock_config.return_value = mock_config_instance

        mock_sound_controller.side_effect = Exception("Sound controller failed")

        mock_input_handler_instance = Mock()
        mock_input_handler.return_value = mock_input_handler_instance

        mock_stt_instance = Mock()
        mock_stt.return_value = mock_stt_instance

        mock_recorder_instance = Mock()
        mock_recorder.return_value = mock_recorder_instance

        mock_spell_checker_instance = Mock()
        mock_spell_checker.return_value = mock_spell_checker_instance

        # Create app instance
        app = MauscribeApp()

        # Verify sound controller is None but app continues
        assert app.sound_controller is None
        assert app.config == mock_config_instance
        assert app.input_handler == mock_input_handler_instance

    @patch("src.main.SoundController")
    @patch("src.main.InputHandler")
    @patch("src.main.SpeechToText")
    @patch("src.main.AudioRecorder")
    @patch("src.main.SpellGrammarChecker")
    @patch("src.main.Config")
    def test_app_initialization_sound_controller_unavailable(
        self,
        mock_config,
        mock_spell_checker,
        mock_recorder,
        mock_stt,
        mock_input_handler,
        mock_sound_controller,
    ):
        """Test application initialization with unavailable sound controller."""
        # Mock all dependencies
        mock_config_instance = Mock()
        mock_config_instance.debug_level = "INFO"
        mock_config.return_value = mock_config_instance

        mock_sound_controller_instance = Mock()
        mock_sound_controller_instance.is_available.return_value = False
        mock_sound_controller.return_value = mock_sound_controller_instance

        mock_input_handler_instance = Mock()
        mock_input_handler.return_value = mock_input_handler_instance

        mock_stt_instance = Mock()
        mock_stt.return_value = mock_stt_instance

        mock_recorder_instance = Mock()
        mock_recorder.return_value = mock_recorder_instance

        mock_spell_checker_instance = Mock()
        mock_spell_checker.return_value = mock_spell_checker_instance

        # Create app instance
        app = MauscribeApp()

        # Verify sound controller is available but returns False
        assert app.sound_controller == mock_sound_controller_instance
        assert app.sound_controller.is_available() is False

    @patch("src.main.SoundController")
    @patch("src.main.InputHandler")
    @patch("src.main.SpeechToText")
    @patch("src.main.AudioRecorder")
    @patch("src.main.SpellGrammarChecker")
    @patch("src.main.Config")
    def test_app_initialization_input_handler_failure(
        self,
        mock_config,
        mock_spell_checker,
        mock_recorder,
        mock_stt,
        mock_input_handler,
        mock_sound_controller,
    ):
        """Test application initialization with input handler failure."""
        # Mock all dependencies
        mock_config_instance = Mock()
        mock_config.return_value = mock_config_instance

        mock_sound_controller_instance = Mock()
        mock_sound_controller_instance.is_available.return_value = True
        mock_sound_controller.return_value = mock_sound_controller_instance

        mock_input_handler.side_effect = Exception("Input handler failed")

        # This should cause sys.exit(1)
        with pytest.raises(SystemExit):
            MauscribeApp()

    @patch("src.main.SoundController")
    @patch("src.main.InputHandler")
    @patch("src.main.SpeechToText")
    @patch("src.main.AudioRecorder")
    @patch("src.main.SpellGrammarChecker")
    @patch("src.main.Config")
    def test_app_initialization_stt_failure(
        self,
        mock_config,
        mock_spell_checker,
        mock_recorder,
        mock_stt,
        mock_input_handler,
        mock_sound_controller,
    ):
        """Test application initialization with STT failure."""
        # Mock all dependencies
        mock_config_instance = Mock()
        mock_config_instance.debug_level = "INFO"
        mock_config.return_value = mock_config_instance

        mock_sound_controller_instance = Mock()
        mock_sound_controller_instance.is_available.return_value = True
        mock_sound_controller.return_value = mock_sound_controller_instance

        mock_input_handler_instance = Mock()
        mock_input_handler.return_value = mock_input_handler_instance

        mock_stt.side_effect = Exception("STT failed")

        # This should cause sys.exit(1)
        with pytest.raises(SystemExit):
            MauscribeApp()

    @patch("src.main.SoundController")
    @patch("src.main.InputHandler")
    @patch("src.main.SpeechToText")
    @patch("src.main.AudioRecorder")
    @patch("src.main.SpellGrammarChecker")
    @patch("src.main.Config")
    def test_app_initialization_recorder_failure(
        self,
        mock_config,
        mock_spell_checker,
        mock_recorder,
        mock_stt,
        mock_input_handler,
        mock_sound_controller,
    ):
        """Test application initialization with recorder failure."""
        # Mock all dependencies
        mock_config_instance = Mock()
        mock_config_instance.debug_level = "INFO"
        mock_config.return_value = mock_config_instance

        mock_sound_controller_instance = Mock()
        mock_sound_controller_instance.is_available.return_value = True
        mock_sound_controller.return_value = mock_sound_controller_instance

        mock_input_handler_instance = Mock()
        mock_input_handler.return_value = mock_input_handler_instance

        mock_stt_instance = Mock()
        mock_stt.return_value = mock_stt_instance

        mock_recorder.side_effect = Exception("Recorder failed")

        # This should cause sys.exit(1)
        with pytest.raises(SystemExit):
            MauscribeApp()

    @patch("src.main.SoundController")
    @patch("src.main.InputHandler")
    @patch("src.main.SpeechToText")
    @patch("src.main.AudioRecorder")
    @patch("src.main.SpellGrammarChecker")
    @patch("src.main.Config")
    def test_app_initialization_spell_checker_failure(
        self,
        mock_config,
        mock_spell_checker,
        mock_recorder,
        mock_stt,
        mock_input_handler,
        mock_sound_controller,
    ):
        """Test application initialization with spell checker failure."""
        # Mock all dependencies
        mock_config_instance = Mock()
        mock_config_instance.debug_level = "INFO"
        mock_config.return_value = mock_config_instance

        mock_sound_controller_instance = Mock()
        mock_sound_controller_instance.is_available.return_value = True
        mock_sound_controller.return_value = mock_sound_controller_instance

        mock_input_handler_instance = Mock()
        mock_input_handler.return_value = mock_input_handler_instance

        mock_stt_instance = Mock()
        mock_stt.return_value = mock_stt_instance

        mock_recorder_instance = Mock()
        mock_recorder.return_value = mock_recorder_instance

        mock_spell_checker.side_effect = Exception("Spell checker failed")

        # This should cause sys.exit(1)
        with pytest.raises(SystemExit):
            MauscribeApp()

    @patch("src.main.SoundController")
    @patch("src.main.InputHandler")
    @patch("src.main.SpeechToText")
    @patch("src.main.AudioRecorder")
    @patch("src.main.SpellGrammarChecker")
    @patch("src.main.Config")
    def test_app_initialization_config_failure(
        self,
        mock_config,
        mock_spell_checker,
        mock_recorder,
        mock_stt,
        mock_input_handler,
        mock_sound_controller,
    ):
        """Test application initialization with config failure."""
        # Mock config to fail
        mock_config.side_effect = Exception("Config failed")

        # This should cause sys.exit(1)
        with pytest.raises(SystemExit):
            MauscribeApp()

    def test_app_properties(self):
        """Test basic app properties after initialization."""
        with patch("src.main.SoundController"), patch("src.main.InputHandler"), patch(
            "src.main.SpeechToText"
        ), patch("src.main.AudioRecorder"), patch(
            "src.main.SpellGrammarChecker"
        ), patch(
            "src.main.Config"
        ):
            app = MauscribeApp()

            # Test basic properties
            assert hasattr(app, "is_recording")
            assert hasattr(app, "recording_thread")
            assert hasattr(app, "system_tray")
            assert hasattr(app, "_original_volume")
            assert hasattr(app, "_last_click_time")
            assert app._click_debounce_ms == 500

            # Test initial values
            assert app.is_recording is False
            assert app.recording_thread is None
            assert app.system_tray is None
            assert app._original_volume is None
            assert app._last_click_time == 0

    @patch("src.main.SoundController")
    @patch("src.main.InputHandler")
    @patch("src.main.SpeechToText")
    @patch("src.main.AudioRecorder")
    @patch("src.main.SpellGrammarChecker")
    @patch("src.main.Config")
    def test_create_system_tray_icon(
        self,
        mock_config,
        mock_spell_checker,
        mock_recorder,
        mock_stt,
        mock_input_handler,
        mock_sound_controller,
    ):
        """Test system tray icon creation."""
        # Mock all dependencies
        mock_config_instance = Mock()
        mock_config_instance.debug_level = "INFO"
        mock_config.return_value = mock_config_instance

        mock_sound_controller_instance = Mock()
        mock_sound_controller_instance.is_available.return_value = True
        mock_sound_controller.return_value = mock_sound_controller_instance

        mock_input_handler_instance = Mock()
        mock_input_handler.return_value = mock_input_handler_instance

        mock_stt_instance = Mock()
        mock_stt.return_value = mock_stt_instance

        mock_recorder_instance = Mock()
        mock_recorder.return_value = mock_recorder_instance

        mock_spell_checker_instance = Mock()
        mock_spell_checker.return_value = mock_spell_checker_instance

        # Create app instance
        app = MauscribeApp()

        # Test icon creation when not recording
        app.is_recording = False
        icon = app._create_system_tray_icon()
        assert icon is not None
        assert icon.size == (64, 64)

        # Test icon creation when recording
        app.is_recording = True
        icon_recording = app._create_system_tray_icon()
        assert icon_recording is not None
        assert icon_recording.size == (64, 64)

    @patch("src.main.SoundController")
    @patch("src.main.InputHandler")
    @patch("src.main.SpeechToText")
    @patch("src.main.AudioRecorder")
    @patch("src.main.SpellGrammarChecker")
    @patch("src.main.Config")
    def test_print_status(
        self,
        mock_config,
        mock_spell_checker,
        mock_recorder,
        mock_stt,
        mock_input_handler,
        mock_sound_controller,
    ):
        """Test status printing functionality."""
        # Mock all dependencies
        mock_config_instance = Mock()
        mock_config_instance.debug_level = "INFO"
        mock_config_instance.input_method = "mouse_button"
        mock_config_instance.mouse_button_primary = "x2"
        mock_config_instance.audio_device = None
        mock_config.return_value = mock_config_instance

        mock_sound_controller_instance = Mock()
        mock_sound_controller_instance.is_available.return_value = True
        mock_sound_controller.return_value = mock_sound_controller_instance

        mock_input_handler_instance = Mock()
        mock_input_handler.return_value = mock_input_handler_instance

        mock_stt_instance = Mock()
        mock_stt.return_value = mock_stt_instance

        mock_recorder_instance = Mock()
        mock_recorder.return_value = mock_recorder_instance

        mock_spell_checker_instance = Mock()
        mock_spell_checker.return_value = mock_spell_checker_instance

        # Create app instance
        app = MauscribeApp()

        # Test status printing when idle
        app.is_recording = False
        with patch("builtins.print") as mock_print:
            app._print_status()
            mock_print.assert_called()

        # Test status printing when recording
        app.is_recording = True
        with patch("builtins.print") as mock_print:
            app._print_status()
            mock_print.assert_called()


class TestMainModule:
    """Test the main module functionality."""

    @patch("src.main.MauscribeApp")
    def test_main_function_exists(self, mock_app_class):
        """Test that main function exists and can be called."""
        # Import the main function
        from src.main import main

        # Mock the app class
        mock_app_instance = Mock()
        mock_app_class.return_value = mock_app_instance

        # Call main function
        main()

        # Verify app was created
        mock_app_class.assert_called_once()
        mock_app_instance.run.assert_called_once()

    def test_main_module_imports(self):
        """Test that main module can be imported without errors."""
        # This should not raise any exceptions
        import src.main

        # Verify the module can be imported
        assert src.main is not None
