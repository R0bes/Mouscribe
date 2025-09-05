"""
GUI for managing the audio database and training data.
Provides interface for viewing, editing, and exporting audio recordings.
"""

import json
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any, Dict, List

from .database import AudioDatabase
from .utils.logger import get_logger


class DatabaseManagerGUI:
    """GUI for managing audio database."""

    def __init__(self, parent: tk.Tk | None = None):
        """Initialize the database manager GUI."""
        self.logger = get_logger(self.__class__.__name__)
        self.database = AudioDatabase()
        self.root: tk.Tk | tk.Toplevel

        # Create main window
        if parent:
            self.root = tk.Toplevel(parent)
            self.root.title("Mauscribe - Audio-Datenbank Manager")
        else:
            self.root = tk.Tk()
            self.root.title("Mauscribe - Audio-Datenbank Manager")

        self.root.geometry("1000x700")
        self.root.minsize(800, 600)

        self._setup_ui()
        self._refresh_data()

    def _setup_ui(self):
        """Setup the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame, text="Audio-Datenbank Manager", font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Statistics frame
        stats_frame = ttk.LabelFrame(main_frame, text="Statistiken", padding="10")
        stats_frame.grid(
            row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10)
        )

        # Statistics labels
        self.stats_labels = {}
        stats_data = [
            ("total_recordings", "Aufnahmen gesamt:"),
            ("total_transcriptions", "Transkriptionen:"),
            ("training_samples", "Trainingsdaten:"),
            ("total_duration_hours", "Gesamtdauer (Stunden):"),
            ("total_size_mb", "Gesamtgröße (MB):"),
        ]

        for i, (key, label) in enumerate(stats_data):
            ttk.Label(stats_frame, text=label).grid(
                row=i // 3, column=(i % 3) * 2, sticky=tk.W, padx=(0, 5)
            )
            self.stats_labels[key] = ttk.Label(
                stats_frame, text="0", font=("Arial", 10, "bold")
            )
            self.stats_labels[key].grid(
                row=i // 3, column=(i % 3) * 2 + 1, sticky=tk.W, padx=(0, 20)
            )

        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=(0, 10))

        ttk.Button(
            button_frame, text="🔄 Aktualisieren", command=self._refresh_data
        ).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="📤 Exportieren", command=self._export_data).pack(
            side=tk.LEFT, padx=(0, 10)
        )
        ttk.Button(
            button_frame, text="🗑️  Aufräumen", command=self._cleanup_old_data
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Search frame
        search_frame = ttk.LabelFrame(main_frame, text="Suche & Filter", padding="10")
        search_frame.grid(
            row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10)
        )

        ttk.Label(search_frame, text="Suche:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 5)
        )
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._filter_data)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))

        ttk.Label(search_frame, text="Tags:").grid(
            row=0, column=2, sticky=tk.W, padx=(0, 5)
        )
        self.tags_var = tk.StringVar()
        self.tags_var.trace("w", self._filter_data)
        tags_entry = ttk.Entry(search_frame, textvariable=self.tags_var, width=20)
        tags_entry.grid(row=0, column=3, sticky=tk.W)

        # Treeview for data
        tree_frame = ttk.LabelFrame(
            main_frame, text="Aufnahmen & Transkriptionen", padding="10"
        )
        tree_frame.grid(
            row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10)
        )
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        # Create treeview
        columns = ("Datum", "Dauer", "Text", "Sprache", "Qualität", "Tags")
        self.tree = ttk.Treeview(
            tree_frame, columns=columns, show="headings", height=15
        )

        # Configure columns
        self.tree.heading("Datum", text="Datum")
        self.tree.heading("Dauer", text="Dauer (s)")
        self.tree.heading("Text", text="Transkription")
        self.tree.heading("Sprache", text="Sprache")
        self.tree.heading("Qualität", text="Qualität")
        self.tree.heading("Tags", text="Tags")

        self.tree.column("Datum", width=120)
        self.tree.column("Dauer", width=80)
        self.tree.column("Text", width=300)
        self.tree.column("Sprache", width=80)
        self.tree.column("Qualität", width=80)
        self.tree.column("Tags", width=150)

        # Scrollbars
        tree_scroll_y = ttk.Scrollbar(
            tree_frame, orient=tk.VERTICAL, command=self.tree.yview
        )
        tree_scroll_x = ttk.Scrollbar(
            tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview
        )
        self.tree.configure(
            yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set
        )

        # Grid treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        tree_scroll_x.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Bind double-click event
        self.tree.bind("<Double-1>", self._on_item_double_click)

        # Details frame
        details_frame = ttk.LabelFrame(main_frame, text="Details", padding="10")
        details_frame.grid(
            row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10)
        )

        # Details text
        self.details_text = tk.Text(details_frame, height=6, wrap=tk.WORD)
        details_scroll = ttk.Scrollbar(
            details_frame, orient=tk.VERTICAL, command=self.details_text.yview
        )
        self.details_text.configure(yscrollcommand=details_scroll.set)

        self.details_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        details_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        details_frame.columnconfigure(0, weight=1)
        details_frame.rowconfigure(0, weight=1)

        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self._on_selection_change)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Bereit")
        status_bar = ttk.Label(
            main_frame, textvariable=self.status_var, relief=tk.SUNKEN
        )
        status_bar.grid(
            row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0)
        )

    def _refresh_data(self):
        """Refresh the data display."""
        try:
            self.status_var.set("Lade Daten...")
            self.root.update()

            # Get training data
            training_data = self.database.get_recordings_for_training()

            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Add data to treeview
            for item in training_data:
                # Format date
                date_str = (
                    item.get("timestamp", "")[:19].replace("T", " ")
                    if item.get("timestamp")
                    else ""
                )

                # Format duration
                duration = item.get("duration_seconds", 0)
                duration_str = f"{duration:.1f}" if duration else "0.0"

                # Format text (truncate if too long)
                text = (
                    item.get("raw_text", "")[:50] + "..."
                    if len(item.get("raw_text", "")) > 50
                    else item.get("raw_text", "")
                )

                # Format tags
                tags = item.get("tags", [])
                tags_str = ", ".join(tags) if tags else ""

                # Insert into treeview
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        date_str,
                        duration_str,
                        text,
                        item.get("language", ""),
                        (
                            f"{item.get('quality_score', 0):.2f}"
                            if item.get("quality_score")
                            else ""
                        ),
                        tags_str,
                    ),
                    tags=(item,),
                )  # Store full item data in tags

            # Update statistics
            stats = self.database.get_statistics()
            for key, label in self.stats_labels.items():
                if key in stats:
                    value = stats[key]
                    if isinstance(value, float):
                        label.config(text=f"{value:.2f}")
                    else:
                        label.config(text=str(value))

            self.status_var.set(f"Geladen: {len(training_data)} Aufnahmen")

        except Exception as e:
            self.logger.error(f"Failed to refresh data: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Laden der Daten: {e}")
            self.status_var.set("Fehler beim Laden der Daten")

    def _filter_data(self, *args):
        """Filter the displayed data based on search terms."""
        search_term = self.search_var.get().lower()
        tags_term = self.tags_var.get().lower()

        # Show all items first
        for item in self.tree.get_children():
            self.tree.reattach(item, "", "end")

        # Hide items that don't match filter
        for item in self.tree.get_children():
            item_data = self.tree.item(item, "tags")[0]  # Get stored data

            # Check search term
            if search_term:
                text = item_data.get("raw_text", "").lower()
                if search_term not in text:
                    self.tree.detach(item)
                    continue

            # Check tags term
            if tags_term:
                tags = item_data.get("tags", [])
                if not any(tags_term in tag.lower() for tag in tags):
                    self.tree.detach(item)
                    continue

        # Update status
        visible_count = len(self.tree.get_children())
        self.status_var.set(f"Gefiltert: {visible_count} Aufnahmen")

    def _on_selection_change(self, event):
        """Handle selection change in treeview."""
        selection = self.tree.selection()
        if not selection:
            self.details_text.delete(1.0, tk.END)
            return

        # Get selected item data
        item = selection[0]
        item_data = self.tree.item(item, "tags")[0]

        # Display details
        self.details_text.delete(1.0, tk.END)

        details = f"""Aufnahme ID: {item_data.get('recording_id', 'N/A')}
Transkription ID: {item_data.get('transcription_id', 'N/A')}
Datum: {item_data.get('timestamp', 'N/A')}
Dauer: {item_data.get('duration_seconds', 'N/A')} Sekunden
Sample Rate: {item_data.get('sample_rate', 'N/A')} Hz
Kanäle: {item_data.get('channels', 'N/A')}
Sprache: {item_data.get('language', 'N/A')}
Qualität: {item_data.get('quality_score', 'N/A')}

Roher Text:
{item_data.get('raw_text', 'N/A')}

Korrigierter Text:
{item_data.get('corrected_text', 'N/A')}

Notizen:
{item_data.get('notes', 'Keine')}

Tags:
{', '.join(item_data.get('tags', [])) if item_data.get('tags') else 'Keine'}

Audio-Datei:
{item_data.get('audio_file_path', 'N/A')}"""

        self.details_text.insert(1.0, details)

    def _on_item_double_click(self, event):
        """Handle double-click on treeview item."""
        selection = self.tree.selection()
        if not selection:
            return

        item = selection[0]
        item_data = self.tree.item(item, "tags")[0]

        # Open edit dialog
        self._edit_item(item_data)

    def _edit_item(self, item_data: dict[str, Any]):
        """Open edit dialog for item."""
        dialog = EditItemDialog(self.root, item_data, self.database)
        self.root.wait_window(dialog.root)
        self._refresh_data()

    def _export_data(self):
        """Export data to file."""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Trainingsdaten exportieren",
            )

            if filename:
                if self.database.export_training_data(filename):
                    messagebox.showinfo(
                        "Erfolg", f"Daten erfolgreich exportiert nach:\n{filename}"
                    )
                    self.status_var.set(f"Daten exportiert: {filename}")
                else:
                    messagebox.showerror("Fehler", "Fehler beim Exportieren der Daten")

        except Exception as e:
            self.logger.error(f"Failed to export data: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Exportieren: {e}")

    def _cleanup_old_data(self):
        """Clean up old recordings."""
        try:
            result = messagebox.askyesno(
                "Aufräumen",
                "Möchten Sie Aufnahmen älter als 30 Tage löschen?\n\n"
                "Dies kann nicht rückgängig gemacht werden!",
            )

            if result:
                deleted_count = self.database.cleanup_old_recordings(days_to_keep=30)
                messagebox.showinfo(
                    "Aufräumen abgeschlossen",
                    f"{deleted_count} alte Aufnahmen wurden gelöscht",
                )
                self._refresh_data()

        except Exception as e:
            self.logger.error(f"Failed to cleanup old data: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Aufräumen: {e}")

    def run(self):
        """Run the GUI."""
        self.root.mainloop()


class EditItemDialog:
    """Dialog for editing training data items."""

    def __init__(
        self,
        parent: tk.Tk | tk.Toplevel,
        item_data: dict[str, Any],
        database: AudioDatabase,
    ):
        """Initialize the edit dialog."""
        self.database = database
        self.item_data = item_data

        # Create dialog window
        self.root = tk.Toplevel(parent)
        self.root.title("Eintrag bearbeiten")
        self.root.geometry("500x400")
        self.root.transient(parent)
        self.root.grab_set()

        self._setup_ui()

    def _setup_ui(self):
        """Setup the dialog UI."""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            main_frame, text="Trainingsdaten bearbeiten", font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Form fields
        # Quality score
        ttk.Label(main_frame, text="Qualitätsbewertung (0-1):").pack(
            anchor=tk.W, pady=(0, 5)
        )
        self.quality_var = tk.DoubleVar(value=self.item_data.get("quality_score", 0.5))
        quality_scale = ttk.Scale(
            main_frame,
            from_=0.0,
            to=1.0,
            variable=self.quality_var,
            orient=tk.HORIZONTAL,
        )
        quality_scale.pack(fill=tk.X, pady=(0, 15))

        # Notes
        ttk.Label(main_frame, text="Notizen:").pack(anchor=tk.W, pady=(0, 5))
        self.notes_text = tk.Text(main_frame, height=4, wrap=tk.WORD)
        self.notes_text.pack(fill=tk.X, pady=(0, 15))
        self.notes_text.insert(1.0, self.item_data.get("notes", ""))

        # Tags
        ttk.Label(main_frame, text="Tags (kommagetrennt):").pack(
            anchor=tk.W, pady=(0, 5)
        )
        self.tags_var = tk.StringVar(value=", ".join(self.item_data.get("tags", [])))
        tags_entry = ttk.Entry(main_frame, textvariable=self.tags_var)
        tags_entry.pack(fill=tk.X, pady=(0, 15))

        # Training validity
        self.valid_var = tk.BooleanVar(
            value=self.item_data.get("is_valid_for_training", True)
        )
        valid_check = ttk.Checkbutton(
            main_frame, text="Für Training geeignet", variable=self.valid_var
        )
        valid_check.pack(anchor=tk.W, pady=(0, 20))

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))

        ttk.Button(button_frame, text="Speichern", command=self._save_changes).pack(
            side=tk.RIGHT, padx=(10, 0)
        )
        ttk.Button(button_frame, text="Abbrechen", command=self.root.destroy).pack(
            side=tk.RIGHT
        )

    def _save_changes(self):
        """Save changes to database."""
        try:
            # Parse tags
            tags_text = self.tags_var.get().strip()
            tags = (
                [tag.strip() for tag in tags_text.split(",") if tag.strip()]
                if tags_text
                else []
            )

            # Update training data
            self.database.save_training_data(
                transcription_id=self.item_data["transcription_id"],
                is_valid_for_training=self.valid_var.get(),
                quality_score=self.quality_var.get(),
                notes=self.notes_text.get(1.0, tk.END).strip(),
                tags=tags,
            )

            messagebox.showinfo("Erfolg", "Änderungen wurden gespeichert")
            self.root.destroy()

        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")


def main():
    """Main entry point for the database manager GUI."""
    app = DatabaseManagerGUI()
    app.run()


if __name__ == "__main__":
    main()
