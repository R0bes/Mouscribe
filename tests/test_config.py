"""Tests for the config module."""
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open
import tempfile
import os

# Import the module to test
from src.config import Config


class TestConfig:
    """Test cases for Config class."""
    
    def test_config_initialization(self):
        """Test Config initialization with default values."""
        config = Config()
        assert config is not None
        assert hasattr(config, 'config')
    
    def test_load_config_file_not_found(self):
        """Test loading config when file doesn't exist."""
        with patch('builtins.open', side_effect=FileNotFoundError):
            config = Config()
            # Should not crash and should have default values
            assert config is not None
    
    def test_load_config_invalid_toml(self):
        """Test loading config with invalid TOML."""
        invalid_toml = "invalid toml content ["
        with patch('builtins.open', mock_open(read_data=invalid_toml)):
            config = Config()
            # Should not crash and should have default values
            assert config is not None
    
    def test_get_setting(self):
        """Test getting a setting value."""
        config = Config()
        # Test getting a setting (should return default or None)
        result = config.get_setting('test_setting', 'default_value')
        assert result == 'default_value'
    
    def test_save_config(self):
        """Test saving config to file."""
        config = Config()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Mock the open function to capture written content
            with patch('builtins.open', mock_open()) as mock_file:
                config.save_config(tmp_path)
                mock_file.assert_called_once()
        finally:
            # Cleanup
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


if __name__ == '__main__':
    pytest.main([__file__])
