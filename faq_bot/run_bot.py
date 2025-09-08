#!/usr/bin/env python3
"""
Main entry point for the FAQ Bot
"""

import sys
import os
import asyncio

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import main directly from the src directory
from main import main

if __name__ == "__main__":
    asyncio.run(main())