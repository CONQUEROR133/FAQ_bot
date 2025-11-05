import asyncio
import logging
import time
import json
import os
from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramNetworkError, TelegramRetryAfter
from config import config
from database import Database
from faq_loader import FAQLoader  # type: ignore
from handlers import router, waiting_for_password
from health import router as health_router
from middlewares import DependenciesMiddleware
from auth_middleware import AuthenticationMiddleware
import logging.handlers

# Custom JSON formatter for structured logging
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "ts": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        if hasattr(record, 'chat_id'):
            log_entry["chat_id"] = record.chat_id
        if hasattr(record, 'message_id'):
            log_entry["message_id"] = record.message_id
        if hasattr(record, 'handler'):
            log_entry["handler"] = record.handler
        if hasattr(record, 'query_similarity'):
            log_entry["query_similarity"] = record.query_similarity
        if hasattr(record, 'response_time'):
            log_entry["response_time"] = record.response_time
        if hasattr(record, 'cache_hit'):
            log_entry["cache_hit"] = record.cache_hit
            
        return json.dumps(log_entry, ensure_ascii=False)

# Setup logging with path to parent directory
log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'bot.log')
os.makedirs(os.path.dirname(log_file), exist_ok=True)

# Create logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create formatter
json_formatter = JSONFormatter()

# Create file handler with rotation
file_handler = logging.handlers.RotatingFileHandler(
    log_file, 
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
file_handler.setFormatter(json_formatter)
logger.addHandler(file_handler)

# Create console handler
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# Set more detailed logging for network errors
logging.getLogger('aiogram.dispatcher').setLevel(logging.WARNING)
logging.getLogger('aiogram.event').setLevel(logging.WARNING)

# Global variable to track startup time
START_TIME = time.time()

async def start_polling_with_retry(bot: Bot, dp: Dispatcher, max_retries: int = 5):
    """Start polling with automatic reconnection on errors"""
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            logging.info(f"Starting polling (attempt {retry_count + 1}/{max_retries})")
            await dp.start_polling(bot)
            break  # If we got here, polling ended normally
            
        except TelegramNetworkError as e:
            retry_count += 1
            wait_time = min(30, 5 * retry_count)  # Progressive delay: 5, 10, 15, 20, 25 sec
            
            logging.error(f"Network error: {e}")
            
            if retry_count < max_retries:
                logging.warning(f"Attempting to reconnect in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            else:
                logging.error("Maximum reconnection attempts exceeded")
                raise
                
        except TelegramRetryAfter as e:
            logging.warning(f"Waiting required {e.retry_after} seconds before retrying")
            await asyncio.sleep(e.retry_after)
            # Don't increment retry_count for API limits
            
        except Exception as e:
            retry_count += 1
            logging.error(f"Unexpected error: {e}")
            
            if retry_count < max_retries:
                wait_time = min(60, 10 * retry_count)  # Long delay for unexpected errors
                logging.warning(f"Attempting restart in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            else:
                logging.error("Maximum restart attempts exceeded")
                raise

async def log_uptime_periodically():
    """Periodically logs bot uptime"""
    while True:
        hours = (time.time() - START_TIME) // 3600
        minutes = ((time.time() - START_TIME) % 3600) // 60
        logging.info(f"Bot uptime: {int(hours)}h {int(minutes)}m")
        await asyncio.sleep(1800)  # Every 30 minutes

async def health_check_periodically(bot: Bot):
    """Periodic bot connection status check"""
    while True:
        try:
            # Check bot status every 5 minutes
            me = await bot.get_me()
            logging.debug(f"Status check: bot @{me.username} is active")
        except Exception as e:
            logging.error(f"Bot status check error: {e}")
        
        await asyncio.sleep(300)  # Every 5 minutes

async def main():
    # Check for bot token
    if not config.BOT_TOKEN:
        logging.error("BOT_TOKEN not found in environment variables")
        raise ValueError("BOT_TOKEN environment variable is required")
    
    # Initialize bot with improved settings for stability
    # Using standard configuration for aiogram compatibility
    bot = Bot(
        token=config.BOT_TOKEN,
        request_timeout=config.REQUEST_TIMEOUT  # Simple timeout for compatibility
    )
    dp = Dispatcher()
    
    # Initialize dependencies
    db = Database()
    db.init_db()
    
    faq_loader = FAQLoader(
        faq_file=config.FAQ_FILE,
        embeddings_file=config.EMBEDDINGS_FILE,
        index_file=config.INDEX_FILE
    )
    
    # Load FAQ with proper error handling
    try:
        faq_loader.load_faq()
    except Exception as e:
        logging.error(f"Failed to load FAQ data: {e}")
        raise RuntimeError(f"FAQ loading failed: {e}") from e
    
    # Create embeddings with proper error handling
    try:
        faq_loader.create_embeddings()
    except Exception as e:
        logging.error(f"Failed to create embeddings: {e}")
        raise RuntimeError(f"Embeddings creation failed: {e}") from e

    # Register middleware for dependency injection
    deps_middleware = DependenciesMiddleware(
        db_instance=db,
        faq_loader_instance=faq_loader,
        config_instance=config
    )
    
    # Register authentication middleware
    auth_middleware = AuthenticationMiddleware(
        db_instance=db,
        config_instance=config,
        waiting_for_password=waiting_for_password
    )
    
    router.message.outer_middleware(deps_middleware)
    router.callback_query.outer_middleware(deps_middleware)
    router.message.outer_middleware(auth_middleware)
    router.callback_query.outer_middleware(auth_middleware)
    dp.include_router(router)
    dp.include_router(health_router)

    # Start background tasks
    asyncio.create_task(log_uptime_periodically())
    asyncio.create_task(health_check_periodically(bot))

    try:
        logging.info("Bot started and ready to work")
        
        # Start improved polling with automatic reconnection
        await start_polling_with_retry(bot, dp, max_retries=10)
        
    except KeyboardInterrupt:
        logging.info("Received stop signal (Ctrl+C stop)")
    except Exception as e:
        logging.error(f"Critical error: {e}")
        raise
    finally:
        try:
            await bot.session.close()
            logging.info("Bot stopped")
        except Exception as e:
            logging.error(f"Error closing session: {e}")

if __name__ == '__main__':
    asyncio.run(main())