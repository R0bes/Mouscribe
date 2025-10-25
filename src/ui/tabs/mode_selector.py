# src/ui/tabs/mode_selector.py - Mode Selection Tab
"""
Mode Selection Tab for switching between Normal and Enhanced modes.
"""

from typing import Any, Callable

import customtkinter as ctk

from ..theme import CyberpunkTheme


class ModeSelectorTab(ctk.CTkFrame):
    """Tab for selecting recording mode."""

    def __init__(self, parent: ctk.CTkTabview, app_instance: Any = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.app_instance = app_instance
        self.current_mode = "normal"

        self._create_layout()
        self._update_mode_display()

    def _create_layout(self) -> None:
        """Create the mode selector layout."""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=8, pady=(8, 4))

        title_label = ctk.CTkLabel(
            header_frame,
            text="🎛️ Recording Mode",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=CyberpunkTheme.ACCENT_CYAN,
        )
        title_label.pack(side="left", padx=20, pady=15)

        # Mode selection cards
        cards_frame = ctk.CTkFrame(self, fg_color=CyberpunkTheme.BG_DARK, corner_radius=8)
        cards_frame.pack(fill="both", expand=True, padx=8, pady=4)

        # Normal mode card
        self._create_mode_card(
            cards_frame,
            "normal",
            "📝 Normal Mode",
            "Audio files deleted after transcription",
            "Perfect for daily use and friends",
        )

        # Enhanced mode card
        self._create_mode_card(
            cards_frame, "enhanced", "🎯 Enhanced Mode", "Audio files saved permanently", "Perfect for training data collection"
        )

        # Current mode display
        self._create_current_mode_display(cards_frame)

        # Statistics
        self._create_statistics_display(cards_frame)

    def _create_mode_card(self, parent: ctk.CTkFrame, mode: str, title: str, description: str, use_case: str) -> None:
        """Create a mode selection card."""
        card_frame = ctk.CTkFrame(parent, fg_color=CyberpunkTheme.BG_SURFACE, corner_radius=8, border_width=1)
        card_frame.pack(fill="x", padx=8, pady=4)

        # Card content
        content_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=12, pady=12)

        # Title
        title_label = ctk.CTkLabel(
            content_frame,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=CyberpunkTheme.ACCENT_CYAN if mode == "enhanced" else CyberpunkTheme.TEXT_PRIMARY,
        )
        title_label.pack(anchor="w")

        # Description
        desc_label = ctk.CTkLabel(
            content_frame, text=description, font=ctk.CTkFont(size=11), text_color=CyberpunkTheme.TEXT_SECONDARY
        )
        desc_label.pack(anchor="w", pady=(4, 0))

        # Use case
        use_case_label = ctk.CTkLabel(
            content_frame, text=use_case, font=ctk.CTkFont(size=10), text_color=CyberpunkTheme.TEXT_MUTED
        )
        use_case_label.pack(anchor="w", pady=(2, 0))

        # Select button
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(8, 0))

        select_button = ctk.CTkButton(
            button_frame,
            text=f"Select {mode.title()} Mode",
            width=150,
            height=32,
            font=ctk.CTkFont(size=11),
            fg_color=CyberpunkTheme.ACCENT_CYAN if mode == "enhanced" else CyberpunkTheme.STATUS_SUCCESS,
            hover_color="#00CCCC" if mode == "enhanced" else "#00CC66",
            command=lambda: self._switch_mode(mode),
        )
        select_button.pack(side="right")

    def _create_current_mode_display(self, parent: ctk.CTkFrame) -> None:
        """Create current mode display."""
        current_frame = ctk.CTkFrame(parent, fg_color=CyberpunkTheme.BG_ELEVATED, corner_radius=8, border_width=1)
        current_frame.pack(fill="x", padx=8, pady=8)

        # Header
        header_frame = ctk.CTkFrame(current_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=12, pady=(12, 8))

        title_label = ctk.CTkLabel(
            header_frame,
            text="📊 Current Mode",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=CyberpunkTheme.ACCENT_PINK,
        )
        title_label.pack(side="left")

        # Mode indicator
        self.mode_indicator = ctk.CTkLabel(
            header_frame,
            text="Normal Mode",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=CyberpunkTheme.STATUS_SUCCESS,
        )
        self.mode_indicator.pack(side="right")

        # Session info
        self.session_info = ctk.CTkLabel(
            current_frame, text="Session: None", font=ctk.CTkFont(size=10), text_color=CyberpunkTheme.TEXT_SECONDARY
        )
        self.session_info.pack(anchor="w", padx=12, pady=(0, 12))

    def _create_statistics_display(self, parent: ctk.CTkFrame) -> None:
        """Create statistics display."""
        stats_frame = ctk.CTkFrame(parent, fg_color=CyberpunkTheme.BG_ELEVATED, corner_radius=8, border_width=1)
        stats_frame.pack(fill="x", padx=8, pady=(0, 8))

        # Header
        header_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=12, pady=(12, 8))

        title_label = ctk.CTkLabel(
            header_frame,
            text="📈 Session Statistics",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=CyberpunkTheme.ACCENT_PINK,
        )
        title_label.pack(side="left")

        # Refresh button
        refresh_button = ctk.CTkButton(
            header_frame,
            text="🔄 Refresh",
            width=80,
            height=24,
            font=ctk.CTkFont(size=10),
            fg_color=CyberpunkTheme.ACCENT_CYAN,
            hover_color="#00CCCC",
            command=self._refresh_statistics,
        )
        refresh_button.pack(side="right")

        # Statistics labels
        stats_content = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_content.pack(fill="x", padx=12, pady=(0, 12))

        self.stats_labels = {}
        stats_info = [
            ("Total Recordings", "0"),
            ("Total Duration", "0:00"),
            ("Average Confidence", "0%"),
            ("Training Data", "0 items"),
        ]

        for i, (label, value) in enumerate(stats_info):
            frame = ctk.CTkFrame(stats_content, fg_color="transparent")
            frame.pack(fill="x", pady=2)

            label_widget = ctk.CTkLabel(
                frame, text=f"{label}:", font=ctk.CTkFont(size=10), text_color=CyberpunkTheme.TEXT_SECONDARY
            )
            label_widget.pack(side="left")

            value_widget = ctk.CTkLabel(
                frame, text=value, font=ctk.CTkFont(size=10, weight="bold"), text_color=CyberpunkTheme.TEXT_PRIMARY
            )
            value_widget.pack(side="right")

            self.stats_labels[label] = value_widget

    def _switch_mode(self, mode: str) -> None:
        """Switch recording mode."""
        try:
            if not self.app_instance:
                print("No app instance available")
                return

            # Switch mode in app
            if hasattr(self.app_instance, "switch_recording_mode"):
                self.app_instance.switch_recording_mode(mode)
                self.current_mode = mode
                self._update_mode_display()
                print(f"✅ Switched to {mode} mode")
            else:
                print("App instance doesn't support mode switching")

        except Exception as e:
            print(f"❌ Failed to switch mode: {e}")

    def _update_mode_display(self) -> None:
        """Update mode display."""
        if self.current_mode == "enhanced":
            self.mode_indicator.configure(text="Enhanced Mode", text_color=CyberpunkTheme.ACCENT_CYAN)
        else:
            self.mode_indicator.configure(text="Normal Mode", text_color=CyberpunkTheme.STATUS_SUCCESS)

        # Update session info
        if self.app_instance and hasattr(self.app_instance, "enhanced_db"):
            session_id = self.app_instance.enhanced_db.current_session_id
            if session_id:
                self.session_info.configure(text=f"Session: {session_id[:12]}...")
            else:
                self.session_info.configure(text="Session: None")

    def _refresh_statistics(self) -> None:
        """Refresh statistics display."""
        try:
            if not self.app_instance or not hasattr(self.app_instance, "get_recording_stats"):
                return

            stats = self.app_instance.get_recording_stats()

            # Update statistics labels
            self.stats_labels["Total Recordings"].configure(text=str(stats.get("total_recordings", 0)))

            duration = stats.get("total_duration", 0)
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            self.stats_labels["Total Duration"].configure(text=f"{minutes}:{seconds:02d}")

            confidence = stats.get("average_confidence", 0)
            self.stats_labels["Average Confidence"].configure(text=f"{confidence:.1%}")

            # Training data count (would need to be implemented)
            self.stats_labels["Training Data"].configure(text="0 items")

        except Exception as e:
            print(f"Failed to refresh statistics: {e}")
