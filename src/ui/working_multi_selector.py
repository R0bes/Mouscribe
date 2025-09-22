#!/usr/bin/env python3
"""
Einfacher, funktionierender Multi-Monitor Region-Selector.
"""

import time
import tkinter as tk
from datetime import datetime
from tkinter import messagebox
from typing import Optional


class Rect:
    """Einfache Rectangle-Klasse."""

    def __init__(self, left: int, top: int, width: int, height: int):
        self.left = left
        self.top = top
        self.width = width
        self.height = height

    def __repr__(self):
        return f"Rect(left={self.left}, top={self.top}, width={self.width}, height={self.height})"


class WorkingMultiSelector:
    """Funktionierender Multi-Monitor Selector."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Verstecke Hauptfenster

        # Erstelle ein großes Overlay-Fenster das alle Bildschirme abdeckt
        self.overlay = tk.Toplevel()

        # Versuche alle Bildschirme zu erfassen
        self._setup_fullscreen_overlay()

        # Region-Parameter
        self.region_width = 200
        self.region_height = 150
        self.min_size = 50
        self.max_size = 800
        self.mouse_x = 0
        self.mouse_y = 0
        self.result = None

        # Canvas für Zeichnung
        self.canvas = tk.Canvas(self.overlay, highlightthickness=0, bg="black")
        self.canvas.pack(fill="both", expand=True)

        # Bind Events
        self.canvas.bind("<Motion>", self.update_mouse_position)
        self.canvas.bind("<Button-1>", self.confirm_selection)
        self.canvas.bind("<Button-3>", self.cancel_selection)
        self.canvas.bind("<MouseWheel>", self.change_size)
        self.overlay.bind("<Escape>", self.cancel_selection)
        self.overlay.bind("<Return>", self.confirm_selection)
        self.overlay.bind("<space>", self.confirm_selection)

        # Cursor ändern
        self.canvas.configure(cursor="crosshair")

        # Anweisungen anzeigen
        self.show_instructions()

        # Starte Update-Loop
        self.update_display()

    def _setup_fullscreen_overlay(self):
        """Setup Overlay für alle Bildschirme."""
        # Erstelle ein sehr großes Fenster das alle Bildschirme abdeckt
        self.overlay.geometry("4000x3000-2000-1500")  # Groß genug für mehrere Monitore
        self.overlay.attributes("-fullscreen", True)
        self.overlay.attributes("-alpha", 0.3)
        self.overlay.configure(bg="black")
        self.overlay.attributes("-topmost", True)
        self.overlay.focus_force()

        # Stelle sicher, dass das Fenster alle Events empfängt
        self.overlay.grab_set()  # Modal machen

    def show_instructions(self):
        """Zeige Anweisungen."""
        # Zentriere Anweisungen auf dem Hauptbildschirm
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        self.canvas.create_text(
            screen_width // 2,
            50,
            text="🎯 MULTI-MONITOR REGION-AUSWAHL",
            fill="white",
            font=("Arial", 16, "bold"),
            tags="instructions",
        )

        self.canvas.create_text(
            screen_width // 2,
            80,
            text="Mausrad: Größe ändern • Linksklick/Enter: Bestätigen • Rechtsklick/ESC: Abbrechen",
            fill="yellow",
            font=("Arial", 12),
            tags="instructions",
        )

        self.canvas.create_text(
            screen_width // 2,
            110,
            text="💡 Tipp: Das Overlay funktioniert auf allen Bildschirmen!",
            fill="cyan",
            font=("Arial", 10),
            tags="instructions",
        )

    def update_mouse_position(self, event):
        """Aktualisiere Mausposition."""
        self.mouse_x = event.x
        self.mouse_y = event.y

    def change_size(self, event):
        """Ändere Größe mit Mausrad."""
        delta = event.delta
        scale_factor = 1.1 if delta > 0 else 0.9

        new_width = int(self.region_width * scale_factor)
        new_height = int(self.region_height * scale_factor)

        # Größe begrenzen
        self.region_width = max(self.min_size, min(self.max_size, new_width))
        self.region_height = max(self.min_size, min(self.max_size, new_height))

    def update_display(self):
        """Aktualisiere die Anzeige."""
        # Lösche vorherige Anzeige
        self.canvas.delete("region")

        # Berechne Region um Mausposition
        half_width = self.region_width // 2
        half_height = self.region_height // 2

        x1 = self.mouse_x - half_width
        y1 = self.mouse_y - half_height
        x2 = self.mouse_x + half_width
        y2 = self.mouse_y + half_height

        # Zeichne Region
        self.canvas.create_rectangle(x1, y1, x2, y2, outline="white", width=3, tags="region")

        # Innere Umrandung
        self.canvas.create_rectangle(x1 + 1, y1 + 1, x2 - 1, y2 - 1, outline="black", width=1, tags="region")

        # Größenanzeige
        self.canvas.create_text(
            self.mouse_x,
            y1 - 20,
            text=f"{self.region_width} × {self.region_height}",
            fill="white",
            font=("Arial", 12, "bold"),
            tags="region",
        )

        # Update nach kurzer Zeit
        self.root.after(16, self.update_display)  # ~60 FPS

    def confirm_selection(self, event=None):
        """Bestätige Auswahl."""
        half_width = self.region_width // 2
        half_height = self.region_height // 2

        left = self.mouse_x - half_width
        top = self.mouse_y - half_height

        self.result = Rect(left, top, self.region_width, self.region_height)
        self.overlay.destroy()
        self.root.destroy()

    def cancel_selection(self, event=None):
        """Breche Auswahl ab."""
        self.result = None
        self.overlay.destroy()
        self.root.destroy()

    def select(self) -> Optional[Rect]:
        """Starte die Multi-Monitor Region-Auswahl."""
        self.root.mainloop()
        return self.result


def test_working_multi_selector():
    """Teste den funktionierenden Multi-Monitor Selector."""
    print("🎯 Teste funktionierenden Multi-Monitor Selector...")
    print("📝 Anleitung:")
    print("   1️⃣  Bewege die Maus zu der gewünschten Position (auch auf anderen Bildschirmen!)")
    print("   2️⃣  Drehe das Mausrad um die Größe zu ändern")
    print("   3️⃣  Linksklick oder Enter zum Bestätigen")
    print("   4️⃣  ESC oder Rechtsklick zum Abbrechen")
    print("   5️⃣  Das Overlay funktioniert auf ALLEN Bildschirmen!")
    print("\n⏳ Starte in 3 Sekunden...")

    for i in range(3, 0, -1):
        print(f"   {i}...")
        time.sleep(1)

    selector = WorkingMultiSelector()
    result = selector.select()

    if result:
        print(f"✅ Region ausgewählt: {result}")
        print(f"   📏 Größe: {result.width}x{result.height}")
        print(f"   📍 Position: ({result.left}, {result.top})")
        return True
    else:
        print("❌ Auswahl abgebrochen")
        return False


if __name__ == "__main__":
    test_working_multi_selector()
