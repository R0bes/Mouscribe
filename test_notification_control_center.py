# test_notification_control_center.py - Test Notification to Control Center Integration
"""
Test script for notification click to Control Center integration.
"""

import os
import sys
import threading
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_notification_callback():
    """Test the notification callback functionality."""
    try:
        from src.config.app_config import AppConfig
        from src.ui.control_center import open_control_center
        from src.ui.notifications import create_notification_manager

        print("Testing Notification to Control Center Integration")
        print("=" * 60)

        # Create notification manager
        notifier = create_notification_manager()
        print("Notification manager created")

        # Create config
        config = AppConfig()
        print("App config created")

        # Callback function that opens Control Center
        def open_control_center_callback():
            print("Notification clicked! Opening Control Center...")
            try:
                open_control_center(config, None)
                print("Control Center opened successfully")
            except Exception as e:
                print(f"❌ Failed to open Control Center: {e}")

        # Show test notification with callback
        print("Showing test notification...")
        success = notifier.transcription_complete(
            text="This is a test transcription to verify the callback works",
            duration=3.5,
            clickable=True,
            callback=open_control_center_callback,
        )

        if success:
            print("Test notification sent successfully")
            print("Click on the notification to test the Control Center opening")
            print("Waiting for notification click...")

            # Wait for user interaction
            print("Press Enter to continue...")
            input()

        else:
            print("Failed to send test notification")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


def test_control_center_bring_to_front():
    """Test the bring to front functionality."""
    try:
        from src.config.app_config import AppConfig
        from src.ui.control_center import open_control_center

        print("Testing Control Center Bring to Front")
        print("=" * 60)

        config = AppConfig()

        print("Opening Control Center...")
        open_control_center(config, None)

        print("Control Center should be brought to front")
        print("Waiting 5 seconds...")
        time.sleep(5)

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    print("Mauscribe Notification to Control Center Test")
    print("=" * 60)

    choice = input(
        "Choose test:\n1. Notification callback test\n2. Control Center bring to front test\n3. Both\nChoice (1-3): "
    )

    if choice == "1":
        test_notification_callback()
    elif choice == "2":
        test_control_center_bring_to_front()
    elif choice == "3":
        test_notification_callback()
        test_control_center_bring_to_front()
    else:
        print("Invalid choice")

    print("Test completed!")
