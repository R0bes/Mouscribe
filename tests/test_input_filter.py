"""Tests für den InputHandler von Mauscribe."""

import pytest
from unittest.mock import Mock, patch

from src.input_handler import InputHandler
from src.utils.config import Config


class TestInputHandlerIntegration:
    """Test-Klasse für die Integration des InputHandlers."""

    def setup_method(self):
        """Setup für jeden Test."""
        self.config = Config()
        self.primary_callback = Mock()
        self.secondary_callback = Mock()

    def test_input_handler_with_mock_callbacks(self):
        """Testet den InputHandler mit Mock-Callbacks."""
        handler = InputHandler(
            pk_callback=self.primary_callback,
            sk_callback=self.secondary_callback
        )
        
        # Prüfe, dass der Handler korrekt initialisiert wurde
        assert handler is not None
        assert handler.primary_callback == self.primary_callback
        assert handler.secondary_callback == self.secondary_callback
        
        handler.stop()

    def test_input_handler_lifecycle(self):
        """Testet den Lebenszyklus des InputHandlers."""
        # Erstelle Handler
        handler = InputHandler(
            pk_callback=self.primary_callback,
            sk_callback=self.secondary_callback
        )
        
        # Prüfe, dass der Handler aktiv ist
        assert handler._active is True
        
        # Stoppe Handler
        handler.stop()
        
        # Prüfe, dass der Handler gestoppt wurde
        assert handler._active is False
        assert handler._ml is None
        assert handler._kl is None

    def test_configuration_integration(self):
        """Testet die Konfigurationsintegration."""
        handler = InputHandler(
            pk_callback=self.primary_callback,
            sk_callback=self.secondary_callback
        )
        
        # Prüfe, dass die Konfiguration korrekt geladen wurde
        config = handler.config
        assert config is not None
        
        # Prüfe spezifische Konfigurationswerte
        assert hasattr(config, 'primary_name')
        assert hasattr(config, 'secondary_name')
        assert hasattr(config, 'primary_method')
        assert hasattr(config, 'secondary_method')
        
        handler.stop()

    def test_debouncer_integration(self):
        """Testet die Debouncer-Integration."""
        handler = InputHandler(
            pk_callback=self.primary_callback,
            sk_callback=self.secondary_callback
        )
        
        # Prüfe, dass der Debouncer existiert
        assert hasattr(handler, '_db')
        assert handler._db is not None
        
        # Teste Debouncer-Funktionalität
        debouncer = handler._db
        
        # Erster Hit sollte False zurückgeben
        assert debouncer.hit("test", 100) is False
        
        # Sofortiger zweiter Hit sollte True zurückgeben
        assert debouncer.hit("test", 100) is True
        
        handler.stop()

    def test_filter_integration(self):
        """Testet die Filter-Integration."""
        handler = InputHandler(
            pk_callback=self.primary_callback,
            sk_callback=self.secondary_callback
        )
        
        # Prüfe, dass der Filter existiert
        assert hasattr(handler, 'filter')
        assert handler.filter is not None
        
        # Prüfe, dass die Callbacks korrekt gesetzt wurden
        assert handler.filter.primary_callback == self.primary_callback
        assert handler.filter.secondary_callback == self.secondary_callback
        
        handler.stop()

    def test_mapper_integration(self):
        """Testet die Mapper-Integration."""
        handler = InputHandler(
            pk_callback=self.primary_callback,
            sk_callback=self.secondary_callback
        )
        
        # Prüfe, dass der Mapper existiert
        assert hasattr(handler, 'mapper')
        assert handler.mapper is not None
        
        handler.stop()

    def test_listener_setup(self):
        """Testet das Setup der Listener."""
        handler = InputHandler(
            pk_callback=self.primary_callback,
            sk_callback=self.secondary_callback
        )
        
        # Prüfe, dass die Listener existieren
        assert hasattr(handler, '_ml')
        assert hasattr(handler, '_kl')
        
        # Prüfe, dass die Listener gestartet wurden
        assert handler._ml is not None
        assert handler._kl is not None
        
        handler.stop()

    def test_error_handling_integration(self):
        """Testet die Fehlerbehandlung-Integration."""
        # Erstelle einen Handler mit fehlerhaften Callbacks
        error_callback = Mock(side_effect=Exception("Test error"))
        
        # Der Handler sollte nicht abstürzen
        handler = InputHandler(
            pk_callback=error_callback,
            sk_callback=error_callback
        )
        
        assert handler is not None
        
        handler.stop()

    def test_configuration_validation(self):
        """Testet die Konfigurationsvalidierung."""
        handler = InputHandler(
            pk_callback=self.primary_callback,
            sk_callback=self.secondary_callback
        )
        
        # Prüfe, dass die Konfiguration gültige Werte hat
        config = handler.config
        
        # Prüfe, dass die Konfiguration die erwarteten Attribute hat
        required_attrs = ['primary_name', 'secondary_name', 'primary_method', 'secondary_method']
        for attr in required_attrs:
            assert hasattr(config, attr), f"Konfiguration fehlt: {attr}"
        
        handler.stop()

    def test_callback_chain(self):
        """Testet die Callback-Kette."""
        handler = InputHandler(
            pk_callback=self.primary_callback,
            sk_callback=self.secondary_callback
        )
        
        # Prüfe, dass die Callbacks korrekt durchgereicht wurden
        assert handler.primary_callback == self.primary_callback
        assert handler.secondary_callback == self.secondary_callback
        assert handler.filter.primary_callback == self.primary_callback
        assert handler.filter.secondary_callback == self.secondary_callback
        
        handler.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
