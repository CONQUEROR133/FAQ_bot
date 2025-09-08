#!/usr/bin/env python3
"""
Main entry point for the FAQ Bot
"""

import sys
import os
import asyncio

# Import main directly from the src directory
from src.main import main

if __name__ == "__main__":
    asyncio.run(main())