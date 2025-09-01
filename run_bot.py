#!/usr/bin/env python3
"""
FAQ Bot Main Launcher
Launches the bot from the organized project structure
"""

import sys
import os
import asyncio

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the main application
from src.main import main

if __name__ == "__main__":
    asyncio.run(main())