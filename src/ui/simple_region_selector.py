#!/usr/bin/env python3
"""
Einfacher, funktionierender Region-Selector ohne komplexe Overlays.
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


class SimpleRegionSelector:
    """Einfacher Region-Selector der wirklich funktioniert."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Verstecke Hauptfenster

        # Erstelle Overlay-Fenster
        self.overlay = tk.Toplevel()
        self.overlay.attributes("-fullscreen", True)
        self.overlay.attributes("-alpha", 0.3)  # Semi-transparent
        self.overlay.configure(bg="black")
        self.overlay.attributes("-topmost", True)
        self.overlay.focus_force()  # Wichtig: Fokus erzwingen

        # Multi-Monitor Support
        self.current_screen = 0
        self.total_screens = self._get_screen_count()

        # Canvas für Zeichnung
        self.canvas = tk.Canvas(self.overlay, highlightthickness=0, bg="black")
        self.canvas.pack(fill="both", expand=True)

        # Region-Parameter
        self.region_width = 200
        self.region_height = 150
        self.min_size = 50
        self.max_size = 800
        self.mouse_x = 0
        self.mouse_y = 0
        self.result = None

        # Bind Events - WICHTIG: Alle Events fangen
        self.canvas.bind("<Motion>", self.update_mouse_position)
        self.canvas.bind("<Button-1>", self.confirm_selection)
        self.canvas.bind("<Button-3>", self.cancel_selection)  # Rechte Maustaste
        self.canvas.bind("<MouseWheel>", self.change_size)
        self.overlay.bind("<Escape>", self.cancel_selection)
        self.overlay.bind("<Return>", self.confirm_selection)
        self.overlay.bind("<space>", self.confirm_selection)

        # Multi-Monitor Tasten
        self.overlay.bind("<Left>", self.switch_screen_left)
        self.overlay.bind("<Right>", self.switch_screen_right)
        self.overlay.bind("<Tab>", self.switch_screen_next)

        # Cursor ändern
        self.canvas.configure(cursor="crosshair")

        # Anweisungen anzeigen
        self.show_instructions()

        # Starte Update-Loop
        self.update_display()

    def _get_screen_count(self):
        """Ermittle die Anzahl der Bildschirme."""
        try:
            import tkinter as tk

            root = tk.Tk()
            root.withdraw()
            screen_count = len(root.tk.call("winfo", "screen", "."))
            root.destroy()
            return max(1, screen_count)
        except Exception:
            return 1

    def switch_screen_left(self, event=None):
        """Wechsle zum linken Bildschirm."""
        if self.total_screens > 1:
            self.current_screen = (self.current_screen - 1) % self.total_screens
            self._update_screen_info()

    def switch_screen_right(self, event=None):
        """Wechsle zum rechten Bildschirm."""
        if self.total_screens > 1:
            self.current_screen = (self.current_screen + 1) % self.total_screens
            self._update_screen_info()

    def switch_screen_next(self, event=None):
        """Wechsle zum nächsten Bildschirm."""
        if self.total_screens > 1:
            self.current_screen = (self.current_screen + 1) % self.total_screens
            self._update_screen_info()

    def _update_screen_info(self):
        """Aktualisiere Bildschirm-Informationen."""
        self.canvas.delete("screen_info")
        if self.total_screens > 1:
            self.canvas.create_text(
                50,
                50,
                text=f"🖥️ Bildschirm {self.current_screen + 1}/{self.total_screens}",
                fill="cyan",
                font=("Arial", 14, "bold"),
                tags="screen_info",
            )

    def show_instructions(self):
        """Zeige Anweisungen."""
        self.canvas.create_text(
            self.overlay.winfo_screenwidth() // 2,
            50,
            text="🎯 REGION-AUSWAHL",
            fill="white",
            font=("Arial", 16, "bold"),
            tags="instructions",
        )

        instructions = [
            "Mausrad: Größe ändern",
            "Linksklick/Enter: Bestätigen",
            "Rechtsklick/ESC: Abbrechen",
        ]

        if self.total_screens > 1:
            instructions.extend(["Pfeiltasten/Tab: Bildschirm wechseln"])

        instruction_text = " • ".join(instructions)

        self.canvas.create_text(
            self.overlay.winfo_screenwidth() // 2,
            80,
            text=instruction_text,
            fill="yellow",
            font=("Arial", 12),
            tags="instructions",
        )

        # Zeige Bildschirm-Info
        self._update_screen_info()

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

        # Zeichne Region (transparentes Loch simulieren)
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
        """Starte die Region-Auswahl."""
        self.root.mainloop()
        return self.result


def test_simple_selector():
    """Teste den einfachen Selector."""
    print("🎯 Teste einfachen Region-Selector...")
    print("📝 Anleitung:")
    print("   1️⃣  Bewege die Maus zu der gewünschten Position")
    print("   2️⃣  Drehe das Mausrad um die Größe zu ändern")
    print("   3️⃣  Linksklick oder Enter zum Bestätigen")
    print("   4️⃣  ESC oder Rechtsklick zum Abbrechen")
    print("\n⏳ Starte in 3 Sekunden...")

    for i in range(3, 0, -1):
        print(f"   {i}...")
        time.sleep(1)

    selector = SimpleRegionSelector()
    result = selector.select()

    if result:
        print(f"✅ Region ausgewählt: {result}")
        return True
    else:
        print("❌ Auswahl abgebrochen")
        return False


if __name__ == "__main__":
    test_simple_selector()
