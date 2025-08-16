"""
Mauscribe - Voice-to-Text Tool
"""

from .audio.recorder import AudioRecorder
from .lang.spell_checker import SpellChecker
from .lang.stt import SpeechToText
from .main import MauscribeApp, main
from .utils.config import Config
from .utils.logger import MauscribeLogger, get_logger, setup_logging

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
