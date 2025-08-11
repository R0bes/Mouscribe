"""
Mauscribe - Voice-to-Text Tool
"""

import logging
import warnings

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Configure logging to be less verbose
logging.getLogger().setLevel(logging.WARNING)

__version__ = "1.0.0"
__author__ = "Robs"
__description__ = "Voice-to-Text Tool mit Push-to-Talk und automatischem Clipboard-Management"

from .config import Config
from .main import MauscribeApp, main
from .recorder import AudioRecorder
from .sound_controller import SoundController
from .spell_checker import SpellGrammarChecker
from .stt import SpeechToText

__all__ = [
    "MauscribeApp",
    "main",
    "AudioRecorder",
    "SpeechToText",
    "SoundController",
    "SpellGrammarChecker",
]
