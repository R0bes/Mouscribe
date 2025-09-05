"""
Integration Tests für MSIX-Funktionalität
Testet MSIX-spezifische Features und Fallback-Mechanismen
"""

import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Füge src zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from msix.audio_adapter import MSIXAudioAdapter
from msix.input_adapter import MSIXInputAdapter
from utils.config import Config


class TestMSIXEnvironment:
    """Tests für MSIX-Umgebungserkennung"""
    
    def test_msix_detection_with_env_vars(self):
        """Testet MSIX-Erkennung über Umgebungsvariablen"""
        with patch.dict(os.environ, {'MSIX_PACKAGE_FAMILY_NAME': 'Mauscribe.Robs_*'}):
            adapter = MSIXAudioAdapter(Config())
            assert adapter._is_msix is True
    
    def test_msix_detection_with_packages_path(self):
        """Testet MSIX-Erkennung über Packages-Pfad"""
        with patch.dict(os.environ, {'LOCALAPPDATA': 'C:\\Users\\Test\\AppData\\Local\\Packages'}):
            adapter = MSIXAudioAdapter(Config())
            assert adapter._is_msix is True
    
    def test_msix_detection_negative(self):
        """Testet MSIX-Erkennung ohne MSIX-Umgebung"""
        with patch.dict(os.environ, {}, clear=True):
            adapter = MSIXAudioAdapter(Config())
            assert adapter._is_msix is False


class TestMSIXAudioAdapter:
    """Tests für MSIX-Audio-Adapter"""
    
    @pytest.fixture
    def config(self):
        """Erstellt Test-Konfiguration"""
        return Config()
    
    @pytest.fixture
    def audio_adapter(self, config):
        """Erstellt MSIX-Audio-Adapter"""
        return MSIXAudioAdapter(config)
    
    def test_audio_system_initialization(self, audio_adapter):
        """Testet Audio-System-Initialisierung"""
        assert audio_adapter._audio_system is not None
        assert audio_adapter._available_devices is not None
    
    def test_device_selection(self, audio_adapter):
        """Testet Audio-Geräteauswahl"""
        if audio_adapter._available_devices:
            device = audio_adapter._available_devices[0]
            assert audio_adapter.select_device(device['index']) is True
            assert audio_adapter._current_device == device
    
    def test_recording_start_stop(self, audio_adapter):
        """Testet Aufnahme-Start und -Stop"""
        if audio_adapter._available_devices:
            audio_adapter.select_device(0)
            
            # Starte Aufnahme
            assert audio_adapter.start_recording() is True
            assert audio_adapter.is_recording() is True
            
            # Stoppe Aufnahme
            audio_data = audio_adapter.stop_recording()
            assert audio_adapter.is_recording() is False
            assert audio_data is not None
    
    def test_callback_system(self, audio_adapter):
        """Testet Callback-System"""
        start_called = False
        stop_called = False
        data_called = False
        
        def on_start():
            nonlocal start_called
            start_called = True
        
        def on_stop():
            nonlocal stop_called
            stop_called = True
        
        def on_data(data):
            nonlocal data_called
            data_called = True
        
        audio_adapter.set_callbacks(on_start, on_stop, on_data)
        
        if audio_adapter._available_devices:
            audio_adapter.select_device(0)
            audio_adapter.start_recording()
            audio_adapter.stop_recording()
            
            assert start_called is True
            assert stop_called is True
    
    def test_fallback_audio_system(self, audio_adapter):
        """Testet Fallback-Audio-System"""
        # Simuliere Fehler in allen Audio-Systemen
        with patch.object(audio_adapter, '_try_winrt_audio', return_value=False), \
             patch.object(audio_adapter, '_try_sounddevice_audio', return_value=False), \
             patch.object(audio_adapter, '_try_pyaudio_audio', return_value=False):
            
            # Erstelle neuen Adapter mit Fallback
            fallback_adapter = MSIXAudioAdapter(Config())
            assert fallback_adapter._audio_system == 'fallback'
            assert len(fallback_adapter._available_devices) > 0


class TestMSIXInputAdapter:
    """Tests für MSIX-Input-Adapter"""
    
    @pytest.fixture
    def config(self):
        """Erstellt Test-Konfiguration"""
        return Config()
    
    @pytest.fixture
    def input_adapter(self, config):
        """Erstellt MSIX-Input-Adapter"""
        return MSIXInputAdapter(config)
    
    def test_input_system_initialization(self, input_adapter):
        """Testet Input-System-Initialisierung"""
        assert input_adapter._input_system is not None
    
    def test_button_mapping(self, input_adapter):
        """Testet Button-Mapping"""
        assert 'primary' in input_adapter._button_mapping
        assert 'secondary' in input_adapter._button_mapping
        assert 'third' in input_adapter._button_mapping
    
    def test_callback_system(self, input_adapter):
        """Testet Callback-System"""
        primary_called = False
        secondary_called = False
        third_called = False
        
        def on_primary():
            nonlocal primary_called
            primary_called = True
        
        def on_secondary():
            nonlocal secondary_called
            secondary_called = True
        
        def on_third():
            nonlocal third_called
            third_called = True
        
        input_adapter.set_callbacks(on_primary, on_secondary, on_third)
        
        # Simuliere Input-Events
        input_adapter._handle_primary_input()
        input_adapter._handle_secondary_input()
        input_adapter._handle_third_input()
        
        assert primary_called is True
        assert secondary_called is True
        assert third_called is True
    
    def test_listening_start_stop(self, input_adapter):
        """Testet Listening-Start und -Stop"""
        assert input_adapter.is_listening() is False
        
        input_adapter.start_listening()
        assert input_adapter.is_listening() is True
        
        input_adapter.stop_listening()
        assert input_adapter.is_listening() is False
    
    def test_fallback_input_system(self, input_adapter):
        """Testet Fallback-Input-System"""
        # Simuliere Fehler in allen Input-Systemen
        with patch.object(input_adapter, '_try_winrt_input', return_value=False), \
             patch.object(input_adapter, '_try_pynput_input', return_value=False), \
             patch.object(input_adapter, '_try_keyboard_lib_input', return_value=False):
            
            # Erstelle neuen Adapter mit Fallback
            fallback_adapter = MSIXInputAdapter(Config())
            assert fallback_adapter._input_system == 'fallback'


class TestMSIXIntegration:
    """Integration Tests für MSIX-Funktionalität"""
    
    @pytest.fixture
    def temp_msix_env(self):
        """Erstellt temporäre MSIX-Umgebung"""
        temp_dir = tempfile.mkdtemp()
        packages_dir = Path(temp_dir) / "Packages"
        packages_dir.mkdir()
        
        with patch.dict(os.environ, {'LOCALAPPDATA': str(temp_dir)}):
            yield temp_dir
        
        shutil.rmtree(temp_dir)
    
    def test_msix_audio_input_integration(self, temp_msix_env):
        """Testet Integration von MSIX-Audio und Input"""
        config = Config()
        
        # Erstelle Audio-Adapter
        audio_adapter = MSIXAudioAdapter(config)
        assert audio_adapter._is_msix is True
        
        # Erstelle Input-Adapter
        input_adapter = MSIXInputAdapter(config)
        assert input_adapter._is_msix is True
        
        # Teste Integration
        if audio_adapter._available_devices:
            audio_adapter.select_device(0)
            input_adapter.start_listening()
            
            # Simuliere Input-Event während Aufnahme
            audio_adapter.start_recording()
            input_adapter._handle_primary_input()
            audio_data = audio_adapter.stop_recording()
            
            assert audio_data is not None
            input_adapter.stop_listening()
    
    def test_msix_permission_handling(self, temp_msix_env):
        """Testet MSIX-Berechtigungshandling"""
        config = Config()
        
        # Teste Audio-Berechtigungen
        audio_adapter = MSIXAudioAdapter(config)
        assert hasattr(audio_adapter, '_check_microphone_permission')
        
        # Teste Input-Berechtigungen
        input_adapter = MSIXInputAdapter(config)
        assert hasattr(input_adapter, '_check_input_permissions')
    
    def test_msix_fallback_mechanisms(self, temp_msix_env):
        """Testet MSIX-Fallback-Mechanismen"""
        config = Config()
        
        # Simuliere Fehler in allen Systemen
        with patch('msix.audio_adapter.SOUNDDEVICE_AVAILABLE', False), \
             patch('msix.audio_adapter.PYAUDIO_AVAILABLE', False), \
             patch('msix.input_adapter.PYNPUT_AVAILABLE', False), \
             patch('msix.input_adapter.KEYBOARD_AVAILABLE', False):
            
            # Audio-Adapter sollte Fallback verwenden
            audio_adapter = MSIXAudioAdapter(config)
            assert audio_adapter._audio_system == 'fallback'
            
            # Input-Adapter sollte Fallback verwenden
            input_adapter = MSIXInputAdapter(config)
            assert input_adapter._input_system == 'fallback'
    
    def test_msix_cleanup(self, temp_msix_env):
        """Testet MSIX-Cleanup"""
        config = Config()
        
        # Erstelle Adapter
        audio_adapter = MSIXAudioAdapter(config)
        input_adapter = MSIXInputAdapter(config)
        
        # Starte Services
        if audio_adapter._available_devices:
            audio_adapter.select_device(0)
            audio_adapter.start_recording()
        
        input_adapter.start_listening()
        
        # Cleanup
        audio_adapter.cleanup()
        input_adapter.cleanup()
        
        assert audio_adapter.is_recording() is False
        assert input_adapter.is_listening() is False


class TestMSIXManifest:
    """Tests für MSIX-Manifest-Funktionalität"""
    
    def test_manifest_structure(self):
        """Testet MSIX-Manifest-Struktur"""
        manifest_path = Path(__file__).parent.parent.parent / "msix" / "manifest" / "AppxManifest.xml"
        
        if manifest_path.exists():
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Prüfe wichtige Manifest-Elemente
            assert 'Mauscribe.Robs' in content
            assert 'microphone' in content
            assert 'runFullTrust' in content
            assert 'inputInjectionBrokered' in content
            assert 'userNotificationListener' in content
    
    def test_manifest_capabilities(self):
        """Testet MSIX-Manifest-Capabilities"""
        manifest_path = Path(__file__).parent.parent.parent / "msix" / "manifest" / "AppxManifest.xml"
        
        if manifest_path.exists():
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Prüfe alle benötigten Capabilities
            required_capabilities = [
                'microphone',
                'backgroundMediaPlayback',
                'backgroundTaskExecution',
                'userAccountInformation',
                'userNotificationListener',
                'runFullTrust',
                'allowElevation',
                'allowExternalContent',
                'allowNetworkTraffic',
                'inputInjectionBrokered',
                'inputObservation'
            ]
            
            for capability in required_capabilities:
                assert capability in content, f"Capability '{capability}' fehlt im Manifest"


class TestMSIXBuildSystem:
    """Tests für MSIX-Build-System"""
    
    def test_build_script_exists(self):
        """Testet ob Build-Skript existiert"""
        build_script = Path(__file__).parent.parent.parent / "msix" / "scripts" / "build_msix.ps1"
        assert build_script.exists(), "MSIX Build-Skript fehlt"
    
    def test_manifest_exists(self):
        """Testet ob Manifest existiert"""
        manifest = Path(__file__).parent.parent.parent / "msix" / "manifest" / "AppxManifest.xml"
        assert manifest.exists(), "MSIX Manifest fehlt"
    
    def test_assets_structure(self):
        """Testet Assets-Struktur"""
        assets_dir = Path(__file__).parent.parent.parent / "assets"
        assert assets_dir.exists(), "Assets-Verzeichnis fehlt"
        
        icons_dir = assets_dir / "icons"
        assert icons_dir.exists(), "Icons-Verzeichnis fehlt"
        
        # Prüfe wichtige Icons
        required_icons = [
            "mauscribe_icon.ico",
            "mauscribe_icon.svg",
            "mauscribe_small.svg"
        ]
        
        for icon in required_icons:
            icon_path = icons_dir / icon
            assert icon_path.exists(), f"Icon '{icon}' fehlt"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
