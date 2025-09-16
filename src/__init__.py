"""
Mauscribe - Voice-to-Text Tool
"""
from .mouscribe import MauscribeApp
from .audio import (
    Recorder, 
    Transcriptor, 
    Volumizer
)
from .utils import (
    Settings, 
    AudioDatabase, 
    CustomDict, 
    get_logger
)

__all__ = [
    "MauscribeApp",
    "Recorder",
    "Transcriptor",
    "Volumizer",
    "AudioDatabase",
    "CustomDict",
    "Settings",
    "get_logger",
]
