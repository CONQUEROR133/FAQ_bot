#!/usr/bin/env python3
"""
Network connectivity test for FAQ Bot
"""

import asyncio
import logging
import os
from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiohttp import ClientTimeout
from config import config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def test_bot_connection():
    """Тестирует подключение к Telegram API"""
    print("🔍 Тестирование подключения к Telegram API...")
    
    if not config.BOT_TOKEN:
        print("❌ BOT_TOKEN не найден в .env файле")
        return False
    
    # Создаем сессию с улучшенными таймаутами
    timeout = ClientTimeout(
        total=config.REQUEST_TIMEOUT,
        connect=config.CONNECT_TIMEOUT,
        sock_read=config.READ_TIMEOUT,
        sock_connect=10
    )
    
    session = AiohttpSession(timeout=timeout)
    bot = Bot(token=config.BOT_TOKEN, session=session)
    
    try:
        # Тестируем базовую связь
        print("📡 Проверка базового подключения...")
        me = await bot.get_me()
        print(f"✅ Подключение успешно! Бот: @{me.username}")
        
        # Тестируем отправку сообщения (если есть ADMIN_ID)
        if config.ADMIN_ID:
            try:
                print("📤 Тестирование отправки сообщения...")
                await bot.send_message(
                    config.ADMIN_ID, 
                    "🧪 Тест сетевого подключения - успешно!"
                )
                print("✅ Тестовое сообщение отправлено админу")
            except Exception as send_error:
                print(f"⚠️ Не удалось отправить тестовое сообщение: {send_error}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False
    finally:
        await bot.session.close()

async def test_file_operations():
    """Тестирует операции с файлами"""
    print("\n📁 Тестирование файловых операций...")
    
    # Проверяем файлы из FAQ
    test_files = [
        "files/alfa_insurance_memo.pdf",
        "files/alfa_insurance_contacts.txt",
        "files/alfa_insurance_services.pdf"
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            try:
                size = os.path.getsize(file_path)
                if size > 50 * 1024 * 1024:  # 50MB
                    print(f"⚠️ Файл слишком большой: {file_path} ({size / 1024 / 1024:.1f}MB)")
                else:
                    print(f"✅ Файл готов к отправке: {file_path} ({size / 1024:.1f}KB)")
            except OSError as e:
                print(f"❌ Ошибка доступа к файлу {file_path}: {e}")
        else:
            print(f"⚠️ Файл не найден: {file_path}")

async def main():
    print("🤖 Тестирование сетевых возможностей FAQ бота")
    print("=" * 50)
    
    # Тест подключения
    connection_ok = await test_bot_connection()
    
    # Тест файлов
    await test_file_operations()
    
    print("\n" + "=" * 50)
    if connection_ok:
        print("🎉 Тестирование завершено успешно!")
        print("Сетевые проблемы должны быть исправлены.")
    else:
        print("❌ Обнаружены проблемы с подключением.")
        print("Проверьте BOT_TOKEN и интернет-соединение.")

if __name__ == '__main__':
    import os
    asyncio.run(main())