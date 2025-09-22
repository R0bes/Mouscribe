#!/usr/bin/env python3
"""
Debug-Test für das Widgetsystem - zeigt genau was passiert
"""

import os
import sys
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def debug_widget_creation():
    """Debug-Widget-Erstellung."""
    print("=== Widget-Debug-Test ===")

    try:
        from src.ui.widgets import TextWidget, WidgetConfig, WidgetTheme

        print("1. Importe erfolgreich")

        # Erstelle Widget mit Debug-Ausgaben
        print("2. Erstelle TextWidget...")
        config = WidgetConfig(
            theme=WidgetTheme.DARK, auto_hide_duration=None, fade_duration=0  # Kein Auto-Hide  # Keine Fade-Animation
        )

        widget = TextWidget("Debug Test Widget", config)
        print(f"   Widget erstellt: {widget}")
        print(f"   Widget sichtbar: {widget.is_visible}")
        print(f"   Widget Fenster: {widget.window}")

        print("3. Zeige Widget...")
        result = widget.show_at_position(200, 200)
        print(f"   show_at_position Ergebnis: {result}")
        print(f"   Widget sichtbar nach show: {widget.is_visible}")
        print(f"   Widget Fenster nach show: {widget.window}")

        if widget.window:
            print(f"   Fenster-Geometrie: {widget.window.geometry()}")
            print(f"   Fenster sichtbar: {widget.window.winfo_viewable()}")
            print(f"   Fenster Zustand: {widget.window.state()}")

        print("4. Warte 3 Sekunden...")
        for i in range(3, 0, -1):
            print(f"   {i}...", end="\r")
            time.sleep(1)

        print("\n5. Verstecke Widget...")
        widget.hide()
        print(f"   Widget sichtbar nach hide: {widget.is_visible}")

        print("✓ Debug-Test abgeschlossen!")
        return True

    except Exception as e:
        print(f"✗ Debug-Test fehlgeschlagen: {e}")
        import traceback

        traceback.print_exc()
        return False


def debug_transcription_widget():
    """Debug TranscriptionWidget."""
    print("\n=== TranscriptionWidget-Debug ===")

    try:
        from src.ui.transcription_widget import TranscriptionWidget

        print("1. Erstelle TranscriptionWidget...")
        widget = TranscriptionWidget()
        print(f"   Widget erstellt: {widget}")
        print(f"   Widget sichtbar: {widget.is_visible}")
        print(f"   Widget root: {widget.root}")
        print(f"   Widget window: {widget.window}")

        print("2. Zeige Widget...")
        widget.show("Debug Transkription", 0.9, 300, 300)
        print(f"   Widget sichtbar nach show: {widget.is_visible}")
        print(f"   Widget window nach show: {widget.window}")

        if widget.window:
            print(f"   Fenster-Geometrie: {widget.window.geometry()}")
            print(f"   Fenster sichtbar: {widget.window.winfo_viewable()}")

        print("3. Warte 3 Sekunden...")
        for i in range(3, 0, -1):
            print(f"   {i}...", end="\r")
            time.sleep(1)

        print("\n4. Verstecke Widget...")
        widget.hide()
        print(f"   Widget sichtbar nach hide: {widget.is_visible}")

        print("✓ TranscriptionWidget-Debug abgeschlossen!")
        return True

    except Exception as e:
        print(f"✗ TranscriptionWidget-Debug fehlgeschlagen: {e}")
        import traceback

        traceback.print_exc()
        return False


def simple_widget_test():
    """Einfacher Widget-Test ohne komplexe Features."""
    print("\n=== Einfacher Widget-Test ===")

    try:
        import tkinter as tk

        print("1. Erstelle einfaches tkinter-Fenster...")
        root = tk.Tk()
        root.title("Einfaches Widget")
        root.geometry("300x200")
        root.configure(bg="lightblue")

        # Label
        label = tk.Label(root, text="Einfaches Widget\nDas sollte sichtbar sein!", font=("Arial", 12), bg="lightblue")
        label.pack(pady=50)

        print("2. Zeige Fenster...")
        root.update()
        root.deiconify()

        print("3. Warte 5 Sekunden...")
        for i in range(5, 0, -1):
            print(f"   {i}...", end="\r")
            root.update()
            time.sleep(1)

        print("\n4. Schließe Fenster...")
        root.destroy()

        print("✓ Einfacher Widget-Test abgeschlossen!")
        return True

    except Exception as e:
        print(f"✗ Einfacher Widget-Test fehlgeschlagen: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Widget-Debug-Test")
    print("=" * 25)

    # Test 1: Einfacher tkinter-Test
    success1 = simple_widget_test()

    if success1:
        # Test 2: Widget-Debug
        success2 = debug_widget_creation()

        if success2:
            # Test 3: TranscriptionWidget-Debug
            debug_transcription_widget()

    print("\n" + "=" * 25)
    if success1:
        print("✓ Grundlegende Widget-Funktionalität funktioniert!")
    else:
        print("✗ Grundlegende Widget-Funktionalität hat Probleme!")
