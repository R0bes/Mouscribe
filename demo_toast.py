#!/usr/bin/env python3
"""
Demo für die neuen modernen Toast-Benachrichtigungen in Mauscribe.
Zeigt alle verfügbaren Benachrichtigungstypen als elegante Widgets.
"""

import os
import sys
import time

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

try:
    from src.windows_notifications import WindowsNotificationManager

    print("✅ Toast-Benachrichtigungen erfolgreich geladen")
except ImportError as e:
    print(f"❌ Fehler beim Laden der Toast-Benachrichtigungen: {e}")
    sys.exit(1)


def demo_toast_notifications():
    """Demonstriert alle Toast-Benachrichtigungstypen."""
    print("🎯 Demo der modernen Toast-Benachrichtigungen")
    print("=" * 50)

    # Initialize notification manager
    notification_manager = WindowsNotificationManager()

    if not notification_manager.is_supported():
        print("❌ Toast-Benachrichtigungen werden auf diesem System nicht unterstützt")
        return

    print("✅ Toast-Benachrichtigungen werden unterstützt")
    print("💡 Schauen Sie in die rechte untere Ecke Ihres Bildschirms")
    print("🖱️  Klicken Sie auf eine Benachrichtigung, um sie zu schließen")
    print()

    # Demo sequence
    demos = [
        ("🎙️ Aufnahme gestartet", "Sprachaufnahme läuft...", "info"),
        ("✨ Transkription abgeschlossen", "Text erfolgreich erkannt", "success"),
        ("📋 Text eingefügt", "Transkribierter Text wurde eingefügt", "info"),
        ("🔍 Rechtschreibprüfung", "Korrekturen wurden angewendet", "info"),
        ("⚠️ Warnung", "Niedriger Batteriestand erkannt", "warning"),
        ("❌ Fehler", "Verbindung zum Server fehlgeschlagen", "error"),
        ("ℹ️ Information", "Mauscribe läuft im Hintergrund", "info"),
    ]

    for i, (title, message, notification_type) in enumerate(demos, 1):
        print(f"{i}. Zeige: {title}")

        # Show notification
        if notification_type == "info":
            notification_manager.show_info(message, "Demo")
        elif notification_type == "success":
            notification_manager.show_transcription_complete(message, 2.5)
        elif notification_type == "warning":
            notification_manager.show_warning(message, "Demo")
        elif notification_type == "error":
            notification_manager.show_error(message, "Demo")

        # Wait between notifications
        time.sleep(2)

    print("\n🎉 Demo abgeschlossen!")
    print("💡 Alle Benachrichtigungen werden automatisch ausgeblendet")
    print("🔄 Benachrichtigungen können über config.toml konfiguriert werden")


def show_system_info():
    """Zeigt Systeminformationen an."""
    print("\n📊 System-Informationen")
    print("-" * 30)

    notification_manager = WindowsNotificationManager()
    if notification_manager.is_supported():
        info = notification_manager.get_system_info()
        for key, value in info.items():
            print(f"  {key}: {value}")
    else:
        print("  Toast-Benachrichtigungen nicht verfügbar")


if __name__ == "__main__":
    print("🚀 Mauscribe Toast-Benachrichtigungen Demo")
    print("=" * 50)

    try:
        show_system_info()
        demo_toast_notifications()

        print("\n👋 Demo beendet")
        print("💡 Toast-Benachrichtigungen sind jetzt in Mauscribe integriert")

    except KeyboardInterrupt:
        print("\n⏹️ Demo durch Benutzer unterbrochen")
    except Exception as e:
        print(f"\n❌ Demo fehlgeschlagen: {e}")
        import traceback

        traceback.print_exc()
