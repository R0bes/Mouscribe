# src/custom_dictionary.py - Custom Dictionary Management for Mauscribe
"""
Custom dictionary management for Mauscribe application.
Allows users to add their own words to be considered correct during spell checking.
"""

import json
from pathlib import Path
from typing import Optional

from .logger import get_logger


class CustomDict:
    """
    Verwaltet ein benutzerdefiniertes Wörterbuch für die Rechtschreibprüfung.

    Benutzer können eigene Wörter hinzufügen, die dann als korrekt betrachtet werden.
    Das Wörterbuch wird in einer JSON-Datei gespeichert und automatisch geladen.
    """

    def __init__(self, dictionary_path: Optional[str] = None):
        """
        Initialisiert das benutzerdefinierte Wörterbuch.

        Args:
            dictionary_path: Pfad zur Wörterbuch-Datei (optional)
        """
        self.logger = get_logger(self.__class__.__name__)

        if dictionary_path is None:
            # Standard-Pfad im Benutzerverzeichnis
            user_dir = Path.home() / ".mauscribe"
            user_dir.mkdir(exist_ok=True)
            dictionary_path = str(user_dir / "custom_dictionary.json")
        self.dictionary_path = Path(dictionary_path)
        self._words: set[str] = set()
        self._load_dictionary()

    def _load_dictionary(self) -> None:
        """Lädt das Wörterbuch aus der JSON-Datei."""
        try:
            if self.dictionary_path and self.dictionary_path.exists():
                with open(self.dictionary_path, encoding="utf-8") as f:
                    data = json.load(f)
                    self._words = set(data.get("words", []))
            else:
                self.logger.info("Kein benutzerdefiniertes Wörterbuch gefunden, erstelle neues")
                self._words = set()
        except Exception as e:
            self.logger.error(f"Fehler beim Laden des Wörterbuchs: {e}")
            self._words = set()

    def _save_dictionary(self) -> None:
        """Speichert das Wörterbuch in die JSON-Datei."""
        try:
            if not self.dictionary_path:
                self.logger.error("Kein Wörterbuch-Pfad gesetzt")
                return

            # Stelle sicher, dass das Verzeichnis existiert
            self.dictionary_path.parent.mkdir(parents=True, exist_ok=True)

            data = {
                "words": sorted(list(self._words)),
                "metadata": {
                    "version": "1.0",
                    "created": str(Path().cwd()),
                    "total_words": len(self._words),
                },
            }

            with open(self.dictionary_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Wörterbuch gespeichert: {len(self._words)} Wörter")
        except Exception as e:
            self.logger.error(f"Fehler beim Speichern des Wörterbuchs: {e}")

    def add_word(self, word: str) -> bool:
        """
        Fügt ein Wort zum benutzerdefinierten Wörterbuch hinzu.

        Args:
            word: Das hinzuzufügende Wort

        Returns:
            True wenn erfolgreich hinzugefügt, False bei Fehlern
        """
        if not word or not word.strip():
            self.logger.warning("Leeres Wort kann nicht hinzugefügt werden")
            return False

        word = word.strip().lower()
        if word in self._words:
            self.logger.info(f"Wort '{word}' ist bereits im Wörterbuch vorhanden")
            return True

        try:
            self._words.add(word)
            self._save_dictionary()
            self.logger.info(f"Wort '{word}' erfolgreich zum Wörterbuch hinzugefügt")
            return True
        except Exception as e:
            self.logger.error(f"Fehler beim Hinzufügen des Wortes '{word}': {e}")
            return False

    def remove_word(self, word: str) -> bool:
        """
        Entfernt ein Wort aus dem benutzerdefinierten Wörterbuch.

        Args:
            word: Das zu entfernende Wort

        Returns:
            True wenn erfolgreich entfernt, False bei Fehlern
        """
        if not word or not word.strip():
            self.logger.warning("Leeres Wort kann nicht entfernt werden")
            return False

        word = word.strip().lower()
        if word not in self._words:
            self.logger.info(f"Wort '{word}' ist nicht im Wörterbuch vorhanden")
            return False

        try:
            self._words.remove(word)
            self._save_dictionary()
            self.logger.info(f"Wort '{word}' erfolgreich aus dem Wörterbuch entfernt")
            return True
        except Exception as e:
            self.logger.error(f"Fehler beim Entfernen des Wortes '{word}': {e}")
            return False

    def has_word(self, word: str) -> bool:
        """
        Prüft, ob ein Wort im benutzerdefinierten Wörterbuch vorhanden ist.

        Args:
            word: Das zu prüfende Wort

        Returns:
            True wenn das Wort vorhanden ist, False sonst
        """
        if not word or not word.strip():
            return False

        return word.strip().lower() in self._words

    def get_all_words(self) -> list[str]:
        """
        Gibt alle Wörter aus dem benutzerdefinierten Wörterbuch zurück.

        Returns:
            Liste aller Wörter (sortiert)
        """
        return sorted(list(self._words))

    def get_word_count(self) -> int:
        """
        Gibt die Anzahl der Wörter im Wörterbuch zurück.

        Returns:
            Anzahl der Wörter
        """
        return len(self._words)

    def clear_dictionary(self) -> bool:
        """
        Löscht alle Wörter aus dem Wörterbuch.

        Returns:
            True wenn erfolgreich gelöscht, False bei Fehlern
        """
        try:
            self._words.clear()
            self._save_dictionary()
            self.logger.info("Wörterbuch erfolgreich geleert")
            return True
        except Exception as e:
            self.logger.error(f"Fehler beim Leeren des Wörterbuchs: {e}")
            return False

    def import_words(self, words: list[str]) -> int:
        """
        Importiert eine Liste von Wörtern in das Wörterbuch.

        Args:
            words: Liste der zu importierenden Wörter

        Returns:
            Anzahl der erfolgreich importierten Wörter
        """
        if not words:
            return 0

        imported_count = 0
        for word in words:
            if self.add_word(word):
                imported_count += 1

        self.logger.info(f"{imported_count} von {len(words)} Wörtern erfolgreich importiert")
        return imported_count

    def export_words(self) -> list[str]:
        """
        Exportiert alle Wörter aus dem Wörterbuch.

        Returns:
            Liste aller Wörter
        """
        return self.get_all_words()

    def get_dictionary_info(self) -> dict:
        """
        Gibt Informationen über das Wörterbuch zurück.

        Returns:
            Dictionary mit Wörterbuch-Informationen
        """
        if not self.dictionary_path:
            return {
                "path": "Nicht gesetzt",
                "word_count": 0,
                "words": [],
                "exists": False,
                "file_size": 0,
            }

        return {
            "path": str(self.dictionary_path),
            "word_count": self.get_word_count(),
            "words": self.get_all_words(),
            "exists": self.dictionary_path.exists(),
            "file_size": (self.dictionary_path.stat().st_size if self.dictionary_path.exists() else 0),
        }


# Globale Instanz für einfache Nutzung
_custom_dictionary: Optional[CustomDict] = None


def get_custom_dictionary() -> CustomDict:
    """Gibt die globale CustomDictionary-Instanz zurück."""
    global _custom_dictionary
    if _custom_dictionary is None:
        _custom_dictionary = CustomDict()
    return _custom_dictionary


def add_custom_word(word: str) -> bool:
    """
    Convenience-Funktion zum Hinzufügen eines Wortes.

    Args:
        word: Das hinzuzufügende Wort

    Returns:
        True wenn erfolgreich, False bei Fehlern
    """
    dictionary = get_custom_dictionary()
    return dictionary.add_word(word)


def remove_custom_word(word: str) -> bool:
    """
    Convenience-Funktion zum Entfernen eines Wortes.

    Args:
        word: Das zu entfernende Wort

    Returns:
        True wenn erfolgreich, False bei Fehlern
    """
    dictionary = get_custom_dictionary()
    return dictionary.remove_word(word)


def is_custom_word(word: str) -> bool:
    """
    Convenience-Funktion zum Prüfen, ob ein Wort im Wörterbuch ist.

    Args:
        word: Das zu prüfende Wort

    Returns:
        True wenn das Wort im Wörterbuch ist, False sonst
    """
    dictionary = get_custom_dictionary()
    return dictionary.has_word(word)
