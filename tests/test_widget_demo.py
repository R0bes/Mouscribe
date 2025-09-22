#!/usr/bin/env python3
"""
Demo-Test für das Widgetsystem - zeigt Widgets visuell an
Nur für manuelle Tests, nicht für automatische Testläufe
"""

import os
import sys
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def demo_widget_system():
    """Demo des Widgetsystems."""
    print("=== Mauscribe Widget System Demo ===")

    try:
        from src.ui.transcription_widget import TranscriptionWidgetManager
        from src.ui.widgets import (
            MouseOverlayManager,
            WidgetPosition,
            WidgetTheme,
            create_recording_widget,
            create_text_widget,
        )

        print("✓ Widget-Module erfolgreich importiert")

        # Demo 1: Text-Widget
        print("\n1. Erstelle Text-Widget...")
        text_widget = create_text_widget("Hallo Welt!", WidgetTheme.DARK)
        print(f"   Text-Widget erstellt: '{text_widget.text}'")
        print(f"   Theme: {text_widget.config.theme.name}")

        # Demo 2: Recording-Widget
        print("\n2. Erstelle Recording-Widget...")
        recording_widget = create_recording_widget(WidgetPosition.TOP_RIGHT)
        print("   Recording-Widget erstellt")
        print(f"   Position: {recording_widget.config.position.name}")
        print(f"   Theme: {recording_widget.config.theme.name}")

        # Demo 3: Transcription-Widget-Manager
        print("\n3. Erstelle Transcription-Widget-Manager...")
        manager = TranscriptionWidgetManager()
        print("   Manager erstellt")

        # Demo 4: Mouse-Overlay-Manager
        print("\n4. Erstelle Mouse-Overlay-Manager...")
        overlay_manager = MouseOverlayManager()
        overlay_manager.register_widget("demo_text", text_widget)
        overlay_manager.register_widget("demo_recording", recording_widget)
        print(f"   Manager erstellt mit {len(overlay_manager.widgets)} Widgets")

        # Demo 5: Widget-Konfigurationen
        print("\n5. Widget-Konfigurationen:")
        print(f"   Text-Widget Position: {text_widget.config.position.name}")
        print(f"   Text-Widget Auto-Hide: {text_widget.config.auto_hide_duration}s")
        print(f"   Recording-Widget Alpha: {recording_widget.config.alpha}")

        print("\n✓ Alle Widget-Demos erfolgreich!")
        print("\nHinweis: Für visuelle Tests müssen die Widgets mit show_at_position() angezeigt werden.")

    except ImportError as e:
        print(f"✗ Import-Fehler: {e}")
        return False
    except Exception as e:
        print(f"✗ Unerwarteter Fehler: {e}")
        return False

    return True


def demo_widget_themes():
    """Demo der verfügbaren Themes."""
    print("\n=== Widget Themes Demo ===")

    try:
        from src.ui.widgets import WidgetTheme

        themes = [WidgetTheme.DARK, WidgetTheme.LIGHT, WidgetTheme.RECORDING, WidgetTheme.SUCCESS]

        for theme in themes:
            print(f"\n{theme.name}:")
            print(f"  Hintergrund: {theme.value['bg']}")
            print(f"  Vordergrund: {theme.value['fg']}")
            print(f"  Rahmen: {theme.value['border']}")
            print(f"  Transparenz: {theme.value['alpha']}")

        print("\n✓ Alle Themes erfolgreich geladen!")

    except Exception as e:
        print(f"✗ Theme-Demo-Fehler: {e}")


def demo_widget_positions():
    """Demo der verfügbaren Positionen."""
    print("\n=== Widget Positionen Demo ===")

    try:
        from src.ui.widgets import WidgetPosition

        positions = [
            WidgetPosition.TOP_RIGHT,
            WidgetPosition.TOP_LEFT,
            WidgetPosition.BOTTOM_RIGHT,
            WidgetPosition.BOTTOM_LEFT,
            WidgetPosition.RIGHT,
            WidgetPosition.LEFT,
        ]

        for position in positions:
            x, y = position.value
            print(f"{position.name}: Offset ({x}, {y})")

        print("\n✓ Alle Positionen erfolgreich geladen!")

    except Exception as e:
        print(f"✗ Position-Demo-Fehler: {e}")


if __name__ == "__main__":
    print("Mauscribe Widget System - Demo")
    print("=" * 40)

    success = demo_widget_system()
    if success:
        demo_widget_themes()
        demo_widget_positions()

        print("\n" + "=" * 40)
        print("Demo abgeschlossen! Das Widgetsystem funktioniert korrekt.")
    else:
        print("\n" + "=" * 40)
        print("Demo fehlgeschlagen! Bitte überprüfen Sie die Installation.")
