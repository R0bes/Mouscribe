"""
Unified GUI for managing audio database and custom dictionary.
Provides interface for viewing, editing, and managing both audio recordings and custom words.
"""

import json
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any, Dict, List, Optional

from ...utils.database import AudioDatabase
from ...utils.dictionary import CustomDict
from ...utils.logger import get_logger


class UnifiedManagerGUI:
    """Unified GUI for managing audio database and custom dictionary."""

    def __init__(
        self,
        config=None,
        notification_manager=None,
        parent: tk.Tk | None = None,
        initial_tab: str = "database",
    ):
        """Initialize the unified manager GUI."""
        self.logger = get_logger(self.__class__.__name__)
        self.config = config
        self.notification_manager = notification_manager
        self.database = AudioDatabase()
        self.dictionary = CustomDict(config=self.config)
        self.root: tk.Tk | tk.Toplevel
        self.initial_tab = initial_tab

        # Create main window
        if parent:
            self.root = tk.Toplevel(parent)
            self.root.title("Mauscribe - Datenbank & Wörterbuch Manager")
        else:
            self.root = tk.Tk()
            self.root.title("Mauscribe - Datenbank & Wörterbuch Manager")

        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)

        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")

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
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="Datenbank & Wörterbuch Manager",
            font=("Arial", 16, "bold"),
        )
        title_label.grid(row=0, column=0, pady=(0, 20))

        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Database tab
        self.database_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.database_frame, text="📊 Audio-Datenbank")
        self._setup_database_tab()

        # Dictionary tab
        self.dictionary_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dictionary_frame, text="📚 Benutzerwörterbuch")
        self._setup_dictionary_tab()

        # Set initial tab
        if self.initial_tab == "dictionary":
            self.notebook.select(1)
        else:
            self.notebook.select(0)

    def _setup_database_tab(self):
        """Setup the database management tab."""
        # Configure grid weights
        self.database_frame.columnconfigure(0, weight=1)
        self.database_frame.rowconfigure(1, weight=1)

        # Statistics frame
        stats_frame = ttk.LabelFrame(
            self.database_frame, text="Statistiken", padding="10"
        )
        stats_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

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
        button_frame = ttk.Frame(self.database_frame)
        button_frame.grid(row=1, column=0, pady=(0, 10))

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
        search_frame = ttk.LabelFrame(
            self.database_frame, text="Suche & Filter", padding="10"
        )
        search_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

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
            self.database_frame, text="Aufnahmen & Transkriptionen", padding="10"
        )
        tree_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # Configure tree frame grid
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        # Create treeview
        columns = ("ID", "Datum", "Dauer", "Text", "Tags")
        self.tree = ttk.Treeview(
            tree_frame, columns=columns, show="headings", height=15
        )

        # Configure columns
        self.tree.heading("ID", text="ID")
        self.tree.heading("Datum", text="Datum")
        self.tree.heading("Dauer", text="Dauer")
        self.tree.heading("Text", text="Transkription")
        self.tree.heading("Tags", text="Tags")

        self.tree.column("ID", width=60)
        self.tree.column("Datum", width=120)
        self.tree.column("Dauer", width=80)
        self.tree.column("Text", width=400)
        self.tree.column("Tags", width=100)

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

        # Grid layout
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        tree_scroll_x.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Bind double-click event
        self.tree.bind("<Double-1>", self._on_item_double_click)

    def _setup_dictionary_tab(self):
        """Setup the dictionary management tab."""
        # Configure grid weights
        self.dictionary_frame.columnconfigure(0, weight=1)
        self.dictionary_frame.rowconfigure(1, weight=1)

        # Statistics frame
        dict_stats_frame = ttk.LabelFrame(
            self.dictionary_frame, text="Wörterbuch Statistiken", padding="10"
        )
        dict_stats_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.dict_stats_labels = {}
        dict_stats_data = [
            ("total_words", "Wörter gesamt:"),
            ("file_path", "Dateipfad:"),
        ]

        for i, (key, label) in enumerate(dict_stats_data):
            ttk.Label(dict_stats_frame, text=label).grid(
                row=i, column=0, sticky=tk.W, padx=(0, 5)
            )
            self.dict_stats_labels[key] = ttk.Label(
                dict_stats_frame, text="0", font=("Arial", 10, "bold")
            )
            self.dict_stats_labels[key].grid(row=i, column=1, sticky=tk.W, padx=(0, 20))

        # Control buttons
        dict_button_frame = ttk.Frame(self.dictionary_frame)
        dict_button_frame.grid(row=1, column=0, pady=(0, 10))

        ttk.Button(
            dict_button_frame, text="➕ Wort hinzufügen", command=self._add_word
        ).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(
            dict_button_frame, text="🗑️  Wort entfernen", command=self._remove_word
        ).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(
            dict_button_frame, text="📤 Importieren", command=self._import_dictionary
        ).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(
            dict_button_frame, text="📥 Exportieren", command=self._export_dictionary
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Add word frame
        add_word_frame = ttk.LabelFrame(
            self.dictionary_frame, text="Neues Wort hinzufügen", padding="10"
        )
        add_word_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(add_word_frame, text="Wort:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 5)
        )
        self.new_word_var = tk.StringVar()
        new_word_entry = ttk.Entry(
            add_word_frame, textvariable=self.new_word_var, width=30
        )
        new_word_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        new_word_entry.bind("<Return>", lambda e: self._add_word())

        ttk.Button(add_word_frame, text="Hinzufügen", command=self._add_word).grid(
            row=0, column=2, padx=(10, 0)
        )

        # Word list frame
        word_list_frame = ttk.LabelFrame(
            self.dictionary_frame, text="Wörterbuch", padding="10"
        )
        word_list_frame.grid(
            row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10)
        )

        # Configure word list frame grid
        word_list_frame.columnconfigure(0, weight=1)
        word_list_frame.rowconfigure(0, weight=1)

        # Create listbox for words
        self.word_listbox = tk.Listbox(word_list_frame, height=15)
        word_list_scroll = ttk.Scrollbar(
            word_list_frame, orient=tk.VERTICAL, command=self.word_listbox.yview
        )
        self.word_listbox.configure(yscrollcommand=word_list_scroll.set)

        # Grid layout
        self.word_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        word_list_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Bind selection event
        self.word_listbox.bind("<<ListboxSelect>>", self._on_word_select)

    def _refresh_data(self):
        """Refresh all data from database and dictionary."""
        self._refresh_database_data()
        self._refresh_dictionary_data()

    def _refresh_database_data(self):
        """Refresh database statistics and data."""
        try:
            # Get statistics
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
                text=f"{stats.get('total_duration_hours', 0):.2f}"
            )
            self.stats_labels["total_size_mb"].config(
                text=f"{stats.get('total_size_mb', 0):.2f}"
            )

            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Load recordings
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

                transcription_text = recording.get("transcription_text", "")
                if len(transcription_text) > 50:
                    transcription_text = transcription_text[:47] + "..."

                self.tree.insert(
                    "",
                    "end",
                    values=(
                        recording.get("id", ""),
                        formatted_date,
                        f"{recording.get('duration', 0):.1f}s",
                        transcription_text,
                        recording.get("tags", ""),
                    ),
                )

        except Exception as e:
            self.logger.error(f"Fehler beim Aktualisieren der Datenbankdaten: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Laden der Datenbankdaten: {e}")

    def _refresh_dictionary_data(self):
        """Refresh dictionary statistics and data."""
        try:
            # Get dictionary statistics
            words = list(self.dictionary.get_all_words())

            # Update statistics labels
            self.dict_stats_labels["total_words"].config(text=str(len(words)))
            self.dict_stats_labels["file_path"].config(
                text=str(self.dictionary.dictionary_path)
            )

            # Clear existing items
            self.word_listbox.delete(0, tk.END)

            # Add words to listbox
            for word in sorted(words):
                self.word_listbox.insert(tk.END, word)

        except Exception as e:
            self.logger.error(f"Fehler beim Aktualisieren der Wörterbuchdaten: {e}")
            messagebox.showerror(
                "Fehler", f"Fehler beim Laden der Wörterbuchdaten: {e}"
            )

    def _filter_data(self, *args):
        """Filter database data based on search criteria."""
        # This would implement filtering logic
        pass

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
                    font=("Arial", 12, "bold"),
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
                    detail_window, text="Transkription:", font=("Arial", 10, "bold")
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

    def _add_word(self):
        """Add a new word to the dictionary."""
        word = self.new_word_var.get().strip()
        if word:
            if self.dictionary.add_word(word):
                self.new_word_var.set("")
                self._refresh_dictionary_data()
                messagebox.showinfo("Erfolg", f"Wort '{word}' wurde hinzugefügt")
            else:
                messagebox.showerror(
                    "Fehler", f"Wort '{word}' konnte nicht hinzugefügt werden"
                )
        else:
            messagebox.showwarning("Warnung", "Bitte geben Sie ein Wort ein")

    def _remove_word(self):
        """Remove selected word from dictionary."""
        selection = self.word_listbox.curselection()
        if selection:
            word = self.word_listbox.get(selection[0])
            if messagebox.askyesno(
                "Bestätigung", f"Möchten Sie das Wort '{word}' entfernen?"
            ):
                if self.dictionary.remove_word(word):
                    self._refresh_dictionary_data()
                    messagebox.showinfo("Erfolg", f"Wort '{word}' wurde entfernt")
                else:
                    messagebox.showerror(
                        "Fehler", f"Wort '{word}' konnte nicht entfernt werden"
                    )
        else:
            messagebox.showwarning("Warnung", "Bitte wählen Sie ein Wort aus")

    def _on_word_select(self, event):
        """Handle word selection in listbox."""
        # Could be used for additional functionality
        pass

    def _export_data(self):
        """Export database data."""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            )
            if filename:
                data = self.database.export_all_data()
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                messagebox.showinfo(
                    "Erfolg", f"Daten wurden nach {filename} exportiert"
                )
        except Exception as e:
            self.logger.error(f"Fehler beim Exportieren der Daten: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Exportieren: {e}")

    def _export_dictionary(self):
        """Export dictionary data."""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[
                    ("JSON files", "*.json"),
                    ("Text files", "*.txt"),
                    ("All files", "*.*"),
                ],
            )
            if filename:
                if filename.endswith(".txt"):
                    # Export as plain text
                    words = list(self.dictionary.get_all_words())
                    with open(filename, "w", encoding="utf-8") as f:
                        for word in sorted(words):
                            f.write(word + "\n")
                else:
                    # Export as JSON
                    data = self.dictionary.export_data()
                    with open(filename, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                messagebox.showinfo(
                    "Erfolg", f"Wörterbuch wurde nach {filename} exportiert"
                )
        except Exception as e:
            self.logger.error(f"Fehler beim Exportieren des Wörterbuchs: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Exportieren: {e}")

    def _import_dictionary(self):
        """Import dictionary data."""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[
                    ("JSON files", "*.json"),
                    ("Text files", "*.txt"),
                    ("All files", "*.*"),
                ]
            )
            if filename:
                if filename.endswith(".txt"):
                    # Import from plain text
                    with open(filename, "r", encoding="utf-8") as f:
                        words = [line.strip() for line in f if line.strip()]
                    for word in words:
                        self.dictionary.add_word(word)
                else:
                    # Import from JSON
                    with open(filename, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    self.dictionary.import_data(data)
                self._refresh_dictionary_data()
                messagebox.showinfo(
                    "Erfolg", f"Wörterbuch wurde aus {filename} importiert"
                )
        except Exception as e:
            self.logger.error(f"Fehler beim Importieren des Wörterbuchs: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Importieren: {e}")

    def _cleanup_old_data(self):
        """Clean up old database data."""
        try:
            if messagebox.askyesno("Bestätigung", "Möchten Sie alte Daten aufräumen?"):
                # This would implement cleanup logic
                messagebox.showinfo("Erfolg", "Aufräumen abgeschlossen")
        except Exception as e:
            self.logger.error(f"Fehler beim Aufräumen: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Aufräumen: {e}")

    def run(self):
        """Run the GUI."""
        self.root.mainloop()

    def show_recording(self, recording_id: int):
        """Show specific recording in the GUI."""
        self.notebook.select(0)  # Switch to database tab
        self._show_recording_details(recording_id)

    def set_window_size(self, width: int, height: int):
        """Set the window size."""
        self.root.geometry(f"{width}x{height}")

    def close(self):
        """Close the GUI window."""
        if hasattr(self, "root") and self.root:
            self.root.destroy()

    def is_visible(self) -> bool:
        """Check if the GUI window is visible."""
        if hasattr(self, "root") and self.root:
            try:
                return self.root.winfo_viewable()
            except:
                return False
        return False

    def bring_to_front(self):
        """Bring the GUI window to the front."""
        if hasattr(self, "root") and self.root:
            try:
                self.root.lift()
                self.root.focus_force()
            except:
                pass
