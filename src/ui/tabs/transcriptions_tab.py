# src/ui/tabs/transcriptions_tab.py - Transcriptions Tab for Control Center
"""
Transcriptions Tab implementation for Mauscribe Control Center.
Features: List view, detail view, filter, search, and actions (copy, delete, export).
"""

import os
import sqlite3
import time
from typing import Any, List, Optional

import customtkinter as ctk

from ..theme import CyberpunkTheme


class TranscriptionsTab(ctk.CTkFrame):
    """Transcriptions tab with list view and detail view."""

    def __init__(self, parent: ctk.CTkTabview, app_instance: Any = None, **kwargs):
        """Initialize the Transcriptions tab.

        Args:
            parent: Parent widget
            app_instance: Reference to main application instance
        """
        super().__init__(parent, **kwargs)
        self.app_instance = app_instance

        # State
        self.current_transcriptions = []
        self.selected_transcription = None

        # Create UI
        self._create_layout()

        # Load real transcriptions from database
        self._load_transcriptions()

        # Subscribe to transcription events
        self._subscribe_to_events()

    def _subscribe_to_events(self) -> None:
        """Subscribe to transcription events."""
        try:
            from ...utils.eventbus import EventType, subscribe_to_event

            # Subscribe to transcription completed event
            subscribe_to_event(EventType.TRANSCRIPTION_COMPLETED, self._on_transcription_completed)

            print("✅ Transcriptions Tab subscribed to TRANSCRIPTION_COMPLETED events")

        except Exception as e:
            print(f"Failed to subscribe to transcription events: {e}")

    def _on_transcription_completed(self, event) -> None:
        """Handle transcription completed event."""
        try:
            print("📝 New transcription completed - refreshing list")
            # Reload transcriptions from database
            self._load_transcriptions()

        except Exception as e:
            print(f"Error handling transcription completed event: {e}")

    def _load_transcriptions(self) -> None:
        """Load transcriptions from database."""
        try:
            import sqlite3

            from ...utils.database import AudioDatabase

            db = AudioDatabase()

            print(f"Loading transcriptions from: {db.db_path}")

            # Check if database file exists
            if not os.path.exists(db.db_path):
                print(f"Database not found: {db.db_path}")
                self._show_empty_state("No database found")
                return

            with sqlite3.connect(db.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT
                        t.id,
                        t.raw_text,
                        t.corrected_text,
                        t.confidence_score,
                        t.language,
                        t.created_at,
                        a.audio_file_path
                    FROM transcriptions t
                    LEFT JOIN audio_recordings a ON t.audio_recording_id = a.id
                    ORDER BY t.created_at DESC
                    LIMIT 100
                """
                )

                rows = cursor.fetchall()

                if not rows:
                    print("No transcriptions found in database")
                    self._show_empty_state("No transcriptions yet")
                    return

                self.current_transcriptions = [dict(row) for row in rows]
                print(f"Loaded {len(self.current_transcriptions)} transcriptions")

            self._refresh_transcriptions()

        except Exception as e:
            print(f"Failed to load transcriptions: {e}")
            self._show_empty_state(f"Error loading transcriptions: {e}")

    def _show_empty_state(self, message: str) -> None:
        """Show empty state message."""
        try:
            # Clear existing transcriptions
            for widget in self.transcriptions_frame.winfo_children():
                widget.destroy()

            # Add empty state message
            empty_label = ctk.CTkLabel(
                self.transcriptions_frame,
                text=message,
                font=CyberpunkTheme.FONT_BODY,
                text_color=CyberpunkTheme.TEXT_SECONDARY,
            )
            empty_label.pack(pady=50)

        except Exception as e:
            print(f"Failed to show empty state: {e}")

    def _create_layout(self) -> None:
        """Create the transcriptions tab layout."""
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color=CyberpunkTheme.BG_SURFACE, corner_radius=8, border_width=1)
        main_frame.pack(fill="both", expand=True, padx=8, pady=8)

        # Header
        header_frame = ctk.CTkFrame(main_frame, fg_color=CyberpunkTheme.BG_ELEVATED, corner_radius=6, height=50)
        header_frame.pack(fill="x", padx=8, pady=(8, 4))
        header_frame.pack_propagate(False)

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="📝 Transcriptions Manager",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=CyberpunkTheme.ACCENT_CYAN,
        )
        title_label.pack(side="left", padx=20, pady=15)

        # Refresh button
        refresh_button = ctk.CTkButton(
            header_frame,
            text="🔄 Refresh",
            width=100,
            height=30,
            font=ctk.CTkFont(size=12),
            fg_color=CyberpunkTheme.ACCENT_CYAN,
            hover_color=CyberpunkTheme.BUTTON_HOVER,
            command=self._refresh_transcriptions,
        )
        refresh_button.pack(side="right", padx=20, pady=10)

        # Content area
        content_frame = ctk.CTkFrame(main_frame, fg_color=CyberpunkTheme.BG_DARK, corner_radius=6, border_width=1)
        content_frame.pack(fill="both", expand=True, padx=8, pady=4)

        # Scrollable frame for transcriptions
        self.transcriptions_frame = ctk.CTkScrollableFrame(content_frame, fg_color=CyberpunkTheme.BG_DARK)
        self.transcriptions_frame.pack(fill="both", expand=True, padx=4, pady=4)

        # Status bar
        status_frame = ctk.CTkFrame(main_frame, fg_color=CyberpunkTheme.BG_ELEVATED, corner_radius=6, height=30)
        status_frame.pack(fill="x", padx=8, pady=(4, 8))
        status_frame.pack_propagate(False)

        self.status_label = ctk.CTkLabel(
            status_frame, text="Ready", font=ctk.CTkFont(size=10), text_color=CyberpunkTheme.TEXT_SECONDARY
        )
        self.status_label.pack(side="left", padx=8, pady=6)

    def _load_sample_data(self) -> None:
        """Load sample transcription data."""
        self.current_transcriptions = [
            {
                "id": 1,
                "timestamp": "2024-10-17 11:30:15",
                "text": "Hallo, das ist eine Test-Transkription für das Control Center.",
                "confidence": 0.95,
                "duration": 3.2,
            },
            {
                "id": 2,
                "timestamp": "2024-10-17 11:25:42",
                "text": "Das ist ein weiterer Test mit niedrigerer Konfidenz.",
                "confidence": 0.78,
                "duration": 2.8,
            },
            {
                "id": 3,
                "timestamp": "2024-10-17 11:20:33",
                "text": "Cyberpunk Control Center funktioniert einwandfrei!",
                "confidence": 0.92,
                "duration": 4.1,
            },
        ]
        self._refresh_transcriptions()

    def _refresh_transcriptions(self) -> None:
        """Refresh the transcriptions display."""
        try:
            # Clear existing widgets
            for widget in self.transcriptions_frame.winfo_children():
                widget.destroy()

            # Add transcription cards
            for i, transcription in enumerate(self.current_transcriptions):
                self._create_transcription_card(transcription, i)

            # Update status
            self.status_label.configure(text=f"Showing {len(self.current_transcriptions)} transcriptions")

        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}")

    def _create_transcription_card(self, transcription: dict, index: int) -> None:
        """Create a transcription card widget."""
        # Card frame
        card_frame = ctk.CTkFrame(
            self.transcriptions_frame, fg_color=CyberpunkTheme.BG_SURFACE, corner_radius=8, border_width=1
        )
        card_frame.pack(fill="x", padx=4, pady=4)

        # Header with timestamp and confidence
        header_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=8, pady=(8, 4))

        # Timestamp
        timestamp_label = ctk.CTkLabel(
            header_frame,
            text=f"🕒 {transcription['timestamp']}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=CyberpunkTheme.TEXT_SECONDARY,
        )
        timestamp_label.pack(side="left")

        # Confidence indicator
        confidence_color = CyberpunkTheme.STATUS_SUCCESS if transcription["confidence"] > 0.9 else CyberpunkTheme.WARNING
        confidence_label = ctk.CTkLabel(
            header_frame,
            text=f"📊 {transcription['confidence']:.0%}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=confidence_color,
        )
        confidence_label.pack(side="right")

        # Text content
        text_label = ctk.CTkLabel(
            card_frame,
            text=transcription["text"],
            font=ctk.CTkFont(size=12),
            text_color=CyberpunkTheme.TEXT_PRIMARY,
            wraplength=800,
            justify="left",
        )
        text_label.pack(fill="x", padx=8, pady=4)

        # Actions frame
        actions_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        actions_frame.pack(fill="x", padx=8, pady=(4, 8))

        # Action buttons
        copy_button = ctk.CTkButton(
            actions_frame,
            text="📋 Copy",
            width=80,
            height=24,
            font=ctk.CTkFont(size=10),
            fg_color=CyberpunkTheme.ACCENT_CYAN,
            hover_color=CyberpunkTheme.BUTTON_HOVER,
            command=lambda: self._copy_transcription(transcription),
        )
        copy_button.pack(side="left", padx=2)

        delete_button = ctk.CTkButton(
            actions_frame,
            text="🗑️ Delete",
            width=80,
            height=24,
            font=ctk.CTkFont(size=10),
            fg_color=CyberpunkTheme.ERROR,
            hover_color="#CC1A33",
            command=lambda: self._delete_transcription(transcription),
        )
        delete_button.pack(side="left", padx=2)

        export_button = ctk.CTkButton(
            actions_frame,
            text="💾 Export",
            width=80,
            height=24,
            font=ctk.CTkFont(size=10),
            fg_color=CyberpunkTheme.STATUS_SUCCESS,
            hover_color="#00CC66",
            command=lambda: self._export_transcription(transcription),
        )
        export_button.pack(side="left", padx=2)

    def _copy_transcription(self, transcription: dict) -> None:
        """Copy transcription to clipboard."""
        try:
            import pyperclip

            pyperclip.copy(transcription["text"])
            self.status_label.configure(text=f"Copied: {transcription['text'][:30]}...")
        except Exception as e:
            self.status_label.configure(text=f"Copy failed: {str(e)}")

    def _delete_transcription(self, transcription: dict) -> None:
        """Delete transcription."""
        try:
            self.current_transcriptions = [t for t in self.current_transcriptions if t["id"] != transcription["id"]]
            self._refresh_transcriptions()
            self.status_label.configure(text=f"Deleted transcription {transcription['id']}")
        except Exception as e:
            self.status_label.configure(text=f"Delete failed: {str(e)}")

    def _export_transcription(self, transcription: dict) -> None:
        """Export transcription to file."""
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"transcription_{transcription['id']}_{timestamp}.txt"

            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"Transcription Export\n")
                f.write(f"ID: {transcription['id']}\n")
                f.write(f"Timestamp: {transcription['timestamp']}\n")
                f.write(f"Confidence: {transcription['confidence']:.0%}\n")
                f.write(f"Duration: {transcription['duration']}s\n")
                f.write("=" * 50 + "\n")
                f.write(transcription["text"])

            self.status_label.configure(text=f"Exported to {filename}")
        except Exception as e:
            self.status_label.configure(text=f"Export failed: {str(e)}")
