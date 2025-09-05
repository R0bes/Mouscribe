"""
Modern GUI for managing audio database and custom dictionary.
Provides an intuitive, modern interface with direct editing capabilities.
"""

import json
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any, Dict, List, Optional

from ...utils.database import AudioDatabase
from ...utils.dictionary import CustomDict
from ...utils.logger import get_logger


class ModernManagerGUI:
    """Modern GUI for managing audio database and custom dictionary."""

    def __init__(
        self,
        config=None,
        notification_manager=None,
        parent: tk.Tk | None = None,
        initial_tab: str = "database",
    ):
        """Initialize the modern manager GUI."""
        self.logger = get_logger(self.__class__.__name__)
        self.config = config
        self.notification_manager = notification_manager
        self.database = AudioDatabase()
        self.dictionary = CustomDict(config=self.config)
        self.root: tk.Tk | tk.Toplevel
        self.initial_tab = initial_tab

        # Auto-save timer
        self.auto_save_timer = None
        self.auto_save_delay = 2000  # 2 seconds

        # Track changes for auto-save
        self.dictionary_changed = False
        self.database_changed = False

        # Create main window
        if parent:
            self.root = tk.Toplevel(parent)
            self.root.title("Mauscribe - Modern Manager")
        else:
            self.root = tk.Tk()
            self.root.title("Mauscribe - Modern Manager")

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
        self.refresh_word_list()  # Load dictionary words

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
            header_frame, text="🎯 Mauscribe Manager", style="Title.TLabel"
        )
        title_label.pack(side=tk.LEFT)

        # Status indicator
        self.status_label = ttk.Label(
            header_frame, text="✅ Bereit", style="Success.TLabel"
        )
        self.status_label.pack(side=tk.RIGHT)

        # Notebook for tabs with modern styling
        self.notebook = ttk.Notebook(main_container)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Database tab
        self.database_frame = ttk.Frame(self.notebook, style="Modern.TFrame")
        self.notebook.add(self.database_frame, text="📊 Audio-Datenbank")
        self._setup_database_tab()

        # Dictionary tab
        self.dictionary_frame = ttk.Frame(self.notebook, style="Modern.TFrame")
        self.notebook.add(self.dictionary_frame, text="📚 Wörterbuch")
        self._setup_dictionary_tab()

        # Set initial tab
        if self.initial_tab == "dictionary":
            self.notebook.select(1)
        else:
            self.notebook.select(0)

    def _setup_database_tab(self):
        """Setup the modern database management tab."""
        # Configure grid weights
        self.database_frame.columnconfigure(0, weight=1)
        self.database_frame.rowconfigure(2, weight=1)

        # Statistics cards
        stats_frame = ttk.Frame(self.database_frame)
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
        button_frame = ttk.Frame(self.database_frame)
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
            self.database_frame, text="🔍 Suche & Filter", padding="15"
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
            self.database_frame, text="📋 Aufnahmen & Transkriptionen", padding="15"
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

    def _setup_dictionary_tab(self):
        """Setup the modern dictionary management tab."""
        # Configure grid weights
        self.dictionary_frame.columnconfigure(0, weight=1)
        self.dictionary_frame.rowconfigure(1, weight=1)

        # Dictionary info
        info_frame = ttk.LabelFrame(
            self.dictionary_frame, text="ℹ️ Wörterbuch-Info", padding="15"
        )
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))

        self.info_label = ttk.Label(
            info_frame, text="Lade Informationen...", style="Modern.TLabel"
        )
        self.info_label.pack(anchor=tk.W)

        # Words list with inline editing
        words_frame = ttk.LabelFrame(
            self.dictionary_frame,
            text="📝 Wörter verwalten (Doppelklick zum Bearbeiten, letzte Zeile für neue Wörter)",
            padding="15",
        )
        words_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        words_frame.columnconfigure(0, weight=1)
        words_frame.rowconfigure(1, weight=1)

        # Search bar
        search_frame = ttk.Frame(words_frame)
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(search_frame, text="🔍 Suchen:", style="Modern.TLabel").pack(
            side=tk.LEFT, padx=(0, 10)
        )

        self.word_search_var = tk.StringVar()
        self.word_search_var.trace("w", self._filter_words)
        word_search_entry = ttk.Entry(
            search_frame,
            textvariable=self.word_search_var,
            font=("Segoe UI", 10),
            width=30,
        )
        word_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Words listbox with modern styling
        list_frame = ttk.Frame(words_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Create listbox with modern font
        self.word_listbox = tk.Listbox(
            list_frame,
            font=("Segoe UI", 10),
            selectmode=tk.SINGLE,
            height=20,
            activestyle="none",
            relief=tk.FLAT,
            bg="white",
            fg="#2c3e50",
            selectbackground="#3498db",
            selectforeground="white",
        )

        # Bind events for inline editing
        self.word_listbox.bind("<Double-Button-1>", self._start_inline_edit)
        self.word_listbox.bind("<Button-1>", self._on_word_select)
        self.word_listbox.bind("<Key>", self._on_listbox_key)

        # Scrollbar
        word_scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.word_listbox.yview
        )
        self.word_listbox.configure(yscrollcommand=word_scrollbar.set)

        self.word_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        word_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Action buttons
        action_frame = ttk.Frame(words_frame)
        action_frame.grid(row=2, column=0, pady=(10, 0))

        ttk.Button(
            action_frame,
            text="🗑️ Löschen",
            command=self._delete_selected_word,
            style="Modern.TButton",
        ).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(
            action_frame,
            text="📤 Exportieren",
            command=self._export_words,
            style="Modern.TButton",
        ).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(
            action_frame,
            text="📥 Importieren",
            command=self._import_words,
            style="Modern.TButton",
        ).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(
            action_frame,
            text="🗑️ Alle löschen",
            command=self._clear_dictionary,
            style="Modern.TButton",
        ).pack(side=tk.LEFT)

        # Inline edit entry (hidden by default)
        self.inline_edit_entry = ttk.Entry(self.dictionary_frame, font=("Segoe UI", 10))
        self.inline_edit_entry.bind("<Return>", self._finish_inline_edit)
        self.inline_edit_entry.bind("<Escape>", self._cancel_inline_edit)
        self.inline_edit_entry.bind("<FocusOut>", self._finish_inline_edit)

    def _setup_auto_save(self):
        """Setup auto-save functionality."""

        def auto_save():
            if self.dictionary_changed:
                self._save_dictionary_changes()
                self.dictionary_changed = False
            if self.database_changed:
                self._save_database_changes()
                self.database_changed = False
            self.auto_save_timer = None

        # Schedule auto-save
        if self.auto_save_timer:
            self.root.after_cancel(self.auto_save_timer)
        self.auto_save_timer = self.root.after(self.auto_save_delay, auto_save)

    def _start_inline_edit(self, event):
        """Start inline editing of a word."""
        selection = self.word_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        self._start_inline_edit_at_index(index)

    def _start_inline_edit_at_index(self, index):
        """Start inline editing at specific index."""
        current_word = self.word_listbox.get(index)

        # Get listbox coordinates
        bbox = self.word_listbox.bbox(index)
        if not bbox:
            return

        x, y, width, height = bbox

        # Position the edit entry
        self.inline_edit_entry.place(x=x, y=y, width=width, height=height)
        self.inline_edit_entry.delete(0, tk.END)
        self.inline_edit_entry.insert(0, current_word)
        self.inline_edit_entry.select_range(0, tk.END)
        self.inline_edit_entry.focus()

        # Store the index being edited
        self.editing_index = index

    def _finish_inline_edit(self, event=None):
        """Finish inline editing."""
        if not hasattr(self, "editing_index"):
            return

        new_word = self.inline_edit_entry.get().strip()
        old_word = self.word_listbox.get(self.editing_index)

        if new_word:
            try:
                if old_word:  # Editing existing word
                    if new_word != old_word:
                        self.dictionary.remove_word(old_word)
                        self.dictionary.add_word(new_word)
                        self.dictionary_changed = True
                        self._setup_auto_save()
                        self.refresh_word_list()
                        self._update_status(
                            f"✅ Wort geändert: '{old_word}' → '{new_word}'", "success"
                        )
                else:  # Adding new word
                    if self.dictionary.add_word(new_word):
                        self.dictionary_changed = True
                        self._setup_auto_save()
                        self.refresh_word_list()
                        self._update_status(
                            f"✅ Wort '{new_word}' hinzugefügt", "success"
                        )
                    else:
                        self._update_status(
                            f"❌ Fehler beim Hinzufügen von '{new_word}'", "error"
                        )
            except Exception as e:
                self._update_status(f"❌ Fehler: {e}", "error")

        self._cancel_inline_edit()

    def _cancel_inline_edit(self, event=None):
        """Cancel inline editing."""
        self.inline_edit_entry.place_forget()
        if hasattr(self, "editing_index"):
            del self.editing_index

    def _on_word_select(self, event):
        """Handle word selection."""
        # Cancel any ongoing inline edit
        if hasattr(self, "editing_index"):
            self._cancel_inline_edit()

    def _on_listbox_key(self, event):
        """Handle keyboard input in listbox."""
        # Check if we're on the last (empty) line
        selection = self.word_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        current_word = self.word_listbox.get(index)

        # If we're on the empty line and user starts typing
        if current_word == "" and event.char.isprintable():
            self._start_inline_edit_at_index(index)
            # Insert the character that was typed
            self.inline_edit_entry.insert(0, event.char)
            return "break"  # Prevent default behavior

    def _delete_selected_word(self):
        """Delete the selected word."""
        selection = self.word_listbox.curselection()
        if not selection:
            self._update_status("⚠️ Bitte wählen Sie ein Wort aus", "warning")
            return

        index = selection[0]
        word = self.word_listbox.get(index)

        if messagebox.askyesno(
            "Bestätigung", f"Möchten Sie das Wort '{word}' wirklich löschen?"
        ):
            try:
                self.dictionary.remove_word(word)
                self.dictionary_changed = True
                self._setup_auto_save()
                self.refresh_word_list()
                self._update_status(f"✅ Wort '{word}' gelöscht", "success")
            except Exception as e:
                self._update_status(f"❌ Fehler beim Löschen: {e}", "error")

    def _filter_words(self, event=None):
        """Filter words based on search term."""
        search_term = self.word_search_var.get().lower()

        self.word_listbox.delete(0, tk.END)

        if not search_term:
            for word in self.all_words:
                self.word_listbox.insert(tk.END, word)
        else:
            filtered_words = [
                word for word in self.all_words if search_term in word.lower()
            ]
            for word in filtered_words:
                self.word_listbox.insert(tk.END, word)

        self._update_status(f"🔍 {self.word_listbox.size()} Wörter gefunden")

    def _save_dictionary_changes(self):
        """Save dictionary changes."""
        try:
            self.dictionary.save()
            self._update_status("💾 Wörterbuch gespeichert", "success")
        except Exception as e:
            self._update_status(f"❌ Speicherfehler: {e}", "error")

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

    def refresh_word_list(self):
        """Refresh the word list."""
        try:
            self.all_words = self.dictionary.get_all_words()
            self.word_listbox.delete(0, tk.END)

            for word in self.all_words:
                self.word_listbox.insert(tk.END, word)

            # Add empty line at the end for new entries
            self.word_listbox.insert(tk.END, "")

            self._update_status(f"📚 {len(self.all_words)} Wörter geladen")
            self.update_info()

        except Exception as e:
            self._update_status(f"❌ Fehler beim Laden: {e}", "error")

    def update_info(self):
        """Update dictionary information."""
        try:
            info = self.dictionary.get_dictionary_info()
            info_text = f"📁 Pfad: {info['path']} | 📊 Wörter: {info['word_count']} | 📄 Datei: {'✅' if info['exists'] else '❌'}"
            self.info_label.config(text=info_text)
        except Exception as e:
            self.info_label.config(text=f"❌ Fehler beim Laden der Informationen: {e}")

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

    def _export_words(self):
        """Export words to file."""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Wörter exportieren",
            )

            if filename:
                words = self.dictionary.get_all_words()
                with open(filename, "w", encoding="utf-8") as f:
                    for word in words:
                        f.write(word + "\n")

                self._update_status(f"✅ Wörter exportiert nach {filename}", "success")

        except Exception as e:
            self._update_status(f"❌ Exportfehler: {e}", "error")

    def _import_words(self):
        """Import words from file."""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Wörter importieren",
            )

            if filename:
                with open(filename, "r", encoding="utf-8") as f:
                    words = [line.strip() for line in f.readlines() if line.strip()]

                added_count = 0
                for word in words:
                    if self.dictionary.add_word(word):
                        added_count += 1

                self.dictionary_changed = True
                self._setup_auto_save()
                self.refresh_word_list()
                self._update_status(f"✅ {added_count} Wörter importiert", "success")

        except Exception as e:
            self._update_status(f"❌ Importfehler: {e}", "error")

    def _clear_dictionary(self):
        """Clear all words from dictionary."""
        if messagebox.askyesno(
            "Bestätigung", "Möchten Sie wirklich alle Wörter löschen?"
        ):
            try:
                self.dictionary.clear()
                self.dictionary_changed = True
                self._setup_auto_save()
                self.refresh_word_list()
                self._update_status("✅ Wörterbuch geleert", "success")
            except Exception as e:
                self._update_status(f"❌ Fehler beim Leeren: {e}", "error")

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
        if self.dictionary_changed:
            self._save_dictionary_changes()
        if self.database_changed:
            self._save_database_changes()

        self.root.destroy()

    def run(self):
        """Run the GUI main loop."""
        self.root.mainloop()
