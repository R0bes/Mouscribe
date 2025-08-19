"""
Mauscribe - Voice-to-Text Tool
"""

from .audio.recorder import AudioRecorder
from .lang.spell_checker import SpellChecker
from .lang.stt import SpeechToText
from .mouscribe import MauscribeApp
from .utils.config import Config
from .utils.logger import MauscribeLogger, get_logger

__all__ = [
    "Config",
    "MauscribeApp",
    "AudioRecorder",
    "SpeechToText",
    "SpellChecker",
    "MauscribeLogger",
    "get_logger",
]
