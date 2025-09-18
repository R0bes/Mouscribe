#!/usr/bin/env python3
"""
Test-Skript für Hot Word Detection
Testet die Hot Word Detection Funktionalität isoliert
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.audio.hotword_detector import HotWordDetector
from src.utils import get_logger, setup_logging


def test_start_word_callback(start_word: str) -> None:
    """Test callback für Start Word Erkennung."""
    print(f"🎯 START WORD ERKANNT: '{start_word}'")
    print(f"⏰ Zeit: {time.strftime('%H:%M:%S')}")

def test_stop_word_callback(stop_word: str) -> None:
    """Test callback für Stop Word Erkennung."""
    print(f"🛑 STOP WORD ERKANNT: '{stop_word}'")
    print(f"⏰ Zeit: {time.strftime('%H:%M:%S')}")


def main():
    """Hauptfunktion für Hot Word Detection Tests."""
    print("🧪 Hot Word Detection Test")
    print("=" * 40)
    
    # Setup logging
    setup_logging()
    logger = get_logger("HotWordTest")
    
    try:
        # Hot Word Detector initialisieren
        print("🔧 Initialisiere Hot Word Detector...")
        detector = HotWordDetector(test_start_word_callback, test_stop_word_callback)
        
        # Einstellungen anzeigen
        stats = detector.get_stats()
        print(f"📊 Konfiguration:")
        print(f"   - Start Words: {stats['start_words']}")
        print(f"   - Stop Words: {stats['stop_words']}")
        print(f"   - Sensitivität: {stats['sensitivity']}")
        print(f"   - Timeout: {stats['timeout_seconds']}s")
        print(f"   - Kontinuierlich: {stats['continuous_listening']}")
        
        # Hot Word Detection starten
        print("\n🎯 Starte Hot Word Detection...")
        if detector.start_listening():
            print("✅ Hot Word Detection läuft!")
            print("\n💡 Sprich eines der Start Words:")
            for word in stats['start_words']:
                print(f"   - '{word}'")
            print("\n💡 Sprich eines der Stop Words:")
            for word in stats['stop_words']:
                print(f"   - '{word}'")
            print("\n⏹️  Drücke Ctrl+C zum Beenden")
            
            try:
                # Warte auf Wake Words
                while True:
                    time.sleep(1)
                    
                    # Zeige aktuelle Statistiken
                    current_stats = detector.get_stats()
                    if current_stats['detection_count'] > 0:
                        print(f"📊 Detections: {current_stats['detection_count']}")
                        
            except KeyboardInterrupt:
                print("\n🛑 Beende Test...")
                
        else:
            print("❌ Hot Word Detection konnte nicht gestartet werden")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Fehler beim Test: {e}")
        return 1
        
    finally:
        # Cleanup
        try:
            detector.cleanup()
            print("✅ Cleanup abgeschlossen")
        except Exception as e:
            logger.error(f"❌ Fehler beim Cleanup: {e}")
    
    print("🎉 Test abgeschlossen!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
