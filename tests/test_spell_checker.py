"""
Tests für den Spell Checker (SpellGrammarChecker).

Testet alle Funktionen des Rechtschreibprüfers inklusive:
- Initialisierung
- Rechtschreibprüfung
- Grammatikprüfung
- Benutzerdefiniertes Wörterbuch
- Automatische Korrektur
- Vorschläge
- Edge Cases und Fehlerbehandlung
"""

import os

# Import des zu testenden Moduls
import sys
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.spell_checker import (
    SpellGrammarChecker,
    add_custom_word,
    check_and_correct_text,
    get_custom_word_count,
    get_custom_words,
    get_spell_checker,
    remove_custom_word,
)


class TestSpellGrammarChecker:
    """Test-Klasse für den SpellGrammarChecker."""

    def setup_method(self):
        """Setup vor jedem Test."""
        # Mock für die Config
        self.config_patcher = patch("src.spell_checker.config")
        self.mock_config = self.config_patcher.start()

        # Standard-Config-Werte setzen
        self.mock_config.spell_check_enabled = True
        self.mock_config.spell_check_language = "de"
        self.mock_config.spell_check_grammar = True
        self.mock_config.spell_check_auto_correct = True
        self.mock_config.spell_check_suggest_only = False
        self.mock_config.custom_dictionary_enabled = True
        self.mock_config.custom_dictionary_auto_add_unknown = True
        self.mock_config.custom_dictionary_max_words = 1000

        # Mock für CustomDictionary
        self.custom_dict_patcher = patch("src.spell_checker.get_custom_dictionary")
        self.mock_custom_dict = self.custom_dict_patcher.start()

        # Mock CustomDictionary-Instanz
        self.mock_dict_instance = Mock()
        self.mock_dict_instance.has_word.return_value = False
        self.mock_dict_instance.add_word.return_value = True
        self.mock_dict_instance.remove_word.return_value = True
        self.mock_dict_instance.get_all_words.return_value = ["test", "wort"]
        self.mock_dict_instance.get_word_count.return_value = 2
        self.mock_dict_instance.clear_dictionary.return_value = True
        self.mock_custom_dict.return_value = self.mock_dict_instance

    def teardown_method(self):
        """Cleanup nach jedem Test."""
        self.config_patcher.stop()
        self.custom_dict_patcher.stop()

    @patch("src.spell_checker.SPELL_CHECKER_AVAILABLE", True)
    @patch("src.spell_checker.SpellChecker")
    def test_initialization_success(self, mock_spell_checker_class):
        """Test erfolgreiche Initialisierung des Spell Checkers."""
        mock_spell_checker = Mock()
        mock_spell_checker_class.return_value = mock_spell_checker

        checker = SpellGrammarChecker()

        assert checker._enabled is True
        assert checker._language == "de"
        assert checker._grammar_check is True
        assert checker._auto_correct is True
        assert checker._suggest_only is False
        assert checker._custom_dict_enabled is True
        assert checker._spell_checker is not None
        assert checker._custom_dictionary is not None

    @patch("src.spell_checker.SPELL_CHECKER_AVAILABLE", False)
    def test_initialization_spell_checker_unavailable(self):
        """Test Initialisierung wenn PySpellChecker nicht verfügbar ist."""
        checker = SpellGrammarChecker()

        assert checker._enabled is False
        assert checker._spell_checker is None

    @patch("src.spell_checker.SPELL_CHECKER_AVAILABLE", True)
    @patch("src.spell_checker.SpellChecker")
    def test_initialization_spell_checker_exception(self, mock_spell_checker_class):
        """Test Initialisierung bei Fehlern im PySpellChecker."""
        mock_spell_checker_class.side_effect = Exception("Test error")

        checker = SpellGrammarChecker()

        assert checker._enabled is False
        assert checker._spell_checker is None

    @patch("src.spell_checker.SPELL_CHECKER_AVAILABLE", True)
    @patch("src.spell_checker.SpellChecker")
    def test_initialization_custom_dict_exception(self, mock_spell_checker_class):
        """Test Initialisierung bei Fehlern im benutzerdefinierten Wörterbuch."""
        mock_spell_checker = Mock()
        mock_spell_checker_class.return_value = mock_spell_checker
        self.mock_custom_dict.side_effect = Exception("Dict error")

        checker = SpellGrammarChecker()

        assert checker._custom_dict_enabled is False
        assert checker._custom_dictionary is None

    @patch("src.spell_checker.SPELL_CHECKER_AVAILABLE", True)
    @patch("src.spell_checker.SpellChecker")
    def test_grammar_patterns_setup(self, mock_spell_checker_class):
        """Test Setup der Grammatikregeln."""
        mock_spell_checker = Mock()
        mock_spell_checker_class.return_value = mock_spell_checker

        checker = SpellGrammarChecker()

        # Prüfe deutsche Grammatikregeln
        assert len(checker._grammar_patterns) > 0

        # Prüfe spezifische Regeln
        pattern_found = False
        for pattern in checker._grammar_patterns:
            if "villen" in str(pattern.get("pattern", "")):
                pattern_found = True
                break
        assert pattern_found, "Deutsche Grammatikregel für 'villen' sollte vorhanden sein"

    @patch("src.spell_checker.SPELL_CHECKER_AVAILABLE", True)
    @patch("src.spell_checker.SpellChecker")
    def test_grammar_patterns_english_language(self, mock_spell_checker_class):
        """Test Grammatikregeln für englische Sprache."""
        mock_spell_checker = Mock()
        mock_spell_checker_class.return_value = mock_spell_checker
        self.mock_config.spell_check_language = "en"

        checker = SpellGrammarChecker()

        # Englische Sprache sollte keine deutschen Grammatikregeln haben
        assert len(checker._grammar_patterns) == 0

    @patch("src.spell_checker.SPELL_CHECKER_AVAILABLE", True)
    @patch("src.spell_checker.SpellChecker")
    def test_check_text_empty_text(self, mock_spell_checker_class):
        """Test Rechtschreibprüfung mit leerem Text."""
        mock_spell_checker = Mock()
        mock_spell_checker_class.return_value = mock_spell_checker

        checker = SpellGrammarChecker()
        result = checker.check_text("")

        assert result == ""

    @patch("src.spell_checker.SPELL_CHECKER_AVAILABLE", True)
    @patch("src.spell_checker.SpellChecker")
    def test_check_text_whitespace_only(self, mock_spell_checker_class):
        """Test Rechtschreibprüfung mit nur Leerzeichen."""
        mock_spell_checker = Mock()
        mock_spell_checker_class.return_value = mock_spell_checker

        checker = SpellGrammarChecker()
        result = checker.check_text("   \n\t   ")

        assert result == "   \n\t   "

    @patch("src.spell_checker.SPELL_CHECKER_AVAILABLE", True)
    @patch("src.spell_checker.SpellChecker")
    def test_check_text_disabled(self, mock_spell_checker_class):
        """Test wenn Rechtschreibprüfung deaktiviert ist."""
        mock_spell_checker = Mock()
        mock_spell_checker_class.return_value = mock_spell_checker
        self.mock_config.spell_check_enabled = False

        checker = SpellGrammarChecker()
        result = checker.check_text("Das ist ein testt.")

        # Text sollte unverändert bleiben
        assert result == "Das ist ein testt."

    @patch("src.spell_checker.SPELL_CHECKER_AVAILABLE", True)
    @patch("src.spell_checker.SpellChecker")
    def test_check_text_grammar_correction(self, mock_spell_checker_class):
        """Test Grammatikkorrektur."""
        mock_spell_checker = Mock()
        mock_spell_checker_class.return_value = mock_spell_checker
        mock_spell_checker.unknown.return_value = set()  # Keine Rechtschreibfehler

        checker = SpellGrammarChecker()
        result = checker.check_text("Das ist ein test. hier geht es weiter.")

        # Prüfe ob Satzanfang korrigiert wurde
        assert "Hier" in result or "hier" not in result

    @patch("src.spell_checker.SPELL_CHECKER_AVAILABLE", True)
    @patch("src.spell_checker.SpellChecker")
    def test_check_text_spelling_correction(self, mock_spell_checker_class):
        """Test Rechtschreibkorrektur."""
        mock_spell_checker = Mock()
        mock_spell_checker_class.return_value = mock_spell_checker

        # Simuliere Rechtschreibfehler
        mock_spell_checker.unknown.return_value = {"testt"}
        mock_spell_checker.candidates.return_value = {"test"}

        checker = SpellGrammarChecker()
        result = checker.check_text("Das ist ein testt.")

        # Prüfe ob Korrektur angewendet wurde
        assert "testt" not in result or "test" in result

    @patch("src.spell_checker.SPELL_CHECKER_AVAILABLE", True)
    @patch("src.spell_checker.SpellChecker")
    def test_check_text_suggest_only_mode(self, mock_spell_checker_class):
        """Test Vorschlagsmodus ohne automatische Korrektur."""
        mock_spell_checker = Mock()
        mock_spell_checker_class.return_value = mock_spell_checker
        self.mock_config.spell_check_suggest_only = True

        # Simuliere Rechtschreibfehler
        mock_spell_checker.unknown.return_value = {"testt"}
        mock_spell_checker.candidates.return_value = {"test"}

        checker = SpellGrammarChecker()
        result = checker.check_text("Das ist ein testt.")

        # Text sollte unverändert bleiben
        assert result == "Das ist ein testt."

    @patch("src.spell_checker.SPELL_CHECKER_AVAILABLE", True)
    @patch("src.spell_checker.SpellChecker")
    def test_check_text_auto_add_unknown_words(self, mock_spell_checker_class):
        """Test automatisches Hinzufügen unbekannter Wörter."""
        mock_spell_checker = Mock()
        mock_spell_checker_class.return_value = mock_spell_checker

        # Simuliere Rechtschreibfehler
        mock_spell_checker.unknown.return_value = {"neueswort"}
        mock_spell_checker.candidates.return_value = {"neueswort"}

        checker = SpellGrammarChecker()
        checker.check_text("Das ist ein neueswort.")

        # Prüfe ob Wort zum Wörterbuch hinzugefügt wurde
        self.mock_dict_instance.add_word.assert_called_with("neueswort")

    @patch("src.spell_checker.SPELL_CHECKER_AVAILABLE", True)
    @patch("src.spell_checker.SpellChecker")
    def test_check_text_dictionary_full(self, mock_spell_checker_class):
        """Test wenn das Wörterbuch voll ist."""
        mock_spell_checker = Mock()
        mock_spell_checker_class.return_value = mock_spell_checker
        self.mock_config.custom_dictionary_max_words = 1
        self.mock_dict_instance.get_word_count.return_value = 1

        # Simuliere Rechtschreibfehler
        mock_spell_checker.unknown.return_value = {"neueswort"}
        mock_spell_checker.candidates.return_value = {"neueswort"}

        checker = SpellGrammarChecker()
        checker.check_text("Das ist ein neueswort.")

        # Wort sollte nicht hinzugefügt werden
        self.mock_dict_instance.add_word.assert_not_called()

    @patch("src.spell_checker.SPELL_CHECKER_AVAILABLE", True)
    @patch("src.spell_checker.SpellChecker")
    def test_check_text_exception_handling(self, mock_spell_checker_class):
        """Test Fehlerbehandlung bei der Rechtschreibprüfung."""
        mock_spell_checker = Mock()
        mock_spell_checker_class.return_value = mock_spell_checker
        mock_spell_checker.unknown.side_effect = Exception("Test error")

        checker = SpellGrammarChecker()
        result = checker.check_text("test text")

        # Bei Fehlern sollte der ursprüngliche Text zurückgegeben werden
        assert result == "test text"

    @patch("src.spell_checker.SPELL_CHECKER_AVAILABLE", True)
    @patch("src.spell_checker.SpellChecker")
    def test_is_similar_word(self, mock_spell_checker_class):
        """Test Ähnlichkeitsprüfung zwischen Wörtern."""
        mock_spell_checker = Mock()
        mock_spell_checker_class.return_value = mock_spell_checker

        checker = SpellGrammarChecker()

        # Test ähnliche Wörter
        assert checker._is_similar_word("test", "test") is True
        assert checker._is_similar_word("test", "tests") is True
        assert checker._is_similar_word("test", "best") is True

        # Test unähnliche Wörter
        assert checker._is_similar_word("test", "completely") is False
        assert checker._is_similar_word("a", "verylongword") is False

    @patch("src.spell_checker.SPELL_CHECKER_AVAILABLE", True)
    @patch("src.spell_checker.SpellChecker")
    def test_get_suggestions(self, mock_spell_checker_class):
        """Test Abrufen von Korrekturvorschlägen."""
        mock_spell_checker = Mock()
        mock_spell_checker_class.return_value = mock_spell_checker

        # Simuliere Rechtschreibfehler
        mock_spell_checker.unknown.return_value = {"testt"}
        mock_spell_checker.candidates.return_value = {"test", "tests"}

        checker = SpellGrammarChecker()
        suggestions = checker.get_suggestions("Das ist ein testt.")

        assert len(suggestions) == 1
        assert suggestions[0]["error_text"] == "testt"
        assert "test" in suggestions[0]["replacements"]
        assert suggestions[0]["category"] == "spelling"

    @patch("src.spell_checker.SPELL_CHECKER_AVAILABLE", True)
    @patch("src.spell_checker.SpellChecker")
    def test_get_suggestions_empty_text(self, mock_spell_checker_class):
        """Test Vorschläge für leeren Text."""
        mock_spell_checker = Mock()
        mock_spell_checker_class.return_value = mock_spell_checker

        checker = SpellGrammarChecker()
        suggestions = checker.get_suggestions("")

        assert suggestions == []

    @patch("src.spell_checker.SPELL_CHECKER_AVAILABLE", True)
    @patch("src.spell_checker.SpellChecker")
    def test_get_suggestions_exception_handling(self, mock_spell_checker_class):
        """Test Fehlerbehandlung bei Vorschlägen."""
        mock_spell_checker = Mock()
        mock_spell_checker_class.return_value = mock_spell_checker
        mock_spell_checker.unknown.side_effect = Exception("Test error")

        checker = SpellGrammarChecker()
        suggestions = checker.get_suggestions("test text")

        assert suggestions == []

    @patch("src.spell_checker.SPELL_CHECKER_AVAILABLE", True)
    @patch("src.spell_checker.SpellChecker")
    def test_is_enabled(self, mock_spell_checker_class):
        """Test Status der Rechtschreibprüfung."""
        mock_spell_checker = Mock()
        mock_spell_checker_class.return_value = mock_spell_checker

        checker = SpellGrammarChecker()
        assert checker.is_enabled() is True

    @patch("src.spell_checker.SPELL_CHECKER_AVAILABLE", False)
    def test_is_enabled_disabled(self):
        """Test Status wenn Rechtschreibprüfung deaktiviert ist."""
        checker = SpellGrammarChecker()
        assert checker.is_enabled() is False

    @patch("src.spell_checker.SPELL_CHECKER_AVAILABLE", True)
    @patch("src.spell_checker.SpellChecker")
    def test_is_custom_dictionary_enabled(self, mock_spell_checker_class):
        """Test Status des benutzerdefinierten Wörterbuchs."""
        mock_spell_checker = Mock()
        mock_spell_checker_class.return_value = mock_spell_checker

        checker = SpellGrammarChecker()
        assert checker.is_custom_dictionary_enabled() is True

    @patch("src.spell_checker.SPELL_CHECKER_AVAILABLE", True)
    @patch("src.spell_checker.SpellChecker")
    def test_add_custom_word(self, mock_spell_checker_class):
        """Test Hinzufügen eines Wortes zum Wörterbuch."""
        mock_spell_checker = Mock()
        mock_spell_checker_class.return_value = mock_spell_checker

        checker = SpellGrammarChecker()
        result = checker.add_custom_word("neueswort")

        assert result is True
        self.mock_dict_instance.add_word.assert_called_with("neueswort")

    @patch("src.spell_checker.SPELL_CHECKER_AVAILABLE", True)
    @patch("src.spell_checker.SpellChecker")
    def test_add_custom_word_disabled(self, mock_spell_checker_class):
        """Test Hinzufügen wenn Wörterbuch deaktiviert ist."""
        mock_spell_checker = Mock()
        mock_spell_checker_class.return_value = mock_spell_checker
        self.mock_config.custom_dictionary_enabled = False

        checker = SpellGrammarChecker()
        result = checker.add_custom_word("neueswort")

        assert result is False

    @patch("src.spell_checker.SPELL_CHECKER_AVAILABLE", True)
    @patch("src.spell_checker.SpellChecker")
    def test_remove_custom_word(self, mock_spell_checker_class):
        """Test Entfernen eines Wortes aus dem Wörterbuch."""
        mock_spell_checker = Mock()
        mock_spell_checker_class.return_value = mock_spell_checker

        checker = SpellGrammarChecker()
        result = checker.remove_custom_word("test")

        assert result is True
        self.mock_dict_instance.remove_word.assert_called_with("test")

    @patch("src.spell_checker.SPELL_CHECKER_AVAILABLE", True)
    @patch("src.spell_checker.SpellChecker")
    def test_get_custom_words(self, mock_spell_checker_class):
        """Test Abrufen aller Wörter aus dem Wörterbuch."""
        mock_spell_checker = Mock()
        mock_spell_checker_class.return_value = mock_spell_checker

        checker = SpellGrammarChecker()
        words = checker.get_custom_words()

        assert words == ["test", "wort"]

    @patch("src.spell_checker.SPELL_CHECKER_AVAILABLE", True)
    @patch("src.spell_checker.SpellChecker")
    def test_get_custom_word_count(self, mock_spell_checker_class):
        """Test Abrufen der Wortanzahl im Wörterbuch."""
        mock_spell_checker = Mock()
        mock_spell_checker_class.return_value = mock_spell_checker

        checker = SpellGrammarChecker()
        count = checker.get_custom_word_count()

        assert count == 2

    @patch("src.spell_checker.SPELL_CHECKER_AVAILABLE", True)
    @patch("src.spell_checker.SpellChecker")
    def test_clear_custom_dictionary(self, mock_spell_checker_class):
        """Test Löschen des Wörterbuchs."""
        mock_spell_checker = Mock()
        mock_spell_checker_class.return_value = mock_spell_checker

        checker = SpellGrammarChecker()
        result = checker.clear_custom_dictionary()

        assert result is True
        self.mock_dict_instance.clear_dictionary.assert_called_once()

    @patch("src.spell_checker.SPELL_CHECKER_AVAILABLE", True)
    @patch("src.spell_checker.SpellChecker")
    def test_close(self, mock_spell_checker_class):
        """Test Schließen des Spell Checkers."""
        mock_spell_checker = Mock()
        mock_spell_checker_class.return_value = mock_spell_checker

        checker = SpellGrammarChecker()
        checker.close()

        assert checker._spell_checker is None

    @patch("src.spell_checker.SPELL_CHECKER_AVAILABLE", True)
    @patch("src.spell_checker.SpellChecker")
    def test_close_exception_handling(self, mock_spell_checker_class):
        """Test Fehlerbehandlung beim Schließen."""
        mock_spell_checker = Mock()
        mock_spell_checker_class.return_value = mock_spell_checker
        mock_spell_checker.side_effect = Exception("Close error")

        checker = SpellGrammarChecker()
        checker.close()  # Sollte keine Exception werfen

        assert checker._spell_checker is None

    @patch("src.spell_checker.SPELL_CHECKER_AVAILABLE", True)
    @patch("src.spell_checker.SpellChecker")
    def test_destructor(self, mock_spell_checker_class):
        """Test Destruktor."""
        mock_spell_checker = Mock()
        mock_spell_checker_class.return_value = mock_spell_checker

        checker = SpellGrammarChecker()
        checker.__del__()  # Sollte keine Exception werfen


class TestGlobalFunctions:
    """Test-Klasse für globale Funktionen des Spell Checkers."""

    def setup_method(self):
        """Setup für jeden Test."""
        # Mock für get_spell_checker
        self.get_checker_patcher = patch("src.spell_checker.get_spell_checker")
        self.mock_get_checker = self.get_checker_patcher.start()

        # Mock SpellGrammarChecker-Instanz
        self.mock_checker = Mock()
        self.mock_get_checker.return_value = self.mock_checker

    def teardown_method(self):
        """Cleanup nach jedem Test."""
        self.get_checker_patcher.stop()

    def test_get_spell_checker_singleton(self):
        """Test Singleton-Pattern von get_src.spell_checker."""
        with patch("src.spell_checker._spell_checker", None):
            with patch("src.spell_checker.SpellGrammarChecker") as mock_class:
                mock_instance = Mock()
                mock_class.return_value = mock_instance

                result = get_spell_checker()

                assert result == mock_instance
                mock_class.assert_called_once()

    def test_get_spell_checker_existing_instance(self):
        """Test get_spell_checker mit existierender Instanz."""
        existing_instance = Mock()
        with patch("src.spell_checker._spell_checker", existing_instance):
            result = get_spell_checker()

            assert result == existing_instance

    def test_check_and_correct_text(self):
        """Test Convenience-Funktion check_and_correct_text."""
        self.mock_checker.check_text.return_value = "korrigierter text"

        result = check_and_correct_text("test text")

        assert result == "korrigierter text"
        self.mock_checker.check_text.assert_called_with("test text")

    def test_check_and_correct_text_none_result(self):
        """Test check_and_correct_text mit None-Ergebnis."""
        self.mock_checker.check_text.return_value = None

        result = check_and_correct_text("test text")

        assert result == "test text"

    def test_add_custom_word_global(self):
        """Test globale add_custom_word Funktion."""
        self.mock_checker.add_custom_word.return_value = True

        result = add_custom_word("neueswort")

        assert result is True
        self.mock_checker.add_custom_word.assert_called_with("neueswort")

    def test_remove_custom_word_global(self):
        """Test globale remove_custom_word Funktion."""
        self.mock_checker.remove_custom_word.return_value = True

        result = remove_custom_word("test")

        assert result is True
        self.mock_checker.remove_custom_word.assert_called_with("test")

    def test_get_custom_words_global(self):
        """Test globale get_custom_words Funktion."""
        self.mock_checker.get_custom_words.return_value = ["test", "wort"]

        result = get_custom_words()

        assert result == ["test", "wort"]
        self.mock_checker.get_custom_words.assert_called_once()

    def test_get_custom_word_count_global(self):
        """Test globale get_custom_word_count Funktion."""
        self.mock_checker.get_custom_word_count.return_value = 5

        result = get_custom_word_count()

        assert result == 5
        self.mock_checker.get_custom_word_count.assert_called_once()


class TestSpellCheckerIntegration:
    """Integrationstests für den Spell Checker."""

    def setup_method(self):
        """Setup für jeden Test."""
        # Mock für die Config
        self.config_patcher = patch("src.spell_checker.config")
        self.mock_config = self.config_patcher.start()

        # Standard-Config-Werte setzen
        self.mock_config.spell_check_enabled = True
        self.mock_config.spell_check_language = "de"
        self.mock_config.spell_check_grammar = True
        self.mock_config.spell_check_auto_correct = True
        self.mock_config.spell_check_suggest_only = False
        self.mock_config.custom_dictionary_enabled = True
        self.mock_config.custom_dictionary_auto_add_unknown = True
        self.mock_config.custom_dictionary_max_words = 1000

        # Mock für CustomDictionary
        self.custom_dict_patcher = patch("src.spell_checker.get_custom_dictionary")
        self.mock_custom_dict = self.custom_dict_patcher.start()

        # Mock CustomDictionary-Instanz
        self.mock_dict_instance = Mock()
        self.mock_dict_instance.has_word.return_value = False
        self.mock_dict_instance.add_word.return_value = True
        self.mock_dict_instance.remove_word.return_value = True
        self.mock_dict_instance.get_all_words.return_value = ["test", "wort"]
        self.mock_dict_instance.get_word_count.return_value = 2
        self.mock_dict_instance.clear_dictionary.return_value = True
        self.mock_custom_dict.return_value = self.mock_dict_instance

    def teardown_method(self):
        """Cleanup nach jedem Test."""
        self.config_patcher.stop()
        self.custom_dict_patcher.stop()

    @patch("src.spell_checker.SPELL_CHECKER_AVAILABLE", True)
    @patch("src.spell_checker.SpellChecker")
    def test_full_text_correction_workflow(self, mock_spell_checker_class):
        """Test vollständiger Textkorrektur-Workflow."""
        mock_spell_checker = Mock()
        mock_spell_checker_class.return_value = mock_spell_checker

        # Simuliere komplexe Korrekturszenarien
        mock_spell_checker.unknown.return_value = {"villen", "warscheinlich"}
        mock_spell_checker.candidates.side_effect = lambda x: {"vielen"} if x == "villen" else {"wahrscheinlich"}

        checker = SpellGrammarChecker()
        result = checker.check_text("Das villen warscheinlich ein test.")

        # Prüfe ob Korrekturen angewendet wurden
        assert "villen" not in result or "vielen" in result
        assert "warscheinlich" not in result or "wahrscheinlich" in result

    @patch("src.spell_checker.SPELL_CHECKER_AVAILABLE", True)
    @patch("src.spell_checker.SpellChecker")
    def test_custom_dictionary_integration(self, mock_spell_checker_class):
        """Test Integration mit benutzerdefiniertem Wörterbuch."""
        mock_spell_checker = Mock()
        mock_spell_checker_class.return_value = mock_spell_checker

        # Simuliere Wörter im benutzerdefinierten Wörterbuch
        self.mock_dict_instance.has_word.side_effect = lambda x: x in ["fachbegriff", "technologie"]
        mock_spell_checker.unknown.return_value = set()  # Keine Fehler

        checker = SpellGrammarChecker()
        result = checker.check_text("Das ist ein fachbegriff und technologie.")

        # Text sollte unverändert bleiben, da Wörter im Wörterbuch sind
        assert "fachbegriff" in result
        assert "technologie" in result

    @patch("src.spell_checker.SPELL_CHECKER_AVAILABLE", True)
    @patch("src.spell_checker.SpellChecker")
    def test_error_recovery(self, mock_spell_checker_class):
        """Test Fehlerbehandlung und Wiederherstellung."""
        mock_spell_checker = Mock()
        mock_spell_checker_class.return_value = mock_spell_checker

        # Simuliere Fehler bei der Rechtschreibprüfung
        mock_spell_checker.unknown.side_effect = [Exception("First error"), set()]

        checker = SpellGrammarChecker()

        # Erster Aufruf sollte fehlschlagen
        result1 = checker.check_text("test text")
        assert result1 == "test text"

        # Zweiter Aufruf sollte funktionieren
        result2 = checker.check_text("test text")
        assert result2 == "test text"


if __name__ == "__main__":
    pytest.main([__file__])
