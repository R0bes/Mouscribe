#!/usr/bin/env python3
"""
Mauscribe - Voice-to-Text Tool
Einfacher Einstiegspunkt
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from voice_control.main import main

if __name__ == '__main__':
    main()
