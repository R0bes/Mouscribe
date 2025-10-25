# simple_notification_test.py - Simple Notification Test
"""
Simple test for notification callback functionality.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_notification():
    """Test notification with callback."""
    try:
        from src.ui.notifications import create_notification_manager

        print("Testing Notification Callback")
        print("=" * 40)

        # Create notification manager
        notifier = create_notification_manager()
        print("Notification manager created")

        # Callback function
        def test_callback():
            print("SUCCESS: Notification callback executed!")

        # Show test notification with callback
        print("Sending test notification...")
        success = notifier.transcription_complete(
            text="Test transcription - click to verify callback", duration=2.0, clickable=True, callback=test_callback
        )

        if success:
            print("Test notification sent successfully")
            print("Click on the notification to test callback")
        else:
            print("Failed to send test notification")

    except Exception as e:
        print(f"Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_notification()
