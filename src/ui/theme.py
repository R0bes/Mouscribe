# src/ui/theme.py - Enhanced Cyberpunk Theme
"""
Enhanced Cyberpunk theme for Mauscribe Control Center.
Modern styling with glow effects, animations, and improved UX.
"""


class CyberpunkTheme:
    """Enhanced Cyberpunk theme with modern effects and styling."""

    # Background Colors - Deeper, more immersive
    BG_DARK = "#0A0E27"  # Deep dark blue
    BG_SURFACE = "#1A1F3A"  # Dark blue surface
    BG_ELEVATED = "#2A3A5A"  # Elevated surface
    BG_CARD = "#1E2A3F"  # Card background
    BG_GLASS = "rgba(26, 31, 58, 0.8)"  # Glass effect

    # Accent Colors - Focused Palette with Glow
    ACCENT_CYAN = "#00F0FF"  # Neon cyan
    ACCENT_PINK = "#FF0080"  # Neon pink

    # Status Colors - Cyan/Pink Variations with Glow
    STATUS_SUCCESS = "#00D0DD"  # Darker cyan
    STATUS_WARNING = "#FF60A0"  # Lighter pink
    STATUS_ERROR = "#FF0040"  # Brighter red-pink
    STATUS_INFO = "#00F0FF"  # Cyan

    # Enhanced Effects
    SHADOW_COLOR = "rgba(0, 0, 0, 0.6)"
    GLOW_CYAN = "#00F0FF"
    GLOW_PINK = "#FF0080"
    GLOW_INTENSITY = "0 0 20px"  # CSS glow effect

    # Text Colors - Better contrast
    TEXT_PRIMARY = "#E8E8E8"  # Brighter white
    TEXT_SECONDARY = "#B8B8B8"  # Medium gray
    TEXT_MUTED = "#888888"  # Muted gray
    TEXT_ACCENT = "#00F0FF"  # Cyan text

    # Border & Effects - Enhanced
    BORDER_COLOR = "#3A4A6A"  # Subtle border
    BORDER_GLOW = "#00F0FF"  # Glowing border
    CORNER_RADIUS = 8  # Slightly more rounded
    BORDER_WIDTH = 1  # Thin borders

    # Fonts - Modern and Bold
    FONT_TITLE = ("Segoe UI", 22, "bold")  # Larger title
    FONT_HEADER = ("Segoe UI", 18, "bold")  # Larger headers
    FONT_BODY = ("Segoe UI", 14, "normal")  # More readable
    FONT_SMALL = ("Segoe UI", 12, "normal")  # Better small text
    FONT_BOLD = ("Segoe UI", 13, "bold")  # Bold accent text
    FONT_MONO = ("Consolas", 12, "normal")  # Monospace for logs

    # Button Colors - Enhanced
    BUTTON_HOVER = "#3A4A6A"  # Button hover color
    BUTTON_ACTIVE = "#4A5A7A"  # Button active color

    # Animation Settings
    ANIMATION_DURATION = 200  # ms
    HOVER_TRANSITION = "smooth"

    # Card Effects
    CARD_SHADOW = "0 4px 12px rgba(0, 240, 255, 0.1)"
    CARD_HOVER_SHADOW = "0 8px 24px rgba(0, 240, 255, 0.2)"

    # Gradient Colors
    GRADIENT_CYAN = ["#00F0FF", "#00CCCC"]
    GRADIENT_PINK = ["#FF0080", "#CC0066"]
    GRADIENT_DARK = ["#0A0E27", "#1A1F3A"]

    # Special Effects
    PULSE_CYAN = "#00F0FF"
    PULSE_PINK = "#FF0080"

    @staticmethod
    def get_glow_color(color: str) -> str:
        """Get glow effect color for given base color."""
        if color == CyberpunkTheme.ACCENT_CYAN:
            return "rgba(0, 240, 255, 0.3)"
        elif color == CyberpunkTheme.ACCENT_PINK:
            return "rgba(255, 0, 128, 0.3)"
        else:
            return "rgba(255, 255, 255, 0.1)"

    @staticmethod
    def get_hover_color(base_color: str) -> str:
        """Get hover color for given base color."""
        if base_color == CyberpunkTheme.ACCENT_CYAN:
            return "#00CCCC"
        elif base_color == CyberpunkTheme.ACCENT_PINK:
            return "#CC0066"
        else:
            return CyberpunkTheme.BUTTON_HOVER
