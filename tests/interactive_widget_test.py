#!/usr/bin/env python3
"""
Interaktiver Widget-Test - Sie können mit den Widgets interagieren
"""

import os
import sys
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def interactive_test():
    """Interaktiver Test mit Widgets."""
    print("=== Interaktiver Widget-Test ===")
    print("Sie können jetzt mit den Widgets interagieren!")

    try:
        from src.ui.transcription_widget import TranscriptionWidgetManager
        from src.ui.widgets import WidgetConfig, WidgetTheme, create_win32_widget

        # Erstelle verschiedene interaktive Widgets
        print("1. Erstelle interaktive Widgets...")

        # Widget 1: Standard-Widget
        widget1 = create_win32_widget("Interaktives Widget 1", WidgetTheme.DARK)
        widget1.show_at_position(100, 100)
        print("   ✓ Widget 1 angezeigt (oben links)")

        # Widget 2: Success-Theme
        config2 = WidgetConfig(theme=WidgetTheme.SUCCESS, auto_hide_duration=None)
        widget2 = create_win32_widget("Success Widget", config2)
        widget2.show_at_position(500, 100)
        print("   ✓ Widget 2 angezeigt (oben rechts)")

        # Widget 3: Recording-Theme
        config3 = WidgetConfig(theme=WidgetTheme.RECORDING, auto_hide_duration=None)
        widget3 = create_win32_widget("Recording Widget", config3)
        widget3.show_at_position(100, 300)
        print("   ✓ Widget 3 angezeigt (unten links)")

        # Widget 4: Transcription-Widget
        manager = TranscriptionWidgetManager()
        manager.show_transcription("Interaktive Transkription: Sie können diesen Text kopieren!", 0.95, 500, 300)
        print("   ✓ Transcription-Widget angezeigt (unten rechts)")

        print("\n=== Interaktionsmöglichkeiten ===")
        print("Sie können jetzt folgende Aktionen ausführen:")
        print("• Widgets mit der Maus ziehen (klicken und ziehen)")
        print("• Auf Buttons klicken")
        print("• Widgets mit dem X-Button schließen")
        print("• Text im Transcription-Widget kopieren")

        print("\nDie Widgets bleiben sichtbar, bis Sie sie manuell schließen.")
        print("Drücken Sie Enter, wenn Sie fertig sind...")

        input()

        print("\nVerstecke alle Widgets...")
        widget1.hide()
        widget2.hide()
        widget3.hide()
        manager.hide_transcription()

        print("✓ Interaktiver Test abgeschlossen!")
        return True

    except Exception as e:
        print(f"✗ Fehler: {e}")
        import traceback

        traceback.print_exc()
        return False


def widget_features_demo():
    """Demo der Widget-Features."""
    print("\n=== Widget-Features Demo ===")

    try:
        from src.ui.widgets import WidgetConfig, WidgetPosition, WidgetTheme, create_recording_widget, create_text_widget

        # Demo 1: Verschiedene Themes
        print("1. Verschiedene Themes:")
        themes = [
            (WidgetTheme.DARK, "Dark Theme"),
            (WidgetTheme.LIGHT, "Light Theme"),
            (WidgetTheme.SUCCESS, "Success Theme"),
            (WidgetTheme.RECORDING, "Recording Theme"),
        ]

        widgets = []
        for i, (theme, name) in enumerate(themes):
            widget = create_text_widget(
                f"{name}\nHintergrund: {theme.value['bg']}", WidgetConfig(theme=theme, auto_hide_duration=None)
            )
            widget.show_at_position(100 + (i % 2) * 400, 100 + (i // 2) * 150)
            widgets.append(widget)
            print(f"   ✓ {name} angezeigt")
            time.sleep(0.5)

        input("\nDrücken Sie Enter für die nächste Demo...")

        # Verstecke Theme-Widgets
        for widget in widgets:
            widget.hide()

        # Demo 2: Verschiedene Positionen
        print("\n2. Verschiedene Positionen:")
        positions = [
            (WidgetPosition.TOP_RIGHT, "Oben Rechts"),
            (WidgetPosition.TOP_LEFT, "Oben Links"),
            (WidgetPosition.BOTTOM_RIGHT, "Unten Rechts"),
            (WidgetPosition.BOTTOM_LEFT, "Unten Links"),
        ]

        widgets = []
        for i, (position, name) in enumerate(positions):
            config = WidgetConfig(position=position, theme=WidgetTheme.DARK, auto_hide_duration=None)
            widget = create_text_widget(f"{name}\nOffset: {position.value}", config)
            widget.show_at_position(200 + (i % 2) * 300, 200 + (i // 2) * 200)
            widgets.append(widget)
            print(f"   ✓ {name} angezeigt")
            time.sleep(0.5)

        input("\nDrücken Sie Enter, um alle zu verstecken...")

        for widget in widgets:
            widget.hide()

        print("✓ Features-Demo abgeschlossen!")
        return True

    except Exception as e:
        print(f"✗ Features-Demo-Fehler: {e}")
        return False


if __name__ == "__main__":
    print("Mauscribe Widget System - Interaktiver Test")
    print("=" * 50)

    print("Dieser Test zeigt interaktive Widgets auf dem Bildschirm.")
    print("Sie können mit ihnen interagieren!")

    proceed = input("\nMöchten Sie fortfahren? (j/n): ").lower().strip()
    if proceed not in ["j", "y", "ja", "yes"]:
        print("Test abgebrochen.")
        exit()

    # Führe interaktive Tests durch
    success1 = interactive_test()

    if success1:
        proceed = input("\nMöchten Sie die Features-Demo sehen? (j/n): ").lower().strip()
        if proceed in ["j", "y", "ja", "yes"]:
            widget_features_demo()

    print("\n" + "=" * 50)
    if success1:
        print("✓ Interaktiver Test erfolgreich!")
        print("Das Widgetsystem ist voll funktionsfähig.")
    else:
        print("✗ Interaktiver Test fehlgeschlagen!")
        print("Bitte überprüfen Sie die Installation.")
