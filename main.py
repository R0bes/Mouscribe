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

from src.mouscribe import start_mouscribe

if __name__ == "__main__":
    start_mouscribe()
