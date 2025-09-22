#!/usr/bin/env python3
"""
Grundlegender tkinter-Test - zeigt ob tkinter überhaupt funktioniert
"""

import time
import tkinter as tk


def test_basic_tkinter():
    """Teste grundlegende tkinter-Funktionalität."""
    print("=== Grundlegender tkinter-Test ===")
    print("Erstelle ein einfaches tkinter-Fenster...")

    try:
        # Erstelle ein einfaches Fenster
        root = tk.Tk()
        root.title("Test Fenster")
        root.geometry("300x200")
        root.configure(bg="lightblue")

        # Füge einen Label hinzu
        label = tk.Label(root, text="Hallo! Dies ist ein Test-Fenster", font=("Arial", 14), bg="lightblue")
        label.pack(pady=50)

        # Füge einen Button hinzu
        button = tk.Button(
            root, text="Klicken Sie hier", command=lambda: print("Button wurde geklickt!"), bg="lightgreen", font=("Arial", 12)
        )
        button.pack(pady=20)

        print("✓ Fenster erstellt")
        print("Sie sollten jetzt ein blaues Fenster mit Text und Button sehen!")
        print("Das Fenster wird nach 5 Sekunden automatisch geschlossen...")

        # Zeige das Fenster
        root.update()
        root.deiconify()

        # Warte 5 Sekunden
        for i in range(5, 0, -1):
            print(f"Schließen in {i} Sekunden...", end="\r")
            root.update()
            time.sleep(1)

        print("\nSchließe Fenster...")
        root.destroy()

        print("✓ Grundlegender tkinter-Test erfolgreich!")
        return True

    except Exception as e:
        print(f"✗ tkinter-Test fehlgeschlagen: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_tkinter_with_input():
    """Teste tkinter mit Benutzereingabe."""
    print("\n=== tkinter-Test mit Benutzereingabe ===")

    try:
        root = tk.Tk()
        root.title("Interaktiver Test")
        root.geometry("400x300")
        root.configure(bg="lightyellow")

        # Titel
        title = tk.Label(root, text="Interaktiver tkinter-Test", font=("Arial", 16, "bold"), bg="lightyellow")
        title.pack(pady=20)

        # Text
        text = tk.Label(
            root,
            text="Dieses Fenster sollte sichtbar sein.\nKlicken Sie auf 'Fertig' wenn Sie es sehen.",
            font=("Arial", 12),
            bg="lightyellow",
        )
        text.pack(pady=20)

        # Button
        def on_click():
            print("✓ Benutzer hat das Fenster gesehen!")
            root.destroy()

        button = tk.Button(
            root,
            text="Ich sehe das Fenster - Fertig!",
            command=on_click,
            bg="lightgreen",
            font=("Arial", 12),
            padx=20,
            pady=10,
        )
        button.pack(pady=20)

        # Zeige das Fenster
        root.update()
        root.deiconify()

        print("✓ Interaktives Fenster erstellt")
        print("Sie sollten jetzt ein gelbes Fenster sehen!")
        print("Klicken Sie auf den Button, wenn Sie das Fenster sehen können.")

        # Starte die tkinter-Schleife
        root.mainloop()

        print("✓ Interaktiver Test erfolgreich!")
        return True

    except Exception as e:
        print(f"✗ Interaktiver Test fehlgeschlagen: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Grundlegender tkinter-Test")
    print("=" * 30)

    # Test 1: Automatischer Test
    success1 = test_basic_tkinter()

    if success1:
        print("\n" + "=" * 30)
        proceed = input("Möchten Sie den interaktiven Test versuchen? (j/n): ").lower().strip()
        if proceed in ["j", "y", "ja", "yes"]:
            test_tkinter_with_input()

    print("\n" + "=" * 30)
    if success1:
        print("✓ tkinter funktioniert grundsätzlich!")
    else:
        print("✗ tkinter hat Probleme!")
        print("Mögliche Ursachen:")
        print("- tkinter ist nicht installiert")
        print("- Display-Probleme")
        print("- Python-Installation unvollständig")
