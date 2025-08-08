"""
Mauscribe Konfiguration
Liest Einstellungen aus config.toml
"""

import tomllib
from pathlib import Path
import os

def load_config():
    """Lädt die Konfiguration aus config.toml"""
    config_path = Path(__file__).parent.parent / "config.toml"
    
    if not config_path.exists():
        print("⚠️  config.toml nicht gefunden, verwende Standardeinstellungen")
        return get_default_config()
    
    try:
        with open(config_path, "rb") as f:
            return tomllib.load(f)
    except Exception as e:
        print(f"⚠️  Fehler beim Laden der config.toml: {e}")
        return get_default_config()

def get_default_config():
    """Standard-Konfiguration falls TOML-Datei nicht existiert"""
    return {
        "input": {"method": "mouse_button"},
        "mouse_button": {
            "primary": "x2",
            "secondary": "x1", 
            "left_with_ctrl": True
        },
        "keyboard": {
            "primary": "f9",
            "secondary": "shift+f9"
        },
        "custom": {
            "combinations": [["ctrl", "shift", "v"], ["alt", "v"]]
        },
        "audio": {
            "sample_rate": 16000,
            "channels": 1,
            "chunk_size": 1024,
            "format": "int16"
        },
        "stt": {
            "model": "base",
            "language": "de",
            "compute_type": "float32"
        },
        "behavior": {
            "auto_paste_after_transcription": False,
            "add_space_after_text": True,
            "paste_double_click_window": 10.0,
            "double_click_threshold": 0.5
        },
        "cursor": {
            "enable": True,
            "type": "microphone"
        },
        "system": {
            "restore_system_sounds": True,
            "volume_reduction_factor": 0.15,
            "min_volume_percent": 5
        },
        "debug": {
            "verbose": False,
            "log_errors": True
        }
    }

# Lade Konfiguration
_config = load_config()

# Input-Konfiguration
INPUT_METHOD = _config["input"]["method"]
ACTIVE_INPUT_CONFIG = _config.get(INPUT_METHOD, {})

# Audio-Konfiguration
SAMPLE_RATE = _config["audio"]["sample_rate"]
CHANNELS = _config["audio"]["channels"]
CHUNK_SIZE = _config["audio"]["chunk_size"]

# STT-Konfiguration
WHISPER_MODEL = _config["stt"]["model"]
LANGUAGE = _config["stt"]["language"]
COMPUTE_TYPE = _config["stt"]["compute_type"]

# Verhalten
AUTO_PASTE_AFTER_TRANSCRIPTION = _config["behavior"]["auto_paste_after_transcription"]
ADD_SPACE_AFTER_TEXT = _config["behavior"]["add_space_after_text"]
PASTE_DOUBLE_CLICK_WINDOW = _config["behavior"]["paste_double_click_window"]
DOUBLE_CLICK_THRESHOLD = _config["behavior"]["double_click_threshold"]

# Cursor
ENABLE_CURSOR_FEEDBACK = _config["cursor"]["enable"]
CURSOR_TYPE = _config["cursor"]["type"]

# System
RESTORE_SYSTEM_SOUNDS = _config["system"]["restore_system_sounds"]
VOLUME_REDUCTION_FACTOR = _config["system"]["volume_reduction_factor"]
MIN_VOLUME_PERCENT = _config["system"]["min_volume_percent"]

# Debug
VERBOSE_LOGGING = _config["debug"]["verbose"]
LOG_ERRORS = _config["debug"]["log_errors"]

# Zusätzliche Variablen für Kompatibilität
VAD_SENSITIVITY = 1
MIN_RECORDING_SECONDS = 0.5
MAX_RECORDING_SECONDS = 0
AUDIO_BUFFER_SIZE = 4096
LOCK_TIMEOUT = 1.0
