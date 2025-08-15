#!/usr/bin/env python3
"""Test script for Windows notifications."""

import logging
from src.ui.windows_notifications import WindowsNotificationManager
from src.utils.config import Config

def test_notifications():
    """Test various notification types."""
    # Set up debug logging
    logging.basicConfig(level=logging.DEBUG)
    
    print("Testing Windows notifications...")
    
    # Initialize notification manager
    config = Config()
    notif = WindowsNotificationManager(config)
    
    print("Showing test notification...")
    
    # Test info notification
    notif.show_info("Test Titel", "Das ist eine Test-Nachricht")
    
    print("Notification sent!")

if __name__ == "__main__":
    test_notifications()
