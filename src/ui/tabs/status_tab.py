# src/ui/tabs/status_tab.py - Status Tab for Control Center
"""
Status Tab implementation for Mauscribe Control Center.
Features: Real-time status display, recording state, transcription progress, system info.
"""

import threading
import time
from typing import Any, Optional

import customtkinter as ctk

from ...utils.eventbus import Event, EventType, get_event_bus, subscribe_to_event, unsubscribe_from_event
from ..theme import CyberpunkTheme


class StatusTab(ctk.CTkFrame):
    """Status tab showing real-time Mauscribe status."""

    def __init__(self, parent: ctk.CTkTabview, app_instance: Any = None, **kwargs):
        """Initialize the Status tab.

        Args:
            parent: Parent widget
            app_instance: Reference to main application instance for live updates
        """
        super().__init__(parent, **kwargs)
        self.app_instance = app_instance

        # State
        self.is_recording = False
        self.is_transcribing = False
        self.current_audio_duration = 0.0
        self.recording_start_time = None
        self.duration_timer = None
        self.last_transcription = ""
        self.system_status = "Ready"

        # Create UI
        self._create_layout()

        # Start event-based updates instead of polling
        self._start_event_updates()

    def _start_event_updates(self) -> None:
        """Start event-based updates using EventBus."""
        try:
            # Subscribe to recording events
            subscribe_to_event(EventType.RECORDING_STARTED, self._on_recording_started)
            subscribe_to_event(EventType.RECORDING_STOPPED, self._on_recording_stopped)
            subscribe_to_event(EventType.RECORDING_DURATION_UPDATE, self._on_recording_duration_update)

            # Subscribe to transcription events
            subscribe_to_event(EventType.TRANSCRIPTION_STARTED, self._on_transcription_started)
            subscribe_to_event(EventType.TRANSCRIPTION_COMPLETED, self._on_transcription_completed)
            subscribe_to_event(EventType.TRANSCRIPTION_FAILED, self._on_transcription_failed)

            print("✅ Status Tab subscribed to EventBus events")

        except Exception as e:
            print(f"Failed to subscribe to events: {e}")

    def _on_recording_started(self, event: Event) -> None:
        """Handle recording started event."""
        try:
            self.is_recording = True
            self.recording_start_time = time.time()
            self.current_audio_duration = 0.0

            # Start duration timer
            self._start_duration_timer()

            self._update_status()
            print("📊 Recording started - Status updated")
        except Exception as e:
            print(f"Error handling recording started: {e}")

    def _on_recording_stopped(self, event: Event) -> None:
        """Handle recording stopped event."""
        try:
            self.is_recording = False
            self.recording_start_time = None
            self.current_audio_duration = 0.0

            # Stop duration timer
            self._stop_duration_timer()

            self._update_status()
            print("📊 Recording stopped - Status updated")
        except Exception as e:
            print(f"Error handling recording stopped: {e}")

    def _start_duration_timer(self) -> None:
        """Start duration update timer."""

        def update_duration():
            if self.is_recording and self.recording_start_time:
                self.current_audio_duration = time.time() - self.recording_start_time
                self._update_status()
                # Schedule next update
                self.duration_timer = self.after(100, update_duration)  # Update every 100ms

        update_duration()

    def _stop_duration_timer(self) -> None:
        """Stop duration update timer."""
        if self.duration_timer:
            self.after_cancel(self.duration_timer)
            self.duration_timer = None

    def _on_recording_duration_update(self, event: Event) -> None:
        """Handle recording duration update event."""
        try:
            if self.is_recording and "duration" in event.data:
                self.current_audio_duration = event.data["duration"]
                self._update_status()
        except Exception as e:
            print(f"Error handling duration update: {e}")

    def _on_transcription_started(self, event: Event) -> None:
        """Handle transcription started event."""
        try:
            self.is_transcribing = True
            self._update_status()
            print("📊 Transcription started - Status updated")
        except Exception as e:
            print(f"Error handling transcription started: {e}")

    def _on_transcription_completed(self, event: Event) -> None:
        """Handle transcription completed event."""
        try:
            self.is_transcribing = False

            # Store transcription result
            if "text" in event.data:
                self.last_transcription = event.data["text"]
                if "confidence" in event.data:
                    confidence = event.data["confidence"]
                    print(f"📊 Transcription completed: '{self.last_transcription}' (confidence: {confidence:.2%})")

            self._update_status()
            print("📊 Transcription completed - Status updated")
        except Exception as e:
            print(f"Error handling transcription completed: {e}")

    def _on_transcription_failed(self, event: Event) -> None:
        """Handle transcription failed event."""
        try:
            self.is_transcribing = False
            self._update_status()
            print("📊 Transcription failed - Status updated")
        except Exception as e:
            print(f"Error handling transcription failed: {e}")

    def _create_layout(self) -> None:
        """Create the status tab layout."""
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color=CyberpunkTheme.BG_DARK, corner_radius=8, border_width=1)
        main_frame.pack(fill="both", expand=True, padx=4, pady=4)

        # Header
        header_frame = ctk.CTkFrame(main_frame, fg_color=CyberpunkTheme.BG_ELEVATED, corner_radius=6, height=50)
        header_frame.pack(fill="x", padx=4, pady=(4, 2))
        header_frame.pack_propagate(False)

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="📊 Mauscribe Status",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=CyberpunkTheme.ACCENT_CYAN,
        )
        title_label.pack(side="left", padx=10, pady=8)

        # Status cards container
        cards_frame = ctk.CTkFrame(main_frame, fg_color=CyberpunkTheme.BG_DARK, corner_radius=6, border_width=1)
        cards_frame.pack(fill="both", expand=True, padx=4, pady=2)

        # Recording status card
        self._create_recording_card(cards_frame)

        # Transcription status card
        self._create_transcription_card(cards_frame)

        # Transcription result view
        self._create_transcription_result_card(cards_frame)

        # Status bar
        status_frame = ctk.CTkFrame(main_frame, fg_color=CyberpunkTheme.BG_ELEVATED, corner_radius=6, height=30)
        status_frame.pack(fill="x", padx=4, pady=(2, 4))
        status_frame.pack_propagate(False)

        self.status_label = ctk.CTkLabel(
            status_frame, text="Ready", font=ctk.CTkFont(size=10), text_color=CyberpunkTheme.TEXT_SECONDARY
        )
        self.status_label.pack(side="left", padx=8, pady=6)

        self.last_update_label = ctk.CTkLabel(
            status_frame, text="", font=ctk.CTkFont(size=10), text_color=CyberpunkTheme.TEXT_SECONDARY
        )
        self.last_update_label.pack(side="right", padx=8, pady=6)

    def _create_recording_card(self, parent: ctk.CTkFrame) -> None:
        """Create recording status card."""
        card_frame = ctk.CTkFrame(parent, fg_color=CyberpunkTheme.BG_SURFACE, corner_radius=8, border_width=1)
        card_frame.pack(fill="x", padx=4, pady=2)

        # Card header
        header_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=6, pady=(6, 4))

        title_label = ctk.CTkLabel(
            header_frame,
            text="🎤 Recording Status",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=CyberpunkTheme.ACCENT_CYAN,
        )
        title_label.pack(side="left")

        # Status indicator
        self.recording_status_label = ctk.CTkLabel(
            header_frame, text="● IDLE", font=ctk.CTkFont(size=12, weight="bold"), text_color=CyberpunkTheme.TEXT_SECONDARY
        )
        self.recording_status_label.pack(side="right")

        # Recording info
        info_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=6, pady=(0, 6))

        self.recording_duration_label = ctk.CTkLabel(
            info_frame, text="Duration: 0:00", font=ctk.CTkFont(size=11), text_color=CyberpunkTheme.TEXT_PRIMARY
        )
        self.recording_duration_label.pack(anchor="w")

        self.recording_info_label = ctk.CTkLabel(
            info_frame, text="Ready to record", font=ctk.CTkFont(size=10), text_color=CyberpunkTheme.TEXT_SECONDARY
        )
        self.recording_info_label.pack(anchor="w")

    def _create_transcription_card(self, parent: ctk.CTkFrame) -> None:
        """Create transcription status card."""
        card_frame = ctk.CTkFrame(parent, fg_color=CyberpunkTheme.BG_SURFACE, corner_radius=8, border_width=1)
        card_frame.pack(fill="x", padx=4, pady=2)

        # Card header
        header_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=6, pady=(6, 4))

        title_label = ctk.CTkLabel(
            header_frame,
            text="📝 Transcription Status",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=CyberpunkTheme.ACCENT_CYAN,
        )
        title_label.pack(side="left")

        # Status indicator
        self.transcription_status_label = ctk.CTkLabel(
            header_frame, text="● IDLE", font=ctk.CTkFont(size=12, weight="bold"), text_color=CyberpunkTheme.TEXT_SECONDARY
        )
        self.transcription_status_label.pack(side="right")

        # Transcription info
        info_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=6, pady=(0, 6))

        self.transcription_progress_label = ctk.CTkLabel(
            info_frame, text="Progress: Ready", font=ctk.CTkFont(size=11), text_color=CyberpunkTheme.TEXT_PRIMARY
        )
        self.transcription_progress_label.pack(anchor="w")

        self.last_transcription_label = ctk.CTkLabel(
            info_frame,
            text="Last: None",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=CyberpunkTheme.ACCENT_CYAN,
            wraplength=600,
            justify="left",
        )
        self.last_transcription_label.pack(anchor="w", pady=(8, 0))

    def _create_transcription_result_card(self, parent: ctk.CTkFrame) -> None:
        """Create transcription result view card."""
        card_frame = ctk.CTkFrame(parent, fg_color=CyberpunkTheme.BG_SURFACE, corner_radius=8, border_width=1)
        card_frame.pack(fill="x", padx=4, pady=2)

        # Card header
        header_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=6, pady=(6, 4))

        title_label = ctk.CTkLabel(
            header_frame,
            text="📝 Latest Transcription",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=CyberpunkTheme.ACCENT_PINK,
        )
        title_label.pack(side="left")

        # Action buttons
        actions_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        actions_frame.pack(side="right")

        # Edit button
        self.edit_button = ctk.CTkButton(
            actions_frame,
            text="✏️ Edit",
            width=60,
            height=24,
            font=ctk.CTkFont(size=10),
            fg_color=CyberpunkTheme.STATUS_WARNING,
            hover_color="#CC6600",
            command=self._edit_transcription,
        )
        self.edit_button.pack(side="left", padx=(0, 4))

        # Copy button
        self.copy_button = ctk.CTkButton(
            actions_frame,
            text="📋 Copy",
            width=60,
            height=24,
            font=ctk.CTkFont(size=10),
            fg_color=CyberpunkTheme.ACCENT_CYAN,
            hover_color="#00CCCC",
            command=self._copy_transcription,
        )
        self.copy_button.pack(side="left")

        # Transcription text area
        text_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        text_frame.pack(fill="x", padx=12, pady=(0, 12))

        self.transcription_text = ctk.CTkTextbox(
            text_frame,
            height=100,
            font=ctk.CTkFont(size=11),
            text_color=CyberpunkTheme.TEXT_PRIMARY,
            fg_color=CyberpunkTheme.BG_DARK,
            border_width=1,
            border_color=CyberpunkTheme.BORDER_COLOR,
            corner_radius=6,
        )
        self.transcription_text.pack(fill="x")

        # Set initial text
        self.transcription_text.insert("1.0", "No transcription yet...")
        self.transcription_text.configure(state="disabled")

    def _edit_transcription(self) -> None:
        """Enable editing of transcription text."""
        if self.last_transcription:
            self.transcription_text.configure(state="normal")
            self.transcription_text.delete("1.0", "end")
            self.transcription_text.insert("1.0", self.last_transcription)
            self.edit_button.configure(text="💾 Save", command=self._save_transcription)
        else:
            print("No transcription to edit")

    def _save_transcription(self) -> None:
        """Save edited transcription."""
        edited_text = self.transcription_text.get("1.0", "end-1c")
        self.last_transcription = edited_text
        self.transcription_text.configure(state="disabled")
        self.edit_button.configure(text="✏️ Edit", command=self._edit_transcription)
        print(f"Transcription saved: {edited_text}")

    def _copy_transcription(self) -> None:
        """Copy transcription to clipboard."""
        if self.last_transcription:
            import tkinter as tk

            root = tk.Tk()
            root.withdraw()  # Hide the window
            root.clipboard_clear()
            root.clipboard_append(self.last_transcription)
            root.destroy()
            print("Transcription copied to clipboard")
        else:
            print("No transcription to copy")

    def _create_system_card(self, parent: ctk.CTkFrame) -> None:
        """Create system info card."""
        card_frame = ctk.CTkFrame(parent, fg_color=CyberpunkTheme.BG_SURFACE, corner_radius=8, border_width=1)
        card_frame.pack(fill="x", padx=4, pady=2)

        # Card header
        header_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=6, pady=(6, 4))

        title_label = ctk.CTkLabel(
            header_frame,
            text="⚙️ System Info",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=CyberpunkTheme.ACCENT_CYAN,
        )
        title_label.pack(side="left")

        # System info
        info_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=6, pady=(0, 6))

        self.system_status_label = ctk.CTkLabel(
            info_frame, text="Status: Ready", font=ctk.CTkFont(size=11), text_color=CyberpunkTheme.TEXT_PRIMARY
        )
        self.system_status_label.pack(anchor="w")

        self.uptime_label = ctk.CTkLabel(
            info_frame, text="Uptime: 0:00:00", font=ctk.CTkFont(size=10), text_color=CyberpunkTheme.TEXT_SECONDARY
        )
        self.uptime_label.pack(anchor="w")

        self.memory_label = ctk.CTkLabel(
            info_frame, text="Memory: Normal", font=ctk.CTkFont(size=10), text_color=CyberpunkTheme.TEXT_SECONDARY
        )
        self.memory_label.pack(anchor="w")

    def _create_activity_card(self, parent: ctk.CTkFrame) -> None:
        """Create recent activity card."""
        card_frame = ctk.CTkFrame(parent, fg_color=CyberpunkTheme.BG_SURFACE, corner_radius=8, border_width=1)
        card_frame.pack(fill="x", padx=4, pady=2)

        # Card header
        header_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=6, pady=(6, 4))

        title_label = ctk.CTkLabel(
            header_frame,
            text="📈 Recent Activity",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=CyberpunkTheme.ACCENT_CYAN,
        )
        title_label.pack(side="left")

        # Activity list
        self.activity_frame = ctk.CTkScrollableFrame(card_frame, fg_color=CyberpunkTheme.BG_DARK, corner_radius=4, height=120)
        self.activity_frame.pack(fill="x", padx=12, pady=(0, 12))

        # Add sample activities
        self._add_activity("🎮 Control Center opened", "just now")
        self._add_activity("📋 Logs loaded", "2 minutes ago")
        self._add_activity("🎵 Audio files refreshed", "5 minutes ago")

    def _add_activity(self, activity: str, timestamp: str) -> None:
        """Add an activity entry."""
        activity_frame = ctk.CTkFrame(self.activity_frame, fg_color="transparent")
        activity_frame.pack(fill="x", padx=4, pady=2)

        activity_label = ctk.CTkLabel(
            activity_frame, text=activity, font=ctk.CTkFont(size=10), text_color=CyberpunkTheme.TEXT_PRIMARY
        )
        activity_label.pack(side="left")

        timestamp_label = ctk.CTkLabel(
            activity_frame, text=timestamp, font=ctk.CTkFont(size=9), text_color=CyberpunkTheme.TEXT_SECONDARY
        )
        timestamp_label.pack(side="right")

    def _refresh_status(self) -> None:
        """Refresh status display manually."""
        self._update_status()

    def _status_update_loop(self) -> None:
        """Status update loop running in background thread."""
        while True:
            try:
                # Get live data from app instance first
                self._update_from_app_instance()
                # Then update UI
                self._update_status()
                time.sleep(0.5)  # Update every 500ms for responsive updates
            except Exception as e:
                print(f"Status update error: {e}")
                time.sleep(1)  # Wait longer on error

    def _update_from_app_instance(self) -> None:
        """Update status from Mauscribe app instance."""
        if not self.app_instance:
            return

        try:
            # Recording status from MauscribeApp.recorder
            if hasattr(self.app_instance, "recorder"):
                recorder = self.app_instance.recorder
                self.is_recording = recorder.is_recording
                if self.is_recording and hasattr(recorder, "recording_start_time"):
                    # Calculate duration
                    import time

                    self.current_audio_duration = time.time() - recorder.recording_start_time
                elif not self.is_recording:
                    self.current_audio_duration = 0.0

            # Transcription status from MauscribeApp.audio_service
            if hasattr(self.app_instance, "audio_service"):
                service = self.app_instance.audio_service
                # Check if transcription is in progress
                # Audio service doesn't have is_transcribing flag, so check thread activity
                self.is_transcribing = False  # Default to false
                # TODO: Implement proper transcription status detection

        except Exception as e:
            print(f"Failed to update from app instance: {e}")

    def _update_status(self) -> None:
        """Update all status displays."""
        try:
            # Update recording status
            if self.is_recording:
                self.recording_status_label.configure(text="● RECORDING", text_color=CyberpunkTheme.STATUS_ERROR)
                self.recording_duration_label.configure(text=f"Duration: {self.current_audio_duration:.1f}s")
                self.recording_info_label.configure(text="Recording in progress...")
            else:
                self.recording_status_label.configure(text="● IDLE", text_color=CyberpunkTheme.TEXT_SECONDARY)
                self.recording_duration_label.configure(text="Duration: 0:00")
                self.recording_info_label.configure(text="Ready to record")

            # Update transcription status
            if self.is_transcribing:
                self.transcription_status_label.configure(text="● PROCESSING", text_color=CyberpunkTheme.STATUS_WARNING)
                self.transcription_progress_label.configure(text="Progress: Transcribing...")
            else:
                self.transcription_status_label.configure(text="● IDLE", text_color=CyberpunkTheme.TEXT_SECONDARY)
                self.transcription_progress_label.configure(text="Progress: Ready")

            # Update last transcription
            if self.last_transcription:
                preview = (
                    self.last_transcription[:50] + "..." if len(self.last_transcription) > 50 else self.last_transcription
                )
                self.last_transcription_label.configure(text=f"Last: {preview}")

                # Update transcription text area
                if hasattr(self, "transcription_text"):
                    self.transcription_text.configure(state="normal")
                    self.transcription_text.delete("1.0", "end")
                    self.transcription_text.insert("1.0", self.last_transcription)
                    self.transcription_text.configure(state="disabled")
            else:
                self.last_transcription_label.configure(text="Last: None")

                # Update transcription text area
                if hasattr(self, "transcription_text"):
                    self.transcription_text.configure(state="normal")
                    self.transcription_text.delete("1.0", "end")
                    self.transcription_text.insert("1.0", "No transcription yet...")
                    self.transcription_text.configure(state="disabled")

            # Update system status
            self.system_status_label.configure(text=f"Status: {self.system_status}")

            # Update uptime (simplified)
            current_time = time.strftime("%H:%M:%S")
            self.uptime_label.configure(text=f"Time: {current_time}")

            # Update last update time
            self.last_update_label.configure(text=f"Updated: {time.strftime('%H:%M:%S')}")

        except Exception as e:
            self.status_label.configure(text=f"Update failed: {str(e)}")

    def _refresh_status(self) -> None:
        """Manually refresh status."""
        self._update_status()
        self.status_label.configure(text="Status refreshed")

    def set_recording_state(self, is_recording: bool, duration: float = 0.0) -> None:
        """Set recording state."""
        self.is_recording = is_recording
        self.current_audio_duration = duration

    def set_transcription_state(self, is_transcribing: bool, last_text: str = "") -> None:
        """Set transcription state."""
        self.is_transcribing = is_transcribing
        if last_text:
            self.last_transcription = last_text

    def set_system_status(self, status: str) -> None:
        """Set system status."""
        self.system_status = status
