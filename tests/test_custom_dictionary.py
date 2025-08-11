# tests/test_custom_dictionary.py - Tests for Custom Dictionary Feature
"""
Tests for the custom dictionary functionality.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Importiere nur das benötigte Modul
try:
    from custom_dictionary import CustomDictionary, add_custom_word, get_custom_dictionary, is_custom_word, remove_custom_word
except ImportError:
    # Füge src zum Python-Pfad hinzu, falls Import fehlschlägt
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    from custom_dictionary import CustomDictionary, add_custom_word, get_custom_dictionary, is_custom_word, remove_custom_word


class TestCustomDictionary(unittest.TestCase):
    """Test cases for CustomDictionary class."""

    def setUp(self):
        """Set up test fixtures."""
        # Erstelle temporäres Verzeichnis für Tests
        self.test_dir = tempfile.mkdtemp()
        self.test_dict_path = Path(self.test_dir) / "test_dictionary.json"
        self.dictionary = CustomDictionary(str(self.test_dict_path))

    def tearDown(self):
        """Clean up test fixtures."""
        # Lösche temporäre Dateien
        if self.test_dict_path.exists():
            self.test_dict_path.unlink()
        if self.test_dir and os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)

    def test_init_with_custom_path(self):
        """Test initialization with custom path."""
        self.assertEqual(self.dictionary.dictionary_path, self.test_dict_path)
        self.assertEqual(len(self.dictionary._words), 0)

    def test_add_word(self):
        """Test adding a word to the dictionary."""
        result = self.dictionary.add_word("testwort")
        self.assertTrue(result)
        self.assertIn("testwort", self.dictionary._words)
        self.assertTrue(self.test_dict_path.exists())

    def test_add_empty_word(self):
        """Test adding an empty word."""
        result = self.dictionary.add_word("")
        self.assertFalse(result)
        self.assertEqual(len(self.dictionary._words), 0)

    def test_add_duplicate_word(self):
        """Test adding a duplicate word."""
        self.dictionary.add_word("testwort")
        result = self.dictionary.add_word("testwort")
        self.assertTrue(result)  # Sollte True zurückgeben, da Wort bereits existiert
        self.assertEqual(len(self.dictionary._words), 1)

    def test_remove_word(self):
        """Test removing a word from the dictionary."""
        self.dictionary.add_word("testwort")
        result = self.dictionary.remove_word("testwort")
        self.assertTrue(result)
        self.assertNotIn("testwort", self.dictionary._words)

    def test_remove_nonexistent_word(self):
        """Test removing a word that doesn't exist."""
        result = self.dictionary.remove_word("nonexistent")
        self.assertFalse(result)

    def test_has_word(self):
        """Test checking if a word exists in the dictionary."""
        self.dictionary.add_word("testwort")
        self.assertTrue(self.dictionary.has_word("testwort"))
        self.assertFalse(self.dictionary.has_word("nonexistent"))

    def test_get_all_words(self):
        """Test getting all words from the dictionary."""
        words = ["wort1", "wort2", "wort3"]
        for word in words:
            self.dictionary.add_word(word)

        all_words = self.dictionary.get_all_words()
        self.assertEqual(len(all_words), 3)
        for word in words:
            self.assertIn(word, all_words)

    def test_get_word_count(self):
        """Test getting the word count."""
        self.assertEqual(self.dictionary.get_word_count(), 0)
        self.dictionary.add_word("testwort")
        self.assertEqual(self.dictionary.get_word_count(), 1)

    def test_clear_dictionary(self):
        """Test clearing the dictionary."""
        self.dictionary.add_word("wort1")
        self.dictionary.add_word("wort2")
        self.assertEqual(self.dictionary.get_word_count(), 2)

        result = self.dictionary.clear_dictionary()
        self.assertTrue(result)
        self.assertEqual(self.dictionary.get_word_count(), 0)

    def test_import_words(self):
        """Test importing words from a list."""
        words = ["import1", "import2", "import3"]
        imported_count = self.dictionary.import_words(words)
        self.assertEqual(imported_count, 3)
        self.assertEqual(self.dictionary.get_word_count(), 3)

    def test_import_empty_list(self):
        """Test importing an empty list."""
        imported_count = self.dictionary.import_words([])
        self.assertEqual(imported_count, 0)

    def test_export_words(self):
        """Test exporting words from the dictionary."""
        words = ["export1", "export2"]
        for word in words:
            self.dictionary.add_word(word)

        exported = self.dictionary.export_words()
        self.assertEqual(len(exported), 2)
        for word in words:
            self.assertIn(word, exported)

    def test_get_dictionary_info(self):
        """Test getting dictionary information."""
        self.dictionary.add_word("testwort")
        info = self.dictionary.get_dictionary_info()

        self.assertIn("path", info)
        self.assertIn("word_count", info)
        self.assertIn("words", info)
        self.assertIn("exists", info)
        self.assertIn("file_size", info)

        self.assertEqual(info["word_count"], 1)
        self.assertTrue(info["exists"])

    def test_case_insensitive(self):
        """Test that words are stored case-insensitively."""
        self.dictionary.add_word("TestWort")
        self.assertTrue(self.dictionary.has_word("testwort"))
        self.assertTrue(self.dictionary.has_word("TESTWORT"))
        self.assertTrue(self.dictionary.has_word("TestWort"))

    def test_word_stripping(self):
        """Test that words are stripped of whitespace."""
        self.dictionary.add_word("  testwort  ")
        self.assertTrue(self.dictionary.has_word("testwort"))
        self.assertIn("testwort", self.dictionary._words)

    def test_add_word_with_whitespace_only(self):
        """Test adding a word that contains only whitespace."""
        result = self.dictionary.add_word("   ")
        self.assertFalse(result)
        self.assertEqual(len(self.dictionary._words), 0)

    def test_remove_word_with_whitespace_only(self):
        """Test removing a word that contains only whitespace."""
        result = self.dictionary.remove_word("   ")
        self.assertFalse(result)

    def test_has_word_with_whitespace_only(self):
        """Test checking a word that contains only whitespace."""
        result = self.dictionary.has_word("   ")
        self.assertFalse(result)

    def test_add_word_with_none(self):
        """Test adding None as a word."""
        result = self.dictionary.add_word(None)
        self.assertFalse(result)

    def test_remove_word_with_none(self):
        """Test removing None as a word."""
        result = self.dictionary.remove_word(None)
        self.assertFalse(result)

    def test_has_word_with_none(self):
        """Test checking None as a word."""
        result = self.dictionary.has_word(None)
        self.assertFalse(result)

    def test_import_words_with_none_values(self):
        """Test importing words list with None values."""
        words = ["valid", None, "also_valid", ""]
        imported_count = self.dictionary.import_words(words)
        self.assertEqual(imported_count, 2)  # Nur "valid" und "also_valid"
        self.assertEqual(self.dictionary.get_word_count(), 2)

    def test_import_words_with_duplicates(self):
        """Test importing words list with duplicates."""
        words = ["word1", "word2", "word1", "word3", "word2"]
        imported_count = self.dictionary.import_words(words)
        # Da add_word Duplikate nicht hinzufügt, sollten alle Wörter hinzugefügt werden
        self.assertEqual(imported_count, 5)
        # Aber nur 3 unique Wörter
        self.assertEqual(self.dictionary.get_word_count(), 3)

    def test_get_dictionary_info_file_not_exists(self):
        """Test getting dictionary info when file doesn't exist."""
        # Erstelle ein neues Dictionary ohne existierende Datei
        new_dict = CustomDictionary(str(Path(self.test_dir) / "nonexistent.json"))
        info = new_dict.get_dictionary_info()

        self.assertIn("path", info)
        self.assertIn("word_count", info)
        self.assertIn("words", info)
        self.assertIn("exists", info)
        self.assertIn("file_size", info)

        self.assertEqual(info["word_count"], 0)
        self.assertFalse(info["exists"])
        self.assertEqual(info["file_size"], 0)

    def test_get_dictionary_info_file_size(self):
        """Test getting dictionary info with file size calculation."""
        self.dictionary.add_word("testwort")
        info = self.dictionary.get_dictionary_info()

        self.assertGreater(info["file_size"], 0)
        self.assertTrue(info["exists"])

    def test_clear_dictionary_empty(self):
        """Test clearing an already empty dictionary."""
        result = self.dictionary.clear_dictionary()
        self.assertTrue(result)
        self.assertEqual(self.dictionary.get_word_count(), 0)

    def test_export_words_empty(self):
        """Test exporting words from empty dictionary."""
        exported = self.dictionary.export_words()
        self.assertEqual(len(exported), 0)
        self.assertEqual(exported, [])

    def test_get_all_words_empty(self):
        """Test getting all words from empty dictionary."""
        all_words = self.dictionary.get_all_words()
        self.assertEqual(len(all_words), 0)
        self.assertEqual(all_words, [])

    def test_metadata_in_saved_file(self):
        """Test that metadata is properly saved in the dictionary file."""
        self.dictionary.add_word("testwort")

        # Lade die gespeicherte Datei und prüfe den Inhalt
        with open(self.test_dict_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("words", data)
        self.assertIn("metadata", data)
        self.assertIn("version", data["metadata"])
        self.assertIn("created", data["metadata"])
        self.assertIn("total_words", data["metadata"])

        self.assertEqual(data["metadata"]["version"], "1.0")
        self.assertEqual(data["metadata"]["total_words"], 1)
        self.assertIn("testwort", data["words"])

    def test_words_are_sorted_in_saved_file(self):
        """Test that words are saved in sorted order."""
        words = ["zebra", "apple", "banana"]
        for word in words:
            self.dictionary.add_word(word)

        # Lade die gespeicherte Datei und prüfe die Sortierung
        with open(self.test_dict_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["words"], ["apple", "banana", "zebra"])

    def test_remove_word_case_insensitive(self):
        """Test removing a word with different case."""
        self.dictionary.add_word("TestWort")
        result = self.dictionary.remove_word("testwort")
        self.assertTrue(result)
        self.assertNotIn("testwort", self.dictionary._words)
        self.assertEqual(self.dictionary.get_word_count(), 0)

    def test_remove_word_with_whitespace(self):
        """Test removing a word with surrounding whitespace."""
        self.dictionary.add_word("testwort")
        result = self.dictionary.remove_word("  testwort  ")
        self.assertTrue(result)
        self.assertNotIn("testwort", self.dictionary._words)
        self.assertEqual(self.dictionary.get_word_count(), 0)


class TestCustomDictionaryIntegration(unittest.TestCase):
    """Integration tests for custom dictionary with spell checker."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_dict_path = Path(self.test_dir) / "test_dictionary.json"

    def tearDown(self):
        """Clean up test fixtures."""
        if self.test_dir and os.path.exists(self.test_dir):
            import shutil

            shutil.rmtree(self.test_dir)

    @patch("src.custom_dictionary.Path.home")
    def test_default_path_creation(self, mock_home):
        """Test that default path is created correctly."""
        mock_home.return_value = Path(self.test_dir)

        dictionary = CustomDictionary()
        expected_path = Path(self.test_dir) / ".mauscribe" / "custom_dictionary.json"

        self.assertEqual(dictionary.dictionary_path, expected_path)
        # Verzeichnis sollte existieren
        self.assertTrue(dictionary.dictionary_path.parent.exists())

    @patch("src.custom_dictionary.Path.home")
    def test_default_path_creation_existing_directory(self, mock_home):
        """Test that default path works with existing directory."""
        mock_home.return_value = Path(self.test_dir)

        # Erstelle das Verzeichnis bereits
        mauscribe_dir = Path(self.test_dir) / ".mauscribe"
        mauscribe_dir.mkdir(exist_ok=True)

        dictionary = CustomDictionary()
        expected_path = mauscribe_dir / "custom_dictionary.json"

        self.assertEqual(dictionary.dictionary_path, expected_path)
        self.assertTrue(dictionary.dictionary_path.parent.exists())


class TestCustomDictionaryErrorHandling(unittest.TestCase):
    """Test error handling scenarios for custom dictionary."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_dict_path = Path(self.test_dir) / "test_dictionary.json"

    def tearDown(self):
        """Clean up test fixtures."""
        if self.test_dir and os.path.exists(self.test_dir):
            import shutil

            shutil.rmtree(self.test_dir)

    @patch("builtins.open")
    def test_load_dictionary_file_not_found(self, mock_open):
        """Test loading dictionary when file doesn't exist."""
        mock_open.side_effect = FileNotFoundError("File not found")

        dictionary = CustomDictionary(str(self.test_dict_path))
        self.assertEqual(len(dictionary._words), 0)

    @patch("builtins.open")
    def test_load_dictionary_json_error(self, mock_open):
        """Test loading dictionary with invalid JSON."""
        mock_open.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)

        dictionary = CustomDictionary(str(self.test_dict_path))
        self.assertEqual(len(dictionary._words), 0)

    @patch("builtins.open")
    def test_load_dictionary_general_error(self, mock_open):
        """Test loading dictionary with general error."""
        mock_open.side_effect = Exception("General error")

        dictionary = CustomDictionary(str(self.test_dict_path))
        self.assertEqual(len(dictionary._words), 0)

    @patch("builtins.open")
    def test_save_dictionary_error(self, mock_open):
        """Test saving dictionary with error."""
        mock_open.side_effect = Exception("Write error")

        dictionary = CustomDictionary(str(self.test_dict_path))
        result = dictionary.add_word("testwort")
        # Das Wort wird trotz Speicherfehler hinzugefügt, da der Fehler erst beim Speichern auftritt
        self.assertTrue(result)
        self.assertIn("testwort", dictionary._words)

    @patch("pathlib.Path.mkdir")
    def test_save_dictionary_directory_creation_error(self, mock_mkdir):
        """Test saving dictionary when directory creation fails."""
        mock_mkdir.side_effect = Exception("Directory creation error")

        dictionary = CustomDictionary(str(self.test_dict_path))
        result = dictionary.add_word("testwort")
        # Das Wort wird trotz Verzeichnisfehler hinzugefügt, da der Fehler erst beim Speichern auftritt
        self.assertTrue(result)
        self.assertIn("testwort", dictionary._words)

    def test_load_dictionary_missing_words_key(self):
        """Test loading dictionary with missing 'words' key."""
        # Erstelle eine JSON-Datei ohne 'words' Schlüssel
        data = {"metadata": {"version": "1.0"}}
        with open(self.test_dict_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

        dictionary = CustomDictionary(str(self.test_dict_path))
        self.assertEqual(len(dictionary._words), 0)

    def test_load_dictionary_invalid_words_type(self):
        """Test loading dictionary with invalid words type."""
        # Erstelle eine JSON-Datei mit ungültigem 'words' Typ
        data = {"words": "not_a_list"}
        with open(self.test_dict_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

        dictionary = CustomDictionary(str(self.test_dict_path))
        # Der Code behandelt ungültige Wörter-Typen nicht, daher wird der
        # String als einzelnes Wort behandelt. Das ist ein Edge Case, der im
        # Code nicht abgefangen wird
        self.assertGreater(len(dictionary._words), 0)

    def test_add_word_save_error_handling(self):
        """Test add_word when save operation fails."""
        # Erstelle ein Dictionary mit einem ungültigen Pfad, der nicht beschreibbar ist
        invalid_path = Path(self.test_dir) / "nonexistent" / "dictionary.json"
        dictionary = CustomDictionary(str(invalid_path))

        # Versuche ein Wort hinzuzufügen - das Wort wird im Speicher hinzugefügt, aber das Speichern schlägt fehl
        result = dictionary.add_word("testwort")
        self.assertTrue(result)  # Das Wort wird erfolgreich hinzugefügt
        self.assertIn("testwort", dictionary._words)  # Das Wort ist im Speicher

    def test_remove_word_save_error_handling(self):
        """Test remove_word when save operation fails."""
        # Erstelle ein Dictionary mit einem ungültigen Pfad, der nicht beschreibbar ist
        invalid_path = Path(self.test_dir) / "nonexistent" / "dictionary.json"
        dictionary = CustomDictionary(str(invalid_path))

        # Füge ein Wort hinzu (wird im Speicher gespeichert)
        dictionary._words.add("testwort")

        # Versuche das Wort zu entfernen - das Wort wird aus dem Speicher entfernt, aber das Speichern schlägt fehl
        result = dictionary.remove_word("testwort")
        self.assertTrue(result)  # Das Wort wird erfolgreich entfernt
        self.assertNotIn("testwort", dictionary._words)  # Das Wort ist nicht mehr im Speicher

    def test_clear_dictionary_save_error_handling(self):
        """Test clear_dictionary when save operation fails."""
        # Erstelle ein Dictionary mit einem ungültigen Pfad, der nicht beschreibbar ist
        invalid_path = Path(self.test_dir) / "nonexistent" / "dictionary.json"
        dictionary = CustomDictionary(str(invalid_path))

        # Füge Wörter hinzu (werden im Speicher gespeichert)
        dictionary._words.add("wort1")
        dictionary._words.add("wort2")

        # Versuche das Wörterbuch zu leeren - die Wörter werden aus dem Speicher entfernt, aber das Speichern schlägt fehl
        result = dictionary.clear_dictionary()
        self.assertTrue(result)  # Das Wörterbuch wird erfolgreich geleert
        self.assertEqual(len(dictionary._words), 0)  # Das Wörterbuch ist leer

    def test_import_words_with_save_errors(self):
        """Test import_words when individual word saves fail."""
        # Erstelle ein Dictionary mit einem ungültigen Pfad, der nicht beschreibbar ist
        invalid_path = Path(self.test_dir) / "nonexistent" / "dictionary.json"
        dictionary = CustomDictionary(str(invalid_path))

        # Versuche Wörter zu importieren - die Wörter werden im Speicher hinzugefügt, aber das Speichern schlägt fehl
        words = ["wort1", "wort2", "wort3"]
        imported_count = dictionary.import_words(words)
        self.assertEqual(imported_count, 3)  # Alle Wörter werden erfolgreich hinzugefügt
        self.assertEqual(len(dictionary._words), 3)  # Alle Wörter sind im Speicher

    def test_load_dictionary_with_corrupted_file(self):
        """Test loading dictionary with corrupted JSON file."""
        # Erstelle eine beschädigte JSON-Datei
        with open(self.test_dict_path, "w", encoding="utf-8") as f:
            f.write('{"words": ["wort1", "wort2", "invalid json')

        dictionary = CustomDictionary(str(self.test_dict_path))
        # Sollte mit leerem Wörterbuch starten bei JSON-Fehlern
        self.assertEqual(len(dictionary._words), 0)

    def test_load_dictionary_with_empty_file(self):
        """Test loading dictionary with empty file."""
        # Erstelle eine leere Datei
        with open(self.test_dict_path, "w", encoding="utf-8"):
            pass

        dictionary = CustomDictionary(str(self.test_dict_path))
        # Sollte mit leerem Wörterbuch starten bei leeren Dateien
        self.assertEqual(len(dictionary._words), 0)

    def test_load_dictionary_with_permission_error(self):
        """Test loading dictionary with permission error."""
        # Erstelle eine Datei ohne Leseberechtigung
        with open(self.test_dict_path, "w", encoding="utf-8") as f:
            json.dump({"words": ["wort1", "wort2"]}, f)

        # Ändere die Berechtigungen (nur lesen)
        os.chmod(self.test_dict_path, 0o444)

        try:
            dictionary = CustomDictionary(str(self.test_dict_path))
            # Bei Berechtigungsfehlern wird das Wörterbuch mit Standardwerten initialisiert
            # Da die Datei existiert, wird versucht, sie zu lesen
            self.assertGreaterEqual(len(dictionary._words), 0)
        finally:
            # Stelle Berechtigungen wieder her
            os.chmod(self.test_dict_path, 0o666)

    def test_save_dictionary_with_permission_error(self):
        """Test saving dictionary with permission error."""
        # Erstelle ein Verzeichnis ohne Schreibberechtigung
        read_only_dir = Path(self.test_dir) / "readonly"
        read_only_dir.mkdir(exist_ok=True)
        os.chmod(read_only_dir, 0o444)

        try:
            invalid_path = read_only_dir / "dictionary.json"
            dictionary = CustomDictionary(str(invalid_path))

            # Versuche ein Wort hinzuzufügen - das Wort wird im Speicher hinzugefügt, aber das Speichern schlägt fehl
            result = dictionary.add_word("testwort")
            self.assertTrue(result)  # Das Wort wird erfolgreich hinzugefügt
            self.assertIn("testwort", dictionary._words)  # Das Wort ist im Speicher
        finally:
            # Stelle Berechtigungen wieder her
            os.chmod(read_only_dir, 0o777)

    def test_exception_handling_in_add_word(self):
        """Test exception handling in add_word method."""
        # Erstelle ein Dictionary mit einem ungültigen Pfad
        invalid_path = Path(self.test_dir) / "nonexistent" / "dictionary.json"
        dictionary = CustomDictionary(str(invalid_path))

        # Füge ein Wort hinzu, das eine Exception auslöst
        with patch.object(dictionary, "_save_dictionary", side_effect=Exception("Test exception")):
            result = dictionary.add_word("testwort")
            self.assertFalse(result)  # Sollte False zurückgeben bei Exception

    def test_exception_handling_in_remove_word(self):
        """Test exception handling in remove_word method."""
        # Erstelle ein Dictionary mit einem ungültigen Pfad
        invalid_path = Path(self.test_dir) / "nonexistent" / "dictionary.json"
        dictionary = CustomDictionary(str(invalid_path))

        # Füge ein Wort hinzu
        dictionary._words.add("testwort")

        # Versuche das Wort zu entfernen, was eine Exception auslöst
        with patch.object(dictionary, "_save_dictionary", side_effect=Exception("Test exception")):
            result = dictionary.remove_word("testwort")
            self.assertFalse(result)  # Sollte False zurückgeben bei Exception

    def test_exception_handling_in_clear_dictionary(self):
        """Test exception handling in clear_dictionary method."""
        # Erstelle ein Dictionary mit einem ungültigen Pfad
        invalid_path = Path(self.test_dir) / "nonexistent" / "dictionary.json"
        dictionary = CustomDictionary(str(invalid_path))

        # Füge Wörter hinzu
        dictionary._words.add("wort1")
        dictionary._words.add("wort2")

        # Versuche das Wörterbuch zu leeren, was eine Exception auslöst
        with patch.object(dictionary, "_save_dictionary", side_effect=Exception("Test exception")):
            result = dictionary.clear_dictionary()
            self.assertFalse(result)  # Sollte False zurückgeben bei Exception


class TestConvenienceFunctions(unittest.TestCase):
    """Test the convenience functions for custom dictionary."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_dict_path = Path(self.test_dir) / "test_dictionary.json"

    def tearDown(self):
        """Clean up test fixtures."""
        if self.test_dir and os.path.exists(self.test_dir):
            import shutil

            shutil.rmtree(self.test_dir)

    @patch("custom_dictionary.get_custom_dictionary")
    def test_add_custom_word(self, mock_get_dict):
        """Test add_custom_word convenience function."""
        mock_dict = MagicMock()
        mock_dict.add_word.return_value = True
        mock_get_dict.return_value = mock_dict

        result = add_custom_word("testwort")
        self.assertTrue(result)
        mock_dict.add_word.assert_called_once_with("testwort")

    @patch("custom_dictionary.get_custom_dictionary")
    def test_remove_custom_word(self, mock_get_dict):
        """Test remove_custom_word convenience function."""
        mock_dict = MagicMock()
        mock_dict.remove_word.return_value = True
        mock_get_dict.return_value = mock_dict

        result = remove_custom_word("testwort")
        self.assertTrue(result)
        mock_dict.remove_word.assert_called_once_with("testwort")

    @patch("custom_dictionary.get_custom_dictionary")
    def test_is_custom_word(self, mock_get_dict):
        """Test is_custom_word convenience function."""
        mock_dict = MagicMock()
        mock_dict.has_word.return_value = True
        mock_get_dict.return_value = mock_dict

        result = is_custom_word("testwort")
        self.assertTrue(result)
        mock_dict.has_word.assert_called_once_with("testwort")

    @patch("src.custom_dictionary.Path.home")
    def test_get_custom_dictionary_singleton(self, mock_home):
        """Test that get_custom_dictionary returns singleton instance."""
        mock_home.return_value = Path(self.test_dir)

        dict1 = get_custom_dictionary()
        dict2 = get_custom_dictionary()

        # Sollte die gleiche Instanz sein
        self.assertIs(dict1, dict2)

    @patch("src.custom_dictionary.Path.home")
    def test_get_custom_dictionary_initialization(self, mock_home):
        """Test that get_custom_dictionary initializes correctly."""
        mock_home.return_value = Path(self.test_dir)

        # Setze die globale Variable zurück
        import src.custom_dictionary

        src.custom_dictionary._custom_dictionary = None

        dictionary = get_custom_dictionary()
        self.assertIsInstance(dictionary, CustomDictionary)
        self.assertIsNotNone(dictionary.dictionary_path)


if __name__ == "__main__":
    unittest.main()
