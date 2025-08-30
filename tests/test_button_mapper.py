# tests/test_button_mapper.py - Tests für den vereinfachten ButtonMapper
"""
Tests für den ButtonMapper des vereinfachten Input-Systems.
"""

from unittest.mock import Mock, patch

import pytest

from src.input.input_handler import InputHandler
from src.utils.config import Config


class TestInputHandler:
    """Test-Klasse für den vereinfachten InputHandler."""

    def setup_method(self):
        """Setup für jeden Test."""
        self.config = Config()
        self.primary_callback = Mock()
        self.secondary_callback = Mock()

    def test_input_handler_initialization(self):
        """Testet die Initialisierung des InputHandlers."""
        # Erstelle InputHandler mit Mock-Callbacks
        handler = InputHandler(primary_callback=self.primary_callback, secondary_callback=self.secondary_callback)

        # Prüfe, dass der Handler korrekt initialisiert wurde
        assert handler is not None
        assert handler.primary_callback == self.primary_callback
        assert handler.secondary_callback == self.secondary_callback

        # Cleanup
        handler.stop()

    def test_input_handler_stop(self):
        """Testet das Stoppen des InputHandlers."""
        # Erstelle Handler
        handler = InputHandler(primary_callback=self.primary_callback, secondary_callback=self.secondary_callback)

        # Prüfe, dass der Handler aktiv ist
        assert handler.is_active() is True

        # Stoppe Handler
        handler.stop()

        # Prüfe, dass der Handler gestoppt wurde
        assert handler.is_active() is False

    def test_debouncer_functionality(self):
        """Testet die Debouncer-Funktionalität."""
        handler = InputHandler(primary_callback=self.primary_callback, secondary_callback=self.secondary_callback)

        # Prüfe, dass der Debouncer existiert
        assert hasattr(handler, "_db")
        assert handler._db is not None

        # Teste Debouncer-Funktionalität
        debouncer = handler._db

        # Erster Hit sollte False zurückgeben
        assert debouncer.hit("test", 100) is False

        # Sofortiger zweiter Hit sollte True zurückgeben
        assert debouncer.hit("test", 100) is True

        # Cleanup
        handler.stop()

    def test_configuration_loading(self):
        """Testet das Laden der Konfiguration."""
        handler = InputHandler(primary_callback=self.primary_callback, secondary_callback=self.secondary_callback)

        # Prüfe, dass die Konfiguration korrekt geladen wurde
        config = handler.config
        assert config is not None

        # Prüfe spezifische Konfigurationswerte
        assert hasattr(config, "primary_name")
        assert hasattr(config, "secondary_name")
        assert hasattr(config, "primary_method")
        assert hasattr(config, "secondary_method")

        # Cleanup
        handler.stop()

    def test_callback_assignment(self):
        """Testet die Zuweisung der Callbacks."""
        handler = InputHandler(primary_callback=self.primary_callback, secondary_callback=self.secondary_callback)

        # Prüfe, dass die Callbacks korrekt zugewiesen wurden
        assert handler.primary_callback == self.primary_callback
        assert handler.secondary_callback == self.secondary_callback

        # Cleanup
        handler.stop()

    def test_mouse_listener_setup(self):
        """Testet das Setup der Maus-Listener."""
        handler = InputHandler(primary_callback=self.primary_callback, secondary_callback=self.secondary_callback)

        # Prüfe, dass die Listener existieren
        assert hasattr(handler, "_ml")
        assert hasattr(handler, "_kl")

        # Prüfe, dass die Listener gestartet wurden
        assert handler._ml is not None
        assert handler._kl is not None

        # Cleanup
        handler.stop()

    def test_keyboard_listener_setup(self):
        """Testet das Setup der Tastatur-Listener."""
        handler = InputHandler(primary_callback=self.primary_callback, secondary_callback=self.secondary_callback)

        # Prüfe, dass die Listener existieren
        assert hasattr(handler, "_ml")
        assert hasattr(handler, "_kl")

        # Prüfe, dass die Listener gestartet wurden
        assert handler._ml is not None
        assert handler._kl is not None

        # Cleanup
        handler.stop()

    def test_error_handling(self):
        """Testet die Fehlerbehandlung."""
        # Erstelle einen Handler mit fehlerhaften Callbacks
        error_callback = Mock(side_effect=Exception("Test error"))

        # Der Handler sollte nicht abstürzen
        handler = InputHandler(primary_callback=error_callback, secondary_callback=error_callback)

        assert handler is not None

        # Cleanup
        handler.stop()

    def test_configuration_values(self):
        """Testet die Konfigurationswerte."""
        handler = InputHandler(primary_callback=self.primary_callback, secondary_callback=self.secondary_callback)

        # Prüfe, dass die Konfiguration gültige Werte hat
        config = handler.config

        # Prüfe, dass die Konfiguration die erwarteten Attribute hat
        required_attrs = [
            "primary_name",
            "secondary_name",
            "primary_method",
            "secondary_method",
        ]
        for attr in required_attrs:
            assert hasattr(config, attr), f"Konfiguration fehlt: {attr}"

        # Cleanup
        handler.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
