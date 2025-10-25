# src/ui/tabs/config_settings_tab.py - Configuration Settings Tab
"""
Configuration Settings Tab - Full settings.toml configuration interface
"""

from typing import Any, Optional

import customtkinter as ctk

from ..theme import CyberpunkTheme


class ConfigSettingsTab(ctk.CTkFrame):
    """Configuration Settings Tab for full settings.toml management."""

    def __init__(self, parent: ctk.CTkFrame, app_instance: Optional[Any] = None) -> None:
        """Initialize the Configuration Settings tab.

        Args:
            parent: Parent frame
            app_instance: Reference to main application instance
        """
        super().__init__(parent, fg_color=CyberpunkTheme.BG_DARK)

        self.app_instance = app_instance
        self.config = app_instance.config if app_instance else None

        # Create layout
        self._create_layout()

        # Load current settings
        self._load_settings()

    def _create_layout(self) -> None:
        """Create the settings layout."""
        # Main container with enhanced styling
        main_frame = ctk.CTkFrame(
            self,
            fg_color=CyberpunkTheme.BG_DARK,
            corner_radius=CyberpunkTheme.CORNER_RADIUS,
            border_width=CyberpunkTheme.BORDER_WIDTH,
            border_color=CyberpunkTheme.BORDER_GLOW,
        )
        main_frame.pack(fill="both", expand=True, padx=8, pady=8)

        # Header
        header_frame = ctk.CTkFrame(main_frame, fg_color=CyberpunkTheme.BG_ELEVATED, corner_radius=6, height=40)
        header_frame.pack(fill="x", padx=4, pady=(4, 2))
        header_frame.pack_propagate(False)

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="⚙️ Configuration Settings",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=CyberpunkTheme.ACCENT_CYAN,
        )
        title_label.pack(side="left", padx=10, pady=8)

        # Content area
        content_frame = ctk.CTkScrollableFrame(main_frame, fg_color=CyberpunkTheme.BG_SURFACE, corner_radius=6, border_width=1)
        content_frame.pack(fill="both", expand=True, padx=4, pady=2)

        # Create settings sections
        self._create_audio_settings(content_frame)
        self._create_transcription_settings(content_frame)
        self._create_recording_settings(content_frame)
        self._create_ui_settings(content_frame)

        # Save button
        save_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        save_frame.pack(fill="x", padx=4, pady=2)

        save_button = ctk.CTkButton(
            save_frame,
            text="💾 Save All Settings",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=CyberpunkTheme.ACCENT_CYAN,
            hover_color="#00CCCC",
            command=self._save_all_settings,
            height=40,
        )
        save_button.pack(side="right", padx=4, pady=4)

    def _create_audio_settings(self, parent: ctk.CTkScrollableFrame) -> None:
        """Create audio settings section."""
        # Audio section header
        audio_header = ctk.CTkLabel(
            parent, text="🔊 Audio Settings", font=ctk.CTkFont(size=14, weight="bold"), text_color=CyberpunkTheme.ACCENT_PINK
        )
        audio_header.pack(fill="x", padx=8, pady=(8, 4))

        # Volume reduction
        volume_frame = ctk.CTkFrame(parent, fg_color="transparent")
        volume_frame.pack(fill="x", padx=8, pady=4)

        volume_label = ctk.CTkLabel(
            volume_frame, text="Volume Reduction Factor:", font=ctk.CTkFont(size=12), text_color=CyberpunkTheme.TEXT_PRIMARY
        )
        volume_label.pack(anchor="w")

        self.volume_slider = ctk.CTkSlider(
            volume_frame, from_=0.0, to=1.0, number_of_steps=100, command=self._on_volume_change
        )
        self.volume_slider.pack(fill="x", pady=4)

        self.volume_value_label = ctk.CTkLabel(
            volume_frame, text="0.0", font=ctk.CTkFont(size=10), text_color=CyberpunkTheme.TEXT_SECONDARY
        )
        self.volume_value_label.pack(anchor="w")

    def _create_transcription_settings(self, parent: ctk.CTkScrollableFrame) -> None:
        """Create transcription settings section."""
        # Transcription section header
        trans_header = ctk.CTkLabel(
            parent,
            text="🎯 Transcription Settings",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=CyberpunkTheme.ACCENT_PINK,
        )
        trans_header.pack(fill="x", padx=8, pady=(8, 4))

        # Language
        lang_frame = ctk.CTkFrame(parent, fg_color="transparent")
        lang_frame.pack(fill="x", padx=8, pady=4)

        lang_label = ctk.CTkLabel(
            lang_frame, text="Language:", font=ctk.CTkFont(size=12), text_color=CyberpunkTheme.TEXT_PRIMARY
        )
        lang_label.pack(anchor="w")

        self.language_dropdown = ctk.CTkComboBox(
            lang_frame, values=["de", "en", "fr", "es", "it", "pt", "ru", "ja", "ko", "zh"], command=self._on_language_change
        )
        self.language_dropdown.pack(fill="x", pady=4)

        # Model
        model_frame = ctk.CTkFrame(parent, fg_color="transparent")
        model_frame.pack(fill="x", padx=8, pady=4)

        model_label = ctk.CTkLabel(
            model_frame, text="Whisper Model:", font=ctk.CTkFont(size=12), text_color=CyberpunkTheme.TEXT_PRIMARY
        )
        model_label.pack(anchor="w")

        self.model_dropdown = ctk.CTkComboBox(
            model_frame, values=["tiny", "base", "small", "medium", "large"], command=self._on_model_change
        )
        self.model_dropdown.pack(fill="x", pady=4)

    def _create_recording_settings(self, parent: ctk.CTkScrollableFrame) -> None:
        """Create recording settings section."""
        # Recording section header
        rec_header = ctk.CTkLabel(
            parent,
            text="🎙️ Recording Settings",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=CyberpunkTheme.ACCENT_PINK,
        )
        rec_header.pack(fill="x", padx=8, pady=(8, 4))

        # Recording mode
        mode_frame = ctk.CTkFrame(parent, fg_color="transparent")
        mode_frame.pack(fill="x", padx=8, pady=4)

        mode_label = ctk.CTkLabel(
            mode_frame, text="Recording Mode:", font=ctk.CTkFont(size=12), text_color=CyberpunkTheme.TEXT_PRIMARY
        )
        mode_label.pack(anchor="w")

        self.mode_dropdown = ctk.CTkComboBox(mode_frame, values=["Normal", "Enhanced"], command=self._on_mode_change)
        self.mode_dropdown.pack(fill="x", pady=4)

    def _create_ui_settings(self, parent: ctk.CTkScrollableFrame) -> None:
        """Create UI settings section."""
        # UI section header
        ui_header = ctk.CTkLabel(
            parent, text="🎨 UI Settings", font=ctk.CTkFont(size=14, weight="bold"), text_color=CyberpunkTheme.ACCENT_PINK
        )
        ui_header.pack(fill="x", padx=8, pady=(8, 4))

        # Theme
        theme_frame = ctk.CTkFrame(parent, fg_color="transparent")
        theme_frame.pack(fill="x", padx=8, pady=4)

        theme_label = ctk.CTkLabel(
            theme_frame, text="Theme:", font=ctk.CTkFont(size=12), text_color=CyberpunkTheme.TEXT_PRIMARY
        )
        theme_label.pack(anchor="w")

        self.theme_dropdown = ctk.CTkComboBox(
            theme_frame, values=["Cyberpunk", "Dark", "Light"], command=self._on_theme_change
        )
        self.theme_dropdown.pack(fill="x", pady=4)

    def _load_settings(self) -> None:
        """Load current settings from config."""
        if not self.config:
            return

        try:
            # Audio settings
            if hasattr(self.config, "audio") and hasattr(self.config.audio, "volume_reduction_factor"):
                self.volume_slider.set(self.config.audio.volume_reduction_factor)
                self.volume_value_label.configure(text=f"{self.config.audio.volume_reduction_factor:.2f}")

            # Transcription settings
            if hasattr(self.config, "transcription"):
                if hasattr(self.config.transcription, "language"):
                    self.language_dropdown.set(self.config.transcription.language)
                if hasattr(self.config.transcription, "model"):
                    self.model_dropdown.set(self.config.transcription.model)

            # Recording settings
            if hasattr(self.config, "recording_mode"):
                self.mode_dropdown.set(self.config.recording_mode)

            # UI settings
            self.theme_dropdown.set("Cyberpunk")

        except Exception as e:
            print(f"Error loading settings: {e}")

    def _on_volume_change(self, value: float) -> None:
        """Handle volume slider change."""
        self.volume_value_label.configure(text=f"{value:.2f}")

    def _on_language_change(self, choice: str) -> None:
        """Handle language dropdown change."""
        if self.config and hasattr(self.config, "transcription"):
            self.config.transcription.language = choice

    def _on_model_change(self, choice: str) -> None:
        """Handle model dropdown change."""
        if self.config and hasattr(self.config, "transcription"):
            self.config.transcription.model = choice

    def _on_mode_change(self, choice: str) -> None:
        """Handle recording mode change."""
        if self.config:
            self.config.recording_mode = choice.lower()

    def _on_theme_change(self, choice: str) -> None:
        """Handle theme change."""
        # TODO: Implement theme switching
        pass

    def _save_all_settings(self) -> None:
        """Save all settings to config file."""
        try:
            if not self.config:
                return

            # Update config values
            if hasattr(self.config, "audio"):
                self.config.audio.volume_reduction_factor = self.volume_slider.get()

            if hasattr(self.config, "transcription"):
                self.config.transcription.language = self.language_dropdown.get()
                self.config.transcription.model = self.model_dropdown.get()

            self.config.recording_mode = self.mode_dropdown.get().lower()

            # Save to file
            self.config.save()

            print("✅ Settings saved successfully!")

        except Exception as e:
            print(f"❌ Error saving settings: {e}")
