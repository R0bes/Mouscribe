#!/usr/bin/env python3
"""
Transcription Widget für unsichere Transkriptionen
Zeigt Transkription direkt unter der Maus an
"""

import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Callable, Optional

try:
    import win32con
    import win32gui

    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


class TranscriptionWidget:
    """Widget für unsichere Transkriptionen."""

    def __init__(self, on_copy: Callable[[str], None] = None, on_close: Callable[[], None] = None):
        self.on_copy = on_copy or (lambda x: None)
        self.on_close = on_close or (lambda: None)

        self.root = None
        self.is_visible = False
        self.transcription_text = ""
        self.confidence = 0.0

        self._create_widget()

    def _create_widget(self):
        """Erstelle das Widget."""
        self.root = tk.Tk()
        self.root.withdraw()  # Verstecke Hauptfenster

        # Erstelle Toplevel-Fenster
        self.window = tk.Toplevel(self.root)
        self.window.withdraw()  # Starte versteckt
        self.window.overrideredirect(True)  # Entferne Fensterrahmen
        self.window.attributes("-topmost", True)  # Immer im Vordergrund
        self.window.attributes("-alpha", 0.9)  # Leicht transparent

        # Win32-spezifische Verbesserungen für bessere Transparenz
        if WIN32_AVAILABLE:
            try:
                self.window.update()  # Stelle sicher, dass Fenster existiert
                hwnd = self.window.winfo_id()
                extended_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, extended_style | win32con.WS_EX_LAYERED)
                win32gui.SetLayeredWindowAttributes(hwnd, 0, 230, win32con.LWA_ALPHA)
            except Exception as e:
                print(f"Win32 styling error: {e}")

        # Setze Größe
        self.window.geometry("400x200")

        # Erstelle Layout
        self._create_layout()

        # Setze Styling
        self._apply_styling()

    def _create_layout(self):
        """Erstelle Widget-Layout."""
        # Hauptframe mit helleren Farben
        main_frame = tk.Frame(self.window, bg="#FFFFFF", relief="raised", bd=2)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Header mit Titel und Schließen-Button
        header_frame = tk.Frame(main_frame, bg="#F8F9FA", relief="flat", bd=0)
        header_frame.pack(fill="x", pady=(0, 8))

        # Titel mit Icon
        self.title_label = tk.Label(
            header_frame,
            text="🎤 Mauscribe Transkription",
            font=("Arial", 14, "bold"),
            fg="#0066CC",  # Dunkles Blau für den Titel
            bg="#F8F9FA",
        )
        self.title_label.pack(side="left")

        # Confidence-Indikator
        self.confidence_label = tk.Label(
            header_frame, text="", font=("Arial", 12, "bold"), fg="#28A745", bg="#F8F9FA"  # Grün für hohe Confidence
        )
        self.confidence_label.pack(side="left", padx=(10, 0))

        # Schließen-Button
        close_button = tk.Button(
            header_frame,
            text="×",
            command=self.close,
            bg="#E74C3C",
            fg="white",
            font=("Arial", 14, "bold"),
            relief="flat",
            bd=0,
            width=3,
            height=1,
        )
        close_button.pack(side="right")

        # Text-Bereich
        text_frame = tk.Frame(main_frame, bg="#FFFFFF", relief="sunken", bd=1)
        text_frame.pack(fill="both", expand=True, pady=(0, 8))

        # Text mit Scrollbar und schönerem Styling
        self.text_widget = tk.Text(
            text_frame,
            wrap="word",
            font=("Arial", 12),  # Einfache Schriftart
            fg="#000000",  # Schwarzer Text
            bg="#FFFFFF",  # Weißer Hintergrund
            relief="flat",
            bd=0,
            padx=15,
            pady=15,
            state="disabled",
            selectbackground="#0066CC",
            selectforeground="white",
            cursor="xterm",
            insertbackground="#0066CC",  # Cursor-Farbe
        )

        scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=scrollbar.set)

        self.text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Button-Bereich
        button_frame = tk.Frame(main_frame, bg="#F8F9FA", relief="flat", bd=0)
        button_frame.pack(fill="x")

        # Kopieren-Button mit schönerem Styling
        self.copy_button = tk.Button(
            button_frame,
            text="📋 Kopieren",
            command=self.copy_text,
            bg="#3498DB",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            bd=0,
            padx=25,
            pady=10,
            cursor="hand2",
            activebackground="#2980B9",
            activeforeground="white",
        )
        self.copy_button.pack(side="left", padx=(0, 15))

        # Hover-Effekt für Kopieren-Button
        def on_copy_enter(e):
            self.copy_button.config(bg="#2980B9")

        def on_copy_leave(e):
            self.copy_button.config(bg="#3498DB")

        self.copy_button.bind("<Enter>", on_copy_enter)
        self.copy_button.bind("<Leave>", on_copy_leave)

        # Schließen-Button mit schönerem Styling
        self.close_button = tk.Button(
            button_frame,
            text="❌ Schließen",
            command=self.close,
            bg="#E74C3C",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            bd=0,
            padx=25,
            pady=10,
            cursor="hand2",
            activebackground="#C0392B",
            activeforeground="white",
        )
        self.close_button.pack(side="right")

        # Hover-Effekt für Schließen-Button
        def on_close_enter(e):
            self.close_button.config(bg="#C0392B")

        def on_close_leave(e):
            self.close_button.config(bg="#E74C3C")

        self.close_button.bind("<Enter>", on_close_enter)
        self.close_button.bind("<Leave>", on_close_leave)

        # Zusätzlicher Button für weitere Aktionen
        self.action_button = tk.Button(
            button_frame,
            text="✨ Aktionen",
            command=self.show_actions,
            bg="#9B59B6",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            bd=0,
            padx=25,
            pady=10,
            cursor="hand2",
            activebackground="#8E44AD",
            activeforeground="white",
        )
        self.action_button.pack(side="left", padx=(0, 15))

        # Hover-Effekt für Action-Button
        def on_action_enter(e):
            self.action_button.config(bg="#8E44AD")

        def on_action_leave(e):
            self.action_button.config(bg="#9B59B6")

        self.action_button.bind("<Enter>", on_action_enter)
        self.action_button.bind("<Leave>", on_action_leave)

        # Drag-Funktionalität
        self._setup_dragging()

    def _update_confidence_display(self, confidence: float):
        """Aktualisiere die Confidence-Anzeige mit Farben."""
        confidence_percent = int(confidence * 100)

        # Wähle Farbe basierend auf Confidence
        if confidence >= 0.8:
            color = "#2ECC71"  # Grün für hohe Confidence
            icon = "🟢"
        elif confidence >= 0.6:
            color = "#F39C12"  # Orange für mittlere Confidence
            icon = "🟡"
        else:
            color = "#E74C3C"  # Rot für niedrige Confidence
            icon = "🔴"

        # Aktualisiere Confidence-Label
        self.confidence_label.config(text=f"{icon} {confidence_percent}%", fg=color)

    def _apply_styling(self):
        """Wende Styling an."""
        # Abgerundete Ecken simulieren durch Padding
        pass

    def _setup_dragging(self):
        """Ermögliche das Ziehen des Widgets."""

        def start_drag(event):
            self.start_x = event.x
            self.start_y = event.y

        def drag_window(event):
            x = self.window.winfo_x() + (event.x - self.start_x)
            y = self.window.winfo_y() + (event.y - self.start_y)
            self.window.geometry(f"+{x}+{y}")

        # Bind Drag-Events
        self.window.bind("<Button-1>", start_drag)
        self.window.bind("<B1-Motion>", drag_window)

    def show(self, text: str, confidence: float, mouse_x: int, mouse_y: int):
        """Zeige Widget mit Transkription."""
        self.transcription_text = text
        self.confidence = confidence

        # Aktualisiere Text mit besserer Formatierung
        self.text_widget.config(state="normal")
        self.text_widget.delete(1.0, tk.END)

        # Füge Text mit Formatierung hinzu
        formatted_text = f"📝 Transkription:\n\n{text}\n\n💡 Tipp: Verwende die Buttons unten für weitere Aktionen!"
        self.text_widget.insert(1.0, formatted_text)

        # Konfiguriere Tags für verschiedene Textteile
        self.text_widget.tag_configure("header", foreground="#0066CC", font=("Arial", 12, "bold"))
        self.text_widget.tag_configure("content", foreground="#000000", font=("Arial", 12))
        self.text_widget.tag_configure("tip", foreground="#666666", font=("Arial", 10, "italic"))

        # Wende Tags an
        self.text_widget.tag_add("header", "1.0", "1.15")  # "📝 Transkription:"
        self.text_widget.tag_add("content", "3.0", f"3.{len(text)}")  # Der eigentliche Text
        self.text_widget.tag_add("tip", f"{len(formatted_text.splitlines())-1}.0", "end")  # Tipp

        self.text_widget.config(state="disabled")

        # Aktualisiere Confidence-Indikator
        self._update_confidence_display(confidence)

        # Positioniere Widget unter der Maus
        self._position_widget(mouse_x, mouse_y)

        # Zeige Widget
        self.window.deiconify()
        self.is_visible = True

        # Auto-hide nach 10 Sekunden
        self._schedule_auto_hide()

    def _position_widget(self, mouse_x: int, mouse_y: int):
        """Positioniere Widget unter der Maus."""
        # Update window um korrekte Größe zu bekommen
        self.window.update_idletasks()

        # Offset unter der Maus
        offset_x = 10
        offset_y = 30

        # Berechne Position
        widget_x = mouse_x + offset_x
        widget_y = mouse_y + offset_y

        # Hole Bildschirm-Dimensionen
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        # Hole Widget-Dimensionen
        widget_width = self.window.winfo_reqwidth()
        widget_height = self.window.winfo_reqheight()

        # Halte Widget auf dem Bildschirm
        if widget_x + widget_width > screen_width:
            widget_x = screen_width - widget_width - 10
        if widget_x < 0:
            widget_x = 10
        if widget_y + widget_height > screen_height:
            widget_y = screen_height - widget_height - 10
        if widget_y < 0:
            widget_y = 10

        self.window.geometry(f"+{widget_x}+{widget_y}")

    def _schedule_auto_hide(self):
        """Plane Auto-Hide nach 10 Sekunden."""

        def auto_hide():
            time.sleep(10)
            if self.is_visible:
                # Verwende after() für thread-sichere tkinter-Aufrufe
                self.window.after(0, self.hide)

        threading.Thread(target=auto_hide, daemon=True).start()

    def hide(self):
        """Verstecke Widget."""
        if self.is_visible:
            self.window.withdraw()
            self.is_visible = False

    def close(self):
        """Schließe Widget."""
        self.hide()
        self.on_close()

    def copy_text(self):
        """Kopiere Text."""
        self.on_copy(self.transcription_text)

    def show_actions(self):
        """Zeige zusätzliche Aktionen für den Text."""
        print(f"✨ Aktionen für Text: {self.transcription_text}")
        # Hier könnten weitere Aktionen wie Übersetzen, Korrigieren, etc. hinzugefügt werden

    def is_showing(self) -> bool:
        """Prüfe ob Widget sichtbar ist."""
        return self.is_visible

    def cleanup(self):
        """Bereinige Widget."""
        if self.root:
            self.root.destroy()
            self.root = None


class TranscriptionWidgetManager:
    """Manager für Transcription Widgets."""

    def __init__(self):
        self.widget: Optional[TranscriptionWidget] = None
        self.on_copy_callback: Optional[Callable[[str], None]] = None

    def set_copy_callback(self, callback: Callable[[str], None]):
        """Setze Copy-Callback."""
        self.on_copy_callback = callback

    def show_transcription(self, text: str, confidence: float, mouse_x: int, mouse_y: int):
        """Zeige Transkription."""
        if not self.widget:
            self.widget = TranscriptionWidget(on_copy=self._on_copy, on_close=self._on_close)

        self.widget.show(text, confidence, mouse_x, mouse_y)

    def hide_transcription(self):
        """Verstecke Transkription."""
        if self.widget:
            self.widget.hide()

    def _on_copy(self, text: str):
        """Callback für Kopieren."""
        if self.on_copy_callback:
            self.on_copy_callback(text)

    def _on_close(self):
        """Callback für Schließen."""
        pass  # Widget bleibt bestehen für weitere Verwendung

    def cleanup(self):
        """Bereinige Manager."""
        if self.widget:
            self.widget.cleanup()
            self.widget = None
