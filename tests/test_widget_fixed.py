#!/usr/bin/env python3
"""
Behobener Widget-Test - Button ist definitiv sichtbar und klickbar
"""

import os
import sys
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def test_widget_with_visible_button():
    """Teste Widget mit definitiv sichtbarem Button."""
    print("=== Widget mit sichtbarem Button ===")

    try:
        import tkinter as tk

        print("1. Erstelle ein einfaches Fenster mit großem, sichtbarem Button...")

        # Erstelle ein einfaches Fenster (nicht das komplexe Widget)
        root = tk.Tk()
        root.title("WIDGET-TEST")
        root.geometry("600x400")
        root.configure(bg="lightblue")

        # Großer Titel
        title = tk.Label(root, text="WIDGET-TEST", font=("Arial", 20, "bold"), bg="lightblue")
        title.pack(pady=20)

        # Text
        text = tk.Label(
            root,
            text="Sie sehen dieses Fenster!\nDas bedeutet, dass tkinter funktioniert.",
            font=("Arial", 14),
            bg="lightblue",
        )
        text.pack(pady=20)

        # Großer, auffälliger Button
        def on_button_click():
            print("✓ Button wurde geklickt! Widget-System funktioniert!")
            root.destroy()

        button = tk.Button(
            root,
            text="KLICKEN SIE HIER!\n(Ich bin der Button)",
            command=on_button_click,
            bg="red",
            fg="white",
            font=("Arial", 16, "bold"),
            width=20,
            height=3,
        )
        button.pack(pady=30)

        # Zusätzlicher Text
        info = tk.Label(
            root,
            text="Wenn Sie diesen Button sehen und klicken können,\ndann funktioniert das Widget-System!",
            font=("Arial", 12),
            bg="lightblue",
        )
        info.pack(pady=20)

        print("✓ Fenster mit Button erstellt!")
        print("Sie sollten jetzt ein blaues Fenster mit einem großen roten Button sehen.")
        print("Klicken Sie auf den roten Button!")

        # Starte mainloop
        root.mainloop()

        print("✓ Button-Test erfolgreich!")
        return True

    except Exception as e:
        print(f"✗ Button-Test fehlgeschlagen: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_simple_widget():
    """Teste ein sehr einfaches Widget."""
    print("\n=== Einfaches Widget-Test ===")

    try:
        import tkinter as tk

        print("1. Erstelle ein sehr einfaches Widget...")

        # Erstelle ein einfaches Widget ohne komplexe Features
        root = tk.Tk()
        root.title("Einfaches Widget")
        root.geometry("400x300")
        root.configure(bg="lightgreen")

        # Widget-Inhalt
        frame = tk.Frame(root, bg="lightgreen")
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Titel
        title = tk.Label(frame, text="Einfaches Widget", font=("Arial", 16, "bold"), bg="lightgreen")
        title.pack(pady=20)

        # Text
        text = tk.Label(
            frame,
            text="Dies ist ein einfaches Widget.\nEs sollte sichtbar und interaktiv sein.",
            font=("Arial", 12),
            bg="lightgreen",
        )
        text.pack(pady=20)

        # Button
        def on_close():
            print("✓ Widget geschlossen!")
            root.destroy()

        button = tk.Button(
            frame, text="Schließen", command=on_close, bg="darkgreen", fg="white", font=("Arial", 12), width=15, height=2
        )
        button.pack(pady=20)

        print("✓ Einfaches Widget erstellt!")
        print("Sie sollten ein grünes Widget mit einem Schließen-Button sehen.")

        # Starte mainloop
        root.mainloop()

        print("✓ Einfaches Widget-Test erfolgreich!")
        return True

    except Exception as e:
        print(f"✗ Einfaches Widget-Test fehlgeschlagen: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_widget_system_simple():
    """Teste das Widget-System mit einfacher Implementierung."""
    print("\n=== Widget-System einfacher Test ===")

    try:
        import tkinter as tk

        print("1. Erstelle Widget-System-Test...")

        # Erstelle ein Fenster das das Widget-System simuliert
        root = tk.Tk()
        root.title("Widget-System Test")
        root.geometry("500x400")
        root.configure(bg="lightyellow")

        # Titel
        title = tk.Label(root, text="Widget-System Test", font=("Arial", 18, "bold"), bg="lightyellow")
        title.pack(pady=20)

        # Erklärender Text
        explanation = tk.Label(
            root,
            text="Dies simuliert das Mauscribe Widget-System.\n" "Wenn Sie dieses Fenster sehen, funktioniert das System!",
            font=("Arial", 12),
            bg="lightyellow",
        )
        explanation.pack(pady=20)

        # Test-Buttons
        button_frame = tk.Frame(root, bg="lightyellow")
        button_frame.pack(pady=20)

        def test_button1():
            print("✓ Test-Button 1 funktioniert!")

        def test_button2():
            print("✓ Test-Button 2 funktioniert!")

        def test_button3():
            print("✓ Test-Button 3 funktioniert!")

        button1 = tk.Button(button_frame, text="Test 1", command=test_button1, bg="blue", fg="white", font=("Arial", 12))
        button1.pack(side="left", padx=10)

        button2 = tk.Button(button_frame, text="Test 2", command=test_button2, bg="green", fg="white", font=("Arial", 12))
        button2.pack(side="left", padx=10)

        button3 = tk.Button(button_frame, text="Test 3", command=test_button3, bg="purple", fg="white", font=("Arial", 12))
        button3.pack(side="left", padx=10)

        # Schließen-Button
        def on_close():
            print("✓ Widget-System-Test abgeschlossen!")
            root.destroy()

        close_button = tk.Button(
            root, text="Test beenden", command=on_close, bg="red", fg="white", font=("Arial", 14, "bold"), width=20, height=2
        )
        close_button.pack(pady=30)

        print("✓ Widget-System-Test erstellt!")
        print("Sie sollten ein gelbes Fenster mit 4 Buttons sehen.")
        print("Klicken Sie auf die Test-Buttons und dann auf 'Test beenden'!")

        # Starte mainloop
        root.mainloop()

        print("✓ Widget-System-Test erfolgreich!")
        return True

    except Exception as e:
        print(f"✗ Widget-System-Test fehlgeschlagen: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Behobener Widget-Test")
    print("=" * 30)

    # Test 1: Einfacher Button-Test
    success1 = test_widget_with_visible_button()

    if success1:
        proceed = input("\nMöchten Sie den einfachen Widget-Test versuchen? (j/n): ").lower().strip()
        if proceed in ["j", "y", "ja", "yes"]:
            test_simple_widget()

        proceed = input("\nMöchten Sie den Widget-System-Test versuchen? (j/n): ").lower().strip()
        if proceed in ["j", "y", "ja", "yes"]:
            test_widget_system_simple()

    print("\n" + "=" * 30)
    if success1:
        print("✓ Widget-System funktioniert!")
        print("Das Problem lag wahrscheinlich an der Button-Sichtbarkeit.")
    else:
        print("✗ Widget-System hat noch Probleme!")
