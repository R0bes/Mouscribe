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


class SettingsTab(ctk.CTkFrame):
    """Settings tab for transcription configuration and real-time status."""

    def __init__(self, parent: ctk.CTkTabview, app_instance: Any = None, **kwargs):
        """Initialize the Settings tab.

        Args:
            parent: Parent widget
            app_instance: Reference to main application instance for live updates
        """
        super().__init__(parent, **kwargs)
        self.app_instance = app_instance

        # State
        self.is_recording = False
        self.is_transcribing = False
        self.is_closing = False
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

            self._safe_update_status()
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

            self._safe_update_status()
            print("📊 Recording stopped - Status updated")
        except Exception as e:
            print(f"Error handling recording stopped: {e}")

    def _start_duration_timer(self) -> None:
        """Start duration update timer."""

        def update_duration():
            if self.is_recording and self.recording_start_time:
                self.current_audio_duration = time.time() - self.recording_start_time
                self._safe_update_status()
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
                self._safe_update_status()
        except Exception as e:
            print(f"Error handling duration update: {e}")

    def _on_transcription_started(self, event: Event) -> None:
        """Handle transcription started event."""
        try:
            self.is_transcribing = True
            self._safe_update_status()
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

            self._safe_update_status()
            print("📊 Transcription completed - Status updated")
        except Exception as e:
            print(f"Error handling transcription completed: {e}")

    def _on_transcription_failed(self, event: Event) -> None:
        """Handle transcription failed event."""
        try:
            self.is_transcribing = False
            self._safe_update_status()
            print("📊 Transcription failed - Status updated")
        except Exception as e:
            print(f"Error handling transcription failed: {e}")

    def _create_settings_column(self, parent: ctk.CTkFrame) -> None:
        """Create the settings column with transcription controls."""
        # Settings frame
        settings_frame = ctk.CTkFrame(parent, fg_color=CyberpunkTheme.BG_SURFACE, corner_radius=6, border_width=1)
        settings_frame.grid(row=0, column=0, padx=(4, 2), pady=4, sticky="nsew")

        # Settings header
        settings_header = ctk.CTkLabel(
            settings_frame,
            text="🎛️ Transcription Settings",
            font=ctk.CTkFont(size=16, weight="bold"),  # Increased from 14
            text_color=CyberpunkTheme.ACCENT_PINK,
        )
        settings_header.pack(fill="x", padx=8, pady=(8, 4))

        # Volume reduction slider
        volume_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        volume_frame.pack(fill="x", padx=8, pady=4)

        volume_label = ctk.CTkLabel(
            volume_frame,
            text="🔊 Volume Reduction:",
            font=ctk.CTkFont(size=13, weight="bold"),  # Increased from 12
            text_color=CyberpunkTheme.TEXT_PRIMARY,
        )
        volume_label.pack(anchor="w")

        self.volume_slider = ctk.CTkSlider(volume_frame, from_=0.0, to=1.0, number_of_steps=20, command=self._on_volume_change)
        self.volume_slider.pack(fill="x", pady=(4, 0))
        self.volume_slider.set(0.5)  # Default 50% reduction

        # Language dropdown
        language_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        language_frame.pack(fill="x", padx=8, pady=4)

        language_label = ctk.CTkLabel(
            language_frame,
            text="🌍 Language:",
            font=ctk.CTkFont(size=13, weight="bold"),  # Increased from 12
            text_color=CyberpunkTheme.TEXT_PRIMARY,
        )
        language_label.pack(anchor="w")

        self.language_dropdown = ctk.CTkOptionMenu(
            language_frame,
            values=["de", "en", "fr", "es", "it", "pt", "ru", "ja", "ko", "zh"],
            command=self._on_language_change,
        )
        self.language_dropdown.pack(fill="x", pady=(4, 0))
        self.language_dropdown.set("de")  # Default to German

        # Model selector
        model_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        model_frame.pack(fill="x", padx=8, pady=4)

        model_label = ctk.CTkLabel(
            model_frame,
            text="🤖 Model:",
            font=ctk.CTkFont(size=13, weight="bold"),  # Increased from 12
            text_color=CyberpunkTheme.TEXT_PRIMARY,
        )
        model_label.pack(anchor="w")

        self.model_dropdown = ctk.CTkOptionMenu(
            model_frame, values=["tiny", "base", "small", "medium", "large"], command=self._on_model_change
        )
        self.model_dropdown.pack(fill="x", pady=(4, 0))
        self.model_dropdown.set("base")  # Default to base model

        # Save settings button
        save_button = ctk.CTkButton(
            settings_frame,
            text="💾 Save Settings",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=CyberpunkTheme.ACCENT_CYAN,
            hover_color="#00CCCC",
            command=self._save_settings,
        )
        save_button.pack(fill="x", padx=8, pady=(8, 8))

    def _create_status_column(self, parent: ctk.CTkFrame) -> None:
        """Create the status column with recording status and transcription result."""
        # Status frame
        status_frame = ctk.CTkFrame(parent, fg_color=CyberpunkTheme.BG_SURFACE, corner_radius=6, border_width=1)
        status_frame.grid(row=0, column=1, padx=(2, 4), pady=4, sticky="nsew")

        # Status header
        status_header = ctk.CTkLabel(
            status_frame,
            text="📊 Current Status",
            font=ctk.CTkFont(size=16, weight="bold"),  # Increased from 14
            text_color=CyberpunkTheme.ACCENT_CYAN,
        )
        status_header.pack(fill="x", padx=8, pady=(8, 4))

        # Recording status (no redundant label needed)
        recording_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        recording_frame.pack(fill="x", padx=8, pady=4)

        self.recording_status_label = ctk.CTkLabel(
            recording_frame,
            text="● IDLE",
            font=ctk.CTkFont(size=14, weight="bold"),  # Larger, more prominent
            text_color=CyberpunkTheme.TEXT_SECONDARY,
        )
        self.recording_status_label.pack(anchor="w")

        # Duration display
        self.duration_label = ctk.CTkLabel(
            recording_frame, text="Duration: 0.0s", font=ctk.CTkFont(size=11), text_color=CyberpunkTheme.TEXT_SECONDARY
        )
        self.duration_label.pack(anchor="w", pady=(2, 0))

        # Latest transcription result
        transcription_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        transcription_frame.pack(fill="both", expand=True, padx=8, pady=4)

        transcription_label = ctk.CTkLabel(
            transcription_frame,
            text="📝 Latest Transcription:",
            font=ctk.CTkFont(size=13, weight="bold"),  # Increased from 12
            text_color=CyberpunkTheme.TEXT_PRIMARY,
        )
        transcription_label.pack(anchor="w")

        # Transcription text with edit/copy controls
        self.transcription_text = ctk.CTkTextbox(
            transcription_frame,
            height=100,
            font=ctk.CTkFont(size=11),
            fg_color=CyberpunkTheme.BG_DARK,
            text_color=CyberpunkTheme.TEXT_PRIMARY,
            wrap="word",
        )
        self.transcription_text.pack(fill="both", expand=True, pady=(4, 0))

        # Edit/Copy buttons will be created in _create_status_column

    def _on_volume_change(self, value: float) -> None:
        """Handle volume slider change."""
        try:
            if self.app_instance and hasattr(self.app_instance, "config"):
                self.app_instance.config.audio.volume_reduction_factor = value
                print(f"Volume reduction set to: {value:.1%}")
        except Exception as e:
            print(f"Error setting volume: {str(e)}")

    def _on_language_change(self, language: str) -> None:
        """Handle language dropdown change."""
        try:
            if self.app_instance and hasattr(self.app_instance, "config"):
                self.app_instance.config.transcription.language = language
                print(f"Language set to: {language}")
        except Exception as e:
            print(f"Error setting language: {str(e)}")

    def _on_model_change(self, model: str) -> None:
        """Handle model dropdown change."""
        try:
            if self.app_instance and hasattr(self.app_instance, "config"):
                self.app_instance.config.transcription.model = model
                print(f"Model set to: {model}")
        except Exception as e:
            print(f"Error setting model: {str(e)}")

    def _save_settings(self) -> None:
        """Save all settings to configuration."""
        try:
            if self.app_instance and hasattr(self.app_instance, "config"):
                self.app_instance.config.save()
                print("Settings saved successfully")
        except Exception as e:
            print(f"Error saving settings: {str(e)}")

    def _edit_transcription(self) -> None:
        """Enable editing of transcription text."""
        try:
            self.transcription_text.configure(state="normal")
            print("Transcription editing enabled")
        except Exception as e:
            print(f"Error enabling edit: {str(e)}")

    def _copy_transcription(self) -> None:
        """Copy transcription text to clipboard."""
        try:
            text = self.transcription_text.get("1.0", "end-1c")
            self.clipboard_clear()
            self.clipboard_append(text)
            print("Transcription copied to clipboard")
        except Exception as e:
            print(f"Error copying transcription: {str(e)}")

    def _create_layout(self) -> None:
        """Create the status tab layout."""
        # Main container with enhanced styling
        main_frame = ctk.CTkFrame(
            self,
            fg_color=CyberpunkTheme.BG_DARK,
            corner_radius=CyberpunkTheme.CORNER_RADIUS,
            border_width=CyberpunkTheme.BORDER_WIDTH,
            border_color=CyberpunkTheme.BORDER_GLOW,
        )
        main_frame.pack(fill="both", expand=True, padx=8, pady=8)

        # Two-column layout (no header needed - tab name is sufficient)
        content_frame = ctk.CTkFrame(main_frame, fg_color=CyberpunkTheme.BG_DARK, corner_radius=6, border_width=1)
        content_frame.pack(fill="both", expand=True, padx=4, pady=4)

        # Configure grid weights - Action gets more space
        content_frame.grid_columnconfigure(0, weight=1)  # Settings column (smaller)
        content_frame.grid_columnconfigure(1, weight=2)  # Status/Action column (larger)
        content_frame.grid_rowconfigure(0, weight=1)  # Use full height

        # Settings column (left)
        self._create_settings_column(content_frame)

        # Status column (right)
        self._create_status_column(content_frame)

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
                self._safe_update_status()
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
            # Ensure we're on the main thread
            if not self.winfo_exists():
                return

            # Update recording status
            if self.is_recording:
                self.recording_status_label.configure(text="● RECORDING", text_color=CyberpunkTheme.STATUS_ERROR)
                self.duration_label.configure(text=f"Duration: {self.current_audio_duration:.1f}s")
            else:
                self.recording_status_label.configure(text="● IDLE", text_color=CyberpunkTheme.TEXT_SECONDARY)
                self.duration_label.configure(text="Duration: 0.0s")

            # Update transcription status
            if self.is_transcribing:
                self.recording_status_label.configure(text="● TRANSCRIBING", text_color=CyberpunkTheme.STATUS_WARNING)

            # Update last transcription result
            if self.last_transcription:
                self.transcription_text.delete("1.0", "end")
                self.transcription_text.insert("1.0", self.last_transcription)

        except Exception as e:
            print(f"Error updating status: {str(e)}")

    def cleanup(self) -> None:
        """Cleanup resources and stop timers."""
        try:
            self.is_closing = True

            # Stop duration timer
            if hasattr(self, "duration_timer") and self.duration_timer:
                self.after_cancel(self.duration_timer)
                self.duration_timer = None

            # Unsubscribe from events
            if hasattr(self, "event_bus") and self.event_bus:
                self.event_bus.unsubscribe("recording_started", self._on_recording_started)
                self.event_bus.unsubscribe("recording_stopped", self._on_recording_stopped)
                self.event_bus.unsubscribe("transcription_started", self._on_transcription_started)
                self.event_bus.unsubscribe("transcription_completed", self._on_transcription_completed)

            print("🧹 SettingsTab cleaned up")

        except Exception as e:
            print(f"❌ Error cleaning up SettingsTab: {e}")

    def _safe_update_status(self) -> None:
        """Safely update status from any thread."""
        try:
            if self.is_closing or not self.winfo_exists():
                return
            self.after(0, self._update_status)
        except Exception as e:
            print(f"Error scheduling status update: {str(e)}")

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
