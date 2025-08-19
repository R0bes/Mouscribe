"""Tests für den InputHandler von Mauscribe."""

import pytest
from unittest.mock import Mock, patch

from src.input_handler import InputHandler
from src.utils.config import Config


class TestInputHandler:
    """Test-Klasse für den InputHandler."""

    def setup_method(self):
        """Setup für jeden Test."""
        self.config = Config()
        self.primary_callback = Mock()
        self.secondary_callback = Mock()

    def test_input_handler_initialization(self):
        """Testet die Initialisierung des InputHandlers."""
        # Erstelle InputHandler mit Mock-Callbacks
        handler = InputHandler(
            pk_callback=self.primary_callback,
            sk_callback=self.secondary_callback
        )
        
        # Prüfe, dass der Handler korrekt initialisiert wurde
        assert handler.primary_callback == self.primary_callback
        assert handler.secondary_callback == self.secondary_callback
        assert handler.config is not None
        assert handler.mapper is not None
        assert handler.filter is not None
        
        # Cleanup
        handler.stop()

    def test_input_handler_stop(self):
        """Testet das Stoppen des InputHandlers."""
        handler = InputHandler(
            pk_callback=self.primary_callback,
            sk_callback=self.secondary_callback
        )
        
        # Stoppe den Handler
        handler.stop()
        
        # Prüfe, dass alle Listener gestoppt wurden
        assert handler._ml is None
        assert handler._kl is None
        assert handler._active is False

    def test_debouncer_functionality(self):
        """Testet die Debouncer-Funktionalität."""
        handler = InputHandler(
            pk_callback=self.primary_callback,
            sk_callback=self.secondary_callback
        )
        
        # Teste Debouncing
        debouncer = handler._db
        
        # Erster Hit sollte False zurückgeben (nicht debounced)
        assert debouncer.hit("test_key", 100) is False
        
        # Sofortiger zweiter Hit sollte True zurückgeben (debounced)
        assert debouncer.hit("test_key", 100) is True
        
        # Nach der Debounce-Zeit sollte es wieder False sein
        import time
        time.sleep(0.2)  # 200ms warten
        assert debouncer.hit("test_key", 100) is False
        
        handler.stop()

    def test_configuration_loading(self):
        """Testet das Laden der Konfiguration."""
        handler = InputHandler(
            pk_callback=self.primary_callback,
            sk_callback=self.secondary_callback
        )
        
        # Prüfe, dass die Konfiguration geladen wurde
        assert handler.config is not None
        assert hasattr(handler.config, 'primary_name')
        assert hasattr(handler.config, 'secondary_name')
        
        handler.stop()

    def test_callback_assignment(self):
        """Testet die Zuweisung der Callbacks."""
        handler = InputHandler(
            pk_callback=self.primary_callback,
            sk_callback=self.secondary_callback
        )
        
        # Prüfe, dass die Callbacks korrekt zugewiesen wurden
        assert handler.filter.primary_callback == self.primary_callback
        assert handler.filter.secondary_callback == self.secondary_callback
        
        handler.stop()

    def test_mouse_listener_setup(self):
        """Testet das Setup der Maus-Listener."""
        handler = InputHandler(
            pk_callback=self.primary_callback,
            sk_callback=self.secondary_callback
        )
        
        # Prüfe, dass der Maus-Listener existiert
        assert handler._ml is not None
        
        handler.stop()

    def test_keyboard_listener_setup(self):
        """Testet das Setup der Tastatur-Listener."""
        handler = InputHandler(
            pk_callback=self.primary_callback,
            sk_callback=self.secondary_callback
        )
        
        # Prüfe, dass der Tastatur-Listener existiert
        assert handler._kl is not None
        
        handler.stop()

    def test_error_handling(self):
        """Testet die Fehlerbehandlung."""
        # Erstelle einen Handler mit fehlerhaften Callbacks
        error_callback = Mock(side_effect=Exception("Test error"))
        
        handler = InputHandler(
            pk_callback=error_callback,
            sk_callback=error_callback
        )
        
        # Der Handler sollte nicht abstürzen
        assert handler is not None
        
        handler.stop()

    def test_configuration_values(self):
        """Testet die Konfigurationswerte."""
        handler = InputHandler(
            pk_callback=self.primary_callback,
            sk_callback=self.secondary_callback
        )
        
        # Prüfe spezifische Konfigurationswerte
        config = handler.config
        
        # Prüfe, dass die Konfiguration die erwarteten Werte hat
        assert hasattr(config, 'primary_name')
        assert hasattr(config, 'secondary_name')
        assert hasattr(config, 'primary_method')
        assert hasattr(config, 'secondary_method')
        
        handler.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
