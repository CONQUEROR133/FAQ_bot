#!/usr/bin/env python3
"""
Start script for FAQ Bot
This script makes it easier to start the bot from any directory
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the main function
if __name__ == "__main__":
    try:
        from main import main
        import asyncio
        asyncio.run(main())
    except ImportError as e:
        print(f"Error importing main module: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting bot: {e}")
        sys.exit(1)