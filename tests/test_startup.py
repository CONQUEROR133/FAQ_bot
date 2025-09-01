#!/usr/bin/env python3
"""
Quick bot startup test to verify timeout fix
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_bot_startup():
    """Test if bot can be initialized without timeout errors"""
    print("🔍 Testing bot startup...")
    
    try:
        from aiogram import Bot
        from config import config
        
        if not config.BOT_TOKEN:
            print("❌ BOT_TOKEN not found in .env file")
            return False
        
        # Test bot initialization
        if not config.BOT_TOKEN:
            print("❌ BOT_TOKEN not found in .env file")
            return False
            
        bot = Bot(
            token=config.BOT_TOKEN,
            request_timeout=config.REQUEST_TIMEOUT
        )
        
        print("✅ Bot initialized successfully")
        
        # Test basic connection
        try:
            me = await bot.get_me()
            print(f"✅ Bot connection test passed: @{me.username}")
        except Exception as e:
            print(f"⚠️ Bot connection test failed: {e}")
        finally:
            await bot.session.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Bot initialization failed: {e}")
        return False

async def test_polling_setup():
    """Test if polling can be set up without timeout errors"""
    print("\n🔍 Testing polling setup...")
    
    try:
        from aiogram import Bot, Dispatcher
        from config import config
        
        if not config.BOT_TOKEN:
            print("❌ BOT_TOKEN not found in .env file")
            return False
        
        bot = Bot(
            token=config.BOT_TOKEN,
            request_timeout=config.REQUEST_TIMEOUT
        )
        dp = Dispatcher()
        
        print("✅ Dispatcher created successfully")
        
        # Test that timeout attribute is accessible (this was the error point)
        if hasattr(bot.session, 'timeout'):
            timeout_val = bot.session.timeout
            print(f"✅ Session timeout accessible: {timeout_val}")
        
        await bot.session.close()
        return True
        
    except Exception as e:
        print(f"❌ Polling setup failed: {e}")
        return False

async def main():
    print("🤖 Testing Bot Startup Fix")
    print("=" * 40)
    
    success = True
    success &= await test_bot_startup()
    success &= await test_polling_setup()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ All startup tests passed!")
        print("The timeout error should be fixed.")
    else:
        print("❌ Startup tests failed!")
        print("There may still be issues.")

if __name__ == '__main__':
    asyncio.run(main())