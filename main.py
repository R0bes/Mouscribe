# main.py - Main entry point for Mauscribe application
#!/usr/bin/env python3
"""
Mauscribe - Voice-to-Text Tool
Simple entry point
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.mouscribe import MauscribeApp
from src.utils.singleton import SystemWideSingleton

def show_already_running_notification(running_pid: int) -> None:
    """
    Zeige eine Benachrichtigung an, dass die Anwendung bereits läuft.
    
    Args:
        running_pid: Die PID der bereits laufenden Instanz
    """
    try:
        # Versuche NotificationManager zu importieren und zu verwenden
        from src.ui.notifications import NotificationManager
        
        # Erstelle eine temporäre NotificationManager-Instanz
        notification_manager = NotificationManager()
        
        # Zeige Benachrichtigung an
        notification_manager.show_warning(
            f"Mauscribe läuft bereits (PID: {running_pid})",
            "Anwendung bereits gestartet"
        )
        
        print(f"[INFO] Benachrichtigung angezeigt: Mauscribe läuft bereits (PID: {running_pid})")
        
    except ImportError:
        # Fallback: Nur Logging, wenn NotificationManager nicht verfügbar
        print(f"NotificationManager nicht verfügbar - nur Konsolenausgabe")
    except Exception as e:
        # Fallback bei Fehlern
        print(f"Fehler beim Anzeigen der Benachrichtigung: {e}")

def main():
    """Main entry point for the Mauscribe application."""
    try:
        # Initialize application
        app = MauscribeApp()
        
        # Run application
        app.run()
        
    except KeyboardInterrupt:
        print("\n[INFO] Mauscribe wird beendet...")
    except SystemExit:
        # Sauberes Beenden bei Singleton-Fehlern
        pass
    except Exception as e:
        print(f"[ERROR] Unerwarteter Fehler: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
