# src/dictionary_manager.py - Dictionary Management CLI for Mauscribe
"""
Command-line interface for managing the custom dictionary.
Provides easy access to add, remove, and view custom words.
"""

import argparse
import sys
from typing import List, Optional

from .custom_dictionary import CustomDictionary, get_custom_dictionary
from .spell_checker import get_spell_checker


def print_dictionary_info(dictionary: CustomDictionary) -> None:
    """Zeigt Informationen über das Wörterbuch an."""
    info = dictionary.get_dictionary_info()
    print("\n📚 Benutzerdefiniertes Wörterbuch")
    print(f"   Pfad: {info['path']}")
    print(f"   Anzahl Wörter: {info['word_count']}")
    print(f"   Datei existiert: {'Ja' if info['exists'] else 'Nein'}")
    if info["exists"]:
        print(f"   Dateigröße: {info['file_size']} Bytes")


def list_words(dictionary: CustomDictionary, limit: int = 0) -> None:
    """Zeigt alle Wörter im Wörterbuch an."""
    words = dictionary.get_all_words()

    if not words:
        print("📝 Das Wörterbuch ist leer.")
        return

    print(f"\n📝 Wörter im Wörterbuch ({len(words)}):")

    if limit > 0:
        words = words[:limit]
        print(f"   (Zeige nur die ersten {limit} Wörter)")

    for i, word in enumerate(words, 1):
        print(f"   {i:3d}. {word}")


def add_word(dictionary: CustomDictionary, word: str) -> None:
    """Fügt ein Wort zum Wörterbuch hinzu."""
    if dictionary.add_word(word):
        print(f"✅ Wort '{word}' erfolgreich zum Wörterbuch hinzugefügt")
    else:
        print(f"❌ Fehler beim Hinzufügen des Wortes '{word}'")


def remove_word(dictionary: CustomDictionary, word: str) -> None:
    """Entfernt ein Wort aus dem Wörterbuch."""
    if dictionary.remove_word(word):
        print(f"✅ Wort '{word}' erfolgreich aus dem Wörterbuch entfernt")
    else:
        print(f"❌ Fehler beim Entfernen des Wortes '{word}'")


def search_word(dictionary: CustomDictionary, word: str) -> None:
    """Sucht nach einem Wort im Wörterbuch."""
    if dictionary.has_word(word):
        print(f"✅ Wort '{word}' ist im Wörterbuch vorhanden")
    else:
        print(f"❌ Wort '{word}' ist nicht im Wörterbuch vorhanden")


def import_words(dictionary: CustomDictionary, words: List[str]) -> None:
    """Importiert eine Liste von Wörtern."""
    if not words:
        print("❌ Keine Wörter zum Importieren angegeben")
        return

    imported = dictionary.import_words(words)
    print(f"✅ {imported} von {len(words)} Wörtern erfolgreich importiert")


def export_words(dictionary: CustomDictionary, output_file: Optional[str] = None) -> None:
    """Exportiert alle Wörter aus dem Wörterbuch."""
    words = dictionary.export_words()

    if output_file:
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                for word in words:
                    f.write(word + "\n")
            print(f"✅ {len(words)} Wörter nach '{output_file}' exportiert")
        except Exception as e:
            print(f"❌ Fehler beim Exportieren: {e}")
    else:
        print(f"\n📤 Export ({len(words)} Wörter):")
        for word in words:
            print(word)


def clear_dictionary(dictionary: CustomDictionary) -> None:
    """Löscht alle Wörter aus dem Wörterbuch."""
    if dictionary.clear_dictionary():
        print("✅ Wörterbuch erfolgreich geleert")
    else:
        print("❌ Fehler beim Leeren des Wörterbuchs")


def main():
    """Hauptfunktion für die Kommandozeilen-Schnittstelle."""
    parser = argparse.ArgumentParser(
        description="Verwaltung des benutzerdefinierten Wörterbuchs für Mauscribe",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  %(prog)s list                    # Alle Wörter anzeigen
  %(prog)s add "Beispielwort"      # Wort hinzufügen
  %(prog)s remove "Beispielwort"   # Wort entfernen
  %(prog)s search "Beispielwort"   # Wort suchen
  %(prog)s import "wort1,wort2"    # Wörter importieren
  %(prog)s export output.txt       # Wörter exportieren
  %(prog)s clear                   # Wörterbuch leeren
        """,
    )

    parser.add_argument(
        "command", choices=["list", "add", "remove", "search", "import", "export", "clear", "info"], help="Befehl ausführen"
    )

    parser.add_argument("args", nargs="*", help="Argumente für den Befehl")

    parser.add_argument("--limit", "-l", type=int, default=0, help="Maximale Anzahl von Wörtern beim Auflisten (0 = alle)")

    parser.add_argument("--output", "-o", type=str, help="Ausgabedatei für Export-Befehl")

    args = parser.parse_args()

    try:
        # Wörterbuch initialisieren
        dictionary = get_custom_dictionary()

        # Befehle ausführen
        if args.command == "info":
            print_dictionary_info(dictionary)

        elif args.command == "list":
            list_words(dictionary, args.limit)

        elif args.command == "add":
            if not args.args:
                print("❌ Bitte geben Sie ein Wort zum Hinzufügen an")
                sys.exit(1)
            add_word(dictionary, args.args[0])

        elif args.command == "remove":
            if not args.args:
                print("❌ Bitte geben Sie ein Wort zum Entfernen an")
                sys.exit(1)
            remove_word(dictionary, args.args[0])

        elif args.command == "search":
            if not args.args:
                print("❌ Bitte geben Sie ein Wort zum Suchen an")
                sys.exit(1)
            search_word(dictionary, args.args[0])

        elif args.command == "import":
            if not args.args:
                print("❌ Bitte geben Sie Wörter zum Importieren an (kommagetrennt)")
                sys.exit(1)
            words = [w.strip() for w in args.args[0].split(",")]
            import_words(dictionary, words)

        elif args.command == "export":
            output_file = args.output or args.args[0] if args.args else None
            export_words(dictionary, output_file)

        elif args.command == "clear":
            clear_dictionary(dictionary)

        # Aktualisierte Informationen anzeigen
        if args.command not in ["info", "list"]:
            print_dictionary_info(dictionary)

    except KeyboardInterrupt:
        print("\n\n👋 Programm durch Benutzer beendet")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fehler: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
