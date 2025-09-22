#!/usr/bin/env python3
"""
Einfacher visueller Widget-Demo - zeigt Widgets automatisch an
"""

import os
import sys
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def show_widgets():
    """Zeige Widgets auf dem Bildschirm."""
    print("=== Einfacher Widget-Demo ===")
    print("Erstelle und zeige Widgets...")

    try:
        from src.ui.transcription_widget import TranscriptionWidgetManager
        from src.ui.widgets import WidgetTheme, create_text_widget

        # Widget 1: Text-Widget
        print("1. Erstelle Text-Widget...")
        text_widget = create_text_widget("Hallo! Dies ist ein sichtbares Widget", WidgetTheme.DARK)
        text_widget.show_at_position(200, 100)
        print("   ✓ Text-Widget angezeigt")

        # Widget 2: Transcription-Widget
        print("2. Erstelle Transcription-Widget...")
        manager = TranscriptionWidgetManager()
        manager.show_transcription("Test-Transkription: Das Widgetsystem funktioniert!", 0.9, 200, 250)
        print("   ✓ Transcription-Widget angezeigt")

        # Widget 3: Weitere Text-Widgets
        print("3. Erstelle weitere Widgets...")
        widget2 = create_text_widget("Widget 2: Verschiedene Themes", WidgetTheme.LIGHT)
        widget2.show_at_position(500, 100)

        widget3 = create_text_widget("Widget 3: Success Theme", WidgetTheme.SUCCESS)
        widget3.show_at_position(200, 400)

        widget4 = create_text_widget("Widget 4: Recording Theme", WidgetTheme.RECORDING)
        widget4.show_at_position(500, 400)

        print("   ✓ Alle Widgets angezeigt")

        print("\n=== Widgets sind jetzt sichtbar! ===")
        print("Sie sollten 5 Widgets auf Ihrem Bildschirm sehen:")
        print("- 1 Text-Widget (oben links)")
        print("- 1 Transcription-Widget (mitte links)")
        print("- 3 weitere Text-Widgets (verschiedene Themes)")
        print("\nDie Widgets werden automatisch nach 10 Sekunden versteckt...")

        # Warte 10 Sekunden
        for i in range(10, 0, -1):
            print(f"Verstecken in {i} Sekunden...", end="\r")
            time.sleep(1)

        print("\nVerstecke alle Widgets...")

        # Verstecke alle Widgets
        text_widget.hide()
        manager.hide_transcription()
        widget2.hide()
        widget3.hide()
        widget4.hide()

        print("✓ Alle Widgets versteckt")
        print("✓ Demo erfolgreich abgeschlossen!")

        return True

    except ImportError as e:
        print(f"✗ Import-Fehler: {e}")
        print("Stellen Sie sicher, dass alle Abhängigkeiten installiert sind:")
        print("- tkinter (sollte mit Python kommen)")
        print("- pywin32 (für Windows-Features)")
        return False
    except Exception as e:
        print(f"✗ Fehler: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Mauscribe Widget System - Einfacher Demo")
    print("=" * 45)

    success = show_widgets()

    if success:
        print("\n" + "=" * 45)
        print("✓ Widget-Demo erfolgreich!")
        print("Das Widgetsystem zeigt Widgets korrekt an.")
    else:
        print("\n" + "=" * 45)
        print("✗ Widget-Demo fehlgeschlagen!")
        print("Bitte überprüfen Sie die Installation.")
