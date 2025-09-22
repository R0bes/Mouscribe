from __future__ import annotations

import os
import sys
import time
import tkinter as tk
from datetime import datetime
from tkinter import messagebox
from typing import Optional, Tuple


class Rect:
    """Einfache Rectangle-Klasse."""

    def __init__(self, left: int, top: int, width: int, height: int):
        self.left = left
        self.top = top
        self.width = width
        self.height = height

    def __repr__(self):
        return f"Rect(left={self.left}, top={self.top}, width={self.width}, height={self.height})"


class RegionSelector:
    """Basis-Klasse für Region-Auswahl."""

    def select(self) -> Rect | None:
        """Wähle eine Region aus und gib Rect zurück."""
        raise NotImplementedError


class QtSelector(RegionSelector):
    """Semi-transparent overlay mit einem transparenten 'Loch' (Auswahl)."""

    def select(self) -> Rect | None:
        """Implementiere Region-Auswahl mit PyQt6."""
        try:
            from PyQt6 import QtCore, QtGui, QtWidgets
        except ImportError:
            print("❌ PyQt6 nicht installiert. Verwende Tkinter-Fallback...")
            return self._tkinter_fallback()

        class Overlay(QtWidgets.QWidget):
            done = QtCore.pyqtSignal()

            def __init__(self):
                super().__init__()
                self.setWindowFlags(
                    QtCore.Qt.WindowType.FramelessWindowHint
                    | QtCore.Qt.WindowType.Tool
                    | QtCore.Qt.WindowType.WindowStaysOnTopHint
                )
                self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
                self.setMouseTracking(True)
                self.setCursor(QtCore.Qt.CursorShape.CrossCursor)

                # Cover virtual desktop (all monitors)
                geo = QtGui.QGuiApplication.primaryScreen().virtualGeometry()
                self.setGeometry(geo)

                self.origin: QtCore.QPoint | None = None
                self.current: QtCore.QPoint | None = None
                self.result_rect: QtCore.QRect | None = None

            def keyPressEvent(self, ev: QtGui.QKeyEvent) -> None:
                if ev.key() == QtCore.Qt.Key.Key_Escape:
                    self.result_rect = None
                    self.done.emit()
                    self.close()

            def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
                self.origin = ev.globalPosition().toPoint()
                self.current = self.origin
                self.update()

            def mouseMoveEvent(self, ev: QtGui.QMouseEvent) -> None:
                if self.origin:
                    self.current = ev.globalPosition().toPoint()
                    self.update()

            def mouseReleaseEvent(self, ev: QtGui.QMouseEvent) -> None:
                if self.origin and self.current:
                    r = QtCore.QRect(self.origin, ev.globalPosition().toPoint()).normalized()
                    self.result_rect = r
                self.done.emit()
                self.close()

            def paintEvent(self, ev: QtGui.QPaintEvent) -> None:
                p = QtGui.QPainter(self)
                p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)

                # 1) Dim entire screen
                p.fillRect(self.rect(), QtGui.QColor(0, 0, 0, 120))

                # 2) If selecting: punch a transparent hole + draw border and size
                if self.origin and self.current:
                    global_sel = QtCore.QRect(self.origin, self.current).normalized()
                    # Convert to widget-local coordinates
                    tl = self.geometry().topLeft()
                    local_sel = QtCore.QRect(global_sel.topLeft() - tl, global_sel.size())

                    # Punch hole (transparent)
                    p.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_Clear)
                    p.fillRect(local_sel, QtCore.Qt.GlobalColor.transparent)

                    # Draw border back in normal mode
                    p.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_SourceOver)
                    pen = QtGui.QPen(QtGui.QColor(255, 255, 255, 230), 2)
                    p.setPen(pen)
                    p.drawRect(local_sel)

                    # Size label
                    w, h = local_sel.width(), local_sel.height()
                    label_rect = QtCore.QRect(local_sel.topLeft() + QtCore.QPoint(6, -30), QtCore.QSize(150, 24))
                    p.fillRect(label_rect, QtGui.QColor(0, 0, 0, 160))
                    p.setPen(QtGui.QColor(255, 255, 255))
                    p.drawText(
                        label_rect.adjusted(6, 0, -6, 0),
                        QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignLeft,
                        f"{w} × {h}",
                    )

        app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
        ov = Overlay()
        ov.showFullScreen()

        loop = QtCore.QEventLoop()
        ov.done.connect(loop.quit)
        loop.exec()

        if not ov.result_rect or ov.result_rect.width() < 2 or ov.result_rect.height() < 2:
            return None

        r = ov.result_rect
        return Rect(left=r.left(), top=r.top(), width=r.width(), height=r.height())


class MouseCenteredSelector(RegionSelector):
    """Region-Selector der um die Maus herum gerendert wird und mit Mausrad die Größe verstellt."""

    def select(self) -> Rect | None:
        """Implementiere mauszentrierte Region-Auswahl mit PyQt6."""
        try:
            from PyQt6 import QtCore, QtGui, QtWidgets
        except ImportError:
            print("❌ PyQt6 nicht installiert. Verwende Tkinter-Fallback...")
            return self._tkinter_mouse_centered_fallback()

        class MouseCenteredOverlay(QtWidgets.QWidget):
            done = QtCore.pyqtSignal()

            def __init__(self):
                super().__init__()
                self.setWindowFlags(
                    QtCore.Qt.WindowType.FramelessWindowHint
                    | QtCore.Qt.WindowType.Tool
                    | QtCore.Qt.WindowType.WindowStaysOnTopHint
                )
                self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
                self.setAttribute(QtCore.Qt.WidgetAttribute.WA_NoSystemBackground, True)
                self.setMouseTracking(True)
                self.setCursor(QtCore.Qt.CursorShape.CrossCursor)

                # Stelle sicher, dass das Fenster alle Events empfängt
                self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
                self.activateWindow()
                self.raise_()
                self.setFocus()

                # Cover virtual desktop (all monitors)
                geo = QtGui.QGuiApplication.primaryScreen().virtualGeometry()
                self.setGeometry(geo)

                # Region-Parameter
                self.region_size = QtCore.QSize(200, 150)  # Startgröße
                self.min_size = QtCore.QSize(50, 50)  # Mindestgröße
                self.max_size = QtCore.QSize(800, 600)  # Maximale Größe
                self.mouse_pos = QtCore.QPoint(0, 0)
                self.result_rect: QtCore.QRect | None = None
                self.is_active = False

            def keyPressEvent(self, ev: QtGui.QKeyEvent) -> None:
                if ev.key() == QtCore.Qt.Key.Key_Escape:
                    self.result_rect = None
                    self.done.emit()
                    self.close()
                elif ev.key() == QtCore.Qt.Key.Key_Return or ev.key() == QtCore.Qt.Key.Key_Space:
                    # Bestätige Auswahl
                    self._confirm_selection()

            def mouseMoveEvent(self, ev: QtGui.QMouseEvent) -> None:
                self.mouse_pos = ev.globalPosition().toPoint()
                self.update()

            def wheelEvent(self, ev: QtGui.QWheelEvent) -> None:
                """Verändere Größe mit Mausrad."""
                # Berechne Skalierungsfaktor
                delta = ev.angleDelta().y()
                scale_factor = 1.1 if delta > 0 else 0.9

                # Neue Größe berechnen
                new_width = int(self.region_size.width() * scale_factor)
                new_height = int(self.region_size.height() * scale_factor)

                # Größe begrenzen
                new_width = max(self.min_size.width(), min(self.max_size.width(), new_width))
                new_height = max(self.min_size.height(), min(self.max_size.height(), new_height))

                self.region_size = QtCore.QSize(new_width, new_height)
                self.update()

            def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
                if ev.button() == QtCore.Qt.MouseButton.LeftButton:
                    self._confirm_selection()
                elif ev.button() == QtCore.Qt.MouseButton.RightButton:
                    # Rechte Maustaste = Abbrechen
                    self.result_rect = None
                    self.done.emit()
                    self.close()

            def _confirm_selection(self):
                """Bestätige die aktuelle Auswahl."""
                center = self.mouse_pos
                half_width = self.region_size.width() // 2
                half_height = self.region_size.height() // 2

                selection_rect = QtCore.QRect(
                    center.x() - half_width, center.y() - half_height, self.region_size.width(), self.region_size.height()
                )

                self.result_rect = selection_rect
                self.done.emit()
                self.close()

            def paintEvent(self, ev: QtGui.QPaintEvent) -> None:
                p = QtGui.QPainter(self)
                p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)

                # 1) Dim entire screen
                p.fillRect(self.rect(), QtGui.QColor(0, 0, 0, 120))

                # 2) Zeichne Region um Mausposition
                center = self.mouse_pos
                half_width = self.region_size.width() // 2
                half_height = self.region_size.height() // 2

                # Convert to widget-local coordinates
                tl = self.geometry().topLeft()
                local_center = center - tl

                region_rect = QtCore.QRect(
                    local_center.x() - half_width,
                    local_center.y() - half_height,
                    self.region_size.width(),
                    self.region_size.height(),
                )

                # Punch hole (transparent)
                p.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_Clear)
                p.fillRect(region_rect, QtCore.Qt.GlobalColor.transparent)

                # Draw border back in normal mode
                p.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_SourceOver)

                # Äußere Umrandung (dick)
                pen = QtGui.QPen(QtGui.QColor(255, 255, 255, 200), 3)
                p.setPen(pen)
                p.drawRect(region_rect)

                # Innere Umrandung (dünn)
                pen = QtGui.QPen(QtGui.QColor(0, 0, 0, 150), 1)
                p.setPen(pen)
                p.drawRect(region_rect.adjusted(1, 1, -1, -1))

                # Größenanzeige
                w, h = self.region_size.width(), self.region_size.height()
                label_text = f"{w} × {h}"

                # Label-Hintergrund
                font = QtGui.QFont("Arial", 12, QtGui.QFont.Weight.Bold)
                fm = QtGui.QFontMetrics(font)
                text_rect = fm.boundingRect(label_text)

                label_bg_rect = QtCore.QRect(
                    local_center.x() - text_rect.width() // 2 - 8,
                    local_center.y() - half_height - 35,
                    text_rect.width() + 16,
                    text_rect.height() + 8,
                )

                p.fillRect(label_bg_rect, QtGui.QColor(0, 0, 0, 180))

                # Label-Text
                p.setPen(QtGui.QColor(255, 255, 255))
                p.setFont(font)
                p.drawText(label_bg_rect, QtCore.Qt.AlignmentFlag.AlignCenter, label_text)

                # Anweisungen
                instructions = [
                    "Mausrad: Größe ändern",
                    "Linksklick: Bestätigen",
                    "Enter/Space: Bestätigen",
                    "Rechtsklick/ESC: Abbrechen",
                ]
                font_small = QtGui.QFont("Arial", 10)
                p.setFont(font_small)
                p.setPen(QtGui.QColor(200, 200, 200, 200))

                # Anweisungen unten links
                y_start = self.height() - 80
                for i, instruction in enumerate(instructions):
                    p.drawText(20, y_start + i * 20, instruction)

        app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
        ov = MouseCenteredOverlay()

        # Wichtig: Fenster richtig anzeigen und fokussieren
        ov.showFullScreen()
        ov.activateWindow()
        ov.raise_()
        ov.setFocus()

        # Kurze Pause damit das Fenster richtig initialisiert wird
        QtCore.QTimer.singleShot(100, lambda: ov.setFocus())

        loop = QtCore.QEventLoop()
        ov.done.connect(loop.quit)
        loop.exec()

        if not ov.result_rect or ov.result_rect.width() < 2 or ov.result_rect.height() < 2:
            return None

        r = ov.result_rect
        return Rect(left=r.left(), top=r.top(), width=r.width(), height=r.height())

    def _tkinter_mouse_centered_fallback(self) -> Rect | None:
        """Tkinter-Fallback für mauszentrierte Region-Auswahl."""
        print("🔄 Verwende Tkinter-Fallback für mauszentrierte Region-Auswahl...")

        class TkinterMouseCenteredSelector:
            def __init__(self):
                self.root = tk.Tk()
                self.root.withdraw()  # Verstecke Hauptfenster

                # Erstelle Overlay-Fenster
                self.overlay = tk.Toplevel()
                self.overlay.attributes("-fullscreen", True)
                self.overlay.attributes("-alpha", 0.3)  # Semi-transparent
                self.overlay.configure(bg="black")
                self.overlay.attributes("-topmost", True)

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

                # Bind Events
                self.canvas.bind("<Motion>", self.update_mouse_position)
                self.canvas.bind("<Button-1>", self.confirm_selection)
                self.canvas.bind("<Button-3>", self.cancel_selection)  # Rechte Maustaste
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

            def show_instructions(self):
                """Zeige Anweisungen."""
                self.canvas.create_text(
                    self.overlay.winfo_screenwidth() // 2,
                    50,
                    text="🎯 Mausrad: Größe ändern • Linksklick/Enter: Bestätigen • Rechtsklick/ESC: Abbrechen",
                    fill="white",
                    font=("Arial", 14, "bold"),
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

        selector = TkinterMouseCenteredSelector()
        selector.root.mainloop()
        return selector.result

    def _tkinter_fallback(self) -> Rect | None:
        """Tkinter-Fallback wenn PyQt6 nicht verfügbar ist."""
        print("🔄 Verwende Tkinter-Fallback für Region-Auswahl...")

        class TkinterSelector:
            def __init__(self):
                self.root = tk.Tk()
                self.root.withdraw()  # Verstecke Hauptfenster

                # Erstelle Overlay-Fenster
                self.overlay = tk.Toplevel()
                self.overlay.attributes("-fullscreen", True)
                self.overlay.attributes("-alpha", 0.3)  # Semi-transparent
                self.overlay.configure(bg="black")
                self.overlay.attributes("-topmost", True)

                # Canvas für Zeichnung
                self.canvas = tk.Canvas(self.overlay, highlightthickness=0, bg="black")
                self.canvas.pack(fill="both", expand=True)

                self.start_x = None
                self.start_y = None
                self.rect_id = None
                self.result = None

                # Bind Events
                self.canvas.bind("<Button-1>", self.start_selection)
                self.canvas.bind("<B1-Motion>", self.update_selection)
                self.canvas.bind("<ButtonRelease-1>", self.end_selection)
                self.overlay.bind("<Escape>", self.cancel_selection)

                # Cursor ändern
                self.canvas.configure(cursor="crosshair")

                # Anweisungen anzeigen
                self.show_instructions()

            def show_instructions(self):
                """Zeige Anweisungen."""
                self.canvas.create_text(
                    self.overlay.winfo_screenwidth() // 2,
                    50,
                    text="🎯 Ziehe um einen Bereich auszuwählen • ESC zum Abbrechen",
                    fill="white",
                    font=("Arial", 16, "bold"),
                    tags="instructions",
                )

            def start_selection(self, event):
                """Starte Auswahl."""
                self.start_x = event.x
                self.start_y = event.y
                self.canvas.delete("selection")

            def update_selection(self, event):
                """Aktualisiere Auswahl."""
                if self.start_x is not None:
                    self.canvas.delete("selection")

                    # Zeichne Rechteck
                    self.rect_id = self.canvas.create_rectangle(
                        self.start_x, self.start_y, event.x, event.y, outline="white", width=2, tags="selection"
                    )

                    # Zeige Größe
                    width = abs(event.x - self.start_x)
                    height = abs(event.y - self.start_y)
                    self.canvas.create_text(
                        event.x + 10,
                        event.y - 20,
                        text=f"{width} × {height}",
                        fill="white",
                        font=("Arial", 12, "bold"),
                        tags="selection",
                    )

            def end_selection(self, event):
                """Beende Auswahl."""
                if self.start_x is not None:
                    x1, y1 = self.start_x, self.start_y
                    x2, y2 = event.x, event.y

                    # Normalisiere Koordinaten
                    left = min(x1, x2)
                    top = min(y1, y2)
                    width = abs(x2 - x1)
                    height = abs(y2 - y1)

                    if width > 10 and height > 10:  # Mindestgröße
                        self.result = Rect(left, top, width, height)

                    self.overlay.destroy()
                    self.root.destroy()

            def cancel_selection(self, event):
                """Breche Auswahl ab."""
                self.result = None
                self.overlay.destroy()
                self.root.destroy()

        selector = TkinterSelector()
        selector.root.mainloop()
        return selector.result


class ScreenCaptureSelector(RegionSelector):
    """Region-Selector mit Bildschirmaufnahme-Funktionalität."""

    def __init__(self, capture_type: str = "screenshot"):
        """
        Args:
            capture_type: "screenshot" oder "video"
        """
        self.capture_type = capture_type
        self.output_dir = "captures"
        os.makedirs(self.output_dir, exist_ok=True)

    def select(self) -> Rect | None:
        """Wähle Region und mache Aufnahme."""
        try:
            from src.ui.simple_region_selector import SimpleRegionSelector

            print(f"🎥 Region-Selector mit {self.capture_type}...")

            # Region auswählen
            selector = SimpleRegionSelector()
            result = selector.select()

            if result:
                print(f"✅ Region ausgewählt: {result}")

                if self.capture_type == "screenshot":
                    return self._take_screenshot(result)
                elif self.capture_type == "video":
                    return self._record_video(result)
                else:
                    print("❌ Unbekannter Capture-Typ")
                    return result
            else:
                print("❌ Keine Region ausgewählt")
                return None

        except Exception as e:
            print(f"❌ Fehler bei Bildschirmaufnahme: {e}")
            return None

    def _take_screenshot(self, region: Rect) -> Rect:
        """Mache einen Screenshot der ausgewählten Region."""
        try:
            print("📸 Mache Screenshot...")

            # Versuche PIL/Pillow zuerst
            try:
                from PIL import ImageGrab

                screenshot = ImageGrab.grab(
                    bbox=(region.left, region.top, region.left + region.width, region.top + region.height)
                )

                # Dateiname generieren
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
                filepath = os.path.join(self.output_dir, filename)

                screenshot.save(filepath)
                print(f"✅ Screenshot gespeichert: {filepath}")
                print(f"   📏 Größe: {region.width}x{region.height}")

                return region

            except ImportError:
                print("❌ PIL/Pillow nicht verfügbar")
                return self._fallback_screenshot(region)

        except Exception as e:
            print(f"❌ Screenshot-Fehler: {e}")
            return region

    def _record_video(self, region: Rect) -> Rect:
        """Nimm ein Video der ausgewählten Region auf."""
        try:
            print("🎬 Starte Video-Aufnahme...")
            print("   📝 Drücke Ctrl+C zum Stoppen")

            # Versuche opencv-python
            try:
                import cv2
                import numpy as np

                # Video-Writer konfigurieren
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"video_{timestamp}.mp4"
                filepath = os.path.join(self.output_dir, filename)

                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                fps = 30
                out = cv2.VideoWriter(filepath, fourcc, fps, (region.width, region.height))

                print(f"🎥 Aufnahme läuft... (Region: {region.width}x{region.height})")
                print("   ⏹️ Drücke Ctrl+C zum Stoppen")

                start_time = time.time()
                frame_count = 0

                try:
                    while True:
                        # Screenshot der Region machen
                        from PIL import ImageGrab

                        screenshot = ImageGrab.grab(
                            bbox=(region.left, region.top, region.left + region.width, region.top + region.height)
                        )

                        # PIL zu OpenCV konvertieren
                        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                        out.write(frame)

                        frame_count += 1

                        # Alle 30 Frames Status anzeigen
                        if frame_count % 30 == 0:
                            elapsed = time.time() - start_time
                            print(f"   📊 {frame_count} Frames, {elapsed:.1f}s")

                        # Kurze Pause für Performance
                        time.sleep(1 / fps)

                except KeyboardInterrupt:
                    print("\n⏹️ Aufnahme gestoppt!")

                # Video schließen
                out.release()
                cv2.destroyAllWindows()

                duration = time.time() - start_time
                print(f"✅ Video gespeichert: {filepath}")
                print(f"   📊 {frame_count} Frames, {duration:.1f}s, {fps} FPS")

                return region

            except ImportError:
                print("❌ OpenCV nicht verfügbar - verwende Fallback")
                return self._fallback_video(region)

        except Exception as e:
            print(f"❌ Video-Aufnahme Fehler: {e}")
            return region

    def _fallback_screenshot(self, region: Rect) -> Rect:
        """Fallback Screenshot mit tkinter."""
        try:
            print("🔄 Verwende Tkinter-Fallback für Screenshot...")

            # Einfacher Screenshot mit tkinter
            root = tk.Tk()
            root.withdraw()

            # Simuliere Screenshot (in echter Implementierung würde man den Bildschirm erfassen)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_fallback_{timestamp}.txt"
            filepath = os.path.join(self.output_dir, filename)

            with open(filepath, "w") as f:
                f.write("Screenshot Info:\n")
                f.write(f"Region: {region.left}, {region.top}, {region.width}, {region.height}\n")
                f.write(f"Zeit: {datetime.now()}\n")
                f.write(f"Größe: {region.width}x{region.height} Pixel\n")

            print(f"✅ Screenshot-Info gespeichert: {filepath}")
            return region

        except Exception as e:
            print(f"❌ Fallback Screenshot Fehler: {e}")
            return region

    def _fallback_video(self, region: Rect) -> Rect:
        """Fallback Video-Aufnahme."""
        try:
            print("🔄 Verwende Fallback für Video-Aufnahme...")

            # Simuliere Video-Aufnahme
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"video_fallback_{timestamp}.txt"
            filepath = os.path.join(self.output_dir, filename)

            print("🎬 Simuliere Video-Aufnahme (5 Sekunden)...")
            start_time = time.time()

            with open(filepath, "w") as f:
                f.write("Video Info:\n")
                f.write(f"Region: {region.left}, {region.top}, {region.width}, {region.height}\n")
                f.write(f"Startzeit: {datetime.now()}\n")
                f.write(f"Größe: {region.width}x{region.height} Pixel\n")
                f.write("Frames: 150 (simuliert)\n")
                f.write("Dauer: 5 Sekunden\n")

            # Simuliere 5 Sekunden Aufnahme
            for i in range(5):
                print(f"   📊 Frame {i*30}-{(i+1)*30}...")
                time.sleep(1)

            print(f"✅ Video-Info gespeichert: {filepath}")
            return region

        except Exception as e:
            print(f"❌ Fallback Video Fehler: {e}")
            return region


class SimpleRegionSelector(RegionSelector):
    """Einfacher Region-Selector für Tests."""

    def select(self) -> Rect | None:
        """Simuliere eine Region-Auswahl für Tests."""
        print("🎯 Simuliere Region-Auswahl...")
        print("   (In der echten Anwendung würde hier der Overlay erscheinen)")

        # Simuliere eine Auswahl
        return Rect(left=100, top=100, width=300, height=200)


def test_region_selector():
    """Teste den Region-Selector."""
    print("🎯 Teste Region-Selector...")

    # Teste Qt-Selector (falls verfügbar)
    try:
        selector = QtSelector()
        result = selector.select()
        if result:
            print(f"✅ Region ausgewählt: {result}")
        else:
            print("❌ Keine Region ausgewählt")
    except Exception as e:
        print(f"❌ Fehler beim Qt-Selector: {e}")

    # Teste einfachen Selector
    print("\n🔄 Teste einfachen Selector...")
    simple_selector = SimpleRegionSelector()
    result = simple_selector.select()
    print(f"✅ Simulierte Region: {result}")


if __name__ == "__main__":
    test_region_selector()
