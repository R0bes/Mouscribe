# src/ui/icon_helper.py - Icon Helper for Cyberpunk Icons
"""
Helper functions for loading and using cyberpunk-themed icons in the UI.
"""

from pathlib import Path
from typing import Optional

import customtkinter as ctk


class IconHelper:
    """Helper class for loading cyberpunk icons."""

    def __init__(self):
        """Initialize icon helper."""
        self.icons_dir = Path(__file__).parent / "icons" / "ui"

    def get_icon_path(self, icon_name: str, size: int = 24) -> Optional[Path]:
        """Get path to icon file.

        Args:
            icon_name: Name of the icon (e.g., 'play', 'pause', 'delete')
            size: Icon size (16, 24, 32)

        Returns:
            Path to icon file or None if not found
        """
        icon_path = self.icons_dir / f"{icon_name}_{size}.png"
        if icon_path.exists():
            return icon_path
        return None

    def create_icon_button(self, parent, icon_name: str, size: int = 24, **kwargs) -> ctk.CTkButton:
        """Create a button with cyberpunk icon.

        Args:
            parent: Parent widget
            icon_name: Name of the icon
            size: Icon size
            **kwargs: Additional button arguments

        Returns:
            CTkButton with icon
        """
        icon_path = self.get_icon_path(icon_name, size)

        if icon_path:
            # Use image icon
            try:
                icon_image = ctk.CTkImage(light_image=str(icon_path), size=(size, size))
                return ctk.CTkButton(parent, image=icon_image, **kwargs)
            except Exception:
                # Fallback to text icon
                pass

        # Fallback to emoji icons
        emoji_map = {
            "play": "▶️",
            "pause": "⏸️",
            "stop": "⏹️",
            "edit": "✏️",
            "copy": "📋",
            "refresh": "🔄",
            "delete": "🗑️",
            "settings": "⚙️",
            "status_success": "✅",
            "status_error": "❌",
            "status_warning": "⚠️",
        }

        text = emoji_map.get(icon_name, "?")
        return ctk.CTkButton(parent, text=text, **kwargs)


# Global instance
icon_helper = IconHelper()
