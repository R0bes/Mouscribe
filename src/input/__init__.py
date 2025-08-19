"""
Input handling package for Mauscribe.

This package contains:
- input_handler: Main input interface with unified mouse and keyboard handling
- input_filter: Input event filtering and processing
- keys: Button mapping and configuration
"""

from .input_handler import InputHandler

__all__: list[str] = ["InputHandler"]
