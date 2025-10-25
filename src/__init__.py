"""
Mauscribe - Voice-to-Text Tool
"""

from .audio import AudioService, Recorder, Volumizer
from .config import get_config
from .input import InputManager
from .mouscribe import MauscribeApp
from .utils import AudioDatabase, CustomDict, get_logger

__all__ = [
    "MauscribeApp",
    "Recorder",
    "Volumizer",
    "AudioService",
    "InputManager",
    "get_config",
    "AudioDatabase",
    "CustomDict",
    "get_logger",
]
