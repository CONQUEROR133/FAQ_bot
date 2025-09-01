#!/usr/bin/env python3
"""
Bot Restart Utility
Gracefully closes any existing bot connections and starts the bot cleanly
"""

import asyncio
import sys
import os
import logging
import time
from datetime import datetime
from typing import Any

# Add src to path before importing from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import config with fallback handling
config: Any = None
try:
    from config import config  # type: ignore
except ImportError as e:
    print(f"Warning: Could not import config module: {e}")
    print("This may be a development environment issue. The bot should still work at runtime.")
    # Create a dummy config object for development
    class DummyConfig:
        BOT_TOKEN = os.getenv('BOT_TOKEN', '')
    config = DummyConfig()

from aiogram import Bot
from aiogram.exceptions import TelegramNetworkError, TelegramConflictError

async def close_existing_connections():
    """Close any existing bot connections using the close() method"""
    try:
        print("🔄 Закрытие существующих подключений...")
        
        # Create a bot instance just to close any existing connections
        bot = Bot(token=config.BOT_TOKEN)
        
        # Try to get bot info to test connection
        try:
            me = await bot.get_me()
            print(f"📡 Подключен как: @{me.username} ({me.first_name})")
        except Exception:
            print("📡 Подключение к Telegram...")
        
        # Call close to terminate any existing connections
        await bot.close()
        print("✅ Существующие подключения закрыты")
        
        # Wait a bit for Telegram to process the close
        await asyncio.sleep(3)
        
    except Exception as e:
        print(f"⚠️  Ошибка при закрытии соединений: {e}")
        print("Это нормально, если бот не был запущен ранее")

async def test_bot_connection():
    """Test if bot can connect successfully"""
    try:
        print("🧪 Тестирование подключения к боту...")
        bot = Bot(token=config.BOT_TOKEN)
        
        me = await bot.get_me()
        print(f"✅ Тест подключения успешен: @{me.username}")
        
        await bot.close()
        return True
        
    except TelegramConflictError:
        print("❌ Ошибка конфликта: другой экземпляр бота все еще активен")
        return False
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

async def start_bot_clean():
    """Start the bot after ensuring no conflicts"""
    print("🚀 Запуск бота...")
    
    # Import main function with error handling
    main_func = None
    try:
        from main import main as main_func  # type: ignore
    except ImportError as e:
        print(f"Warning: Could not import main module: {e}")
        print("This may be a development environment issue. The bot should still work at runtime.")
        # For development, we'll just return
        return
    
    try:
        await main_func()
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")
        import traceback
        traceback.print_exc()
        raise

async def main_restart():
    """Main function to restart the bot cleanly"""
    print("=== Утилита перезапуска бота ===")
    print(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Токен бота: {'✅ Установлен' if config.BOT_TOKEN else '❌ Не установлен'}")
    
    if not config.BOT_TOKEN:
        print("❌ Ошибка: BOT_TOKEN не установлен")
        return
    
    # Step 1: Close existing connections
    await close_existing_connections()
    
    # Step 2: Test connection
    if not await test_bot_connection():
        print("⏳ Ожидание 10 секунд перед повторной попыткой...")
        await asyncio.sleep(10)
        
        if not await test_bot_connection():
            print("❌ Не удается подключиться к боту. Возможно, есть активный экземпляр.")
            print("💡 Попробуйте:")
            print("   1. Остановить все Python процессы")
            print("   2. Подождать 1-2 минуты")
            print("   3. Запустить снова")
            return
    
    # Step 3: Start the bot
    await start_bot_clean()

if __name__ == "__main__":
    asyncio.run(main_restart())