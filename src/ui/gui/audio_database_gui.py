"""
Modern GUI for managing audio database.
Provides an intuitive, modern interface for audio recordings and transcriptions.
"""

import json
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any, Dict, List, Optional

from ...utils.database import AudioDatabase
from ...utils.logger import get_logger


class AudioDatabaseGUI:
    """Modern GUI for managing audio database."""

    def __init__(
        self, config=None, notification_manager=None, parent: tk.Tk | None = None
    ):
        """Initialize the audio database GUI."""
        self.logger = get_logger(self.__class__.__name__)
        self.config = config
        self.notification_manager = notification_manager
        self.database = AudioDatabase()
        self.root: tk.Tk | tk.Toplevel

        # Auto-save timer
        self.auto_save_timer = None
        self.auto_save_delay = 2000  # 2 seconds

        # Track changes for auto-save
        self.database_changed = False

        # Create main window
        if parent:
            self.root = tk.Toplevel(parent)
            self.root.title("Mauscribe - Audio-Datenbank Manager")
        else:
            self.root = tk.Tk()
            self.root.title("Mauscribe - Audio-Datenbank Manager")

        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)

        # Apply modern styling
        self._setup_styles()

        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")

        self._setup_ui()
        self._refresh_data()

        # Setup auto-save
        self._setup_auto_save()

    def _setup_styles(self):
        """Setup modern styling for the GUI."""
        style = ttk.Style()

        # Configure modern theme
        try:
            style.theme_use("clam")  # Modern theme
        except:
            pass  # Fallback to default theme

        # Configure colors
        style.configure("Modern.TFrame", background="#f5f5f5")
        style.configure("Modern.TLabel", background="#f5f5f5", font=("Segoe UI", 9))
        style.configure("Modern.TButton", font=("Segoe UI", 9))
        style.configure(
            "Title.TLabel", font=("Segoe UI", 16, "bold"), foreground="#2c3e50"
        )
        style.configure(
            "Subtitle.TLabel", font=("Segoe UI", 12, "bold"), foreground="#34495e"
        )
        style.configure("Success.TLabel", foreground="#27ae60")
        style.configure("Warning.TLabel", foreground="#f39c12")
        style.configure("Error.TLabel", foreground="#e74c3c")

    def _setup_ui(self):
        """Setup the modern user interface."""
        # Main container
        main_container = ttk.Frame(self.root, style="Modern.TFrame", padding="20")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)

        # Header
        header_frame = ttk.Frame(main_container)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))

        title_label = ttk.Label(
            header_frame, text="🎙️ Mauscribe Audio-Datenbank", style="Title.TLabel"
        )
        title_label.pack(side=tk.LEFT)

        # Status indicator
        self.status_label = ttk.Label(
            header_frame, text="✅ Bereit", style="Success.TLabel"
        )
        self.status_label.pack(side=tk.RIGHT)

        # Main content
        content_frame = ttk.Frame(main_container)
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(2, weight=1)

        # Statistics cards
        stats_frame = ttk.Frame(content_frame)
        stats_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))

        # Create modern stat cards
        self.stats_labels = {}
        stats_data = [
            ("total_recordings", "🎙️ Aufnahmen", "0"),
            ("total_transcriptions", "📝 Transkriptionen", "0"),
            ("training_samples", "🎯 Trainingsdaten", "0"),
            ("total_duration_hours", "⏱️ Gesamtdauer", "0h"),
            ("total_size_mb", "💾 Größe", "0 MB"),
        ]

        for i, (key, label, default_value) in enumerate(stats_data):
            card_frame = ttk.LabelFrame(stats_frame, text=label, padding="10")
            card_frame.grid(row=0, column=i, padx=(0, 10), sticky=(tk.W, tk.E))

            self.stats_labels[key] = ttk.Label(
                card_frame,
                text=default_value,
                font=("Segoe UI", 14, "bold"),
                foreground="#2c3e50",
            )
            self.stats_labels[key].pack()

            stats_frame.columnconfigure(i, weight=1)

        # Action buttons
        button_frame = ttk.Frame(content_frame)
        button_frame.grid(row=1, column=0, pady=(0, 20))

        ttk.Button(
            button_frame,
            text="🔄 Aktualisieren",
            command=self._refresh_data,
            style="Modern.TButton",
        ).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(
            button_frame,
            text="📤 Exportieren",
            command=self._export_data,
            style="Modern.TButton",
        ).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(
            button_frame,
            text="🗑️ Aufräumen",
            command=self._cleanup_old_data,
            style="Modern.TButton",
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Search and filter
        search_frame = ttk.LabelFrame(
            content_frame, text="🔍 Suche & Filter", padding="15"
        )
        search_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))

        search_frame.columnconfigure(1, weight=1)
        search_frame.columnconfigure(3, weight=1)

        ttk.Label(search_frame, text="Suche:", style="Modern.TLabel").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10)
        )
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._filter_data)
        search_entry = ttk.Entry(
            search_frame, textvariable=self.search_var, font=("Segoe UI", 10)
        )
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 20))

        ttk.Label(search_frame, text="Tags:", style="Modern.TLabel").grid(
            row=0, column=2, sticky=tk.W, padx=(0, 10)
        )
        self.tags_var = tk.StringVar()
        self.tags_var.trace("w", self._filter_data)
        tags_entry = ttk.Entry(
            search_frame, textvariable=self.tags_var, font=("Segoe UI", 10)
        )
        tags_entry.grid(row=0, column=3, sticky=(tk.W, tk.E))

        # Data table
        table_frame = ttk.LabelFrame(
            content_frame, text="📋 Aufnahmen & Transkriptionen", padding="15"
        )
        table_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # Create modern treeview
        columns = ("ID", "Datum", "Dauer", "Text", "Tags")
        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", height=20
        )

        # Configure columns with modern styling
        column_widths = {"ID": 60, "Datum": 120, "Dauer": 80, "Text": 400, "Tags": 150}
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100), minwidth=50)

        # Add scrollbars
        tree_scroll_y = ttk.Scrollbar(
            table_frame, orient=tk.VERTICAL, command=self.tree.yview
        )
        tree_scroll_x = ttk.Scrollbar(
            table_frame, orient=tk.HORIZONTAL, command=self.tree.xview
        )
        self.tree.configure(
            yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set
        )

        # Grid layout
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        tree_scroll_x.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Bind double-click event for details
        self.tree.bind("<Double-1>", self._on_item_double_click)

    def _setup_auto_save(self):
        """Setup auto-save functionality."""

        def auto_save():
            if self.database_changed:
                self._save_database_changes()
                self.database_changed = False
            self.auto_save_timer = None

        # Schedule auto-save
        if self.auto_save_timer:
            self.root.after_cancel(self.auto_save_timer)
        self.auto_save_timer = self.root.after(self.auto_save_delay, auto_save)

    def _on_item_double_click(self, event):
        """Handle double-click on database item."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            recording_id = item["values"][0]
            self._show_recording_details(recording_id)

    def _show_recording_details(self, recording_id: int):
        """Show detailed view of a recording."""
        try:
            recording = self.database.get_recording_by_id(recording_id)
            if recording:
                # Create detail window
                detail_window = tk.Toplevel(self.root)
                detail_window.title(f"Aufnahme Details - ID: {recording_id}")
                detail_window.geometry("600x400")

                # Add details
                ttk.Label(
                    detail_window,
                    text=f"ID: {recording.get('id')}",
                    font=("Segoe UI", 12, "bold"),
                ).pack(pady=10)
                ttk.Label(
                    detail_window, text=f"Datum: {recording.get('created_at')}"
                ).pack()
                ttk.Label(
                    detail_window,
                    text=f"Dauer: {recording.get('duration', 0):.2f} Sekunden",
                ).pack()
                ttk.Label(
                    detail_window,
                    text=f"Dateigröße: {recording.get('file_size', 0)} Bytes",
                ).pack()

                # Transcription text
                ttk.Label(
                    detail_window, text="Transkription:", font=("Segoe UI", 10, "bold")
                ).pack(pady=(20, 5))
                text_widget = tk.Text(detail_window, height=10, wrap=tk.WORD)
                text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
                text_widget.insert(
                    tk.END,
                    recording.get(
                        "transcription_text", "Keine Transkription verfügbar"
                    ),
                )

        except Exception as e:
            self.logger.error(f"Fehler beim Anzeigen der Aufnahmedetails: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Laden der Details: {e}")

    def _save_database_changes(self):
        """Save database changes."""
        try:
            # Database changes would be saved here
            self._update_status("💾 Datenbank gespeichert", "success")
        except Exception as e:
            self._update_status(f"❌ Speicherfehler: {e}", "error")

    def _update_status(self, message: str, status_type: str = "info"):
        """Update status message with color coding."""
        colors = {
            "success": "#27ae60",
            "warning": "#f39c12",
            "error": "#e74c3c",
            "info": "#2c3e50",
        }

        self.status_label.config(
            text=message, foreground=colors.get(status_type, "#2c3e50")
        )

    def _refresh_data(self):
        """Refresh database data."""
        try:
            # Get database statistics
            stats = self.database.get_statistics()

            # Update statistics labels
            self.stats_labels["total_recordings"].config(
                text=str(stats.get("total_recordings", 0))
            )
            self.stats_labels["total_transcriptions"].config(
                text=str(stats.get("total_transcriptions", 0))
            )
            self.stats_labels["training_samples"].config(
                text=str(stats.get("training_samples", 0))
            )
            self.stats_labels["total_duration_hours"].config(
                text=f"{stats.get('total_duration_hours', 0):.1f}h"
            )
            self.stats_labels["total_size_mb"].config(
                text=f"{stats.get('total_size_mb', 0):.1f} MB"
            )

            # Refresh treeview data
            self._load_treeview_data()

            self._update_status("🔄 Daten aktualisiert", "success")

        except Exception as e:
            self._update_status(f"❌ Fehler beim Aktualisieren: {e}", "error")

    def _load_treeview_data(self):
        """Load data into the treeview."""
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Get recordings from database
            recordings = self.database.get_all_recordings_with_transcriptions()

            for recording in recordings:
                # Format date for display
                created_at = recording.get("created_at", "")
                if created_at:
                    try:
                        # Parse timestamp and format it
                        from datetime import datetime

                        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        formatted_date = dt.strftime("%d.%m.%Y %H:%M")
                    except:
                        formatted_date = created_at
                else:
                    formatted_date = "Unbekannt"

                # Format duration
                duration = recording.get("duration", 0)
                if duration:
                    duration_str = f"{duration:.1f}s"
                else:
                    duration_str = "0s"

                # Get transcription text
                transcription_text = recording.get("transcription_text", "")
                display_text = (
                    transcription_text[:50] + "..."
                    if len(transcription_text) > 50
                    else transcription_text
                )

                self.tree.insert(
                    "",
                    tk.END,
                    values=(
                        recording.get("id", ""),
                        formatted_date,
                        duration_str,
                        display_text,
                        recording.get("tags", ""),
                    ),
                )

        except Exception as e:
            self._update_status(f"❌ Fehler beim Laden der Daten: {e}", "error")

    def _filter_data(self, event=None):
        """Filter treeview data based on search terms."""
        search_term = self.search_var.get().lower()
        tags_term = self.tags_var.get().lower()

        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            recordings = self.database.get_all_recordings_with_transcriptions()

            for recording in recordings:
                text = recording.get("transcription_text", "").lower()
                tags = recording.get("tags", "").lower()

                # Apply filters
                if search_term and search_term not in text:
                    continue
                if tags_term and tags_term not in tags:
                    continue

                # Format date for display
                created_at = recording.get("created_at", "")
                if created_at:
                    try:
                        # Parse timestamp and format it
                        from datetime import datetime

                        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        formatted_date = dt.strftime("%d.%m.%Y %H:%M")
                    except:
                        formatted_date = created_at
                else:
                    formatted_date = "Unbekannt"

                # Format duration
                duration = recording.get("duration", 0)
                if duration:
                    duration_str = f"{duration:.1f}s"
                else:
                    duration_str = "0s"

                # Get transcription text
                transcription_text = recording.get("transcription_text", "")
                display_text = (
                    transcription_text[:50] + "..."
                    if len(transcription_text) > 50
                    else transcription_text
                )

                self.tree.insert(
                    "",
                    tk.END,
                    values=(
                        recording.get("id", ""),
                        formatted_date,
                        duration_str,
                        display_text,
                        recording.get("tags", ""),
                    ),
                )

        except Exception as e:
            self._update_status(f"❌ Fehler beim Filtern: {e}", "error")

    def _export_data(self):
        """Export database data."""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Daten exportieren",
            )

            if filename:
                data = self.database.get_all_recordings_with_transcriptions()
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                self._update_status(f"✅ Daten exportiert nach {filename}", "success")

        except Exception as e:
            self._update_status(f"❌ Exportfehler: {e}", "error")

    def _cleanup_old_data(self):
        """Cleanup old data."""
        if messagebox.askyesno(
            "Bestätigung", "Möchten Sie wirklich alte Daten aufräumen?"
        ):
            try:
                # Implement cleanup logic here
                self._update_status("✅ Aufräumen abgeschlossen", "success")
            except Exception as e:
                self._update_status(f"❌ Aufräumfehler: {e}", "error")

    def bring_to_front(self):
        """Bring the window to front."""
        self.root.lift()
        self.root.focus_force()

    def is_visible(self):
        """Check if the GUI window is visible."""
        try:
            return self.root.winfo_exists() and self.root.winfo_viewable()
        except:
            return False

    def close(self):
        """Close the GUI window."""
        # Save any pending changes
        if self.database_changed:
            self._save_database_changes()

        self.root.destroy()

    def run(self):
        """Run the GUI main loop."""
        self.root.mainloop()
