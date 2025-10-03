#!/usr/bin/env python3
"""
Simple start script for FAQ Bot
Runs the bot directly without PowerShell dependencies
"""

import sys
import os
import subprocess
import signal
import time

def main():
    """Main function to start the FAQ bot"""
    print("🤖 Starting FAQ Bot...")
    
    # Add src directory to Python path
    src_path = os.path.join(os.path.dirname(__file__), 'src')
    sys.path.insert(0, src_path)
    
    try:
        # Import and run the main function directly
        from main import main as bot_main
        import asyncio
        
        print("✅ Starting bot...")
        asyncio.run(bot_main())
        
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()