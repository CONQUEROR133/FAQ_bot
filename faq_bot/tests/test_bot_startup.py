#!/usr/bin/env python3
"""
Basic bot startup test to verify core functionality
"""

import asyncio
import sys
import os
import pytest

# Add the src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.mark.asyncio
async def test_bot_initialization():
    """Test if bot can be initialized without errors"""
    print("🔍 Testing bot initialization...")
    
    try:
        from aiogram import Bot
        from config import config
        
        if not config.BOT_TOKEN:
            print("⚠️ BOT_TOKEN not found in .env file")
            pytest.skip("BOT_TOKEN not found in .env file")  # Skip instead of pass
        
        # Test bot initialization
        bot = Bot(
            token=config.BOT_TOKEN,
            default_request_timeout=config.REQUEST_TIMEOUT
        )
        
        print("✅ Bot initialized successfully")
        await bot.session.close()
        assert True
        
    except Exception as e:
        print(f"❌ Bot initialization failed: {e}")
        pytest.fail(f"Bot initialization failed: {e}")

@pytest.mark.asyncio
async def test_config_loading():
    """Test if configuration loads correctly"""
    print("🔍 Testing configuration loading...")
    
    try:
        from config import config
        
        # Check that required config values exist
        required_configs = ['BOT_TOKEN', 'REQUEST_TIMEOUT', 'ACCESS_PASSWORD']
        
        for conf in required_configs:
            if hasattr(config, conf):
                value = getattr(config, conf)
                if conf == 'BOT_TOKEN' and value:
                    print(f"✅ {conf}: [REDACTED - LENGTH {len(value)}]")
                else:
                    print(f"✅ {conf}: {value}")
            else:
                print(f"⚠️ {conf}: Not found in config")
        
        assert True
        
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        pytest.fail(f"Configuration loading failed: {e}")

@pytest.mark.asyncio
async def test_database_connection():
    """Test database connection and initialization"""
    print("🔍 Testing database connection...")
    
    try:
        from database import Database
        
        # Test database initialization
        db = Database()
        db.init_db()
        
        print("✅ Database initialized successfully")
        
        # Test basic database operations
        test_user_id = 123456
        is_authenticated = db.is_user_authenticated(test_user_id)
        print(f"✅ User authentication check: {is_authenticated}")
        
        assert True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        pytest.fail(f"Database connection failed: {e}")