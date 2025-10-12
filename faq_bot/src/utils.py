import logging
import os
import asyncio
from aiogram import types
from aiogram.exceptions import TelegramRetryAfter, TelegramNetworkError

async def retry_file_operation(operation, max_retries=3, delay=1):
    """Retry file operation on network errors"""
    for attempt in range(max_retries):
        try:
            return await operation()
        except (TelegramNetworkError, ConnectionError, OSError) as e:
            if attempt == max_retries - 1:
                raise e
            wait_time = delay * (attempt + 1)
            logging.warning(f"Attempt {attempt + 1}/{max_retries} failed: {e}. Retrying in {wait_time} seconds.")
            await asyncio.sleep(wait_time)
        except TelegramRetryAfter as e:
            logging.warning(f"Waiting required {e.retry_after} seconds.")
            await asyncio.sleep(e.retry_after)
        except Exception as e:
            # For other errors, don't retry
            raise e
    return None

async def send_file_with_retry(message, file_path):
    """Send file with retry mechanism"""
    async def send_file():
        if message:
            return await message.answer_document(types.FSInputFile(file_path))
        return None
    
    return await retry_file_operation(send_file)

def check_file_size(file_path, max_size_mb=50):
    """Check if file size is within limits"""
    try:
        file_size = os.path.getsize(file_path)
        max_size_bytes = max_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            return False, file_size
        return True, file_size
    except OSError as e:
        logging.error(f"Error checking file size: {e}")
        return False, 0

def remove_keyboard(message):
    """Remove keyboard from message"""
    try:
        if message and hasattr(message, 'edit_reply_markup') and not isinstance(message, types.InaccessibleMessage):
            return message.edit_reply_markup(reply_markup=None)
    except Exception as e:
        logging.warning(f"Could not remove keyboard: {e}")
    return None

def send_callback_answer(callback, text, show_alert=False):
    """Send callback answer with error handling"""
    try:
        return callback.answer(text, show_alert=show_alert)
    except Exception as e:
        logging.warning(f"Could not send callback answer: {e}")
        return None
