#!/usr/bin/env python3
"""
Visueller Test für das Widgetsystem - zeigt tatsächlich Widgets auf dem Bildschirm an
"""

import os
import sys
import threading
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def visual_widget_test():
    """Visueller Test der Widgets."""
    print("=== Visueller Widget-Test ===")
    print("Widgets werden jetzt auf dem Bildschirm angezeigt...")
    print("Drücken Sie Enter, um fortzufahren...")

    try:
        from src.ui.transcription_widget import TranscriptionWidgetManager
        from src.ui.widgets import (
            WidgetConfig,
            WidgetPosition,
            WidgetTheme,
            Win32Widget,
            create_recording_widget,
            create_text_widget,
        )

        print("✓ Widget-Module erfolgreich importiert")

        # Test 1: Text-Widget anzeigen
        print("\n1. Zeige Text-Widget...")
        text_widget = create_text_widget("Hallo! Dies ist ein Test-Widget", WidgetTheme.DARK)
        text_widget.show_at_position(200, 100)
        print("   Text-Widget sollte jetzt sichtbar sein")

        input("   Drücken Sie Enter für das nächste Widget...")

        # Test 2: Recording-Widget anzeigen
        print("\n2. Zeige Recording-Widget...")
        recording_widget = create_recording_widget(WidgetPosition.TOP_RIGHT)
        recording_widget.show_at_position(500, 150)
        print("   Recording-Widget sollte jetzt sichtbar sein")

        input("   Drücken Sie Enter für das nächste Widget...")

        # Test 3: Transcription-Widget anzeigen
        print("\n3. Zeige Transcription-Widget...")
        manager = TranscriptionWidgetManager()
        manager.show_transcription("Dies ist eine Test-Transkription mit hoher Genauigkeit", 0.85, 300, 250)
        print("   Transcription-Widget sollte jetzt sichtbar sein")

        input("   Drücken Sie Enter für das nächste Widget...")

        # Test 4: Win32-Widget mit verschiedenen Themes
        print("\n4. Zeige Win32-Widgets mit verschiedenen Themes...")

        # Dark Theme
        dark_widget = Win32Widget("Dark Theme", WidgetConfig(theme=WidgetTheme.DARK))
        dark_widget.show_at_position(100, 300)
        print("   Dark Theme Widget angezeigt")

        time.sleep(1)

        # Light Theme
        light_widget = Win32Widget("Light Theme", WidgetConfig(theme=WidgetTheme.LIGHT))
        light_widget.show_at_position(400, 300)
        print("   Light Theme Widget angezeigt")

        time.sleep(1)

        # Success Theme
        success_widget = Win32Widget("Success Theme", WidgetConfig(theme=WidgetTheme.SUCCESS))
        success_widget.show_at_position(700, 300)
        print("   Success Theme Widget angezeigt")

        input("   Drücken Sie Enter, um alle Widgets zu verstecken...")

        # Verstecke alle Widgets
        print("\n5. Verstecke alle Widgets...")
        text_widget.hide()
        recording_widget.hide()
        manager.hide_transcription()
        dark_widget.hide()
        light_widget.hide()
        success_widget.hide()
        print("   Alle Widgets versteckt")

        print("\n✓ Visueller Test abgeschlossen!")

    except ImportError as e:
        print(f"✗ Import-Fehler: {e}")
        return False
    except Exception as e:
        print(f"✗ Unerwarteter Fehler: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


def interactive_widget_demo():
    """Interaktive Widget-Demo."""
    print("\n=== Interaktive Widget-Demo ===")
    print("Sie können jetzt mit den Widgets interagieren!")

    try:
        from src.ui.widgets import WidgetTheme, create_win32_widget

        # Erstelle interaktive Widgets
        widget1 = create_win32_widget("Interaktives Widget 1", WidgetTheme.DARK)
        widget2 = create_win32_widget("Interaktives Widget 2", WidgetTheme.SUCCESS)

        # Zeige Widgets
        widget1.show_at_position(200, 200)
        widget2.show_at_position(500, 200)

        print("✓ Zwei interaktive Widgets angezeigt")
        print("  - Sie können sie mit der Maus ziehen")
        print("  - Klicken Sie auf die Buttons")
        print("  - Schließen Sie sie mit dem X-Button")

        print("\nDrücken Sie Enter, wenn Sie fertig sind...")
        input()

        # Cleanup
        widget1.hide()
        widget2.hide()

        print("✓ Interaktive Demo abgeschlossen!")

    except Exception as e:
        print(f"✗ Demo-Fehler: {e}")
        return False

    return True


def widget_position_demo():
    """Demo der verschiedenen Widget-Positionen."""
    print("\n=== Widget-Positionen Demo ===")

    try:
        from src.ui.widgets import WidgetConfig, WidgetPosition, WidgetTheme, create_text_widget

        positions = [
            (WidgetPosition.TOP_RIGHT, "Oben Rechts"),
            (WidgetPosition.TOP_LEFT, "Oben Links"),
            (WidgetPosition.BOTTOM_RIGHT, "Unten Rechts"),
            (WidgetPosition.BOTTOM_LEFT, "Unten Links"),
            (WidgetPosition.RIGHT, "Rechts"),
            (WidgetPosition.LEFT, "Links"),
        ]

        widgets = []

        for i, (position, name) in enumerate(positions):
            config = WidgetConfig(position=position, theme=WidgetTheme.DARK)
            widget = create_text_widget(f"{name}\nPosition: {position.name}", config)
            widget.show_at_position(100 + (i % 3) * 300, 100 + (i // 3) * 150)
            widgets.append(widget)
            print(f"✓ {name} Widget angezeigt")
            time.sleep(0.5)

        print("\nAlle Positionen demonstriert!")
        input("Drücken Sie Enter, um alle zu verstecken...")

        for widget in widgets:
            widget.hide()

        print("✓ Positionen-Demo abgeschlossen!")

    except Exception as e:
        print(f"✗ Positionen-Demo-Fehler: {e}")
        return False

    return True


if __name__ == "__main__":
    print("Mauscribe Widget System - Visueller Test")
    print("=" * 50)

    print("Warnung: Dieser Test zeigt echte Widgets auf dem Bildschirm!")
    print("Stellen Sie sicher, dass Sie Platz auf dem Desktop haben.")

    proceed = input("\nMöchten Sie fortfahren? (j/n): ").lower().strip()
    if proceed not in ["j", "y", "ja", "yes"]:
        print("Test abgebrochen.")
        exit()

    # Führe visuelle Tests durch
    success1 = visual_widget_test()

    if success1:
        proceed = input("\nMöchten Sie die interaktive Demo sehen? (j/n): ").lower().strip()
        if proceed in ["j", "y", "ja", "yes"]:
            interactive_widget_demo()

        proceed = input("\nMöchten Sie die Positionen-Demo sehen? (j/n): ").lower().strip()
        if proceed in ["j", "y", "ja", "yes"]:
            widget_position_demo()

    print("\n" + "=" * 50)
    if success1:
        print("✓ Visueller Test erfolgreich abgeschlossen!")
        print("Das Widgetsystem funktioniert korrekt und zeigt Widgets an.")
    else:
        print("✗ Visueller Test fehlgeschlagen!")
        print("Bitte überprüfen Sie die Installation und Abhängigkeiten.")
