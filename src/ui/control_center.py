# src/ui/control_center.py - Mauscribe Control Center
"""
Mauscribe Control Center - Modern GUI with Cyberpunk Theme
Clean architecture with proper theme management and tab integration.
"""

import sys
import threading
import time
from pathlib import Path
from typing import Any, Optional

import customtkinter as ctk

from ..config import AppConfig
from ..utils import get_logger
from .theme import CyberpunkTheme


class ControlCenterWindow:
    """Main Control Center window with Cyberpunk theme."""

    def __init__(self, config: AppConfig, app_instance: Any) -> None:
        """Initialize the Control Center window.

        Args:
            config: Application configuration
            app_instance: Reference to main application instance
        """
        self.config = config
        self.app_instance = app_instance
        self.logger = get_logger("ControlCenter")

        # Window state
        self.window: Optional[ctk.CTk] = None
        self.tab_view: Optional[ctk.CTkTabview] = None
        self.is_running = False
        self.is_closing = False
        self.tabs = {}  # Store tab references for cleanup

        self.logger.info("🎮 Control Center initialized")

    def create_window(self) -> None:
        """Create and configure the main window."""
        try:
            self.logger.info("🎮 Creating Control Center window...")

            # Setup logging for Control Center
            from ..utils.logger import setup_logging

            setup_logging()

            # Create main window with enhanced styling
            self.window = ctk.CTk()
            self.window.title("🎮 Mauscribe Control Center")
            self.window.geometry("1000x700")  # Larger for better experience
            self.window.minsize(800, 600)

            # Enhanced window styling
            self.window.configure(fg_color=CyberpunkTheme.BG_DARK)

            # Center window on screen
            self._center_window()

            # Apply Cyberpunk theme
            self._apply_theme()

            # Set window icon
            self._set_window_icon()

            # Create layout
            self._create_layout()

            # Setup window callbacks
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)

            self.is_running = True
            self.logger.info("✅ Control Center window created successfully")

        except Exception as e:
            self.logger.error(f"❌ Failed to create Control Center window: {e}")
            raise

    def _center_window(self) -> None:
        """Center the window on the screen."""
        try:
            self.window.update_idletasks()

            # Get screen dimensions
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()

            # Calculate position
            window_width = 900
            window_height = 600
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2

            # Set geometry
            self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")

            self.logger.info(f"📍 Window centered at ({x}, {y})")

        except Exception as e:
            self.logger.error(f"❌ Failed to center window: {e}")

    def _apply_theme(self) -> None:
        """Apply Cyberpunk theme to CustomTkinter."""
        try:
            # Set appearance mode
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("blue")

            # Get theme manager
            theme_manager = ctk.ThemeManager()

            # Apply Cyberpunk colors to theme
            theme_manager.theme["CTk"]["fg_color"] = [CyberpunkTheme.BG_DARK, CyberpunkTheme.BG_DARK]
            theme_manager.theme["CTk"]["text_color"] = [CyberpunkTheme.TEXT_PRIMARY, CyberpunkTheme.TEXT_PRIMARY]

            # Frame styling
            theme_manager.theme["CTkFrame"]["fg_color"] = [CyberpunkTheme.BG_SURFACE, CyberpunkTheme.BG_SURFACE]
            theme_manager.theme["CTkFrame"]["top_fg_color"] = [CyberpunkTheme.BG_ELEVATED, CyberpunkTheme.BG_ELEVATED]
            theme_manager.theme["CTkFrame"]["text_color"] = [CyberpunkTheme.TEXT_PRIMARY, CyberpunkTheme.TEXT_PRIMARY]

            # Button styling
            theme_manager.theme["CTkButton"]["fg_color"] = [CyberpunkTheme.BG_ELEVATED, CyberpunkTheme.BG_ELEVATED]
            theme_manager.theme["CTkButton"]["hover_color"] = [CyberpunkTheme.ACCENT_CYAN, CyberpunkTheme.ACCENT_CYAN]
            theme_manager.theme["CTkButton"]["text_color"] = [CyberpunkTheme.TEXT_PRIMARY, CyberpunkTheme.TEXT_PRIMARY]

            # Entry styling
            theme_manager.theme["CTkEntry"]["fg_color"] = [CyberpunkTheme.BG_DARK, CyberpunkTheme.BG_DARK]
            theme_manager.theme["CTkEntry"]["text_color"] = [CyberpunkTheme.TEXT_PRIMARY, CyberpunkTheme.TEXT_PRIMARY]

            # Textbox styling
            theme_manager.theme["CTkTextbox"]["fg_color"] = [CyberpunkTheme.BG_DARK, CyberpunkTheme.BG_DARK]
            theme_manager.theme["CTkTextbox"]["text_color"] = [CyberpunkTheme.TEXT_PRIMARY, CyberpunkTheme.TEXT_PRIMARY]

            # TabView styling (if available)
            if "CTkTabview" in theme_manager.theme:
                theme_manager.theme["CTkTabview"]["fg_color"] = [CyberpunkTheme.BG_SURFACE, CyberpunkTheme.BG_SURFACE]

            # Configure window background
            self.window.configure(fg_color=CyberpunkTheme.BG_DARK)

            self.logger.info("🎨 Cyberpunk theme applied successfully")

        except Exception as e:
            self.logger.error(f"❌ Failed to apply theme: {e}")

    def _set_window_icon(self) -> None:
        """Set window icon with fallback."""
        try:
            project_root = Path(__file__).parent.parent.parent
            icon_path = project_root / "src" / "ui" / "icons" / "icon.ico"

            if icon_path.exists():
                self.window.iconbitmap(str(icon_path))
                self.logger.info("🎯 Window icon set")
            else:
                self.logger.debug("Icon file not found, using default")

        except Exception as e:
            self.logger.debug(f"Icon loading failed: {e}")

    def _create_layout(self) -> None:
        """Create the main window layout."""
        try:
            self.logger.info("🎨 Creating window layout...")

            # Main container
            main_frame = ctk.CTkFrame(
                self.window,
                fg_color=CyberpunkTheme.BG_SURFACE,
                corner_radius=CyberpunkTheme.CORNER_RADIUS,
                border_width=CyberpunkTheme.BORDER_WIDTH,
            )
            main_frame.pack(fill="both", expand=True, padx=12, pady=12)

            # Header
            self._create_header(main_frame)

            # Tab view
            self._create_tab_view(main_frame)

            # Footer
            self._create_footer(main_frame)

            self.logger.info("✅ Layout created successfully")

        except Exception as e:
            self.logger.error(f"❌ Failed to create layout: {e}")
            raise

    def _create_header(self, parent: ctk.CTkFrame) -> None:
        """Create the header section."""
        try:
            header_frame = ctk.CTkFrame(parent, fg_color="transparent", height=60)
            header_frame.pack(fill="x", padx=8, pady=(8, 2))
            header_frame.pack_propagate(False)

            # Title
            title_label = ctk.CTkLabel(
                header_frame,
                text="🎮 Mauscribe Control Center",
                font=CyberpunkTheme.FONT_TITLE,
                text_color=CyberpunkTheme.ACCENT_CYAN,
            )
            title_label.pack(side="left", padx=8, pady=8)

            # Status indicator
            status_label = ctk.CTkLabel(
                header_frame, text="● Ready", font=CyberpunkTheme.FONT_SMALL, text_color=CyberpunkTheme.STATUS_SUCCESS
            )
            status_label.pack(side="right", padx=8, pady=8)

            self.logger.info("📋 Header created")

        except Exception as e:
            self.logger.error(f"❌ Failed to create header: {e}")

    def _create_tab_view(self, parent: ctk.CTkFrame) -> None:
        """Create the tab view with all tabs."""
        try:
            self.tab_view = ctk.CTkTabview(
                parent,
                fg_color=CyberpunkTheme.BG_SURFACE,
                corner_radius=CyberpunkTheme.CORNER_RADIUS,
                border_width=CyberpunkTheme.BORDER_WIDTH,
                segmented_button_fg_color=CyberpunkTheme.BG_ELEVATED,
                segmented_button_selected_color=CyberpunkTheme.ACCENT_CYAN,
                segmented_button_selected_hover_color=CyberpunkTheme.get_hover_color(CyberpunkTheme.ACCENT_CYAN),
                segmented_button_unselected_color=CyberpunkTheme.BG_ELEVATED,
                segmented_button_unselected_hover_color=CyberpunkTheme.BUTTON_HOVER,
                text_color=CyberpunkTheme.TEXT_PRIMARY,
                command=self._on_tab_change,
            )
            self.tab_view.pack(fill="both", expand=True, padx=8, pady=4)

            # Create tabs in order
            self._create_transcription_tab()
            self._create_audio_tab()
            self._create_logs_tab()
            self._create_settings_tab()

            self.logger.info("📑 Tab view created with all tabs")

        except Exception as e:
            self.logger.error(f"❌ Failed to create tab view: {e}")
            raise

    def _on_tab_change(self, tab_name: str = None) -> None:
        """Handle tab change events."""
        try:
            if tab_name:
                self.logger.info(f"🔄 Tab changed to: {tab_name}")
            else:
                self.logger.info("🔄 Tab changed")
            # Add any tab-specific initialization here
        except Exception as e:
            self.logger.error(f"❌ Error handling tab change: {e}")

    def _create_transcription_tab(self) -> None:
        """Create the Transcription tab (formerly Settings)."""
        try:
            transcription_tab = self.tab_view.add("🎤 Transcription")
            from .tabs import SettingsTab

            transcription_widget = SettingsTab(transcription_tab, app_instance=self.app_instance)
            transcription_widget.pack(fill="both", expand=True)

            # Store reference for cleanup
            self.tabs["transcription"] = transcription_widget

            self.logger.info("🎤 Transcription tab created")

        except Exception as e:
            self.logger.error(f"❌ Failed to create Transcription tab: {e}")

    def _create_settings_tab(self) -> None:
        """Create the Settings tab for configuration."""
        try:
            settings_tab = self.tab_view.add("⚙️ Settings")
            from .tabs import ConfigSettingsTab

            settings_widget = ConfigSettingsTab(settings_tab, app_instance=self.app_instance)
            settings_widget.pack(fill="both", expand=True)

            # Store reference for cleanup
            self.tabs["settings"] = settings_widget

            self.logger.info("⚙️ Settings tab created")

        except Exception as e:
            self.logger.error(f"❌ Failed to create Settings tab: {e}")

    def _create_audio_tab(self) -> None:
        """Create the Audio Files tab."""
        try:
            audio_tab = self.tab_view.add("🎵 Audio Files")
            from .tabs import AudioTab

            audio_widget = AudioTab(audio_tab, app_instance=self.app_instance)
            audio_widget.pack(fill="both", expand=True)

            # Store reference for cleanup
            self.tabs["audio"] = audio_widget

            self.logger.info("🎵 Audio Files tab created")

        except Exception as e:
            self.logger.error(f"❌ Failed to create Audio Files tab: {e}")

    def _create_logs_tab(self) -> None:
        """Create the Logs tab."""
        try:
            logs_tab = self.tab_view.add("📋 Logs")
            from .tabs import LogsTab

            logs_widget = LogsTab(logs_tab, app_instance=self.app_instance)
            logs_widget.pack(fill="both", expand=True)

            # Store reference for cleanup
            self.tabs["logs"] = logs_widget

            self.logger.info("📋 Logs tab created")

        except Exception as e:
            self.logger.error(f"❌ Failed to create Logs tab: {e}")

    def _create_footer(self, parent: ctk.CTkFrame) -> None:
        """Create the footer section."""
        try:
            footer_frame = ctk.CTkFrame(parent, fg_color="transparent", height=30)
            footer_frame.pack(fill="x", padx=8, pady=(2, 8))
            footer_frame.pack_propagate(False)

            # Status text
            status_text = ctk.CTkLabel(
                footer_frame,
                text="Mauscribe Control Center v2.0 | Ready",
                font=CyberpunkTheme.FONT_SMALL,
                text_color=CyberpunkTheme.TEXT_MUTED,
            )
            status_text.pack(side="left", padx=8, pady=4)

            # Version info
            version_text = ctk.CTkLabel(
                footer_frame, text="Cyberpunk Theme", font=CyberpunkTheme.FONT_SMALL, text_color=CyberpunkTheme.ACCENT_PINK
            )
            version_text.pack(side="right", padx=8, pady=4)

            self.logger.info("📄 Footer created")

        except Exception as e:
            self.logger.error(f"❌ Failed to create footer: {e}")

    def run(self) -> None:
        """Run the Control Center window."""
        try:
            if self.window and self.is_running:
                self.logger.info("🚀 Starting Control Center main loop")
                self.window.mainloop()
            else:
                self.logger.error("❌ Window not ready for main loop")

        except Exception as e:
            self.logger.error(f"❌ Error in main loop: {e}")

    def bring_to_front(self) -> None:
        """Bring the Control Center window to front and focus it."""
        try:
            if self.window:
                # Bring window to front
                self.window.lift()
                self.window.attributes("-topmost", True)
                self.window.after_idle(lambda: self.window.attributes("-topmost", False))

                # Focus the window
                self.window.focus_force()

                # On Windows, use win32gui to bring to front
                if sys.platform == "win32":
                    try:
                        import win32con
                        import win32gui

                        # Get window handle
                        hwnd = self.window.winfo_id()

                        # Bring window to front
                        win32gui.SetForegroundWindow(hwnd)
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

                    except ImportError:
                        # win32gui not available, use tkinter only
                        pass

                self.logger.info("🎯 Control Center brought to front")

        except Exception as e:
            self.logger.error(f"❌ Failed to bring window to front: {e}")

    def close_window(self) -> None:
        """Close the Control Center window."""
        try:
            self.logger.info("🔒 Closing Control Center")
            self.is_running = False
            self.is_closing = True

            # Check if we should close the main app
            if hasattr(self.app_instance, "config") and hasattr(self.app_instance.config.ui, "close_app_on_gui_close"):
                if self.app_instance.config.ui.close_app_on_gui_close:
                    self.logger.info("🔄 Closing main application...")
                    if hasattr(self.app_instance, "shutdown_event"):
                        self.app_instance.shutdown_event.set()

            # Cleanup tabs first
            self._cleanup_tabs()

            if self.window:
                self.window.destroy()
                self.window = None

            self.logger.info("✅ Control Center closed")

        except Exception as e:
            self.logger.error(f"❌ Error closing window: {e}")

    def _cleanup_tabs(self) -> None:
        """Cleanup all tabs and their event handlers."""
        try:
            for tab_name, tab_widget in self.tabs.items():
                if hasattr(tab_widget, "cleanup"):
                    tab_widget.cleanup()
                elif hasattr(tab_widget, "_cleanup"):
                    tab_widget._cleanup()

            self.tabs.clear()
            self.logger.info("🧹 Tabs cleaned up")

        except Exception as e:
            self.logger.error(f"❌ Error cleaning up tabs: {e}")


def open_control_center(config: AppConfig, app_instance: Any) -> None:
    """Open the Control Center in a separate thread.

    Args:
        config: Application configuration
        app_instance: Reference to main application instance
    """

    def run_control_center():
        """Run the Control Center in a separate thread."""
        try:
            logger = get_logger("ControlCenter")
            logger.info("🎮 Opening Control Center...")

            # Create and run Control Center
            control_center = ControlCenterWindow(config, app_instance)
            control_center.create_window()

            # Bring window to front and focus
            control_center.bring_to_front()

            control_center.run()

        except Exception as e:
            logger = get_logger("ControlCenter")
            logger.error(f"❌ Failed to open Control Center: {e}")

            # Show error notification if available
            if hasattr(app_instance, "toaster"):
                try:
                    app_instance.toaster.show_error("Control Center Error", f"Failed to open Control Center: {str(e)}")
                except Exception:
                    pass

    # Start Control Center in separate thread
    thread = threading.Thread(target=run_control_center, daemon=True)
    thread.start()
