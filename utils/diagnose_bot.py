#!/usr/bin/env python3
"""
Bot Health Diagnostic Script
Helps diagnose why the bot stops responding and provides solutions
"""

import asyncio
import logging
import sys
import os
from datetime import datetime, timedelta

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Настройка логирования для диагностики
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def test_bot_connection():
    """Тестирует основное подключение к боту"""
    print("🔍 Тестирование подключения к боту...")
    
    try:
        from aiogram import Bot
        from config import config
        
        if not config.BOT_TOKEN:
            print("❌ BOT_TOKEN не найден в .env файле")
            return False
        
        bot = Bot(token=config.BOT_TOKEN, request_timeout=config.REQUEST_TIMEOUT)
        
        # Тест базового подключения
        me = await bot.get_me()
        print(f"✅ Подключение успешно: @{me.username}")
        
        # Тест получения обновлений
        try:
            updates = await bot.get_updates(limit=1, timeout=1)
            print(f"✅ Получение обновлений работает: {len(updates)} сообщений")
        except Exception as e:
            print(f"⚠️ Проблема с получением обновлений: {e}")
        
        await bot.session.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

def analyze_bot_logs():
    """Анализирует логи бота для выявления проблем"""
    print("\n📋 Анализ логов бота...")
    
    log_file = "bot.log"
    if not os.path.exists(log_file):
        print("⚠️ Файл bot.log не найден")
        return False
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            print("⚠️ Лог файл пустой")
            return False
        
        print(f"📝 Найдено {len(lines)} записей в логе")
        
        # Ищем последние ошибки
        error_lines = [line for line in lines if 'ERROR' in line]
        warning_lines = [line for line in lines if 'WARNING' in line]
        
        print(f"🔴 Найдено ошибок: {len(error_lines)}")
        print(f"🟡 Найдено предупреждений: {len(warning_lines)}")
        
        # Показываем последние проблемы
        if error_lines:
            print("\n🔴 Последние ошибки:")
            for line in error_lines[-3:]:  # Последние 3 ошибки
                print(f"   {line.strip()}")
        
        if warning_lines:
            print("\n🟡 Последние предупреждения:")
            for line in warning_lines[-3:]:  # Последние 3 предупреждения
                print(f"   {line.strip()}")
        
        # Проверяем на известные проблемы
        network_errors = [line for line in lines if 'ServerDisconnectedError' in line or 'TelegramNetworkError' in line]
        timeout_errors = [line for line in lines if 'timeout' in line.lower()]
        
        if network_errors:
            print(f"\n🌐 Обнаружены сетевые ошибки: {len(network_errors)}")
            print("   Рекомендация: Перезапустите бота с улучшенным переподключением")
        
        if timeout_errors:
            print(f"\n⏰ Обнаружены ошибки таймаута: {len(timeout_errors)}")
            print("   Рекомендация: Проверьте интернет-соединение")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка анализа логов: {e}")
        return False

def check_system_resources():
    """Проверяет системные ресурсы"""
    print("\n💻 Проверка системных ресурсов...")
    
    try:
        import psutil
        
        # Проверка памяти
        memory = psutil.virtual_memory()
        print(f"📊 Память: {memory.percent}% использовано")
        
        # Проверка CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        print(f"🖥️ CPU: {cpu_percent}% использовано")
        
        # Проверка диска
        disk = psutil.disk_usage('.')
        print(f"💾 Диск: {disk.percent}% использовано")
        
        return True
        
    except ImportError:
        print("⚠️ psutil не установлен, пропускаем проверку ресурсов")
        return True
    except Exception as e:
        print(f"❌ Ошибка проверки ресурсов: {e}")
        return False

def provide_recommendations():
    """Предоставляет рекомендации по решению проблем"""
    print("\n💡 Рекомендации:")
    print()
    print("1. 🔄 Если бот перестал отвечать:")
    print("   - Перезапустите бота: start_bot.bat")
    print("   - Проверьте интернет-соединение")
    print("   - Убедитесь что токен бота действителен")
    print()
    print("2. 🌐 При сетевых ошибках:")
    print("   - Новая версия main.py имеет автоматическое переподключение")
    print("   - Бот будет пытаться переподключиться автоматически")
    print("   - При критических ошибках - полный перезапуск")
    print()
    print("3. 📁 При проблемах с файлами:")
    print("   - Запустите clear_cache.bat для очистки кэша")
    print("   - Проверьте существование файлов в папке files/")
    print("   - Убедитесь что файлы не превышают 50MB")
    print()
    print("4. 🔧 Профилактические меры:")
    print("   - Регулярно перезапускайте бота (раз в сутки)")
    print("   - Следите за логами: tail -f bot.log")
    print("   - Используйте clear_cache.bat после изменений FAQ")

async def main():
    print("🤖 Диагностика состояния FAQ бота")
    print("=" * 50)
    
    # Тесты подключения
    connection_ok = await test_bot_connection()
    
    # Анализ логов
    logs_ok = analyze_bot_logs()
    
    # Проверка ресурсов
    resources_ok = check_system_resources()
    
    # Рекомендации
    provide_recommendations()
    
    print("\n" + "=" * 50)
    if connection_ok:
        print("✅ Подключение к боту работает")
    else:
        print("❌ Проблемы с подключением к боту")
    
    if logs_ok:
        print("✅ Анализ логов завершен")
    
    print("\n🎯 Следующие шаги:")
    if not connection_ok:
        print("1. Проверьте BOT_TOKEN в .env файле")
        print("2. Проверьте интернет-соединение")
        print("3. Перезапустите бота")
    else:
        print("1. Бот работает нормально")
        print("2. Мониторьте логи на предмет ошибок")
        print("3. При необходимости используйте clear_cache.bat")

if __name__ == '__main__':
    asyncio.run(main())