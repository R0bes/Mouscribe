#!/usr/bin/env python3
"""
Test script for the new input handler configuration system.
Tests the primary and secondary button configurations with different methods.
"""

import time
from src.input_handler import InputHandler
from src.utils.config import Config


def test_callback(button_type: str, value: bool):
    """Test callback function for input events."""
    print(f"{button_type} button event: {value}")


def test_input_handler():
    """Test the input handler with different configurations."""
    print("Testing Input Handler with new configuration system...")
    
    # Load configuration
    config = Config()
    print(f"Primary button: {config.primary_name} ({config.primary_type})")
    print(f"Primary method: {config.primary_method}")
    print(f"Secondary button: {config.secondary_name} ({config.secondary_type})")
    print(f"Secondary method: {config.secondary_method}")
    
    # Create input handler
    handler = InputHandler(
        pk_callback=lambda x: test_callback("Primary", x),
        sk_callback=lambda x: test_callback("Secondary", x)
    )
    
    print("\nInput handler started. Press the configured buttons to test:")
    print(f"- Primary: {config.primary_name} ({config.primary_method})")
    print(f"- Secondary: {config.secondary_name} ({config.secondary_method})")
    print("Press Ctrl+C to stop...")
    
    try:
        # Keep running to test input
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping input handler...")
        handler.stop()
        print("Input handler stopped.")


if __name__ == "__main__":
    test_input_handler()
