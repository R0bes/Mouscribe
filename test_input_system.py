#!/usr/bin/env python3
"""
Test script to validate the current input system and identify issues.
"""

import sys
import time

from src.input.input_handler import InputHandler
from src.utils.config import Config


def test_callback(pressed: bool):
    """Simple test callback to verify input handling."""
    status = "PRESSED" if pressed else "RELEASED"
    print(f"🎯 Input detected: {status} at {time.time():.3f}")


def main():
    """Test the input system."""
    print("🧪 Testing Input System...")

    try:
        # Load configuration
        config = Config()
        print(f"✅ Config loaded: primary={config.primary_name}, secondary={config.secondary_name}")

        # Create input handler
        handler = InputHandler(test_callback, test_callback)
        print("✅ Input handler created")

        print("\n🎮 Input System is running...")
        print("   - Press primary button (X2) to test")
        print("   - Press secondary button (X1) to test")
        print("   - Press Ctrl+C to stop")

        # Keep running
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n⏹️  Stopping input system...")

        # Cleanup
        handler.stop()
        print("✅ Input system stopped")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
