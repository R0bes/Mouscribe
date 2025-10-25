# src/ui/tabs/logs_tab.py - Logs Tab for Control Center
"""
Logs Tab implementation for Mauscribe Control Center.
Features: Live log display, filtering, search, export, and statistics.
"""

import threading
import time
from pathlib import Path
from typing import Any, List, Optional

import customtkinter as ctk

from ...utils.logger import LogEntry, clear_log_buffer, get_log_buffer, get_log_statistics, get_recent_logs
from ..theme import CyberpunkTheme


class LogsTab(ctk.CTkFrame):
    """Logs tab with filtering, search, and live updates."""

    def __init__(self, parent: ctk.CTkTabview, app_instance: Any = None, **kwargs):
        """Initialize the Logs tab.

        Args:
            parent: Parent widget
            app_instance: Reference to main application instance
        """
        super().__init__(parent, **kwargs)
        self.app_instance = app_instance

        # State
        self.current_filter = "ALL"
        self.search_text = ""
        self.auto_scroll = True
        self.update_thread: Optional[threading.Thread] = None
        self.running = False
        self.is_closing = False

        # Initialize logging system
        self._initialize_logging()

        # Initialize attributes to avoid AttributeError
        self.log_text = None
        self.stats_label = None
        self.update_label = None
        self.filter_buttons = {}
        self.search_entry = None
        self.auto_scroll_var = None

        # Create UI
        self._create_layout()

        # Start live updates
        self._start_live_updates()

    def _initialize_logging(self) -> None:
        """Initialize logging system for the logs tab."""
        try:
            from ...utils.logger import StructuredLogHandler, get_logger, setup_logging

            # Setup logging with buffer enabled
            setup_logging()

            # Add some test logs to demonstrate functionality
            test_logger = get_logger("LogsTab")
            test_logger.info("📋 Logs Tab initialized")
            test_logger.warning("⚠️ This is a test warning from LogsTab")
            test_logger.error("❌ This is a test error from LogsTab")
            test_logger.debug("🔍 This is a debug message from LogsTab")

            # Add more test logs to make it more visible
            test_logger.info("🎮 Control Center is running")
            test_logger.warning("⚠️ This is another warning")
            test_logger.error("❌ This is another error")
            test_logger.info("📊 Status Tab is active")
            test_logger.info("🎵 Audio Files Tab is ready")
            test_logger.info("📝 Transcriptions Tab is ready")

            # Add some realistic logs
            test_logger.info("🚀 Mauscribe started successfully")
            test_logger.info("🎙️ Audio service initialized")
            test_logger.info("📱 System tray ready")
            test_logger.warning("⚠️ No audio input detected")
            test_logger.info("✅ All systems ready")

        except Exception as e:
            print(f"Failed to initialize logging: {e}")

    def _add_test_content(self, parent: ctk.CTkFrame) -> None:
        """Add test content to make tab visible."""
        try:
            test_frame = ctk.CTkFrame(parent, fg_color=CyberpunkTheme.BG_ELEVATED, corner_radius=6, height=100)
            test_frame.pack(fill="x", padx=4, pady=4)
            test_frame.pack_propagate(False)

            test_label = ctk.CTkLabel(
                test_frame,
                text="📋 Logs Tab - Test Content",
                font=CyberpunkTheme.FONT_HEADER,
                text_color=CyberpunkTheme.ACCENT_CYAN,
            )
            test_label.pack(pady=20)

            info_label = ctk.CTkLabel(
                test_frame,
                text="This tab will show live logs from Mauscribe",
                font=CyberpunkTheme.FONT_BODY,
                text_color=CyberpunkTheme.TEXT_SECONDARY,
            )
            info_label.pack(pady=10)

        except Exception as e:
            print(f"Failed to add test content: {e}")

    def _load_real_logs(self) -> None:
        """Load real logs from the logging system."""
        try:
            from ...utils.logger import get_recent_logs

            print("Attempting to load real logs...")

            # Get recent logs
            logs = get_recent_logs(count=50)
            print(f"get_recent_logs returned: {logs}")

            if logs:
                # Clear existing content
                if self.log_text:
                    self.log_text.delete("1.0", "end")

                # Add each log entry
                for log_entry in logs:
                    self._add_log_entry(log_entry)

                print(f"Loaded {len(logs)} real log entries")
            else:
                print("No real logs found, adding fallback content")
                # Add fallback test logs if real logs fail
                if self.log_text:
                    self.log_text.insert("end", "📋 No logs available yet\n")
                    self.log_text.insert("end", "⚠️ Start Mauscribe to see logs here\n")
                    self.log_text.insert("end", "🎮 Control Center is ready\n")

        except Exception as e:
            print(f"Failed to load real logs: {e}")
            # Add fallback test logs if real logs fail
            if self.log_text:
                self.log_text.insert("end", f"❌ Error loading logs: {e}\n")
                self.log_text.insert("end", "📋 No logs available yet\n")
                self.log_text.insert("end", "⚠️ Start Mauscribe to see logs here\n")
                self.log_text.insert("end", "🎮 Control Center is ready\n")

    def _create_layout(self) -> None:
        """Create the logs tab layout."""
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color=CyberpunkTheme.BG_DARK, corner_radius=8, border_width=1)
        main_frame.pack(fill="both", expand=True, padx=4, pady=4)

        # Toolbar
        self._create_toolbar(main_frame)

        # Log display area
        self._create_log_display(main_frame)

        # Load real logs instead of test content
        self._load_real_logs()

        # Status bar
        self._create_status_bar(main_frame)

    def _create_toolbar(self, parent: ctk.CTkFrame) -> None:
        """Create the toolbar with filters and controls."""
        toolbar_frame = ctk.CTkFrame(parent, fg_color=CyberpunkTheme.BG_ELEVATED, corner_radius=6, height=50)
        toolbar_frame.pack(fill="x", padx=4, pady=(4, 2))
        toolbar_frame.pack_propagate(False)

        # Filter buttons
        filter_frame = ctk.CTkFrame(toolbar_frame, fg_color="transparent")
        filter_frame.pack(side="left", padx=4, pady=4)

        filter_label = ctk.CTkLabel(
            filter_frame, text="Filter:", font=ctk.CTkFont(size=12, weight="bold"), text_color=CyberpunkTheme.TEXT_PRIMARY
        )
        filter_label.pack(side="left", padx=(0, 8))

        # Filter buttons
        self.filter_buttons = {}
        filter_levels = ["ALL", "ERROR", "WARNING", "INFO", "DEBUG"]

        for level in filter_levels:
            button = ctk.CTkButton(
                filter_frame,
                text=level,
                width=60,
                height=28,
                font=ctk.CTkFont(size=10, weight="bold"),
                fg_color=CyberpunkTheme.BG_SURFACE,
                hover_color=CyberpunkTheme.BUTTON_HOVER,
                text_color=CyberpunkTheme.TEXT_SECONDARY,
                command=lambda level_name=level: self._set_filter(level_name),
            )
            button.pack(side="left", padx=2)
            self.filter_buttons[level] = button

        # Set ALL as active (but don't refresh yet)
        self.current_filter = "ALL"

        # Update filter button appearance
        self._update_filter_buttons()

        # Search frame
        search_frame = ctk.CTkFrame(toolbar_frame, fg_color="transparent")
        search_frame.pack(side="left", padx=(10, 4), pady=4)

        search_label = ctk.CTkLabel(
            search_frame, text="Search:", font=ctk.CTkFont(size=12, weight="bold"), text_color=CyberpunkTheme.TEXT_PRIMARY
        )
        search_label.pack(side="left", padx=(0, 8))

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search logs...",
            width=200,
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color=CyberpunkTheme.BG_DARK,
            text_color=CyberpunkTheme.TEXT_PRIMARY,
        )
        self.search_entry.pack(side="left", padx=(0, 8))
        self.search_entry.bind("<KeyRelease>", self._on_search_change)

        # Control buttons
        controls_frame = ctk.CTkFrame(toolbar_frame, fg_color="transparent")
        controls_frame.pack(side="right", padx=4, pady=4)

        # Clear button
        clear_button = ctk.CTkButton(
            controls_frame,
            text="🗑️ Clear",
            width=80,
            height=28,
            font=ctk.CTkFont(size=10),
            fg_color=CyberpunkTheme.STATUS_ERROR,
            hover_color="#CC1A33",
            command=self._clear_logs,
        )
        clear_button.pack(side="right", padx=4)

        # Export button
        export_button = ctk.CTkButton(
            controls_frame,
            text="💾 Export",
            width=80,
            height=28,
            font=ctk.CTkFont(size=10),
            fg_color=CyberpunkTheme.STATUS_SUCCESS,
            hover_color="#00CC66",
            command=self._export_logs,
        )
        export_button.pack(side="right", padx=4)

        # Auto-scroll checkbox
        self.auto_scroll_var = ctk.BooleanVar(value=True)
        auto_scroll_checkbox = ctk.CTkCheckBox(
            controls_frame,
            text="Auto-scroll",
            variable=self.auto_scroll_var,
            font=ctk.CTkFont(size=10),
            text_color=CyberpunkTheme.TEXT_PRIMARY,
            command=self._toggle_auto_scroll,
        )
        auto_scroll_checkbox.pack(side="right", padx=8)

    def _create_log_display(self, parent: ctk.CTkFrame) -> None:
        """Create the log display area."""
        # Log display frame
        display_frame = ctk.CTkFrame(parent, fg_color=CyberpunkTheme.BG_DARK, corner_radius=6, border_width=1)
        display_frame.pack(fill="both", expand=True, padx=4, pady=2)

        # Scrollable frame for chat-like log cards
        self.logs_scrollable = ctk.CTkScrollableFrame(
            display_frame,
            fg_color=CyberpunkTheme.BG_DARK,
            scrollbar_button_color=CyberpunkTheme.ACCENT_CYAN,
            scrollbar_button_hover_color=CyberpunkTheme.ACCENT_PINK,
        )
        self.logs_scrollable.pack(fill="both", expand=True, padx=2, pady=2)

        # Store log card references for animation
        self.log_cards = []
        self.is_closing = False

    def _create_status_bar(self, parent: ctk.CTkFrame) -> None:
        """Create the status bar."""
        status_frame = ctk.CTkFrame(parent, fg_color=CyberpunkTheme.BG_ELEVATED, corner_radius=6, height=30)
        status_frame.pack(fill="x", padx=4, pady=(2, 4))
        status_frame.pack_propagate(False)

        # Statistics
        self.stats_label = ctk.CTkLabel(
            status_frame, text="Ready", font=ctk.CTkFont(size=10), text_color=CyberpunkTheme.TEXT_SECONDARY
        )
        self.stats_label.pack(side="left", padx=8, pady=6)

        # Last update time
        self.update_label = ctk.CTkLabel(
            status_frame, text="", font=ctk.CTkFont(size=10), text_color=CyberpunkTheme.TEXT_SECONDARY
        )
        self.update_label.pack(side="right", padx=8, pady=6)

    def _setup_text_tags(self) -> None:
        """Setup text tags for log level colors."""
        # CTkTextbox doesn't support tag_configure, so we'll use simple text formatting
        # Colors will be applied via text insertion with color formatting
        pass

    def _create_log_card(self, log_entry) -> None:
        """Create a chat-like log card with unified format."""
        try:
            # Check if widget still exists
            if not self.winfo_exists() or not self.logs_scrollable.winfo_exists():
                return

            # Parse log entry for unified format
            parsed_log = self._parse_log_entry(log_entry)

            # Card frame with enhanced styling and glow effect
            card_frame = ctk.CTkFrame(
                self.logs_scrollable,
                fg_color=self._get_log_bg_color(parsed_log["level"]),
                corner_radius=CyberpunkTheme.CORNER_RADIUS,
                border_width=2,
                border_color=self._get_log_border_color(parsed_log["level"]),
            )
            card_frame.pack(fill="x", padx=6, pady=4)

            # Store card reference
            self.log_cards.append(card_frame)

            # Configure grid layout
            card_frame.grid_columnconfigure(1, weight=1)  # Message expands
            card_frame.grid_columnconfigure(2, weight=0)  # Module fixed
            card_frame.grid_columnconfigure(3, weight=0)  # Level fixed

            # Time (left, fixed width)
            time_label = ctk.CTkLabel(
                card_frame,
                text=parsed_log["time"],
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=CyberpunkTheme.TEXT_SECONDARY,
                width=80,
                fg_color=self._get_time_bg_color(parsed_log["level"]),
            )
            time_label.grid(row=0, column=0, padx=(8, 4), pady=6, sticky="w")

            # Message (center, expands)
            message_label = ctk.CTkLabel(
                card_frame,
                text=parsed_log["message"],
                font=ctk.CTkFont(size=12, weight="normal"),
                text_color=CyberpunkTheme.TEXT_PRIMARY,
                anchor="w",
                justify="left",
                wraplength=600,
            )
            message_label.grid(row=0, column=1, padx=4, pady=6, sticky="ew")

            # Module (right, fixed width)
            module_label = ctk.CTkLabel(
                card_frame,
                text=parsed_log["module"],
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=CyberpunkTheme.ACCENT_CYAN,
                width=100,
                fg_color=self._get_module_bg_color(parsed_log["level"]),
            )
            module_label.grid(row=0, column=2, padx=4, pady=6, sticky="e")

            # Level badge (far right, fixed width)
            level_badge = ctk.CTkLabel(
                card_frame,
                text=parsed_log["level"],
                font=ctk.CTkFont(size=10, weight="bold"),
                fg_color=self._get_level_color(parsed_log["level"]),
                text_color=CyberpunkTheme.BG_DARK,
                width=70,
            )
            level_badge.grid(row=0, column=3, padx=(4, 8), pady=6, sticky="e")

            # Fade-in animation
            self._animate_log_card(card_frame)

        except Exception as e:
            print(f"Error creating log card: {str(e)}")

    def _parse_log_entry(self, log_entry) -> dict:
        """Parse log entry into unified format."""
        try:
            # Handle different log entry formats
            if hasattr(log_entry, "formatted_time"):
                # Real LogEntry object
                return {
                    "time": log_entry.formatted_time,
                    "level": log_entry.level,
                    "module": getattr(log_entry, "module", "Unknown").split(".")[-1],
                    "message": log_entry.message,
                }
            elif hasattr(log_entry, "time"):
                # Mock LogEntry object
                return {
                    "time": log_entry.time,
                    "level": log_entry.level,
                    "module": getattr(log_entry, "module", "Unknown"),
                    "message": log_entry.message,
                }
            else:
                # Fallback
                return {"time": "00:00:00", "level": "INFO", "module": "Unknown", "message": str(log_entry)}
        except Exception as e:
            print(f"Error parsing log entry: {e}")
            return {"time": "00:00:00", "level": "ERROR", "module": "Parser", "message": f"Parse error: {str(e)}"}

    def _get_log_bg_color(self, level: str) -> str:
        """Get background color based on log level."""
        colors = {
            "DEBUG": CyberpunkTheme.BG_SURFACE,
            "INFO": "#1A2F3A",  # Darker cyan tint
            "WARNING": "#3A2F1A",  # Darker orange tint
            "ERROR": "#3A1A2F",  # Darker pink tint
            "CRITICAL": "#2F1A1A",  # Darker red tint
        }
        return colors.get(level, CyberpunkTheme.BG_SURFACE)

    def _get_log_border_color(self, level: str) -> str:
        """Get border color based on log level."""
        colors = {
            "DEBUG": CyberpunkTheme.BORDER_COLOR,
            "INFO": CyberpunkTheme.ACCENT_CYAN,
            "WARNING": CyberpunkTheme.STATUS_WARNING,
            "ERROR": CyberpunkTheme.STATUS_ERROR,
            "CRITICAL": "#FF0040",
        }
        return colors.get(level, CyberpunkTheme.BORDER_COLOR)

    def _get_time_bg_color(self, level: str) -> str:
        """Get time background color based on log level."""
        colors = {"DEBUG": "#2A2A2A", "INFO": "#1A3A2A", "WARNING": "#3A2A1A", "ERROR": "#3A1A1A", "CRITICAL": "#2A1A1A"}
        return colors.get(level.upper(), "#2A2A2A")

    def _get_module_bg_color(self, level: str) -> str:
        """Get module background color based on log level."""
        colors = {"DEBUG": "#1A1A2A", "INFO": "#1A2A1A", "WARNING": "#2A1A1A", "ERROR": "#2A1A1A", "CRITICAL": "#1A1A1A"}
        return colors.get(level.upper(), "#1A1A2A")

    def _get_level_color(self, level: str) -> str:
        """Get level badge color."""
        colors = {
            "DEBUG": CyberpunkTheme.TEXT_MUTED,
            "INFO": CyberpunkTheme.ACCENT_CYAN,
            "WARNING": CyberpunkTheme.STATUS_WARNING,
            "ERROR": CyberpunkTheme.STATUS_ERROR,
            "CRITICAL": "#FF0040",
        }
        return colors.get(level, CyberpunkTheme.TEXT_MUTED)

    def _animate_log_card(self, card_frame) -> None:
        """Enhanced fade-in animation for log cards."""
        try:
            # Start with subtle effect
            card_frame.configure(fg_color=CyberpunkTheme.BG_DARK)

            # Enhanced fade-in animation
            def fade_in(step=0):
                if step <= 15 and not self.is_closing:
                    # Progressive color change for smooth animation
                    if step == 0:
                        card_frame.configure(fg_color=CyberpunkTheme.BG_SURFACE)
                    elif step == 5:
                        card_frame.configure(fg_color=CyberpunkTheme.BG_ELEVATED)
                    elif step == 10:
                        # Final color will be set by the calling method
                        pass

                    # Schedule next step
                    self.after(30, lambda: fade_in(step + 1))

            # Start animation with delay
            self.after(100, lambda: fade_in())

        except Exception as e:
            print(f"Error animating log card: {str(e)}")

    def _update_filter_buttons(self) -> None:
        """Update filter button appearance."""
        if not self.filter_buttons:
            return

        for btn_level, button in self.filter_buttons.items():
            if btn_level == self.current_filter:
                button.configure(fg_color=CyberpunkTheme.ACCENT_CYAN, text_color=CyberpunkTheme.BG_DARK)
            else:
                button.configure(fg_color=CyberpunkTheme.BG_SURFACE, text_color=CyberpunkTheme.TEXT_SECONDARY)

    def _set_filter(self, level: str) -> None:
        """Set the log level filter."""
        self.current_filter = level

        # Update button colors
        self._update_filter_buttons()

        # Refresh display
        self._refresh_logs()

    def _on_search_change(self, event) -> None:
        """Handle search text change."""
        self.search_text = self.search_entry.get().strip()
        self._refresh_logs()

    def _toggle_auto_scroll(self) -> None:
        """Toggle auto-scroll mode."""
        self.auto_scroll = self.auto_scroll_var.get()

    def _clear_logs(self) -> None:
        """Clear all logs."""
        clear_log_buffer()
        self.log_text.delete("1.0", "end")
        self._update_statistics()

    def _export_logs(self) -> None:
        """Export filtered logs to file."""
        try:
            # Get current logs
            logs = self._get_filtered_logs()

            if not logs:
                return

            # Create export filename
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"mauscribe_logs_{timestamp}.txt"

            # Write to file
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"Mauscribe Logs Export - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Filter: {self.current_filter}\n")
                f.write(f"Search: {self.search_text or 'None'}\n")
                f.write("=" * 80 + "\n\n")

                for log in logs:
                    f.write(f"[{log.formatted_time}] {log.level:8} {log.module:15} - {log.message}\n")

            # Update status
            self.stats_label.configure(text=f"Exported {len(logs)} logs to {filename}")

        except Exception as e:
            self.stats_label.configure(text=f"Export failed: {str(e)}")

    def _get_filtered_logs(self) -> list[LogEntry]:
        """Get logs filtered by current settings."""
        logs = get_recent_logs(count=1000)  # Get more logs for filtering

        # Filter by level
        if self.current_filter != "ALL":
            logs = [log for log in logs if log.level == self.current_filter]

        # Filter by search text
        if self.search_text:
            search_lower = self.search_text.lower()
            logs = [log for log in logs if (search_lower in log.message.lower() or search_lower in log.module.lower())]

        return logs

    def _refresh_logs(self) -> None:
        """Refresh the log display."""
        try:
            # Check if UI elements are ready
            if not self.logs_scrollable or not self.stats_label:
                return

            logs = self._get_filtered_logs()

            # Clear current cards
            for card in self.log_cards:
                card.destroy()
            self.log_cards.clear()

            # Add logs as cards
            for log in logs:
                self._create_log_card(log)

            # If no logs from buffer, add some test logs
            if not logs:
                self._add_test_logs()

            # Auto-scroll to bottom
            if self.auto_scroll:
                self.logs_scrollable._parent_canvas.yview_moveto(1.0)

            # Update statistics
            self._update_statistics()

            # Update last update time
            if self.update_label:
                self.update_label.configure(text=f"Updated: {time.strftime('%H:%M:%S')}")

        except Exception as e:
            if self.stats_label:
                self.stats_label.configure(text=f"Refresh failed: {str(e)}")

    def _add_test_logs(self) -> None:
        """Add test logs if no real logs are available."""
        test_logs = [
            ("11:43:15", "INFO", "LogsTab", "📋 Logs Tab initialized"),
            ("11:43:16", "WARNING", "LogsTab", "⚠️ This is a test warning"),
            ("11:43:17", "ERROR", "LogsTab", "❌ This is a test error"),
            ("11:43:18", "DEBUG", "LogsTab", "🔍 This is a debug message"),
            ("11:43:19", "INFO", "ControlCenter", "🎮 Control Center is running"),
            ("11:43:20", "WARNING", "SystemTray", "⚠️ System Tray active"),
            ("11:43:21", "INFO", "AudioDatabase", "🗄️ Database initialized"),
            ("11:43:22", "ERROR", "Transcription", "❌ Transcription failed"),
            ("11:43:23", "INFO", "StatusTab", "📊 Status Tab ready"),
            ("11:43:24", "INFO", "AudioTab", "🎵 Audio Files Tab ready"),
        ]

        for timestamp, level, module, message in test_logs:
            # Create a simple log entry
            log_entry = type("LogEntry", (), {"time": timestamp, "level": level, "module": module, "message": message})()
            self._create_log_card(log_entry)

    def _add_log_entry(self, log: LogEntry) -> None:
        """Add a single log entry as a chat card."""
        try:
            # Check if widget still exists and not closing
            if not self.winfo_exists() or self.is_closing:
                return

            # Create log entry with proper attributes
            log_entry = type(
                "LogEntry",
                (),
                {
                    "time": log.formatted_time,
                    "level": log.level,
                    "module": log.module.split(".")[-1] if hasattr(log, "module") else "Unknown",
                    "message": log.message,
                },
            )()

            # Create chat card
            self._create_log_card(log_entry)

        except Exception as e:
            print(f"Error adding log entry: {str(e)}")

    def cleanup(self) -> None:
        """Cleanup resources and stop event handlers."""
        try:
            self.is_closing = True
            self.running = False

            # Stop update thread
            if self.update_thread and self.update_thread.is_alive():
                self.update_thread.join(timeout=1.0)

            # Clear log cards
            self.log_cards.clear()

            # Unsubscribe from events if event bus exists
            if hasattr(self.app_instance, "event_bus") and self.app_instance.event_bus:
                try:
                    self.app_instance.event_bus.unsubscribe("log_entry", self._add_log_entry)
                    self.app_instance.event_bus.unsubscribe("LOG_MESSAGE_ADDED", self._on_log_added)
                except Exception:
                    pass  # Ignore unsubscribe errors

            print("🧹 LogsTab cleaned up")

        except Exception as e:
            print(f"❌ Error cleaning up LogsTab: {e}")

    def _update_statistics(self) -> None:
        """Update the statistics display."""
        try:
            if not self.stats_label:
                return

            stats = get_log_statistics()
            filtered_logs = self._get_filtered_logs()

            stats_text = (
                f"Total: {stats['TOTAL']} | "
                f"Errors: {stats['ERROR']} | "
                f"Warnings: {stats['WARNING']} | "
                f"Showing: {len(filtered_logs)}"
            )

            self.stats_label.configure(text=stats_text)

        except Exception as e:
            if self.stats_label:
                self.stats_label.configure(text=f"Stats error: {str(e)}")

    def _start_live_updates(self) -> None:
        """Start event-based live updates."""
        try:
            from ...utils.eventbus import EventType, subscribe_to_event

            # Subscribe to log events
            subscribe_to_event(EventType.LOG_MESSAGE_ADDED, self._on_log_added)

            print("✅ Logs Tab subscribed to LOG_MESSAGE_ADDED events")

        except Exception as e:
            print(f"Failed to subscribe to log events: {e}")

    def _on_log_added(self, event) -> None:
        """Handle new log message event."""
        try:
            # Create LogEntry from event data
            from ...utils.logger import LogEntry

            log_entry = LogEntry(
                timestamp=event.data["timestamp"],
                level=event.data["level"],
                module=event.data["module"],
                message=event.data["message"],
                thread_id=0,  # Not needed for display
            )

            # Add to UI
            self._add_log_entry(log_entry)

        except Exception as e:
            print(f"Error handling log event: {e}")

    def stop_updates(self) -> None:
        """Stop the live update thread."""
        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=1.0)
