import asyncio
import logging
import time
from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramNetworkError, TelegramRetryAfter
from config import config
from database import Database
from faq_loader import FAQLoader  # type: ignore
from handlers import router
from middlewares import DependenciesMiddleware
from auth_middleware import AuthenticationMiddleware

# Настройка логирования с путем к родительской директории
import os
log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cache', 'bot.log')
os.makedirs(os.path.dirname(log_file), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Устанавливаем более детальное логирование для сетевых ошибок
logging.getLogger('aiogram.dispatcher').setLevel(logging.WARNING)
logging.getLogger('aiogram.event').setLevel(logging.WARNING)

# Глобальная переменная для отслеживания времени запуска
START_TIME = time.time()

async def start_polling_with_retry(bot: Bot, dp: Dispatcher, max_retries: int = 5):
    """Запуск polling с автоматическим переподключением при ошибках"""
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            logging.info(f"Запуск polling (попытка {retry_count + 1}/{max_retries})")
            await dp.start_polling(bot)
            break  # Если дошли сюда, значит polling завершился нормально
            
        except TelegramNetworkError as e:
            retry_count += 1
            wait_time = min(30, 5 * retry_count)  # Прогрессивная задержка: 5, 10, 15, 20, 25 сек
            
            logging.error(f"Сетевая ошибка: {e}")
            
            if retry_count < max_retries:
                logging.warning(f"Попытка переподключения через {wait_time} сек...")
                await asyncio.sleep(wait_time)
            else:
                logging.error("Превышено максимальное количество попыток переподключения")
                raise
                
        except TelegramRetryAfter as e:
            logging.warning(f"Требуется ожидание {e.retry_after} сек. перед повторной попыткой")
            await asyncio.sleep(e.retry_after)
            # Не увеличиваем retry_count для ограничений API
            
        except Exception as e:
            retry_count += 1
            logging.error(f"Непредвиденная ошибка: {e}")
            
            if retry_count < max_retries:
                wait_time = min(60, 10 * retry_count)  # Длинная задержка для непредвиденных ошибок
                logging.warning(f"Попытка перезапуска через {wait_time} сек...")
                await asyncio.sleep(wait_time)
            else:
                logging.error("Превышено максимальное количество попыток перезапуска")
                raise

async def log_uptime_periodically():
    """Периодически логирует время работы бота"""
    while True:
        hours = (time.time() - START_TIME) // 3600
        minutes = ((time.time() - START_TIME) % 3600) // 60
        logging.info(f"Бот работает: {int(hours)}ч {int(minutes)}мин")
        await asyncio.sleep(1800)  # Каждые 30 минут

async def health_check_periodically(bot: Bot):
    """Периодическая проверка состояния подключения бота"""
    while True:
        try:
            # Проверяем состояние бота каждые 5 минут
            me = await bot.get_me()
            logging.debug(f"Проверка состояния: бот @{me.username} активен")
        except Exception as e:
            logging.error(f"Ошибка проверки состояния бота: {e}")
        
        await asyncio.sleep(300)  # Каждые 5 минут

async def main():
    # Проверка наличия токена бота
    if not config.BOT_TOKEN:
        logging.error("BOT_TOKEN не найден в переменных окружения")
        raise ValueError("BOT_TOKEN environment variable is required")
    
    # Инициализация бота с улучшенными настройками для стабильности
    # Используем стандартную конфигурацию для совместимости с aiogram
    bot = Bot(
        token=config.BOT_TOKEN,
        request_timeout=config.REQUEST_TIMEOUT  # Простой таймаут для совместимости
    )
    dp = Dispatcher()
    
    # Инициализация зависимостей
    db = Database()
    db.init_db()
    
    faq_loader = FAQLoader(
        faq_file=config.FAQ_FILE,
        embeddings_file=config.EMBEDDINGS_FILE,
        index_file=config.INDEX_FILE
    )
    faq_loader.load_faq()
    faq_loader.create_embeddings()

    # Регистрируем middleware для внедрения зависимостей
    deps_middleware = DependenciesMiddleware(
        db_instance=db,
        faq_loader_instance=faq_loader,
        config_instance=config
    )
    
    # Примечание: AuthenticationMiddleware временно отключен, так как блокирует ввод пароля
    # Аутентификация обрабатывается на уровне обработчиков в handlers.py
    
    router.message.outer_middleware(deps_middleware)
    router.callback_query.outer_middleware(deps_middleware)
    dp.include_router(router)

    # Запускаем фоновые задачи
    asyncio.create_task(log_uptime_periodically())
    asyncio.create_task(health_check_periodically(bot))

    try:
        logging.info("Бот запущен и готов к работе")
        
        # Запуск улучшенного polling с автоматическим переподключением
        await start_polling_with_retry(bot, dp, max_retries=10)
        
    except KeyboardInterrupt:
        logging.info("Получен сигнал остановки (Остановка по клавише Ctrl+C)")
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")
        raise
    finally:
        try:
            await bot.session.close()
            logging.info("Бот остановлен")
        except Exception as e:
            logging.error(f"Ошибка при закрытии сессии: {e}")

if __name__ == '__main__':
    asyncio.run(main())