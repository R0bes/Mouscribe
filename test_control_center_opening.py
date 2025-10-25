# test_control_center_opening.py - Test Control Center Opening
"""
Test Control Center opening from notification callback.
"""

import os
import sys
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_control_center_opening():
    """Test opening Control Center from callback."""
    try:
        from src.config.app_config import AppConfig
        from src.ui.control_center import open_control_center
        from src.ui.notifications import create_notification_manager

        print("Testing Control Center Opening from Notification")
        print("=" * 50)

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
                print(f"Failed to open Control Center: {e}")

        # Show test notification with callback
        print("Sending notification with Control Center callback...")
        success = notifier.transcription_complete(
            text="Click this notification to open Control Center",
            duration=5.0,
            clickable=True,
            callback=open_control_center_callback,
        )

        if success:
            print("Notification sent successfully")
            print("Click on the notification to open Control Center")
            print("Waiting 10 seconds for interaction...")
            time.sleep(10)
        else:
            print("Failed to send notification")

    except Exception as e:
        print(f"Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_control_center_opening()
