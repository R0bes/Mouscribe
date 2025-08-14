"""
Mauscribe - Voice-to-Text Tool
"""

from .config import Config
from .logger import MauscribeLogger, get_logger, setup_logging
from .main import MauscribeApp, main
from .recorder import AudioRecorder
from .spell_checker import SpellChecker
from .stt import SpeechToText

setup_logging()

__all__ = [
    "Config",
    "MauscribeApp",
    "main",
    "AudioRecorder",
    "SpeechToText",
    "SpellChecker",
    "MauscribeLogger",
    "get_logger",
]
