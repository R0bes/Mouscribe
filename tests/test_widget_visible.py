#!/usr/bin/env python3
"""
Test für sichtbare Widgets - zeigt Widgets an sehr sichtbaren Positionen
"""

import os
import sys
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def test_visible_widgets():
    """Teste Widgets an sehr sichtbaren Positionen."""
    print("=== Sichtbare Widget-Test ===")

    try:
        import tkinter as tk

        from src.ui.widgets import TextWidget, WidgetConfig, WidgetTheme

        print("1. Erstelle ein großes, auffälliges Widget...")

        # Erstelle ein sehr großes und auffälliges Widget
        config = WidgetConfig(
            theme=WidgetTheme.DARK,
            size="500x300",  # Sehr groß
            auto_hide_duration=None,  # Kein Auto-Hide
            fade_duration=0,  # Keine Animation
            alpha=1.0,  # Vollständig sichtbar
        )

        widget = TextWidget("GROSSES SICHTBARES WIDGET\nSie sollten das sehen können!", config)

        print("2. Zeige Widget in der Bildschirmmitte...")
        # Positioniere in der Bildschirmmitte
        widget.show_at_position(400, 300)

        print("3. Erstelle zusätzlich ein einfaches tkinter-Fenster zum Vergleich...")

        # Erstelle ein einfaches tkinter-Fenster zum Vergleich
        root = tk.Tk()
        root.title("VERGLEICHS-FENSTER")
        root.geometry("400x200")
        root.configure(bg="red")  # Sehr auffällige Farbe

        label = tk.Label(
            root, text="VERGLEICHS-FENSTER\nDas sollten Sie sehen!", font=("Arial", 16, "bold"), bg="red", fg="white"
        )
        label.pack(pady=50)

        root.update()
        root.deiconify()

        print("✓ Beide Fenster erstellt!")
        print("Sie sollten jetzt sehen:")
        print("- Ein großes dunkles Widget (500x300)")
        print("- Ein rotes Vergleichs-Fenster (400x200)")

        print("\nWarte 10 Sekunden...")
        for i in range(10, 0, -1):
            print(f"   {i}...", end="\r")
            time.sleep(1)

        print("\nSchließe alle Fenster...")
        widget.hide()
        root.destroy()

        print("✓ Sichtbarer Widget-Test abgeschlossen!")
        return True

    except Exception as e:
        print(f"✗ Sichtbarer Widget-Test fehlgeschlagen: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_widget_with_mainloop():
    """Teste Widget mit tkinter mainloop."""
    print("\n=== Widget mit Mainloop-Test ===")

    try:
        import tkinter as tk

        from src.ui.widgets import TextWidget, WidgetConfig, WidgetTheme

        print("1. Erstelle Widget mit mainloop...")

        # Erstelle Widget
        config = WidgetConfig(theme=WidgetTheme.SUCCESS, size="400x200", auto_hide_duration=None, fade_duration=0)

        widget = TextWidget("MAINLOOP WIDGET\nKlicken Sie auf 'Fertig' wenn Sie es sehen!", config)
        widget.show_at_position(300, 200)

        # Erstelle ein Kontroll-Fenster
        root = tk.Tk()
        root.title("Kontrolle")
        root.geometry("300x150")
        root.configure(bg="lightgreen")

        label = tk.Label(root, text="Kontrolle", font=("Arial", 14), bg="lightgreen")
        label.pack(pady=20)

        def on_finish():
            print("✓ Benutzer hat das Widget gesehen!")
            widget.hide()
            root.destroy()

        button = tk.Button(
            root, text="Ich sehe das Widget - Fertig!", command=on_finish, bg="green", fg="white", font=("Arial", 12)
        )
        button.pack(pady=20)

        print("✓ Widget und Kontroll-Fenster erstellt!")
        print("Sie sollten ein grünes Widget und ein Kontroll-Fenster sehen.")

        # Starte mainloop
        root.mainloop()

        print("✓ Mainloop-Test abgeschlossen!")
        return True

    except Exception as e:
        print(f"✗ Mainloop-Test fehlgeschlagen: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Sichtbarer Widget-Test")
    print("=" * 30)

    # Test 1: Große, auffällige Widgets
    success1 = test_visible_widgets()

    if success1:
        proceed = input("\nMöchten Sie den Mainloop-Test versuchen? (j/n): ").lower().strip()
        if proceed in ["j", "y", "ja", "yes"]:
            test_widget_with_mainloop()

    print("\n" + "=" * 30)
    if success1:
        print("✓ Widgets sollten sichtbar gewesen sein!")
    else:
        print("✗ Widget-Test fehlgeschlagen!")
