#!/usr/bin/env python3
"""
Test script for Windows notifications in Mauscribe.
Run this script to test various notification types.
"""

import os
import sys
import time

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

try:
    from src.windows_notifications import WindowsNotificationManager

    print("✅ Windows notification manager imported successfully")
except ImportError as e:
    print(f"❌ Failed to import Windows notification manager: {e}")
    sys.exit(1)


def test_notifications():
    """Test various notification types."""
    print("🧪 Testing Windows notifications...")

    # Initialize notification manager
    notification_manager = WindowsNotificationManager()

    if not notification_manager.is_supported():
        print("❌ Windows notifications are not supported on this system")
        return

    print("✅ Windows notifications are supported")

    # Test system info
    system_info = notification_manager.get_system_info()
    print(f"📊 System info: {system_info}")

    # Test various notification types
    print("\n🎯 Testing notification types...")

    # Recording started
    print("1. Testing recording started notification...")
    notification_manager.show_recording_started()
    time.sleep(2)

    # Recording stopped
    print("2. Testing recording stopped notification...")
    notification_manager.show_recording_stopped(150)
    time.sleep(2)

    # Transcription complete
    print("3. Testing transcription complete notification...")
    notification_manager.show_transcription_complete("Dies ist ein Testtext für die Transkription", 3.5)
    time.sleep(2)

    # Text pasted
    print("4. Testing text pasted notification...")
    notification_manager.show_text_pasted("Ein Beispieltext der eingefügt wurde")
    time.sleep(2)

    # Spell check complete
    print("5. Testing spell check complete notification...")
    notification_manager.show_spell_check_complete("Falsch geschriebener Text", "Korrekt geschriebener Text")
    time.sleep(2)

    # Info notification
    print("6. Testing info notification...")
    notification_manager.show_info("Dies ist eine Informationsbenachrichtigung", "Test")
    time.sleep(2)

    # Warning notification
    print("7. Testing warning notification...")
    notification_manager.show_warning("Dies ist eine Warnungsbenachrichtigung", "Test")
    time.sleep(2)

    # Error notification
    print("8. Testing error notification...")
    notification_manager.show_error("Dies ist eine Fehlerbenachrichtigung", "Test")
    time.sleep(2)

    print("\n✅ All notification tests completed!")
    print("💡 Check your screen for the notification popups")


def test_configuration():
    """Test notification manager with configuration."""
    print("\n⚙️ Testing with configuration...")

    try:
        from src.utils.config import Config

        config = Config()
        print("✅ Configuration loaded successfully")

        # Initialize notification manager with config
        notification_manager = WindowsNotificationManager(config)

        if notification_manager.is_supported():
            print("✅ Notification manager with config initialized")

            # Test a notification
            notification_manager.show_info("Test mit Konfiguration", "Konfiguration")
            time.sleep(2)
        else:
            print("❌ Notification manager not supported with config")

    except ImportError as e:
        print(f"⚠️ Could not load configuration: {e}")
    except Exception as e:
        print(f"❌ Error testing with configuration: {e}")


if __name__ == "__main__":
    print("🚀 Mauscribe Windows Notification Test")
    print("=" * 40)

    try:
        test_notifications()
        test_configuration()

        print("\n🎉 All tests completed successfully!")
        print("💡 If you saw notification popups, the system is working correctly")

    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()

    print("\n👋 Test finished")
