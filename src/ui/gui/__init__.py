# src/ui/gui/__init__.py - GUI Package for Mauscribe
"""
GUI components for Mauscribe application.
Contains all graphical user interface elements.
"""

from .manager import GUIManager
from .unified_manager_gui import UnifiedManagerGUI

__all__ = ["UnifiedManagerGUI", "GUIManager"]
