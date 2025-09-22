#!/usr/bin/env python3
"""
Einfacher, funktionierender Multi-Monitor Region-Selector.
Verwendet PyQt6 für echte Multi-Monitor-Unterstützung.
"""

import sys
import time
from datetime import datetime
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


def create_multi_monitor_selector():
    """Erstelle einen Multi-Monitor Selector."""
    try:
        from PyQt6 import QtCore, QtGui, QtWidgets

        class MultiMonitorOverlay(QtWidgets.QWidget):
            done = QtCore.pyqtSignal()

            def __init__(self):
                super().__init__()

                # Multi-Monitor Setup
                self.screens = QtGui.QGuiApplication.screens()
                self.current_screen = 0
                self.result_rect = None

                # Region-Parameter
                self.region_width = 200
                self.region_height = 150
                self.min_size = 50
                self.max_size = 800
                self.mouse_pos = QtCore.QPoint(0, 0)

                # Setup für alle Bildschirme
                self._setup_multi_monitor()

            def _setup_multi_monitor(self):
                """Setup für Multi-Monitor."""
                # Erstelle ein Fenster das alle Bildschirme abdeckt
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

            def keyPressEvent(self, ev: QtGui.QKeyEvent) -> None:
                if ev.key() == QtCore.Qt.Key.Key_Escape:
                    self.result_rect = None
                    self.done.emit()
                    self.close()
                elif ev.key() == QtCore.Qt.Key.Key_Return or ev.key() == QtCore.Qt.Key.Key_Space:
                    self._confirm_selection()
                elif ev.key() == QtCore.Qt.Key.Key_Left:
                    self._switch_screen_left()
                elif ev.key() == QtCore.Qt.Key.Key_Right:
                    self._switch_screen_right()
                elif ev.key() == QtCore.Qt.Key.Key_Tab:
                    self._switch_screen_next()

            def _switch_screen_left(self):
                """Wechsle zum linken Bildschirm."""
                if len(self.screens) > 1:
                    self.current_screen = (self.current_screen - 1) % len(self.screens)
                    self.update()

            def _switch_screen_right(self):
                """Wechsle zum rechten Bildschirm."""
                if len(self.screens) > 1:
                    self.current_screen = (self.current_screen + 1) % len(self.screens)
                    self.update()

            def _switch_screen_next(self):
                """Wechsle zum nächsten Bildschirm."""
                if len(self.screens) > 1:
                    self.current_screen = (self.current_screen + 1) % len(self.screens)
                    self.update()

            def mouseMoveEvent(self, ev: QtGui.QMouseEvent) -> None:
                self.mouse_pos = ev.globalPosition().toPoint()
                self.update()

            def wheelEvent(self, ev: QtGui.QWheelEvent) -> None:
                """Verändere Größe mit Mausrad."""
                delta = ev.angleDelta().y()
                scale_factor = 1.1 if delta > 0 else 0.9

                new_width = int(self.region_width * scale_factor)
                new_height = int(self.region_height * scale_factor)

                # Größe begrenzen
                self.region_width = max(self.min_size, min(self.max_size, new_width))
                self.region_height = max(self.min_size, min(self.max_size, new_height))
                self.update()

            def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
                if ev.button() == QtCore.Qt.MouseButton.LeftButton:
                    self._confirm_selection()
                elif ev.button() == QtCore.Qt.MouseButton.RightButton:
                    self.result_rect = None
                    self.done.emit()
                    self.close()

            def _confirm_selection(self):
                """Bestätige die aktuelle Auswahl."""
                # Finde den Bildschirm auf dem sich die Maus befindet
                screen = self._get_screen_at_position(self.mouse_pos)
                if screen:
                    screen_geo = screen.geometry()
                    half_width = self.region_width // 2
                    half_height = self.region_height // 2

                    # Globale Koordinaten
                    global_left = self.mouse_pos.x() - half_width
                    global_top = self.mouse_pos.y() - half_height

                    self.result_rect = QtCore.QRect(global_left, global_top, self.region_width, self.region_height)

                self.done.emit()
                self.close()

            def _get_screen_at_position(self, pos):
                """Finde den Bildschirm an der gegebenen Position."""
                for screen in self.screens:
                    geo = screen.geometry()
                    if geo.contains(pos):
                        return screen
                return self.screens[0]  # Fallback

            def paintEvent(self, ev: QtGui.QPaintEvent) -> None:
                painter = QtGui.QPainter(self)
                painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)

                # 1) Dim entire screen
                painter.fillRect(self.rect(), QtGui.QColor(0, 0, 0, 120))

                # 2) Zeichne Region um Mausposition
                half_width = self.region_width // 2
                half_height = self.region_height // 2

                # Convert to widget-local coordinates
                tl = self.geometry().topLeft()
                local_center = self.mouse_pos - tl

                region_rect = QtCore.QRect(
                    local_center.x() - half_width, local_center.y() - half_height, self.region_width, self.region_height
                )

                # Punch hole (transparent)
                painter.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_Clear)
                painter.fillRect(region_rect, QtCore.Qt.GlobalColor.transparent)

                # Draw border back in normal mode
                painter.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_SourceOver)

                # Äußere Umrandung (dick)
                pen = QtGui.QPen(QtGui.QColor(255, 255, 255, 200), 3)
                painter.setPen(pen)
                painter.drawRect(region_rect)

                # Innere Umrandung (dünn)
                pen = QtGui.QPen(QtGui.QColor(0, 0, 0, 150), 1)
                painter.setPen(pen)
                painter.drawRect(region_rect.adjusted(1, 1, -1, -1))

                # Größenanzeige
                w, h = self.region_width, self.region_height
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

                painter.fillRect(label_bg_rect, QtGui.QColor(0, 0, 0, 180))

                # Label-Text
                painter.setPen(QtGui.QColor(255, 255, 255))
                painter.setFont(font)
                painter.drawText(label_bg_rect, QtCore.Qt.AlignmentFlag.AlignCenter, label_text)

                # Anweisungen
                instructions = [
                    "Mausrad: Größe ändern",
                    "Linksklick: Bestätigen",
                    "Enter/Space: Bestätigen",
                    "Rechtsklick/ESC: Abbrechen",
                ]

                if len(self.screens) > 1:
                    instructions.extend(["Pfeiltasten/Tab: Bildschirm wechseln"])

                font_small = QtGui.QFont("Arial", 10)
                painter.setFont(font_small)
                painter.setPen(QtGui.QColor(200, 200, 200, 200))

                # Anweisungen unten links
                y_start = self.height() - 100
                for i, instruction in enumerate(instructions):
                    painter.drawText(20, y_start + i * 20, instruction)

                # Bildschirm-Info
                if len(self.screens) > 1:
                    painter.setPen(QtGui.QColor(100, 200, 255, 200))
                    painter.drawText(20, 20, f"🖥️ Bildschirm {self.current_screen + 1}/{len(self.screens)}")

        # Hauptfunktion
        app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
        overlay = MultiMonitorOverlay()
        overlay.showFullScreen()

        # Event Loop
        loop = QtCore.QEventLoop()
        overlay.done.connect(loop.quit)
        loop.exec()

        if not overlay.result_rect or overlay.result_rect.width() < 2 or overlay.result_rect.height() < 2:
            return None

        r = overlay.result_rect
        return Rect(left=r.left(), top=r.top(), width=r.width(), height=r.height())

    except ImportError:
        print("❌ PyQt6 nicht verfügbar - verwende Tkinter-Fallback")
        from src.ui.simple_region_selector import SimpleRegionSelector

        selector = SimpleRegionSelector()
        return selector.select()


def test_final_multi_selector():
    """Teste den finalen Multi-Monitor Selector."""
    print("🎯 Teste finalen Multi-Monitor Selector...")
    print("📝 Anleitung:")
    print("   1️⃣  Bewege die Maus zu der gewünschten Position (auch auf anderen Bildschirmen!)")
    print("   2️⃣  Drehe das Mausrad um die Größe zu ändern")
    print("   3️⃣  Linksklick oder Enter zum Bestätigen")
    print("   4️⃣  ESC oder Rechtsklick zum Abbrechen")
    print("   5️⃣  Pfeiltasten/Tab zum Bildschirm wechseln (bei mehreren Monitoren)")
    print("\n⏳ Starte in 3 Sekunden...")

    for i in range(3, 0, -1):
        print(f"   {i}...")
        time.sleep(1)

    result = create_multi_monitor_selector()

    if result:
        print(f"✅ Region ausgewählt: {result}")
        print(f"   📏 Größe: {result.width}x{result.height}")
        print(f"   📍 Position: ({result.left}, {result.top})")
        return True
    else:
        print("❌ Auswahl abgebrochen")
        return False


if __name__ == "__main__":
    test_final_multi_selector()
