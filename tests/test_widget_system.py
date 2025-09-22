#!/usr/bin/env python3
"""
Einfacher Test für das Widgetsystem von Mauscribe
Testet grundlegende Widget-Funktionalitäten ohne GUI-Abhängigkeiten
"""

import os
import sys
import threading
import time
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class TestWidgetSystem:
    """Test-Klasse für das Widgetsystem."""

    def setup_method(self):
        """Setup für jeden Test."""
        self.mock_tkinter()

    def mock_tkinter(self):
        """Mock tkinter für Tests ohne GUI."""
        # Mock tkinter components
        self.tk_mock = Mock()
        self.toplevel_mock = Mock()
        self.frame_mock = Mock()
        self.label_mock = Mock()
        self.button_mock = Mock()

        # Mock tkinter methods
        self.tk_mock.Tk.return_value = Mock()
        self.tk_mock.Toplevel.return_value = self.toplevel_mock
        self.tk_mock.Frame.return_value = self.frame_mock
        self.tk_mock.Label.return_value = self.label_mock
        self.tk_mock.Button.return_value = self.button_mock

        # Mock window methods
        self.toplevel_mock.withdraw = Mock()
        self.toplevel_mock.deiconify = Mock()
        self.toplevel_mock.geometry = Mock()
        self.toplevel_mock.attributes = Mock()
        self.toplevel_mock.update_idletasks = Mock()
        self.toplevel_mock.winfo_screenwidth = Mock(return_value=1920)
        self.toplevel_mock.winfo_screenheight = Mock(return_value=1080)
        self.toplevel_mock.winfo_reqwidth = Mock(return_value=300)
        self.toplevel_mock.winfo_reqheight = Mock(return_value=200)
        self.toplevel_mock.winfo_x = Mock(return_value=100)
        self.toplevel_mock.winfo_y = Mock(return_value=100)
        self.toplevel_mock.winfo_id = Mock(return_value=12345)
        self.toplevel_mock.bind = Mock()
        self.toplevel_mock.configure = Mock()
        self.toplevel_mock.pack = Mock()
        self.toplevel_mock.destroy = Mock()

        # Mock frame methods
        self.frame_mock.pack = Mock()

        # Mock label methods
        self.label_mock.pack = Mock()
        self.label_mock.configure = Mock()

        # Mock button methods
        self.button_mock.pack = Mock()
        self.button_mock.bind = Mock()
        self.button_mock.configure = Mock()

    @patch("src.ui.widgets.tk")
    @patch("src.ui.widgets.WINDOWS_API_AVAILABLE", False)
    def test_base_widget_creation(self, mock_tk):
        """Teste BaseWidget-Erstellung."""
        from src.ui.widgets import BaseWidget, WidgetConfig, WidgetTheme

        # Mock tkinter
        mock_tk.Tk.return_value = Mock()
        mock_tk.Toplevel.return_value = self.toplevel_mock
        mock_tk.Frame.return_value = self.frame_mock

        # Erstelle Widget-Config
        config = WidgetConfig(theme=WidgetTheme.DARK, position=None, auto_hide_duration=3.0)

        # Erstelle Test-Widget
        class TestWidget(BaseWidget):
            def create_content(self, parent):
                return self.frame_mock

        widget = TestWidget(config)

        # Teste Grundfunktionen
        assert widget.config == config
        assert widget.is_visible is False
        assert widget.window is None

    @patch("src.ui.widgets.tk")
    @patch("src.ui.widgets.WINDOWS_API_AVAILABLE", False)
    def test_widget_config(self, mock_tk):
        """Teste Widget-Konfiguration."""
        from src.ui.widgets import WidgetConfig, WidgetPosition, WidgetTheme

        # Teste verschiedene Konfigurationen
        config1 = WidgetConfig()
        assert config1.theme == WidgetTheme.DARK
        assert config1.position == WidgetPosition.TOP_RIGHT
        assert config1.auto_hide_duration == 3.0

        config2 = WidgetConfig(theme=WidgetTheme.LIGHT, position=WidgetPosition.BOTTOM_LEFT, auto_hide_duration=5.0)
        assert config2.theme == WidgetTheme.LIGHT
        assert config2.position == WidgetPosition.BOTTOM_LEFT
        assert config2.auto_hide_duration == 5.0

    @patch("src.ui.widgets.tk")
    @patch("src.ui.widgets.WINDOWS_API_AVAILABLE", False)
    def test_text_widget(self, mock_tk):
        """Teste TextWidget."""
        from src.ui.widgets import TextWidget, WidgetConfig, WidgetTheme

        # Mock tkinter
        mock_tk.Tk.return_value = Mock()
        mock_tk.Toplevel.return_value = self.toplevel_mock
        mock_tk.Label.return_value = self.label_mock

        # Erstelle TextWidget
        widget = TextWidget("Test Text")

        # Teste Grundfunktionen
        assert widget.text == "Test Text"
        assert widget.is_visible is False

        # Teste Content-Erstellung
        content = widget.create_content(self.toplevel_mock)
        assert content == self.label_mock

        # Teste Content-Update
        widget.update_content("Neuer Text")
        assert widget.text == "Neuer Text"

    @patch("src.ui.widgets.tk")
    @patch("src.ui.widgets.WINDOWS_API_AVAILABLE", False)
    def test_recording_widget(self, mock_tk):
        """Teste RecordingWidget."""
        from src.ui.widgets import RecordingWidget, WidgetConfig, WidgetTheme

        # Mock tkinter
        mock_tk.Tk.return_value = Mock()
        mock_tk.Toplevel.return_value = self.toplevel_mock
        mock_tk.Frame.return_value = self.frame_mock
        mock_tk.Label.return_value = self.label_mock

        # Erstelle RecordingWidget
        widget = RecordingWidget()

        # Teste Grundfunktionen
        assert widget.recording_time == 0.0
        assert widget.is_visible is False

        # Teste Content-Erstellung
        content = widget.create_content(self.toplevel_mock)
        assert content == self.frame_mock

        # Teste Zeit-Update
        widget.update_content(recording_time=65.5)
        assert widget.recording_time == 65.5

    @patch("src.ui.widgets.tk")
    @patch("src.ui.widgets.WINDOWS_API_AVAILABLE", False)
    def test_mouse_overlay_manager(self, mock_tk):
        """Teste MouseOverlayManager."""
        from src.ui.widgets import MouseOverlayManager, TextWidget

        # Mock tkinter
        mock_tk.Tk.return_value = Mock()
        mock_tk.Toplevel.return_value = self.toplevel_mock
        mock_tk.Label.return_value = self.label_mock

        # Erstelle Manager
        manager = MouseOverlayManager()

        # Teste Grundfunktionen
        assert manager.widgets == {}
        assert manager._mouse_monitor_active is False

        # Erstelle Test-Widget
        widget = TextWidget("Test")

        # Registriere Widget
        manager.register_widget("test_widget", widget)
        assert "test_widget" in manager.widgets

        # Teste Widget-Anzeige
        result = manager.show_widget("test_widget", 100, 100)
        assert result is True

        # Teste Widget-Verstecken
        manager.hide_widget("test_widget")

        # Teste Verstecken aller Widgets
        manager.hide_all()

    @patch("src.ui.widgets.tk")
    @patch("src.ui.widgets.WINDOWS_API_AVAILABLE", False)
    def test_widget_themes(self, mock_tk):
        """Teste Widget-Themes."""
        from src.ui.widgets import WidgetTheme

        # Teste alle Themes
        themes = [WidgetTheme.DARK, WidgetTheme.LIGHT, WidgetTheme.RECORDING, WidgetTheme.SUCCESS]

        for theme in themes:
            assert "bg" in theme.value
            assert "fg" in theme.value
            assert "border" in theme.value
            assert "alpha" in theme.value
            assert 0.0 <= theme.value["alpha"] <= 1.0

    @patch("src.ui.widgets.tk")
    @patch("src.ui.widgets.WINDOWS_API_AVAILABLE", False)
    def test_widget_positions(self, mock_tk):
        """Teste Widget-Positionen."""
        from src.ui.widgets import WidgetPosition

        # Teste alle Positionen
        positions = [
            WidgetPosition.TOP_RIGHT,
            WidgetPosition.TOP_LEFT,
            WidgetPosition.BOTTOM_RIGHT,
            WidgetPosition.BOTTOM_LEFT,
            WidgetPosition.RIGHT,
            WidgetPosition.LEFT,
        ]

        for position in positions:
            assert isinstance(position.value, tuple)
            assert len(position.value) == 2
            assert isinstance(position.value[0], int)
            assert isinstance(position.value[1], int)

    @patch("src.ui.widgets.tk")
    @patch("src.ui.widgets.WINDOWS_API_AVAILABLE", False)
    def test_convenience_functions(self, mock_tk):
        """Teste Convenience-Funktionen."""
        from src.ui.widgets import WidgetPosition, WidgetTheme, create_recording_widget, create_text_widget

        # Mock tkinter
        mock_tk.Tk.return_value = Mock()
        mock_tk.Toplevel.return_value = self.toplevel_mock
        mock_tk.Label.return_value = self.label_mock
        mock_tk.Frame.return_value = self.frame_mock

        # Teste Text-Widget-Erstellung
        text_widget = create_text_widget("Test Text", WidgetTheme.LIGHT)
        assert text_widget.text == "Test Text"
        assert text_widget.config.theme == WidgetTheme.LIGHT

        # Teste Recording-Widget-Erstellung
        recording_widget = create_recording_widget(WidgetPosition.BOTTOM_RIGHT)
        assert recording_widget.config.position == WidgetPosition.BOTTOM_RIGHT
        assert recording_widget.config.theme == WidgetTheme.RECORDING


class TestTranscriptionWidget:
    """Test-Klasse für TranscriptionWidget."""

    def setup_method(self):
        """Setup für jeden Test."""
        self.mock_tkinter()

    def mock_tkinter(self):
        """Mock tkinter für Tests ohne GUI."""
        # Mock tkinter components
        self.tk_mock = Mock()
        self.toplevel_mock = Mock()
        self.frame_mock = Mock()
        self.label_mock = Mock()
        self.button_mock = Mock()
        self.text_mock = Mock()
        self.scrollbar_mock = Mock()

        # Mock tkinter methods
        self.tk_mock.Tk.return_value = Mock()
        self.tk_mock.Toplevel.return_value = self.toplevel_mock
        self.tk_mock.Frame.return_value = self.frame_mock
        self.tk_mock.Label.return_value = self.label_mock
        self.tk_mock.Button.return_value = self.button_mock
        self.tk_mock.Text.return_value = self.text_mock
        self.tk_mock.Scrollbar.return_value = self.scrollbar_mock

        # Mock window methods
        self.toplevel_mock.withdraw = Mock()
        self.toplevel_mock.deiconify = Mock()
        self.toplevel_mock.geometry = Mock()
        self.toplevel_mock.attributes = Mock()
        self.toplevel_mock.update_idletasks = Mock()
        self.toplevel_mock.winfo_screenwidth = Mock(return_value=1920)
        self.toplevel_mock.winfo_screenheight = Mock(return_value=1080)
        self.toplevel_mock.winfo_reqwidth = Mock(return_value=400)
        self.toplevel_mock.winfo_reqheight = Mock(return_value=200)
        self.toplevel_mock.winfo_x = Mock(return_value=100)
        self.toplevel_mock.winfo_y = Mock(return_value=100)
        self.toplevel_mock.winfo_id = Mock(return_value=12345)
        self.toplevel_mock.bind = Mock()
        self.toplevel_mock.configure = Mock()
        self.toplevel_mock.pack = Mock()
        self.toplevel_mock.destroy = Mock()
        self.toplevel_mock.after = Mock()

        # Mock text methods
        self.text_mock.config = Mock()
        self.text_mock.delete = Mock()
        self.text_mock.insert = Mock()
        self.text_mock.pack = Mock()

        # Mock scrollbar methods
        self.scrollbar_mock.pack = Mock()

        # Mock other components
        self.frame_mock.pack = Mock()
        self.label_mock.pack = Mock()
        self.label_mock.config = Mock()
        self.button_mock.pack = Mock()
        self.button_mock.bind = Mock()
        self.button_mock.configure = Mock()

    @patch("src.ui.transcription_widget.tk")
    @patch("src.ui.transcription_widget.WIN32_AVAILABLE", False)
    def test_transcription_widget_creation(self, mock_tk):
        """Teste TranscriptionWidget-Erstellung."""
        from src.ui.transcription_widget import TranscriptionWidget

        # Mock tkinter
        mock_tk.Tk.return_value = Mock()
        mock_tk.Toplevel.return_value = self.toplevel_mock
        mock_tk.Frame.return_value = self.frame_mock
        mock_tk.Label.return_value = self.label_mock
        mock_tk.Button.return_value = self.button_mock
        mock_tk.Text.return_value = self.text_mock
        mock_tk.Scrollbar.return_value = self.scrollbar_mock

        # Erstelle TranscriptionWidget
        widget = TranscriptionWidget()

        # Teste Grundfunktionen
        assert widget.is_visible is False
        assert widget.transcription_text == ""
        assert widget.confidence == 0.0
        assert widget.root is not None

    @patch("src.ui.transcription_widget.tk")
    @patch("src.ui.transcription_widget.WIN32_AVAILABLE", False)
    def test_transcription_widget_manager(self, mock_tk):
        """Teste TranscriptionWidgetManager."""
        from src.ui.transcription_widget import TranscriptionWidgetManager

        # Mock tkinter
        mock_tk.Tk.return_value = Mock()
        mock_tk.Toplevel.return_value = self.toplevel_mock
        mock_tk.Frame.return_value = self.frame_mock
        mock_tk.Label.return_value = self.label_mock
        mock_tk.Button.return_value = self.button_mock
        mock_tk.Text.return_value = self.text_mock
        mock_tk.Scrollbar.return_value = self.scrollbar_mock

        # Erstelle Manager
        manager = TranscriptionWidgetManager()

        # Teste Grundfunktionen
        assert manager.widget is None
        assert manager.on_copy_callback is None

        # Setze Copy-Callback
        callback = Mock()
        manager.set_copy_callback(callback)
        assert manager.on_copy_callback == callback

        # Teste Transkription-Anzeige
        manager.show_transcription("Test Text", 0.8, 100, 100)
        assert manager.widget is not None

        # Teste Transkription-Verstecken
        manager.hide_transcription()

        # Teste Cleanup
        manager.cleanup()
        assert manager.widget is None


def test_widget_system_integration():
    """Integrationstest für das Widgetsystem."""
    # Teste, dass alle Module importiert werden können
    try:
        from src.ui.transcription_widget import TranscriptionWidget, TranscriptionWidgetManager
        from src.ui.widgets import (
            BaseWidget,
            MouseOverlayManager,
            RecordingWidget,
            TextWidget,
            WidgetConfig,
            WidgetPosition,
            WidgetTheme,
        )

        assert True
    except ImportError as e:
        pytest.fail(f"Widget system import failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
