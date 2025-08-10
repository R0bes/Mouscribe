# tests/test_custom_dictionary.py - Tests for Custom Dictionary Feature
"""
Tests for the custom dictionary functionality.
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.custom_dictionary import CustomDictionary


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
        
        self.assertIn('path', info)
        self.assertIn('word_count', info)
        self.assertIn('words', info)
        self.assertIn('exists', info)
        self.assertIn('file_size', info)
        
        self.assertEqual(info['word_count'], 1)
        self.assertTrue(info['exists'])
    
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
    
    @patch('src.custom_dictionary.Path.home')
    def test_default_path_creation(self, mock_home):
        """Test that default path is created correctly."""
        mock_home.return_value = Path(self.test_dir)
        
        dictionary = CustomDictionary()
        expected_path = Path(self.test_dir) / ".mauscribe" / "custom_dictionary.json"
        
        self.assertEqual(dictionary.dictionary_path, expected_path)
        # Verzeichnis sollte existieren
        self.assertTrue(dictionary.dictionary_path.parent.exists())


if __name__ == '__main__':
    unittest.main()
