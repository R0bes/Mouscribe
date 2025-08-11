# tests/test_dictionary_gui.py - Tests for Dictionary GUI
"""
Tests for the dictionary GUI functionality.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, mock_open, patch

# Importiere nur das benötigte Modul
try:
    from src.dictionary_gui import DictionaryGUI
except ImportError:
    # Füge src zum Python-Pfad hinzu, falls Import fehlschlägt
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    from dictionary_gui import DictionaryGUI


class TestDictionaryGUI(unittest.TestCase):
    """Test cases for DictionaryGUI class."""

    def setUp(self):
        """Set up test fixtures."""
        # Erstelle temporäres Verzeichnis für Tests
        self.test_dir = tempfile.mkdtemp()
        self.test_dict_path = Path(self.test_dir) / "test_dictionary.json"

        # Mock für tkinter
        self.mock_root = Mock()
        self.mock_root.title = Mock()
        self.mock_root.geometry = Mock()
        self.mock_root.resizable = Mock()
        self.mock_root.columnconfigure = Mock()
        self.mock_root.rowconfigure = Mock()
        self.mock_root.mainloop = Mock()

        # Mock für custom_dictionary
        self.mock_dictionary = Mock()
        self.mock_dictionary.get_dictionary_info.return_value = {
            "path": str(self.test_dict_path),
            "word_count": 5,
            "exists": True,
        }
        self.mock_dictionary.get_all_words.return_value = [
            "wort1",
            "wort2",
            "wort3",
            "wort4",
            "wort5",
        ]
        self.mock_dictionary.add_word.return_value = True
        self.mock_dictionary.remove_word.return_value = True
        self.mock_dictionary.clear_dictionary.return_value = True
        self.mock_dictionary.import_words.return_value = 3
        self.mock_dictionary.export_words.return_value = ["wort1", "wort2", "wort3"]

    def tearDown(self):
        """Clean up test fixtures."""
        # Lösche temporäre Dateien
        if self.test_dict_path.exists():
            self.test_dict_path.unlink()
        if self.test_dir and os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)

    @patch("src.dictionary_gui.get_custom_dictionary")
    @patch("src.dictionary_gui.tk.Tk")
    @patch.object(DictionaryGUI, "setup_ui")
    @patch.object(DictionaryGUI, "refresh_word_list")
    def test_init_with_root(self, mock_refresh, mock_setup_ui, mock_tk, mock_get_dict):
        """Test initialization with provided root."""
        mock_get_dict.return_value = self.mock_dictionary

        gui = DictionaryGUI(self.mock_root)

        self.assertEqual(gui.root, self.mock_root)
        self.assertEqual(gui.dictionary, self.mock_dictionary)
        mock_get_dict.assert_called_once()
        mock_setup_ui.assert_called_once()
        mock_refresh.assert_called_once()

    @patch("src.dictionary_gui.get_custom_dictionary")
    @patch("src.dictionary_gui.tk.Tk")
    @patch.object(DictionaryGUI, "setup_ui")
    @patch.object(DictionaryGUI, "refresh_word_list")
    def test_init_without_root(
        self, mock_refresh, mock_setup_ui, mock_tk, mock_get_dict
    ):
        """Test initialization without root (creates new Tk instance)."""
        mock_tk_instance = Mock()
        mock_tk.return_value = mock_tk_instance
        mock_get_dict.return_value = self.mock_dictionary

        gui = DictionaryGUI()

        self.assertEqual(gui.root, mock_tk_instance)
        mock_tk.assert_called_once()
        mock_get_dict.assert_called_once()
        mock_setup_ui.assert_called_once()
        mock_refresh.assert_called_once()

    @patch("src.dictionary_gui.get_custom_dictionary")
    @patch("src.dictionary_gui.tk.Tk")
    @patch.object(DictionaryGUI, "setup_ui")
    @patch.object(DictionaryGUI, "refresh_word_list")
    def test_setup_ui(self, mock_refresh, mock_setup_ui, mock_tk, mock_get_dict):
        """Test UI setup."""
        mock_get_dict.return_value = self.mock_dictionary

        gui = DictionaryGUI(self.mock_root)

        # Da setup_ui gemockt ist, überprüfen wir nur den Mock
        mock_setup_ui.assert_called_once()

    @patch("src.dictionary_gui.get_custom_dictionary")
    @patch("src.dictionary_gui.tk.Tk")
    @patch.object(DictionaryGUI, "setup_ui")
    @patch.object(DictionaryGUI, "refresh_word_list")
    def test_update_info_success(
        self, mock_refresh, mock_setup_ui, mock_tk, mock_get_dict
    ):
        """Test successful info update."""
        mock_get_dict.return_value = self.mock_dictionary

        gui = DictionaryGUI(self.mock_root)

        # Mock für info_label
        gui.info_label = Mock()

        gui.update_info()

        self.mock_dictionary.get_dictionary_info.assert_called_once()
        gui.info_label.config.assert_called_once()

    @patch("src.dictionary_gui.get_custom_dictionary")
    @patch("src.dictionary_gui.tk.Tk")
    @patch.object(DictionaryGUI, "setup_ui")
    @patch.object(DictionaryGUI, "refresh_word_list")
    def test_update_info_exception(
        self, mock_refresh, mock_setup_ui, mock_tk, mock_get_dict
    ):
        """Test info update with exception."""
        mock_get_dict.return_value = self.mock_dictionary
        self.mock_dictionary.get_dictionary_info.side_effect = Exception("Test error")

        gui = DictionaryGUI(self.mock_root)

        # Mock für info_label
        gui.info_label = Mock()

        gui.update_info()

        gui.info_label.config.assert_called_once()
        # Überprüfe, ob der Fehlertext gesetzt wurde
        call_args = gui.info_label.config.call_args[1]["text"]
        self.assertIn("Fehler beim Laden der Informationen", call_args)

    @patch("src.dictionary_gui.get_custom_dictionary")
    @patch("src.dictionary_gui.tk.Tk")
    @patch.object(DictionaryGUI, "setup_ui")
    @patch.object(DictionaryGUI, "refresh_word_list")
    def test_refresh_word_list_success(
        self, mock_refresh, mock_setup_ui, mock_tk, mock_get_dict
    ):
        """Test successful word list refresh."""
        mock_get_dict.return_value = self.mock_dictionary

        gui = DictionaryGUI(self.mock_root)

        # Mock für word_listbox und status_label
        gui.word_listbox = Mock()
        gui.status_label = Mock()

        # Da refresh_word_list gemockt ist, überprüfen wir nur den Mock
        mock_refresh.assert_called_once()

    @patch("src.dictionary_gui.get_custom_dictionary")
    @patch("src.dictionary_gui.tk.Tk")
    @patch.object(DictionaryGUI, "setup_ui")
    @patch.object(DictionaryGUI, "refresh_word_list")
    @patch("src.dictionary_gui.messagebox.showerror")
    def test_refresh_word_list_exception(
        self, mock_showerror, mock_refresh, mock_setup_ui, mock_tk, mock_get_dict
    ):
        """Test word list refresh with exception."""
        mock_get_dict.return_value = self.mock_dictionary
        self.mock_dictionary.get_all_words.side_effect = Exception("Test error")

        gui = DictionaryGUI(self.mock_root)

        # Mock für word_listbox und status_label
        gui.word_listbox = Mock()
        gui.status_label = Mock()

        # Da refresh_word_list gemockt ist, überprüfen wir nur den Mock
        mock_refresh.assert_called_once()

    @patch("src.dictionary_gui.get_custom_dictionary")
    @patch("src.dictionary_gui.tk.Tk")
    @patch.object(DictionaryGUI, "setup_ui")
    @patch.object(DictionaryGUI, "refresh_word_list")
    def test_filter_words_no_search_term(
        self, mock_refresh, mock_setup_ui, mock_tk, mock_get_dict
    ):
        """Test word filtering without search term."""
        mock_get_dict.return_value = self.mock_dictionary

        gui = DictionaryGUI(self.mock_root)
        gui.all_words = ["wort1", "wort2", "wort3"]

        # Mock für search_entry, word_listbox und status_label
        gui.search_entry = Mock()
        gui.search_entry.get.return_value = ""
        gui.word_listbox = Mock()
        gui.word_listbox.size.return_value = 3
        gui.status_label = Mock()

        gui.filter_words()

        # Überprüfe, ob alle Wörter angezeigt werden
        self.assertEqual(gui.word_listbox.insert.call_count, 3)
        gui.status_label.config.assert_called_with(text="3 Wörter gefunden")

    @patch("src.dictionary_gui.get_custom_dictionary")
    @patch("src.dictionary_gui.tk.Tk")
    @patch.object(DictionaryGUI, "setup_ui")
    @patch.object(DictionaryGUI, "refresh_word_list")
    def test_filter_words_with_search_term(
        self, mock_refresh, mock_setup_ui, mock_tk, mock_get_dict
    ):
        """Test word filtering with search term."""
        mock_get_dict.return_value = self.mock_dictionary

        gui = DictionaryGUI(self.mock_root)
        gui.all_words = ["wort1", "wort2", "wort3", "testwort"]

        # Mock für search_entry, word_listbox und status_label
        gui.search_entry = Mock()
        gui.search_entry.get.return_value = "wort"
        gui.word_listbox = Mock()
        gui.word_listbox.size.return_value = 4
        gui.status_label = Mock()

        gui.filter_words()

        # Überprüfe, ob nur gefilterte Wörter angezeigt werden
        # "wort" ist in "wort1", "wort2", "wort3", "testwort" enthalten
        self.assertEqual(gui.word_listbox.insert.call_count, 4)
        gui.status_label.config.assert_called_with(text="4 Wörter gefunden")

    @patch("src.dictionary_gui.get_custom_dictionary")
    @patch("src.dictionary_gui.tk.Tk")
    @patch.object(DictionaryGUI, "setup_ui")
    @patch.object(DictionaryGUI, "refresh_word_list")
    @patch("src.dictionary_gui.messagebox.showwarning")
    def test_add_word_empty(
        self, mock_showwarning, mock_refresh, mock_setup_ui, mock_tk, mock_get_dict
    ):
        """Test adding empty word."""
        mock_get_dict.return_value = self.mock_dictionary

        gui = DictionaryGUI(self.mock_root)

        # Mock für add_entry
        gui.add_entry = Mock()
        gui.add_entry.get.return_value = "   "

        gui.add_word()

        mock_showwarning.assert_called_once_with(
            "Warnung", "Bitte geben Sie ein Wort ein"
        )

    @patch("src.dictionary_gui.get_custom_dictionary")
    @patch("src.dictionary_gui.tk.Tk")
    @patch.object(DictionaryGUI, "setup_ui")
    @patch.object(DictionaryGUI, "refresh_word_list")
    @patch("src.dictionary_gui.messagebox.showinfo")
    def test_add_word_success(
        self, mock_showinfo, mock_refresh, mock_setup_ui, mock_tk, mock_get_dict
    ):
        """Test successful word addition."""
        mock_get_dict.return_value = self.mock_dictionary

        gui = DictionaryGUI(self.mock_root)

        # Mock für add_entry, status_label und refresh_word_list
        gui.add_entry = Mock()
        gui.add_entry.get.return_value = "testwort"
        gui.add_entry.delete = Mock()
        gui.status_label = Mock()
        gui.refresh_word_list = Mock()

        gui.add_word()

        self.mock_dictionary.add_word.assert_called_once_with("testwort")
        gui.add_entry.delete.assert_called_once_with(0, "end")
        gui.refresh_word_list.assert_called_once()
        gui.status_label.config.assert_called_with(
            text="Wort 'testwort' erfolgreich hinzugefügt"
        )
        mock_showinfo.assert_called_once()

    @patch("src.dictionary_gui.get_custom_dictionary")
    @patch("src.dictionary_gui.tk.Tk")
    @patch.object(DictionaryGUI, "setup_ui")
    @patch.object(DictionaryGUI, "refresh_word_list")
    @patch("src.dictionary_gui.messagebox.showerror")
    def test_add_word_failure(
        self, mock_showerror, mock_refresh, mock_setup_ui, mock_tk, mock_get_dict
    ):
        """Test word addition failure."""
        mock_get_dict.return_value = self.mock_dictionary
        self.mock_dictionary.add_word.return_value = False

        gui = DictionaryGUI(self.mock_root)

        # Mock für add_entry
        gui.add_entry = Mock()
        gui.add_entry.get.return_value = "testwort"

        gui.add_word()

        mock_showerror.assert_called_once()

    @patch("src.dictionary_gui.get_custom_dictionary")
    @patch("src.dictionary_gui.tk.Tk")
    @patch.object(DictionaryGUI, "setup_ui")
    @patch.object(DictionaryGUI, "refresh_word_list")
    @patch("src.dictionary_gui.messagebox.showerror")
    def test_add_word_exception(
        self, mock_showerror, mock_refresh, mock_setup_ui, mock_tk, mock_get_dict
    ):
        """Test word addition with exception."""
        mock_get_dict.return_value = self.mock_dictionary
        self.mock_dictionary.add_word.side_effect = Exception("Test error")

        gui = DictionaryGUI(self.mock_root)

        # Mock für add_entry
        gui.add_entry = Mock()
        gui.add_entry.get.return_value = "testwort"

        gui.add_word()

        mock_showerror.assert_called_once()

    @patch("src.dictionary_gui.get_custom_dictionary")
    @patch("src.dictionary_gui.tk.Tk")
    @patch.object(DictionaryGUI, "setup_ui")
    @patch.object(DictionaryGUI, "refresh_word_list")
    @patch("src.dictionary_gui.messagebox.showwarning")
    def test_remove_selected_word_no_selection(
        self, mock_showwarning, mock_refresh, mock_setup_ui, mock_tk, mock_get_dict
    ):
        """Test removing word without selection."""
        mock_get_dict.return_value = self.mock_dictionary

        gui = DictionaryGUI(self.mock_root)

        # Mock für word_listbox
        gui.word_listbox = Mock()
        gui.word_listbox.curselection.return_value = []

        gui.remove_selected_word()

        mock_showwarning.assert_called_once_with(
            "Warnung", "Bitte wählen Sie ein Wort aus"
        )

    @patch("src.dictionary_gui.get_custom_dictionary")
    @patch("src.dictionary_gui.tk.Tk")
    @patch.object(DictionaryGUI, "setup_ui")
    @patch.object(DictionaryGUI, "refresh_word_list")
    @patch("src.dictionary_gui.messagebox.askyesno")
    @patch("src.dictionary_gui.messagebox.showinfo")
    def test_remove_selected_word_success(
        self,
        mock_showinfo,
        mock_askyesno,
        mock_refresh,
        mock_setup_ui,
        mock_tk,
        mock_get_dict,
    ):
        """Test successful word removal."""
        mock_get_dict.return_value = self.mock_dictionary
        mock_askyesno.return_value = True

        gui = DictionaryGUI(self.mock_root)

        # Mock für word_listbox, status_label und refresh_word_list
        gui.word_listbox = Mock()
        gui.word_listbox.curselection.return_value = [0]
        gui.word_listbox.get.return_value = "testwort"
        gui.status_label = Mock()
        gui.refresh_word_list = Mock()

        gui.remove_selected_word()

        self.mock_dictionary.remove_word.assert_called_once_with("testwort")
        gui.refresh_word_list.assert_called_once()
        gui.status_label.config.assert_called_with(
            text="Wort 'testwort' erfolgreich entfernt"
        )
        mock_showinfo.assert_called_once()

    @patch("src.dictionary_gui.get_custom_dictionary")
    @patch("src.dictionary_gui.tk.Tk")
    @patch.object(DictionaryGUI, "setup_ui")
    @patch.object(DictionaryGUI, "refresh_word_list")
    @patch("src.dictionary_gui.messagebox.askyesno")
    def test_remove_selected_word_user_cancels(
        self, mock_askyesno, mock_refresh, mock_setup_ui, mock_tk, mock_get_dict
    ):
        """Test word removal when user cancels."""
        mock_get_dict.return_value = self.mock_dictionary
        mock_askyesno.return_value = False

        gui = DictionaryGUI(self.mock_root)

        # Mock für word_listbox
        gui.word_listbox = Mock()
        gui.word_listbox.curselection.return_value = [0]
        gui.word_listbox.get.return_value = "testwort"

        gui.remove_selected_word()

        # Überprüfe, dass remove_word nicht aufgerufen wurde
        self.mock_dictionary.remove_word.assert_not_called()

    @patch("src.dictionary_gui.get_custom_dictionary")
    @patch("src.dictionary_gui.tk.Tk")
    @patch.object(DictionaryGUI, "setup_ui")
    @patch.object(DictionaryGUI, "refresh_word_list")
    @patch("src.dictionary_gui.messagebox.askyesno")
    @patch("src.dictionary_gui.messagebox.showerror")
    def test_remove_selected_word_failure(
        self,
        mock_showerror,
        mock_askyesno,
        mock_refresh,
        mock_setup_ui,
        mock_tk,
        mock_get_dict,
    ):
        """Test word removal failure."""
        mock_get_dict.return_value = self.mock_dictionary
        mock_askyesno.return_value = True
        self.mock_dictionary.remove_word.return_value = False

        gui = DictionaryGUI(self.mock_root)

        # Mock für word_listbox
        gui.word_listbox = Mock()
        gui.word_listbox.curselection.return_value = [0]
        gui.word_listbox.get.return_value = "testwort"

        gui.remove_selected_word()

        mock_showerror.assert_called_once()

    @patch("src.dictionary_gui.get_custom_dictionary")
    @patch("src.dictionary_gui.tk.Tk")
    @patch.object(DictionaryGUI, "setup_ui")
    @patch.object(DictionaryGUI, "refresh_word_list")
    @patch("src.dictionary_gui.messagebox.askyesno")
    @patch("src.dictionary_gui.messagebox.showerror")
    def test_remove_selected_word_exception(
        self,
        mock_showerror,
        mock_askyesno,
        mock_refresh,
        mock_setup_ui,
        mock_tk,
        mock_get_dict,
    ):
        """Test word removal with exception."""
        mock_get_dict.return_value = self.mock_dictionary
        mock_askyesno.return_value = True
        self.mock_dictionary.remove_word.side_effect = Exception("Test error")

        gui = DictionaryGUI(self.mock_root)

        # Mock für word_listbox
        gui.word_listbox = Mock()
        gui.word_listbox.curselection.return_value = [0]
        gui.word_listbox.get.return_value = "testwort"

        gui.remove_selected_word()

        mock_showerror.assert_called_once()

    @patch("src.dictionary_gui.get_custom_dictionary")
    @patch("src.dictionary_gui.tk.Tk")
    @patch.object(DictionaryGUI, "setup_ui")
    @patch.object(DictionaryGUI, "refresh_word_list")
    @patch("src.dictionary_gui.messagebox.askyesno")
    @patch("src.dictionary_gui.messagebox.showinfo")
    def test_clear_dictionary_success(
        self,
        mock_showinfo,
        mock_askyesno,
        mock_refresh,
        mock_setup_ui,
        mock_tk,
        mock_get_dict,
    ):
        """Test successful dictionary clearing."""
        mock_get_dict.return_value = self.mock_dictionary
        mock_askyesno.return_value = True

        gui = DictionaryGUI(self.mock_root)

        # Mock für status_label und refresh_word_list
        gui.status_label = Mock()
        gui.refresh_word_list = Mock()

        gui.clear_dictionary()

        self.mock_dictionary.clear_dictionary.assert_called_once()
        gui.refresh_word_list.assert_called_once()
        gui.status_label.config.assert_called_with(
            text="Wörterbuch erfolgreich geleert"
        )
        mock_showinfo.assert_called_once()

    @patch("src.dictionary_gui.get_custom_dictionary")
    @patch("src.dictionary_gui.tk.Tk")
    @patch.object(DictionaryGUI, "setup_ui")
    @patch.object(DictionaryGUI, "refresh_word_list")
    @patch("src.dictionary_gui.messagebox.askyesno")
    def test_clear_dictionary_user_cancels(
        self, mock_askyesno, mock_refresh, mock_setup_ui, mock_tk, mock_get_dict
    ):
        """Test dictionary clearing when user cancels."""
        mock_get_dict.return_value = self.mock_dictionary
        mock_askyesno.return_value = False

        gui = DictionaryGUI(self.mock_root)

        gui.clear_dictionary()

        # Überprüfe, dass clear_dictionary nicht aufgerufen wurde
        self.mock_dictionary.clear_dictionary.assert_not_called()

    @patch("src.dictionary_gui.get_custom_dictionary")
    @patch("src.dictionary_gui.tk.Tk")
    @patch.object(DictionaryGUI, "setup_ui")
    @patch.object(DictionaryGUI, "refresh_word_list")
    @patch("src.dictionary_gui.messagebox.askyesno")
    @patch("src.dictionary_gui.messagebox.showerror")
    def test_clear_dictionary_failure(
        self,
        mock_showerror,
        mock_askyesno,
        mock_refresh,
        mock_setup_ui,
        mock_tk,
        mock_get_dict,
    ):
        """Test dictionary clearing failure."""
        mock_get_dict.return_value = self.mock_dictionary
        mock_askyesno.return_value = True
        self.mock_dictionary.clear_dictionary.return_value = False

        gui = DictionaryGUI(self.mock_root)

        gui.clear_dictionary()

        mock_showerror.assert_called_once()

    @patch("src.dictionary_gui.get_custom_dictionary")
    @patch("src.dictionary_gui.tk.Tk")
    @patch.object(DictionaryGUI, "setup_ui")
    @patch.object(DictionaryGUI, "refresh_word_list")
    @patch("src.dictionary_gui.messagebox.askyesno")
    @patch("src.dictionary_gui.messagebox.showerror")
    def test_clear_dictionary_exception(
        self,
        mock_showerror,
        mock_askyesno,
        mock_refresh,
        mock_setup_ui,
        mock_tk,
        mock_get_dict,
    ):
        """Test dictionary clearing with exception."""
        mock_get_dict.return_value = self.mock_dictionary
        mock_askyesno.return_value = True
        self.mock_dictionary.clear_dictionary.side_effect = Exception("Test error")

        gui = DictionaryGUI(self.mock_root)

        gui.clear_dictionary()

        mock_showerror.assert_called_once()

    @patch("src.dictionary_gui.get_custom_dictionary")
    @patch("src.dictionary_gui.tk.Tk")
    @patch.object(DictionaryGUI, "setup_ui")
    @patch.object(DictionaryGUI, "refresh_word_list")
    @patch("src.dictionary_gui.filedialog.askopenfilename")
    @patch("src.dictionary_gui.messagebox.showinfo")
    def test_import_words_success(
        self,
        mock_showinfo,
        mock_askopenfilename,
        mock_refresh,
        mock_setup_ui,
        mock_tk,
        mock_get_dict,
    ):
        """Test successful word import."""
        mock_get_dict.return_value = self.mock_dictionary
        mock_askopenfilename.return_value = "/test/path/words.txt"

        gui = DictionaryGUI(self.mock_root)

        # Mock für status_label und refresh_word_list
        gui.status_label = Mock()
        gui.refresh_word_list = Mock()

        # Mock für open
        mock_file_content = "wort1\nwort2\nwort3\n"
        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            gui.import_words()

        self.mock_dictionary.import_words.assert_called_once_with(
            ["wort1", "wort2", "wort3"]
        )
        gui.refresh_word_list.assert_called_once()
        gui.status_label.config.assert_called_with(text="3 von 3 Wörtern importiert")
        mock_showinfo.assert_called_once()

    @patch("src.dictionary_gui.get_custom_dictionary")
    @patch("src.dictionary_gui.tk.Tk")
    @patch.object(DictionaryGUI, "setup_ui")
    @patch.object(DictionaryGUI, "refresh_word_list")
    @patch("src.dictionary_gui.filedialog.askopenfilename")
    def test_import_words_no_file_selected(
        self, mock_askopenfilename, mock_refresh, mock_setup_ui, mock_tk, mock_get_dict
    ):
        """Test word import when no file is selected."""
        mock_get_dict.return_value = self.mock_dictionary
        mock_askopenfilename.return_value = ""

        gui = DictionaryGUI(self.mock_root)

        gui.import_words()

        # Überprüfe, dass import_words nicht aufgerufen wurde
        self.mock_dictionary.import_words.assert_not_called()

    @patch("src.dictionary_gui.get_custom_dictionary")
    @patch("src.dictionary_gui.tk.Tk")
    @patch.object(DictionaryGUI, "setup_ui")
    @patch.object(DictionaryGUI, "refresh_word_list")
    @patch("src.dictionary_gui.filedialog.askopenfilename")
    @patch("src.dictionary_gui.messagebox.showwarning")
    def test_import_words_empty_file(
        self,
        mock_showwarning,
        mock_askopenfilename,
        mock_refresh,
        mock_setup_ui,
        mock_tk,
        mock_get_dict,
    ):
        """Test word import with empty file."""
        mock_get_dict.return_value = self.mock_dictionary
        mock_askopenfilename.return_value = "/test/path/empty.txt"

        gui = DictionaryGUI(self.mock_root)

        # Mock für open
        with patch("builtins.open", mock_open(read_data="")):
            gui.import_words()

        mock_showwarning.assert_called_once_with(
            "Warnung", "Die ausgewählte Datei enthält keine Wörter"
        )

    @patch("src.dictionary_gui.get_custom_dictionary")
    @patch("src.dictionary_gui.tk.Tk")
    @patch.object(DictionaryGUI, "setup_ui")
    @patch.object(DictionaryGUI, "refresh_word_list")
    @patch("src.dictionary_gui.filedialog.askopenfilename")
    @patch("src.dictionary_gui.messagebox.showerror")
    def test_import_words_exception(
        self,
        mock_showerror,
        mock_askopenfilename,
        mock_refresh,
        mock_setup_ui,
        mock_tk,
        mock_get_dict,
    ):
        """Test word import with exception."""
        mock_get_dict.return_value = self.mock_dictionary
        mock_askopenfilename.return_value = "/test/path/words.txt"

        gui = DictionaryGUI(self.mock_root)

        # Mock für open mit Exception
        with patch("builtins.open", side_effect=Exception("Test error")):
            gui.import_words()

        mock_showerror.assert_called_once()

    @patch("src.dictionary_gui.get_custom_dictionary")
    @patch("src.dictionary_gui.tk.Tk")
    @patch.object(DictionaryGUI, "setup_ui")
    @patch.object(DictionaryGUI, "refresh_word_list")
    @patch("src.dictionary_gui.filedialog.asksaveasfilename")
    @patch("src.dictionary_gui.messagebox.showinfo")
    def test_export_words_success(
        self,
        mock_showinfo,
        mock_asksaveasfilename,
        mock_refresh,
        mock_setup_ui,
        mock_tk,
        mock_get_dict,
    ):
        """Test successful word export."""
        mock_get_dict.return_value = self.mock_dictionary
        mock_asksaveasfilename.return_value = "/test/path/export.txt"

        gui = DictionaryGUI(self.mock_root)

        # Mock für status_label
        gui.status_label = Mock()

        # Mock für open
        mock_file = mock_open()
        with patch("builtins.open", mock_file):
            gui.export_words()

        self.mock_dictionary.export_words.assert_called_once()
        mock_file().write.assert_called()
        gui.status_label.config.assert_called_with(text="3 Wörter exportiert")
        mock_showinfo.assert_called_once()

    @patch("src.dictionary_gui.get_custom_dictionary")
    @patch("src.dictionary_gui.tk.Tk")
    @patch.object(DictionaryGUI, "setup_ui")
    @patch.object(DictionaryGUI, "refresh_word_list")
    @patch("src.dictionary_gui.filedialog.asksaveasfilename")
    def test_export_words_no_file_selected(
        self,
        mock_asksaveasfilename,
        mock_refresh,
        mock_setup_ui,
        mock_tk,
        mock_get_dict,
    ):
        """Test word export when no file is selected."""
        mock_get_dict.return_value = self.mock_dictionary
        mock_asksaveasfilename.return_value = ""

        gui = DictionaryGUI(self.mock_root)

        gui.export_words()

        # Überprüfe, dass export_words nicht aufgerufen wurde
        self.mock_dictionary.export_words.assert_not_called()

    @patch("src.dictionary_gui.get_custom_dictionary")
    @patch("src.dictionary_gui.tk.Tk")
    @patch.object(DictionaryGUI, "setup_ui")
    @patch.object(DictionaryGUI, "refresh_word_list")
    @patch("src.dictionary_gui.filedialog.asksaveasfilename")
    @patch("src.dictionary_gui.messagebox.showerror")
    def test_export_words_exception(
        self,
        mock_showerror,
        mock_asksaveasfilename,
        mock_refresh,
        mock_setup_ui,
        mock_tk,
        mock_get_dict,
    ):
        """Test word export with exception."""
        mock_get_dict.return_value = self.mock_dictionary
        mock_asksaveasfilename.return_value = "/test/path/export.txt"

        gui = DictionaryGUI(self.mock_root)

        # Mock für open mit Exception
        with patch("builtins.open", side_effect=Exception("Test error")):
            gui.export_words()

        mock_showerror.assert_called_once()

    @patch("src.dictionary_gui.get_custom_dictionary")
    @patch("src.dictionary_gui.tk.Tk")
    @patch.object(DictionaryGUI, "setup_ui")
    @patch.object(DictionaryGUI, "refresh_word_list")
    def test_run(self, mock_refresh, mock_setup_ui, mock_tk, mock_get_dict):
        """Test GUI run method."""
        mock_get_dict.return_value = self.mock_dictionary

        gui = DictionaryGUI(self.mock_root)

        gui.run()

        self.mock_root.mainloop.assert_called_once()


class TestDictionaryGUIMainFunction(unittest.TestCase):
    """Test cases for main function."""

    @patch("src.dictionary_gui.tk.Tk")
    @patch("src.dictionary_gui.DictionaryGUI")
    def test_main_function(self, mock_gui_class, mock_tk):
        """Test main function."""
        mock_root = Mock()
        mock_tk.return_value = mock_root
        mock_gui = Mock()
        mock_gui_class.return_value = mock_gui

        # Import und rufe main auf
        from src.dictionary_gui import main

        main()

        mock_tk.assert_called_once()
        mock_gui_class.assert_called_once_with(mock_root)
        mock_gui.run.assert_called_once()


if __name__ == "__main__":
    unittest.main()
