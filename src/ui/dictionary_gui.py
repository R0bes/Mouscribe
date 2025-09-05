# src/dictionary_gui.py - Dictionary Management GUI for Mauscribe
"""
Graphical user interface for managing the custom dictionary.
Provides a user-friendly way to add, remove, and view custom words.
"""

import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import List, Optional

from .custom_dictionary import CustomDict, get_custom_dictionary


class DictionaryGUI:
    """GUI für die Verwaltung des benutzerdefinierten Wörterbuchs."""

    def __init__(self, root: Optional[tk.Tk] = None, config=None):
        """
        Initialisiert die GUI.

        Args:
            root: Tkinter-Root-Fenster (optional, wird erstellt wenn None)
            config: Config-Objekt für Wörterbuch-Pfad (optional)
        """
        self.root = root or tk.Tk()
        self.dictionary = get_custom_dictionary(config)

        self.setup_ui()
        self.refresh_word_list()

    def setup_ui(self):
        """Erstellt die Benutzeroberfläche."""
        self.root.title("Mauscribe - Wörterbuch-Verwaltung")
        self.root.geometry("600x500")
        self.root.resizable(True, True)

        # Hauptframe
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Konfiguration des Grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Titel
        title_label = ttk.Label(
            main_frame,
            text="📚 Benutzerdefiniertes Wörterbuch",
            font=("Arial", 16, "bold"),
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Wörterbuch-Informationen
        info_frame = ttk.LabelFrame(
            main_frame, text="Wörterbuch-Informationen", padding="10"
        )
        info_frame.grid(
            row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20)
        )

        self.info_label = ttk.Label(info_frame, text="Lade Informationen...")
        self.info_label.grid(row=0, column=0, sticky=tk.W)

        # Wort hinzufügen
        add_frame = ttk.LabelFrame(main_frame, text="Wort hinzufügen", padding="10")
        add_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(add_frame, text="Wort:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10)
        )
        self.add_entry = ttk.Entry(add_frame, width=30)
        self.add_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        self.add_entry.bind("<Return>", lambda e: self.add_word())

        add_button = ttk.Button(add_frame, text="Hinzufügen", command=self.add_word)
        add_button.grid(row=0, column=2)

        add_frame.columnconfigure(1, weight=1)

        # Wortliste
        list_frame = ttk.LabelFrame(
            main_frame, text="Wörter im Wörterbuch", padding="10"
        )
        list_frame.grid(
            row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10)
        )

        # Suchleiste
        search_frame = ttk.Frame(list_frame)
        search_frame.grid(
            row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10)
        )

        ttk.Label(search_frame, text="Suchen:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10)
        )
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.filter_words)

        search_frame.columnconfigure(1, weight=1)

        # Wortliste mit Scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.word_listbox = tk.Listbox(list_container, height=15, selectmode=tk.SINGLE)
        scrollbar = ttk.Scrollbar(
            list_container, orient=tk.VERTICAL, command=self.word_listbox.yview
        )
        self.word_listbox.configure(yscrollcommand=scrollbar.set)

        self.word_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        list_container.columnconfigure(0, weight=1)
        list_container.rowconfigure(0, weight=1)

        # Buttons unter der Liste
        button_frame = ttk.Frame(list_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))

        ttk.Button(
            button_frame, text="Wort entfernen", command=self.remove_selected_word
        ).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(
            button_frame, text="Alle anzeigen", command=self.refresh_word_list
        ).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(
            button_frame, text="Wörterbuch leeren", command=self.clear_dictionary
        ).grid(row=0, column=2, padx=(0, 10))

        # Import/Export
        io_frame = ttk.LabelFrame(main_frame, text="Import/Export", padding="10")
        io_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Button(io_frame, text="Wörter importieren", command=self.import_words).grid(
            row=0, column=0, padx=(0, 10)
        )
        ttk.Button(io_frame, text="Wörter exportieren", command=self.export_words).grid(
            row=0, column=1, padx=(0, 10)
        )

        # Statusleiste
        self.status_label = ttk.Label(
            main_frame, text="Bereit", relief=tk.SUNKEN, anchor=tk.W
        )
        self.status_label.grid(
            row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0)
        )

        # Alle Wörter speichern
        self.all_words = []

        # UI aktualisieren
        self.update_info()

    def update_info(self):
        """Aktualisiert die Wörterbuch-Informationen."""
        try:
            info = self.dictionary.get_dictionary_info()
            info_text = f"Pfad: {info['path']} | Wörter: {info['word_count']} | Datei: {'Ja' if info['exists'] else 'Nein'}"
            self.info_label.config(text=info_text)
        except Exception as e:
            self.info_label.config(text=f"Fehler beim Laden der Informationen: {e}")

    def refresh_word_list(self):
        """Aktualisiert die Wortliste."""
        try:
            self.all_words = self.dictionary.get_all_words()
            self.word_listbox.delete(0, tk.END)

            for word in self.all_words:
                self.word_listbox.insert(tk.END, word)

            self.status_label.config(text=f"{len(self.all_words)} Wörter geladen")
            self.update_info()

        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Wörter: {e}")
            self.status_label.config(text="Fehler beim Laden der Wörter")

    def filter_words(self, event=None):
        """Filtert die Wörter basierend auf der Sucheingabe."""
        search_term = self.search_entry.get().lower()

        self.word_listbox.delete(0, tk.END)

        if not search_term:
            # Alle Wörter anzeigen
            for word in self.all_words:
                self.word_listbox.insert(tk.END, word)
        else:
            # Gefilterte Wörter anzeigen
            filtered_words = [
                word for word in self.all_words if search_term in word.lower()
            ]
            for word in filtered_words:
                self.word_listbox.insert(tk.END, word)

        self.status_label.config(text=f"{self.word_listbox.size()} Wörter gefunden")

    def add_word(self):
        """Fügt ein Wort zum Wörterbuch hinzu."""
        word = self.add_entry.get().strip()

        if not word:
            messagebox.showwarning("Warnung", "Bitte geben Sie ein Wort ein")
            return

        try:
            if self.dictionary.add_word(word):
                self.add_entry.delete(0, tk.END)
                self.refresh_word_list()
                self.status_label.config(text=f"Wort '{word}' erfolgreich hinzugefügt")
                messagebox.showinfo(
                    "Erfolg",
                    f"Wort '{word}' wurde erfolgreich zum Wörterbuch hinzugefügt",
                )
            else:
                messagebox.showerror(
                    "Fehler", f"Fehler beim Hinzufügen des Wortes '{word}'"
                )

        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Hinzufügen des Wortes: {e}")

    def remove_selected_word(self):
        """Entfernt das ausgewählte Wort aus dem Wörterbuch."""
        selection = self.word_listbox.curselection()

        if not selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie ein Wort aus")
            return

        word = self.word_listbox.get(selection[0])

        if messagebox.askyesno(
            "Bestätigung", f"Möchten Sie das Wort '{word}' wirklich entfernen?"
        ):
            try:
                if self.dictionary.remove_word(word):
                    self.refresh_word_list()
                    self.status_label.config(text=f"Wort '{word}' erfolgreich entfernt")
                    messagebox.showinfo(
                        "Erfolg", f"Wort '{word}' wurde erfolgreich entfernt"
                    )
                else:
                    messagebox.showerror(
                        "Fehler", f"Fehler beim Entfernen des Wortes '{word}'"
                    )

            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Entfernen des Wortes: {e}")

    def clear_dictionary(self):
        """Leert das gesamte Wörterbuch."""
        if messagebox.askyesno(
            "Bestätigung",
            "Möchten Sie wirklich alle Wörter aus dem Wörterbuch entfernen?\n\nDiese Aktion kann nicht rückgängig gemacht werden!",
        ):
            try:
                if self.dictionary.clear_dictionary():
                    self.refresh_word_list()
                    self.status_label.config(text="Wörterbuch erfolgreich geleert")
                    messagebox.showinfo(
                        "Erfolg", "Das Wörterbuch wurde erfolgreich geleert"
                    )
                else:
                    messagebox.showerror("Fehler", "Fehler beim Leeren des Wörterbuchs")

            except Exception as e:
                messagebox.showerror(
                    "Fehler", f"Fehler beim Leeren des Wörterbuchs: {e}"
                )

    def import_words(self):
        """Importiert Wörter aus einer Datei."""
        file_path = filedialog.askopenfilename(
            title="Wörter importieren",
            filetypes=[("Textdateien", "*.txt"), ("Alle Dateien", "*.*")],
        )

        if not file_path:
            return

        try:
            with open(file_path, encoding="utf-8") as f:
                words = [line.strip() for line in f if line.strip()]

            if not words:
                messagebox.showwarning(
                    "Warnung", "Die ausgewählte Datei enthält keine Wörter"
                )
                return

            imported = self.dictionary.import_words(words)
            self.refresh_word_list()

            self.status_label.config(
                text=f"{imported} von {len(words)} Wörtern importiert"
            )
            messagebox.showinfo(
                "Import abgeschlossen",
                f"{imported} von {len(words)} Wörtern wurden erfolgreich importiert",
            )

        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Importieren: {e}")

    def export_words(self):
        """Exportiert alle Wörter in eine Datei."""
        file_path = filedialog.asksaveasfilename(
            title="Wörter exportieren",
            defaultextension=".txt",
            filetypes=[("Textdateien", "*.txt"), ("Alle Dateien", "*.*")],
        )

        if not file_path:
            return

        try:
            words = self.dictionary.export_words()

            with open(file_path, "w", encoding="utf-8") as f:
                for word in words:
                    f.write(word + "\n")

            self.status_label.config(text=f"{len(words)} Wörter exportiert")
            messagebox.showinfo(
                "Export abgeschlossen",
                f"{len(words)} Wörter wurden erfolgreich nach '{file_path}' exportiert",
            )

        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Exportieren: {e}")

    def run(self):
        """Startet die GUI."""
        self.root.mainloop()


def main():
    """Hauptfunktion für die GUI."""
    root = tk.Tk()
    app = DictionaryGUI(root)
    app.run()


if __name__ == "__main__":
    main()
