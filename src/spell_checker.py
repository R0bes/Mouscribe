from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Set

from .logger import get_logger

try:
    from spellchecker import SpellChecker as SC

    SPELL_CHECKER_AVAILABLE = True
except ImportError:
    SPELL_CHECKER_AVAILABLE = False
    get_logger(__name__).warning(
        "Warnung: pyspellchecker nicht verfügbar. Rechtschreibprüfung deaktiviert."
    )

from . import config
from .custom_dictionary import CustomDict, get_custom_dictionary


class SpellChecker:
    """
    Einfacher Rechtschreibprüfer für deutsche und englische Texte.

    Verwendet pyspellchecker für Rechtschreibprüfung ohne externe Dependencies.
    Fokus auf Rechtschreibung, einfache Grammatikregeln.
    """

    def __init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__)

        self._spell_checker: SC | None = None
        # Verwende getattr mit Standardwerten für mypy-Kompatibilität
        self._language = getattr(config, "spell_check_language", "de")
        self._enabled = (
            getattr(config, "spell_check_enabled", True) and SPELL_CHECKER_AVAILABLE
        )
        self._grammar_check = getattr(config, "spell_check_grammar", True)
        self._auto_correct = getattr(config, "spell_check_auto_correct", False)
        self._suggest_only = getattr(config, "spell_check_suggest_only", False)

        # Benutzerdefiniertes Wörterbuch
        self._custom_dictionary: CustomDict | None = None
        self._custom_dict_enabled = getattr(config, "custom_dictionary_enabled", True)
        self._auto_add_unknown = getattr(
            config, "custom_dictionary_auto_add_unknown", False
        )
        self._max_words = getattr(config, "custom_dictionary_max_words", 1000)

        # Einfache deutsche Grammatikregeln
        self._grammar_patterns = self._setup_grammar_patterns()

        if self._enabled:
            self._initialize_spell_checker()

        if self._custom_dict_enabled:
            self._initialize_custom_dictionary()

    def _setup_grammar_patterns(self) -> list[dict[str, Any]]:
        """Erstellt einfache Grammatikregeln für Deutsch."""
        patterns = []

        if self._language == "de":
            patterns.extend(
                [
                    # Groß-/Kleinschreibung nach Punkt
                    {
                        "pattern": r"\.(\s+)([a-zäöüß])",
                        "replacement": r".\1\2",
                        "description": "Satzanfang sollte großgeschrieben werden",
                        "correction": lambda m: f".{m.group(1)}{m.group(2).upper()}",
                    },
                    # Doppelte Leerzeichen
                    {
                        "pattern": r"  +",
                        "replacement": r" ",
                        "description": "Doppelte Leerzeichen entfernen",
                        "correction": lambda m: " ",
                    },
                    # Häufige Rechtschreibfehler
                    {
                        "pattern": r"\bvillen?\b",
                        "replacement": "vielen",
                        "description": "Häufiger Rechtschreibfehler: villen -> vielen",
                        "correction": lambda m: "vielen",
                    },
                    {
                        "pattern": r"\bwarscheinlich\b",
                        "replacement": "wahrscheinlich",
                        "description": "Häufiger Rechtschreibfehler: warscheinlich -> wahrscheinlich",
                        "correction": lambda m: "wahrscheinlich",
                    },
                ]
            )

        return patterns

    def _initialize_spell_checker(self) -> None:
        """Initialisiert den PySpellChecker."""
        if not SPELL_CHECKER_AVAILABLE:
            self.logger.warning(
                "PySpellChecker nicht verfügbar - Rechtschreibprüfung deaktiviert"
            )
            self._enabled = False
            return

        try:
            self.logger.info(
                f"Initialisiere Rechtschreibprüfung für Sprache: {self._language}"
            )

            # Sprachcode anpassen
            lang_code = self._language
            if lang_code == "de":
                lang_code = "de"
            elif lang_code == "en":
                lang_code = "en"
            else:
                lang_code = "en"  # Fallback

            self._spell_checker = SC(language=lang_code)
            self.logger.info("Rechtschreibprüfung erfolgreich initialisiert")
        except Exception as e:
            self.logger.error(
                f"Fehler beim Initialisieren der Rechtschreibprüfung: {e}"
            )
            self._enabled = False

    def _initialize_custom_dictionary(self) -> None:
        """Initialisiert das benutzerdefinierte Wörterbuch."""
        try:
            self.logger.info("Initialisiere benutzerdefiniertes Wörterbuch...")
            self._custom_dictionary = get_custom_dictionary()

            self.logger.info(
                f"Benutzerdefiniertes Wörterbuch geladen: {self._custom_dictionary.get_word_count()} Wörter"
            )
        except Exception as e:
            self.logger.error(
                f"Fehler beim Initialisieren des benutzerdefinierten Wörterbuchs: {e}"
            )
            self._custom_dictionary = None
            self._custom_dict_enabled = False

    def check_text(self, text: str) -> str | None:
        """
        Prüft und korrigiert einen Text.

        Args:
            text: Der zu prüfende Text

        Returns:
            Korrigierter Text oder None bei Fehlern
        """
        if not self._enabled or not self._spell_checker or not text.strip():
            return text

        try:
            corrected_text = text
            corrections_made = []

            # 1. Grammatikregeln anwenden
            if self._grammar_check:
                for rule in self._grammar_patterns:
                    if re.search(rule["pattern"], corrected_text, re.IGNORECASE):
                        old_text = corrected_text
                        if "correction" in rule:
                            corrected_text = re.sub(
                                rule["pattern"],
                                rule["correction"],
                                corrected_text,
                                flags=re.IGNORECASE,
                            )
                        else:
                            corrected_text = re.sub(
                                rule["pattern"],
                                rule["replacement"],
                                corrected_text,
                                flags=re.IGNORECASE,
                            )

                        if old_text != corrected_text:
                            corrections_made.append(f"Grammatik: {rule['description']}")

            # 2. Rechtschreibprüfung
            words = re.findall(r"\b[a-zA-ZäöüßÄÖÜ]+\b", corrected_text)

            # Filtere Wörter, die im benutzerdefinierten Wörterbuch sind
            if self._custom_dictionary:
                words_to_check = [
                    word for word in words if not self._custom_dictionary.has_word(word)
                ]
            else:
                words_to_check = words

            misspelled = self._spell_checker.unknown(words_to_check)

            if misspelled:
                if self._suggest_only:
                    self._print_suggestions(text, misspelled)
                elif self._auto_correct:
                    # Automatische Korrektur
                    for word in misspelled:
                        candidates = self._spell_checker.candidates(word)
                        if candidates:
                            best_candidate = min(
                                candidates, key=lambda x: abs(len(x) - len(word))
                            )
                            # Nur ersetzen wenn ähnlich genug
                            if self._is_similar_word(word, best_candidate):
                                corrected_text = re.sub(
                                    r"\b" + re.escape(word) + r"\b",
                                    best_candidate,
                                    corrected_text,
                                    flags=re.IGNORECASE,
                                )
                                corrections_made.append(
                                    f"Rechtschreibung: {word} -> {best_candidate}"
                                )

                # Automatisch unbekannte Wörter zum Wörterbuch hinzufügen (falls aktiviert)
                if self._auto_add_unknown and self._custom_dictionary:
                    for word in misspelled:
                        if (
                            self._custom_dictionary.get_word_count() < self._max_words
                            or self._max_words == 0
                        ):
                            if self._custom_dictionary.add_word(word):
                                self.logger.info(
                                    f"Wort '{word}' automatisch zum Wörterbuch hinzugefügt"
                                )
                        else:
                            self.logger.warning(
                                f"Wörterbuch ist voll ({self._max_words} Wörter), kann '{word}' nicht hinzufügen"
                            )

            # Ergebnis ausgeben
            if corrections_made and corrected_text != text:
                self.logger.info("Korrekturen angewendet:")
                for correction in corrections_made:
                    self.logger.info(f"  - {correction}")
                self.logger.info(f"  Vorher: {text}")
                self.logger.info(f"  Nachher: {corrected_text}")

            return corrected_text

        except Exception as e:
            self.logger.error(f"Fehler bei der Rechtschreibprüfung: {e}")
            return text

    def _is_similar_word(self, word1: str, word2: str) -> bool:
        """Prüft ob zwei Wörter ähnlich genug sind für eine Korrektur."""
        # Einfache Ähnlichkeitsprüfung
        if abs(len(word1) - len(word2)) > 2:
            return False

        # Levenshtein-ähnliche Prüfung (vereinfacht)
        if len(word1) <= 3:
            return word1.lower() == word2.lower()[: len(word1)]

        # Mindestens 60% der Buchstaben müssen übereinstimmen
        common_chars = set(word1.lower()) & set(word2.lower())
        similarity = len(common_chars) / max(len(word1), len(word2))
        return similarity >= 0.6

    def _print_suggestions(self, text: str, misspelled: set[str]) -> None:
        """Zeigt Korrekturvorschläge an."""
        self.logger.info(f"\nRechtschreibprüfung für: '{text}'")
        self.logger.info("=" * 50)

        for i, word in enumerate(misspelled, 1):
            if self._spell_checker:
                candidates = self._spell_checker.candidates(word)
                self.logger.info(f"{i}. Fehler: '{word}'")

                if candidates:
                    suggestions = list(candidates)[:3]  # Top 3
                    suggestions_str = ", ".join([f"'{s}'" for s in suggestions])
                    self.logger.info(f"   Vorschläge: {suggestions_str}")
                else:
                    self.logger.info("   Keine Vorschläge gefunden")
                self.logger.info("")

    def get_suggestions(self, text: str) -> list[dict[str, Any]]:
        """
        Gibt eine Liste von Korrekturvorschlägen zurück.

        Returns:
            Liste von Dictionaries mit Fehlerinformationen
        """
        if not self._enabled or not self._spell_checker or not text.strip():
            return []

        try:
            suggestions = []
            words = re.findall(r"\b[a-zA-ZäöüßÄÖÜ]+\b", text)

            # Filtere Wörter, die im benutzerdefinierten Wörterbuch sind
            if self._custom_dictionary:
                words_to_check = [
                    word for word in words if not self._custom_dictionary.has_word(word)
                ]
            else:
                words_to_check = words

            if self._spell_checker:
                misspelled = self._spell_checker.unknown(words_to_check)

                for word in misspelled:
                    candidates = self._spell_checker.candidates(word)
                    if candidates:
                        error_info = {
                            "error_text": word,
                            "replacements": list(candidates)[:5],  # Top 5 Vorschläge
                            "message": f"Möglicher Rechtschreibfehler: '{word}'",
                            "category": "spelling",
                        }
                        suggestions.append(error_info)

            return suggestions

        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der Vorschläge: {e}")
            return []

    def is_enabled(self) -> bool:
        """Prüft, ob die Rechtschreibprüfung aktiviert ist."""
        return self._enabled and self._spell_checker is not None

    def is_custom_dictionary_enabled(self) -> bool:
        """Prüft, ob das benutzerdefinierte Wörterbuch aktiviert ist."""
        return self._custom_dict_enabled and self._custom_dictionary is not None

    def add_custom_word(self, word: str) -> bool:
        """
        Fügt ein Wort zum benutzerdefinierten Wörterbuch hinzu.

        Args:
            word: Das hinzuzufügende Wort

        Returns:
            True wenn erfolgreich, False bei Fehlern
        """
        if not self.is_custom_dictionary_enabled():
            self.logger.warning("Benutzerdefiniertes Wörterbuch ist nicht aktiviert")
            return False

        if self._custom_dictionary:
            return self._custom_dictionary.add_word(word)
        return False

    def remove_custom_word(self, word: str) -> bool:
        """
        Entfernt ein Wort aus dem benutzerdefinierten Wörterbuch.

        Args:
            word: Das zu entfernende Wort

        Returns:
            True wenn erfolgreich, False bei Fehlern
        """
        if not self.is_custom_dictionary_enabled():
            self.logger.warning("Benutzerdefiniertes Wörterbuch ist nicht aktiviert")
            return False

        if self._custom_dictionary:
            return self._custom_dictionary.remove_word(word)
        return False

    def get_custom_words(self) -> list[str]:
        """
        Gibt alle Wörter aus dem benutzerdefinierten Wörterbuch zurück.

        Returns:
            Liste aller Wörter oder leere Liste wenn nicht aktiviert
        """
        if not self.is_custom_dictionary_enabled():
            return []

        if self._custom_dictionary:
            return self._custom_dictionary.get_all_words()
        return []

    def get_custom_word_count(self) -> int:
        """
        Gibt die Anzahl der Wörter im benutzerdefinierten Wörterbuch zurück.

        Returns:
            Anzahl der Wörter oder 0 wenn nicht aktiviert
        """
        if not self.is_custom_dictionary_enabled():
            return 0

        if self._custom_dictionary:
            return self._custom_dictionary.get_word_count()
        return 0

    def clear_custom_dictionary(self) -> bool:
        """
        Löscht alle Wörter aus dem benutzerdefinierten Wörterbuch.

        Returns:
            True wenn erfolgreich, False bei Fehlern
        """
        if not self.is_custom_dictionary_enabled():
            self.logger.warning("Benutzerdefiniertes Wörterbuch ist nicht aktiviert")
            return False

        if self._custom_dictionary:
            return self._custom_dictionary.clear_dictionary()
        return False

    def close(self) -> None:
        """Schließt den Spell Checker."""
        if self._spell_checker:
            try:
                # PySpellChecker braucht kein explizites Schließen
                self.logger.info("SpellChecker geschlossen")
            except Exception as e:
                self.logger.error(f"Fehler beim Schließen des SpellCheckers: {e}")
            finally:
                self._spell_checker = None

    def __del__(self) -> None:
        """Destruktor zum Aufräumen."""
        self.close()


# Globale Instanz für einfache Nutzung
_spell_checker: SpellChecker | None = None


def get_spell_checker() -> SpellChecker:
    """Gibt die globale SpellGrammarChecker-Instanz zurück."""
    global _spell_checker
    if _spell_checker is None:
        _spell_checker = SpellChecker()
    return _spell_checker


def check_and_correct_text(text: str) -> str:
    """
    Convenience-Funktion für schnelle Textkorrektur.

    Args:
        text: Der zu korrigierende Text

    Returns:
        Korrigierter Text
    """
    checker = get_spell_checker()
    result = checker.check_text(text)
    return result if result is not None else text


def add_custom_word(word: str) -> bool:
    """
    Convenience-Funktion zum Hinzufügen eines Wortes zum benutzerdefinierten Wörterbuch.

    Args:
        word: Das hinzuzufügende Wort

    Returns:
        True wenn erfolgreich, False bei Fehlern
    """
    checker = get_spell_checker()
    return checker.add_custom_word(word)


def remove_custom_word(word: str) -> bool:
    """
    Convenience-Funktion zum Entfernen eines Wortes aus dem benutzerdefinierten Wörterbuch.

    Args:
        word: Das zu entfernende Wort

    Returns:
        True wenn erfolgreich, False bei Fehlern
    """
    checker = get_spell_checker()
    return checker.remove_custom_word(word)


def get_custom_words() -> list[str]:
    """
    Convenience-Funktion zum Abrufen aller Wörter aus dem benutzerdefinierten Wörterbuch.

    Returns:
        Liste aller Wörter
    """
    checker = get_spell_checker()
    return checker.get_custom_words()


def get_custom_word_count() -> int:
    """
    Convenience-Funktion zum Abrufen der Anzahl der Wörter im benutzerdefinierten Wörterbuch.

    Returns:
        Anzahl der Wörter
    """
    checker = get_spell_checker()
    return checker.get_custom_word_count()
