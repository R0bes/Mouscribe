# tests/test_dictionary_manager.py - Tests for Dictionary Manager Functions
"""
Tests for the dictionary manager CLI functions.
Covers all CLI functionality including word management, import/export, and error handling.
"""

import json
import os
import tempfile
from unittest.mock import MagicMock, mock_open, patch

import pytest

from src.custom_dictionary import CustomDictionary
# Import der Dictionary Manager Funktionen
from src.dictionary_manager import (add_word, clear_dictionary, export_words,
                                    import_words, list_words, main,
                                    print_dictionary_info, remove_word,
                                    search_word)


class TestDictionaryManagerFunctions:
    """Testklasse für die Dictionary Manager Funktionen."""

    @pytest.fixture
    def temp_dict_file(self):
        """Erstellt eine temporäre Dictionary-Datei für Tests."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(
                {
                    "words": ["test", "example", "dictionary"],
                    "metadata": {"version": "1.0", "created": "2024-01-01"},
                },
                f,
            )
            temp_path = f.name

        yield temp_path

        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    @pytest.fixture
    def mock_dictionary(self):
        """Mock für das CustomDictionary."""
        mock_dict = MagicMock(spec=CustomDictionary)
        mock_dict.get_dictionary_info.return_value = {
            "path": "/test/path/dict.json",
            "word_count": 3,
            "exists": True,
            "file_size": 150,
        }
        mock_dict.get_all_words.return_value = ["test", "example", "dictionary"]
        mock_dict.export_words.return_value = ["test", "example", "dictionary"]
        return mock_dict

    def test_print_dictionary_info(self, mock_dictionary, capsys):
        """Test: print_dictionary_info Funktion."""
        # Act
        print_dictionary_info(mock_dictionary)
        captured = capsys.readouterr()

        # Assert
        assert "📚 Benutzerdefiniertes Wörterbuch" in captured.out
        assert "Pfad: /test/path/dict.json" in captured.out
        assert "Anzahl Wörter: 3" in captured.out
        assert "Datei existiert: Ja" in captured.out
        assert "Dateigröße: 150 Bytes" in captured.out

    def test_list_words_no_limit(self, mock_dictionary, capsys):
        """Test: list_words Funktion ohne Limit."""
        # Act
        list_words(mock_dictionary)
        captured = capsys.readouterr()

        # Assert
        assert "📝 Wörter im Wörterbuch (3):" in captured.out
        assert "1. test" in captured.out
        assert "2. example" in captured.out
        assert "3. dictionary" in captured.out

    def test_list_words_with_limit(self, mock_dictionary, capsys):
        """Test: list_words Funktion mit Limit."""
        # Act
        list_words(mock_dictionary, limit=2)
        captured = capsys.readouterr()

        # Assert
        assert "📝 Wörter im Wörterbuch (3):" in captured.out
        assert "(Zeige nur die ersten 2 Wörter)" in captured.out
        assert "1. test" in captured.out
        assert "2. example" in captured.out
        assert "3. dictionary" not in captured.out

    def test_list_words_empty_dictionary(self, mock_dictionary, capsys):
        """Test: list_words Funktion mit leerem Wörterbuch."""
        # Arrange
        mock_dictionary.get_all_words.return_value = []

        # Act
        list_words(mock_dictionary)
        captured = capsys.readouterr()

        # Assert
        assert "📝 Das Wörterbuch ist leer." in captured.out

    def test_add_word_success(self, mock_dictionary, capsys):
        """Test: add_word Funktion erfolgreich."""
        # Arrange
        mock_dictionary.add_word.return_value = True

        # Act
        add_word(mock_dictionary, "neueswort")
        captured = capsys.readouterr()

        # Assert
        assert (
            "✅ Wort 'neueswort' erfolgreich zum Wörterbuch hinzugefügt" in captured.out
        )
        mock_dictionary.add_word.assert_called_once_with("neueswort")

    def test_add_word_failure(self, mock_dictionary, capsys):
        """Test: add_word Funktion fehlgeschlagen."""
        # Arrange
        mock_dictionary.add_word.return_value = False

        # Act
        add_word(mock_dictionary, "fehlerwort")
        captured = capsys.readouterr()

        # Assert
        assert "❌ Fehler beim Hinzufügen des Wortes 'fehlerwort'" in captured.out
        mock_dictionary.add_word.assert_called_once_with("fehlerwort")

    def test_remove_word_success(self, mock_dictionary, capsys):
        """Test: remove_word Funktion erfolgreich."""
        # Arrange
        mock_dictionary.remove_word.return_value = True

        # Act
        remove_word(mock_dictionary, "zuentfernendeswort")
        captured = capsys.readouterr()

        # Assert
        assert (
            "✅ Wort 'zuentfernendeswort' erfolgreich aus dem Wörterbuch entfernt"
            in captured.out
        )
        mock_dictionary.remove_word.assert_called_once_with("zuentfernendeswort")

    def test_remove_word_failure(self, mock_dictionary, capsys):
        """Test: remove_word Funktion fehlgeschlagen."""
        # Arrange
        mock_dictionary.remove_word.return_value = False

        # Act
        remove_word(mock_dictionary, "fehlerwort")
        captured = capsys.readouterr()

        # Assert
        assert "❌ Fehler beim Entfernen des Wortes 'fehlerwort'" in captured.out
        mock_dictionary.remove_word.assert_called_once_with("fehlerwort")

    def test_search_word_found(self, mock_dictionary, capsys):
        """Test: search_word Funktion - Wort gefunden."""
        # Arrange
        mock_dictionary.has_word.return_value = True

        # Act
        search_word(mock_dictionary, "testwort")
        captured = capsys.readouterr()

        # Assert
        assert "✅ Wort 'testwort' ist im Wörterbuch vorhanden" in captured.out
        mock_dictionary.has_word.assert_called_once_with("testwort")

    def test_search_word_not_found(self, mock_dictionary, capsys):
        """Test: search_word Funktion - Wort nicht gefunden."""
        # Arrange
        mock_dictionary.has_word.return_value = False

        # Act
        search_word(mock_dictionary, "nichtvorhanden")
        captured = capsys.readouterr()

        # Assert
        assert (
            "❌ Wort 'nichtvorhanden' ist nicht im Wörterbuch vorhanden" in captured.out
        )
        mock_dictionary.has_word.assert_called_once_with("nichtvorhanden")

    def test_import_words_success(self, mock_dictionary, capsys):
        """Test: import_words Funktion erfolgreich."""
        # Arrange
        words = ["wort1", "wort2", "wort3"]
        mock_dictionary.import_words.return_value = 3

        # Act
        import_words(mock_dictionary, words)
        captured = capsys.readouterr()

        # Assert
        assert "✅ 3 von 3 Wörtern erfolgreich importiert" in captured.out
        mock_dictionary.import_words.assert_called_once_with(words)

    def test_import_words_partial_success(self, mock_dictionary, capsys):
        """Test: import_words Funktion teilweise erfolgreich."""
        # Arrange
        words = ["wort1", "wort2", "wort3"]
        mock_dictionary.import_words.return_value = 2

        # Act
        import_words(mock_dictionary, words)
        captured = capsys.readouterr()

        # Assert
        assert "✅ 2 von 3 Wörtern erfolgreich importiert" in captured.out
        mock_dictionary.import_words.assert_called_once_with(words)

    def test_import_words_empty_list(self, mock_dictionary, capsys):
        """Test: import_words Funktion mit leerer Liste."""
        # Act
        import_words(mock_dictionary, [])
        captured = capsys.readouterr()

        # Assert
        assert "❌ Keine Wörter zum Importieren angegeben" in captured.out
        mock_dictionary.import_words.assert_not_called()

    def test_export_words_to_console(self, mock_dictionary, capsys):
        """Test: export_words Funktion ohne Datei."""
        # Act
        export_words(mock_dictionary)
        captured = capsys.readouterr()

        # Assert
        assert "📤 Export (3 Wörter):" in captured.out
        assert "test" in captured.out
        assert "example" in captured.out
        assert "dictionary" in captured.out
        mock_dictionary.export_words.assert_called_once()

    def test_export_words_to_file(self, mock_dictionary, temp_dict_file):
        """Test: export_words Funktion mit Datei."""
        # Arrange
        export_file = temp_dict_file.replace(".json", "_export.txt")

        # Act
        export_words(mock_dictionary, export_file)

        # Assert
        assert os.path.exists(export_file)
        with open(export_file, "r", encoding="utf-8") as f:
            content = f.read()
            assert "test" in content
            assert "example" in content
            assert "dictionary" in content

        # Cleanup
        if os.path.exists(export_file):
            os.unlink(export_file)

    def test_export_words_file_error(self, mock_dictionary):
        """Test: export_words Funktion mit Dateifehler."""
        # Arrange
        invalid_path = "/invalid/path/export.txt"

        # Act & Assert
        with patch("builtins.open", side_effect=Exception("Permission denied")):
            # Sollte keine Exception werfen, sondern Fehler ausgeben
            try:
                export_words(mock_dictionary, invalid_path)
            except Exception:
                pytest.fail("export_words sollte keine Exception werfen")

    def test_clear_dictionary_success(self, mock_dictionary, capsys):
        """Test: clear_dictionary Funktion erfolgreich."""
        # Arrange
        mock_dictionary.clear_dictionary.return_value = True

        # Act
        clear_dictionary(mock_dictionary)
        captured = capsys.readouterr()

        # Assert
        assert "✅ Wörterbuch erfolgreich geleert" in captured.out
        mock_dictionary.clear_dictionary.assert_called_once()

    def test_clear_dictionary_failure(self, mock_dictionary, capsys):
        """Test: clear_dictionary Funktion fehlgeschlagen."""
        # Arrange
        mock_dictionary.clear_dictionary.return_value = False

        # Act
        clear_dictionary(mock_dictionary)
        captured = capsys.readouterr()

        # Assert
        assert "❌ Fehler beim Leeren des Wörterbuchs" in captured.out
        mock_dictionary.clear_dictionary.assert_called_once()


class TestDictionaryManagerMain:
    """Testklasse für die main Funktion."""

    @patch("src.dictionary_manager.get_custom_dictionary")
    def test_main_add_word(self, mock_get_dict):
        """Test: main Funktion mit add Befehl."""
        # Arrange
        mock_dict = MagicMock()
        mock_get_dict.return_value = mock_dict

        # Act
        with patch("sys.argv", ["dictionary_manager.py", "add", "testwort"]):
            main()

        # Assert
        mock_dict.add_word.assert_called_once_with("testwort")

    @patch("src.dictionary_manager.get_custom_dictionary")
    def test_main_remove_word(self, mock_get_dict):
        """Test: main Funktion mit remove Befehl."""
        # Arrange
        mock_dict = MagicMock()
        mock_get_dict.return_value = mock_dict

        # Act
        with patch("sys.argv", ["dictionary_manager.py", "remove", "testwort"]):
            main()

        # Assert
        mock_dict.remove_word.assert_called_once_with("testwort")

    @patch("src.dictionary_manager.get_custom_dictionary")
    def test_main_search_word(self, mock_get_dict):
        """Test: main Funktion mit search Befehl."""
        # Arrange
        mock_dict = MagicMock()
        mock_get_dict.return_value = mock_dict

        # Act
        with patch("sys.argv", ["dictionary_manager.py", "search", "testwort"]):
            main()

        # Assert
        mock_dict.has_word.assert_called_once_with("testwort")

    @patch("src.dictionary_manager.get_custom_dictionary")
    def test_main_list_words(self, mock_get_dict):
        """Test: main Funktion mit list Befehl."""
        # Arrange
        mock_dict = MagicMock()
        mock_get_dict.return_value = mock_dict

        # Act
        with patch("sys.argv", ["dictionary_manager.py", "list"]):
            main()

        # Assert
        mock_dict.get_all_words.assert_called_once()

    @patch("src.dictionary_manager.get_custom_dictionary")
    def test_main_info(self, mock_get_dict):
        """Test: main Funktion mit info Befehl."""
        # Arrange
        mock_dict = MagicMock()
        mock_get_dict.return_value = mock_dict

        # Act
        with patch("sys.argv", ["dictionary_manager.py", "info"]):
            main()

        # Assert
        mock_dict.get_dictionary_info.assert_called_once()

    @patch("src.dictionary_manager.get_custom_dictionary")
    def test_main_clear(self, mock_get_dict):
        """Test: main Funktion mit clear Befehl."""
        # Arrange
        mock_dict = MagicMock()
        mock_get_dict.return_value = mock_dict

        # Act
        with patch("sys.argv", ["dictionary_manager.py", "clear"]):
            main()

        # Assert
        mock_dict.clear_dictionary.assert_called_once()

    @patch("src.dictionary_manager.get_custom_dictionary")
    def test_main_import(self, mock_get_dict):
        """Test: main Funktion mit import Befehl."""
        # Arrange
        mock_dict = MagicMock()
        mock_get_dict.return_value = mock_dict

        # Act
        with patch(
            "sys.argv", ["dictionary_manager.py", "import", "wort1,wort2,wort3"]
        ):
            main()

        # Assert
        mock_dict.import_words.assert_called_once_with(["wort1", "wort2", "wort3"])

    @patch("src.dictionary_manager.get_custom_dictionary")
    def test_main_export(self, mock_get_dict):
        """Test: main Funktion mit export Befehl."""
        # Arrange
        mock_dict = MagicMock()
        mock_get_dict.return_value = mock_dict

        # Act
        with patch("sys.argv", ["dictionary_manager.py", "export", "export.txt"]):
            with patch("builtins.open", mock_open()):
                main()

        # Assert
        mock_dict.export_words.assert_called_once()

    def test_main_no_args(self):
        """Test: main Funktion ohne Argumente."""
        # Act
        with patch("sys.argv", ["dictionary_manager.py"]):
            with patch("sys.exit") as mock_exit:
                main()

        # Assert
        mock_exit.assert_called_once_with(2)

    def test_main_invalid_command(self):
        """Test: main Funktion mit ungültigem Befehl."""
        # Act
        with patch("sys.argv", ["dictionary_manager.py", "invalid"]):
            with patch("sys.exit") as mock_exit:
                main()

        # Assert
        mock_exit.assert_called_with(2)


if __name__ == "__main__":
    pytest.main([__file__])
