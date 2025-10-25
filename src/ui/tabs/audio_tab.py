# src/ui/tabs/audio_tab.py - Audio Files Tab for Control Center
"""
Audio Files Tab implementation for Mauscribe Control Center.
Features: File browser, play, delete, export, and disk usage.
"""

import os
import sqlite3
import subprocess
import time
from pathlib import Path
from typing import Any, List, Optional

import customtkinter as ctk
import pygame

from ..icon_helper import icon_helper
from ..theme import CyberpunkTheme


class AudioTab(ctk.CTkFrame):
    """Audio files tab with file browser and management."""

    def __init__(self, parent: ctk.CTkTabview, app_instance: Any = None, **kwargs):
        """Initialize the Audio files tab.

        Args:
            parent: Parent widget
            app_instance: Reference to main application instance
        """
        super().__init__(parent, **kwargs)
        self.app_instance = app_instance

        # State
        self.current_files = []
        self.selected_file = None
        self.file_cards = []  # Store card references for reuse
        self.current_page = 0
        self.page_size = 20
        self.is_closing = False

        # Audio player state
        self.currently_playing = None
        self.is_playing = False
        self.playback_position = 0.0
        self.playback_duration = 0.0
        self.playback_timer = None

        # Create UI
        self._create_layout()

        # Load audio files from database
        self._load_audio_files()

        # Subscribe to audio file events
        self._subscribe_to_events()

    def _subscribe_to_events(self) -> None:
        """Subscribe to audio file events."""
        try:
            from ...utils.eventbus import EventType, subscribe_to_event

            # Subscribe to audio file saved event
            subscribe_to_event(EventType.AUDIO_FILE_SAVED, self._on_audio_file_saved)

            print("✅ Audio Files Tab subscribed to AUDIO_FILE_SAVED events")

        except Exception as e:
            print(f"Failed to subscribe to audio events: {e}")

    def _on_audio_file_saved(self, event) -> None:
        """Handle audio file saved event."""
        try:
            print("🎵 New audio file saved - refreshing list")
            # Reload audio files from database
            self._load_audio_files()

        except Exception as e:
            print(f"Error handling audio file saved event: {e}")

    def _create_layout(self) -> None:
        """Create the audio files tab layout."""
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color=CyberpunkTheme.BG_SURFACE, corner_radius=8, border_width=1)
        main_frame.pack(fill="both", expand=True, padx=8, pady=8)

        # Header
        header_frame = ctk.CTkFrame(main_frame, fg_color=CyberpunkTheme.BG_ELEVATED, corner_radius=6, height=40)
        header_frame.pack(fill="x", padx=8, pady=(8, 2))
        header_frame.pack_propagate(False)

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="🎵 Audio Files Manager",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=CyberpunkTheme.ACCENT_CYAN,
        )
        title_label.pack(side="left", padx=20, pady=8)

        # Action buttons
        actions_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        actions_frame.pack(side="right", padx=20, pady=5)

        refresh_button = ctk.CTkButton(
            actions_frame,
            text="🔄 Refresh",
            width=100,
            height=30,
            font=ctk.CTkFont(size=12),
            fg_color=CyberpunkTheme.ACCENT_CYAN,
            hover_color=CyberpunkTheme.BUTTON_HOVER,
            command=self._refresh_files,
        )
        refresh_button.pack(side="right", padx=5)

        bulk_delete_button = ctk.CTkButton(
            actions_frame,
            text="🗑️ Bulk Delete",
            width=120,
            height=30,
            font=ctk.CTkFont(size=12),
            fg_color=CyberpunkTheme.STATUS_ERROR,
            hover_color="#CC1A33",
            command=self._bulk_delete_old_files,
        )
        bulk_delete_button.pack(side="right", padx=5)

        # Content area
        content_frame = ctk.CTkFrame(main_frame, fg_color=CyberpunkTheme.BG_DARK, corner_radius=6, border_width=1)
        content_frame.pack(fill="both", expand=True, padx=8, pady=4)

        # Scrollable frame for audio files
        self.files_frame = ctk.CTkScrollableFrame(content_frame, fg_color=CyberpunkTheme.BG_DARK)
        self.files_frame.pack(fill="both", expand=True, padx=4, pady=4)

        # Statistics panel
        stats_frame = ctk.CTkFrame(main_frame, fg_color=CyberpunkTheme.BG_ELEVATED, corner_radius=6, height=60)
        stats_frame.pack(fill="x", padx=8, pady=(2, 8))
        stats_frame.pack_propagate(False)

        # Statistics labels
        stats_left = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_left.pack(side="left", fill="x", expand=True, padx=8, pady=8)

        self.total_files_label = ctk.CTkLabel(
            stats_left,
            text="📁 Total Files: 0",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=CyberpunkTheme.TEXT_PRIMARY,
        )
        self.total_files_label.pack(anchor="w")

        self.total_size_label = ctk.CTkLabel(
            stats_left,
            text="💾 Total Size: 0 MB",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=CyberpunkTheme.TEXT_PRIMARY,
        )
        self.total_size_label.pack(anchor="w")

        stats_right = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_right.pack(side="right", fill="x", expand=True, padx=8, pady=8)

        self.total_duration_label = ctk.CTkLabel(
            stats_right,
            text="⏱️ Total Duration: 0:00",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=CyberpunkTheme.TEXT_PRIMARY,
        )
        self.total_duration_label.pack(anchor="e")

        self.status_label = ctk.CTkLabel(
            stats_right, text="Ready", font=ctk.CTkFont(size=10), text_color=CyberpunkTheme.TEXT_SECONDARY
        )
        self.status_label.pack(anchor="e")

    def _load_audio_files(self) -> None:
        """Load audio files from database."""
        try:
            # Import database
            from ...utils.database import AudioDatabase

            db = AudioDatabase()

            # Log database path for debugging
            print(f"Loading audio files from: {db.db_path}")

            # Check if database file exists
            if not os.path.exists(db.db_path):
                print(f"Database not found: {db.db_path}")
                self.status_label.configure(text="No database found")
                return

            # Get all audio recordings
            with sqlite3.connect(db.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # First check if table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='audio_recordings'")
                if not cursor.fetchone():
                    print("audio_recordings table not found")
                    self.status_label.configure(text="No audio_recordings table found")
                    return

                # Query audio files with transcriptions
                cursor.execute(
                    """
                    SELECT
                        a.id,
                        a.timestamp,
                        a.audio_file_path,
                        a.duration_seconds,
                        a.sample_rate,
                        a.channels,
                        a.audio_format,
                        a.file_size_bytes,
                        t.id as transcription_id,
                        t.raw_text,
                        t.corrected_text,
                        t.confidence_score,
                        t.language,
                        t.created_at as transcription_created_at
                    FROM audio_recordings a
                    LEFT JOIN transcriptions t ON a.id = t.audio_recording_id
                    ORDER BY a.timestamp DESC
                """
                )

                rows = cursor.fetchall()

                if not rows:
                    print("No audio recordings found in database")
                    self.status_label.configure(text="No audio files yet. Start recording to see files here.")
                    return

                self.current_files = [dict(row) for row in rows]
                print(f"Loaded {len(self.current_files)} audio files")

            print(f"About to refresh files with {len(self.current_files)} files")
            self._refresh_files()
            self.status_label.configure(text=f"Loaded {len(self.current_files)} audio files")
            print("Files refresh completed")

        except Exception as e:
            self.status_label.configure(text=f"Error loading files: {str(e)}")
            # Fallback: show sample data
            self._load_sample_data()

    def _load_sample_data(self) -> None:
        """Load sample audio file data."""
        self.current_files = [
            {
                "id": 1,
                "timestamp": "2024-10-17 11:30:15",
                "audio_file_path": "data/audio/recording_20241017_113015.wav",
                "duration_seconds": 3.2,
                "sample_rate": 44100,
                "channels": 1,
                "audio_format": "wav",
                "file_size_bytes": 282240,
            },
            {
                "id": 2,
                "timestamp": "2024-10-17 11:25:42",
                "audio_file_path": "data/audio/recording_20241017_112542.wav",
                "duration_seconds": 2.8,
                "sample_rate": 44100,
                "channels": 1,
                "audio_format": "wav",
                "file_size_bytes": 246960,
            },
            {
                "id": 3,
                "timestamp": "2024-10-17 11:20:33",
                "audio_file_path": "data/audio/recording_20241017_112033.wav",
                "duration_seconds": 4.1,
                "sample_rate": 44100,
                "channels": 1,
                "audio_format": "wav",
                "file_size_bytes": 361620,
            },
        ]
        self._refresh_files()

    def _refresh_files(self) -> None:
        """Refresh the audio files display."""
        try:
            # Check if widget still exists and not closing
            if not self.winfo_exists() or not self.files_frame.winfo_exists() or self.is_closing:
                return

            # Hide existing widgets instead of destroying them
            for widget in self.files_frame.winfo_children():
                widget.pack_forget()

            # Clear card references
            self.file_cards.clear()

            # Add file cards for current page
            start_idx = self.current_page * self.page_size
            end_idx = min(start_idx + self.page_size, len(self.current_files))

            # Only show files for current page
            for i, file_info in enumerate(self.current_files[start_idx:end_idx]):
                self._create_file_card(file_info, start_idx + i)

            # Update statistics
            self._update_statistics()

            # Add "Load More" button if there are more files
            self._add_load_more_button()

        except Exception as e:
            print(f"Refresh failed: {str(e)}")
            if hasattr(self, "status_label"):
                self.status_label.configure(text=f"Refresh failed: {str(e)}")

    def _create_file_card(self, file_info: dict, index: int) -> None:
        """Create an audio file card widget."""
        try:
            # Card frame - enhanced styling with glow effect
            card_frame = ctk.CTkFrame(
                self.files_frame,
                fg_color=CyberpunkTheme.BG_CARD,
                corner_radius=CyberpunkTheme.CORNER_RADIUS,
                border_width=CyberpunkTheme.BORDER_WIDTH,
                border_color=CyberpunkTheme.BORDER_COLOR,
                height=70,  # Slightly taller for better readability
            )
            card_frame.pack(fill="x", padx=4, pady=3)
            card_frame.pack_propagate(False)  # Maintain fixed height

            # Store card reference
            self.file_cards.append(card_frame)

            # Configure grid weights for responsive layout
            card_frame.grid_columnconfigure(1, weight=1)  # Transcription text expands

            # Timestamp (left, fixed width)
            timestamp_label = ctk.CTkLabel(
                card_frame,
                text=file_info["timestamp"].split(" ")[1][:8],  # Show only time HH:MM:SS
                font=ctk.CTkFont(size=11, weight="bold"),  # Increased from 10
                text_color=CyberpunkTheme.TEXT_SECONDARY,
                width=80,
            )
            timestamp_label.grid(row=0, column=0, padx=(8, 4), pady=8, sticky="w")

            # Transcription text (center, expands)
            transcription_text = file_info.get("raw_text") or "No transcription"
            if transcription_text and len(transcription_text) > 80:
                transcription_text = transcription_text[:77] + "..."

            transcription_label = ctk.CTkLabel(
                card_frame,
                text=transcription_text,
                font=ctk.CTkFont(size=12, weight="normal"),  # Increased from 11
                text_color=CyberpunkTheme.TEXT_PRIMARY,
                anchor="w",
                justify="left",
            )
            transcription_label.grid(row=0, column=1, padx=4, pady=8, sticky="ew")

            # Duration (right, fixed width)
            duration_label = ctk.CTkLabel(
                card_frame,
                text=f"{file_info['duration_seconds']:.1f}s",
                font=ctk.CTkFont(size=11, weight="bold"),  # Increased from 10
                text_color=CyberpunkTheme.ACCENT_CYAN,
                width=50,
            )
            duration_label.grid(row=0, column=2, padx=4, pady=8, sticky="e")

            # Actions frame (far right, hidden by default)
            actions_frame = ctk.CTkFrame(card_frame, fg_color="transparent", width=200)
            actions_frame.grid(row=0, column=3, padx=(4, 8), pady=8, sticky="e")
            actions_frame.grid_propagate(False)

            # Action buttons - compact design
            play_button = icon_helper.create_icon_button(
                actions_frame,
                "play",
                size=16,
                width=30,
                height=24,
                fg_color=CyberpunkTheme.STATUS_SUCCESS,
                hover_color="#00CC66",
                command=lambda: self._play_audio_inline(file_info),
            )
            play_button.pack(side="left", padx=1)

            # Add pause/stop buttons if this file is currently playing
            if self.currently_playing and self.currently_playing["id"] == file_info["id"]:
                if self.is_playing:
                    pause_button = ctk.CTkButton(
                        actions_frame,
                        text="⏸",
                        width=30,
                        height=24,
                        font=ctk.CTkFont(size=10),
                        fg_color=CyberpunkTheme.STATUS_WARNING,
                        hover_color="#CC6600",
                        command=self._pause_audio,
                    )
                    pause_button.pack(side="left", padx=1)
                else:
                    resume_button = ctk.CTkButton(
                        actions_frame,
                        text="▶",
                        width=30,
                        height=24,
                        font=ctk.CTkFont(size=10),
                        fg_color=CyberpunkTheme.STATUS_SUCCESS,
                        hover_color="#00CC66",
                        command=self._resume_audio,
                    )
                    resume_button.pack(side="left", padx=1)

                stop_button = ctk.CTkButton(
                    actions_frame,
                    text="⏹",
                    width=30,
                    height=24,
                    font=ctk.CTkFont(size=10),
                    fg_color=CyberpunkTheme.STATUS_ERROR,
                    hover_color="#CC1A33",
                    command=self._stop_audio,
                )
                stop_button.pack(side="left", padx=1)

            # Compact export button
            export_button = ctk.CTkButton(
                actions_frame,
                text="📤",
                width=30,
                height=24,
                font=ctk.CTkFont(size=10),
                fg_color=CyberpunkTheme.ACCENT_CYAN,
                hover_color=CyberpunkTheme.BUTTON_HOVER,
                command=lambda: self._export_file(file_info),
            )
            export_button.pack(side="left", padx=1)

            # Compact re-transcribe button
            retranscribe_button = ctk.CTkButton(
                actions_frame,
                text="🔄",
                width=30,
                height=24,
                font=ctk.CTkFont(size=10),
                fg_color=CyberpunkTheme.STATUS_WARNING,
                hover_color="#CC6600",
                command=lambda: self._retranscribe_file(file_info),
            )
            retranscribe_button.pack(side="left", padx=1)

            # Compact delete button
            delete_button = ctk.CTkButton(
                actions_frame,
                text="🗑",
                width=30,
                height=24,
                font=ctk.CTkFont(size=10),
                fg_color=CyberpunkTheme.STATUS_ERROR,
                hover_color="#CC1A33",
                command=lambda: self._delete_file(file_info),
            )
            delete_button.pack(side="right", padx=1)

        except Exception as e:
            print(f"Error creating file card: {str(e)}")

    def _add_load_more_button(self) -> None:
        """Add Load More button if there are more files to load."""
        try:
            total_files = len(self.current_files)
            current_end = (self.current_page + 1) * self.page_size

            if current_end < total_files:
                load_more_frame = ctk.CTkFrame(self.files_frame, fg_color="transparent")
                load_more_frame.pack(fill="x", padx=4, pady=8)

                load_more_button = ctk.CTkButton(
                    load_more_frame,
                    text=f"📥 Load More ({total_files - current_end} remaining)",
                    height=32,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    fg_color=CyberpunkTheme.ACCENT_CYAN,
                    hover_color="#00CCCC",
                    command=self._load_more_files,
                )
                load_more_button.pack(pady=4)

        except Exception as e:
            print(f"Error adding load more button: {str(e)}")

    def _load_more_files(self) -> None:
        """Load next page of files."""
        try:
            self.current_page += 1
            self._refresh_files()

            if hasattr(self, "status_label"):
                loaded_count = min((self.current_page + 1) * self.page_size, len(self.current_files))
                self.status_label.configure(text=f"Loaded {loaded_count} of {len(self.current_files)} files")

        except Exception as e:
            print(f"Error loading more files: {str(e)}")
            if hasattr(self, "status_label"):
                self.status_label.configure(text=f"Load more failed: {str(e)}")

    def _play_audio_inline(self, file_info: dict) -> None:
        """Play audio file using pygame mixer."""
        try:
            file_path = Path(file_info["audio_file_path"])
            if not file_path.exists():
                if hasattr(self, "status_label"):
                    self.status_label.configure(text=f"File not found: {file_path}")
                return

            # Stop current playback if playing
            if self.is_playing:
                self._stop_audio()

            # Initialize pygame mixer if not already done
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

            # Load and play the audio file
            pygame.mixer.music.load(str(file_path))
            pygame.mixer.music.play()

            # Update state
            self.currently_playing = file_info
            self.is_playing = True
            self.playback_duration = file_info["duration_seconds"]
            self.playback_position = 0.0

            # Start playback timer
            self._start_playback_timer()

            if hasattr(self, "status_label"):
                self.status_label.configure(text=f"Playing: {file_path.name}")

        except Exception as e:
            print(f"Error playing audio: {str(e)}")
            if hasattr(self, "status_label"):
                self.status_label.configure(text=f"Playback failed: {str(e)}")

    def _stop_audio(self) -> None:
        """Stop current audio playback."""
        try:
            if self.is_playing:
                pygame.mixer.music.stop()
                self.is_playing = False
                self.currently_playing = None
                self.playback_position = 0.0

                # Stop playback timer
                if self.playback_timer:
                    self.after_cancel(self.playback_timer)
                    self.playback_timer = None

                if hasattr(self, "status_label"):
                    self.status_label.configure(text="Playback stopped")

        except Exception as e:
            print(f"Error stopping audio: {str(e)}")

    def _pause_audio(self) -> None:
        """Pause current audio playback."""
        try:
            if self.is_playing:
                pygame.mixer.music.pause()
                self.is_playing = False

                if hasattr(self, "status_label"):
                    self.status_label.configure(text="Playback paused")

        except Exception as e:
            print(f"Error pausing audio: {str(e)}")

    def _resume_audio(self) -> None:
        """Resume paused audio playback."""
        try:
            if not self.is_playing and self.currently_playing:
                pygame.mixer.music.unpause()
                self.is_playing = True
                self._start_playback_timer()

                if hasattr(self, "status_label"):
                    self.status_label.configure(text="Playback resumed")

        except Exception as e:
            print(f"Error resuming audio: {str(e)}")

    def _start_playback_timer(self) -> None:
        """Start timer to update playback position."""

        def update_position():
            if self.is_playing:
                self.playback_position += 0.1  # Update every 100ms
                if self.playback_position >= self.playback_duration:
                    self._stop_audio()
                else:
                    self.playback_timer = self.after(100, update_position)

        self.playback_timer = self.after(100, update_position)

    def _retranscribe_file(self, file_info: dict) -> None:
        """Re-transcribe audio file."""
        try:
            if not self.app_instance:
                self.status_label.configure(text="No app instance available for re-transcription")
                return

            file_path = Path(file_info["audio_file_path"])
            if not file_path.exists():
                self.status_label.configure(text=f"File not found: {file_path}")
                return

            # Read audio file
            with open(file_path, "rb") as f:
                audio_data = f.read()

            self.status_label.configure(text=f"Re-transcribing: {file_path.name}")

            # Use app instance to transcribe
            if hasattr(self.app_instance, "transcriptor"):
                # Transcribe in background thread
                import threading

                def transcribe_thread():
                    try:
                        result = self.app_instance.transcriptor.transcribe(
                            audio_data,
                            model_size=self.app_instance.config.transcription.model,
                            language=self.app_instance.config.transcription.language,
                        )
                        if result:
                            # Update database with new transcription
                            from ...utils.database import AudioDatabase

                            db = AudioDatabase()

                            # Check if transcription already exists
                            with sqlite3.connect(db.db_path) as conn:
                                cursor = conn.cursor()
                                cursor.execute(
                                    "SELECT id FROM transcriptions WHERE audio_recording_id = ?", (file_info["id"],)
                                )
                                existing = cursor.fetchone()

                                if existing:
                                    # UPDATE existing transcription
                                    cursor.execute(
                                        """
                                        UPDATE transcriptions
                                        SET raw_text = ?, confidence_score = ?, language = ?, created_at = CURRENT_TIMESTAMP
                                        WHERE audio_recording_id = ?
                                    """,
                                        (result.text, result.confidence, result.language, file_info["id"]),
                                    )
                                else:
                                    # INSERT new transcription
                                    cursor.execute(
                                        """
                                        INSERT INTO transcriptions (audio_recording_id, raw_text, confidence_score, language, created_at)
                                        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                                    """,
                                        (file_info["id"], result.text, result.confidence, result.language),
                                    )

                                conn.commit()

                            # Refresh the display
                            self.after(0, self._load_audio_files)
                            self.after(
                                0, lambda: self.status_label.configure(text=f"Re-transcription completed: {file_path.name}")
                            )
                        else:
                            self.after(
                                0, lambda: self.status_label.configure(text=f"Re-transcription failed: {file_path.name}")
                            )
                    except Exception as exc:
                        error_msg = f"Re-transcription error: {str(exc)}"
                        self.after(0, lambda: self.status_label.configure(text=error_msg))

                threading.Thread(target=transcribe_thread, daemon=True).start()
            else:
                self.status_label.configure(text="Transcription service not available")

        except Exception as e:
            self.status_label.configure(text=f"Re-transcription failed: {str(e)}")

    def cleanup(self) -> None:
        """Cleanup resources and stop audio playback."""
        try:
            self.is_closing = True

            # Stop audio playback
            if self.is_playing:
                self._stop_audio()

            # Clear file cards
            self.file_cards.clear()
            self.current_files.clear()

            # Unsubscribe from events if event bus exists
            if hasattr(self.app_instance, "event_bus") and self.app_instance.event_bus:
                self.app_instance.event_bus.unsubscribe("audio_file_saved", self._on_audio_file_saved)

            print("🧹 AudioTab cleaned up")

        except Exception as e:
            print(f"❌ Error cleaning up AudioTab: {e}")

    def _play_file(self, file_info: dict) -> None:
        """Play audio file with system default player."""
        try:
            file_path = Path(file_info["audio_file_path"])

            if not file_path.exists():
                self.status_label.configure(text=f"File not found: {file_path}")
                return

            # Use system default player
            if os.name == "nt":  # Windows
                os.startfile(str(file_path))
            elif os.name == "posix":  # macOS and Linux
                subprocess.run(["open" if os.uname().sysname == "Darwin" else "xdg-open", str(file_path)])

            self.status_label.configure(text=f"Playing: {file_path.name}")

        except Exception as e:
            self.status_label.configure(text=f"Play failed: {str(e)}")

    def _export_file(self, file_info: dict) -> None:
        """Export audio file to a new location."""
        try:
            import tkinter.filedialog as fd

            file_path = Path(file_info["audio_file_path"])
            if not file_path.exists():
                self.status_label.configure(text=f"File not found: {file_path}")
                return

            # Ask user for export location
            export_path = fd.asksaveasfilename(
                title="Export Audio File",
                defaultextension=f".{file_info['audio_format']}",
                filetypes=[("Audio files", "*.wav *.mp3 *.ogg"), ("All files", "*.*")],
            )

            if export_path:
                import shutil

                shutil.copy2(file_path, export_path)
                self.status_label.configure(text=f"Exported to: {Path(export_path).name}")

        except Exception as e:
            self.status_label.configure(text=f"Export failed: {str(e)}")

    def _delete_file(self, file_info: dict) -> None:
        """Delete audio file and database record."""
        try:
            file_path = Path(file_info["audio_file_path"])

            # Delete file if it exists
            if file_path.exists():
                file_path.unlink()

            # Delete from database
            from ...utils.database import AudioDatabase

            db = AudioDatabase()

            with sqlite3.connect(db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM audio_recordings WHERE id = ?", (file_info["id"],))
                conn.commit()

            # Remove from current list
            self.current_files = [f for f in self.current_files if f["id"] != file_info["id"]]
            self._refresh_files()

            self.status_label.configure(text=f"Deleted file: {file_path.name}")

        except Exception as e:
            self.status_label.configure(text=f"Delete failed: {str(e)}")

    def _bulk_delete_old_files(self) -> None:
        """Delete old files (older than 30 days)."""
        try:
            from ...utils.database import AudioDatabase

            db = AudioDatabase()

            deleted_count = db.cleanup_old_recordings(days_to_keep=30)

            # Reload files
            self._load_audio_files()

            self.status_label.configure(text=f"Bulk deleted {deleted_count} old files")

        except Exception as e:
            self.status_label.configure(text=f"Bulk delete failed: {str(e)}")

    def _update_statistics(self) -> None:
        """Update the statistics display."""
        try:
            total_files = len(self.current_files)
            total_size = sum(f["file_size_bytes"] for f in self.current_files)
            total_duration = sum(f["duration_seconds"] for f in self.current_files)

            # Format duration
            hours = int(total_duration // 3600)
            minutes = int((total_duration % 3600) // 60)
            duration_str = f"{hours}:{minutes:02d}" if hours > 0 else f"{minutes}:{int(total_duration % 60):02d}"

            # Update labels
            self.total_files_label.configure(text=f"📁 Total Files: {total_files}")
            self.total_size_label.configure(text=f"💾 Total Size: {total_size/1024/1024:.1f} MB")
            self.total_duration_label.configure(text=f"⏱️ Total Duration: {duration_str}")

        except Exception as e:
            self.status_label.configure(text=f"Statistics update failed: {str(e)}")
