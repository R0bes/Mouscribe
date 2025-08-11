"""
Mauscribe - Voice-to-Text Tool
"""

import warnings
import logging

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Configure logging to be less verbose
logging.getLogger().setLevel(logging.WARNING)

__version__ = "1.0.0"
__author__ = "Robs"
__description__ = "Voice-to-Text Tool mit Push-to-Talk und automatischem Clipboard-Management"

from .main import MauscribeController, main
from .config import *
from .recorder import AudioRecorder
from .stt import SpeechToText
from .sound_controller import SoundController

__all__ = [
    "MauscribeController",
    "main",
    "AudioRecorder",
    "SpeechToText",
    "SoundController",
]
